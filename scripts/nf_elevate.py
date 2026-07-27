# Per-volume elevation layers — crafted against each page's real selectors.
# Every block is presentation-only: typography, depth, states, and one
# authored motion per page. No content or logic is touched.

# Ambient/entrance animations sit behind prefers-reduced-motion:no-preference.
M = "@media (prefers-reduced-motion: no-preference){%s}"

# per-volume accent (each book's own palette) — used for the Catalogue dots
ACCENTS = {
    "":             "#C9A35B",
    "seals":        "#E8C879",
    "portals":      "#7FD9D4",
    "root":         "#D9964A",
    "reaction-map": "#D7DE5A",
    "divide":       "#C29A52",
    "fractal":      "#E5A93C",
    "fracture":     "#C9A35B",
    "sovereign":    "#C85F7E",
    "playground":   "#FFC23D",
    "festival":     "#D8FF3D",
}

# pages that get the brass bookmark-ribbon reading progress
RIBBON = {"", "fracture", "festival", "playground", "reaction-map"}

# scroll-reveal targets per page: [selector, mode]  (mode: rise | pop)
REVEAL = {
    "":           [[".section", "rise"], [".manifesto", "rise"], [".book", "rise"]],
    "fracture":   [[".prose .sub", "rise"]],
    "playground": [[".mission", "pop"], [".worldbar", "pop"]],
}

ELEVATE = {

# ---------------------------------------------------------------- the hub
"": """
.hero h1{letter-spacing:-.022em;text-wrap:balance}
.hero-meta{gap:10px 26px;letter-spacing:.14em}
.book{transition:transform .28s var(--nf-ease),box-shadow .28s var(--nf-ease)}
.book:hover{transform:translateY(-5px);
  box-shadow:0 22px 48px -14px rgba(0,0,0,.65),0 0 0 1px rgba(201,163,91,.28),
  0 0 40px -8px rgba(201,163,91,.22)}
.book img{transition:filter .3s var(--nf-ease)}
.book:hover img{filter:brightness(1.07) saturate(1.04)}
.open{transition:color .18s var(--nf-ease),letter-spacing .18s var(--nf-ease)}
.open:hover{letter-spacing:.03em}
.manifesto{position:relative}
.manifesto::before,.manifesto::after{content:"";position:absolute;left:50%;
  transform:translateX(-50%);width:64px;height:1px;
  background:linear-gradient(90deg,transparent,rgba(201,163,91,.55),transparent)}
.manifesto::before{top:-1px}.manifesto::after{bottom:-1px}
""" + M % """
.hero-emblem{animation:nf-emberglow 7s ease-in-out infinite}
@keyframes nf-emberglow{
  0%,100%{filter:drop-shadow(0 4px 10px rgba(0,0,0,.5)) drop-shadow(0 0 16px rgba(201,163,91,.16))}
  50%{filter:drop-shadow(0 4px 10px rgba(0,0,0,.5)) drop-shadow(0 0 30px rgba(232,200,121,.4))}}
.hero>*{animation:nf-rise-in 640ms cubic-bezier(.16,1,.3,1) both}
.hero>*:nth-child(2){animation-delay:70ms}.hero>*:nth-child(3){animation-delay:140ms}
.hero>*:nth-child(4){animation-delay:210ms}.hero>*:nth-child(5){animation-delay:280ms}
.hero>*:nth-child(n+6){animation-delay:340ms}
@keyframes nf-rise-in{from{opacity:0;transform:translateY(16px);filter:blur(5px)}
  to{opacity:1;transform:none;filter:none}}
""",

# ---------------------------------------------------------------- the root
"root": """
.question{font-size:clamp(26px,5.4vw,38px);letter-spacing:-.02em;text-wrap:balance}
.eyebrow{letter-spacing:.24em}
.opt{transition:transform .16s var(--nf-ease),border-color .16s,color .16s,
  background .16s,box-shadow .16s}
.opt:hover{transform:translateY(-1px);box-shadow:0 6px 18px -8px rgba(217,150,74,.45)}
.opt:active{transform:scale(.985)}
.btn{box-shadow:0 4px 14px -6px rgba(217,150,74,.45)}
.btn:hover{box-shadow:0 12px 28px -8px rgba(217,150,74,.55)}
.insight{border-left-width:1px;padding-left:19px;position:relative}
.insight::before{content:"";position:absolute;left:-3.5px;top:17px;width:6px;height:6px;
  transform:rotate(45deg);background:var(--candle)}
.insight.sage::before{background:var(--sage)}
.insight.violet::before{background:var(--violet)}
.rail-node.lit{box-shadow:0 0 10px rgba(217,150,74,.75),0 0 22px rgba(217,150,74,.3)}
.record-box{box-shadow:inset 0 1px 0 rgba(237,226,204,.06),0 18px 44px -20px rgba(0,0,0,.7)}
textarea,input[type=text]{transition:border-color .18s var(--nf-ease),box-shadow .18s var(--nf-ease)}
""",

# ---------------------------------------------------------------- the press
"seals": """
.hero-stamp{transition:transform .3s var(--nf-ease)}
.hero-stamp:hover{transform:rotate(-2.5deg) scale(1.02)}
.hero-stamp+h1{letter-spacing:-.02em;text-wrap:balance}
.meta{letter-spacing:.16em}
.scrollcue{letter-spacing:.3em;position:relative;padding-bottom:20px}
.scrollcue::after{content:"";position:absolute;left:50%;bottom:0;width:1px;height:15px;
  background:linear-gradient(var(--nf-brass),transparent)}
""" + M % """
.hero-stamp{animation:nf-sealglow 8s ease-in-out infinite}
@keyframes nf-sealglow{
  0%,100%{filter:drop-shadow(0 10px 26px rgba(0,0,0,.55))}
  50%{filter:drop-shadow(0 10px 26px rgba(0,0,0,.55)) drop-shadow(0 0 34px rgba(201,163,91,.34))}}
.scrollcue::after{animation:nf-cue 2.4s ease-in-out infinite}
@keyframes nf-cue{0%,100%{transform:translateY(0);opacity:.9}50%{transform:translateY(5px);opacity:.35}}
""",

# ---------------------------------------------------------------- the portals
"portals": """
.hero-banner{filter:drop-shadow(0 18px 44px rgba(0,0,0,.55))}
h1{letter-spacing:-.015em;text-wrap:balance}
.topbar{backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}
.topbar button,.topbar a{transition:color .18s var(--nf-ease),border-color .18s var(--nf-ease)}
""",

# ---------------------------------------------------------------- the fractal
"fractal": """
.cover-img{box-shadow:0 26px 70px -22px rgba(0,0,0,.75),0 0 0 1px rgba(229,169,60,.16);
  transition:transform .35s var(--nf-ease),box-shadow .35s var(--nf-ease)}
.cover-img:hover{transform:translateY(-4px)}
.cover-title{letter-spacing:-.025em;text-wrap:balance}
.cover-cta{transition:transform .2s var(--nf-ease),box-shadow .2s var(--nf-ease)}
.cover-cta:hover{transform:translateY(-2px);box-shadow:0 12px 30px -10px rgba(229,169,60,.5)}
.pull{position:relative;padding-left:1.5rem}
.pull::before{content:"\\201C";font-family:var(--nf-display);font-size:2.6em;line-height:0;
  position:absolute;left:0;top:.44em;color:var(--accent,#E5A93C);opacity:.65}
""" + M % """
.cover>*{animation:nf-rise-in 680ms cubic-bezier(.16,1,.3,1) both}
.cover>*:nth-child(2){animation-delay:80ms}.cover>*:nth-child(3){animation-delay:160ms}
.cover>*:nth-child(4){animation-delay:240ms}.cover>*:nth-child(n+5){animation-delay:310ms}
@keyframes nf-rise-in{from{opacity:0;transform:translateY(16px);filter:blur(5px)}
  to{opacity:1;transform:none;filter:none}}
""",

# ---------------------------------------------------------------- all fracture
"fracture": """
.cover-frac{letter-spacing:-.01em}
.cover-cta{border:1px solid rgba(201,163,91,.45);padding:.85em 1.5em;
  transition:background .22s var(--nf-ease),transform .22s var(--nf-ease),
  box-shadow .22s var(--nf-ease)}
.cover-cta:hover{background:rgba(201,163,91,.12);transform:translateY(-2px);
  box-shadow:0 10px 26px -12px rgba(201,163,91,.5)}
.prose .sub{display:flex;align-items:center;gap:14px}
.prose .sub::after{content:"";flex:1;height:1px;
  background:linear-gradient(90deg,rgba(201,163,91,.4),transparent)}
""" + M % """
.cover-text>*{animation:nf-rise-in 680ms cubic-bezier(.16,1,.3,1) both}
.cover-text>*:nth-child(2){animation-delay:80ms}.cover-text>*:nth-child(3){animation-delay:160ms}
.cover-text>*:nth-child(4){animation-delay:240ms}.cover-text>*:nth-child(5){animation-delay:300ms}
.cover-text>*:nth-child(n+6){animation-delay:360ms}
@keyframes nf-rise-in{from{opacity:0;transform:translateY(16px);filter:blur(5px)}
  to{opacity:1;transform:none;filter:none}}
""",

# ---------------------------------------------------------------- sovereign
"sovereign": """
.cover-cta{transition:transform .2s var(--nf-ease),box-shadow .2s var(--nf-ease)}
.cover-cta:hover{transform:translateY(-2px);box-shadow:0 12px 30px -10px rgba(207,154,62,.5)}
.ch-title{letter-spacing:-.018em;text-wrap:balance;position:relative;padding-bottom:.55em}
.ch-title::after{content:"";position:absolute;left:0;bottom:0;width:44px;height:1px;
  background:linear-gradient(90deg,#CF9A3E,transparent)}
.resume{backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
""",

# ---------------------------------------------------------------- the divide
"divide": """
.wt-title{letter-spacing:-.02em;text-wrap:balance}
.entry-title{letter-spacing:-.02em;text-wrap:balance}
.sec-t{text-wrap:balance}
.wt-btn{transition:transform .2s var(--nf-ease),box-shadow .2s var(--nf-ease)}
.wt-btn:hover{transform:translateY(-2px);box-shadow:0 14px 34px -12px rgba(194,154,82,.55)}
.wt-mark{filter:drop-shadow(0 0 22px rgba(194,154,82,.32))}
""",

# ---------------------------------------------------------------- playground
"playground": """
.cover-title{text-wrap:balance}
.mission{transition:transform .22s cubic-bezier(.34,1.56,.64,1),box-shadow .22s}
.mission:hover{transform:translateY(-4px) rotate(-.4deg);
  box-shadow:8px 10px 0 -2px rgba(34,26,74,.16)}
.cover-cta{transition:transform .18s cubic-bezier(.34,1.56,.64,1)}
.cover-cta:hover{transform:scale(1.05) rotate(-1deg)}
.cover-cta:active{transform:scale(.97)}
""",

# ---------------------------------------------------------------- festie codex
"festival": """
.cover-title{text-wrap:balance}
.cover-cta{transition:transform .16s var(--nf-ease),box-shadow .16s var(--nf-ease)}
.cover-cta:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 #000}
.cover-cta:active{transform:translate(0,0);box-shadow:2px 2px 0 #000}
.chip{transition:transform .15s var(--nf-ease)}
.chip:hover{transform:translateX(3px)}
""",

# ---------------------------------------------------------------- reaction map
"reaction-map": """
.hero h1{letter-spacing:-.02em;text-wrap:balance}
.tab{transition:color .16s var(--nf-ease),border-color .16s,background .16s}
.card{box-shadow:0 14px 36px -20px rgba(0,0,0,.6)}
""",
}
