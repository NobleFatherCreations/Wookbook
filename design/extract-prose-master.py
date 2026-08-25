#!/usr/bin/env python3
"""Extract real chapter/content prose for every Noble Father Creations book
and tool, straight from each project's own shipped source — no invented
content, only what the project itself already contains.

Run from the repo root: python3 design/extract-prose-master.py [--apply]
Dry-run (default) prints word counts only. --apply writes the .md files to
content/prose/, plus content/prose/ALL-BOOKS.md (everything concatenated).

Three extraction methods, matched per-project to how that project actually
stores its content:
  - static:  headings/paragraphs/list-items walked straight out of the HTML
             (feminine, children, wook, fracture, loop, scale, faith)
  - fractal: a JS `const DATA = {...}` object (happens to be valid JSON)
  - root:    a branching guided-practice state machine (shell(...) calls)
  - json:    a plain JS `NAME = [...]` array that is itself valid JSON, for
             reference-style content that isn't prose in the chapter sense
             (playbook's 349-entry tactic compendium)
  - music:   static, but framing copy only -- not a chapter book, noted as
             such rather than forced into the same shape as the others.
"""
import json
import os
import re
import sys

from bs4 import BeautifulSoup

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT_DIR = os.path.join(ROOT, "content", "prose")


def clean_text(s):
    return re.sub(r"\s+", " ", s).strip()


def extract_static(path, skip_selectors=None):
    """Walk h1-h4/p/li/blockquote in document order, tags stripped."""
    raw = open(path, encoding="utf-8", errors="replace").read()
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup.find_all(["script", "style", "svg", "nav"]):
        tag.decompose()
    for tag in soup.find_all(attrs={"aria-hidden": "true"}):
        tag.decompose()

    lines, seen_recent = [], []

    def emit(line):
        line = clean_text(line)
        if not line:
            return
        if seen_recent and seen_recent[-1] == line:
            return
        seen_recent.append(line)
        if len(seen_recent) > 3:
            seen_recent.pop(0)
        lines.append(line)

    body = soup.body or soup
    heading_tags = {"h1": "#", "h2": "##", "h3": "###", "h4": "####"}
    for el in body.find_all(["h1", "h2", "h3", "h4", "p", "li", "blockquote"]):
        if el.name == "p" and el.find_parent("li"):
            continue
        text = el.get_text(" ", strip=True)
        if not text:
            continue
        if el.name in heading_tags:
            emit(f"\n{heading_tags[el.name]} {text}\n")
        elif el.name == "li":
            emit(f"- {text}")
        elif el.name == "blockquote":
            emit(f"> {text}")
        else:
            emit(text)
    return "\n".join(lines)


def extract_fractal(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    i = text.find("const DATA = ") + len("const DATA = ")
    data, _ = json.JSONDecoder().raw_decode(text, i)

    def block_text(blocks):
        lines = []
        for b in blocks:
            t, x = b.get("t"), b.get("x", "")
            if t == "h":
                lines.append(f"\n### {x}\n")
            elif t == "q":
                lines.append(f"> {x}")
            else:
                lines.append(x)
        return "\n\n".join(l for l in lines if l)

    out = ["## Framing chapters\n"]
    for c in data["closings"]:
        out.append(f"\n## {c.get('kicker','')} — {c.get('title','')}\n")
        if c.get("sub"):
            out.append(f"*{c['sub']}*\n")
        out.append(block_text(c.get("blocks", [])))
    out.append("\n\n---\n\n## The eight cycle stages\n")
    for s in data["stages"]:
        out.append(f"\n### {s['n']}. {s['name']} — {s['fn']}\n")
        out.append(f"**What it looks like:** {s['gloss']}\n")
        out.append(f"**What it actually is:** {s['truth']}\n")
        out.append(f"**What it sounds like:** {s['sound']}\n")
    out.append("\n\n---\n\n## The thirty sectors\n")
    for sec in data["sectors"]:
        n = sec["num"]
        name = sec.get("full") or sec.get("short")
        out.append(f"\n### Sector {n}: {name}\n")
        if sec.get("controls"):
            out.append(f"*Controls: {sec['controls']}*\n")
        tech_name = data["techNames"][n - 1] if n - 1 < len(data["techNames"]) else None
        essence = data["essence"].get(str(n))
        if tech_name:
            out.append(f"**Technique: {tech_name}**" + (f" — {essence}" if essence else "") + "\n")
        out.append(sec.get("narrative", ""))
    return "\n".join(out)


def extract_root(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    STEP_TITLES = {
        "callback": "0. Before we begin (returning-visitor check-in)",
        "resume": "0b. Welcome back", "root": "1. Where it starts",
        "who": "2. Who / what surfaced", "conscious": "3. Was this already on your mind?",
        "breath": "3b. A breath, if this was buried", "belief": "4. Naming the belief",
        "theme-pick": "4b. If more than one theme surfaced", "origin": "5. Where the belief came from",
        "originfollow": "5b. Following the origin", "body": "6. Where you feel it in the body",
        "protector": "7. Naming the protector", "tally": "8. What it's cost you / given you",
        "named": "9. Naming it", "action": "10. One action",
        "commitment": "11. Commitment / how you'll know", "record": "12. Closing record",
    }

    def find_str_literal(s, start):
        i = start
        while i < len(s) and s[i] in " \t\n":
            i += 1
        if i >= len(s) or s[i] not in "\"'`":
            return None, start
        quote = s[i]
        j, buf = i + 1, []
        while j < len(s):
            c = s[j]
            if c == "\\" and j + 1 < len(s):
                buf.append(s[j:j + 2]); j += 2; continue
            if c == quote:
                j += 1; break
            buf.append(c); j += 1
        raw = "".join(buf)
        raw = raw.replace("\\n", " ").replace("\\'", "'").replace('\\"', '"').replace("\\`", "`")
        return re.sub(r"\s+", " ", raw).strip(), j

    def strip_html(s):
        s = re.sub(r"<[^>]+>", " ", s)
        s = re.sub(r"\$\{[^}]*\}", "", s)
        return re.sub(r"\s+", " ", s).strip()

    out = []
    for m in re.finditer(r'if\(id==="([a-z_-]+)"\)\{', text):
        step_id = m.group(1)
        block_start = m.end()
        shell_m = re.search(r"shell\(", text[block_start:block_start + 4000])
        if not shell_m:
            continue
        pos = block_start + shell_m.end()
        title, pos = find_str_literal(text, pos)
        pos += 1
        subtitle, pos = find_str_literal(text, pos)
        heading = STEP_TITLES.get(step_id, step_id)
        out.append(f"\n## {heading}\n")
        if title:
            out.append(f"**{strip_html(title)}**")
        if subtitle:
            out.append(strip_html(subtitle))
    return "\n".join(out)


def extract_bodies(path):
    """loop/scale: chapter titles/blurbs live in var CH={...} (metadata only),
    but the actual chapter prose is assigned separately per-chapter as
    `BODIES[N]=\`<p>...</p>...\`;` template literals of real HTML."""
    text = open(path, encoding="utf-8", errors="replace").read()

    ch_start = text.find("var CH={")
    ch_end = text.find("\n};", ch_start)
    ch_chunk = text[ch_start:ch_end]
    ch_pattern = re.compile(
        r"(?P<n>\d+):\{t:'(?P<t>(?:[^'\\]|\\.)*)',d:'(?P<d>(?:[^'\\]|\\.)*)',m:(?P<m>\d+)\}"
    )
    titles = {}
    for m in ch_pattern.finditer(ch_chunk):
        t = m.group("t").replace("\\'", "'").replace("\\u2019", "’").replace("\\u2014", "—")
        titles[int(m.group("n"))] = t

    out = []
    for m in re.finditer(r"BODIES\[(\d+)\]\s*=\s*`", text):
        n = int(m.group(1))
        start = m.end()
        end = text.find("`;", start)
        if end == -1:
            continue
        html_chunk = text[start:end]
        soup = BeautifulSoup(html_chunk, "html.parser")
        for tag in soup.find_all(["script", "style"]):
            tag.decompose()
        lines = []
        for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "blockquote"]):
            if el.name == "p" and el.find_parent("li"):
                continue
            t = el.get_text(" ", strip=True)
            if t:
                lines.append(t)
        title = titles.get(n, f"Chapter {n}")
        out.append(f"\n## Chapter {n}: {title}\n\n" + "\n\n".join(lines))
    return "\n".join(out)


def render_json_value(val, depth=2):
    """Generic, order-preserving JSON->markdown for CODEX_DATA-shaped content:
    strings become paragraphs, lists of strings become bullets, lists of
    dicts become one subsection per item (each string field as its own
    line), plain dicts become key: value lines with nested structures
    recursed into. Every string value in the tree ends up in the output --
    nothing silently dropped, which matters more here than a tidy shape."""
    h = "#" * min(depth, 6)
    if isinstance(val, str):
        return val + "\n"
    if isinstance(val, list):
        if not val:
            return ""
        if all(isinstance(x, str) for x in val):
            return "\n".join(f"- {x}" for x in val) + "\n"
        if all(isinstance(x, list) for x in val):
            # e.g. timeline: [[date, event, note], ...]
            lines = []
            for row in val:
                cells = [str(c) for c in row if c not in (None, "")]
                lines.append("- " + " — ".join(cells))
            return "\n".join(lines) + "\n"
        # list of dicts: one subsection per item
        parts = []
        for item in val:
            if isinstance(item, dict):
                label = item.get("name") or item.get("title") or item.get("key") or item.get("who") or item.get("entity") or item.get("say") or item.get("role") or item.get("what")
                if label:
                    parts.append(f"\n{h}# {label}\n")
                parts.append(render_json_value(item, depth + 2))
            else:
                parts.append(render_json_value(item, depth))
        return "\n".join(p for p in parts if p)
    if isinstance(val, dict):
        lines = []
        for k, v in val.items():
            if v in (None, "", [], {}):
                continue
            if isinstance(v, str):
                lines.append(f"**{k}:** {v}")
            else:
                lines.append(f"\n**{k}**\n\n" + render_json_value(v, depth + 1))
        return "\n\n".join(lines) + "\n"
    return str(val) if val not in (None, "") else ""


def extract_faith(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    i = text.find("window.CODEX_DATA = ") + len("window.CODEX_DATA = ")
    data, _ = json.JSONDecoder().raw_decode(text, i)

    out = []
    religions = data.get("religions", [])
    out.append(f"## The twenty-seven traditions\n\n*{len(religions)} entries, in the book's own order.*\n")
    for r in religions:
        out.append(f"\n## {r.get('name', r.get('id',''))}")
        if r.get("family"):
            out.append(f"*{r['family']}*\n")
        # opening/neutral read as the entry's real prose lede
        for lede_key in ("opening", "neutral", "origin"):
            if r.get(lede_key):
                label = {"opening": "Opening", "neutral": "Overview", "origin": "Origin"}[lede_key]
                out.append(f"\n### {label}\n\n{r[lede_key]}\n")
        skip = {"id", "name", "family", "opening", "neutral", "origin"}
        for k, v in r.items():
            if k in skip or v in (None, "", [], {}):
                continue
            out.append(f"\n### {k}\n\n" + render_json_value(v, 4))

    out.append("\n\n---\n\n## Shared framework\n\n"
                "*The book's methodology, applied identically across all 27 traditions "
                "above -- tactics catalogue, red flags, exit procedure, glossary, and "
                "the rest of the shared apparatus, in the book's own order.*\n")
    shared_skip = {"religions", "img", "brand"}
    for k, v in data.items():
        if k in shared_skip or v in (None, "", [], {}):
            continue
        out.append(f"\n## {k}\n\n" + render_json_value(v, 3))

    return "\n".join(out)


def extract_json_array(path, array_name, render):
    text = open(path, encoding="utf-8", errors="replace").read()
    i = text.find(array_name)
    if i == -1:
        sys.exit(f"array {array_name!r} not found in {path}")
    i = text.find("[", i)
    data, _ = json.JSONDecoder().raw_decode(text, i)
    return render(data)


def render_compendium(entries):
    out = [f"*{len(entries)} entries, grouped by category.*\n"]
    by_cat = {}
    for e in entries:
        by_cat.setdefault(e.get("cat", "Uncategorized"), []).append(e)
    for cat in sorted(by_cat):
        out.append(f"\n## {cat}\n")
        for e in by_cat[cat]:
            out.append(f"\n### {e.get('name','')}\n")
            if e.get("what"):
                out.append(f"**What it is:** {e['what']}")
            if e.get("why"):
                out.append(f"**Why it works:** {e['why']}")
            if e.get("healthy"):
                out.append(f"**Healthy alternative:** {e['healthy']}")
            if e.get("sounds"):
                out.append("**Sounds like:** " + " / ".join(e["sounds"]))
    return "\n\n".join(out)


# The first element is the project's `slug` from sites.json, and it is also
# the output filename. These agreed with nothing before 2026-08-25: this list
# used a fourth set of names alongside sites.json's `codename`, sites.json's
# `slug`, and BOOKS.md's headings. The worst collision was here -- "festival"
# named The Festie *Codex* in this file while slug "festival" belongs to The
# Festie *Bible*, a different project, which is how the two came to be
# confused for three weeks. Keep this column equal to sites.json `slug`;
# design/audit-registry.py checks it.
BOOKS = [
    ("feminine", "The Sovereign Divine Feminine", "static",
     os.path.join(ROOT, "source/projects/noble-father-sovereign.html")),
    ("children", "Playground Protectors", "static",
     os.path.join(ROOT, "source/projects/noble-father-playground.html")),
    ("wook", "The Festie Codex", "static",
     os.path.join(ROOT, "source/projects/noble-father-festival.html")),
    ("fracture", "The Fracture", "static",
     os.path.join(ROOT, "source/projects/noble-father-fracture.html")),
    ("loop", "The Loop", "bodies", os.path.join(ROOT, "fixes/loop.html")),
    ("scale", "The Weighing", "bodies", os.path.join(ROOT, "fixes/scale.html")),
    ("faith", "The Coercive Control Codex", "faith",
     os.path.join(ROOT, "source/projects/faith-index.html")),
    ("fractal", "The Fractal", "fractal",
     os.path.join(ROOT, "source/projects/noble-father-fractal.html")),
    ("shadowroot", "The Root", "root",
     os.path.join(ROOT, "source/projects/noble-father-root.html")),
    ("playbook", "The Pattern Decoder", "compendium",
     os.path.join(ROOT, "content/prose/_raw/playbook.html")),
    ("music", "The Listening Room", "static",
     os.path.join(ROOT, "content/prose/_raw/music.html")),
]

NOTES = {
    "shadowroot": "This is a tool, not a book: an 18-step branching guided practice moved "
            "through once, in sequence, not browsed like chapters. Extracted from the "
            "tool's own state-machine prompts.",
    "fractal": "An interactive technique-decoder/constellation-map tool, not a linear "
               "chapter book -- organized here by its real sections: framing chapters, "
               "the 8 cycle stages, and the 30 sectors.",
    "playbook": "A 349-entry reference compendium of manipulation tactics, not a linear "
                "chapter book -- organized here by category, one entry per tactic.",
    "music": "A curated music/streaming page, not a chapter book -- this is its framing "
             "copy only; the actual songs live as audio, not text.",
}


def main():
    apply = "--apply" in sys.argv
    os.makedirs(OUT_DIR, exist_ok=True)
    combined = ["# Noble Father Creations — Extracted Content\n",
                "*Every book and tool's own actual text, straight from its shipped "
                "source. Regenerate with `python3 design/extract-prose-master.py "
                "--apply` if any project's content changes.*\n", "---\n"]

    for slug, title, method, path in BOOKS:
        if not os.path.exists(path):
            print(f"{slug:12s} SKIP -- source not found: {path}")
            continue
        if method == "static":
            text = extract_static(path)
        elif method == "fractal":
            text = extract_fractal(path)
        elif method == "root":
            text = extract_root(path)
        elif method == "bodies":
            text = extract_bodies(path)
        elif method == "faith":
            text = extract_faith(path)
        elif method == "compendium":
            text = extract_json_array(path, "COMPENDIUM", render_compendium)
        else:
            sys.exit(f"unknown method {method}")

        word_count = len(text.split())
        rel_path = os.path.relpath(path, ROOT)
        note = NOTES.get(slug)
        header = f"# {title}\n\n*Extracted from `{rel_path}` — {word_count:,} words.*"
        if note:
            header += f"\n\n{note}"
        header += "\n\n---\n\n"
        full = header + text + "\n"

        out_path = os.path.join(OUT_DIR, f"{slug}.md")
        print(f"{slug:12s} {word_count:>7,} words  -> content/prose/{slug}.md")
        if apply:
            open(out_path, "w", encoding="utf-8").write(full)

        combined.append(f"\n# {title}\n\n*({rel_path}, {word_count:,} words)*\n")
        if note:
            combined.append(f"\n{note}\n")
        combined.append("\n---\n\n" + text + "\n")

    if apply:
        all_path = os.path.join(OUT_DIR, "ALL-BOOKS.md")
        open(all_path, "w", encoding="utf-8").write("\n".join(combined))
        print(f"\n{'ALL-BOOKS':12s} -> content/prose/ALL-BOOKS.md")
    else:
        print("\n(dry run -- pass --apply to write the .md files)")


if __name__ == "__main__":
    main()
