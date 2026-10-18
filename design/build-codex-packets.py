#!/usr/bin/env python3
"""Split the Pattern Decoder codex into writer packets.

Run from the repo root:  python3 design/build-codex-packets.py [--apply]
Dry-run (default) prints the plan. --apply writes content/codex-final/packets/
and content/codex-final/manifest.json.

Entries already written (an accepted batch file, or exemplars.json) are left
out, so re-running after some batches land plans only what remains.

Each packet entry carries what the writer needs and nothing that tempts them
to copy scaffolding:
  - identity: name, category, tier, branch, whether it is risk-flagged
  - the earlier approved draft for why_this_matters / what_it_is_not, if any
  - the entry's own existing text, with every shared (boilerplate) sentence
    already removed, so what is left is genuinely specific to this tactic
  - the one-line definitions of its related tactics, for the "how to tell
    apart" field
Risk-flagged entries (manipulation_playbook_risk) go in their own smaller
batches so the writer holds the stricter instructions in mind for all of them.
"""
import argparse
import glob
import importlib.util
import json
import os
from collections import OrderedDict, defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")
FINAL = os.path.join(ROOT, "content", "codex-final")
PACKETS = os.path.join(FINAL, "packets")
DATA = os.path.join(ROOT, "content", "playbook-data.json")
DRAFTS = os.path.join(ROOT, "content", "playbook-drafts.json")

_spec = importlib.util.spec_from_file_location(
    "codex_boilerplate", os.path.join(os.path.dirname(__file__), "codex-boilerplate.py"))
bp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bp)

NORMAL_CHUNK = 9
RISK_CHUNK = 7


def written_names():
    done = set()
    for p in glob.glob(os.path.join(FINAL, "*.json")):
        if os.path.basename(p) in ("manifest.json", "reviews.json"):
            continue
        done |= set(json.load(open(p, encoding="utf-8")))
    return done


def chunk(names, size):
    """Even-sized chunks no larger than `size` (avoids a 1-entry tail batch)."""
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    d = json.load(open(DATA, encoding="utf-8"))
    X = OrderedDict((e["name"], e) for e in d["codex_completed"])
    drafts = {x["name"]: x for x in json.load(open(DRAFTS, encoding="utf-8"))["codex_fields"]}
    report, _ = bp.analyze(list(X.values()))
    done = written_names()

    todo = [n for n in X if n not in done]
    by_cat = defaultdict(lambda: {"risk": [], "normal": []})
    for n in todo:
        risk = "manipulation_playbook_risk" in X[n]["human_review_flags"]
        by_cat[X[n]["category"]]["risk" if risk else "normal"].append(n)

    plan = []
    for cat in sorted(by_cat):
        for names in chunk(by_cat[cat]["normal"], NORMAL_CHUNK):
            plan.append(("normal", cat, names))
    for cat in sorted(by_cat):
        for names in chunk(by_cat[cat]["risk"], RISK_CHUNK):
            plan.append(("risk", cat, names))

    start = len(glob.glob(os.path.join(FINAL, "batch-*.json"))) + 1
    manifest = []
    for i, (kind, cat, names) in enumerate(plan):
        bid = f"batch-{start + i:02d}"
        entries = []
        for n in names:
            e = X[n]
            shared = report.get(n, {})
            existing = {}
            for f in bp.PROSE_FIELDS:
                v = e.get(f)
                bad = {s["text"] for s in shared.get(f, [])}
                if isinstance(v, list):
                    keep = [s for s in v if s not in bad]
                    if keep:
                        existing[f] = keep
                elif isinstance(v, str) and v not in bad and f not in (
                        "core_meaning",):
                    existing[f] = v
            existing.pop("response_options", None)
            dr = drafts.get(n, {})
            related = []
            for r in e.get("related_tactics", []):
                re_ = X.get(r)
                if re_ and not bp.is_truncated(re_["short_definition"]):
                    related.append({"name": r, "definition": re_["short_definition"]})
                else:
                    related.append({"name": r})
            entries.append(OrderedDict([
                ("name", n),
                ("category", e["category"]),
                ("tier", e["tier"]),
                ("branch", e["branch"]),
                ("risk_flagged", kind == "risk"),
                ("safety_flag_candidates", [f for f in e["human_review_flags"]
                                            if f in ("societal_scale_needs_review",)]),
                ("source_definition_is_cut_off", bp.is_truncated(e["short_definition"])
                 or bp.is_truncated(e["core_meaning"])),
                ("approved_draft", {k: dr.get(k) for k in
                                    ("why_this_matters", "what_it_is_not", "note")
                                    if dr.get(k)}),
                ("existing_specific_text", existing),
                ("related_tactics", related),
            ]))
        manifest.append({"id": bid, "kind": kind, "category": cat,
                         "names": names, "status": "pending"})
        if a.apply:
            os.makedirs(PACKETS, exist_ok=True)
            with open(os.path.join(PACKETS, bid + ".json"), "w", encoding="utf-8") as fh:
                json.dump({"batch": bid, "kind": kind, "category": cat, "entries": entries},
                          fh, indent=1, ensure_ascii=False)

    print(f"{len(done)} entries already written, {len(todo)} to write, "
          f"{len(manifest)} batches ({sum(m['kind']=='risk' for m in manifest)} risk)")
    for m in manifest:
        print(f"  {m['id']}  {m['kind']:6s} {m['category'][:34]:34s} {len(m['names'])}")
    if a.apply:
        with open(os.path.join(FINAL, "manifest.json"), "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=1, ensure_ascii=False)
        print("wrote", PACKETS, "and manifest.json")
    else:
        print("dry run -- pass --apply to write packets")


if __name__ == "__main__":
    main()
