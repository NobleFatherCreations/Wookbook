#!/usr/bin/env python3
"""Inject the Noble Father shared chrome (design tokens, wax-seal Catalogue
navigation, ink-veil page transitions) into every volume.

Two variants:
  site       — links are root-relative paths (/seals/ etc.), for the unified site
  standalone — links are the existing *.netlify.app URLs, for interim hosting

The chrome never touches page content or logic: it appends one <style> to
<head> and one nav fragment + <script> before </body>. Idempotent.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# slug, roman, title, descriptor, old netlify URL (None = not yet hosted)
VOLUMES = [
    ("",             "I",    "The Catalogue",                "Every volume, one shelf",            None),
    ("seals",        "II",   "The Press",                    "Real wax, a voice inside",           "https://noblenfcseals.netlify.app/"),
    ("portals",      "III",  "The Portals",                  "Strontium glow, no battery",         "https://nfcportals.netlify.app/"),
    ("root",         "IV",   "The Root",                     "A shadow work practice",             "https://nobleshadows.netlify.app/"),
    ("reaction-map", "V",    "The Reaction Map",             "Conscious consumption, mapped",      None),
    ("divide",       "VI",   "The Sacred Divide",            "25 traditions, 750 entries",         "https://thenobledivide.netlify.app/"),
    ("fractal",      "VII",  "The Fractal",                  "One pattern runs the world",         "https://thefractal.netlify.app/"),
    ("fracture",     "VIII", "All Fracture",                 "The reading edition",                "https://fractures.netlify.app/"),
    ("sovereign",    "IX",   "The Sovereign Divine Feminine","A field guide",                      "https://sovereign-woman.netlify.app/"),
    ("playground",   "X",    "Playground Protectors",        "Shaela's guide for brave kids",      "https://playgroundprotector.netlify.app/"),
    ("festival",     "XI",   "The Festie Codex",             "The gate — attendee's cut",          "https://wook-in-sheeps-clothing.netlify.app/"),
]
EXTERNAL = [  # live volumes not yet part of this build — always external links
    ("XII",  "The Pattern Decoder", "349 tactics, decoded", "https://noblepatterns.netlify.app/"),
    ("XIII", "The Music",           "Free to stream",       "https://noblemusic.netlify.app/"),
]

FRAUNCES_LINK = ('<link href="https://fonts.googleapis.com/css2?family='
                 'Fraunces:opsz,wght@9..144,500;9..144,600&display=swap" rel="stylesheet">')

CSS = r"""
/* ============ Noble Father shared chrome — design tokens ============ */
:root{
  --nf-ink:#141019; --nf-ink-2:#0E0A14; --nf-panel:#1B1522; --nf-panel-2:#241B2E;
  --nf-bone:#ECE4D6; --nf-bone-dim:#BCB1A0; --nf-muted:#8A8071;
  --nf-brass:#C9A35B; --nf-brass-bright:#E8C879;
  --nf-wax:#B23A33; --nf-wax-bright:#DC5A4D; --nf-wax-deep:#8E2B26;
  --nf-line:rgba(201,163,91,.16);
  --nf-ease:cubic-bezier(.2,.7,.2,1);
  --nf-display:'Fraunces',Georgia,'Times New Roman',serif;
  --nf-mono:'Space Mono','IBM Plex Mono',ui-monospace,'SFMono-Regular',monospace;
}
.nf-chrome,.nf-chrome *{margin:0;padding:0;box-sizing:border-box}

/* ---- the veil: every arrival rises out of ink ---- */
.nf-veil{position:fixed;inset:0;background:var(--nf-ink-2);z-index:9990;
  pointer-events:none;opacity:0;animation:nf-veil-in 340ms var(--nf-ease) both}
@keyframes nf-veil-in{from{opacity:1}to{opacity:0}}
.nf-veil.nf-veil-out{animation:none;opacity:1;transition:opacity 180ms cubic-bezier(.5,0,.9,.6)}

/* ---- the seal ---- */
.nf-seal{position:fixed;right:18px;bottom:18px;z-index:9950;width:56px;height:56px;
  border-radius:50%;border:none;cursor:pointer;
  font-family:var(--nf-display);font-weight:600;font-size:19px;letter-spacing:.02em;
  color:#F2E6D2;text-shadow:0 -1px 1px rgba(0,0,0,.45),0 1px 1px rgba(255,255,255,.12);
  background:radial-gradient(circle at 34% 28%,var(--nf-wax-bright),var(--nf-wax) 52%,var(--nf-wax-deep) 100%);
  box-shadow:inset 0 2px 3px rgba(255,255,255,.22),inset 0 -3px 5px rgba(0,0,0,.35),
    0 0 0 3px rgba(178,58,51,.28),0 6px 18px rgba(0,0,0,.55);
  transition:transform 180ms var(--nf-ease),box-shadow 180ms var(--nf-ease)}
.nf-seal:hover{transform:translateY(-2px) rotate(-4deg);
  box-shadow:inset 0 2px 3px rgba(255,255,255,.22),inset 0 -3px 5px rgba(0,0,0,.35),
    0 0 0 3px rgba(178,58,51,.34),0 8px 22px rgba(0,0,0,.6),0 0 24px rgba(232,200,121,.28)}
.nf-seal:active{transform:scale(.92);transition-duration:90ms}
.nf-seal:focus-visible{outline:2px solid var(--nf-brass);outline-offset:3px}
.nf-seal[aria-expanded="true"]{transform:scale(.92);opacity:0;pointer-events:none;transition-duration:140ms}

/* ---- scrim + leather catalogue panel ---- */
.nf-scrim{position:fixed;inset:0;background:rgba(10,7,13,.58);backdrop-filter:blur(5px);
  -webkit-backdrop-filter:blur(5px);z-index:9960;opacity:0;pointer-events:none;
  transition:opacity 140ms var(--nf-ease)}
.nf-open .nf-scrim{opacity:1;pointer-events:auto;transition-duration:220ms}
.nf-panel{position:fixed;top:0;right:0;bottom:0;width:min(408px,100vw);z-index:9970;
  display:flex;flex-direction:column;
  background:linear-gradient(164deg,#1E1726,#141019 55%,#0E0A14),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)' opacity='.05'/%3E%3C/svg%3E");
  border-left:1px solid rgba(201,163,91,.28);
  box-shadow:inset 1px 0 0 rgba(236,228,214,.05),-32px 0 64px rgba(0,0,0,.5);
  transform:translateX(103%);visibility:hidden;
  transition:transform 160ms cubic-bezier(.5,0,.9,.6),visibility 0s 160ms}
.nf-open .nf-panel{transform:translateX(0);visibility:visible;
  transition:transform 270ms var(--nf-ease),visibility 0s}
@media(max-width:560px){
  .nf-panel{width:100vw;border-left:none;border-top:1px solid rgba(201,163,91,.28);
    transform:translateY(103%)}
  .nf-open .nf-panel{transform:translateY(0)}
}
.nf-panel-head{display:flex;align-items:flex-start;justify-content:space-between;
  padding:26px 26px 18px;border-bottom:1px solid var(--nf-line)}
.nf-eyebrow{font-family:var(--nf-mono);font-size:10px;letter-spacing:.3em;
  text-transform:uppercase;color:var(--nf-brass);margin-bottom:8px}
.nf-panel-title{font-family:var(--nf-display);font-size:27px;font-weight:500;
  color:var(--nf-bone);line-height:1.1}
.nf-close{background:none;border:1px solid rgba(201,163,91,.3);color:var(--nf-bone-dim);
  width:34px;height:34px;border-radius:50%;cursor:pointer;font-size:17px;line-height:1;
  flex-shrink:0;margin-left:12px;transition:color 140ms,border-color 140ms,transform 140ms var(--nf-ease)}
.nf-close:hover{color:var(--nf-brass-bright);border-color:var(--nf-brass);transform:rotate(90deg)}
.nf-close:focus-visible{outline:2px solid var(--nf-brass);outline-offset:2px}
.nf-toc{list-style:none;overflow-y:auto;flex:1;padding:10px 26px 18px;overscroll-behavior:contain}
.nf-row{border-bottom:1px solid rgba(201,163,91,.12)}
.nf-row a{display:grid;grid-template-columns:34px 1fr auto;grid-template-rows:auto auto;
  align-items:baseline;column-gap:10px;padding:13px 2px;text-decoration:none;
  transition:transform 160ms var(--nf-ease)}
.nf-row a:hover{transform:translateX(4px)}
.nf-row a:focus-visible{outline:2px solid var(--nf-brass);outline-offset:-2px;border-radius:4px}
.nf-num{grid-row:1/3;font-family:var(--nf-mono);font-size:11px;color:var(--nf-muted);
  transition:color 160ms,text-shadow 160ms}
.nf-row a:hover .nf-num{color:var(--nf-brass);text-shadow:0 0 12px rgba(232,200,121,.5)}
.nf-vol{font-family:var(--nf-display);font-size:16.5px;font-weight:500;color:var(--nf-bone);
  transition:color 160ms}
.nf-row a:hover .nf-vol{color:var(--nf-brass-bright)}
.nf-desc{grid-column:2/4;font-size:11.5px;color:var(--nf-muted);letter-spacing:.02em;
  font-family:system-ui,-apple-system,sans-serif}
.nf-ext{grid-column:3;font-size:11px;color:var(--nf-muted)}
.nf-row.nf-here .nf-vol{color:var(--nf-brass)}
.nf-row.nf-here .nf-num{color:var(--nf-wax-bright)}
.nf-here-dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-left:7px;
  background:radial-gradient(circle at 35% 30%,var(--nf-wax-bright),var(--nf-wax-deep));
  box-shadow:0 0 8px rgba(220,90,77,.6);vertical-align:baseline}
.nf-panel-foot{padding:14px 26px 20px;border-top:1px solid var(--nf-line);
  font-family:var(--nf-display);font-style:italic;font-size:12.5px;color:var(--nf-muted)}
.nf-open .nf-row{opacity:0;transform:translateY(9px);
  animation:nf-rise 210ms var(--nf-ease) both;animation-delay:calc(var(--nf-i)*20ms + 60ms)}
@keyframes nf-rise{to{opacity:1;transform:translateY(0)}}

@media(prefers-reduced-motion:reduce){
  .nf-veil{animation:none;opacity:0}
  .nf-veil.nf-veil-out{transition:none}
  .nf-seal,.nf-seal:hover,.nf-close:hover,.nf-row a,.nf-row a:hover{transition:none;transform:none}
  .nf-panel,.nf-open .nf-panel{transition:transform 0s,visibility 0s}
  .nf-scrim,.nf-open .nf-scrim{transition:none}
  .nf-open .nf-row{animation:none;opacity:1;transform:none}
}
"""

JS = r"""
(function(){
  var root=document.getElementById('nf-chrome');if(!root)return;
  var seal=root.querySelector('.nf-seal'),scrim=root.querySelector('.nf-scrim'),
      panel=root.querySelector('.nf-panel'),close=root.querySelector('.nf-close');
  var reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function open(){root.classList.add('nf-open');seal.setAttribute('aria-expanded','true');
    panel.removeAttribute('aria-hidden');close.focus({preventScroll:true})}
  function shut(){root.classList.remove('nf-open');seal.setAttribute('aria-expanded','false');
    panel.setAttribute('aria-hidden','true');seal.focus({preventScroll:true})}
  seal.addEventListener('click',open);
  close.addEventListener('click',shut);
  scrim.addEventListener('click',shut);
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'&&root.classList.contains('nf-open'))shut()});
  // ink-veil exit: internal same-origin links leave through the dark
  var veil=root.querySelector('.nf-veil');
  document.addEventListener('click',function(e){
    if(reduced||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||e.button!==0)return;
    var a=e.target&&e.target.closest?e.target.closest('a[href]'):null;
    if(!a||a.target==='_blank')return;
    var href=a.getAttribute('href');
    if(!href||href.charAt(0)==='#'||/^(mailto|tel|javascript):/.test(href))return;
    var u;try{u=new URL(a.href,location.href)}catch(_){return}
    if(u.origin!==location.origin)return;
    if(u.pathname===location.pathname&&u.hash)return;
    e.preventDefault();
    veil.classList.add('nf-veil-out');
    setTimeout(function(){location.href=a.href},190);
  },true);
  window.addEventListener('pageshow',function(e){
    if(e.persisted)veil.classList.remove('nf-veil-out')});
})();
"""

def toc_html(current_slug, variant):
    rows, i = [], 0
    for slug, num, title, desc, old_url in VOLUMES:
        if variant == "site":
            href = "/" if slug == "" else "/%s/" % slug
            ext = ""
        else:
            if slug == "":       # no hosted hub yet in the interim
                continue
            if slug == current_slug:
                href, ext = "#", ""
            elif old_url:
                href, ext = old_url, ""
            else:
                continue         # reaction-map has no live URL yet
        here = ' nf-here' if slug == current_slug else ''
        dot = '<span class="nf-here-dot" aria-hidden="true"></span>' if here else ''
        cur = ' aria-current="page"' if here else ''
        rows.append(
            '<li class="nf-row%s" style="--nf-i:%d"><a href="%s"%s>'
            '<span class="nf-num">%s</span><span class="nf-vol">%s%s</span>'
            '<span class="nf-desc">%s</span></a></li>' % (here, i, href, cur, num, title, dot, desc))
        i += 1
    for num, title, desc, url in EXTERNAL:
        rows.append(
            '<li class="nf-row" style="--nf-i:%d"><a href="%s" target="_blank" rel="noopener">'
            '<span class="nf-num">%s</span><span class="nf-vol">%s</span>'
            '<span class="nf-ext">&#8599;</span>'
            '<span class="nf-desc">%s</span></a></li>' % (i, url, num, title, desc))
        i += 1
    return (
        '<div id="nf-chrome" class="nf-chrome" data-nf-page="%s">'
        '<div class="nf-veil" aria-hidden="true"></div>'
        '<button class="nf-seal" type="button" aria-expanded="false" '
        'aria-controls="nf-panel" aria-label="Open the Catalogue — Noble Father Creations">NF</button>'
        '<div class="nf-scrim" aria-hidden="true"></div>'
        '<nav class="nf-panel" id="nf-panel" aria-label="The Catalogue" aria-hidden="true">'
        '<div class="nf-panel-head"><div><div class="nf-eyebrow">Noble Father Creations</div>'
        '<h2 class="nf-panel-title">The Catalogue</h2></div>'
        '<button class="nf-close" type="button" aria-label="Close the Catalogue">&#10005;</button></div>'
        '<ul class="nf-toc">%s</ul>'
        '<div class="nf-panel-foot">Bound by hand in the study &mdash; thirteen volumes &amp; counting.</div>'
        '</nav></div>' % (current_slug or "home", ''.join(rows)))

# page-specific chrome accommodations (presentation only, no logic changes)
PAGE_CSS = {
    "reaction-map": (".backtop{bottom:86px!important;right:20px!important}"
                     "body.touring .nf-seal{opacity:0;pointer-events:none}"),
    "fracture": (".prose>p:first-of-type::first-letter{font-family:var(--nf-display);"
                 "font-weight:600;font-size:3.1em;line-height:.82;float:left;"
                 "color:var(--nf-brass);padding:.06em .09em 0 0}"),
}

def inject(path, slug, variant):
    html = path.read_text(encoding="utf-8")
    if 'id="nf-chrome"' in html:
        return False
    add_font = "Fraunces" not in html
    head_bits = (FRAUNCES_LINK if add_font else "") + \
        '\n<style id="nf-chrome-css">%s%s</style>\n' % (CSS, PAGE_CSS.get(slug, ""))
    body_bits = '\n%s\n<script id="nf-chrome-js">%s</script>\n' % (toc_html(slug, variant), JS)
    if "</head>" in html:
        html = html.replace("</head>", head_bits + "</head>", 1)
    else:
        html = head_bits + html
    if "</body>" in html:
        idx = html.rindex("</body>")
        html = html[:idx] + body_bits + html[idx:]
    else:
        html += body_bits
    path.write_text(html, encoding="utf-8")
    return True

def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "site"
    base = ROOT / ("site" if variant == "site" else "standalone")
    for slug, _, title, _, _ in VOLUMES:
        if variant == "site":
            p = base / slug / "index.html" if slug else base / "index.html"
        else:
            p = base / ("noble-father-%s.html" % (slug or "catalogue"))
        if not p.exists():
            print("MISSING", p); continue
        print(("injected " if inject(p, slug, variant) else "skipped  ") + str(p))

if __name__ == "__main__":
    main()
