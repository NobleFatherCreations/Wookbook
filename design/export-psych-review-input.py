#!/usr/bin/env python3
"""Export the staged drafts, plus their grounding source material, as one
review input for a clinical/psychological read.

Run from the repo root: python3 design/export-psych-review-input.py

Writes content/drafting/psych-review-input.json (gitignored -- an input to
one review pass, not an artefact worth keeping on its own).

Why the source fields travel with the draft
--------------------------------------------
The earlier verification (structural integrity, near-duplicate detection,
intent-language sweep) checked that the drafts were well-formed and not
copy-pasted. It could not check whether they are *clinically sound* --
whether a disconfirming case actually holds up, whether a mechanism is
described accurately, whether an entry risks pathologising an ordinary
difference. That needs a domain read, not a text-processing one, so each
row carries the entry's own short_definition, expanded_definition,
what_it_sounds_like and common_false_positives alongside the draft, so a
reviewer can check the draft against what the book itself already says
about the tactic rather than judging it as free-standing prose.
"""
import json
import os
from collections import OrderedDict

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "content", "drafting", "psych-review-input.json")

PRIORITY_FLAGS = {"safety_sensitive", "culturally_sensitive",
                  "neurodivergence_sensitive", "manipulation_playbook_risk",
                  "high_false_positive_risk"}


def lines(entry, field):
    v = entry.get(field)
    items = v if isinstance(v, list) else [v]
    return [i.strip() for i in items if isinstance(i, str) and i.strip()]


def main():
    drafts = json.load(open(os.path.join(ROOT, "content", "playbook-drafts.json"),
                            encoding="utf-8"))
    data = json.load(open(os.path.join(ROOT, "content", "playbook-data.json"),
                          encoding="utf-8"))
    entries = {e["name"]: e for e in data["codex_completed"]}

    codex_rows = []
    for r in drafts["codex_fields"]:
        e = entries[r["name"]]
        flags = e.get("human_review_flags") or []
        codex_rows.append(OrderedDict([
            ("name", r["name"]),
            ("category", e["category"]),
            ("tier", e.get("tier")),
            ("maturity", e.get("codex_maturity")),
            ("risk_flags", [f for f in flags if f in PRIORITY_FLAGS]),
            ("priority_review", bool(set(flags) & PRIORITY_FLAGS)
             or r["confidence"] in ("medium", "low")),
            ("draft_confidence", r["confidence"]),
            ("draft_note", r.get("note", "")),
            ("drafted", OrderedDict([
                ("why_this_matters", r.get("why_this_matters")),
                ("what_it_is_not", r.get("what_it_is_not")),
            ])),
            ("source_material", OrderedDict([
                ("short_definition", e.get("short_definition", "")),
                ("expanded_definition", e.get("expanded_definition", "")),
                ("what_it_sounds_like", lines(e, "what_it_sounds_like")[:4]),
                ("common_false_positives", lines(e, "common_false_positives")[:3]),
                ("psychological_mechanism", e.get("psychological_mechanism", "")),
            ])),
        ]))

    hook_rows = []
    for h in drafts["hooks"]:
        e = entries[h["name"]]
        hook_rows.append(OrderedDict([
            ("name", h["name"]),
            ("category", e["category"]),
            ("tier", e.get("tier")),
            ("drafted_hook", h["hook"]),
            ("hook_source", h["source"]),
            ("hook_note", h.get("note", "")),
            ("priority_review", h["source"] == "composed"),
            ("source_material", OrderedDict([
                ("short_definition", e.get("short_definition", "")),
                ("what_it_sounds_like", lines(e, "what_it_sounds_like")[:4]),
            ])),
        ]))

    n_priority_codex = sum(1 for r in codex_rows if r["priority_review"])
    n_priority_hooks = sum(1 for r in hook_rows if r["priority_review"])

    payload = OrderedDict([
        ("note", "Every drafted line from content/playbook-drafts.json, "
                 "joined with the source material it was derived from, for "
                 "an independent clinical/psychological review. Nothing here "
                 "is approved -- this is the review input, not a verdict."),
        ("counts", OrderedDict([
            ("codex_entries", len(codex_rows)),
            ("codex_priority_review", n_priority_codex),
            ("hooks", len(hook_rows)),
            ("hooks_priority_review", n_priority_hooks),
        ])),
        ("codex_entries", codex_rows),
        ("hooks", hook_rows),
    ])

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(payload, open(OUT, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("wrote %s" % os.path.relpath(OUT, ROOT))
    print("  %d codex entries (%d flagged for priority review: risk-flagged "
          "or confidence < high)" % (len(codex_rows), n_priority_codex))
    print("  %d hooks (%d flagged for priority review: composed rather than "
          "trimmed from the book's own text)" % (len(hook_rows), n_priority_hooks))


if __name__ == "__main__":
    main()
