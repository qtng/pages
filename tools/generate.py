#!/usr/bin/env python3
"""Generates the static landing pages of the characters: docs/<HEX>/index.html, docs/index.html (index), docs/grade/<N>/index.html (lists), docs/sitemap.xml.

The pages are plain HTML with the shared docs/style.css (no scripts). The data comes from the chunom repository:
dict.csv and js/glyph_relations.json, read from a local checkout or, by default, from the site itself (--site, default https://v2.chunom.org).

  python3 tools/generate.py                          data from the site (--site)
  python3 tools/generate.py --chunom ../chunom        data from a local checkout of qtng/chunom
  python3 tools/generate.py --assets ../chunom-assets only link images that exist in a local checkout of qtng/chunom-assets

The generated folders (docs/<HEX>/, docs/grade/, sitemap.xml, index.html) are overwritten; style.css and the hand-written pages (docs/pa/, docs/pa-editor/, docs/fonts/, docs/links/) stay. REDIRECTS lists the old addresses that only forward.
"""
import argparse, csv, re, html, io, json, shutil, urllib.parse, urllib.request
from pathlib import Path

QATT = 'https://qatt.org'                  # the other site: Bootstrap comes from there
   # <size>/<HEX>.webp: many characters are in no font, so they are shown as images like in the dictionary
SITE_NAME = 'Chunom.org'
KINDS = {'v': 'Variant', 's': 'Simplified', 't': 'Traditional'}
# Old addresses of chunom.org (/pages/<name>/) that now live elsewhere: name -> target (relative to the site)
REDIRECTS = {
    'genibrel': 'chunom/dict/genibrel.html',
    'bonet': 'chunom/dict/bonet.html',
    'ime': 'chunom/writer.html',
    'imepad': 'chunom/writer.html',
    'moses': 'chunom/translate.html',
    'standard': 'pages/grade/1/',
}
ROOT = Path(__file__).resolve().parent.parent
_unused = Path(__file__).resolve().parent.parent
DOCS = ROOT / 'docs'

ap = argparse.ArgumentParser()
ap.add_argument('--site', default='https://v2.chunom.org', help='address of the site, https://chunom.org when it is live (default: %(default)s)')
ap.add_argument('--chunom', help='local checkout of qtng/chunom (default: download from the site)')
ap.add_argument('--assets', help='local checkout of qtng/chunom-assets (default: assume every image exists)')
args = ap.parse_args()
SITE = args.site.rstrip('/')               # the address of the site: canonicals, og:image and the sitemap need it; everything else is root-relative
BASE = f'{SITE}/pages'                     # where docs/ is published
APP = '/chunom/index.html'                 # the dictionary with the popup (?detail=)
IMAGES = '/chunom-assets/generated'        # <size>/<HEX>.webp: many characters are in no font, so they are shown as images like in the dictionary


def read(path):
    if args.chunom:
        return (Path(args.chunom) / path).read_text(encoding='utf-8')
    with urllib.request.urlopen(f'{SITE}/chunom/{path}') as response:
        return response.read().decode('utf-8')


NAV_HEAD = ['<script src="/pages/site.js"></script>',   # site-wide script (docs/site.js), empty for now
            f'<link rel="stylesheet" href="{QATT}/vendor/bootstrap/css/bootstrap.min.css">']   # the menu bar of the site (navigation.js) needs Bootstrap
NAV_SCRIPT = '<script defer src="/chunom/js/navigation.js"></script>'
esc = lambda text: html.escape(str(text), quote=True)
hexcode = lambda ch: f'{ord(ch):X}'
rows = [r for r in csv.reader(io.StringIO(read('dict.csv'))) if len(r) >= 3]
relations = json.loads(read('js/glyph_relations.json'))
images = {p.stem for p in (Path(args.assets) / 'generated' / '160').glob('*.webp')} if args.assets else None

by_char, words = {}, {}
for r in rows:
    if len(r[1]) == 1:
        by_char.setdefault(r[1], []).append(r)
for r in rows:
    if len(r[1]) > 1:
        for ch in dict.fromkeys(r[1]):
            if ch in by_char:
                words.setdefault(ch, []).append(r)
chars = sorted(by_char, key=ord)
variants_of = {}
for variant, (kind, main) in relations.items():
    variants_of.setdefault(main, []).append((variant, kind))


def has_image(ch):
    if images is None:
        return ch in by_char or ch in relations or ch in variants_of
    return hexcode(ch) in images


def glyph(ch, link=None):
    """A character as a small image (alt = the character), or as text when there is no image."""
    inner = esc(ch)
    if has_image(ch):
        inner = f'<img class="g" src="{IMAGES}/32/{hexcode(ch)}.webp" width="32" height="32" alt="{esc(ch)}" loading="lazy">'
    return f'<a href="{link}">{inner}</a>' if link else inner


def a(ch):
    return glyph(ch, f'../{hexcode(ch)}/' if ch in by_char else None)


def page(ch):
    entries, code = by_char[ch], hexcode(ch)
    first = entries[0]
    readings = list(dict.fromkeys(r[0] for r in entries))
    url = f'{BASE}/{code}/'
    title = f'{ch} - Chữ Nôm U+{code}: {readings[0]} - {first[2]}'
    compounds = words.get(ch, [])
    description = f'Vietnamese {ch} ({", ".join(readings)}) {first[2]}' + (' | ' + '| '.join(f'{r[1]} {r[0]}' for r in compounds[:8]) if compounds else '')
    big = has_image(ch)
    heading = esc(ch)
    if big:
        heading = f'<img class="big" src="{IMAGES}/160/{code}.webp" width="160" height="160" alt="{esc(ch)}">'
    related = []
    if ch in relations:
        kind, main = relations[ch]
        related.append((main, 'Standard form'))
        related += [(v, KINDS[k]) for v, k in variants_of.get(main, []) if v != ch]
    else:
        related += [(v, KINDS[k]) for v, k in variants_of.get(ch, [])]

    facts = [('Unicode', f'U+{code}')]
    for label, index in (('Grade', 3), ('Frequency', 5), ('Strokes', 4)):
        value = next((r[index] for r in entries if len(r) > index and r[index] and (index != 3 or r[index] != '0')), '')
        if value:
            facts.append((label, f'#{value}' if label == 'Frequency' else value))
    og = [('og:type', 'article'), ('og:site_name', SITE_NAME), ('og:title', title), ('og:description', description), ('og:url', url)]
    if big:
        og.append(('og:image', f'{SITE}{IMAGES}/160/{code}.webp'))

    lines = [
        '<!doctype html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{esc(title)}</title>', f'<meta name="description" content="{esc(description)}">',
        '<meta name="robots" content="index,follow">', f'<link rel="canonical" href="{url}">',
        *[f'<meta property="{k}" content="{esc(v)}">' for k, v in og],
        *NAV_HEAD, '<link rel="stylesheet" href="../style.css">', NAV_SCRIPT, '</head>', '<body>',
        '<main>', '<p class="crumbs"><a href="../">Chữ Nôm characters</a></p>',
        f'<h1 lang="vi">{heading}</h1>',
        f'<p class="lead">{esc(readings[0])} – {esc(first[2])}</p>',
    ]
    lines += ['<dl>', *[f'<dt>{k}</dt><dd>{esc(v)}</dd>' for k, v in facts], '</dl>']
    lines += ['<h2>Readings</h2>', '<ul>', *[f'<li><b>{esc(r[0])}</b> – {esc(r[2])}</li>' for r in entries], '</ul>']
    if related:
        lines += ['<h2>Related characters</h2>', '<ul class="chars">', *[f'<li>{a(c)} <small>{esc(k)}</small></li>' for c, k in related], '</ul>']
    if compounds:
        lines += [f'<h2>Words with {esc(ch)}</h2>', '<ul class="words">', *[f'<li><span lang="vi">{"".join(glyph(c) for c in r[1])}</span><span><b>{esc(r[0])}</b> – {esc(r[2])}</span></li>' for r in compounds[:40]], '</ul>']
    lines += [
        f'<p><a href="{APP}?detail={urllib.parse.quote(ch)}">Open {esc(ch)} in the dictionary</a> – with animation, audio and decks.</p>',
        f'<p><small>More: <a href="https://en.wiktionary.org/wiki/{urllib.parse.quote(ch)}">Wiktionary</a> · '
        f'<a href="https://www.unicode.org/cgi-bin/GetUnihanData.pl?codepoint={code}">Unihan</a></small></p>',
        '</main>', f'<footer>{SITE_NAME}</footer>', '</body>', '</html>', '']
    return '\n'.join(lines)


# The lists of index.html of the dictionary: Grade 1 = the 100 most frequent entries (any level), Grades 2-4 = the levels without them
rank = lambda r: int(r[5]) if len(r) > 5 and r[5].isdigit() else float('inf')
key = lambda r: (r[1], r[0])


def ranked(entries):
    seen = set()
    return [r for r in sorted(entries, key=rank) if key(r) not in seen and not seen.add(key(r))]


top100 = ranked(r for r in rows if rank(r) != float('inf'))[:100]
in_top = {key(r) for r in top100}
by_level = lambda *levels: ranked(r for r in rows if len(r) > 3 and r[3] in levels and key(r) not in in_top)
GRADES = {
    '1': ('Grade 1 Characters', 'The 100 most frequent Chữ Nôm words', top100),
    '2': ('Grade 2 Characters', 'Frequent Chữ Nôm words of levels 1 and 2', by_level('1', '2')),
    '3': ('Grade 3 Characters', 'Chữ Nôm words of level 3', by_level('3')),
    '4': ('Grade 4 Characters', 'Chữ Nôm words of level 4', by_level('4')),
    '0': ('Other Characters', 'Further Chữ Nôm words', by_level('0')),
}


def grade_page(number):
    heading, text, entries = GRADES[number]
    title = f'{heading} - {text} - {SITE_NAME}'
    description = f'{text}: {len(entries)} entries with readings and meanings. ' + ', '.join(f'{r[1]} {r[0]}' for r in entries[:12])
    nav = ' · '.join(f'<a href="../{n}/">{esc(GRADES[n][0].replace(" Characters", ""))}</a>' if n != number else f'<b>{esc(GRADES[n][0].replace(" Characters", ""))}</b>' for n in GRADES)
    items = []
    for r in entries:
        nom = ''.join(glyph(c, f'../../{hexcode(c)}/' if c in by_char else None) for c in r[1])
        items.append(f'<li><span lang="vi">{nom}</span><span><b>{esc(r[0])}</b> – {esc(r[2])}</span></li>')
    return '\n'.join([
        '<!doctype html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{esc(title)}</title>', f'<meta name="description" content="{esc(description)}">',
        '<meta name="robots" content="index,follow">', f'<link rel="canonical" href="{BASE}/grade/{number}/">',
        f'<meta property="og:type" content="website"><meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}">',
        *NAV_HEAD, '<link rel="stylesheet" href="../../style.css">', NAV_SCRIPT, '</head>', '<body>',
        '<main>', '<p class="crumbs"><a href="../../">Chữ Nôm characters</a></p>',
        f'<h1 class="list">{esc(heading)}</h1>', f'<p class="lead">{esc(text)} ({len(entries)} entries)</p>',
        f'<p class="grades">{nav}</p>', '<ul class="words">', *items, '</ul>', '</main>', f'<footer>{SITE_NAME}</footer>', '</body>', '</html>', ''])


def redirect_page(target):
    url = f'{SITE}/{target}'
    return '\n'.join([
        '<!doctype html>', '<html lang="en">', '<head>', '<meta charset="utf-8">', f'<title>Moved to {esc(url)}</title>',
        f'<link rel="canonical" href="{url}">', f'<meta http-equiv="refresh" content="0; url={url}">', NAV_HEAD[0],
        f'<script>location.replace({json.dumps(url)});</script>', '</head>', '<body>',
        f'<p>This page has moved to <a href="{url}">{esc(url)}</a>.</p>', '</body>', '</html>', ''])


def index():
    groups = {}
    for ch in chars:
        level = next((r[3] for r in by_char[ch] if r[3] != '0'), '0')
        groups.setdefault(level, []).append(ch)
    lines = [
        '<!doctype html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>Chữ Nôm characters - Chunom.org</title>',
        f'<meta name="description" content="{len(chars)} Chữ Nôm characters with readings, meanings, variants and example words.">',
        '<meta name="robots" content="index,follow">', f'<link rel="canonical" href="{BASE}/">',
        *NAV_HEAD, '<link rel="stylesheet" href="style.css">', NAV_SCRIPT, '</head>', '<body>',
        '<main>', '<h1 class="list">Chữ Nôm characters</h1>',
        '<p class="grades">' + ' · '.join(f'<a href="grade/{n}/">{esc(g[0])}</a>' for n, g in GRADES.items()) + ' · <a href="pa/">Phonetic Annotation</a> · <a href="fonts/">Fonts</a> · <a href="links/">Links</a></p>']
    for level in sorted(groups, key=lambda l: (l == '0', l)):
        lines += [f'<h2>{"Grade " + level if level != "0" else "Other characters"}</h2>', '<ul class="chars">']
        lines += [f'<li>{glyph(ch, hexcode(ch) + "/")} <small>{esc(by_char[ch][0][0])}</small></li>' for ch in groups[level]]
        lines.append('</ul>')
    lines += ['</main>', f'<footer>{SITE_NAME}</footer>', '</body>', '</html>', '']
    return '\n'.join(lines)


for old in DOCS.iterdir():          # the generated folders only (names are hex codes)
    if old.is_dir() and re.fullmatch(r'[0-9A-F]{4,5}', old.name):
        shutil.rmtree(old, ignore_errors=True)
for ch in chars:
    (DOCS / hexcode(ch)).mkdir(parents=True, exist_ok=True)
    (DOCS / hexcode(ch) / 'index.html').write_text(page(ch), encoding='utf-8')
(DOCS / 'index.html').write_text(index(), encoding='utf-8')
for name, target in REDIRECTS.items():
    (DOCS / name).mkdir(parents=True, exist_ok=True)
    (DOCS / name / 'index.html').write_text(redirect_page(target), encoding='utf-8')
shutil.rmtree(DOCS / 'grade', ignore_errors=True)
for number in GRADES:
    (DOCS / 'grade' / number).mkdir(parents=True)
    (DOCS / 'grade' / number / 'index.html').write_text(grade_page(number), encoding='utf-8')
urls = [f'{BASE}/', f'{BASE}/pa/', f'{BASE}/fonts/', f'{BASE}/links/', f'{BASE}/pa-editor/'] + [f'{BASE}/grade/{n}/' for n in GRADES] + [f'{BASE}/{hexcode(ch)}/' for ch in chars]
(DOCS / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                  + ''.join(f'<url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n', encoding='utf-8')
# the hand-written pages hold the address of the site in canonical, og:url and a bookmarklet: set it to --site
for page in ('pa', 'pa-editor', 'fonts', 'links'):
    path = DOCS / page / 'index.html'
    text = path.read_text(encoding='utf-8')
    old = re.search(r'rel="canonical" href="(https?://[^/"]+)', text).group(1)
    path.write_text(text.replace(old, SITE), encoding='utf-8')
print(f'{len(chars)} pages written to {DOCS}')
