#!/usr/bin/env python3
"""
Generate THE HOUSE cross-project nav (the nf-chrome catalogue panel) from
sites.json, so it is never hand-pasted/hand-edited per page again.

Usage:
  python3 design/build-house-nav.py --page root            # print HTML block for one page
  python3 design/build-house-nav.py --apply file1.html ...  # replace the block in place

The entry list below (url/desc/accent/external) is curated presentation data
that doesn't live in sites.json (short "why visit" copy, per-volume accent
dot color, roman numeral order) -- but every title is asserted equal to
sites.json's own title for that slug/url at generation time, so title drift
(e.g. "The Sacred Divide" vs sites.json's "The Coercive Control Codex") is
caught and fixed here rather than silently re-copied forward.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITES = json.loads((ROOT / "sites.json").read_text())

ROMAN = ["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV"]

# (slug-for-lookup, url, desc, accent-hex, external-target-blank)
ENTRIES = [
    ("loop",     "https://noblefathercreations.com/loop",        "The machine that learns you",   "#6E93B5", False),
    ("__press",  "https://noblenfcseals.netlify.app/",            "Real wax, a voice inside",       "#E8C879", False),
    ("__portals","https://nfcportals.netlify.app/",                "Strontium glow, no battery",     "#7FD9D4", False),
    ("shadowroot","https://nobleshadows.netlify.app/",             "A shadow work practice",         "#D9964A", False),
    ("scale",    "https://noblefathercreations.com/scale",        "How to be right about people",   "#9B8FA8", False),
    ("faith",    "https://thenobledivide.netlify.app/",            "25 traditions, 750 entries",     "#C29A52", False),
    ("fractal",  "https://thefractal.netlify.app/",                "One pattern runs the world",     "#E5A93C", False),
    ("fracture", "https://fractures.netlify.app/",                 "The reading edition",            "#C9A35B", False),
    ("feminine", "https://sovereign-woman.netlify.app/",           "A field guide",                  "#C85F7E", False),
    ("children", "https://playgroundprotector.netlify.app/",       "Shaela's guide for brave kids",  "#FFC23D", False),
    ("wook",     "https://wook-in-sheeps-clothing.netlify.app/",   "The gate — attendee's cut",      "#D8FF3D", False),
    ("festival", "https://noblefathercreations.com/festival",      "Twelve field guides, the whole festival world", "#4FD1C5", False),
    ("__casting","https://incandescent-kataifi-cde77d.netlify.app/","Hand-poured, one of one",       "#E07856", False),
    ("playbook", "https://noblepatterns.netlify.app/",              "349 tactics, decoded",           "#8A8071", True),
    ("music",    "https://noblemusic.netlify.app/",                 "Free to stream",                 "#8A8071", True),
]

# volume label overrides where the house's own short-form name differs from
# the book's full sites.json title (e.g. shop/press/casting aren't in
# sites.json's `projects` list at all -- they're craftBusiness).
LABEL_OVERRIDE = {
    "__press": "The Press",
    "__portals": "The Portals",
    "__casting": "The Casting",
}

def _lookup_title(key):
    if key in LABEL_OVERRIDE:
        return LABEL_OVERRIDE[key]
    for p in SITES["projects"]:
        if p["slug"] == key:
            return p["title"]
    raise KeyError(f"no sites.json project with slug {key!r}")

def build_entries():
    out = []
    for key, url, desc, accent, external in ENTRIES:
        title = _lookup_title(key)
        out.append({"title": title, "url": url, "desc": desc, "accent": accent, "external": external})
    return out

def render_row(i, e, here):
    num = ROMAN[i]
    dot = f'<span class="nf-dot" style="--va:{e["accent"]}" aria-hidden="true"></span>'
    numspan = f'<span class="nf-num">{num}</span>'
    if here:
        vol = f'<span class="nf-vol">{e["title"]}<span class="nf-here-dot" aria-hidden="true"></span></span>'
        a_open = '<a href="#" aria-current="page">'
        li_class = "nf-row nf-here"
    else:
        vol = f'<span class="nf-vol">{e["title"]}</span>'
        target = ' target="_blank" rel="noopener"' if e["external"] else ""
        a_open = f'<a href="{e["url"]}"{target}>'
        li_class = "nf-row"
    ext = '<span class="nf-ext">&#8599;</span>' if e["external"] else ""
    desc = f'<span class="nf-desc">{e["desc"]}</span>'
    return (f'<li class="{li_class}" style="--nf-i:{i}">{a_open}{dot}{numspan}{vol}{ext}{desc}</a></li>')

def render_block(current_url, page_slug, extra_attrs="", include_ribbon=False):
    entries = build_entries()
    rows = []
    matched_here = False
    for i, e in enumerate(entries):
        here = e["url"].rstrip("/") == current_url.rstrip("/")
        if here:
            matched_here = True
        rows.append(render_row(i, e, here))
    if not matched_here:
        raise ValueError(f"current_url {current_url!r} did not match any nav entry -- add it to ENTRIES")
    ribbon = '<div class="nf-ribbon" aria-hidden="true"></div>' if include_ribbon else ""
    count_word = len(entries)
    return (
        f'<div id="nf-chrome" class="nf-chrome" data-nf-page="{page_slug}"{extra_attrs}>'
        f'{ribbon}'
        f'<div class="nf-veil" aria-hidden="true"></div>'
        f'<button class="nf-seal" type="button" aria-expanded="false" aria-controls="nf-panel" '
        f'aria-label="Open the Catalogue — Noble Father Creations">NF</button>'
        f'<div class="nf-scrim" aria-hidden="true"></div>'
        f'<nav class="nf-panel" id="nf-panel" aria-label="The Catalogue" aria-hidden="true">'
        f'<div class="nf-panel-head"><div><div class="nf-eyebrow">Noble Father Creations</div>'
        f'<h2 class="nf-panel-title">The Catalogue</h2></div>'
        f'<button class="nf-close" type="button" aria-label="Close the Catalogue">&#10005;</button></div>'
        f'<ul class="nf-toc">{"".join(rows)}</ul>'
        f'<div class="nf-panel-foot">Bound by hand in the study &mdash; {count_word} volumes &amp; counting.</div>'
        f'</nav></div>'
    )

BLOCK_RE = re.compile(r'<div id="nf-chrome"[^>]*>.*?</nav></div>', re.DOTALL)

NF_CHROME_CSS = (ROOT / "design" / "nf-chrome-css.txt").read_text()
NF_CHROME_JS = (ROOT / "design" / "nf-chrome-js.txt").read_text()

def apply_to_file(path, current_url, page_slug):
    text = path.read_text()
    m = BLOCK_RE.search(text)
    if not m:
        raise ValueError(f"{path}: no existing nf-chrome block found -- use --insert-full for a page with no nav yet")
    had_ribbon = '<div class="nf-ribbon"' in m.group(0)
    extra_attrs_m = re.search(r'data-nf-reveal=\'[^\']*\'', m.group(0))
    extra_attrs = (" " + extra_attrs_m.group(0)) if extra_attrs_m else ""
    new_block = render_block(current_url, page_slug, extra_attrs=extra_attrs, include_ribbon=had_ribbon)
    text = text[:m.start()] + new_block + text[m.end():]
    path.write_text(text)
    return True

def insert_full_block(path, current_url, page_slug):
    """For a page with no nf-chrome at all: insert CSS before </head> (or as
    the last <style> before </body> if no </head> match), HTML+JS before
    </body>. Errors if an nf-chrome block already exists (use --apply instead)."""
    text = path.read_text()
    if BLOCK_RE.search(text):
        raise ValueError(f"{path}: already has an nf-chrome block -- use --apply instead")
    if 'id="nf-chrome-css"' in text or 'id="nf-chrome-js"' in text:
        raise ValueError(f"{path}: already has nf-chrome CSS/JS but no HTML block -- inspect manually, don't double-insert")
    body_close = text.rfind("</body>")
    if body_close == -1:
        raise ValueError(f"{path}: no </body> found")
    html_block = render_block(current_url, page_slug, include_ribbon=False)
    insertion = NF_CHROME_CSS + "\n" + html_block + "\n" + NF_CHROME_JS + "\n"
    text = text[:body_close] + insertion + text[body_close:]
    path.write_text(text)
    return True

NH_BLOCK_RE = re.compile(
    r'<button type="button" id="nh-tab".*?<script id="nh-js">.*?</script>',
    re.DOTALL,
)
NH_STYLE_RE = re.compile(r'<style id="nh-css">.*?</style>\s*', re.DOTALL)
NH_PRINT_RE = re.compile(r'#nh-tab,#nh-veil')

def convert_nh_to_nf(path, current_url, page_slug):
    """Replace the older #nh-tab red side-tab component (loop/scale/playbook/
    music) with the current nf-chrome seal+drawer, matching the 8+2 pages
    already converted. Removes the nh-* <style>, HTML, and <script> blocks
    plus the #nh-tab/#nh-veil print-media reference, then inserts the
    canonical nf-chrome block before </body>."""
    text = path.read_text()
    if not NH_BLOCK_RE.search(text):
        raise ValueError(f"{path}: no nh-tab HTML+JS block found")
    if not NH_STYLE_RE.search(text):
        raise ValueError(f"{path}: no nh-css style block found")
    text = NH_STYLE_RE.sub("", text)
    text = NH_BLOCK_RE.sub("", text)
    text = NH_PRINT_RE.sub("#nf-chrome", text)
    body_close = text.rfind("</body>")
    if body_close == -1:
        raise ValueError(f"{path}: no </body> found")
    html_block = render_block(current_url, page_slug, include_ribbon=False)
    insertion = NF_CHROME_CSS + "\n" + html_block + "\n" + NF_CHROME_JS + "\n"
    text = text[:body_close] + insertion + text[body_close:]
    path.write_text(text)
    return True

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", nargs=2, metavar=("URL", "SLUG"), help="print the block for a given current-page URL and data-nf-page slug")
    ap.add_argument("--apply", nargs=3, metavar=("FILE", "URL", "SLUG"), action="append", default=[])
    ap.add_argument("--insert-full", nargs=3, metavar=("FILE", "URL", "SLUG"), action="append", default=[])
    ap.add_argument("--convert-nh", nargs=3, metavar=("FILE", "URL", "SLUG"), action="append", default=[])
    args = ap.parse_args()
    if args.print:
        print(render_block(args.print[0], args.print[1]))
    for f, url, slug in args.apply:
        apply_to_file(Path(f), url, slug)
        print(f"updated {f}")
    for f, url, slug in args.insert_full:
        insert_full_block(Path(f), url, slug)
        print(f"inserted full block into {f}")
    for f, url, slug in args.convert_nh:
        convert_nh_to_nf(Path(f), url, slug)
        print(f"converted nh-tab to nf-chrome in {f}")
