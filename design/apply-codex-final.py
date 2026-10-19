#!/usr/bin/env python3
"""Write the finished codex entries into the Pattern Decoder page.

Run from the repo root:  python3 design/apply-codex-final.py [--apply] [--allow-partial]
Dry-run (default) checks and reports, writes nothing.

What it does
------------
Reads every accepted batch in content/codex-final/ (exemplars.json and
batch-NN.json), and rewrites the two data arrays inside
content/prose/_raw/playbook.html:

  CODEX_COMPLETED  each entry takes its new prose fields. safety_sensitive is
                   added as an explicit true/false (the page used to infer it
                   by searching safety_note for a stock phrase, which cannot
                   survive tactic-specific safety notes). codex_maturity
                   becomes "mature". The review flags that meant "this text is
                   still scaffolding" are removed; the flags that describe the
                   topic (culturally_sensitive, manipulation_playbook_risk...)
                   stay. The old response_options._note is dropped.
  COMPENDIUM       what/sounds/nots/why follow the codex, and the stub flag is
                   cleared, so lists and the data export agree with the entry.

Refuses to run unless all 349 tactics are present and the validator and the
boilerplate detector both pass on the result, unless --allow-partial (for
rehearsals only; never deploy a partial apply).

After --apply, regenerate the JSON export:
    python3 design/extract-playbook-data.py --apply
"""
import argparse
import glob
import json
import os
import subprocess
import sys
from collections import OrderedDict

ROOT = os.path.join(os.path.dirname(__file__), "..")
FINAL = os.path.join(ROOT, "content", "codex-final")
HTML = os.path.join(ROOT, "content", "prose", "_raw", "playbook.html")

WRITTEN = [
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
RESOLVED_FLAGS = {
    "examples_need_review", "definition_needs_review",
    "stub_expanded_needs_review", "societal_scale_needs_review",
    "aftermath_self_reflection_needs_review",
}


def read_array(html, name):
    marker = f"const {name} = "
    i = html.index(marker) + len(marker)
    value, end = json.JSONDecoder().raw_decode(html[i:])
    return value, i, i + end


def dump(v):
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--allow-partial", action="store_true")
    a = ap.parse_args()

    html = open(HTML, encoding="utf-8").read()
    codex, c0, c1 = read_array(html, "CODEX_COMPLETED")
    comp, p0, p1 = read_array(html, "COMPENDIUM")

    final = {}
    for p in sorted(glob.glob(os.path.join(FINAL, "*.json"))):
        b = os.path.basename(p)
        if not (b == "exemplars.json" or b.startswith(("batch-", "merged-"))):
            continue
        final.update(json.load(open(p, encoding="utf-8")))
    missing = [e["name"] for e in codex if e["name"] not in final]
    unknown = [n for n in final if n not in {e["name"] for e in codex}]
    print(f"finished entries: {len(final)} of {len(codex)}; missing {len(missing)}; unknown {len(unknown)}")
    if unknown:
        sys.exit(f"unknown tactic names: {unknown[:5]}")
    if missing and not a.allow_partial:
        sys.exit(f"{len(missing)} tactics still unwritten, e.g. {missing[:5]}. Use --allow-partial only to rehearse.")

    new_codex = []
    for e in codex:
        f = final.get(e["name"])
        if not f:
            new_codex.append(e)
            continue
        out = OrderedDict()
        for k, v in e.items():
            if k in WRITTEN:
                out[k] = f[k]
                if k == "safety_note":
                    out["safety_sensitive"] = f["safety_sensitive"]
            elif k == "codex_maturity":
                out[k] = "mature"
            elif k == "human_review_flags":
                flags = [x for x in v if x not in RESOLVED_FLAGS and x != "safety_sensitive"]
                if f["safety_sensitive"]:
                    flags.append("safety_sensitive")
                out[k] = flags
            else:
                out[k] = v
        new_codex.append(out)

    by = {e["name"]: e for e in new_codex}
    new_comp = []
    for c in comp:
        f = final.get(c["name"])
        if not f:
            new_comp.append(c)
            continue
        out = OrderedDict()
        for k, v in c.items():
            if k == "stub":
                continue
            out[k] = v
        out["what"] = f["short_definition"]
        out["sounds"] = f["what_it_sounds_like"]
        out["nots"] = f["what_it_is_not"]
        out["why"] = f["why_this_matters"]
        new_comp.append(out)

    assert p1 <= c0, "COMPENDIUM must precede CODEX_COMPLETED in the page"
    out_html = html[:p0] + dump(new_comp) + html[p1:c0] + dump(new_codex) + html[c1:]
    print("page size:", len(html), "->", len(out_html))
    if a.apply:
        open(HTML, "w", encoding="utf-8").write(out_html)
        print("wrote", HTML)
        print("next: python3 design/extract-playbook-data.py --apply")
    else:
        print("dry run -- pass --apply to write")


if __name__ == "__main__":
    main()
