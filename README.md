# SVN-Ripper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.txt)
[![Stars](https://img.shields.io/github/stars/pretera/SVN-Ripper?style=social)](https://github.com/pretera/SVN-Ripper/stargazers)
[![Downloads](https://img.shields.io/github/downloads/pretera/SVN-Ripper/total)](https://github.com/pretera/SVN-Ripper/releases)

**SVN-Ripper** is a security tool that recovers full source code from `.svn` version control metadata accidentally exposed to the internet. Additionnaly, we have developed a sub-tool that uses Google Dorks to automatically find exposed `.svn` repositories on the internet using Google, Bing Search and SerpAPI.

Developed by [Pretera](https://pretera.com)  
Blog: [Tool Release: SVN-Ripper](https://pretera.com/blogs/svn-ripper)

---

## Features

- **Auto-fetch exposed `.svn/entries` files**
- **Reconstruct folder tree and decode `.svn-base` files**
- **Restore PHP, JS, HTML, PDF, and other real extensions**
- **Generate beautiful HTML reports and JSON exports**
- **Package recovered files into timestamped ZIPs**
- **Proxy support (e.g., Burp Suite, WAF bypass)**
- **Bonus tool: `find_svn.py` to search for exposed `.svn` repositories**

---

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

Or install it as a CLI tool:

```bash
pip install .
```

Then run with:

```bash
svn-ripper -u https://example.com/
```

---

## Usage

### `svn_ripper.py` - Recover code from `.svn`

```bash
python cli/svn_ripper.py -u https://target.com/
```

**Arguments:**

- `-u`, `--url`: Single base URL to scan
- `-l`, `--list`: File with list of base URLs
- `-o`, `--out`: Output directory for recovered files (default: `recovered`)
- `-t`, `--template`: Path to HTML report template (default included)

### Example:

```bash
python cli/svn_ripper.py -l urls.txt -o dumped_sources/
```

Generates:
- Recovered source files (preserving paths)
- HTML report (with color-coded status)
- `recovered_<timestamp>.zip` package

---

## `find_svn.py` - Search exposed SVN folders online

This script uses Google dorks or APIs to identify `.svn` exposures online.

### Requirements

Install `googlesearch-python`:

```bash
pip install googlesearch-python
```

### Usage

```bash
python cli/find_svn.py --engine google --max 20
```

**Arguments:**

- `--engine`: Search engine to use (`google`, `serpapi`, or `bing`)
- `--max`: Max results per dork (default: 10)
- `--delay`: Delay between queries (Google only)
- `--serpapi-key`: SerpAPI key (if engine is `serpapi`)
- `--bing-key`: Bing Search API key (if engine is `bing`)

---

## Automation

The tool produces machine-readable reports (HTML & JSON), making it easy to:

- File security tickets
- Share forensic reports with developers
- Automate incident response

---

## Demo

![SVN-Ripper Report Screenshot](https://pretera.com/assets/svn-ripper-demo.png)

---

## Output Structure

```
recovered/
├── index.php
├── config/
│   └── db.php
├── report_20250731_220530.html
└── recovered_20250731_220530.zip
```

---

## Proxy Support

To route traffic via proxy (e.g., Burp), export:

```bash
export HTTP_PROXY=http://127.0.0.1:8080
export HTTPS_PROXY=http://127.0.0.1:8080
```

---

## 📝 License

This project is licensed under the MIT License.  
See [LICENSE.txt](LICENSE.txt) for more details.

---

## 🤝 Credits

Created by [Dardan Prebreza](https://pretera.com) — Offensive Security Lead @ Pretera  
Maintained by the [Pretera Offensive Team](https://pretera.com)

---
