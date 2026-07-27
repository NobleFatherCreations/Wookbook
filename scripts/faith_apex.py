#!/usr/bin/env python3
"""Pass 02 — the apex chain diagram.

Each apex row is a chain of custody for an office: who holds it, who chose
them, who can remove them. The third link is the one that matters, and in the
record it is frequently not there at all. Rendered as prose that fact reads as
one more sentence; rendered as a chain it is the argument.

Three terminal states, classified from the row's own words:

  intact   a removal mechanism exists and is used      closed link
  nominal  exists on paper, never exercised            hairline ghost link
  broken   no mechanism at all                         the link hangs open

Nothing is asserted that the row does not already say. No network, no storage,
no new files — the constraint set is preserved exactly.
"""
import re

MARK = "fx-apex"

# the classifier and the chain, injected as a helper the templates call
HELPER_JS = r'''
/* --- apex chain: classify a removal mechanism from the row's own words --- */
function fxApexState(s){
  var t = String(s||'').trim().toLowerCase();
  if(!t || t === '—' || t === '-') return 'broken';
  if(/^(—|-)\s/.test(t)) return 'broken';
  if(/^(no one|nobody|none|no body|no such|no formal|no mechanism)/.test(t)) return 'broken';
  if(/no removal|cannot be removed|no procedure|no court above/.test(t)) return 'broken';
  if(/in theory|never|effectively resignation only|in practice, never|rarely/.test(t)) return 'nominal';
  return 'intact';
}
function fxApexChain(state){
  var open = state === 'broken';
  var ghost = state === 'nominal';
  /* two closed links, then the link that carries the answer */
  var s = '<svg class="fx-chain" viewBox="0 0 34 168" fill="none" aria-hidden="true" focusable="false">';
  s += '<g class="fx-lk fx-lk1"><rect x="10" y="4" width="14" height="34" rx="7" /></g>';
  s += '<g class="fx-lk fx-lk2"><rect x="10" y="30" width="14" height="34" rx="7" /></g>';
  s += '<g class="fx-lk fx-lk3"><rect x="10" y="56" width="14" height="34" rx="7" /></g>';
  if(open){
    /* the chain does not close: the last link hangs open, its end unmet */
    s += '<g class="fx-lk fx-lk4 fx-open">'
      +  '<path d="M17 82 C 10 82 10 92 10 100 L 10 112 C 10 120 13.5 124 17 124" />'
      +  '<path d="M17 82 C 24 82 24 92 24 100 L 24 108" />'
      +  '</g>';
    s += '<circle class="fx-gapdot" cx="24" cy="116" r="1.6" />';
  } else {
    s += '<g class="fx-lk fx-lk4' + (ghost ? ' fx-ghost' : '') + '">'
      +  '<rect x="10" y="82" width="14" height="34" rx="7" /></g>';
  }
  s += '</svg>';
  return s;
}
'''

# the row template, rewritten to carry the chain and its state
OLD_ROW = re.compile(
    r'\$\{A\.rows\.map\(row=>`<article class="ax">\s*'
    r'<div class="ax-office">\$\{fmt\(row\[0\]\)\}</div>\s*'
    r'<div class="ax-holder">\$\{fmt\(row\[1\]\)\}</div>\s*'
    r'<div class="ax-cols">\s*'
    r'<div><span class="st8-k">Chosen by</span><p>\$\{fmt\(row\[2\]\)\}</p></div>\s*'
    r'<div class="ax-rm"><span class="st8-k">Removable by</span><p>\$\{fmt\(row\[3\]\)\}</p></div>\s*'
    r'</div>\s*</article>`\)\.join\(\'\'\)\}', re.S)

NEW_ROW = (
    "${A.rows.map(row=>{const _s=fxApexState(row[3]);return `"
    '<article class="ax fx-ax fx-${_s}">'
    '<div class="fx-ax-chain">${fxApexChain(_s)}</div>'
    '<div class="fx-ax-body">'
    '<div class="ax-office">${fmt(row[0])}</div>'
    '<div class="ax-holder">${fmt(row[1])}</div>'
    '<div class="ax-cols">'
    '<div class="fx-rung"><span class="st8-k">Chosen by</span><p>${fmt(row[2])}</p></div>'
    '<div class="ax-rm fx-rung"><span class="st8-k">Removable by</span>'
    '<p>${fmt(row[3])}</p>'
    '<span class="fx-verdict" aria-hidden="true">'
    "${_s==='broken'?'chain open':_s==='nominal'?'never exercised':'mechanism holds'}"
    '</span>'
    '</div></div></div></article>`}).join(\'\')}'
)

CSS = r"""
/* ===================== the apex chain ===================== */
.fx-ax{display:grid;grid-template-columns:34px 1fr;gap:1.1rem;align-items:start}
.fx-ax-body{min-width:0}
.fx-ax-chain{position:sticky;top:1rem;align-self:start;line-height:0}
.fx-chain{width:34px;height:168px;overflow:visible}
.fx-chain rect,.fx-chain path{stroke:var(--gilt);stroke-width:1.15;fill:none;
  vector-effect:non-scaling-stroke}
.fx-lk3 rect{opacity:.9}
.fx-ghost rect{stroke-dasharray:3 3;opacity:.5}
.fx-open path{stroke:var(--curtain, #7E2733);stroke-width:1.4}
.fx-gapdot{fill:var(--curtain,#7E2733);opacity:.85}
.fx-broken .fx-lk1 rect,.fx-broken .fx-lk2 rect,.fx-broken .fx-lk3 rect{opacity:.55}

/* the verdict is the row's own finding, set as a label not a claim */
.fx-verdict{display:inline-block;margin-top:.45rem;
  font-family:var(--mono);font-size:.62rem;letter-spacing:.18em;text-transform:uppercase}
.fx-broken .fx-verdict{color:var(--curtain,#B04250)}
.fx-nominal .fx-verdict{color:var(--gilt)}
.fx-intact .fx-verdict{opacity:.55}
.fx-broken .ax-rm{position:relative}

@media(max-width:600px){
  .fx-ax{grid-template-columns:22px 1fr;gap:.8rem}
  .fx-chain{width:22px;height:132px}
  .fx-ax-chain{position:static}
}

/* the draw happens once, on first sight, and never repeats */
@media (prefers-reduced-motion: no-preference){
  .fx-chain.fx-arm .fx-lk rect,.fx-chain.fx-arm .fx-lk path{
    stroke-dasharray:var(--fx-len,120);stroke-dashoffset:var(--fx-len,120)}
  .fx-chain.fx-arm.fx-drawn .fx-lk rect,.fx-chain.fx-arm.fx-drawn .fx-lk path{
    stroke-dashoffset:0;
    transition:stroke-dashoffset 620ms cubic-bezier(.22,.61,.36,1)}
  .fx-chain.fx-drawn .fx-lk2 rect{transition-delay:110ms}
  .fx-chain.fx-drawn .fx-lk3 rect{transition-delay:220ms}
  .fx-chain.fx-drawn .fx-lk4 rect,.fx-chain.fx-drawn .fx-lk4 path{transition-delay:330ms}
  .fx-chain.fx-arm .fx-gapdot{opacity:0}
  .fx-chain.fx-arm.fx-drawn .fx-gapdot{opacity:.85;transition:opacity 300ms linear 900ms}
}
@media (prefers-contrast: more){
  .fx-chain rect,.fx-chain path{stroke-width:1.6}
  .fx-ghost rect{opacity:.8}
}
@media print{
  .fx-chain rect,.fx-chain path{stroke:#000!important;stroke-dashoffset:0!important}
  .fx-gapdot{fill:#000!important;opacity:1!important}
  .fx-verdict{color:#000!important}
}
"""

JS = r"""
(function(){
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function(es){
    es.forEach(function(en){
      if(!en.isIntersecting) return;
      en.target.classList.add('fx-drawn');
      io.unobserve(en.target);
    });
  },{ rootMargin:'0px 0px -8% 0px', threshold:.15 }) : null;

  /* this is a hash-routed document: every route swaps #app, so new chains
     must be armed on each render, never once at load. A chain that is never
     armed stays fully drawn — nothing can be left invisible. */
  function arm(){
    var chains = document.querySelectorAll('.fx-chain:not([data-fx])');
    if(!chains.length) return;
    chains.forEach(function(svg){
      svg.setAttribute('data-fx','1');
      if(reduced || !io) return;
      svg.querySelectorAll('rect,path').forEach(function(el){
        var len = 120;
        try{ if(el.getTotalLength) len = Math.ceil(el.getTotalLength()); }catch(e){}
        el.style.setProperty('--fx-len', len);
      });
      svg.classList.add('fx-arm');
      if(svg.getBoundingClientRect().top < innerHeight * 0.95){
        requestAnimationFrame(function(){ svg.classList.add('fx-drawn'); });
      } else {
        io.observe(svg);
      }
    });
  }
  arm();
  var app = document.getElementById('app');
  if(app && window.MutationObserver){
    new MutationObserver(function(){ arm(); }).observe(app,{childList:true,subtree:true});
  }
  addEventListener('hashchange', function(){ setTimeout(arm, 0); });
})();
"""


def build(html):
    if MARK in html:
        return html
    n = len(OLD_ROW.findall(html))
    html = OLD_ROW.sub(lambda m: NEW_ROW, html)
    # the helper must exist before any template uses it
    anchor = "function relEntryHTML(t, i, open){"
    html = html.replace(anchor, HELPER_JS + "\n" + anchor, 1)
    html = html.replace("</head>", '<style id="%s">%s</style>\n</head>' % (MARK, CSS), 1)
    i = html.rindex("</body>")
    html = html[:i] + '<script id="fx-apex-js">%s</script>\n' % JS + html[i:]
    print("  apex row templates rewritten:", n)
    return html


if __name__ == "__main__":
    import pathlib
    p = pathlib.Path(__file__).resolve().parent.parent / "faith" / "index.html"
    p.write_text(build(p.read_text(encoding="utf-8")), encoding="utf-8")
    print("  written:", p)
