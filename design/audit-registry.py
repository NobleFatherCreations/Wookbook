#!/usr/bin/env python3
"""Cross-check the three registries against each other and against disk.

Run from the repo root: python3 design/audit-registry.py
Exits non-zero if any check fails, so it can gate a commit or a deploy.

Why this exists
---------------
The registries disagreed, silently, for weeks. Three separate failures, all
of the same shape -- a lookup returns nothing, so the answer looks like "no
info available" when the information is sitting on disk:

  1. sites.json carried `codename: null` for four of twelve projects (The
     Loop, The Weighing, the Codex, The Listening Room). Anything keyed on
     codename simply could not see them.

  2. sites.json and chapters.json key on `codename`; BOOKS.md is written
     around `slug`. Only one project (fractal) has the same value for both,
     so the two halves of the documentation could not be joined without a
     translation table that never existed.

  3. BOOKS.md recorded festie-codex-full.html and
     source/projects/noble-father-festival.html as an unresolved discrepancy
     ("different title -- diff before doing any design work here"), which
     blocked all wook work. The two files are byte-identical. The real
     difference was with a third file, noble-father-festiebible.html, which
     is a different project.

Every check below exists because one of those actually happened. `slug` is
the canonical key -- it matches the live URL and the BOOKS.md headings, so
it is the name a person already knows.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")


def rel(p):
    return os.path.relpath(p, ROOT)


def load(name):
    return json.load(open(os.path.join(ROOT, name), encoding="utf-8"))


def tracked_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT,
                         capture_output=True, text=True).stdout
    return set(out.split("\n"))


class Audit:
    def __init__(self):
        self.fail, self.warn = [], []

    def bad(self, check, detail):
        self.fail.append((check, detail))

    def note(self, check, detail):
        self.warn.append((check, detail))

    def report(self):
        for label, rows, mark in (("FAIL", self.fail, "x"),
                                  ("WARN", self.warn, "!")):
            if not rows:
                continue
            print("%s (%d)" % (label, len(rows)))
            grouped = defaultdict(list)
            for check, detail in rows:
                grouped[check].append(detail)
            for check in sorted(grouped):
                print("  %s %s" % (mark, check))
                for detail in grouped[check]:
                    print("      %s" % detail)
            print()
        if not self.fail and not self.warn:
            print("all checks pass")
        elif not self.fail:
            print("no failures; %d warning(s)" % len(self.warn))
        return 1 if self.fail else 0


def main():
    a = Audit()
    sites = load("sites.json")
    chapters = load("chapters.json")
    books_md = open(os.path.join(ROOT, "BOOKS.md"), encoding="utf-8").read()
    tracked = tracked_files()

    projects = sites["projects"]
    by_slug = {}

    # --- 1. every project is addressable -------------------------------
    for p in projects:
        title = p.get("title", "(untitled)")
        slug = p.get("slug")
        if not slug:
            a.bad("project has no slug", title)
            continue
        if slug in by_slug:
            a.bad("duplicate slug", "%s used by %s and %s"
                  % (slug, by_slug[slug].get("title"), title))
        by_slug[slug] = p
        if not p.get("codename"):
            a.bad("codename is null -- lookups by codename miss this project",
                  "%s (slug: %s)" % (title, slug))
        for key in ("codename", "slug"):
            val = p.get(key) or ""
            if val and not re.fullmatch(r"[a-z0-9][a-z0-9-]*", val):
                a.bad("identifier is not url/filename safe",
                      "%s.%s = %r" % (title, key, val))

    # --- 2. declared files exist and are tracked -----------------------
    def check_path(owner, key, path):
        if not path:
            return
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            a.bad("declared file missing from disk", "%s.%s -> %s"
                  % (owner, key, path))
        elif path not in tracked:
            a.bad("declared file exists but is untracked", "%s.%s -> %s"
                  % (owner, key, path))

    for p in projects:
        for key in ("localSource", "dataSource"):
            check_path(p.get("title", "?"), key, p.get(key))
    check_path("hub", "localSource", sites.get("hub", {}).get("localSource"))

    # --- 3. no orphan sources ------------------------------------------
    declared = set()

    def collect(node):
        if isinstance(node, dict):
            for v in node.values():
                collect(v)
        elif isinstance(node, list):
            for v in node:
                collect(v)
        elif isinstance(node, str) and node.endswith((".html", ".json")):
            declared.add(node)

    collect(sites)
    for path in sorted(tracked):
        if not path.endswith(".html"):
            continue
        if not (path.startswith("source/projects/") or path.startswith("fixes/")
                or "/" not in path):
            continue
        if path not in declared:
            a.note("tracked source not referenced by sites.json -- unfindable",
                   path)

    # --- 4. declared sync pairs really are in sync ---------------------
    # Two projects deliberately keep the same document at two paths. For
    # those, identical is the required state and *drift* is the bug -- the
    # wook pair silently desynchronised once already when a repo-wide sweep
    # walked source/projects/ and missed the repo-root copy. Any duplicate
    # that is NOT declared here is the other kind of problem: an
    # accidental copy nobody knows is being maintained.
    def digest(path):
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            return None
        with open(full, "rb") as fh:
            return hashlib.md5(fh.read()).hexdigest()

    paired = set()
    for pair in sites.get("syncPairs", []):
        files = pair.get("files") or []
        paired.update(files)
        seen = {}
        for path in files:
            if path not in tracked:
                a.bad("sync pair names an untracked file",
                      "%s: %s" % (pair.get("project"), path))
                continue
            dg = digest(path)
            if dg is None:
                a.bad("sync pair names a missing file",
                      "%s: %s" % (pair.get("project"), path))
            else:
                seen[path] = dg
        if len(set(seen.values())) > 1:
            a.bad("sync pair has DRIFTED -- these must be byte-identical",
                  "%s: %s" % (pair.get("project"), " vs ".join(sorted(seen))))

    digests = defaultdict(list)
    for path in sorted(tracked):
        if not path.endswith(".html") or path in paired:
            continue
        dg = digest(path)
        if dg:
            digests[dg].append(path)
    for paths in digests.values():
        if len(paths) > 1:
            a.bad("undeclared byte-identical duplicates -- declare in "
                  "sites.json syncPairs or remove one", " == ".join(paths))

    # --- 5. registries agree on the same projects ----------------------
    chapter_slugs = {b.get("slug") for b in chapters["books"]}
    for slug in sorted(set(by_slug) - chapter_slugs):
        a.note("project absent from chapters.json", slug)
    for slug in sorted(chapter_slugs - set(by_slug)):
        a.bad("chapters.json names a project sites.json does not", str(slug))

    for b in chapters["books"]:
        slug, title = b.get("slug"), b.get("title")
        if not b.get("project"):
            a.bad("chapters.json project key is null", "%s (slug: %s)"
                  % (title, slug))
        movements = b.get("movements") or []
        chs = list(b.get("chapters") or [])
        for m in movements:
            chs.extend(m.get("chapters") or [])
        if not chs:
            a.note("chapters.json holds no chapters for this book", str(title))
        for c in chs:
            if not c.get("slug"):
                a.note("chapter has no slug -- only an anchor number",
                       "%s ch.%s" % (title, c.get("n")))
                break

    # --- 6. BOOKS.md covers every project, under the canonical key -----
    headings = dict(re.findall(r"^## ([^\s]+) — (.+?)(?:\s+\*\*\[|$)",
                               books_md, re.M))
    for slug, p in sorted(by_slug.items()):
        if slug not in headings:
            a.bad("no BOOKS.md section for this project",
                  "%s (expected heading '## %s — ')" % (p.get("title"), slug))
    for head in sorted(set(headings) - set(by_slug)):
        a.bad("BOOKS.md section names a project sites.json does not", head)

    # --- 7. prose exists for every project -----------------------------
    prose_dir = os.path.join(ROOT, "content", "prose")
    prose = {f[:-3] for f in os.listdir(prose_dir)
             if f.endswith(".md") and f not in ("ALL-BOOKS.md", "README.md")}
    # The prose filename must equal the slug. Anything looser is how
    # content/prose/festival.md came to hold The Festie *Codex* while slug
    # "festival" belongs to The Festie *Bible*.
    mapped = set()
    for p in projects:
        slug = p.get("slug")
        if slug in prose:
            mapped.add(slug)
        elif p.get("codename") in prose:
            a.bad("prose file is named after codename, not slug",
                  "content/prose/%s.md should be %s.md (%s)"
                  % (p.get("codename"), slug, p.get("title")))
            mapped.add(p.get("codename"))
        else:
            a.note("no prose extracted for this project",
                   "%s (expected content/prose/%s.md)" % (p.get("title"), slug))
    for orphan in sorted(prose - mapped):
        a.bad("prose file matches no project slug",
              "content/prose/%s.md" % orphan)

    # --- 8. INDEX.md exists and is not stale ---------------------------
    index_path = os.path.join(ROOT, "INDEX.md")
    if not os.path.exists(index_path):
        a.bad("INDEX.md missing", "run python3 design/build-index.py --apply")
    else:
        index = open(index_path, encoding="utf-8").read()
        for p in projects:
            if "`%s`" % p.get("slug") not in index:
                a.bad("INDEX.md is stale -- project absent",
                      "%s; regenerate with design/build-index.py --apply"
                      % p.get("title"))

    print("audited %d projects, %d chapter records, %d prose files\n"
          % (len(projects), len(chapters["books"]), len(prose)))
    return a.report()


if __name__ == "__main__":
    sys.exit(main())
