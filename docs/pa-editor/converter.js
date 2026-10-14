// Quốc Ngữ -> Phonetic Annotation glyphs (U+E001.. of pa.ttf), as on the old chunom.org editor.
// conv(text, id) appends the glyphs of the text to the element with that id.
var p_consonants = ['', 'b', 'c', 'ch', 'd', 'dz', 'ph', 'g', 'gi', 'h', 'kh', 'l', 'm', 'n', 'ng', 'nh', 'r', 's', 't', 'th', 'tr', 'v', 'x'];
var p_vowels = ['a', 'ar', 'ae', 'aer', 'e', 'er', 'i', 'ir', 'o', 'or', 'u', 'ur', 'y', 'yr', 'wa', 'war', 'wae', 'waer', 'we', 'wer', 'wi', 'wir'];
var p_alt_finals = {o: 'u', y: 'i'};
var p_finals = ['u', 'i', 'm', 'n', 'ng', 'nh', 'p', 't', 'c','ch'];

function getGlyphs(consonant,glide,vowel,modifier,ending,tone){

  if (consonant == 'p') consonant = 'b';
  if (vowel != '') {
    var a = p_consonants.indexOf(consonant);
    var b = p_vowels.indexOf(glide+vowel+modifier);
    if (a == -1 || b == -1) return '';
    var g1 = String.fromCharCode(0xE062 + a + 23*(1+b));
                var tone = (parseInt(tone)||0);
    var g2 = ending ? String.fromCharCode(0xE026 + 10*tone + p_finals.indexOf(p_alt_finals[ending] || ending)) : tone?String.fromCharCode(0xe000+tone):'';
    return g1 + g2;
  } else if (consonant != '' && ending == '') {
var i = p_consonants.indexOf(consonant)
    var c=String.fromCharCode(0xE062+i);
                if (tone) c+= String.fromCharCode(0xe000+tone);
    return c;
  } else {
    return null;
  }
}

function conv(text, out){
  var txt = text.toLowerCase().replace(/\r?\n/g, " \n ").replace(/\./g, '。').replace(/\,/g, '、').replace(/\?/g, '？').replace(/([,\.\?、。？])/g, " $1 ").replace(/  ([,\.\?、。？])/g, " $1").replace(/([,\.\?、。？]). /g, "$1 ").split(" ");
  for (var i=0,ilen=txt.length; i<ilen; i++){
    var t = txt[i];
    var map_base_vowels = "aăâeêioơôuưy";
    var maps = [
      "áắấéếíóớốúứý",
      "àằầèềìòờồùừỳ",
      "ảẳẩẻểỉỏởổủửỷ",
      "ãẵẫẽễĩõỡỗũữỹ",
      "ạặậẹệịọợộụựỵ"
    ];
    var sound = t.match(/([áắấéếíóớốúứýàằầèềìòờồùừỳảẳẩẻểỉỏởổủửỷãẵẫẽễĩõỡỗũữỹạặậẹệịọợộụựỵ])/);
    var tone = 0;
    if (sound) {
      for (var k=0; k < maps.length; k++){
        if (maps[k].indexOf(sound[0]) >= 0) {
          t = t.replace(sound[0], map_base_vowels.charAt(maps[k].indexOf(sound[0])));
          tone = k+1;
        }
      }
    }
    var m = t.match(/^(\_|[cdgknpt]h|ngh?|tr|gi|qu|[bcdđghklmnrstvx])?(\_|oo|ôô|u?ei|ou|o?ae|[uoiy]?[aăâeêoôơưy]|[uoiy]|[uoiy]?[aăâeêioôơuưy][aeêơ])(ch|nh|ng|[iouynmpct])?$/);
    if (!m) m = t.match(/^(\_|[cdgknpt]h|ngh?|tr|gi|qu|[bcdđghklmnrstvx])$/);
    if (m) {
      var initial = m[1]||'', v = m[2]||'', glide = '', final = m[3]||'';
      if (initial == "qu") {
        glide = 'w';
        initial = "c";
        if (v == 'ô') v = 'â';
        else if (v == 'o' && final == '') {
          v = 'o';
          final = 'u';
        }
      } else if (initial == 'k') {
        initial = 'c';
      } else if (
        v.indexOf("oa") == 0 || v.indexOf("uâ") == 0 ||
        v.indexOf("oe") == 0 || v.indexOf("uê") == 0 ||
        v.indexOf("uy") == 0 ||
        v.indexOf("oă") == 0 || v.indexOf("uơ") == 0
      ) {
        glide = 'w';
        v = v.substr(1);
      }
      v = v.replace(/ư[aoơ]$/, "yr ");
      v = v.replace(/ư$/, "y ");
      v = v.replace(/ơ$/, "ar ");
      v = v.replace(/â$/, "aer ");
      v = v.replace(/ă$/, "ae ");
      v = v.replace(/[iy][aeê]2? ?$/, "ir ");
      v = v.replace(/y$/, "i ");
      v = v.replace(/e$/, "er ");
      v = v.replace(/ê$/, "e ");
      v = v.replace(/u[oôa]2? ?$/, "ur ");
      v = v.replace(/o$/, "or ");
      v = v.replace(/ô$/, "o ");
      v = v.replace(" ", "");
      if (v == "i" && initial == "g") initial = "gi";
      if (v == "a" && (final != '' && "uy".indexOf(final) >= 0 || final == "nh" || final == "ch")) v = "ae";
      if (final) final = final.replace("o", "u").replace("y", "i");
      if (initial) initial = initial.replace("ngh", "ng").replace("gh", "g").replace(/d/, "dz").replace("đ", "d");
      
      if (initial == "_" && v == "_") {
        document.getElementById(out).innerText += final;
      } else {
        var g = getGlyphs(initial, glide, v, '', final, tone);
        if (g) {
          document.getElementById(out).innerText += g;
        } else {
          document.getElementById(out).innerText += ' ' + txt[i].toUpperCase() + String.fromCharCode(0xA0);
        }
      }
    } else {
      if (t != '') {
if (",.?、。？".indexOf(txt[i]) > -1)
  document.getElementById(out).innerText += txt[i].toUpperCase() + ' ';
else
  document.getElementById(out).innerText += txt[i].toUpperCase() + String.fromCharCode(0xA0);
/*        if (t.charCodeAt(0) > 3000) {
          document.getElementById(out).innerText += String.fromCharCode(0xA0);
        }*/
      }
    }
  }
  document.getElementById(out).innerHTML = document.getElementById(out).innerText.replace(/ /g, '<span class="fw-space"> </span>').replace(/\xA0/g, '<!--<span class="fw-space">&nbsp;</span>-->').replace(/\n/g, '<br>')
}
