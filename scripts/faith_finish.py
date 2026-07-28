#!/usr/bin/env python3
"""Passes 01, 07, 08 — motion and view transitions, micro-typography,
accessibility and print.

Motion here has one job: communicate structure and position. Route changes are
directional so hierarchy is taught without words; nothing loops, nothing
follows the cursor, nothing delays a sentence.

Typography moves to foundry rules: oldstyle figures in prose and lining tabular
figures in tables, never mixed; hanging punctuation; tracking tightened above
3rem and opened below 0.9rem; widow and orphan control on every lede and quote.

Accessibility is treated as craft: reduced motion, more contrast, reduced
transparency and forced colours are all answered, and the 12.4px floor is
never crossed.
"""
MARK = "fx-finish"

CSS = r"""
/* ============ pass 01 · motion, and only where it teaches ============ */
@view-transition{navigation:auto}
@media (prefers-reduced-motion: no-preference){
  /* deeper rises from below; returning settles from above */
  ::view-transition-old(root){animation:fx-vo 160ms cubic-bezier(.22,.61,.36,1) both}
  ::view-transition-new(root){animation:fx-vn 200ms cubic-bezier(.22,.61,.36,1) both}
  @keyframes fx-vo{to{opacity:0}}
  @keyframes fx-vn{from{opacity:0;transform:translateY(8px)}}
  html[data-fx-back]::view-transition-new(root){animation:fx-vb 200ms cubic-bezier(.22,.61,.36,1) both}
  @keyframes fx-vb{from{opacity:0;transform:translateY(-8px)}}

  /* the hub act grid: 12ms stagger, capped near 220ms */
  .acts>*{animation:fx-rise 200ms cubic-bezier(.22,.61,.36,1) both;
    animation-delay:calc(var(--fx-i,0)*12ms)}
  @keyframes fx-rise{from{opacity:0;transform:translateY(6px)}}

  /* the cold open blooms once, on entry, never on scroll */
  .coldopen{animation:fx-bloom 450ms cubic-bezier(.22,.61,.36,1) both}
  .coldopen .co-name{animation:fx-settle 260ms cubic-bezier(.22,.61,.36,1) 120ms both}
  .coldopen .co-inner p:first-of-type{animation:fx-settle 260ms cubic-bezier(.22,.61,.36,1) 200ms both}
  @keyframes fx-bloom{from{opacity:.55}}
  @keyframes fx-settle{from{opacity:0;transform:translateY(4px)}}

  /* card hover: the existing lift, plus an accent hairline that draws */
  .acts a,.card,.tile{position:relative}
  .acts a::after,.tile::after{content:"";position:absolute;left:0;top:0;bottom:0;width:2px;
    background:var(--gilt);transform:scaleY(0);transform-origin:50% 0;
    transition:transform 180ms cubic-bezier(.22,.61,.36,1)}
  .acts a:hover::after,.acts a:focus-visible::after,
  .tile:hover::after,.tile:focus-within::after{transform:scaleY(1)}

  /* <details> animate to auto height natively where it is supported */
  @supports (interpolate-size: allow-keywords){
    :root{interpolate-size:allow-keywords}
    details::details-content{block-size:0;overflow:clip;
      transition:block-size 200ms cubic-bezier(.22,.61,.36,1),content-visibility 200ms allow-discrete}
    details[open]::details-content{block-size:auto}
  }
}
@media (prefers-reduced-motion: reduce){
  ::view-transition-old(root),::view-transition-new(root){animation:none}
  .acts>*,.coldopen,.coldopen .co-name{animation:none}
  .acts a::after,.tile::after{transition:none;transform:scaleY(1);opacity:0}
  .acts a:hover::after{opacity:1}
}

/* ============ pass 07 · micro-typography ============ */
:root{font-variant-numeric:oldstyle-nums proportional-nums}
body,p,li,blockquote,dd{font-variant-numeric:oldstyle-nums proportional-nums;
  font-kerning:normal;text-rendering:optimizeLegibility}
/* tables and evidence want lining, tabular figures — never the prose set */
table,.matrix,.cmp,td,th,.evid,.mono,code,kbd,samp,.fx-mx-read,
.gbadge,.tier,.st8-k,.fx-verdict{
  font-variant-numeric:lining-nums tabular-nums}
h1,h2,h3,.display,.sec-t,.entry-title{text-wrap:balance;font-kerning:normal}
p,.lede,li,blockquote{text-wrap:pretty}
.lede,blockquote,p{orphans:2;widows:2}
/* optical sizing by hand: tighter above 3rem, opened below 0.9rem */
.display,h1{letter-spacing:-.018em}
.st8-k,.kicker,.sec-k,.gbadge,.tier,.fx-verdict,.fx-k{letter-spacing:.14em}
/* hanging punctuation where the engine offers it */
blockquote,.pull,.ax-lede{hanging-punctuation:first last}
/* real small caps where the embedded faces carry them */
.caps,.sec-k,.kicker{font-variant-caps:small-caps;font-feature-settings:"smcp" 1,"c2sc" 0}
/* the marks the document leaves behind */
::selection{background:color-mix(in srgb,var(--curtain,#8A2432) 30%,transparent);
  color:var(--ink)}
:root{caret-color:var(--curtain,#8A2432);scrollbar-color:var(--gilt) transparent;
  scrollbar-width:thin}
::marker{color:var(--gilt)}
::-webkit-scrollbar{width:11px;height:11px}
::-webkit-scrollbar-thumb{background:color-mix(in srgb,var(--gilt) 55%,transparent);
  border-radius:6px}
::-webkit-scrollbar-track{background:transparent}

/* ============ pass 08 · accessibility, then print ============ */
a:focus-visible,button:focus-visible,summary:focus-visible,
[tabindex]:focus-visible,input:focus-visible,select:focus-visible{
  outline:2px solid var(--gilt);outline-offset:2px;border-radius:2px}
/* the floor is 12.4px and nothing may sit under it */
.fineprint,.small,.st8-k,.gbadge,.tier,.fx-k,.fx-verdict,.fx-mx-read,
.sec-k,.kicker,.mono{font-size:max(0.775rem,12.4px)}
@media (prefers-contrast: more){
  a{text-decoration-thickness:from-font}
  .fx-mx-dot{outline:1px solid var(--ink)}
  :root{--vault-line:color-mix(in srgb,var(--gilt) 70%,transparent)}
}
@media (prefers-reduced-transparency: reduce){
  .fx-mx tr.fx-lit>th,.fx-mx tr.fx-lit>td,.fx-mx .fx-collit{
    background:color-mix(in srgb,var(--gilt) 22%,transparent)}
}
@media (forced-colors: active){
  .fx-mx-dot{forced-color-adjust:none;border:1px solid CanvasText}
  .fx-g-codified .fx-mx-dot{background:CanvasText}
  .fx-g-sourced .fx-mx-dot{background:GrayText}
  .fx-g-structural .fx-mx-dot{background:Canvas}
  .fx-g-none .fx-mx-dot{background:Canvas}
  .fx-chain rect,.fx-chain path{stroke:CanvasText}
  a:focus-visible{outline:2px solid Highlight}
}
@media print{
  /* every act prints as a standalone document, dark registers inverted */
  @page{margin:18mm 16mm}
  html,body{background:#fff!important;color:#000!important}
  h1,h2,h3,.display,.sec-t{break-after:avoid;page-break-after:avoid}
  p,li,blockquote,.ax,.fx-ax{break-inside:avoid;page-break-inside:avoid}
  .fx-ax{border-bottom:1px solid #000}
  .fx-mx-read,.fx-mx-tools{display:none!important}
  a[href^="#/"]::after{content:""}
  .fineprint,.st8-k{color:#333!important}
}
"""

# route direction, so motion can say "deeper" or "back" without words
JS = r"""
(function(){
  var depth = (location.hash || '').split('/').length;
  addEventListener('hashchange', function(){
    var d = (location.hash || '').split('/').length;
    if(d < depth) document.documentElement.setAttribute('data-fx-back','');
    else document.documentElement.removeAttribute('data-fx-back');
    depth = d;
  });
  /* stagger index for the act grid, set once per render */
  function idx(){
    document.querySelectorAll('.acts').forEach(function(g){
      [].slice.call(g.children).forEach(function(c,i){
        if(i < 18) c.style.setProperty('--fx-i', i);
      });
    });
  }
  idx();
  var app = document.getElementById('app');
  if(app && window.MutationObserver){
    new MutationObserver(idx).observe(app,{childList:true,subtree:true});
  }
})();
"""


def build(html):
    if MARK in html:
        return html
    html = html.replace("</head>", '<style id="%s">%s</style>\n</head>' % (MARK, CSS), 1)
    i = html.rindex("</body>")
    return html[:i] + '<script id="fx-finish-js">%s</script>\n' % JS + html[i:]


if __name__ == "__main__":
    import pathlib
    p = pathlib.Path(__file__).resolve().parent.parent / "faith" / "index.html"
    p.write_text(build(p.read_text(encoding="utf-8")), encoding="utf-8")
    print("  written:", p)
