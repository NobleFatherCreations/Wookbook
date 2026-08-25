#!/usr/bin/env python3
"""Build HOOKS-TODO.md -- the worksheet for choosing the 215 remaining hooks.

Run from the repo root: python3 design/build-hook-worksheet.py [--apply]
Dry-run (default) prints a summary, writes nothing.

What this is for
----------------
A clip's opening line has to be readable in about three seconds, muted, on a
phone. 134 of the 349 tactics already have one: the Detected tier stores real
spoken lines in what_it_sounds_like, and 30 more were reached by taking the
opening clause of short_definition.

The other 215 cannot be solved mechanically, and it is worth being exact
about why, because the obvious fixes all look like they work and don't:

  this_may_be_it_when      1,225 items, 20 distinct. Every entry has a line
                           under the budget; it is the same line. Boilerplate.
  pattern_over_time_signs    974 items, 15 distinct. Same problem.
  what_it_is                 980 items, 326 distinct -- but the short ones are
                           the shared scaffolding lines, not the specific ones.
  what_it_sounds_like        99% distinct, and on these entries it holds
                           descriptions of a signal, median 106 characters.
  short_definition           100% distinct on all 349, which is why it is the
                           fallback -- but only 30 of these 215 have a lead
                           clause that fits.

Counting lines that are unique AND short across those fields: 11 of 245.
There is no mechanical answer, so this script does not invent one. It puts
the candidate lines in front of a person instead, so choosing a hook is a
ten-second decision rather than a read of 38 fields.

Order of work
-------------
Categories with no shoot-ready entry at all come first. Ten categories cannot
appear in the release at all until they have one, so they buy the most
coverage per hook written.
"""
import argparse
import json
import os
import sys
from collections import Counter, OrderedDict, defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")
CLIPS = os.path.join(ROOT, "content", "decoder-clips.json")
DATA = os.path.join(ROOT, "content", "playbook-data.json")
OUT = os.path.join(ROOT, "HOOKS-TODO.md")

BUDGET = 80
# Fields worth offering, in the order a chooser should consider them.
# Boilerplate fields are deliberately absent -- see the module docstring.
CANDIDATE_FIELDS = ("what_it_sounds_like", "short_definition", "what_it_is",
                    "core_meaning")


def candidates(entry, boilerplate):
    """Distinct lines from this entry that aren't shared with other entries."""
    out = []
    for field in CANDIDATE_FIELDS:
        value = entry.get(field)
        items = value if isinstance(value, list) else [value]
        for item in items:
            if not isinstance(item, str):
                continue
            line = item.strip()
            if not line or line in boilerplate:
                continue
            if any(line == existing for _, existing in out):
                continue
            out.append((field, line))
    out.sort(key=lambda pair: len(pair[1]))
    return out[:4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    clips = json.load(open(CLIPS, encoding="utf-8"))["clips"]
    entries = {e["name"]: e
               for e in json.load(open(DATA, encoding="utf-8"))["codex_completed"]}

    # A line repeated across entries identifies nothing, whatever field it
    # sits in. Work that out from the corpus rather than hard-coding it.
    seen = Counter()
    for entry in entries.values():
        for field in CANDIDATE_FIELDS:
            value = entry.get(field)
            items = value if isinstance(value, list) else [value]
            for item in items:
                if isinstance(item, str) and item.strip():
                    seen[item.strip()] += 1
    boilerplate = {line for line, n in seen.items() if n > 1}

    todo = [c for c in clips if c["stage"] == "needs_hook"]
    ready_cats = {c["category"] for c in clips if c["stage"] == "shoot_ready"}
    all_cats = {c["category"] for c in clips}
    blocked_cats = sorted(all_cats - ready_cats)

    by_cat = defaultdict(list)
    for clip in todo:
        by_cat[clip["category"]].append(clip)

    ordered = ([c for c in blocked_cats if c in by_cat]
               + [c for c in sorted(by_cat) if c not in blocked_cats])

    L = ["# HOOKS-TODO — choose an opening line for %d tactics\n" % len(todo)]
    L.append("**Generated. Do not hand-edit** — run "
             "`python3 design/build-hook-worksheet.py --apply`. Record the "
             "chosen line in the book, not here; then rerun "
             "`design/build-decoder-clips.py --apply`.\n")
    L.append("A hook must be readable in about three seconds, muted, on a "
             "phone — roughly **%d characters**. Each tactic below lists its "
             "most distinctive short lines, longest-useful first. Pick one, or "
             "trim one at a boundary the sentence already has.\n" % BUDGET)
    L.append("Lines shared across entries are excluded: "
             "`this_may_be_it_when` has 20 distinct values across the whole "
             "corpus and `pattern_over_time_signs` has 15, so neither can "
             "identify a tactic no matter how short it is.\n")

    if blocked_cats:
        L.append("## Do these first\n")
        L.append("These %d categories have **no shoot-ready entry at all** and "
                 "cannot appear in the release until one is written:\n"
                 % len(blocked_cats))
        for cat in blocked_cats:
            L.append("- **%s** — %d tactics waiting" % (cat, len(by_cat[cat])))
        L.append("")

    for cat in ordered:
        flag = "  ·  **blocks this category**" if cat in blocked_cats else ""
        L.append("## %s (%d)%s\n" % (cat, len(by_cat[cat]), flag))
        for clip in sorted(by_cat[cat], key=lambda c: c["name"]):
            entry = entries[clip["name"]]
            L.append("### %s" % clip["name"])
            L.append("")
            L.append("`%s` · current opening is %d chars, %d over"
                     % (clip["tier"], clip["hook_chars"],
                        max(0, clip["hook_chars"] - BUDGET)))
            L.append("")
            cands = candidates(entry, boilerplate)
            if not cands:
                L.append("- *(no distinctive line under any field — needs "
                         "writing from scratch)*")
            for field, line in cands:
                mark = "**fits**" if len(line) <= BUDGET else "%d over" % (
                    len(line) - BUDGET)
                L.append("- [ ] `%d` %s — %s  <br>`%s`"
                         % (len(line), mark, field, line))
            L.append("")

    print("%d tactics need a hook" % len(todo))
    print("%d categories blocked entirely: %s"
          % (len(blocked_cats), ", ".join(blocked_cats) or "none"))
    fits = sum(1 for c in todo
               if any(len(l) <= BUDGET
                      for _, l in candidates(entries[c["name"]], boilerplate)))
    print("%d of %d already have a distinctive line that fits as written"
          % (fits, len(todo)))

    if not args.apply:
        print("\ndry run -- pass --apply to write %s"
              % os.path.relpath(OUT, ROOT))
        return 0
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
