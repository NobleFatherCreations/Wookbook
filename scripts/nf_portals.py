#!/usr/bin/env python3
"""The Vitrine — boutique rebuild of The Portals.

The page already carried the right asset: every pendant is photographed
twice, in daylight and glowing. That pairing is the product's whole promise,
and it was buried behind a hover state. Here it becomes the centrepiece: a
brass Light Line you drag across the piece to take the room dark.

Only the presentation generators (`reveal`, `panelHTML`, the rail card) are
re-emitted. SETS, IMG, the rotator navigation, the drawer, the global night
switch and every event contract are left exactly as they were.
"""
import re

MARK = "pv-vitrine"

# --------------------------------------------------------------- generators
REVEAL_JS = r'''function reveal(day,glow,cls,tag){
  return '<div class="reveal pv-piece '+cls+'" data-piece>'
    +'<img class="glow" loading="lazy" decoding="async" src="'+glow+'" alt="the same pendant glowing in the dark">'
    +'<img class="day" loading="lazy" decoding="async" src="'+day+'" alt="the pendant in daylight">'
    +(tag?'<span class="pv-tag">'+tag+'</span>':'')+'</div>';
}
function heroReveal(day,glow){
  return '<div class="reveal pv-piece pv-hero r45" data-piece data-wipe style="--wipe:62%">'
    +'<img class="glow" decoding="async" src="'+glow+'" alt="the same pendant glowing in the dark">'
    +'<img class="day" decoding="async" src="'+day+'" alt="the pendant in daylight">'
    +'<span class="pv-line" aria-hidden="true"><span class="pv-knob"></span></span>'
    +'<span class="pv-daymark" aria-hidden="true">Day</span>'
    +'<span class="pv-nightmark" aria-hidden="true">Night</span>'
    +'</div>';
}'''

PANEL_JS = r'''function panelHTML(s){var im=IMG[s.id];
  var layers=s.layers.map(function(l){
    return '<li class="pv-layer"><span class="pv-layer-n">'+l.n+'</span>'
      +'<div class="pv-layer-b"><h4 class="pv-layer-t">'+l.name+'</h4><p>'+l.d+'</p></div></li>';
  }).join('');
  var car=im.car.map(function(c){return reveal(c.day,c.glow,'pv-thumb sq','Tap to glow');}).join('');
  var article=(/^the\s/i.test(s.name)?'':'The ')+s.name+' Set';
  return '<div class="panel pv-panel" style="--sglow:'+s.glow+'"><div class="pv-inner">'

  /* masthead */
  +'<header class="pv-mast">'
    +'<p class="pv-kicker"><span class="pv-gem"></span>'+article+'</p>'
    +'<h3 class="pv-name">'+s.name+'</h3>'
    +'<p class="pv-tagline">'+s.tag+'</p>'
    +'<p class="pv-intro">'+s.intro+'</p>'
  +'</header>'

  /* the case: the piece under glass, and its composition beside it */
  +'<div class="showcase pv-showcase">'
    +'<div class="pic pv-case">'
      +'<div class="pv-plinth">'+heroReveal(im.heroDay,im.heroGlow)+'</div>'
      +'<p class="pv-drag-hint">Drag the line across the piece</p>'
      +'<div class="mini pv-mini" data-mini>'
        +'<button data-d class="on">Daylight</button><button data-g>Lights out</button>'
      +'</div>'
      +'<p class="pcap pv-cap">One example &middot; every piece is one of one</p>'
    +'</div>'
    +'<div class="lay pv-spec">'
      +'<div class="pv-spec-head"><span class="pv-spec-t">Composition</span>'
      +'<span class="pv-spec-s">described in the order it is poured</span></div>'
      +'<ol class="pv-layers">'+layers+'</ol>'
    +'</div>'
  +'</div>'

  /* the apex — the lights-out promise, given its own room */
  +'<figure class="apex pv-apex">'
    +'<figcaption class="pv-apex-e">The Apex Reveal</figcaption>'
    +'<blockquote class="pv-apex-q">'+s.apex+'</blockquote>'
  +'</figure>'

  /* the rest of the set */
  +'<section class="variety pv-variety">'
    +'<div class="pv-var-head"><h4>More from the '+s.name.replace(/^THE\s+/i,'')+' set</h4>'
    +'<p>Four of roughly thirty &mdash; tap any piece to wake it</p></div>'
    +'<div class="car pv-grid">'+car+'</div>'
  +'</section>'

  /* enquiry */
  +'<aside class="set-cta pv-enquire">'
    +'<div class="pv-enq-b">'
      +'<p class="pv-enq-k">Availability</p>'
      +'<h4 class="pv-enq-t">Around thirty pieces in the '+s.name.replace(/^THE\s+/i,'')+' set</h4>'
      +'<p class="pv-enq-c">Each set begins as a limited run of roughly thirty one-of-one pendants — no two alike. What you see here is only a glimpse. Message me to see the full set and what is still available right now.</p>'
    +'</div>'
    +'<div class="links pv-enq-l">'
      +'<a class="pv-btn pv-btn-p" href="'+LINKS.email+'">Enquire by email</a>'
      +'<a class="pv-btn" href="'+LINKS.tiktok+'" target="_blank" rel="noopener">TikTok</a>'
      +'<a class="pv-btn" href="'+LINKS.fb+'" target="_blank" rel="noopener">Facebook</a>'
    +'</div>'
  +'</aside>'
+'</div></div>';}'''

RAIL_JS = (r'''rail.innerHTML=SETS.map(function(s,i){'''
           r'''return '<button class="rcard pv-rcard" data-i="'+i+'" style="--gc:'+s.glow+'">'''
           r'''<span class="pv-rgem"></span><span class="rn">'+(i<9?'0':'')+(i+1)+'</span>'''
           r'''<span class="rt">'+s.name+'</span></button>';}).join('');''')

# ------------------------------------------------------------------ the wipe
WIPE_JS = r"""
(function(){
  var reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('[data-wipe]').forEach(function(el){
    var drag=false;
    function at(x){
      var r=el.getBoundingClientRect();
      var p=Math.min(100,Math.max(0,((x-r.left)/r.width)*100));
      el.style.setProperty('--wipe',p.toFixed(2)+'%');
      el.classList.add('pv-wiping');
    }
    el.addEventListener('pointerdown',function(e){
      drag=true;el.classList.add('pv-dragging');
      try{el.setPointerCapture(e.pointerId)}catch(_){}
      at(e.clientX);e.preventDefault();
    });
    el.addEventListener('pointermove',function(e){if(drag)at(e.clientX)});
    ['pointerup','pointercancel','lostpointercapture'].forEach(function(t){
      el.addEventListener(t,function(){drag=false;el.classList.remove('pv-dragging')});
    });
    el.addEventListener('keydown',function(e){
      var cur=parseFloat(el.style.getPropertyValue('--wipe'))||62;
      if(e.key==='ArrowLeft'||e.key==='ArrowRight'){
        cur+=(e.key==='ArrowLeft'?-8:8);
        el.style.setProperty('--wipe',Math.min(100,Math.max(0,cur))+'%');
        el.classList.add('pv-wiping');e.preventDefault();
      }
    });
    el.setAttribute('tabindex','0');
    el.setAttribute('role','slider');
    el.setAttribute('aria-label','Drag to move the light across the pendant');
  });
  // the segmented control drives the same line, so both controls agree
  function slide(p,to){
    if(!p)return;
    p.classList.remove('pv-dragging');
    p.style.setProperty('--wipe',to);
  }
  document.querySelectorAll('[data-mini]').forEach(function(m){
    var sc=m.closest('.showcase');
    var piece=sc&&sc.querySelector('[data-wipe]');
    if(!piece)return;
    var d=m.querySelector('[data-d]'),g=m.querySelector('[data-g]');
    if(d)d.addEventListener('click',function(){slide(piece,'100%')});
    if(g)g.addEventListener('click',function(){slide(piece,'0%')});
  });
  var sw=document.getElementById('tbSwitch');
  if(sw)sw.addEventListener('click',function(){
    setTimeout(function(){
      var on=document.body.classList.contains('night');
      document.querySelectorAll('[data-wipe]').forEach(function(p){
        slide(p,on?'0%':'62%');
      });
    },0);
  });
})();
"""

# --------------------------------------------------------------------- CSS
CSS = r"""
/* ===================== THE VITRINE — Portals boutique ===================== */
.pv-panel{--pv-ease:cubic-bezier(.2,.7,.2,1);padding:8px 0 10px}
/* the stage sits outside .wrap, so the panel carries its own measure */
.pv-inner{box-sizing:border-box;max-width:1180px;margin-inline:auto;
  padding-inline:clamp(20px,5vw,56px)}

/* ---- set masthead ---- */
.pv-mast{max-width:660px;margin:0 auto 60px;text-align:center}
.pv-kicker{display:inline-flex;align-items:center;gap:10px;margin:0 0 18px;
  font-family:var(--label);font-size:.62rem;letter-spacing:.34em;text-transform:uppercase;
  color:var(--cream-dim)}
.pv-gem{width:7px;height:7px;border-radius:50%;background:var(--sglow,#7fe39a);
  box-shadow:0 0 10px var(--sglow,#7fe39a);flex:none}
.pv-name{font-family:var(--display);font-size:clamp(2.7rem,8.5vw,5rem);font-weight:600;
  letter-spacing:.055em;line-height:.98;margin:0;color:var(--cream)}
.pv-tagline{margin:16px auto 0;max-width:34ch;font-family:var(--display);font-style:italic;
  font-size:clamp(1.08rem,2.5vw,1.42rem);line-height:1.42;color:var(--gold)}
.pv-intro{margin:22px auto 0;max-width:56ch;font-size:.98rem;line-height:1.78;
  color:var(--cream-dim)}
.pv-intro em{color:var(--cream);font-style:italic}

/* ---- the case ---- */
.pv-showcase{gap:clamp(34px,5vw,68px);align-items:flex-start}
.pv-case{max-width:420px;flex:1 1 330px;min-width:0;width:100%}
/* the plinth: a lit surface the piece stands on */
.pv-plinth{position:relative;padding:0 0 26px;width:100%}
.pv-plinth .pv-hero{width:100%}
.pv-plinth::after{content:"";position:absolute;left:8%;right:8%;bottom:6px;height:30px;
  border-radius:50%;background:radial-gradient(ellipse at 50% 0%,rgba(0,0,0,.72),transparent 72%);
  filter:blur(8px)}

.pv-hero{border-radius:16px;cursor:ew-resize;touch-action:pan-y;
  box-shadow:0 30px 80px -24px rgba(0,0,0,.85),0 0 0 1px rgba(201,162,75,.16)}
.pv-hero:focus-visible{outline:2px solid var(--gold);outline-offset:4px}
/* The piece arrives already half-dark: daylight on one side of the line,
   the hidden sun on the other. That duality is the entire product. */
.pv-hero .day{
  -webkit-clip-path:inset(0 calc(100% - var(--wipe,62%)) 0 0);
  clip-path:inset(0 calc(100% - var(--wipe,62%)) 0 0);
  transition:clip-path .2s linear,opacity 1.05s ease}
.pv-hero.pv-dragging .day{transition:none}
/* hover no longer flips the piece — the line owns the reveal */
.pv-hero.lit .day{opacity:1}
.pv-line{position:absolute;top:0;bottom:0;left:var(--wipe,62%);width:1px;z-index:4;
  background:linear-gradient(180deg,transparent,rgba(240,220,174,.92) 12%,
    rgba(240,220,174,.92) 88%,transparent);
  box-shadow:0 0 12px rgba(232,200,121,.8);opacity:.62;
  transition:opacity .3s var(--pv-ease)}
.pv-hero:hover .pv-line,.pv-hero.pv-dragging .pv-line,
.pv-hero:focus-visible .pv-line{opacity:1}
.pv-knob{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:34px;height:34px;border-radius:50%;
  background:radial-gradient(circle at 34% 30%,#F4E2B4,#C9A35B 58%,#8E6B2F);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.5),0 4px 14px rgba(0,0,0,.7),
    0 0 0 1px rgba(0,0,0,.35)}
.pv-knob::after{content:"";position:absolute;inset:0;margin:auto;width:13px;height:7px;
  background:
    linear-gradient(90deg,rgba(20,14,8,.85) 1px,transparent 1px) 0 0/4px 100%;
  opacity:.85}
.pv-hero.pv-dragging{cursor:grabbing}
.pv-hero.pv-dragging .pv-knob{transform:translate(-50%,-50%) scale(1.1)}
.pv-daymark,.pv-nightmark{position:absolute;bottom:12px;z-index:4;
  font-family:var(--label);font-size:.54rem;letter-spacing:.24em;text-transform:uppercase;
  color:rgba(240,232,214,.72);text-shadow:0 1px 5px rgba(0,0,0,.9);
  opacity:.6;transition:opacity .3s var(--pv-ease);pointer-events:none}
.pv-daymark{left:14px}.pv-nightmark{right:14px}
.pv-hero:hover .pv-daymark,.pv-hero:hover .pv-nightmark{opacity:1}

.pv-drag-hint{margin:0 0 16px;text-align:center;font-family:var(--label);
  font-size:.58rem;letter-spacing:.22em;text-transform:uppercase;color:var(--cream-dim);
  opacity:.85}

/* segmented control, not two buttons */
.pv-mini{display:inline-flex;margin:0 auto;padding:3px;gap:2px;border-radius:999px;
  background:rgba(255,255,255,.03);border:1px solid rgba(201,162,75,.22)}
.pv-case{display:flex;flex-direction:column;align-items:center}
.pv-mini button{appearance:none;border:0;cursor:pointer;background:none;border-radius:999px;
  padding:9px 17px;font-family:var(--label);font-size:.6rem;letter-spacing:.19em;
  text-transform:uppercase;color:var(--cream-dim);
  transition:background .24s var(--pv-ease),color .24s var(--pv-ease)}
.pv-mini button.on{background:rgba(201,162,75,.16);color:var(--cream)}
.pv-mini button.g.on{background:color-mix(in srgb,var(--sglow) 22%,transparent);
  color:#F2EEE2}
.pv-mini button:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.pv-cap{margin:16px 0 0;text-align:center;font-family:var(--label);font-size:.56rem;
  letter-spacing:.2em;text-transform:uppercase;color:var(--cream-dim);opacity:.8}

/* ---- composition, set like a jeweller's certificate ---- */
.pv-spec{flex:1 1 360px;min-width:0}
.pv-spec-head{display:flex;flex-direction:column;gap:5px;padding-bottom:16px;
  border-bottom:1px solid rgba(201,162,75,.26);margin-bottom:6px}
.pv-spec-t{font-family:var(--display);font-size:1.32rem;color:var(--cream);letter-spacing:.02em}
.pv-spec-s{font-family:var(--label);font-size:.56rem;letter-spacing:.2em;text-transform:uppercase;
  color:var(--cream-dim)}
.pv-layers{list-style:none;margin:0;padding:0}
.pv-layer{display:grid;grid-template-columns:44px 1fr;gap:16px;align-items:start;
  padding:22px 0;border-bottom:1px solid rgba(201,162,75,.1)}
.pv-layer-n{font-family:var(--display);font-size:1.02rem;letter-spacing:.06em;
  color:var(--sglow,#7fe39a);opacity:.9;padding-top:2px;
  border-right:1px solid rgba(201,162,75,.18);height:100%}
.pv-layer-t{margin:0 0 8px;font-family:var(--display);font-size:1.14rem;font-weight:600;
  letter-spacing:.02em;color:var(--cream)}
.pv-layer-b p{margin:0;font-size:.92rem;line-height:1.72;color:var(--cream-dim)}

/* ---- the apex ---- */
.pv-apex{position:relative;max-width:880px;margin:clamp(52px,7vw,84px) auto 0;
  padding:clamp(38px,5vw,62px) clamp(24px,4vw,52px);
  border-radius:18px;overflow:hidden;text-align:center;
  background:linear-gradient(168deg,rgba(255,255,255,.035),rgba(0,0,0,.34));
  border:1px solid rgba(201,162,75,.18)}
.pv-apex::before{content:"";position:absolute;left:50%;top:-38%;width:min(80%,540px);
  aspect-ratio:1;transform:translateX(-50%);pointer-events:none;
  background:radial-gradient(circle,color-mix(in srgb,var(--sglow) 26%,transparent),transparent 68%);
  filter:blur(28px);opacity:.9}
.pv-apex-e{position:relative;font-family:var(--label);font-size:.58rem;letter-spacing:.34em;
  text-transform:uppercase;color:var(--sglow,#7fe39a);margin-bottom:20px}
.pv-apex-q{position:relative;margin:0;max-width:46ch;margin-inline:auto;
  font-family:var(--display);font-style:italic;font-size:clamp(1.16rem,2.7vw,1.66rem);
  line-height:1.5;color:var(--cream);text-wrap:balance}

/* ---- more from the set ---- */
.pv-variety{margin-top:clamp(48px,6vw,76px)}
.pv-var-head{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;
  gap:10px;padding-bottom:16px;margin-bottom:22px;
  border-bottom:1px solid rgba(201,162,75,.18)}
.pv-var-head h4{margin:0;font-family:var(--display);font-size:1.24rem;font-weight:600;
  color:var(--cream);letter-spacing:.02em}
.pv-var-head p{margin:0;font-family:var(--label);font-size:.56rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--cream-dim)}
.pv-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;
  overflow:visible;scroll-snap-type:none;padding:0}
@media(max-width:720px){.pv-grid{grid-template-columns:repeat(2,1fr);gap:11px}}
.pv-thumb{border-radius:12px;transition:transform .4s var(--pv-ease),box-shadow .4s var(--pv-ease)}
.pv-thumb:hover{transform:translateY(-4px)}
.pv-tag{position:absolute;left:9px;bottom:9px;z-index:5;
  font-family:var(--label);font-size:.5rem;letter-spacing:.18em;text-transform:uppercase;
  color:rgba(240,232,214,.8);text-shadow:0 1px 5px rgba(0,0,0,.9);
  opacity:0;transition:opacity .3s var(--pv-ease)}
.pv-thumb:hover .pv-tag{opacity:1}

/* ---- enquiry ---- */
.pv-enquire{display:grid;gap:clamp(22px,3vw,44px);align-items:center;text-align:left;
  grid-template-columns:1fr;margin-top:clamp(48px,6vw,76px);
  padding:clamp(28px,4vw,46px);border-radius:18px;
  background:linear-gradient(168deg,rgba(255,255,255,.03),transparent);
  border:1px solid rgba(201,162,75,.2)}
@media(min-width:860px){.pv-enquire{grid-template-columns:1.5fr auto}}
.pv-enq-k{margin:0 0 12px;font-family:var(--label);font-size:.56rem;letter-spacing:.3em;
  text-transform:uppercase;color:var(--sglow,#7fe39a)}
.pv-enq-t{margin:0 0 14px;font-family:var(--display);font-size:clamp(1.3rem,2.8vw,1.86rem);
  font-weight:600;line-height:1.2;color:var(--cream);letter-spacing:.01em;text-wrap:balance}
.pv-enq-c{margin:0;max-width:54ch;font-size:.93rem;line-height:1.74;color:var(--cream-dim)}
.pv-enq-l{display:flex;flex-wrap:wrap;gap:10px}
.pv-btn{display:inline-flex;align-items:center;justify-content:center;text-decoration:none;
  padding:13px 22px;border-radius:999px;white-space:nowrap;
  border:1px solid rgba(201,162,75,.34);color:var(--cream);
  font-family:var(--label);font-size:.6rem;letter-spacing:.2em;text-transform:uppercase;
  transition:border-color .26s var(--pv-ease),background .26s var(--pv-ease),
    transform .26s var(--pv-ease)}
.pv-btn:hover{border-color:var(--gold);background:rgba(201,162,75,.1);transform:translateY(-2px)}
.pv-btn-p{background:linear-gradient(168deg,#E8C879,#C9A35B 62%,#A8813A);
  border-color:transparent;color:#1A130A;font-weight:700}
.pv-btn-p:hover{background:linear-gradient(168deg,#F4E2B4,#D4AF63 62%,#B58C42);
  box-shadow:0 12px 30px -12px rgba(201,163,91,.6)}

/* ---- the rail, as a row of set tabs ---- */
.pv-rcard{display:flex;align-items:center;gap:9px;min-width:auto;
  padding:10px 15px;border-radius:999px;
  transition:border-color .26s var(--pv-ease),background .26s var(--pv-ease),
    color .26s var(--pv-ease)}
.pv-rgem{width:6px;height:6px;border-radius:50%;background:var(--gc);flex:none;
  box-shadow:0 0 8px var(--gc);opacity:.6;transition:opacity .26s}
.pv-rcard .rn{font-family:var(--label);font-size:.54rem;letter-spacing:.14em;
  color:var(--cream-dim);opacity:.75}
.pv-rcard .rt{font-family:var(--display);font-size:.86rem;letter-spacing:.09em}
.pv-rcard:hover{border-color:rgba(201,162,75,.5);color:var(--cream)}
.pv-rcard.active .pv-rgem{opacity:1}
.pv-rcard.active{background:rgba(201,162,75,.12);border-color:rgba(201,162,75,.55);
  color:var(--cream)}

/* ---- the page hero, as a shopfront ---- */
.site-hero{position:relative;overflow:hidden;isolation:isolate}
.site-hero>.hero-banner{position:absolute;top:0;left:0;width:100%;height:auto;z-index:-1;
  opacity:.26;margin:0;
  -webkit-mask-image:linear-gradient(180deg,#000 0%,rgba(0,0,0,.5) 52%,transparent 88%);
  mask-image:linear-gradient(180deg,#000 0%,rgba(0,0,0,.5) 52%,transparent 88%)}
.site-hero::after{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;
  background:
    radial-gradient(72% 50% at 50% 46%,rgba(10,10,12,.66),transparent 76%),
    radial-gradient(120% 84% at 50% 20%,transparent 32%,rgba(10,10,12,.72) 88%)}
.site-hero h1{letter-spacing:.08em;text-wrap:balance}
.site-hero .tag{text-wrap:balance}
.site-hero .scrollcue{position:relative;padding-bottom:26px;letter-spacing:.3em}
.site-hero .scrollcue::after{content:"";position:absolute;left:50%;bottom:0;width:1px;height:20px;
  background:linear-gradient(180deg,rgba(201,162,75,.85),transparent)}

@media (prefers-reduced-motion: no-preference){
  .site-hero .scrollcue::after{animation:pv-cue 2.6s ease-in-out infinite}
  @keyframes pv-cue{0%,100%{transform:translateY(0);opacity:.9}50%{transform:translateY(6px);opacity:.35}}
  .pv-mast>*{animation:pv-rise 620ms cubic-bezier(.16,1,.3,1) both}
  .pv-mast>*:nth-child(2){animation-delay:60ms}
  .pv-mast>*:nth-child(3){animation-delay:120ms}
  .pv-mast>*:nth-child(4){animation-delay:180ms}
  @keyframes pv-rise{from{opacity:0;transform:translateY(13px);filter:blur(5px)}
    to{opacity:1;transform:none;filter:none}}
}
@media (prefers-reduced-motion: reduce){
  .pv-thumb,.pv-btn,.pv-line{transition:none}
  .pv-thumb:hover,.pv-btn:hover{transform:none}
}

@media(max-width:620px){
  .pv-showcase{gap:30px}
  .pv-layer{grid-template-columns:34px 1fr;gap:12px;padding:18px 0}
  .pv-enquire{padding:24px 20px}
  .pv-enq-l{width:100%}
  .pv-btn{flex:1 1 auto}
}
"""


def build(html):
    if MARK in html:
        return html
    # replace the two presentation generators
    html = re.sub(r'function reveal\(day,glow,cls,tag\)\{.*?\n\}',
                  lambda m: REVEAL_JS, html, count=1, flags=re.S)
    if "function heroReveal" not in html:      # older one-line form
        html = re.sub(r'function reveal\(day,glow,cls,tag\)\{[^\n]*?\}\s*$',
                      lambda m: REVEAL_JS, html, count=1, flags=re.M)
    i = html.index("function panelHTML(s){")
    j = html.index("var track=document.getElementById('track')", i)
    html = html[:i] + PANEL_JS + "\n" + html[j:]
    # the rail cards
    html = re.sub(r"rail\.innerHTML=SETS\.map\(function\(s,i\)\{.*?\}\)\.join\(''\);",
                  lambda m: RAIL_JS, html, count=1, flags=re.S)
    # styles + the light line
    html = html.replace("</head>", '<style id="%s">%s</style>\n</head>' % (MARK, CSS), 1)
    k = html.rindex("</body>")
    html = html[:k] + '\n<script id="pv-wipe-js">%s</script>\n' % WIPE_JS + html[k:]
    return html
