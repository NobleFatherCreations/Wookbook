#!/usr/bin/env python3
"""Extract The Pattern Decoder's three datasets out of its shipped HTML into
one machine-readable JSON source of truth.

Run from the repo root: python3 design/extract-playbook-data.py [--apply]
Dry-run (default) validates and prints a report, writes nothing.
--apply writes content/playbook-data.json.

Why this exists
---------------
The Pattern Decoder has never had a git-tracked authoring source. What the
repo holds is content/prose/_raw/playbook.html -- a 5.2MB mirror of the live
page, fetched so the prose extraction had a reproducible input. All 349
tactics live inside that file as JavaScript array literals. That is a fine
mirror and a bad source: nothing can read it without parsing a whole web
app, and a single bad live deploy would take the data with it.

This script lifts the data out into content/playbook-data.json, which is
small, diffable, and readable by anything. The HTML mirror stays as the
provenance record; the JSON becomes what everything else reads.

The three datasets, all declared as `const NAME = [...]` in the page and all
of them valid JSON once the array is isolated:

  COMPENDIUM       349 tactics, reference shape -- what/why/healthy/sounds.
                   This is the short-form unit: four fields, fixed order.
  CODEX_COMPLETED  the same 349 tactics, 38 fields each -- the full clinical
                   entry, including boundary_script, discernment_questions,
                   safety_note and misuse_warning.
  RECIPES          109 validated tactic *sequences* (Grooming, Love Addiction
                   Engineering...), each naming its component tactics in order.

Nothing is summarised, reworded or reordered. The extraction is a copy.
"""
import argparse
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "content", "prose", "_raw", "playbook.html")
OUT = os.path.join(ROOT, "content", "playbook-data.json")

# name -> expected entry count, so a silently truncated deploy fails loudly
DATASETS = {
    "COMPENDIUM": 349,
    "CODEX_COMPLETED": 349,
    "RECIPES": 109,
}


def find_array(src, name):
    """Return the JSON text of `const <name> = [...]`.

    Scans for the matching close bracket rather than regex-ing to the first
    `];` -- entry prose contains both brackets and semicolons, and several
    entries contain escaped quotes, so string state has to be tracked.
    """
    marker = "const %s = [" % name
    at = src.find(marker)
    if at < 0:
        raise LookupError("%s not declared in %s" % (name, os.path.basename(SRC)))
    start = src.index("[", at)
    depth, in_str, escaped = 0, False, False
    for i in range(start, len(src)):
        c = src[i]
        if escaped:
            escaped = False
            continue
        if c == "\\":
            escaped = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return src[start:i + 1]
    raise ValueError("%s: unterminated array literal" % name)


def check_recipe_links(compendium, recipes):
    """Every tactic a recipe names should resolve to a real compendium entry.

    Reported, never repaired -- an unresolved name is a content question for
    the author, not something a script should guess at.
    """
    known = {e["name"] for e in compendium}
    unresolved = {}
    for r in recipes:
        missing = [c for c in r["c"] if c not in known]
        if missing:
            unresolved[r["n"]] = missing
    return unresolved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write content/playbook-data.json (default: dry run)")
    args = ap.parse_args()

    src = open(SRC, encoding="utf-8", errors="replace").read()
    print("source  %s (%.1f MB)" % (os.path.relpath(SRC, ROOT), len(src) / 1e6))
    print()

    data, failed = {}, False
    for name, expected in DATASETS.items():
        try:
            entries = json.loads(find_array(src, name))
        except (LookupError, ValueError, json.JSONDecodeError) as exc:
            print("  %-16s FAILED  %s" % (name, exc))
            failed = True
            continue
        fields = sorted({k for e in entries for k in e})
        ok = len(entries) == expected
        print("  %-16s %4d entries (expected %d) %s  %d fields"
              % (name, len(entries), expected, "ok" if ok else "MISMATCH",
                 len(fields)))
        if not ok:
            failed = True
        data[name.lower()] = entries

    if failed:
        print("\nrefusing to write: extraction did not validate")
        return 1

    unresolved = check_recipe_links(data["compendium"], data["recipes"])
    print()
    if unresolved:
        print("  %d recipe(s) name a tactic with no compendium entry:"
              % len(unresolved))
        for recipe, names in sorted(unresolved.items()):
            print("    %-34s -> %s" % (recipe, ", ".join(names)))
        print("  (reported only -- resolve in the book, not here)")
    else:
        print("  recipe cross-references: all resolve to compendium entries")

    categories = sorted({e["cat"] for e in data["compendium"]})
    print("  categories: %d" % len(categories))

    payload = {
        "note": ("The Pattern Decoder's own data, copied verbatim out of "
                 "content/prose/_raw/playbook.html. Regenerate with "
                 "design/extract-playbook-data.py --apply. Nothing here is "
                 "summarised or reworded."),
        "source": "content/prose/_raw/playbook.html",
        "counts": {k: len(v) for k, v in data.items()},
        "categories": categories,
        **data,
    }

    if not args.apply:
        print("\ndry run -- pass --apply to write %s"
              % os.path.relpath(OUT, ROOT))
        return 0

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")
    print("\nwrote %s (%.1f MB)"
          % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
