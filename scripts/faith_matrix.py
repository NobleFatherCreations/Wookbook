#!/usr/bin/env python3
"""Pass 03 — the matrix as an instrument.

810 cells (27 traditions x 30 tactics) were rendered as identical bullets, so
the grid carried no information at all: every cell looked the same whether the
finding was codified, sourced, structural or absent. The grade was already in
the data and simply was not being shown.

Now each cell is filled by its own evidence grade, the row and column light as
a cross-hair, the whole grid is operable by keyboard alone, and a live readout
names the cell under the cursor or caret. Screen readers get real row and
column headers plus a per-cell label.

No new data. No network, no storage, still one file.
"""
import re

MARK = "fx-matrix"

OLD = re.compile(
    r'<div class="matrixwrap"><table class="matrix">\s*'
    r'<thead>.*?</thead>\s*<tbody>.*?</tbody>\s*</table></div>', re.S)

NEW = (
    '<div class="fx-mx-tools">'
    '<div class="fx-mx-key" role="img" aria-label="Legend: cell fill shows evidence grade">'
    '<span class="fx-k"><i class="fx-sw fx-g-codified"></i>Codified</span>'
    '<span class="fx-k"><i class="fx-sw fx-g-sourced"></i>Sourced</span>'
    '<span class="fx-k"><i class="fx-sw fx-g-structural"></i>Structural</span>'
    '<span class="fx-k"><i class="fx-sw fx-g-none"></i>Ungraded</span>'
    '</div>'
    '<output class="fx-mx-read" id="fxMxRead" aria-live="polite">'
    'Move across the grid to read a cell.</output>'
    '</div>'
    '<div class="matrixwrap fx-mxwrap"><table class="matrix fx-mx">'
    '<caption class="fx-sr">Evidence grade for each tactic within each tradition. '
    'Use the arrow keys to move; Enter opens the tactic.</caption>'
    '<thead><tr><th class="fx-mx-corner" scope="col">Tradition \\ Tactic</th>'
    '${D.tactics.map(t=>`<th scope="col" class="fx-mx-ch" data-c="${t.order}">'
    '<a href="#/tactic/${t.order}"><span class="fx-sr">${esc(t.name)}</span>'
    '<span aria-hidden="true">${String(t.order).padStart(2,\'0\')}</span></a></th>`).join(\'\')}'
    '</tr></thead>'
    '<tbody>${D.religions.map((r,i)=>`<tr data-r="${i+1}">'
    '<th scope="row" class="fx-mx-rh"><a href="#/religion/${r.id}">'
    '<span aria-hidden="true">${String(i+1).padStart(2,\'0\')}</span> ${esc(r.name)}</a></th>'
    '${D.tactics.map(t=>{const _g=gradeOf(r.id,t.order);'
    'const _n=_g?_g[0]:\'\';const _k=fxMxKind(_g);'
    'return `<td class="fx-mx-c fx-g-${_k}" data-r="${i+1}" data-c="${t.order}" '
    'data-rel="${esc(r.name)}" data-tac="${esc(t.name)}" data-grade="${esc(_n||\'Ungraded\')}">'
    '<a href="#/tactic/${t.order}?rel=${i+1}" tabindex="-1" '
    'aria-label="${esc(r.name)}, ${esc(t.name)}: ${esc(_n||\'ungraded\')}">'
    '<span class="fx-sr">${esc(_n||\'ungraded\')}</span>'
    '<span class="fx-mx-dot" aria-hidden="true"></span></a></td>`}).join(\'\')}'
    '</tr>`).join(\'\')}</tbody>'
    '</table></div>')

HELPER_JS = r'''
/* --- matrix: reduce a grade tuple to a fill class, from the data alone --- */
function fxMxKind(g){
  if(!g) return 'none';
  var n = String(g[0]||'').toLowerCase();
  if(g[2] === 'sourced') return 'sourced';
  if(/codified|explicit|mandated/.test(n)) return 'codified';
  if(/structural|cultural|practice/.test(n)) return 'structural';
  return n ? 'structural' : 'none';
}
'''

CSS = r"""
/* ===================== the matrix, as an instrument ===================== */
.fx-sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;
  clip:rect(0 0 0 0);white-space:nowrap;border:0}
.fx-mx-tools{display:flex;flex-wrap:wrap;align-items:center;gap:.9rem 1.4rem;
  margin:.9rem 0 .7rem}
.fx-mx-key{display:flex;flex-wrap:wrap;gap:.85rem}
.fx-k{display:inline-flex;align-items:center;gap:.4rem;
  font-family:var(--mono);font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink2)}
.fx-sw{width:11px;height:11px;border-radius:2px;display:inline-block;
  border:1px solid color-mix(in srgb,var(--ink) 30%,transparent)}
.fx-g-codified .fx-mx-dot,.fx-sw.fx-g-codified{background:var(--curtain,#8A2432)}
.fx-g-sourced  .fx-mx-dot,.fx-sw.fx-g-sourced{background:var(--lapis,#3E5F8A)}
.fx-g-structural .fx-mx-dot,.fx-sw.fx-g-structural{background:var(--gilt,#A8813A)}
.fx-g-none     .fx-mx-dot,.fx-sw.fx-g-none{background:transparent;
  box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--ink) 26%,transparent)}
.fx-mx-read{font-family:var(--mono);font-size:.68rem;letter-spacing:.06em;
  color:var(--ink2);min-height:1.2em;flex:1 1 16rem}
.fx-mx-read b{color:var(--ink);font-weight:700}

.fx-mxwrap{overflow-x:auto;max-width:100%;position:relative;
  overscroll-behavior-x:contain;contain:paint}
.fx-mx{border-collapse:collapse}
.fx-mx-c{padding:0}
.fx-mx-c a{display:block;padding:3px;line-height:0;text-decoration:none}
.fx-mx-dot{display:block;width:9px;height:9px;border-radius:2px;
  transition:transform .12s linear}
.fx-mx-c:hover .fx-mx-dot,.fx-mx-c.fx-on .fx-mx-dot{transform:scale(1.35)}
.fx-mx-c.fx-cursor{outline:2px solid var(--gilt);outline-offset:-2px}
/* the cross-hair: the row and column of the active cell */
.fx-mx tr.fx-lit>th,.fx-mx tr.fx-lit>td{background:color-mix(in srgb,var(--gilt) 9%,transparent)}
.fx-mx .fx-collit{background:color-mix(in srgb,var(--gilt) 9%,transparent)}
.fx-mx-rh a,.fx-mx-ch a{text-decoration:none}
.fx-mx:focus-within .fx-mx-corner{color:var(--gilt)}
.fx-mxwrap:focus{outline:2px solid var(--gilt);outline-offset:3px}

@media (prefers-reduced-motion: reduce){.fx-mx-dot{transition:none}}
@media (prefers-contrast: more){
  .fx-mx-dot{outline:1px solid var(--ink)}
  .fx-g-none .fx-mx-dot{box-shadow:inset 0 0 0 2px var(--ink)}
}
@media print{
  .fx-mx-tools{display:none}
  .fx-mx-dot{outline:1px solid #000!important}
  .fx-g-none .fx-mx-dot{background:#fff!important}
  .fx-g-codified .fx-mx-dot{background:#000!important}
  .fx-g-sourced .fx-mx-dot{background:#666!important}
  .fx-g-structural .fx-mx-dot{background:#bbb!important}
}
"""

JS = r"""
(function(){
  function wire(){
    var tbl = document.querySelector('.fx-mx');
    if(!tbl || tbl.dataset.fx) return;
    tbl.dataset.fx = '1';
    var read = document.getElementById('fxMxRead');
    var cells = [].slice.call(tbl.querySelectorAll('.fx-mx-c'));
    if(!cells.length) return;
    var cols = tbl.querySelectorAll('thead .fx-mx-ch').length;
    var cur = 0;

    function clearLit(){
      tbl.querySelectorAll('tr.fx-lit').forEach(function(t){t.classList.remove('fx-lit')});
      tbl.querySelectorAll('.fx-collit').forEach(function(t){t.classList.remove('fx-collit')});
      tbl.querySelectorAll('.fx-on').forEach(function(t){t.classList.remove('fx-on')});
    }
    function light(cell){
      clearLit();
      if(!cell) return;
      cell.classList.add('fx-on');
      var tr = cell.closest('tr'); if(tr) tr.classList.add('fx-lit');
      var c = cell.getAttribute('data-c');
      tbl.querySelectorAll('[data-c="'+c+'"]').forEach(function(t){t.classList.add('fx-collit')});
      if(read){
        read.innerHTML = '<b>' + cell.getAttribute('data-rel') + '</b> &middot; ' +
          cell.getAttribute('data-tac') + ' &middot; ' + cell.getAttribute('data-grade');
      }
    }
    cells.forEach(function(c,i){
      c.addEventListener('mouseenter', function(){ light(c); });
      c.addEventListener('focusin', function(){ cur = i; light(c); });
    });
    tbl.addEventListener('mouseleave', function(){ clearLit(); });

    /* the grid is one tab stop; the arrow keys move the caret inside it */
    function focusCell(i){
      if(i < 0 || i >= cells.length) return;
      cells[cur] && cells[cur].classList.remove('fx-cursor');
      cur = i;
      var c = cells[cur];
      c.classList.add('fx-cursor');
      c.setAttribute('tabindex','0');
      c.focus({preventScroll:false});
      light(c);
    }
    cells[0].setAttribute('tabindex','0');
    tbl.addEventListener('keydown', function(e){
      var k = e.key, n = null;
      if(k === 'ArrowRight') n = cur + 1;
      else if(k === 'ArrowLeft') n = cur - 1;
      else if(k === 'ArrowDown') n = cur + cols;
      else if(k === 'ArrowUp') n = cur - cols;
      else if(k === 'Home') n = cur - (cur % cols);
      else if(k === 'End') n = cur - (cur % cols) + cols - 1;
      else if(k === 'Enter' || k === ' '){
        var a = cells[cur] && cells[cur].querySelector('a');
        if(a){ e.preventDefault(); a.click(); }
        return;
      } else return;
      e.preventDefault();
      focusCell(n);
    });
  }
  wire();
  var app = document.getElementById('app');
  if(app && window.MutationObserver){
    new MutationObserver(function(){ wire(); }).observe(app,{childList:true,subtree:true});
  }
  addEventListener('hashchange', function(){ setTimeout(wire, 0); });
})();
"""


def build(html):
    if MARK in html:
        return html
    n = len(OLD.findall(html))
    html = OLD.sub(lambda m: NEW, html)
    anchor = "function relEntryHTML(t, i, open){"
    html = html.replace(anchor, HELPER_JS + "\n" + anchor, 1)
    html = html.replace("</head>", '<style id="%s">%s</style>\n</head>' % (MARK, CSS), 1)
    i = html.rindex("</body>")
    html = html[:i] + '<script id="fx-matrix-js">%s</script>\n' % JS + html[i:]
    print("  matrix tables rewritten:", n)
    return html


if __name__ == "__main__":
    import pathlib
    p = pathlib.Path(__file__).resolve().parent.parent / "faith" / "index.html"
    p.write_text(build(p.read_text(encoding="utf-8")), encoding="utf-8")
    print("  written:", p)
