# pages

Static landing pages of the Chữ Nôm characters, published with GitHub Pages from `docs/` at `<site>/pages/` (https://chunom.org).

- `docs/<HEX>/index.html` – one page per character (plain HTML, shared `docs/style.css`, no scripts)
- `docs/index.html` – index of all characters, `docs/sitemap.xml` – sitemap
- the generator `tools/pages/generate.py` is in the private repository `qtng/chunom-private` – it generates all of the above from `dict.csv` and `js/glyph_relations.json` of [qtng/chunom](https://github.com/qtng/chunom)

Regenerate (Python 3, no dependencies; run in `qtng/chunom-private`, it writes the checkout of this repository next to it, or `PAGES_PUBLIC`):

    python3 tools/pages/generate.py --site https://chunom.org             # data from the site; --site sets canonicals, sitemap and og:image
    python3 tools/pages/generate.py --chunom ../chunom --assets ../chunom-assets   # from local checkouts

Then commit `docs/`. Change the layout in `tools/pages/generate.py` there (`page()`), the look in `docs/style.css`.
