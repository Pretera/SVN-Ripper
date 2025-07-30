# SVN-Ripper

SVN-Ripper is an open-source tool designed to recover source code from exposed `.svn` folders.  
It supports CLI input of a single URL or a list of URLs and attempts to decode recovered files.

## Features

- Scans `.svn/entries` to enumerate source files
- Attempts to download and decode `.svn-base` files
- Supports gzip and UTF-8 decoding
- CLI support for:
  - `-u` for a single URL
  - `-l` to load from a file
  - `-o` to specify output directory
- Generates a structured HTML report

## Usage

```bash
python3 svn_ripper_cli.py -u https://target.com/
python3 svn_ripper_cli.py -l urls.txt -o output_folder
```

## License

MIT License — see LICENSE file.
