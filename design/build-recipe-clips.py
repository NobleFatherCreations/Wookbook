#!/usr/bin/env python3
"""Build the manifest for the Pattern Decoder's 109 tactic sequences.

Run from the repo root: python3 design/build-recipe-clips.py [--apply]
Dry-run (default) prints the report, writes nothing.
--apply writes content/recipe-clips.json.

Why these are the strongest series in the catalogue
--------------------------------------------------
Naming one manipulation tactic is a commodity; every therapy account does it.
Showing the assembly ORDER is not, and RECIPES holds 109 validated sequences
that nothing else here offers:

    Grooming = Love Bombing -> Boundary Testing -> Manufactured Intimacy ->
               Intermittent Reinforcement -> Isolation -> Identity Hooking ->
               Conditional Love

Median six steps, range two to eleven. 196 distinct tactics participate, so
the series is self-cross-linking: every step is a tactic with its own clip,
and a viewer who recognises step four can go find step one.

Two things this checks that matter for publishing
-------------------------------------------------
**Held steps.** A sequence whose steps are held by the book's own grading
(reference_stub, or manipulation_playbook_risk) inherits that. A sequence
made mostly of stubs is a sequence the book has not finished describing.

**Instructional risk.** These are the highest-risk pieces in the whole
adaptation, and the risk is structural rather than per-entry: a sequence is,
by construction, a set of steps in working order. That is exactly what the
book's own misuse_warning is about. Every sequence therefore carries the
count of risk-flagged steps, and any sequence containing a
manipulation_playbook_risk step is held by default -- an author's decision,
not a pipeline's.
"""
import argparse
import json
import os
import sys
from collections import Counter, OrderedDict

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "content", "playbook-data.json")
OUT = os.path.join(ROOT, "content", "recipe-clips.json")

HOLD_FLAGS = {"manipulation_playbook_risk"}
HOLD_MATURITY = {"reference_stub"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    data = json.load(open(SRC, encoding="utf-8"))
    entries = {e["name"]: e for e in data["codex_completed"]}
    recipes = data["recipes"]

    rows = []
    for recipe in recipes:
        steps = []
        for name in recipe.get("c") or []:
            entry = entries.get(name)
            flags = set(entry.get("human_review_flags") or []) if entry else set()
            maturity = entry.get("codex_maturity") if entry else None
            steps.append(OrderedDict([
                ("name", name),
                ("known", entry is not None),
                ("maturity", maturity),
                ("short_definition", (entry or {}).get("short_definition", "")),
                ("held", bool(flags & HOLD_FLAGS) or maturity in HOLD_MATURITY),
                ("risk_flags", sorted(flags & (HOLD_FLAGS | {
                    "safety_sensitive", "high_false_positive_risk"}))),
            ]))

        held_steps = [s for s in steps if s["held"]]
        risky = [s for s in steps
                 if "manipulation_playbook_risk" in s["risk_flags"]]
        unknown = [s for s in steps if not s["known"]]

        if unknown:
            stage, why = "needs_source", ["step not in the compendium"]
        elif risky:
            stage, why = "held", ["contains %d manipulation_playbook_risk step(s)"
                                  % len(risky)]
        elif len(held_steps) > len(steps) / 2:
            stage, why = "held", ["%d of %d steps are reference stubs"
                                  % (len(held_steps), len(steps))]
        else:
            stage, why = "shoot_ready", []

        rows.append(OrderedDict([
            ("name", recipe.get("n")),
            ("description", recipe.get("d", "")),
            ("step_count", len(steps)),
            ("steps", steps),
            ("held_steps", len(held_steps)),
            ("stage", stage),
            ("held_because", why),
        ]))

    rows.sort(key=lambda r: (r["stage"] != "shoot_ready", -r["step_count"]))
    ready = [r for r in rows if r["stage"] == "shoot_ready"]

    print("Pattern Decoder -- tactic sequences")
    print("  %d sequences, %d distinct tactics participating"
          % (len(rows), len({s["name"] for r in rows for s in r["steps"]})))
    for stage, n in Counter(r["stage"] for r in rows).most_common():
        print("    %3d %s" % (n, stage))
    print()
    lengths = sorted(r["step_count"] for r in rows)
    print("  steps per sequence: median %d, range %d-%d"
          % (lengths[len(lengths) // 2], lengths[0], lengths[-1]))
    print()
    print("  held, by reason:")
    for reason, n in Counter(r["held_because"][0] for r in rows
                             if r["held_because"]).most_common(6):
        print("    %-46s %3d" % (reason[:46], n))
    print()
    print("  longest shoot-ready sequences:")
    for r in ready[:6]:
        print("    %-34s %2d steps" % (r["name"][:34], r["step_count"]))
        print("       %s" % " -> ".join(s["name"] for s in r["steps"]))

    if not args.apply:
        print("\ndry run -- pass --apply to write %s" % os.path.relpath(OUT, ROOT))
        return 0

    payload = OrderedDict([
        ("note", "Tactic sequences from the Pattern Decoder's RECIPES data. "
                 "Every name and step is the book's own; nothing is written "
                 "here. Regenerate rather than hand-editing."),
        ("source", "content/playbook-data.json"),
        ("caveat", "A sequence is by construction a set of steps in working "
                   "order, which is what the book's own misuse_warning is "
                   "about. Any sequence containing a manipulation_playbook_risk "
                   "step is held by default; publishing it is an author's "
                   "decision."),
        ("counts", {"total": len(rows), "shoot_ready": len(ready)}),
        ("sequences", rows),
    ])
    json.dump(payload, open(OUT, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    open(OUT, "a", encoding="utf-8").write("\n")
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
