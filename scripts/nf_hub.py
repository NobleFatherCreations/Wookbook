#!/usr/bin/env python3
"""The Study — compositional rebuild of the Catalogue hub.

This is not a stylesheet on top of the old page. It re-emits the hub's
presentation DOM around one spatial idea: a candlelit study you descend
through, where every volume is a physical book standing on a shelf.

Content is carried over verbatim — titles, hooks, descriptions, tags,
links, cover art. Only the composition changes.

Run from rebuild.py; idempotent via the st-study marker.
"""
import re

MARK = "st-study"


# --------------------------------------------------------------- extraction
def grab(article):
    """Pull the content of one .book/.craft article into a dict."""
    d = {}
    g = re.search(r'style="--glow:([^"]*)"', article)
    d["glow"] = g.group(1).strip().rstrip(";") if g else "#C9A35B"
    c = re.search(r'<span class="code">(.*?)</span>', article, re.S)
    d["code"] = c.group(1).strip() if c else ""
    im = re.search(r'<img\s[^>]*>', article)
    d["img"] = im.group(0) if im else ""
    sv = re.search(r'<svg\b.*?</svg>', article, re.S)
    d["svg"] = sv.group(0) if sv else ""
    h3 = re.search(r'<h3>(.*?)</h3>', article, re.S)
    title = h3.group(1) if h3 else ""
    sub = re.search(r'<span class="sub">(.*?)</span>', title, re.S)
    d["sub"] = sub.group(1).strip() if sub else ""
    d["title"] = re.sub(r'<span class="sub">.*?</span>', "", title, flags=re.S).strip()
    hk = re.search(r'<p class="hook">(.*?)</p>', article, re.S)
    d["hook"] = hk.group(1).strip() if hk else ""
    ds = re.search(r'<p class="desc">(.*?)</p>', article, re.S)
    d["desc"] = ds.group(1).strip() if ds else ""
    d["tags"] = re.findall(r'<span class="tag">(.*?)</span>', article, re.S)
    op = re.search(r'<a class="open"([^>]*)>(.*?)</a>', article, re.S)
    d["open_attrs"] = op.group(1).strip() if op else ""
    d["open_text"] = re.sub(r'<span class="arr">.*?</span>', "", op.group(2), flags=re.S).strip() if op else ""
    st = re.search(r'<a class="stretch"([^>]*)></a>', article, re.S)
    d["stretch"] = st.group(1).strip() if st else ""
    d["closer"] = "book closer" in article[:60]
    return d


# ------------------------------------------------------------------ re-emit
def volume(d, i):
    """One standing volume: physical book on a shelf + catalogue entry."""
    # the numeral is the real catalogue number carried in the code
    cn = re.search(r'(\d{2,})', d["code"])
    n = cn.group(1) if cn else ""
    tags = "".join('<li>%s</li>' % t for t in d["tags"])
    face = d["img"] or d["svg"]
    kind = "st-vol st-closer" if d["closer"] else "st-vol"
    # closer has no cover photo — it gets the emblem plate instead
    book = (
        '<div class="st-book">'
        '<div class="st-book-face">%s</div>'
        '<span class="st-book-spine" aria-hidden="true"></span>'
        '<span class="st-book-edge" aria-hidden="true"></span>'
        '<span class="st-book-gloss" aria-hidden="true"></span>'
        '</div>' % face)
    return (
        '<article class="%s reveal" style="--glow:%s">'
        '<div class="st-vol-plate">%s'
        '<span class="st-shelf" aria-hidden="true"></span>'
        '<span class="st-pool" aria-hidden="true"></span>'
        '</div>'
        '<div class="st-vol-entry">'
        '<div class="st-vol-rule">%s'
        '<span class="st-vol-code">%s</span></div>'
        '<h3 class="st-vol-title">%s</h3>'
        '%s'
        '<p class="st-vol-hook">%s</p>'
        '<p class="st-vol-desc">%s</p>'
        '<ul class="st-vol-tags">%s</ul>'
        '<a class="st-vol-open"%s>%s<span class="st-arr" aria-hidden="true">&#8594;</span></a>'
        '</div>'
        '<a class="stretch"%s></a>'
        '</article>' % (
            kind, d["glow"], book,
            ('<span class="st-vol-n">%s</span>' % n) if n else "",
            d["code"], d["title"],
            ('<p class="st-vol-sub">%s</p>' % d["sub"]) if d["sub"] else "",
            d["hook"], d["desc"], tags, d["open_attrs"], d["open_text"], d["stretch"]))


def rebuild_articles(html, cls, start):
    """Replace every <article class="cls ..."> block with a standing volume."""
    pat = re.compile(r'<article class="%s[^"]*"[^>]*>.*?</article>' % cls, re.S)
    idx = [start]

    def rep(m):
        d = grab(m.group(0))
        out = volume(d, idx[0])
        idx[0] += 1
        return out

    return pat.sub(rep, html), idx[0]


# ------------------------------------------------------------------- hero
HERO = '''<section class="st-hero">
  <div class="st-hero-room" aria-hidden="true">
    __PLATE__
    <span class="st-hero-glow"></span>
    <span class="st-hero-beam"></span>
    <span class="st-hero-motes"></span>
    <span class="st-hero-vignette"></span>
  </div>
  <div class="st-hero-inner">
    <div class="st-hero-seal" aria-hidden="true"><span class="st-hero-emblem"></span></div>
    <p class="st-hero-eyebrow">Noble Father Creations</p>
    <h1 class="st-hero-title"><span class="st-l1">The collected</span><span class="st-l2">works.</span></h1>
    <p class="st-hero-thesis">Field guides that reveal the pattern hiding inside everyday systems &mdash; and hand-made objects that hide a living core under wax and resin.</p>
    <p class="st-hero-mantra"><em>Worn in the light. Alive in the dark.</em></p>
    <ul class="st-colophon">
      <li><b>2</b><span>living tools</span></li>
      <li><b>6</b><span>interactive books</span></li>
      <li><b>2</b><span>NFC craft lines</span></li>
      <li><b>Free</b><span>to read</span></li>
    </ul>
    <a class="st-enter" href="#manifesto"><span>Enter the study</span>
      <span class="st-enter-line" aria-hidden="true"></span></a>
  </div>
</section>'''


def rebuild_hero(html):
    """Replace the centered text hero with the room — and absorb the brand
    banner (479px of dead darkness above the fold) into it as the backdrop."""
    plate = ""
    bm = re.search(r'<div class="brand-banner">\s*(<img\s[^>]*>)\s*</div>', html, re.S)
    if bm:
        img = re.sub(r'\sclass="[^"]*"', "", bm.group(1))
        img = img.replace("<img", '<img class="st-hero-plate" alt=""', 1)
        plate = img
        html = html.replace(bm.group(0), "", 1)
    hero = HERO.replace("__PLATE__", plate)
    pat = re.compile(r'<section class="hero">.*?</section>', re.S)
    return pat.sub(lambda m: hero, html, count=1)


# ---------------------------------------------------------- chapter openings
def rebuild_sec_heads(html):
    """№ numeral pulled into the margin, brass rule, editorial title."""
    pat = re.compile(
        r'<div class="sec-head reveal">\s*<div class="t">'
        r'<span class="eyebrow">(.*?)</span><h2>(.*?)</h2></div>'
        r'\s*(?:<p class="note">(.*?)</p>)?\s*</div>', re.S)

    def rep(m):
        eyebrow, title, note = m.group(1), m.group(2), (m.group(3) or "")
        num = re.match(r'\s*№\s*(\S+)', eyebrow)
        numeral = num.group(1) if num else ""
        name = re.sub(r'^\s*№\s*\S+\s*&mdash;\s*|^\s*№\s*\S+\s*—\s*', "", eyebrow).strip()
        return (
            '<div class="st-chapter reveal">'
            '<span class="st-chapter-num" aria-hidden="true">%s</span>'
            '<div class="st-chapter-body">'
            '<p class="st-chapter-name">%s</p>'
            '<h2 class="st-chapter-title">%s</h2>'
            '<span class="st-chapter-rule" aria-hidden="true"></span>'
            '%s</div></div>' % (
                numeral, name, title,
                ('<p class="st-chapter-note">%s</p>' % note) if note else ""))

    return pat.sub(rep, html)


def rebuild_kickers(html):
    """The Music / Maker / Support carry their kicker inline instead of in a
    sec-head. Bring them into the same chapter typography without disturbing
    their own layouts. Also corrects a duplicated catalogue numeral: Music and
    Support were both № 03."""
    html = html.replace('<span class="eyebrow">№ 03 — Support</span>',
                        '<span class="eyebrow">№ 04 — Support</span>', 1)

    def rep(m):
        raw = m.group(1).strip()
        num = re.match(r'№\s*(\S+)\s*(?:—|&mdash;)\s*(.+)', raw)
        if num:
            return ('<p class="st-kicker"><span class="st-kicker-n">%s</span>%s</p>'
                    % (num.group(1), num.group(2).strip()))
        return '<p class="st-kicker">%s</p>' % raw

    return re.sub(r'<span class="eyebrow">([^<]*)</span>', rep, html)


# --------------------------------------------------------------------- CSS
CSS = r"""
/* ================= THE STUDY — hub composition ================= */
.st-hero,.st-vol,.st-chapter{--st-ease:cubic-bezier(.2,.7,.2,1)}

/* ---- the room ---- */
.st-hero{position:relative;min-height:100svh;display:flex;align-items:center;
  justify-content:center;overflow:hidden;padding:96px 22px 72px;isolation:isolate}
.st-hero-room{position:absolute;inset:0;z-index:0;pointer-events:none}
/* the brand banner, lifted out of the flow and hung as the room's back wall:
   natural aspect so its key art is never blown up, masked into the dark */
.st-hero-plate{position:absolute;top:0;left:0;width:100%;height:auto;
  opacity:.3;
  -webkit-mask-image:linear-gradient(180deg,#000 0%,rgba(0,0,0,.58) 48%,transparent 90%);
  mask-image:linear-gradient(180deg,#000 0%,rgba(0,0,0,.58) 48%,transparent 90%);
  transform:translate3d(0,calc(var(--st-scroll,0)*-46px),0)}
.st-hero-glow{position:absolute;top:-18%;right:-6%;width:min(90vw,860px);aspect-ratio:1;
  border-radius:50%;
  background:radial-gradient(circle,rgba(232,200,121,.20),rgba(201,163,91,.09) 42%,transparent 68%);
  filter:blur(14px);
  transform:translate3d(0,calc(var(--st-scroll,0)*-90px),0)}
.st-hero-beam{position:absolute;top:-30%;right:4%;width:min(72vw,560px);height:150%;
  background:linear-gradient(198deg,rgba(232,200,121,.11),rgba(232,200,121,.03) 38%,transparent 66%);
  filter:blur(26px);transform:rotate(9deg) translate3d(0,calc(var(--st-scroll,0)*-52px),0)}
.st-hero-motes{position:absolute;inset:0;opacity:.5;
  background-image:
    radial-gradient(1.4px 1.4px at 18% 32%,rgba(240,220,174,.55),transparent),
    radial-gradient(1.2px 1.2px at 74% 22%,rgba(240,220,174,.4),transparent),
    radial-gradient(1.6px 1.6px at 42% 68%,rgba(240,220,174,.35),transparent),
    radial-gradient(1.1px 1.1px at 86% 60%,rgba(240,220,174,.45),transparent),
    radial-gradient(1.3px 1.3px at 28% 84%,rgba(240,220,174,.3),transparent),
    radial-gradient(1px 1px at 62% 46%,rgba(240,220,174,.4),transparent);
  transform:translate3d(0,calc(var(--st-scroll,0)*-140px),0)}
.st-hero-vignette{position:absolute;inset:0;
  background:
    radial-gradient(78% 54% at 50% 52%,rgba(10,7,13,.72),rgba(10,7,13,.34) 62%,transparent 82%),
    radial-gradient(130% 92% at 50% 34%,transparent 30%,rgba(10,7,13,.55) 74%,rgba(10,7,13,.88) 100%)}

.st-hero-inner{position:relative;z-index:1;max-width:760px;text-align:center;
  transform:translate3d(0,calc(var(--st-scroll,0)*44px),0);
  opacity:calc(1 - var(--st-scroll,0)*.85)}

/* the seal struck at the head of the page */
.st-hero-seal{width:96px;height:96px;margin:0 auto 30px;border-radius:50%;
  display:grid;place-items:center;position:relative;
  background:radial-gradient(circle at 34% 28%,#241B2E,#15101C 68%,#0E0A14);
  box-shadow:inset 0 1px 0 rgba(240,220,174,.18),inset 0 -6px 14px rgba(0,0,0,.6),
    0 0 0 1px rgba(201,163,91,.34),0 18px 44px -18px rgba(0,0,0,.9)}
.st-hero-seal::after{content:"";position:absolute;inset:9px;border-radius:50%;
  border:1px dashed rgba(201,163,91,.3)}
.st-hero-emblem{width:52px;height:52px;background-image:var(--brand-logo);
  background-size:contain;background-repeat:no-repeat;background-position:center;
  filter:drop-shadow(0 3px 8px rgba(0,0,0,.7))}

.st-hero-eyebrow{font-family:var(--nf-mono,"Space Mono",monospace);font-size:10.5px;
  letter-spacing:.34em;text-transform:uppercase;color:var(--nf-brass,#C9A35B);margin:0 0 18px}
.st-hero-title{font-family:var(--nf-display,"Fraunces",Georgia,serif);font-weight:500;
  line-height:.94;letter-spacing:-.035em;margin:0;display:flex;flex-direction:column;
  align-items:center;gap:.02em}
.st-l1{font-size:clamp(2.9rem,10.5vw,6rem);color:#ECE4D6}
.st-l2{font-size:clamp(3.4rem,13vw,7.4rem);font-style:italic;font-weight:600;
  background:linear-gradient(174deg,#F4E2B4,#C9A35B 44%,#8E6B2F 78%,#E8C879);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 2px 10px rgba(201,163,91,.24))}
.st-hero-thesis{margin:30px auto 0;max-width:44ch;font-size:clamp(15px,1.6vw,17.5px);
  line-height:1.68;color:#BCB1A0}
.st-hero-mantra{margin:14px auto 0;font-family:var(--nf-display,"Fraunces",Georgia,serif);
  font-size:clamp(15.5px,1.7vw,18px);color:#ECE4D6;letter-spacing:.005em}

/* colophon rule — facts set like a specimen sheet */
.st-colophon{list-style:none;margin:38px auto 0;padding:16px 0 0;max-width:600px;
  display:grid;grid-template-columns:repeat(4,1fr);gap:8px;
  border-top:1px solid rgba(201,163,91,.26)}
.st-colophon li{display:flex;flex-direction:column;gap:5px;align-items:center;
  position:relative;padding:0 6px}
.st-colophon li+li::before{content:"";position:absolute;left:0;top:5%;height:74%;
  width:1px;background:linear-gradient(180deg,transparent,rgba(201,163,91,.28),transparent)}
.st-colophon b{font-family:var(--nf-display,"Fraunces",Georgia,serif);font-weight:500;
  font-size:clamp(19px,2.6vw,26px);color:#E8C879;letter-spacing:-.02em;line-height:1}
.st-colophon span{font-family:var(--nf-mono,"Space Mono",monospace);font-size:9.5px;
  letter-spacing:.16em;text-transform:uppercase;color:#8A8071;line-height:1.35;text-align:center}

.st-enter{display:inline-flex;flex-direction:column;align-items:center;gap:12px;
  margin-top:44px;text-decoration:none;
  font-family:var(--nf-mono,"Space Mono",monospace);font-size:10.5px;letter-spacing:.3em;
  text-transform:uppercase;color:#8A8071;transition:color .22s var(--st-ease)}
.st-enter:hover{color:#E8C879}
.st-enter-line{width:1px;height:38px;
  background:linear-gradient(180deg,rgba(201,163,91,.75),transparent)}

/* ---- chapter openings ---- */
.st-chapter{display:grid;grid-template-columns:auto 1fr;gap:clamp(16px,3vw,34px);
  align-items:start;margin-bottom:clamp(38px,6vw,66px)}
.st-chapter-num{font-family:var(--nf-display,"Fraunces",Georgia,serif);font-weight:500;
  font-size:clamp(2.4rem,7vw,4.6rem);line-height:.8;letter-spacing:-.04em;
  color:transparent;-webkit-text-stroke:1px rgba(201,163,91,.42);opacity:.9;
  padding-top:.06em}
.st-chapter-name{font-family:var(--nf-mono,"Space Mono",monospace);font-size:10px;
  letter-spacing:.3em;text-transform:uppercase;color:var(--nf-brass,#C9A35B);margin:0 0 12px}
.st-chapter-title{font-family:var(--nf-display,"Fraunces",Georgia,serif);font-weight:500;
  font-size:clamp(1.85rem,4.6vw,3.05rem);line-height:1.06;letter-spacing:-.028em;
  color:#ECE4D6;margin:0;text-wrap:balance;max-width:20ch}
.st-chapter-title em{font-style:italic;color:#E8C879}
.st-chapter-rule{display:block;height:1px;margin:22px 0 0;max-width:280px;
  background:linear-gradient(90deg,rgba(201,163,91,.6),transparent)}
.st-chapter-note{margin:16px 0 0;font-family:var(--nf-mono,"Space Mono",monospace);
  font-size:10.5px;letter-spacing:.1em;color:#8A8071;line-height:1.7}

/* ---- inline kickers: Music / Maker / Support share the chapter voice ---- */
.st-kicker{display:flex;align-items:center;gap:12px;margin:0 0 16px;
  font-family:var(--nf-mono,"Space Mono",monospace);font-size:10px;letter-spacing:.3em;
  text-transform:uppercase;color:var(--nf-brass,#C9A35B)}
.st-kicker-n{font-family:var(--nf-display,"Fraunces",Georgia,serif);font-size:1.9rem;
  line-height:.8;letter-spacing:-.04em;color:transparent;
  -webkit-text-stroke:1px rgba(201,163,91,.45);flex-shrink:0}
#music h2,#maker h2,#support h2,.manifesto h2{font-family:var(--nf-display,"Fraunces",Georgia,serif);
  font-weight:500;font-size:clamp(1.85rem,4.4vw,2.9rem);line-height:1.07;
  letter-spacing:-.028em;color:#ECE4D6;text-wrap:balance;margin:0}
#music h2 em,#maker h2 em,#support h2 em{font-style:italic;color:#E8C879}
#music h2::after,#maker h2::after,#support h2::after{content:"";display:block;
  height:1px;margin-top:22px;max-width:280px;
  background:linear-gradient(90deg,rgba(201,163,91,.6),transparent)}
/* Support sets its block centred — the kicker and rule follow it */
#support .st-kicker{justify-content:center}
#support h2::after{margin-inline:auto;
  background:linear-gradient(90deg,transparent,rgba(201,163,91,.6),transparent)}

/* ---- standing volumes ---- */
.library,.workshop{display:flex;flex-direction:column;gap:clamp(46px,6.5vw,86px)}
.st-vol{position:relative;display:grid;gap:clamp(26px,4vw,58px);align-items:center;
  grid-template-columns:1fr}
@media(min-width:880px){
  .st-vol{grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr)}
  .st-vol:nth-child(even) .st-vol-plate{order:2}
  .st-vol:nth-child(even) .st-vol-entry{order:1}
}

/* the plate the book stands on */
.st-vol-plate{position:relative;display:flex;justify-content:center;align-items:flex-end;
  padding-bottom:30px;perspective:1400px}
.st-shelf{position:absolute;left:4%;right:4%;bottom:22px;height:2px;border-radius:2px;
  background:linear-gradient(90deg,transparent,rgba(201,163,91,.5) 14%,
    rgba(201,163,91,.62) 50%,rgba(201,163,91,.5) 86%,transparent);
  box-shadow:0 1px 0 rgba(0,0,0,.6),0 6px 16px -6px rgba(0,0,0,.8)}
.st-pool{position:absolute;left:12%;right:12%;bottom:0;height:38px;border-radius:50%;
  background:radial-gradient(ellipse at 50% 0%,rgba(0,0,0,.62),transparent 72%);
  filter:blur(7px)}

/* the book as an object */
.st-book{position:relative;width:min(300px,74%);aspect-ratio:1/1.42;
  transform-style:preserve-3d;
  transform:rotateY(-13deg) rotateX(2.5deg) translateZ(0);
  transition:transform .55s var(--st-ease),filter .55s var(--st-ease);
  filter:drop-shadow(-14px 22px 30px rgba(0,0,0,.72))}
.st-vol:hover .st-book,.st-vol:focus-within .st-book{
  transform:rotateY(-6deg) rotateX(1deg) translateY(-12px);
  filter:drop-shadow(-16px 30px 40px rgba(0,0,0,.8))
    drop-shadow(0 0 34px color-mix(in srgb,var(--glow) 26%,transparent))}
.st-book-face{position:absolute;inset:0;overflow:hidden;
  border-radius:2px 5px 5px 2px;background:#15101C;
  box-shadow:inset 0 0 0 1px rgba(240,220,174,.14),inset -8px 0 22px -12px rgba(0,0,0,.9)}
.st-book-face img,.st-book-face svg{width:100%;height:100%;object-fit:cover;display:block}
.st-book-face svg{padding:22%;opacity:.85}
/* spine: the bound edge catching candlelight */
.st-book-spine{position:absolute;left:0;top:0;bottom:0;width:13px;border-radius:2px 0 0 2px;
  background:linear-gradient(90deg,#0B0810,#2A2033 34%,#15101C 76%,rgba(0,0,0,.55));
  box-shadow:inset -1px 0 0 rgba(0,0,0,.7),inset 1px 0 0 rgba(240,220,174,.16)}
/* page edges: the cream block of paper */
.st-book-edge{position:absolute;right:-6px;top:5px;bottom:5px;width:7px;border-radius:0 3px 3px 0;
  background:repeating-linear-gradient(180deg,#E7DCC4 0 1.5px,#C6B896 1.5px 3px);
  box-shadow:1px 0 5px rgba(0,0,0,.6);transform:rotateY(6deg);transform-origin:left center;opacity:.9}
/* one specular sweep of candlelight across the cover */
.st-book-gloss{position:absolute;inset:0;border-radius:2px 5px 5px 2px;pointer-events:none;
  background:linear-gradient(114deg,transparent 26%,rgba(255,238,196,.16) 42%,
    rgba(255,238,196,.05) 52%,transparent 68%);
  opacity:.85;transition:opacity .55s var(--st-ease),transform .55s var(--st-ease)}
.st-vol:hover .st-book-gloss{opacity:1;transform:translateX(5%)}

/* the catalogue entry beside it */
.st-vol-entry{min-width:0}
.st-vol-rule{display:flex;align-items:center;gap:14px;margin-bottom:18px}
.st-vol-n{font-family:var(--nf-display,"Fraunces",Georgia,serif);font-size:13px;font-weight:500;
  letter-spacing:.06em;color:var(--glow,#C9A35B);flex-shrink:0;
  padding:3px 9px;border:1px solid color-mix(in srgb,var(--glow) 40%,transparent);border-radius:2px}
.st-vol-code{font-family:var(--nf-mono,"Space Mono",monospace);font-size:9.5px;
  letter-spacing:.24em;text-transform:uppercase;color:#8A8071;position:relative;
  padding-left:14px;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.st-vol-code::before{content:"";position:absolute;left:0;top:50%;width:8px;height:1px;
  background:rgba(201,163,91,.5)}
.st-vol-title{font-family:var(--nf-display,"Fraunces",Georgia,serif);font-weight:500;
  font-size:clamp(1.6rem,3.6vw,2.5rem);line-height:1.08;letter-spacing:-.028em;
  color:#ECE4D6;margin:0;text-wrap:balance;
  transition:color .3s var(--st-ease)}
.st-vol:hover .st-vol-title{color:#F4E2B4}
.st-vol-sub{margin:9px 0 0;font-family:var(--nf-mono,"Space Mono",monospace);font-size:10.5px;
  letter-spacing:.14em;text-transform:uppercase;color:var(--glow,#C9A35B);opacity:.9}
.st-vol-hook{margin:14px 0 0;font-family:var(--nf-display,"Fraunces",Georgia,serif);
  font-style:italic;font-size:clamp(16px,1.9vw,19px);line-height:1.42;color:#E8C879;
  text-wrap:balance}
.st-vol-desc{margin:16px 0 0;font-size:14.8px;line-height:1.75;color:#BCB1A0;max-width:56ch}
.st-vol-tags{list-style:none;margin:22px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:7px}
.st-vol-tags li{font-family:var(--nf-mono,"Space Mono",monospace);font-size:9.5px;
  letter-spacing:.15em;text-transform:uppercase;color:#8A8071;
  padding:6px 11px;border:1px solid rgba(201,163,91,.2);border-radius:2px;
  transition:border-color .3s var(--st-ease),color .3s var(--st-ease)}
.st-vol:hover .st-vol-tags li{border-color:rgba(201,163,91,.36);color:#BCB1A0}
.st-vol-open{display:inline-flex;align-items:center;gap:10px;margin-top:26px;
  font-family:var(--nf-mono,"Space Mono",monospace);font-size:10.5px;letter-spacing:.22em;
  text-transform:uppercase;color:#ECE4D6;text-decoration:none;
  padding-bottom:9px;border-bottom:1px solid rgba(201,163,91,.34);
  transition:color .26s var(--st-ease),border-color .26s var(--st-ease)}
.st-vol-open:hover{color:#E8C879;border-color:#C9A35B}
.st-arr{display:inline-block;transition:transform .26s var(--st-ease)}
.st-vol:hover .st-arr{transform:translateX(5px)}
.st-vol .stretch{position:absolute;inset:0;z-index:3}
.st-vol-entry,.st-vol-plate{position:relative;z-index:4;pointer-events:none}
.st-vol-open,.st-vol .st-book{pointer-events:auto}

/* the closer plate — no cover art, the collection mark instead */
.st-closer .st-book-face{background:linear-gradient(168deg,#241B2E,#15101C);
  display:grid;place-items:center}
.st-closer .st-book-face svg{width:78%;height:78%;padding:0}

@media(max-width:879px){
  .st-book{width:min(232px,62%)}
  .st-vol-plate{padding-bottom:26px}
  /* chapter numeral rides above the title instead of squeezing it */
  .st-chapter{grid-template-columns:1fr;gap:0}
  .st-chapter-num{font-size:2.6rem;margin-bottom:10px;padding-top:0}
  .st-chapter-title{max-width:none}
}

/* the sticky masthead must never sit on top of a section it anchors */
.section,.manifesto,#library,#workshop,#instruments,#music,#maker,#support{
  scroll-margin-top:86px}

/* mobile: the room has to fit the phone, hero content and all */
@media(max-width:560px){
  .st-hero{min-height:calc(100svh - 64px);padding:34px 20px 92px}
  .st-hero-seal{width:70px;height:70px;margin-bottom:20px}
  .st-hero-seal::after{inset:7px}
  .st-hero-emblem{width:38px;height:38px}
  .st-hero-eyebrow{margin-bottom:13px;letter-spacing:.28em}
  .st-hero-thesis{margin-top:20px;font-size:14.5px;line-height:1.6}
  .st-hero-mantra{margin-top:10px}
  .st-colophon{margin-top:24px;padding-top:13px;gap:4px;
    grid-template-columns:repeat(4,1fr)}
  .st-colophon li{padding:0 3px}
  .st-colophon span{font-size:8px;letter-spacing:.1em}
  .st-enter{margin-top:26px}
  .st-enter-line{height:26px}
  /* the plate is atmosphere on a phone, never legible type behind the seal */
  .st-hero-plate{opacity:.2;transform:scale(1.5);transform-origin:50% 0}
}

/* ---- reduced motion ---- */
@media(prefers-reduced-motion:reduce){
  .st-hero-glow,.st-hero-beam,.st-hero-motes,.st-hero-inner{transform:none!important;opacity:1!important}
  .st-book,.st-vol:hover .st-book{transition:none;transform:rotateY(-10deg)}
  .st-book-gloss,.st-arr{transition:none}
}
"""

# scroll-linked candlelight: one warm source that tracks the descent
JS = r"""
(function(){
  if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  var hero=document.querySelector('.st-hero');if(!hero)return;
  var tick=false;
  function frame(){
    var h=hero.offsetHeight||1;
    var p=Math.min(1,Math.max(0,scrollY/h));
    hero.style.setProperty('--st-scroll',p.toFixed(4));
    tick=false;
  }
  addEventListener('scroll',function(){if(!tick){tick=true;requestAnimationFrame(frame)}},
    {passive:true});
  frame();
})();
"""


# ------------------------------------------------------------------- driver
def build(html):
    if MARK in html:
        return html
    html = rebuild_hero(html)
    html = rebuild_sec_heads(html)
    html = rebuild_kickers(html)
    html, nxt = rebuild_articles(html, "craft", 0)      # instruments + workshop
    html, _ = rebuild_articles(html, "book", nxt)       # the library
    inject = ('\n<style id="%s">%s</style>\n' % (MARK, CSS))
    html = html.replace("</head>", inject + "</head>", 1)
    i = html.rindex("</body>")
    html = html[:i] + '\n<script id="st-study-js">%s</script>\n' % JS + html[i:]
    return html
