# pages

Static landing pages of the Chữ Nôm characters, published with GitHub Pages from `docs/` at `<site>/pages/` (https://chunom.org).

- `docs/<HEX>/index.html` – one page per character (plain HTML, shared `docs/style.css`, no scripts)
- `docs/index.html` – index of all characters
- `tools/generate.py` – generates all of the above from `dict.csv` and `js/glyph_relations.json` of [qtng/chunom](https://github.com/qtng/chunom)

Regenerate (Python 3, no dependencies):

    python3 tools/generate.py --site https://chunom.org             # data from the site; --site sets canonicals and og:image
    python3 tools/generate.py --chunom ../chunom --assets ../chunom-assets   # from local checkouts

Then commit `docs/`. Change the layout in `tools/generate.py` (`page()`), the look in `docs/style.css`.
