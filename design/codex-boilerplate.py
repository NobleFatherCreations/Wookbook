#!/usr/bin/env python3
"""Measure boilerplate in the Pattern Decoder codex.

Run from the repo root:
    python3 design/codex-boilerplate.py [--data PATH] [--json OUT] [--quiet]

"Boilerplate" here is measurable, not a feeling: a sentence (or list item) is
shared text if, once the entry's own name, its category and the names of its
related tactics are replaced by placeholders, the same sentence appears on
SHARED_MIN or more different entries. Name-swapped templates ("X-type behavior
in the Y category tends to...") are caught by that substitution.

A truncated definition (one that stops on "to", "the", "make"...) is reported
separately, because it is a defect rather than boilerplate.

Exit status is 0 only when no prose field of any entry contains shared text and
no definition is truncated. That is the bar for "the codex has no boilerplate".
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "content", "playbook-data.json")

SHARED_MIN = 3  # same normalized sentence on this many entries or more

# Fields that hold prose written about one tactic. Fields that describe what
# the tool can do (detectability_note, detection_notes) and structural fields
# are not checked here: they are statements about the tool, not the tactic.
PROSE_FIELDS = [
    "short_definition", "core_meaning", "expanded_definition",
    "plain_language_summary", "why_this_matters", "what_it_is",
    "what_it_sounds_like", "what_it_is_not", "this_may_be_it_when",
    "this_may_not_be_it_when", "innocent_or_ordinary_possibilities",
    "common_false_positives", "discernment_questions", "less_concerning_if",
    "more_concerning_if", "pattern_over_time_signs", "repair_check",
    "boundary_respect_check", "psychological_mechanism",
    "possible_impact_on_receiver", "response_options", "boundary_script",
    "safety_note", "misuse_warning", "how_to_distinguish_from_related",
]

TRUNC_TAIL = {
    "to", "the", "a", "an", "of", "and", "or", "in", "for", "with", "that",
    "make", "by", "from", "on", "as", "at", "into", "their", "its", "any",
    "is", "are", "be", "not", "so", "than", "after", "before", "about",
}


def sentences(value):
    """Yield the sentences / list items of a field value as plain strings."""
    if value is None:
        return
    if isinstance(value, dict):
        for k, v in value.items():
            if k.startswith("_"):
                continue
            yield from sentences(v)
        return
    if isinstance(value, list):
        for v in value:
            yield from sentences(v)
        return
    text = str(value).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"“(])", text)
    for p in parts:
        p = p.strip()
        if p:
            yield p


def make_normalizer(entry):
    names = [entry["name"]] + list(entry.get("related_tactics") or [])
    names = sorted({n for n in names if n}, key=len, reverse=True)
    cat = entry.get("category") or ""

    def norm(s):
        t = s
        for n in names:
            t = re.sub(re.escape(n), "<T>", t, flags=re.I)
        if cat:
            t = re.sub(re.escape(cat), "<C>", t, flags=re.I)
        t = t.lower()
        t = re.sub(r"[^a-z0-9<>' ]+", " ", t)
        return re.sub(r"\s+", " ", t).strip()

    return norm


def is_truncated(text):
    t = (text or "").strip()
    if len(t.split()) < 4:
        return True
    last = re.sub(r"[^A-Za-z']+$", "", t.rstrip(".!?\"”)")).split()
    return bool(last) and last[-1].lower() in TRUNC_TAIL


def analyze(entries):
    freq = Counter()
    per = {}
    for e in entries:
        norm = make_normalizer(e)
        seen = set()
        rows = defaultdict(list)
        for f in PROSE_FIELDS:
            for s in sentences(e.get(f)):
                n = norm(s)
                if len(n.split()) < 4:
                    continue
                rows[f].append((s, n))
                seen.add(n)
        per[e["name"]] = rows
        freq.update(seen)
    report = {}
    for name, rows in per.items():
        bad = defaultdict(list)
        for f, items in rows.items():
            for s, n in items:
                if freq[n] >= SHARED_MIN:
                    bad[f].append({"text": s, "shared_with": freq[n] - 1})
        report[name] = dict(bad)
    return report, freq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DATA)
    ap.add_argument("--json")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    d = json.load(open(a.data, encoding="utf-8"))
    entries = d["codex_completed"] if "codex_completed" in d else d
    report, _ = analyze(entries)

    trunc = [e["name"] for e in entries
             if is_truncated(e.get("short_definition"))
             or is_truncated(e.get("core_meaning"))]
    entries_bad = {n: r for n, r in report.items() if r}
    field_counts = Counter(f for r in entries_bad.values() for f in r)
    total_items = sum(len(v) for r in entries_bad.values() for v in r.values())

    if not a.quiet:
        print(f"entries: {len(entries)}")
        print(f"entries containing shared text: {len(entries_bad)}")
        print(f"shared sentences/items in total: {total_items}")
        print(f"truncated definitions: {len(trunc)}")
        print("fields with shared text (entries affected):")
        for f, c in field_counts.most_common():
            print(f"  {f:36s} {c}")
        clean = [e["name"] for e in entries if not report[e["name"]]]
        print(f"entries with NO shared text: {len(clean)}")
    if a.json:
        json.dump({"truncated": trunc, "shared": report}, open(a.json, "w"),
                  indent=1, ensure_ascii=False)
    ok = not entries_bad and not trunc
    print("RESULT:", "clean" if ok else "boilerplate remains")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
