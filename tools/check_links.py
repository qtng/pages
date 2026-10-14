#!/usr/bin/env python3
"""Reports external links of the hand-written pages (docs/pa, docs/fonts, docs/links) that do not answer.

  python3 tools/check_links.py

Run it from a machine with free internet access; a 'FAIL' is a candidate to remove (a few sites refuse bots, check by hand).
"""
import re, urllib.request
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / 'docs'
seen = {}
for page in ['pa', 'fonts', 'links']:
    for url in re.findall(r'href="(https?://[^"]+)"', (DOCS / page / 'index.html').read_text(encoding='utf-8')):
        seen.setdefault(url.replace('&amp;', '&'), page)
for url, page in sorted(seen.items()):
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        status = urllib.request.urlopen(request, timeout=15).status
    except Exception as e:
        status = f'FAIL ({e})'
    print(f'{status}\t{page}\t{url}')
