#!/usr/bin/env python3
"""Split the Pattern Decoder codex into writer packets, merge-aware.

Run from the repo root:  python3 design/build-codex-packets.py [--apply]
Dry-run (default) prints the plan. --apply writes content/codex-final/packets/
and rewrites content/codex-final/manifest.json for what is still to write.

The 349 original tactics became 310 when the author merged 32 groups of
near-identical tactics (content/codex-final/tactic-merges.json). So:

  - a merged-away name never gets an entry of its own; it is an alias;
  - a canonical name in a merge group gets ONE entry covering every member,
    written in its own batches ("merged-NN"), from the members' definitions,
    quotes, reviewed drafts, and any entry already written for a member
    (kept in content/codex-final/superseded/);
  - related-tactic names are mapped through the aliases so no entry points at
    a tactic that no longer has a page.

Entries already written (an accepted batch, merged-NN or exemplars.json) are
left out, so re-running after some batches land plans only what remains.
Pending packets are replaced; packets of accepted batches are kept.
"""
import argparse
import glob
import importlib.util
import json
import os
import re
from collections import OrderedDict, defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")
FINAL = os.path.join(ROOT, "content", "codex-final")
PACKETS = os.path.join(FINAL, "packets")
SUPERSEDED = os.path.join(FINAL, "superseded")
DATA = os.path.join(ROOT, "content", "playbook-data.json")
DRAFTS = os.path.join(ROOT, "content", "playbook-drafts.json")


def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(__file__), fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


bp = _load("codex_boilerplate", "codex-boilerplate.py")
val = _load("validate_codex_final", "validate-codex-final.py")

NORMAL_CHUNK = 8
RISK_CHUNK = 7
MERGED_CHUNK = 4
TIER_RANK = {"Detected": 0, "Pattern-only": 1, "Watch-only": 2, "Reference-only": 3}


def entry_files():
    return val.entry_files()


def written_names():
    done = set()
    for p in entry_files():
        done |= set(json.load(open(p, encoding="utf-8")))
    return done


def chunk(names, size):
    if not names:
        return []
    n = -(-len(names) // size)
    base, extra = divmod(len(names), n)
    out, i = [], 0
    for k in range(n):
        step = base + (1 if k < extra else 0)
        out.append(names[i:i + step])
        i += step
    return out


def superseded_text():
    out = {}
    for p in glob.glob(os.path.join(SUPERSEDED, "*.json")):
        out.update(json.load(open(p, encoding="utf-8")))
    return out


def last_batch_number(prefix):
    nums = [int(re.search(r"(\d+)", os.path.basename(p)).group(1))
            for p in glob.glob(os.path.join(FINAL, prefix + "-*.json"))]
    return max(nums) if nums else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    d = json.load(open(DATA, encoding="utf-8"))
    X = OrderedDict((e["name"], e) for e in d["codex_completed"])
    drafts = {x["name"]: x for x in json.load(open(DRAFTS, encoding="utf-8"))["codex_fields"]}
    groups = json.load(open(os.path.join(FINAL, "tactic-merges.json")))["groups"]
    canon_of = {}
    members_of = {}
    for g in groups:
        members_of[g["canonical"]] = [g["canonical"]] + g["merged"]
        for n in g["merged"]:
            canon_of[n] = g["canonical"]
    kinds = json.load(open(os.path.join(FINAL, "tactic-kinds.json")))["entries"]
    old_text = superseded_text()
    report, _ = bp.analyze(list(X.values()))
    done = written_names()

    def canon(n):
        return canon_of.get(n, n)

    def risk(n):
        return "manipulation_playbook_risk" in X[n]["human_review_flags"]

    def specific(n):
        e, shared = X[n], report.get(n, {})
        ex = {}
        for f in bp.PROSE_FIELDS:
            v = e.get(f)
            bad = {s["text"] for s in shared.get(f, [])}
            if isinstance(v, list):
                keep = [s for s in v if s not in bad]
                if keep:
                    ex[f] = keep
            elif isinstance(v, str) and v not in bad and f != "core_meaning":
                ex[f] = v
        ex.pop("response_options", None)
        return ex

    def related_for(names):
        own = set(names)
        seen, out = set(), []
        for n in names:
            for r in X[n].get("related_tactics", []):
                c = canon(r)
                if c in own or c in seen or c not in X:
                    continue
                seen.add(c)
                rr = X[c]
                out.append({"name": c, "definition": rr["short_definition"]}
                           if not bp.is_truncated(rr["short_definition"]) else {"name": c})
        return out

    def annotate(entry, names):
        if any(n in val.REQUIRE_SAFETY for n in names):
            entry["reviewer_requires_safety_sensitive"] = (
                "TRUE. The 2026-08-27 clinical review named this entry as one most likely to be read by "
                "someone in current danger. Set safety_sensitive true and write the note and script accordingly.")
        if any(n in val.KNOWN_BROKEN for n in names):
            entry["source_definition_is_cut_off"] = True
            entry["known_truncation_note"] = ("A source short_definition for this entry stops mid-sentence. "
                                              "Write a complete one; do not reuse the old text.")
        two = [n for n in names if kinds.get(n, {}).get("kind") == "names two things"]
        if two:
            entry["covers_two_things"] = ("A title joins two things (" + "; ".join(two) + "). Cover BOTH, and say "
                                          "plainly whether they are two names for one behavior or two related behaviors.")
        entry["old_safety_signals"] = {
            "old_page_badge": any("No elevated safety concern" not in X[n]["safety_note"] for n in names),
            "old_review_flag_safety_sensitive": any("safety_sensitive" in X[n]["human_review_flags"] for n in names),
            "other_flags": sorted({f for n in names for f in X[n]["human_review_flags"]
                                   if f in ("forensic_or_evidence_risk", "workplace_or_legal_ambiguity",
                                            "clinical_adjacent_wording", "aftermath_self_reflection_needs_review",
                                            "high_false_positive_risk")}),
            "note": "Old signals were set by a coarse rule. Decide safety_sensitive yourself from the spec; hints only."}

    # what still needs writing
    todo_single, todo_merged = [], []
    for n in X:
        if n in canon_of:
            continue
        if n in done:
            continue
        (todo_merged if n in members_of else todo_single).append(n)

    by_cat = defaultdict(lambda: {"risk": [], "normal": []})
    for n in todo_single:
        by_cat[X[n]["category"]]["risk" if risk(n) else "normal"].append(n)
    plan = []
    for cat in sorted(by_cat):
        for names in chunk(by_cat[cat]["normal"], NORMAL_CHUNK):
            plan.append(("normal", cat, names))
    for cat in sorted(by_cat):
        for names in chunk(by_cat[cat]["risk"], RISK_CHUNK):
            plan.append(("risk", cat, names))
    # Merged entries are heavier (several members each), so they are pooled across
    # categories into even batches rather than one tiny batch per category.
    pooled = sorted(todo_merged, key=lambda n: (X[n]["category"], n))
    mplan = [("merged", "mixed categories", names) for names in chunk(pooled, MERGED_CHUNK)]

    nstart = last_batch_number("batch") + 1
    mstart = last_batch_number("merged") + 1
    manifest, written_packets = [], []
    for i, (kind, cat, names) in enumerate(plan):
        manifest.append((f"batch-{nstart + i:02d}", kind, cat, names))
    for i, (kind, cat, names) in enumerate(mplan):
        manifest.append((f"merged-{mstart + i:02d}", kind, cat, names))

    if a.apply:
        os.makedirs(PACKETS, exist_ok=True)
        keep_ids = {os.path.splitext(os.path.basename(p))[0] for p in entry_files()}
        for p in glob.glob(os.path.join(PACKETS, "*.json")):
            if os.path.splitext(os.path.basename(p))[0] not in keep_ids:
                os.remove(p)

    for bid, kind, cat, names in manifest:
        entries = []
        for n in names:
            group = members_of.get(n, [n])
            e = X[n]
            tier = min((X[m]["tier"] for m in group), key=lambda t: TIER_RANK[t])
            ent = OrderedDict([
                ("name", n), ("category", e["category"]), ("tier", tier),
                ("branch", e["branch"] if len(group) == 1 else
                 min((X[m] for m in group), key=lambda x: TIER_RANK[x["tier"]])["branch"]),
                ("risk_flagged", any(risk(m) for m in group)),
                ("source_definition_is_cut_off",
                 any(bp.is_truncated(X[m]["short_definition"]) or bp.is_truncated(X[m]["core_meaning"])
                     for m in group)),
            ])
            if len(group) == 1:
                dr = drafts.get(n, {})
                ent["approved_draft"] = {k: dr.get(k) for k in ("why_this_matters", "what_it_is_not", "note") if dr.get(k)}
                ent["existing_specific_text"] = specific(n)
            else:
                ent["MERGED_ENTRY"] = (
                    "The author merged these tactics into ONE entry. Write a single entry under the name '" + n +
                    "' that fully covers every member below. In expanded_definition say the others are the same "
                    "tactic under different names, and name them. Draw what_it_sounds_like, what_it_is_not and the "
                    "other lists from ALL members (choose the best and most distinct items; do not just concatenate). "
                    "Each member's previously written entry, if there is one, is the best starting text.")
                ent["merged_names_to_cover"] = group
                ent["members"] = []
                for m in group:
                    dr = drafts.get(m, {})
                    mem = OrderedDict([
                        ("name", m), ("tier", X[m]["tier"]),
                        ("source_definition", X[m]["short_definition"]),
                        ("approved_draft", {k: dr.get(k) for k in ("why_this_matters", "what_it_is_not", "note") if dr.get(k)}),
                        ("existing_specific_text", specific(m))])
                    if m in old_text:
                        mem["previously_written_entry"] = old_text[m]
                    ent["members"].append(mem)
            ent["related_tactics"] = related_for(group)
            annotate(ent, group)
            entries.append(ent)
        if a.apply:
            with open(os.path.join(PACKETS, bid + ".json"), "w", encoding="utf-8") as fh:
                json.dump({"batch": bid, "kind": kind, "category": cat, "entries": entries},
                          fh, indent=1, ensure_ascii=False)

    total = len(X) - len(canon_of)
    print(f"{len(X)} original tactics - {len(canon_of)} merged away = {total} entries in the book")
    print(f"{len(done)} written and kept; {len(todo_single)} single + {len(todo_merged)} merged entries still to write "
          f"in {len(manifest)} batches ({sum(1 for m in manifest if m[1]=='risk')} risk, "
          f"{sum(1 for m in manifest if m[1]=='merged')} merged)")
    assert len(done) + len(todo_single) + len(todo_merged) == total, "plan does not add up to the book"
    for bid, kind, cat, names in manifest:
        print(f"  {bid}  {kind:6s} {cat[:34]:34s} {len(names)}")
    if a.apply:
        with open(os.path.join(FINAL, "manifest.json"), "w", encoding="utf-8") as fh:
            json.dump([{"id": b, "kind": k, "category": c, "names": n, "status": "pending"}
                       for b, k, c, n in manifest], fh, indent=1, ensure_ascii=False)
        print("wrote packets and manifest.json")
    else:
        print("dry run -- pass --apply to write packets")


if __name__ == "__main__":
    main()
