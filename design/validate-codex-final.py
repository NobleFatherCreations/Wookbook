#!/usr/bin/env python3
"""Validate rewritten Pattern Decoder codex entries before they are accepted.

Run from the repo root:
    python3 design/validate-codex-final.py content/codex-final/batch-01.json [more.json ...]
    python3 design/validate-codex-final.py --all        # every accepted batch together

A batch is a JSON object {"<tactic name>": {field: value, ...}, ...}. Entries
are checked on their own AND against every other accepted batch, so shared
sentences are caught across batches, not only inside one. Exit status 0 means
the batch may be accepted.

What is enforced, and why each rule exists
-------------------------------------------
shape        every field present, right type, right length. A short field is
             usually a placeholder; a long one is usually a rambling one.
no templates a sentence that appears on three or more entries (after the
             tactic's own name, category and related names are masked) is
             boilerplate by definition. See design/codex-boilerplate.py.
no scaffolding  stock phrases from the old scaffolding, fill-in-the-blank
             placeholders ("[specific thing]", "when X happened") and tool
             talk ("this tool", "pasted text") do not belong in a tactic's
             own entry.
no verdicts  no diagnoses or character labels. On interpersonal entries, no
             intent claims either unless the sentence rules intent out.
no how-to    on the entries flagged manipulation_playbook_risk, no
             instructional drift: the entry stays on recognizing it, what it
             costs, how to check it, and how to protect yourself.
"""
import argparse
import glob
import importlib.util
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.join(os.path.dirname(__file__), "..")
FINAL = os.path.join(ROOT, "content", "codex-final")
DATA = os.path.join(ROOT, "content", "playbook-data.json")

_spec = importlib.util.spec_from_file_location(
    "codex_boilerplate", os.path.join(os.path.dirname(__file__), "codex-boilerplate.py"))
bp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bp)

STR_FIELDS = {  # field: (min words, max words)
    "short_definition": (10, 30),
    "core_meaning": (10, 30),
    "expanded_definition": (40, 110),
    "plain_language_summary": (12, 45),
    "why_this_matters": (20, 60),
    "repair_check": (20, 60),
    "boundary_respect_check": (20, 60),
    "psychological_mechanism": (30, 85),
    "possible_impact_on_receiver": (30, 90),
    "boundary_script": (15, 80),
    "safety_note": (25, 95),
    "how_to_distinguish_from_related": (30, 105),
}
LIST_FIELDS = {  # field: (min items, max items, min words/item, max words/item)
    "what_it_is": (4, 6, 6, 45),
    "what_it_sounds_like": (5, 8, 2, 40),
    "what_it_is_not": (5, 6, 6, 45),
    "this_may_be_it_when": (5, 5, 6, 40),
    "this_may_not_be_it_when": (5, 5, 6, 40),
    "innocent_or_ordinary_possibilities": (3, 4, 6, 40),
    "common_false_positives": (3, 4, 6, 45),
    "discernment_questions": (4, 6, 6, 40),
    "less_concerning_if": (3, 3, 6, 40),
    "more_concerning_if": (3, 3, 6, 40),
    "pattern_over_time_signs": (4, 4, 6, 40),
    "misuse_warning": (1, 2, 8, 45),
}
RESPONSE_KEYS = ["soft_clarification", "firm_boundary", "disengagement",
                 "support_seeking", "workplace_or_professional"]
ALLOWED = set(STR_FIELDS) | set(LIST_FIELDS) | {
    "response_options", "safety_sensitive", "plain_language_summary"}

SCAFFOLD = [
    r"in this project'?s taxonomy", r"\bfalls under the\b", r"\bthis tool\b",
    r"\bpasted text\b", r"as a communication pattern", r"not a fixed trait",
    r"one example is a signal to examine", r"\bphrase[- ]matching\b",
    r"\binnocent reading\b", r"\bthe general guidance still applies\b",
    r"\[[^\]]*\]", r"\btbd\b", r"\bwhen x happened\b", r"\b(?:i felt|feel) y\b",
    r"\bin the same category\b", r"\bthe specific mechanism in\b",
    r"\blorem\b", r"\bplaceholder\b",
]
DIAGNOSIS = re.compile(
    r"\b(narcissists?|sociopaths?|psychopaths?|abusers?|toxic (?:person|people)|"
    r"is abusive|are abusive|borderline|bpd|npd)\b", re.I)
INTENT = re.compile(
    r"\b(on purpose|deliberately|intentionally|purposely|knows? exactly|means? to|"
    r"intends? to|wants? to control|trying to control|aims? (?:to|at))\b", re.I)
NEGATION = re.compile(
    r"\b(not|no|never|nothing|neither|without|whether|doesn'?t|does not|cannot|"
    r"can'?t|isn'?t|rarely|unless|claim|assume|proves?|prove)\b", re.I)
INSTRUCT = re.compile(
    r"\b(step[- ]by[- ]step|how to (?:create|build|run|set up|make|evade|avoid|get around|bypass)|"
    r"you (?:can|could|should|will need to) (?:create|build|set up|buy|generate|train|clone|"
    r"scrape|hide|evade|bypass|register|purchase)|to avoid detection|evade detection|"
    r"bypass(?:ing)? (?:the )?(?:filter|moderation|detection|verification)|tutorial|"
    r"recipe for|first,? (?:create|register|buy|set up))\b", re.I)
INTENT_ERROR_BRANCHES = {"detected", "pattern", "watch", "aftermath"}
END_OK = ('.', '?', '!', '"', '”', ')', "'")
# Words a finished sentence cannot end on. Deliberately short: "it", "that",
# "to", "is" and "for" all end real sentences ("than you used to.").
NEVER_LAST = {"the", "a", "an", "of", "and", "or", "but", "with", "by", "from",
              "as", "at", "into", "their", "its", "any", "than", "which", "make"}


def words(s):
    return len(re.findall(r"[A-Za-z0-9'’-]+", s))


def texts(entry):
    """Every (field, string) in an entry, lists and response options flattened."""
    for f in list(STR_FIELDS) + list(LIST_FIELDS):
        v = entry.get(f)
        if isinstance(v, str):
            yield f, v
        elif isinstance(v, list):
            for i in v:
                if isinstance(i, str):
                    yield f, i
    ro = entry.get("response_options")
    if isinstance(ro, dict):
        for k, v in ro.items():
            if isinstance(v, str):
                yield "response_options." + k, v


def load_base():
    d = json.load(open(DATA, encoding="utf-8"))
    return {e["name"]: e for e in d["codex_completed"]}


def load_batches(paths):
    out = {}
    for p in paths:
        for name, entry in json.load(open(p, encoding="utf-8")).items():
            out[name] = (entry, os.path.basename(p))
    return out


def check_shape(name, e, errs):
    extra = set(e) - ALLOWED
    if extra:
        errs.append(f"unknown fields: {sorted(extra)}")
    for f, (lo, hi) in STR_FIELDS.items():
        v = e.get(f)
        if not isinstance(v, str) or not v.strip():
            errs.append(f"{f}: missing or empty")
            continue
        n = words(v)
        if not lo <= n <= hi:
            errs.append(f"{f}: {n} words (want {lo}-{hi})")
    for f, (lo, hi, wlo, whi) in LIST_FIELDS.items():
        v = e.get(f)
        if not isinstance(v, list) or not all(isinstance(i, str) and i.strip() for i in v):
            errs.append(f"{f}: missing or not a list of strings")
            continue
        if not lo <= len(v) <= hi:
            errs.append(f"{f}: {len(v)} items (want {lo}-{hi})")
        for i in v:
            n = words(i)
            if not wlo <= n <= whi:
                errs.append(f"{f}: item of {n} words (want {wlo}-{whi}): {i[:60]!r}")
        if len({x.strip().lower() for x in v}) != len(v):
            errs.append(f"{f}: repeats an item")
    if isinstance(e.get("discernment_questions"), list):
        for q in e["discernment_questions"]:
            if not q.strip().endswith("?"):
                errs.append(f"discernment_questions: not a question: {q[:60]!r}")
    ro = e.get("response_options")
    if not isinstance(ro, dict) or sorted(ro) != sorted(RESPONSE_KEYS):
        errs.append(f"response_options: need exactly {RESPONSE_KEYS}")
    else:
        for k in RESPONSE_KEYS:
            n = words(ro[k]) if isinstance(ro[k], str) else 0
            if not 12 <= n <= 55:
                errs.append(f"response_options.{k}: {n} words (want 12-55)")
    if not isinstance(e.get("safety_sensitive"), bool):
        errs.append("safety_sensitive: must be true or false")
    if bp.is_truncated(e.get("short_definition")):
        errs.append("short_definition looks cut off or too short")
    if e.get("short_definition") and e.get("core_meaning") != e.get("short_definition"):
        errs.append("core_meaning must equal short_definition")


def check_text(name, e, base, risk, errs, warns):
    branch = base.get("branch")
    for f, s in texts(e):
        if f != "boundary_script" and not f.startswith("response_options") \
                and not s.rstrip().endswith(END_OK):
            errs.append(f"{f}: does not end like a finished sentence: {s[-40:]!r}")
        for pat in SCAFFOLD:
            if re.search(pat, s, re.I):
                errs.append(f"{f}: scaffolding/placeholder language ({pat}): {s[:70]!r}")
                break
        if DIAGNOSIS.search(s) and not DIAGNOSIS.search(name):
            errs.append(f"{f}: diagnosis or character label: {DIAGNOSIS.search(s).group(0)!r}")
        for sent in bp.sentences(s):
            if INTENT.search(sent) and not NEGATION.search(sent):
                msg = f"{f}: intent claim without ruling it out: {sent[:80]!r}"
                (errs if branch in INTENT_ERROR_BRANCHES else warns).append(msg)
            if risk and INSTRUCT.search(sent):
                errs.append(f"{f}: instructional drift on a risk entry: {sent[:80]!r}")
            last = re.sub(r"[^A-Za-z']+$", "", sent.rstrip(".!?\"”)'")).split()
            if last and last[-1].lower() in NEVER_LAST and f != "boundary_script":
                errs.append(f"{f}: sentence may be cut off: {sent[-50:]!r}")
    sd = e.get("short_definition", "")
    if sd and sd.strip().rstrip(".").lower() in (e.get("expanded_definition", "").lower()):
        warns.append("expanded_definition repeats short_definition word for word")


def corpus_freq(batches, base_all):
    freq = Counter()
    for name, (e, _) in batches.items():
        b = dict(base_all.get(name, {"name": name}))
        norm = bp.make_normalizer(b)
        seen = set()
        for f, s in texts(e):
            if f == "core_meaning":
                continue
            for sent in bp.sentences(s):
                n = norm(sent)
                if len(n.split()) >= 4:
                    seen.add(n)
        freq.update(seen)
    return freq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    check = a.files
    allfiles = sorted(glob.glob(os.path.join(FINAL, "*.json")))
    allfiles = [p for p in allfiles if os.path.basename(p) not in
                ("manifest.json", "reviews.json")]
    if a.all:
        check = allfiles
    if not check:
        ap.error("give batch files or --all")
    base_all = load_base()
    mine = load_batches(check)
    others = load_batches([p for p in allfiles
                           if os.path.abspath(p) not in {os.path.abspath(c) for c in check}])
    pool = dict(others)
    pool.update(mine)
    freq = corpus_freq(pool, base_all)

    bad = 0
    for name, (e, src) in mine.items():
        errs, warns = [], []
        base = base_all.get(name)
        if base is None:
            errs.append("not a known tactic name")
            base = {"name": name}
        risk = "manipulation_playbook_risk" in base.get("human_review_flags", [])
        check_shape(name, e, errs)
        check_text(name, e, base, risk, errs, warns)
        norm = bp.make_normalizer(base)
        for f, s in texts(e):
            if f == "core_meaning":
                continue
            for sent in bp.sentences(s):
                n = norm(sent)
                if len(n.split()) >= 4 and freq[n] >= bp.SHARED_MIN:
                    errs.append(f"{f}: shared with {freq[n]-1} other entries: {sent[:80]!r}")
        if errs:
            bad += 1
        if (errs or warns) and not a.quiet:
            print(f"== {name} [{src}]{'  (risk)' if risk else ''}")
            for m in errs:
                print("   ERROR", m)
            for m in warns:
                print("   warn ", m)
    print(f"checked {len(mine)} entries: {len(mine)-bad} pass, {bad} fail")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
