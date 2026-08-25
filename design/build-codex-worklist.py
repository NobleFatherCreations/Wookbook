#!/usr/bin/env python3
"""Build CODEX-TODO.md -- which Pattern Decoder fields still need real content.

Run from the repo root: python3 design/build-codex-worklist.py [--apply]
Dry-run (default) prints the summary, writes nothing.

What "incomplete" means here
----------------------------
No field in CODEX_COMPLETED is empty -- all 38 are populated on all 349
entries, which is why a missing-field check finds nothing. The book grades
itself instead, via `codex_maturity` (mature 81 / needs_review 143 /
reference_stub 101 / developing 24) and per-entry `human_review_flags`.

What separates a mature entry from a stub is not presence, it is
specificity. Measured across the corpus:

    why_this_matters    entry-specific on 81/81 mature, generic on 101/101 stubs
    what_it_is_not      entry-specific on 81/81 mature, generic on 101/101 stubs

Those two fields are the work. Everything else is either already specific
everywhere (short_definition, what_it_sounds_like, what_it_is,
plain_language_summary) or generic everywhere **by design** -- the shared
framework the book applies identically to every entry:

    this_may_be_it_when      20 distinct lines across 1,745 items
    this_may_not_be_it_when  20 distinct lines across 1,745 items
    pattern_over_time_signs  15 distinct
    safety_note, repair_check, psychological_mechanism,
    possible_impact_on_receiver -- one shared statement each

Those are not defects and must not be "completed" -- they are the apparatus.
This script therefore only reports fields that are generic on *some* entries
and specific on others, which is the signature of unfinished work rather
than of shared scaffolding.
"""
import argparse
import json
import os
import sys
from collections import Counter, OrderedDict, defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "content", "playbook-data.json")
OUT = os.path.join(ROOT, "CODEX-TODO.md")

# Fields judged on specificity. Deliberately excludes the shared-framework
# fields listed in the docstring: they are generic everywhere on purpose.
JUDGED = ("why_this_matters", "what_it_is_not", "what_it_is",
          "short_definition", "what_it_sounds_like", "expanded_definition",
          "common_false_positives", "detection_notes",
          "how_to_distinguish_from_related")


def lines(entry, field):
    value = entry.get(field)
    items = value if isinstance(value, list) else [value]
    return [i.strip() for i in items if isinstance(i, str) and i.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    entries = json.load(open(SRC, encoding="utf-8"))["codex_completed"]

    counts = Counter()
    for entry in entries:
        for field in JUDGED:
            for line in lines(entry, field):
                counts[(field, line)] += 1

    def all_generic(entry, field):
        got = lines(entry, field)
        return bool(got) and all(counts[(field, l)] > 1 for l in got)

    # A field only counts as unfinished if it is specific somewhere -- that
    # is what distinguishes "not written yet" from "shared apparatus".
    varies = [f for f in JUDGED
              if 0 < sum(all_generic(e, f) for e in entries) < len(entries)]

    todo = OrderedDict()
    for entry in entries:
        gaps = [f for f in varies if all_generic(entry, f)]
        if gaps:
            todo[entry["name"]] = (entry, gaps)

    risky = [e for e in entries
             if "manipulation_playbook_risk" in (e.get("human_review_flags") or [])]

    print("Pattern Decoder -- codex completion worklist\n")
    print("  maturity, as the book grades itself:")
    for grade, n in Counter(e.get("codex_maturity") for e in entries).most_common():
        print("    %-16s %3d" % (grade, n))
    print()
    print("  fields that are specific on some entries and generic on others:")
    for field in varies:
        n = sum(all_generic(e, field) for e in entries)
        print("    %-32s generic on %3d / %d" % (field, n, len(entries)))
    print()
    print("  %d entries have at least one such field to write" % len(todo))
    print("  %d entries carry manipulation_playbook_risk (a publish decision, "
          "not a writing job)" % len(risky))

    if not args.apply:
        print("\ndry run -- pass --apply to write %s" % os.path.relpath(OUT, ROOT))
        return 0

    L = ["# CODEX-TODO — Pattern Decoder fields that still need real content\n"]
    L.append("**Generated. Do not hand-edit** — run "
             "`python3 design/build-codex-worklist.py --apply`. Write the "
             "content in the book itself, then re-extract with "
             "`design/extract-playbook-data.py --apply`.\n")
    L.append("Nothing here is an empty field: all 38 fields are populated on "
             "all 349 entries. What is missing is **specificity** — these "
             "fields currently hold the shared scaffolding line rather than "
             "something true of this tactic in particular.\n")
    L.append("### Not on this list, and must not be \"fixed\"\n")
    L.append("`this_may_be_it_when`, `this_may_not_be_it_when`, "
             "`pattern_over_time_signs`, `safety_note`, `repair_check`, "
             "`psychological_mechanism` and `possible_impact_on_receiver` are "
             "generic on **every** entry, including all 81 mature ones. That "
             "is the book's shared apparatus, applied identically by design — "
             "not unfinished work.\n")

    if risky:
        L.append("## Decide before publishing: %d entries flagged "
                 "`manipulation_playbook_risk`\n" % len(risky))
        L.append("The book's own judgement is that naming the mechanism this "
                 "precisely is usable as instruction. These are held out of the "
                 "clip queue automatically. Whether they should be published at "
                 "all is an author's call, not a pipeline's.\n")
        for entry in sorted(risky, key=lambda e: e["name"]):
            L.append("- **%s** — %s · `%s`"
                     % (entry["name"], entry["category"],
                        entry.get("codex_maturity")))
        L.append("")

    by_cat = defaultdict(list)
    for name, (entry, gaps) in todo.items():
        by_cat[entry["category"]].append((entry, gaps))

    L.append("## %d entries with a field to write\n" % len(todo))
    for cat in sorted(by_cat):
        rows = sorted(by_cat[cat], key=lambda r: r[0]["name"])
        L.append("### %s (%d)\n" % (cat, len(rows)))
        for entry, gaps in rows:
            L.append("- [ ] **%s** · `%s` — needs %s"
                     % (entry["name"], entry.get("codex_maturity"),
                        ", ".join("`%s`" % g for g in gaps)))
            L.append("  <br>*currently:* %s"
                     % (lines(entry, gaps[0])[0][:160] if lines(entry, gaps[0])
                        else ""))
        L.append("")

    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
