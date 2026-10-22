#!/usr/bin/env python3
"""Lift the brand assets and proven logic out of the v9 page, once, for the v10 build.

Run from the repo root:  python3 design/decoder-v10/extract-assets.py
Source: the v9 page in git (commit b180cbe4), so a later rewrite of playbook.html
cannot change what this extracts. Writes design/decoder-v10/assets/.
"""
import json, os, re, subprocess

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
OUT = os.path.join(os.path.dirname(__file__), "assets")
html = subprocess.run(["git", "-C", ROOT, "show", "b180cbe4:content/prose/_raw/playbook.html"],
                      capture_output=True, text=True, check=True).stdout


def js_value(name):
    m = re.search(r"const " + name + r"\s*=\s*", html)
    i = m.end()
    if html[i] in "\"'`":
        q = html[i]; j = i + 1
        while html[j] != q or html[j - 1] == "\\":
            j += 1
        return json.loads(html[i:j + 1]) if q == '"' else html[i + 1:j]
    v, e = json.JSONDecoder().raw_decode(html[i:])
    return v


def js_block(start, end_marker):
    """Verbatim JS source from `start` up to (not including) `end_marker`."""
    i = html.index(start)
    return html[i:html.index(end_marker, i)].rstrip()


def save(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"  {name:22s} {len(text)//1024:5d} KB")


os.makedirs(OUT, exist_ok=True)
faces = re.findall(r"@font-face\s*\{[^}]*\}", html)
keep = [f for f in faces if re.search(r"font-family:\s*'(IM Fell English|Public Sans)'", f)]
save("fonts.css", "\n".join(keep))
save("cover.txt", js_value("COVER_PLATE"))
save("wordmark.svg", js_value("WORDMARK"))
save("brand-logo.txt", js_value("BRAND_LOGO_URI"))
save("narrow-by-feeling.json", json.dumps(js_value("NARROW_BY_FEELING"), ensure_ascii=False))
# Proven logic, copied verbatim: the feeling clusters and the search stopwords.
save("feelings.js", js_block("const FEELING_GROUPS=[", "/* ====="))
save("search-stop.js", js_block("const SEARCH_STOP=", "function searchTokens"))
# The shared House (Noble Father Creations) menu: its own <style>, markup and script.
s = html.rfind("<style", 0, html.index('id="nf-chrome"'))
e = html.index("</script>", html.index('id="nf-chrome-js"')) + len("</script>")
save("house.html", html[s:e])
save("beacon.html", re.search(r"<script defer type='module' src='https://static\.cloudflareinsights\.com[^>]*></script>", html).group(0))
