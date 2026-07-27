#!/usr/bin/env python3
"""The Descent — compositional rebuild of The Root.

The practice already had its metaphor: you follow one reaction *down* to the
belief underneath it. Nothing on the page moved downward. Now the whole
surface does — a plumb line drops beside you, a brass bob marks how deep you
are, the ground darkens as you descend, and each new question rises past you
from below.

Only the presentation generators are re-emitted — `shell`, `renderRail`, and
the record's markup. The branching engine, the sixteen themes, the storage
layer, the step graph and every handler are untouched.
"""
import re

MARK = "rt-descent"

# ---------------------------------------------------------------- generators
SHELL_JS = r'''function shell(eyebrow,question,bodyHtml,opts){
  opts=opts||{};
  var d=history.length;
  stage.innerHTML=`<div class="card rt-card">
    <p class="eyebrow rt-depth"><span class="rt-depth-mark" aria-hidden="true"></span>${esc(eyebrow)}</p>
    <h2 class="question rt-question">${question}</h2>
    ${opts.subtext?`<p class="subtext rt-sub">${opts.subtext}</p>`:""}
    ${bodyHtml}
  </div>`;
}'''

RAIL_JS = r'''function renderRail(){
  const rail=document.getElementById("rail");
  const mob=document.getElementById("railMobile");
  rail.innerHTML="";mob.innerHTML="";
  document.documentElement.style.setProperty("--rt-depth",
    Math.min(1,(history.length-1)/13).toFixed(3));
  history.forEach(function(h,i){
    const isBranch=branchSteps.has(h);
    const last=i===history.length-1;
    if(i>0){const line=document.createElement("div");line.className="rail-line rt-rope";rail.appendChild(line);}
    const node=document.createElement("div");
    node.className="rail-node rt-node lit"+(isBranch?" branch":"")+(last?" rt-bob":"");
    rail.appendChild(node);
    const dot=document.createElement("i");
    dot.className="lit"+(last?" rt-dot-now":"");mob.appendChild(dot);
  });
  const tail=document.createElement("div");
  tail.className="rt-rope-tail";rail.appendChild(tail);
}'''


def rebuild_record(html):
    """The record stops being a text box and becomes a written page."""
    old = re.search(
        r'stage\.innerHTML=`<div class="card record-wrap">.*?</div>`;',
        html, re.S)
    if not old:
        return html
    new = ('stage.innerHTML=`<div class="card record-wrap rt-leaf">'
           '<div class="rt-leaf-head">'
           '<p class="eyebrow rt-depth"><span class="rt-depth-mark" aria-hidden="true"></span>'
           'Finished &middot; the record</p>'
           '<h2 class="question rt-question rt-leaf-t">One thread, followed all the way down.</h2>'
           '</div>'
           '<div class="record-box rt-page">${esc(record)}'
           '<span class="rt-page-seal" aria-hidden="true">NF</span></div>'
           '${returning}'
           '<p class="closing-line rt-closing">Your reactions are the map. '
           'This was one line on it.</p>'
           '<div class="actions rt-actions">'
           '<button class="btn" id="copyBtn">Copy the record</button>'
           '<button class="btn ghost" id="dlBtn">Download .txt</button>'
           '<button class="btn ghost" id="againBtn">Begin a new thread</button>'
           '</div>'
           '<p class="small-print rt-fine">Everything above stays only in this browser, '
           'on this device. Nothing was sent anywhere.</p>'
           '</div>`;')
    return html[:old.start()] + new + html[old.end():]


# --------------------------------------------------------------------- CSS
CSS = r"""
/* ==================== THE DESCENT — The Root ==================== */
:root{--rt-depth:0;--rt-ease:cubic-bezier(.2,.7,.2,1)}

/* the ground darkens as the thread is followed down */
body::before{
  background:
    radial-gradient(1100px 650px at 78% -8%,
      rgba(217,150,74,calc(.09 - var(--rt-depth)*.055)), transparent 60%),
    radial-gradient(900px 600px at -8% 108%,
      rgba(185,95,61,calc(.07 - var(--rt-depth)*.04)), transparent 55%),
    linear-gradient(180deg, transparent, rgba(6,4,3,calc(var(--rt-depth)*.55)));
  transition:background 1.1s var(--rt-ease)}

/* ---- chrome ---- */
.topbar{padding:20px 22px 14px}
.wordmark{font-size:16px;letter-spacing:.005em;gap:10px}
.wordmark .sub{letter-spacing:.2em;font-size:9.5px}
.resetlink{font-family:var(--sans);font-size:10px;letter-spacing:.18em;
  text-transform:uppercase;text-decoration:none;padding:8px 13px;border-radius:999px;
  border:1px solid var(--line);transition:border-color .24s var(--rt-ease),
  color .24s var(--rt-ease)}
.resetlink:hover{border-color:var(--candle);color:var(--candle)}

/* ---- the plumb line ---- */
.rail{width:30px;margin-right:16px;padding-top:14px;justify-content:flex-start}
.rt-rope{width:1px;min-height:26px;flex:0 0 auto;
  background:linear-gradient(180deg,rgba(217,150,74,.55),rgba(217,150,74,.22));
  border-radius:0}
.rt-rope-tail{width:1px;flex:1 1 auto;min-height:40px;
  background:linear-gradient(180deg,rgba(237,226,204,.16),transparent)}
.rt-node{width:7px;height:7px;border-width:1px;
  background:var(--candle);border-color:var(--candle);
  box-shadow:0 0 9px rgba(217,150,74,.55)}
.rt-node.branch{width:8px;height:8px;background:var(--sage);border-color:var(--sage);
  box-shadow:0 0 9px rgba(143,175,155,.6)}
/* the weight at the end of the line — where you are now */
.rt-node.rt-bob{width:15px;height:15px;border-radius:50%;
  background:radial-gradient(circle at 35% 30%,#F0DCAE,#D9964A 55%,#8A5A20);
  border:none;box-shadow:0 0 0 4px rgba(217,150,74,.13),0 0 20px rgba(217,150,74,.6),
    0 5px 12px rgba(0,0,0,.6);
  transform:none}
.rt-node.rt-bob.branch{background:radial-gradient(circle at 35% 30%,#CFE3D4,#8FAF9B 55%,#4E6B58);
  box-shadow:0 0 0 4px rgba(143,175,155,.13),0 0 20px rgba(143,175,155,.55),
    0 5px 12px rgba(0,0,0,.6)}
@media (prefers-reduced-motion: no-preference){
  .rt-node.rt-bob{animation:rt-bob-in 520ms cubic-bezier(.34,1.4,.5,1) both}
  @keyframes rt-bob-in{from{transform:translateY(-9px) scale(.5);opacity:0}
    to{transform:none;opacity:1}}
}
/* mobile: a depth gauge rather than a row of dots */
.stage-mobile-progress{gap:0;align-items:center;margin-bottom:26px;
  padding-bottom:14px;border-bottom:1px solid var(--line)}
.stage-mobile-progress i{width:14px;height:1.5px;border-radius:0;background:rgba(217,150,74,.32)}
.stage-mobile-progress i.rt-dot-now{width:9px;height:9px;border-radius:50%;margin-left:5px;
  background:radial-gradient(circle at 35% 30%,#F0DCAE,#D9964A 60%,#8A5A20);
  box-shadow:0 0 12px rgba(217,150,74,.65)}

/* ---- the question is the room ---- */
.rt-card{max-width:640px}
@media (prefers-reduced-motion: no-preference){
  .card{animation:rt-rise .62s cubic-bezier(.16,1,.3,1) both}
  @keyframes rt-rise{from{opacity:0;transform:translateY(26px);filter:blur(6px)}
    to{opacity:1;transform:none;filter:none}}
}
.rt-depth{display:flex;align-items:center;gap:10px;margin-bottom:20px;
  font-size:10px;letter-spacing:.26em;text-transform:uppercase;color:var(--candle);
  font-weight:600}
.rt-depth-mark{width:16px;height:1px;background:linear-gradient(90deg,var(--candle),transparent);
  flex:none}
.rt-question{font-size:clamp(27px,5.6vw,40px);font-weight:500;line-height:1.16;
  letter-spacing:-.024em;color:var(--parchment);text-wrap:balance;
  font-variation-settings:"SOFT" 0,"WONK" 0}
.rt-sub{margin-top:16px;font-size:15px;line-height:1.68;color:var(--muted);max-width:50ch}

/* ---- inputs ---- */
textarea,input[type=text]{border-radius:4px;background:rgba(255,255,255,.022);
  border:1px solid var(--line-strong);font-size:16px;padding:16px 18px;
  transition:border-color .26s var(--rt-ease),box-shadow .26s var(--rt-ease),
    background .26s var(--rt-ease)}
textarea:focus,input:focus{background:rgba(255,255,255,.04);
  box-shadow:0 0 0 3px rgba(217,150,74,.1),0 10px 30px -14px rgba(0,0,0,.7)}
.field{margin-top:30px}

/* ---- answers ---- */
.opts{gap:10px;margin-top:26px}
.opt{border-radius:3px;padding:13px 19px;font-size:15px;font-weight:400;
  background:rgba(255,255,255,.018);border-color:var(--line);letter-spacing:.004em;
  transition:transform .2s var(--rt-ease),border-color .2s,color .2s,background .2s,
    box-shadow .2s}
.opt:hover{transform:translateY(-1px);border-color:var(--candle);
  box-shadow:0 8px 22px -12px rgba(217,150,74,.5)}
.opt:active{transform:translateY(0) scale(.99)}
.opt.sel{background:rgba(217,150,74,.1);border-color:var(--candle);
  box-shadow:inset 0 0 0 1px rgba(217,150,74,.28)}
.opt.wide{border-radius:4px}

/* ---- the insight, set as a margin note rather than a slab ---- */
.insight{position:relative;background:none;border:0;border-radius:0;
  margin-top:26px;padding:2px 0 2px 26px;font-size:15px;line-height:1.72;
  color:var(--muted);font-family:var(--serif);font-style:italic}
.insight::before{content:"";position:absolute;left:0;top:6px;bottom:6px;width:1px;
  background:linear-gradient(180deg,var(--candle),transparent)}
.insight::after{content:"";position:absolute;left:-3px;top:8px;width:7px;height:7px;
  transform:rotate(45deg);background:var(--candle);
  box-shadow:0 0 10px rgba(217,150,74,.6)}
.insight.sage::before{background:linear-gradient(180deg,var(--sage),transparent)}
.insight.sage::after{background:var(--sage);box-shadow:0 0 10px rgba(143,175,155,.6)}
.insight.violet::before{background:linear-gradient(180deg,var(--violet),transparent)}
.insight.violet::after{background:var(--violet);box-shadow:0 0 10px rgba(178,150,220,.6)}
.insight em{color:var(--parchment);font-style:normal;font-weight:500}

/* ---- actions ---- */
.actions{margin-top:34px;gap:12px}
.btn{border-radius:999px;padding:14px 30px;font-size:14px;letter-spacing:.02em;
  background:linear-gradient(168deg,#EFAE63,#D9964A 46%,#B87A32);
  color:#1A1008;box-shadow:0 10px 26px -12px rgba(217,150,74,.6)}
.btn:hover{transform:translateY(-2px);box-shadow:0 16px 34px -14px rgba(217,150,74,.7)}
.btn.ghost{background:none;color:var(--parchment);border:1px solid var(--line-strong);
  box-shadow:none}
.backlink{font-size:12px;letter-spacing:.16em;text-transform:uppercase}
.skip{font-size:11px;letter-spacing:.16em;text-transform:uppercase;text-decoration:none;
  border-bottom:1px solid var(--line-strong);padding-bottom:3px}

/* ---- the tally reads as a balance ---- */
.two-col{gap:22px;margin-top:28px}
.tally-col h4{letter-spacing:.2em;font-size:10px;padding-bottom:10px;
  border-bottom:1px solid var(--line)}
.tally-col li{background:rgba(255,255,255,.02);border-color:var(--line);border-radius:3px;
  font-size:14px;padding:10px 13px}
.tallyline{font-family:var(--sans);font-size:10.5px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--dim);margin-top:20px;
  padding-top:14px;border-top:1px solid var(--line)}

/* ---- the record, as a leaf of paper ---- */
.rt-leaf{max-width:680px}
.rt-leaf-head{margin-bottom:26px}
.rt-leaf-t{font-size:clamp(22px,4vw,30px)!important}
.rt-page{position:relative;border-radius:3px;padding:38px 34px 54px;
  background:linear-gradient(174deg,#171009,#120C07 70%,#0D0805);
  border:1px solid rgba(217,150,74,.22);
  box-shadow:inset 0 1px 0 rgba(240,220,174,.07),0 26px 60px -26px rgba(0,0,0,.9);
  font-family:var(--serif);font-size:14.5px;line-height:1.9;color:#DCD2BC;
  letter-spacing:.004em}
.rt-page::before{content:"";position:absolute;left:0;right:0;top:0;height:2px;
  background:linear-gradient(90deg,transparent,rgba(217,150,74,.5),transparent)}
.rt-page-seal{position:absolute;right:22px;bottom:18px;width:38px;height:38px;
  border-radius:50%;display:grid;place-items:center;
  font-family:var(--serif);font-size:12px;font-weight:600;color:#F2E6D2;
  background:radial-gradient(circle at 34% 28%,#C4564A,#8E2B26 62%,#6B1F1B);
  box-shadow:inset 0 1px 2px rgba(255,255,255,.22),0 4px 12px rgba(0,0,0,.6);
  opacity:.92}
.rt-closing{font-size:15px;color:var(--dim);margin-top:26px;
  padding-left:20px;border-left:1px solid var(--line-strong)}
.rt-actions{margin-top:30px}
.rt-fine{font-size:10.5px;letter-spacing:.1em;color:var(--dim);margin-top:22px}
.returning{border-radius:4px;border-color:rgba(143,175,155,.3);
  background:rgba(143,175,155,.07)}

@media(max-width:560px){
  .topbar{padding:14px 16px 10px;gap:12px;align-items:flex-start}
  .wordmark{flex-direction:column;align-items:flex-start;gap:3px;font-size:15px}
  .wordmark .sub{font-size:8.5px;letter-spacing:.15em}
  .resetlink{font-size:9px;padding:7px 11px;white-space:nowrap;flex:none}
  .rt-question{font-size:clamp(24px,7vw,31px)}
  .rt-page{padding:26px 20px 46px;font-size:13.5px}
}

@media (prefers-reduced-motion: reduce){
  body::before,.card,.rt-node.rt-bob{transition:none;animation:none}
  .opt:hover,.btn:hover{transform:none}
}
"""


def build(html):
    if MARK in html:
        return html
    html = re.sub(r'function shell\(eyebrow,question,bodyHtml,opts\)\{.*?\n\}',
                  lambda m: SHELL_JS, html, count=1, flags=re.S)
    html = re.sub(r'function renderRail\(\)\{.*?\n\}',
                  lambda m: RAIL_JS, html, count=1, flags=re.S)
    html = rebuild_record(html)
    html = html.replace("</head>", '<style id="%s">%s</style>\n</head>' % (MARK, CSS), 1)
    return html
