#!/usr/bin/env python3
"""Generate INDEX.md -- one page that can answer "where is X?" for any project.

Run from the repo root: python3 design/build-index.py [--apply]
Dry-run (default) prints the index, writes nothing.

Why this exists
---------------
Everything in this repo was findable only if you already knew which of four
different names a project went by, and which of five files to look in. The
Festie Bible was the clearest case: a v6 project with 12 structured guides
that had no BOOKS.md section, no chapters.json record and no prose file --
reachable only by guessing its filename.

This file is generated from sites.json, so it cannot drift the way a
hand-written index would. Every alias a project has ever been called is
listed, so a lookup by the wrong name still lands. Regenerate after any
sites.json change; design/audit-registry.py enforces the rules it relies on.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "INDEX.md")


def load(name):
    return json.load(open(os.path.join(ROOT, name), encoding="utf-8"))


def words(path):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return 0
    return len(open(full, encoding="utf-8", errors="replace").read().split())


def structure(slug, prose_path, chapters_by_slug):
    """Describe the book's real shape, measured -- not a guess."""
    book = chapters_by_slug.get(slug)
    if book:
        movements = book.get("movements") or []
        chs = list(book.get("chapters") or [])
        for m in movements:
            chs.extend(m.get("chapters") or [])
        if chs:
            return "%d chapters in %d movements" % (len(chs), len(movements))
    full = os.path.join(ROOT, prose_path) if prose_path else None
    if full and os.path.exists(full):
        text = open(full, encoding="utf-8", errors="replace").read()
        h2 = len(re.findall(r"^## ", text, re.M))
        h3 = len(re.findall(r"^### ", text, re.M))
        if h2 or h3:
            return "%d sections, %d sub-entries" % (h2, h3)
    return "—"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    sites = load("sites.json")
    chapters = load("chapters.json")
    by_slug = {b.get("slug"): b for b in chapters["books"]}
    books_md = open(os.path.join(ROOT, "BOOKS.md"), encoding="utf-8").read()
    heads = set(re.findall(r"^## ([^\s]+) — ", books_md, re.M))

    projects = sorted(sites["projects"], key=lambda p: -words(
        "content/prose/%s.md" % p.get("slug")))

    L = []
    L.append("# INDEX — where everything is\n")
    L.append("**Generated. Do not hand-edit** — run "
             "`python3 design/build-index.py --apply` after any `sites.json` "
             "change. `design/audit-registry.py` enforces the rules this "
             "relies on and exits non-zero when they break.\n")
    L.append("`slug` is the canonical key everywhere: it matches the live URL, "
             "the `BOOKS.md` heading, and the `content/prose/` filename. "
             "`codename` is kept only as an alias, because older notes and "
             "`chapters.json` were written against it.\n")

    total = sum(words("content/prose/%s.md" % p.get("slug")) for p in projects)
    L.append("%d projects · %s words of extracted prose\n"
             % (len(projects), format(total, ",")))

    L.append("\n## Lookup table\n")
    L.append("| Project | slug | alias | Live | Prose | Words |")
    L.append("|---|---|---|---|---|---|")
    for p in projects:
        slug = p.get("slug")
        code = p.get("codename")
        alias = "`%s`" % code if code and code != slug else "—"
        prose = "content/prose/%s.md" % slug
        has = os.path.exists(os.path.join(ROOT, prose))
        n = words(prose)
        L.append("| %s | `%s` | %s | [%s](%s) | %s | %s |"
                 % (p.get("title"), slug, alias, p.get("slug"), p.get("url"),
                    "`%s`" % prose if has else "—",
                    format(n, ",") if n else "—"))

    L.append("\n## Per project\n")
    for p in projects:
        slug = p.get("slug")
        code = p.get("codename")
        prose = "content/prose/%s.md" % slug
        has_prose = os.path.exists(os.path.join(ROOT, prose))
        L.append("### %s" % p.get("title"))
        L.append("")
        L.append("*%s*" % (p.get("tagline") or ""))
        L.append("")
        rows = [
            ("slug", "`%s`" % slug),
            ("alias (`codename`)", "`%s`" % code if code and code != slug
             else "none — same as slug"),
            ("live", p.get("url")),
            ("version", p.get("version")),
            ("shape", structure(slug, prose if has_prose else None, by_slug)),
            ("page source", "`%s`" % p["localSource"] if p.get("localSource")
             else "none"),
            ("structured data", "`%s`" % p["dataSource"] if p.get("dataSource")
             else "—"),
            ("prose", "`%s` (%s words)" % (prose, format(words(prose), ","))
             if has_prose else "not extracted"),
            ("chapter data", "`chapters.json` → `%s`" % slug
             if slug in by_slug else "absent from chapters.json"),
            ("notes", "`BOOKS.md` → `## %s`" % slug if slug in heads
             else "**no BOOKS.md section**"),
        ]
        if p.get("leakFix"):
            rows.append(("pending fix", "`%s`" % p["leakFix"]))
        for pair in sites.get("syncPairs", []):
            if pair.get("project") == slug:
                rows.append(("kept in sync with",
                             " + ".join("`%s`" % f for f in pair["files"])))
        for k, v in rows:
            L.append("- **%s** — %s" % (k, v))
        L.append("")

    L.append("## Adaptation assets\n")
    L.append("Short-form work products, as they get built:\n")
    L.append("| Project | Asset | What it holds |")
    L.append("|---|---|---|")
    assets = [
        ("playbook", "`content/playbook-data.json`",
         "349 tactics x 38 fields, 349 compendium entries, 109 tactic sequences"),
        ("playbook", "`content/decoder-clips.json`",
         "349 five-beat clip records; 112 shoot-ready, 152 held, 85 awaiting a hook"),
        ("playbook", "`HOOKS-TODO.md`",
         "worksheet: candidate opening lines for the 215, blocked categories first"),
        ("playbook", "`content/recipe-clips.json`",
         "109 tactic sequences; 79 shoot-ready, 30 held on their own steps' grading"),
        ("playbook", "`CODEX-TODO.md`",
         "266 entries whose why_this_matters or what_it_is_not is still scaffolding"),
        ("festival", "`content/festie-bible-data.json`",
         "12 role-based field guides with checks, outlines and scenarios"),
        ("festival", "`content/bible-clips.json`",
         "149 scenarios, all shoot-ready; 127 cross-link to Decoder tactics"),
        ("music", "`deploy/music/MANIFEST.json`",
         "176 tracks across 6 shelves, used as the bed library for every clip"),
    ]
    for slug, path, what in assets:
        exists = os.path.exists(os.path.join(ROOT, path.strip("`")))
        L.append("| `%s` | %s | %s |" % (slug, path if exists
                                         else path + " *(missing)*", what))

    L.append("\n## The registries\n")
    L.append("| File | Holds | Keyed on |")
    L.append("|---|---|---|")
    L.append("| `sites.json` | live URL, deploy route, sources, versions, "
             "changelog, sync pairs | `slug` |")
    L.append("| `BOOKS.md` | per-book content, stance and design position | "
             "`slug` (heading) |")
    L.append("| `chapters.json` | movement/chapter data | `slug`, with "
             "`project` as alias |")
    L.append("| `MEMORY.md` | cross-session history, append-only | prose |")
    L.append("| `INDEX.md` | this file — where everything is | generated |")

    text = "\n".join(L) + "\n"
    if not args.apply:
        print(text)
        print("dry run -- pass --apply to write INDEX.md", file=sys.stderr)
        return 0
    open(OUT, "w", encoding="utf-8").write(text)
    print("wrote INDEX.md (%d projects)" % len(projects))
    return 0


if __name__ == "__main__":
    sys.exit(main())
