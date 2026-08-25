#!/usr/bin/env python3
"""Fill chapters.json for the books that have no chapter data.

Run from the repo root: python3 design/extract-chapters-all.py [--apply]
Dry-run (default) prints what would be written, changes nothing.

Why this exists
---------------
CLAUDE.md names chapters.json as the single source of truth that drives the
contents page, Prev/Next nav, the reading-progress bar and THE HOUSE
cross-project map. Eight of twelve books had nothing in it, so all four of
those surfaces had nothing to read. The old TODO said the data was "not yet
extracted", which was true when it was written and stopped being true once
content/prose/ existed -- the words have been sitting there ever since.

What this does and does not do
------------------------------
Every title here is the book's own heading, verbatim. Every blurb is the
book's own first sentence under that heading, verbatim. readMin is measured
from the word count at 200 wpm, not estimated by eye. Nothing is written.

Loop and Scale are left alone: their movement/chapter data was extracted from
their own MOVEMENTS/CH literals and is richer than headings. They only get
slugs added, derived from their existing titles, because all 85 of their
chapters were addressable by anchor number alone.

Structure varies per book and is followed, not imposed:
  fractal   h2 are framing groups, h3 are the real units (sectors, stages)
  fracture  h2 sections with h3 nested beneath
  others    flat h2 sections
Front matter is marked rather than dropped -- a contents page wants to know
that "How to Use This Book" is not chapter one.
"""
import argparse
import json
import os
import re
import sys
from collections import OrderedDict

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROSE = os.path.join(ROOT, "content", "prose")
OUT = os.path.join(ROOT, "chapters.json")

WPM = 200

# Books whose h3 headings are the navigational unit, not their h2.
H3_BOOKS = {"fractal", "festival"}

# Not chapter books. Their real structure is the dataSource named in
# sites.json -- 12 role guides for the Bible, 176 tracks on 6 shelves for the
# Listening Room. Forcing headings on them would invent a shape they don't have.
NOT_CHAPTERED = {"music"}

# Interface text that survives prose extraction and is not a sentence about
# the chapter: source-count chrome, arrows, tap targets.
CHROME = re.compile(r"^§|sources? cited|→|^tap |^click |^swipe |^scroll ",
                    re.I)

# Headings that are apparatus rather than a chapter. Matched case-insensitively
# against the whole heading; kept in the data with front_matter: true so a
# contents page can order them separately instead of losing them.
FRONT_MATTER = re.compile(
    r"how to (use|read)|finding your way|preface|who this book is for|"
    r"editorial|legal notice|content disclosure|a note (on|for)|the cast|"
    r"lexicon|setlist|methodology|acknowledg|about the author|copyright|"
    r"dedication|epigraph|before we|first ride|stay in the loop|also by|"
    r"updates|sources? (&|and) citations|colophon|the real ones|"
    r"^the archive$|appendix|glossary|index|resources|why i made this|"
    r"your 9-second tour|tap a mission|the heroes")


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60] or "x"


def sections(path, level):
    """(title, body) pairs for every heading at `level`, in document order."""
    marker = "#" * level + " "
    out, title, buf = [], None, []
    for line in open(path, encoding="utf-8", errors="replace"):
        if line.startswith(marker):
            if title is not None:
                out.append((title, "\n".join(buf)))
            title, buf = line[len(marker):].strip(), []
        elif title is not None:
            buf.append(line.rstrip())
    if title is not None:
        out.append((title, "\n".join(buf)))
    return out


def blurb(body):
    """The section's own first real sentence. Never paraphrased."""
    for raw in body.split("\n"):
        line = raw.strip()
        if not line or line.startswith(("#", "|", "-", "*", ">")):
            continue
        line = re.sub(r"\*\*|__|\*", "", line)
        if len(line) < 25 or CHROME.search(line):
            continue
        m = re.match(r"(.{25,240}?[.!?])(\s|$)", line)
        return (m.group(1) if m else line[:240]).strip()
    return ""


def build(slug, url):
    path = os.path.join(PROSE, "%s.md" % slug)
    if not os.path.exists(path):
        return None
    level = 3 if slug in H3_BOOKS else 2
    rows = sections(path, level)
    chapters, n = [], 0
    for title, body in rows:
        clean = re.sub(r"^[^\w(]+\s*", "", title).strip()
        if not clean:
            continue
        front = bool(FRONT_MATTER.search(clean.lower()))
        if not front:
            n += 1
        words = len(body.split())
        chapters.append(OrderedDict([
            ("n", None if front else n),
            ("title", clean),
            ("blurb", blurb(body)),
            ("readMin", max(1, round(words / WPM)) if words else 0),
            ("words", words),
            ("slug", slugify(clean)),
            ("url", "%s#%s" % (url, slugify(clean))),
            ("front_matter", front),
        ]))
    return chapters


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    data = json.load(open(OUT, encoding="utf-8"), object_pairs_hook=OrderedDict)
    sites = json.load(open(os.path.join(ROOT, "sites.json"), encoding="utf-8"))
    url_of = {p["slug"]: p["url"] for p in sites["projects"]}

    print("%-12s %8s %8s %8s  %s" % ("slug", "units", "front", "readMin", "note"))
    for book in data["books"]:
        slug = book.get("slug")
        movements = book.get("movements") or []
        existing = list(book.get("chapters") or [])
        for m in movements:
            existing.extend(m.get("chapters") or [])

        if existing:
            # Loop and Scale: keep the richer data, only fill missing slugs.
            added = 0
            for m in movements:
                for c in m.get("chapters") or []:
                    if not c.get("slug"):
                        c["slug"] = slugify(c.get("title") or "")
                        c["url"] = "%s#%s" % (url_of.get(slug, ""), c["slug"])
                        added += 1
            print("%-12s %8d %8s %8d  kept; added %d slugs"
                  % (slug, len(existing), "-",
                     sum(c.get("readMin") or 0 for c in existing), added))
            continue

        if slug in NOT_CHAPTERED:
            book["chapterNote"] = (
                "Not a chapter book -- see dataSource in sites.json for its "
                "real structure.")
            print("%-12s %8s %8s %8s  not a chapter book"
                  % (slug, "-", "-", "-"))
            continue

        chapters = build(slug, url_of.get(slug, ""))
        if chapters is None:
            print("%-12s %8s %8s %8s  no prose file -- see dataSource"
                  % (slug, "-", "-", "-"))
            continue
        front = sum(1 for c in chapters if c["front_matter"])
        book["chapters"] = chapters
        book["chapterSource"] = ("content/prose/%s.md headings, verbatim; "
                                 "readMin measured at %d wpm" % (slug, WPM))
        print("%-12s %8d %8d %8d  extracted"
              % (slug, len(chapters) - front, front,
                 sum(c["readMin"] for c in chapters)))

    data["updated"] = "2026-08-25"
    data["todo"] = [
        "The Festie Bible and The Listening Room are not chapter books; their "
        "structure lives in the dataSource named in sites.json (12 role guides, "
        "176 tracks on 6 shelves).",
        "Blurbs are each section's own first sentence. Several read as an "
        "opening line rather than a summary -- worth an editorial pass, but "
        "they are the book's words, not invented ones.",
    ]

    if not args.apply:
        print("\ndry run -- pass --apply to write chapters.json")
        return 0
    json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(OUT, "a", encoding="utf-8").write("\n")
    print("\nwrote chapters.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
