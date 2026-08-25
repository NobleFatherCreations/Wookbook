#!/usr/bin/env python3
"""Export the two drafting jobs as self-contained JSON briefs.

Run from the repo root: python3 design/export-drafting-inputs.py

Writes to content/drafting/ (gitignored -- these are inputs to a drafting
pass, not artefacts worth keeping):

  hooks-input.json   the clips still needing an opening line, each with the
                     entry's own candidate lines and how far over budget the
                     current one is.
  codex-input.json   the entries whose why_this_matters or what_it_is_not
                     still hold shared scaffolding, each with the specific
                     fields a replacement should be derived FROM, plus worked
                     examples taken from mature entries in the same category.

The examples matter more than the instructions. Every mature entry already
demonstrates the house voice for these two fields; a draft that reads like
the examples is right, and one that doesn't is wrong regardless of how well
it follows a prompt.
"""
import json
import os
from collections import Counter, defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUTDIR = os.path.join(ROOT, "content", "drafting")
BUDGET = 80


def lines(entry, field):
    v = entry.get(field)
    items = v if isinstance(v, list) else [v]
    return [i.strip() for i in items if isinstance(i, str) and i.strip()]


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    data = json.load(open(os.path.join(ROOT, "content", "playbook-data.json"),
                          encoding="utf-8"))
    entries = {e["name"]: e for e in data["codex_completed"]}
    clips = json.load(open(os.path.join(ROOT, "content", "decoder-clips.json"),
                           encoding="utf-8"))["clips"]

    JUDGED = ("why_this_matters", "what_it_is_not")
    counts = Counter()
    for e in entries.values():
        for f in JUDGED:
            for l in lines(e, f):
                counts[(f, l)] += 1

    def generic(e, f):
        got = lines(e, f)
        return bool(got) and all(counts[(f, l)] > 1 for l in got)

    # ---- hooks -----------------------------------------------------------
    hook_rows = []
    for c in clips:
        if c["stage"] != "needs_hook":
            continue
        e = entries[c["name"]]
        cands = []
        for f in ("what_it_sounds_like", "short_definition", "what_it_is"):
            for l in lines(e, f):
                if counts.get((f, l), 0) <= 1 or f not in JUDGED:
                    cands.append({"field": f, "chars": len(l), "line": l})
        cands.sort(key=lambda d: d["chars"])
        hook_rows.append({
            "name": c["name"], "category": c["category"], "tier": c["tier"],
            "current_hook": c["beats"]["hook"],
            "current_chars": c["hook_chars"],
            "over_by": max(0, c["hook_chars"] - BUDGET),
            "short_definition": e.get("short_definition", ""),
            "candidates": cands[:6],
        })

    # ---- codex fields ----------------------------------------------------
    by_cat_examples = defaultdict(list)
    for e in entries.values():
        if e.get("codex_maturity") != "mature":
            continue
        by_cat_examples[e["category"]].append({
            "name": e["name"],
            "short_definition": e.get("short_definition", ""),
            "why_this_matters": e.get("why_this_matters", ""),
            "what_it_is_not": lines(e, "what_it_is_not")[:2],
        })

    codex_rows = []
    for e in entries.values():
        gaps = [f for f in JUDGED if generic(e, f)]
        if not gaps:
            continue
        codex_rows.append({
            "name": e["name"], "category": e["category"],
            "tier": e.get("tier"), "maturity": e.get("codex_maturity"),
            "needs": gaps,
            "derive_from": {
                "short_definition": e.get("short_definition", ""),
                "expanded_definition": e.get("expanded_definition", ""),
                "plain_language_summary": e.get("plain_language_summary", ""),
                "what_it_sounds_like": lines(e, "what_it_sounds_like")[:4],
                "what_it_is": lines(e, "what_it_is")[:3],
                "common_false_positives": lines(e, "common_false_positives")[:3],
            },
            "current_generic": {f: lines(e, f)[:1] for f in gaps},
            "risk_flags": [f for f in (e.get("human_review_flags") or [])
                           if f in ("high_false_positive_risk",
                                    "manipulation_playbook_risk",
                                    "safety_sensitive",
                                    "culturally_sensitive",
                                    "neurodivergence_sensitive")],
        })

    json.dump({"budget_chars": BUDGET, "count": len(hook_rows),
               "clips": hook_rows},
              open(os.path.join(OUTDIR, "hooks-input.json"), "w",
                   encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"count": len(codex_rows),
               "examples_by_category": dict(by_cat_examples),
               "entries": codex_rows},
              open(os.path.join(OUTDIR, "codex-input.json"), "w",
                   encoding="utf-8"), ensure_ascii=False, indent=1)

    print("hooks-input.json  %d clips need an opening line" % len(hook_rows))
    print("codex-input.json  %d entries need a field" % len(codex_rows))
    for f in JUDGED:
        print("   %-22s %d" % (f, sum(1 for r in codex_rows if f in r["needs"])))
    print("   worked examples from mature entries in %d categories"
          % len(by_cat_examples))


if __name__ == "__main__":
    main()
