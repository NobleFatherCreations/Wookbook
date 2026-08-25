#!/usr/bin/env python3
"""Validate drafted hooks and codex fields, and stage them as a reviewable overlay.

Run from the repo root: python3 design/apply-drafts.py [--apply]
Dry-run (default) validates and reports, writes nothing.

Why an overlay rather than an edit
----------------------------------
None of this is the author's text. It is drafted content awaiting a yes or
no, and it must never become indistinguishable from the book's own words.
So it is written to content/playbook-drafts.json and applied on top of the
extracted data at build time, exactly like the CORRECTIONS mechanism in
design/extract-playbook-data.py. Three consequences worth keeping:

  - content/prose/_raw/playbook.html stays a byte-faithful mirror of live,
    so the drift check against the live page keeps working.
  - Every clip built from a drafted field is marked `drafted: true`, so
    nothing can ship believing a draft is the book.
  - Rejecting a draft is deleting one object, not unpicking an edit.

Approval is per entry, via the `approved` key. Nothing is approved by
default. DRAFTS-REVIEW.md is generated for reading through.

What is checked
---------------
Hooks: length against the budget, and a refusal list for withheld-hook
phrasing. The project's standing rule is that a hook names what the viewer
already lived through and never teases a payoff -- these books argue against
engineered attention, so a manipulative hook would discredit the book it came
from. That is worth a machine check, not just an instruction in a prompt.

Codex fields: near-duplicate detection across all drafted what_it_is_not
values. The whole point of that field is to be specific to one tactic; a
draft that could be pasted onto another entry has failed, and generating 266
variations of one sentence is the obvious failure mode.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, OrderedDict

ROOT = os.path.join(os.path.dirname(__file__), "..")
DRAFTDIR = os.path.join(ROOT, "content", "drafting")
OUT = os.path.join(ROOT, "content", "playbook-drafts.json")
REVIEW = os.path.join(ROOT, "DRAFTS-REVIEW.md")

HOOK_BUDGET = 80

# Withheld-hook phrasing. A hook must name the thing, not promise it.
TEASE = re.compile(
    r"\bwait for it\b|\byou won'?t believe\b|\bhere'?s why\b|\bpart \d\b|"
    r"\bkeep watching\b|\bstay tuned\b|\bread on\b|\bfind out\b|"
    r"\bthe reason will\b|\bnumber \d+ will\b|\bwhat happens next\b|"
    r"\bcomments? below\b|\blink in bio\b|\bthis one trick\b", re.I)

# Asserting diagnosis or character rather than describing a pattern.
ASSERTS = re.compile(
    r"\bis a narcissist\b|\bis abusive\b|\bthey'?re a sociopath\b|"
    r"\bis gaslighting you\b|\bhas npd\b|\bis a psychopath\b", re.I)


def norm(text):
    return re.sub(r"[^a-z0-9 ]", "", (text or "").lower()).strip()


def shingles(text, n=5):
    words = norm(text).split()
    return {" ".join(words[i:i + n]) for i in range(max(0, len(words) - n + 1))}


def near_duplicates(rows, key, threshold=0.6):
    """Pairs whose 5-word shingle overlap exceeds `threshold`."""
    sig = [(r["name"], shingles(r.get(key) or "")) for r in rows
           if (r.get(key) or "").strip()]
    hits = []
    for i in range(len(sig)):
        for j in range(i + 1, len(sig)):
            a, b = sig[i][1], sig[j][1]
            if not a or not b:
                continue
            overlap = len(a & b) / min(len(a), len(b))
            if overlap >= threshold:
                hits.append((sig[i][0], sig[j][0], round(overlap, 2)))
    return hits


def load(name):
    path = os.path.join(DRAFTDIR, name)
    if not os.path.exists(path):
        return None
    return json.load(open(path, encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    entries = {e["name"]: e for e in json.load(
        open(os.path.join(ROOT, "content", "playbook-data.json"),
             encoding="utf-8"))["codex_completed"]}

    problems = []

    # ---- hooks -----------------------------------------------------------
    hooks = load("hooks-output.json") or []
    seen_names = set()
    for row in hooks:
        name, hook = row.get("name"), (row.get("hook") or "").strip()
        if name not in entries:
            problems.append(("hook names an unknown tactic", name))
            continue
        if name in seen_names:
            problems.append(("duplicate hook entry", name))
        seen_names.add(name)
        if not hook:
            problems.append(("hook is empty", name))
            continue
        if len(hook) > HOOK_BUDGET:
            problems.append(("hook over budget (%d chars)" % len(hook), name))
        if TEASE.search(hook):
            problems.append(("hook withholds rather than names", "%s: %r"
                             % (name, hook)))
        if ASSERTS.search(hook):
            problems.append(("hook asserts diagnosis or character", "%s: %r"
                             % (name, hook)))

    dupe_hooks = [(a, b, o) for a, b, o in near_duplicates(
        [{"name": r["name"], "t": r.get("hook")} for r in hooks], "t", 0.8)]
    for a, b, o in dupe_hooks:
        problems.append(("hooks near-identical (%.0f%%)" % (o * 100),
                         "%s / %s" % (a, b)))

    # ---- codex fields ----------------------------------------------------
    codex = []
    for fname in sorted(os.listdir(DRAFTDIR)) if os.path.isdir(DRAFTDIR) else []:
        if fname.startswith("codex-output") and fname.endswith(".json"):
            codex.extend(load(fname) or [])

    for row in codex:
        name = row.get("name")
        if name not in entries:
            problems.append(("codex draft names an unknown tactic", str(name)))
            continue
        for field in ("why_this_matters", "what_it_is_not"):
            val = row.get(field)
            if val is None:
                continue
            if not str(val).strip():
                problems.append(("%s is empty" % field, name))
            elif ASSERTS.search(str(val)):
                problems.append(("%s asserts diagnosis or character" % field,
                                 name))

    dupes = near_duplicates(codex, "what_it_is_not", 0.6)
    for a, b, o in dupes:
        problems.append(("what_it_is_not near-duplicate (%.0f%%)" % (o * 100),
                         "%s / %s" % (a, b)))

    # ---- report ----------------------------------------------------------
    print("drafts found: %d hooks, %d codex entries" % (len(hooks), len(codex)))
    print()
    if problems:
        grouped = {}
        for kind, detail in problems:
            grouped.setdefault(kind, []).append(detail)
        print("PROBLEMS (%d)" % len(problems))
        for kind in sorted(grouped):
            print("  x %s" % kind)
            for detail in grouped[kind][:6]:
                print("      %s" % detail)
            if len(grouped[kind]) > 6:
                print("      ... and %d more" % (len(grouped[kind]) - 6))
        print()
    else:
        print("no problems found")
        print()

    if hooks:
        by_source = Counter(r.get("source") for r in hooks)
        print("hook provenance: %s" % ", ".join(
            "%s %d" % (k, v) for k, v in by_source.most_common()))
    if codex:
        print("codex confidence: %s" % ", ".join(
            "%s %d" % (k, v) for k, v in
            Counter(r.get("confidence") for r in codex).most_common()))

    if not args.apply:
        print("\ndry run -- pass --apply to stage the overlay")
        return 1 if problems else 0

    payload = OrderedDict([
        ("note", "DRAFTED CONTENT AWAITING APPROVAL. Not the author's text. "
                 "Applied over the extracted data at build time; nothing here "
                 "is in the book until it is written into the book. Approve by "
                 "setting approved: true on an entry."),
        ("generated", "2026-08-25"),
        ("hook_budget_chars", HOOK_BUDGET),
        ("hooks", [OrderedDict([("name", r["name"]), ("hook", r["hook"]),
                                ("source", r.get("source")),
                                ("from_field", r.get("from_field")),
                                ("note", r.get("note", "")),
                                ("approved", False)]) for r in hooks]),
        ("codex_fields", [OrderedDict([
            ("name", r["name"]),
            ("why_this_matters", r.get("why_this_matters")),
            ("what_it_is_not", r.get("what_it_is_not")),
            ("confidence", r.get("confidence")),
            ("note", r.get("note", "")),
            ("approved", False)]) for r in codex]),
    ])
    json.dump(payload, open(OUT, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    open(OUT, "a", encoding="utf-8").write("\n")
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
