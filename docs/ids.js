// Draws the IDS sequences of the texts (span.ids[data-ids], docs/shelf/) as glyphs: IDS -> KAGE data -> SVG.
// Prototype. Loaded by site.js only on pages that have such spans. The parts come from GlyphWiki (name uXXXX, with the glyphs they use),
// the layout boxes below put them together with KAGE "99" lines, kage-engine (qatt.org/js/kage-engine.min.js) draws the strokes.
// Whatever fails (part not in GlyphWiki, no network) stays as it was: the text of the span.
(function () {
  var ARITY = { '⿰': 2, '⿱': 2, '⿲': 3, '⿳': 3, '⿴': 2, '⿵': 2, '⿶': 2, '⿷': 2, '⿸': 2, '⿹': 2, '⿺': 2, '⿻': 2, '⿼': 2, '⿽': 2, '⿾': 1, '⿿': 1 };
  // Boxes [x1, y1, x2, y2] of the operands in the 200 x 200 glyph
  var FULL = [0, 0, 200, 200];
  var BOX = {
    '⿰': [[0, 0, 100, 200], [100, 0, 200, 200]],
    '⿱': [[0, 0, 200, 100], [0, 100, 200, 200]],
    '⿲': [[0, 0, 67, 200], [67, 0, 133, 200], [133, 0, 200, 200]],
    '⿳': [[0, 0, 200, 67], [0, 67, 200, 133], [0, 133, 200, 200]],
    '⿴': [FULL, [50, 50, 150, 150]],
    '⿵': [FULL, [50, 70, 150, 200]],
    '⿶': [FULL, [50, 0, 150, 130]],
    '⿷': [FULL, [70, 50, 200, 150]],
    '⿸': [FULL, [70, 70, 200, 200]],
    '⿹': [FULL, [0, 70, 130, 200]],
    '⿺': [FULL, [70, 0, 200, 130]],
    '⿻': [FULL, FULL],
    '⿼': [FULL, [70, 0, 200, 130]],
    '⿽': [FULL, [70, 70, 200, 200]],
    '⿾': [FULL],
    '⿿': [FULL]
  };
  var API = 'https://glyphwiki.org/api/glyph?name=';

  // "⿰辶芇" -> { op, args: [...] } | { ch }; null if it is no valid IDS
  function parse(s) {
    var chars = Array.from(s), i = 0;
    function node() {
      var c = chars[i++];
      if (c === undefined) throw 0;
      if (ARITY[c]) { var args = []; for (var n = 0; n < ARITY[c]; n++) args.push(node()); return { op: c, args: args }; }
      if (c === '？' || c === '?') throw 0;
      return { ch: c };
    }
    try { var t = node(); return i === chars.length ? t : null; } catch (e) { return null; }
  }
  var partName = function (ch) { return 'u' + ch.codePointAt(0).toString(16); };

  // Puts the KAGE data of the sequence into buhin ({name: data}); returns the name of the glyph, and the list of GlyphWiki parts needed
  function compose(tree, buhin, parts, key) {
    if (tree.ch) { parts[partName(tree.ch)] = 1; return partName(tree.ch); }
    var boxes = BOX[tree.op];
    var lines = tree.args.map(function (a, n) {
      var b = boxes[n] || FULL;
      return '99:0:0:' + b.join(':') + ':' + compose(a, buhin, parts, key + '_' + n);
    });
    buhin[key] = lines.join('$');
    return key;
  }

  var cache = {}, pending = {};
  function loadPart(name) {   // GlyphWiki data of a part and, recursively, of the glyphs it uses
    if (cache[name]) return Promise.resolve();
    if (pending[name]) return pending[name];
    pending[name] = fetch(API + name).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (j) {
      if (!j || !j.data) throw 0;
      cache[name] = j.data;
      var used = [];
      j.data.split('$').forEach(function (l) { var f = l.split(':'); if (f[0] === '99' && f[7]) used.push(f[7].split('@')[0]); });
      return Promise.all(used.map(loadPart));
    });
    return pending[name];
  }

  function render(tree, key) {
    var buhin = {}, parts = {}, top = compose(tree, buhin, parts, key);
    return Promise.all(Object.keys(parts).map(loadPart)).then(function () {
      var k = new Kage();
      k.kShotai = k.kMincho;
      Object.keys(cache).forEach(function (n) { k.kBuhin.push(n, cache[n]); });
      Object.keys(buhin).forEach(function (n) { k.kBuhin.push(n, buhin[n]); });
      var p = new Kage.Polygons();
      k.makeGlyph(p, top);
      var svg = p.generateSVG().replace(/^<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '');
      return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="1.3em" height="1.3em" style="vertical-align:-.3em" fill="currentColor">' + svg + '</svg>';
    });
  }

  function run() {
    var spans = Array.prototype.slice.call(document.querySelectorAll('span.ids[data-ids]'));
    var uniq = {};
    spans.forEach(function (sp, n) {
      var ids = sp.getAttribute('data-ids'), tree = parse(ids);
      if (!tree || !tree.op) return;
      (uniq[ids] = uniq[ids] || { tree: tree, spans: [] }).spans.push(sp);
    });
    Object.keys(uniq).forEach(function (ids, n) {
      render(uniq[ids].tree, 'ids' + n).then(function (svg) {
        uniq[ids].spans.forEach(function (sp) {
          sp.innerHTML = svg;
          sp.classList.add('drawn', 'text-danger');
          sp.setAttribute('role', 'img');
          sp.setAttribute('aria-label', ids);
        });
      }).catch(function () { /* stays text */ });
    });
  }

  if (typeof module !== 'undefined') module.exports = { parse: parse, compose: compose };
  else window.IdsGlyphs = { run: run, parse: parse };
})();
