#!/usr/bin/env python3
"""Full reproducible build: pristine sources -> site/ + standalone/.

Order: copy sources, correct the Divide's stale <title>, hoist the
Reaction Map's `store` declaration (pre-existing TDZ crash fix), inject
shared chrome, rewire hub links (site variant only).
"""
import re, shutil, subprocess, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

ROOT = pathlib.Path(__file__).resolve().parent.parent
UP = pathlib.Path("/root/.claude/uploads/d88434ad-a117-5356-83fe-58c871ee3068")

SOURCES = {  # slug -> pristine file
    "":             UP / "b2e34ab8-noblefathercreations.html",
    "seals":        UP / "ab0da454-Noble_Father_Seals.html",
    "portals":      UP / "68bea2a4-Noble_Father_Portals.html",
    "root":         UP / "3d55834c-therootshadowwork.html",
    "reaction-map": UP / "c3105e2c-reactionmap.html",
    "divide":       UP / "00a35c60-Faithindex.html",
    "fractal":      UP / "8e202ddc-thefractal.html",
    "fracture":     UP / "7445d1a0-All_Fracture_Interactive.html",
    "sovereign":    UP / "c5f779d8-sovereignfeminine.html",
    "playground":   UP / "1732b3e6-playgroundprotectors.html",
    "festival":     ROOT / "festie-codex-full.html",
}

HUB_MAP = {
    "https://thenobledivide.netlify.app/":           "/divide/",
    "https://nobleshadows.netlify.app/":             "/root/",
    "https://sovereign-woman.netlify.app/":          "/sovereign/",
    "https://playgroundprotector.netlify.app/":      "/playground/",
    "https://wook-in-sheeps-clothing.netlify.app/":  "/festival/",
    "https://thefractal.netlify.app/":               "/fractal/",
    "https://fractures.netlify.app/":                "/fracture/",
    "https://nfcportals.netlify.app/":               "/portals/",
    "https://noblenfcseals.netlify.app/":            "/seals/",
    # noblepatterns (Pattern Decoder) and noblemusic stay external — no files yet
}

STORE_MARK = "/* ---- guarded device storage (works on Netlify; silently in-memory elsewhere) ---- */"

def fix_divide_title(html):
    return html.replace(
        "<title>The Coercive Control Codex</title>",
        "<title>The Sacred Divide — Noble Father Creations</title>", 1)

def hide_missing_assets(html):
    # the single-file export references an assets/ folder that was never
    # exported; hide those images cleanly instead of showing broken icons
    return re.sub(r'<img (src="assets/[^"]+")',
                  r'<img onerror="this.hidden=true" \1', html)

def hoist_store(html):
    i = html.index(STORE_MARK)
    j = html.index("function logTactics", i)
    block = html[i:j].rstrip() + "\n"
    html = html[:i] + html[j:]
    k = html.index("<script>") + len("<script>")
    return html[:k] + "\n" + block + html[k:]

def study_hub(html):
    import nf_hub
    return nf_hub.build(html)

def rewire_hub(html):
    n = 0
    for old, new in HUB_MAP.items():
        pat = re.compile(r'href="' + re.escape(old) + r'"(\s+target="_blank")?(\s+rel="noopener")?')
        html, c = pat.subn('href="%s"' % new, html)
        n += c
    print("  hub links rewired:", n)
    return html

def build():
    site = ROOT / "site"
    stand = ROOT / "standalone"
    for d in (site, stand):
        if d.exists():
            shutil.rmtree(d)
    for slug, src in SOURCES.items():
        html = src.read_text(encoding="utf-8")
        if slug == "divide":
            html = fix_divide_title(html)
        if slug == "reaction-map":
            html = hide_missing_assets(hoist_store(html))
        if slug == "":
            html = study_hub(html)
        if slug == "portals":
            import nf_portals
            html = nf_portals.build(html)
        if slug == "root":
            import nf_root
            html = nf_root.build(html)
        if slug == "divide":
            import nf_divide
            html = nf_divide.build(html)
        # site copy (hub gets rewired links)
        dest = site / slug / "index.html" if slug else site / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(rewire_hub(html) if slug == "" else html, encoding="utf-8")
        # standalone copy keeps original links
        (stand / ("noble-father-%s.html" % (slug or "catalogue"))).parent.mkdir(parents=True, exist_ok=True)
        (stand / ("noble-father-%s.html" % (slug or "catalogue"))).write_text(html, encoding="utf-8")
        print("copied", slug or "hub")
    (site / "_redirects").write_text((ROOT / "scripts" / "_redirects.tmpl").read_text())
    for variant in ("site", "standalone"):
        subprocess.run([sys.executable, str(ROOT / "scripts" / "nf_chrome.py"), variant], check=True)

if __name__ == "__main__":
    build()
