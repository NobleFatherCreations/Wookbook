#!/usr/bin/env python3
"""Playground Protectors — effects, atmosphere, and the grown-up fog.

Three things this adds:

1. THE FOG. The book is written for two readers at once, and the grown-up
   passages talk *about* children rather than to them. Those are now sealed
   behind drifting fog: a child scrolling past sees weather and keeps going,
   and cannot read the text even by squinting, because while the fog is up the
   content is `inert` and hidden from assistive tech too. A grown-up taps once
   and it clears — remembered for the rest of the visit.

2. THINGS THAT POP. Power-ups burst, panels land like comic frames, speech
   bubbles spring, moves slide in, mission titles arrive a letter at a time,
   and lighting a mission bulb throws real confetti.

3. WEATHER PER WORLD. Each of the four worlds carries its own drifting
   atmosphere so the book changes climate as a reader moves through it.

Not one word of the story is altered.
"""
import re

MARK = "pp-fx"

# grown-up passages that get sealed behind weather
FOG_TARGETS = [
    ('<div class="note-card grown">', 'note-card grown'),
]

CSS = r"""
/* ================== PLAYGROUND PROTECTORS — effects ================== */
:root{--pp-ease:cubic-bezier(.34,1.32,.5,1);--pp-out:cubic-bezier(.4,0,.9,.5)}

/* ---------- THE FOG over grown-up passages ---------- */
/* while fogged the block also collapses, so a child scrolls past in one flick
   and the tap target is always on screen rather than lost down a long column */
.pp-fogwrap{position:relative;border-radius:20px;overflow:hidden;isolation:isolate;
  max-height:280px;transition:max-height .6s var(--pp-out)}
.pp-fogwrap.pp-clear{overflow:visible;max-height:none}
.pp-fogwrap>.pp-fogged{transition:filter .55s var(--pp-out),opacity .55s var(--pp-out)}
.pp-fogwrap:not(.pp-clear)>.pp-fogged{filter:blur(11px) saturate(.55) brightness(1.08);
  opacity:.5;pointer-events:none;user-select:none}
.pp-fog{position:absolute;inset:0;z-index:3;display:grid;place-items:center;
  padding:18px;text-align:center;cursor:pointer;border:0;width:100%;
  font-family:inherit;border-radius:20px;
  background:
    radial-gradient(60% 46% at 22% 34%,rgba(255,255,255,.96),transparent 70%),
    radial-gradient(52% 42% at 74% 60%,rgba(255,255,255,.94),transparent 72%),
    radial-gradient(46% 40% at 50% 88%,rgba(255,255,255,.9),transparent 74%),
    linear-gradient(180deg,rgba(233,240,252,.92),rgba(214,228,248,.94));
  transition:opacity .5s var(--pp-out),transform .5s var(--pp-out)}
.pp-fogwrap.pp-clear .pp-fog{opacity:0;transform:scale(1.04);pointer-events:none}
.pp-fog-chip{display:inline-flex;align-items:center;gap:.5rem;
  background:#fff;border:4px solid var(--ink);border-radius:999px;
  padding:.7rem 1.15rem;box-shadow:0 5px 0 rgba(0,0,0,.16);
  font-family:var(--disp,inherit);font-weight:800;font-size:.95rem;color:var(--ink);
  transition:transform .22s var(--pp-ease),box-shadow .22s var(--pp-ease)}
.pp-fog:hover .pp-fog-chip{transform:translateY(-3px);box-shadow:0 8px 0 rgba(0,0,0,.18)}
.pp-fog:active .pp-fog-chip{transform:translateY(1px);box-shadow:0 3px 0 rgba(0,0,0,.18)}
.pp-fog:focus-visible{outline:4px solid var(--grape,#6A4BE0);outline-offset:3px}
.pp-fog-sub{display:block;margin-top:.55rem;font-family:var(--disp,inherit);
  font-weight:700;font-size:.72rem;letter-spacing:.06em;color:#5C6B87;
  text-transform:uppercase}
@media (prefers-reduced-motion: no-preference){
  .pp-fog{background-size:190% 190%,170% 170%,200% 200%,100% 100%;
    animation:pp-drift 22s ease-in-out infinite}
  @keyframes pp-drift{
    0%,100%{background-position:12% 30%,78% 62%,48% 88%,0 0}
    50%{background-position:34% 44%,58% 40%,60% 74%,0 0}}
}

/* ---------- POWER-UPS burst ---------- */
.powerup{position:relative;overflow:visible}
@media (prefers-reduced-motion: no-preference){
  .pp-in .pu-burst{animation:pp-burst .62s var(--pp-ease) both}
  @keyframes pp-burst{
    0%{transform:scale(.4) rotate(-9deg);opacity:0}
    60%{transform:scale(1.12) rotate(2deg);opacity:1}
    100%{transform:scale(1) rotate(0);opacity:1}}
  .pp-in .pu-name{animation:pp-pop .5s var(--pp-ease) .12s both}
  @keyframes pp-pop{from{transform:translateY(9px) scale(.94);opacity:0}
    to{transform:none;opacity:1}}
  /* rays fire out of the burst once */
  .pu-burst::after{content:"";position:absolute;left:50%;top:50%;width:150px;height:150px;
    margin:-75px 0 0 -75px;pointer-events:none;border-radius:50%;opacity:0;
    background:conic-gradient(from 0deg,
      rgba(255,194,61,.55) 0 6deg,transparent 6deg 30deg,
      rgba(255,194,61,.55) 30deg 36deg,transparent 36deg 60deg,
      rgba(255,194,61,.55) 60deg 66deg,transparent 66deg 90deg,
      rgba(255,194,61,.55) 90deg 96deg,transparent 96deg 120deg,
      rgba(255,194,61,.55) 120deg 126deg,transparent 126deg 150deg,
      rgba(255,194,61,.55) 150deg 156deg,transparent 156deg 180deg,
      rgba(255,194,61,.55) 180deg 186deg,transparent 186deg 210deg,
      rgba(255,194,61,.55) 210deg 216deg,transparent 216deg 240deg,
      rgba(255,194,61,.55) 240deg 246deg,transparent 246deg 270deg,
      rgba(255,194,61,.55) 270deg 276deg,transparent 276deg 300deg,
      rgba(255,194,61,.55) 300deg 306deg,transparent 306deg 330deg,
      rgba(255,194,61,.55) 330deg 336deg,transparent 336deg)}
  .pp-in .pu-burst::after{animation:pp-rays .8s ease-out both}
  @keyframes pp-rays{0%{opacity:.9;transform:scale(.2) rotate(0)}
    100%{opacity:0;transform:scale(1.5) rotate(38deg)}}
}

/* ---------- PANELS land like comic frames ---------- */
@media (prefers-reduced-motion: no-preference){
  .pp-anim{opacity:0;transform:translateY(22px) scale(.985);
    transition:opacity .5s var(--pp-ease),transform .5s var(--pp-ease);
    transition-delay:var(--pp-d,0ms)}
  .pp-anim.pp-in{opacity:1;transform:none}
}

/* ---------- SPEECH BUBBLES spring ---------- */
@media (prefers-reduced-motion: no-preference){
  .pp-in.saybubble,.pp-in .saybubble{animation:pp-bubble .5s var(--pp-ease) both}
  @keyframes pp-bubble{0%{transform:scale(.82) translateY(8px);opacity:0}
    100%{transform:none;opacity:1}}
}

/* ---------- MOVES slide in ---------- */
@media (prefers-reduced-motion: no-preference){
  .pp-in .move{animation:pp-slide .46s var(--pp-ease) both}
  .pp-in .move:nth-child(2){animation-delay:70ms}
  .pp-in .move:nth-child(3){animation-delay:140ms}
  .pp-in .move:nth-child(n+4){animation-delay:200ms}
  @keyframes pp-slide{from{transform:translateX(-16px);opacity:0}to{transform:none;opacity:1}}
}

/* ---------- MISSION TITLES arrive a letter at a time ---------- */
.pp-ch{display:inline-block;white-space:pre}
@media (prefers-reduced-motion: no-preference){
  .pp-title .pp-ch{opacity:0;transform:translateY(.36em) rotate(-7deg);
    animation:pp-letter .46s var(--pp-ease) both;
    animation-delay:calc(var(--i)*22ms)}
  @keyframes pp-letter{to{opacity:1;transform:none}}
}

/* ---------- WEATHER PER WORLD ---------- */
.pp-weather{position:absolute;inset:0;pointer-events:none;z-index:0;overflow:hidden;
  border-radius:inherit}
.pp-weather span{position:absolute;display:block;border-radius:50%;opacity:.5;
  max-width:55vw;max-height:55vw}
#world1,#world2,#world3,#world4{position:relative;isolation:isolate;overflow-x:clip}
#world1>*,#world2>*,#world3>*,#world4>*{position:relative;z-index:1}
#world1 .pp-weather span{background:radial-gradient(circle,rgba(34,197,140,.5),transparent 70%)}
#world2 .pp-weather span{background:radial-gradient(circle,rgba(255,159,64,.45),transparent 70%)}
#world3 .pp-weather span{background:radial-gradient(circle,rgba(30,155,230,.45),transparent 70%)}
#world4 .pp-weather span{background:radial-gradient(circle,rgba(106,75,224,.42),transparent 70%)}
@media (prefers-reduced-motion: no-preference){
  .pp-weather span{animation:pp-float var(--t,26s) ease-in-out infinite;
    animation-delay:var(--dl,0s)}
  @keyframes pp-float{
    0%,100%{transform:translate3d(0,0,0) scale(1)}
    50%{transform:translate3d(var(--dx,18px),var(--dy,-26px),0) scale(1.14)}}
}

/* ---------- MAP CHIPS are springy ---------- */
.mchip{transition:transform .2s var(--pp-ease),box-shadow .2s var(--pp-ease)}
.mchip:hover{transform:translateY(-3px) rotate(-1deg)}
.mchip:active{transform:translateY(1px) scale(.97)}

/* ---------- CONFETTI when a mission lights up ---------- */
.pp-confetti{position:fixed;inset:0;pointer-events:none;z-index:9930;overflow:hidden}
.pp-confetti i{position:absolute;width:9px;height:14px;border-radius:2px;
  will-change:transform,opacity}
@media (prefers-reduced-motion: no-preference){
  .pp-confetti i{animation:pp-fall var(--t,1500ms) cubic-bezier(.2,.6,.4,1) forwards}
  @keyframes pp-fall{
    0%{transform:translate3d(0,0,0) rotate(0);opacity:1}
    100%{transform:translate3d(var(--dx,0px),var(--dy,320px),0) rotate(var(--rot,540deg));opacity:0}}
}

/* ---------- BULBS glow when lit ---------- */
.bulb{transition:transform .3s var(--pp-ease),filter .3s var(--pp-ease)}
.bulb.lit,.bulb.on{filter:drop-shadow(0 0 10px rgba(255,194,61,.85))}
@media (prefers-reduced-motion: no-preference){
  .pp-justlit{animation:pp-lit .6s var(--pp-ease) both}
  @keyframes pp-lit{0%{transform:scale(1)}45%{transform:scale(1.42) rotate(9deg)}
    100%{transform:scale(1)}}
}

@media (prefers-reduced-motion: reduce){
  .pp-anim{opacity:1;transform:none}
  .pp-weather{display:none}
  .pp-confetti{display:none}
}
"""

JS = r"""
(function(){
  var reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- THE FOG ---------- */
  document.querySelectorAll('[data-pp-fog]').forEach(function(el,idx){
    var wrap=document.createElement('div');
    wrap.className='pp-fogwrap';
    el.parentNode.insertBefore(wrap,el);
    wrap.appendChild(el);
    el.classList.add('pp-fogged');

    var btn=document.createElement('button');
    btn.type='button';btn.className='pp-fog';
    btn.innerHTML='<span><span class="pp-fog-chip">\u{1F32B}️ This part is for grown-ups</span>'
      +'<span class="pp-fog-sub">Tap to clear the fog · kids can skip right past</span></span>';
    wrap.appendChild(btn);

    var key='ppFog'+idx;
    function clear(){
      wrap.classList.add('pp-clear');
      el.removeAttribute('inert');el.removeAttribute('aria-hidden');
      try{sessionStorage.setItem(key,'1')}catch(_){}
      setTimeout(function(){if(btn.parentNode)btn.remove()},600);
    }
    var already=false;try{already=sessionStorage.getItem(key)==='1'}catch(_){}
    if(already){clear();}
    else{
      // while the fog is up a child cannot reach the words, by eye or by reader
      el.setAttribute('inert','');el.setAttribute('aria-hidden','true');
      btn.addEventListener('click',clear);
    }
  });

  /* ---------- things that pop as they arrive ---------- */
  if(!reduced&&'IntersectionObserver' in window){
    var sel='.panel,.powerup,.saybubble,.moves,.pucard,.lt-body,.lv-body,.note-card,.plate';
    var els=[].slice.call(document.querySelectorAll(sel)).filter(function(e){
      return !e.closest('.pp-fogwrap')&&!e.closest('#nf-chrome');
    });
    els.forEach(function(e,i){
      e.classList.add('pp-anim');
    });
    var seen=0;
    var io=new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if(!en.isIntersecting)return;
        var e=en.target;
        e.style.setProperty('--pp-d',(Math.min(seen++%3,2)*80)+'ms');
        e.classList.add('pp-in');
        io.unobserve(e);
      });
    },{rootMargin:'0px 0px -7% 0px',threshold:.06});
    els.forEach(function(e){
      if(e.getBoundingClientRect().top<innerHeight*.92){e.classList.add('pp-in');}
      else io.observe(e);
    });
    // safety sweep: nothing may stay invisible once scrolled past
    var tick=false;
    addEventListener('scroll',function(){
      if(tick)return;tick=true;
      requestAnimationFrame(function(){
        els.forEach(function(e){
          if(!e.classList.contains('pp-in')&&
             e.getBoundingClientRect().top<innerHeight*.96)e.classList.add('pp-in');
        });
        tick=false;
      });
    },{passive:true});
  }

  /* ---------- mission titles, a letter at a time ---------- */
  if(!reduced){
    document.querySelectorAll('.ch-h,.mission-h,h2.plate-h,.lv-head h2').forEach(function(h){
      if(h.dataset.ppSplit||h.querySelector('img,svg'))return;
      var txt=h.textContent;
      if(txt.length>44)return;
      var frag=document.createDocumentFragment(),i=0;
      txt.split('').forEach(function(c){
        var s=document.createElement('span');
        s.className='pp-ch';s.textContent=c;s.style.setProperty('--i',i++);
        frag.appendChild(s);
      });
      h.textContent='';h.appendChild(frag);
      h.classList.add('pp-title');h.dataset.ppSplit='1';h.setAttribute('aria-label',txt);
    });
  }

  /* ---------- weather in each world ---------- */
  if(!reduced){
    ['world1','world2','world3','world4'].forEach(function(id){
      var w=document.getElementById(id);if(!w)return;
      var lay=document.createElement('div');
      lay.className='pp-weather';lay.setAttribute('aria-hidden','true');
      for(var i=0;i<7;i++){
        var s=document.createElement('span');
        var size=90+Math.random()*190;
        s.style.width=s.style.height=size+'px';
        s.style.left=(6+Math.random()*74)+'%';
        s.style.top=(Math.random()*100)+'%';
        s.style.setProperty('--t',(20+Math.random()*20)+'s');
        s.style.setProperty('--dl',(-Math.random()*20)+'s');
        s.style.setProperty('--dx',((Math.random()-.5)*70).toFixed(0)+'px');
        s.style.setProperty('--dy',((Math.random()-.5)*80).toFixed(0)+'px');
        lay.appendChild(s);
      }
      w.insertBefore(lay,w.firstChild);
    });
  }

  /* ---------- confetti when a mission bulb lights ---------- */
  if(!reduced){
    var COLORS=['#FFC23D','#22C58C','#FF6B6B','#6A4BE0','#1E9BE6','#FF9F40'];
    function burst(x,y){
      var box=document.createElement('div');
      box.className='pp-confetti';box.setAttribute('aria-hidden','true');
      for(var i=0;i<26;i++){
        var p=document.createElement('i');
        p.style.left=x+'px';p.style.top=y+'px';
        p.style.background=COLORS[i%COLORS.length];
        p.style.setProperty('--dx',((Math.random()-.5)*300).toFixed(0)+'px');
        p.style.setProperty('--dy',(120+Math.random()*260).toFixed(0)+'px');
        p.style.setProperty('--rot',((Math.random()-.5)*900).toFixed(0)+'deg');
        p.style.setProperty('--t',(1100+Math.random()*900).toFixed(0)+'ms');
        box.appendChild(p);
      }
      document.body.appendChild(box);
      setTimeout(function(){box.remove()},2200);
    }
    // watch the book's own bulbs; when one becomes lit, celebrate it
    var bulbs=[].slice.call(document.querySelectorAll('.bulb'));
    if(bulbs.length&&window.MutationObserver){
      var mo=new MutationObserver(function(muts){
        muts.forEach(function(m){
          var b=m.target;
          if(!b.classList||!(b.classList.contains('lit')||b.classList.contains('on')))return;
          if(b.dataset.ppCelebrated)return;
          b.dataset.ppCelebrated='1';
          b.classList.add('pp-justlit');
          var r=b.getBoundingClientRect();
          if(r.width)burst(r.left+r.width/2,r.top+r.height/2);
          setTimeout(function(){b.classList.remove('pp-justlit')},700);
        });
      });
      bulbs.forEach(function(b){
        if(b.classList.contains('lit')||b.classList.contains('on'))b.dataset.ppCelebrated='1';
        mo.observe(b,{attributes:true,attributeFilter:['class']});
      });
    }
  }
})();
"""


def build(html):
    if MARK in html:
        return html
    # seal the grown-up passages behind weather
    for needle, _ in FOG_TARGETS:
        html = html.replace(needle, needle[:-1] + ' data-pp-fog>', 1)
    # the standalone grown-up tip section
    html = re.sub(r'(<section class="[^"]*"\s+id="parents-tip")',
                  r'\1 data-pp-fog', html, count=1)
    html = html.replace("</head>", '<style id="%s">%s</style>\n</head>' % (MARK, CSS), 1)
    i = html.rindex("</body>")
    return html[:i] + '\n<script id="pp-fx-js">%s</script>\n' % JS + html[i:]
