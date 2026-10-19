#!/usr/bin/env python3
"""Write the finished, merged codex into the Pattern Decoder page.

Run from the repo root:  python3 design/apply-codex-final.py [--apply] [--allow-partial]
Dry-run (default) checks and reports, writes nothing.

What it does to content/prose/_raw/playbook.html
------------------------------------------------
Reads every accepted entry file in content/codex-final/ (exemplars.json,
batch-NN.json, merged-NN.json) and the merge decisions in tactic-merges.json.

  CODEX_COMPLETED  - the 39 merged-away tactics are removed. Each canonical
                     entry takes its new prose fields, an explicit
                     safety_sensitive true/false, the best tier of its group
                     (and that tier's detectability text), codex_maturity
                     "mature", and `absorbs` = the names folded into it.
                     Review flags that meant "still scaffolding" are cleared;
                     flags that describe the topic stay.
  COMPENDIUM       - same removals; what/sounds/nots/why follow the codex.
  RECIPES          - every chain is mapped through the aliases (a chain never
                     names a tactic that no longer has a page; a name that
                     would appear twice keeps its first place).
  NARROW_BY_FEELING- the hand-written feeling -> tactic lists, remapped.
  ALIASES          - new const: merged-away name -> canonical name, used by the
                     page so old links, saved stars and searches still work.
  counts           - the visible "349" in the title, buttons and captions
                     becomes the real number.

Refuses to run unless all expected entries are present (the book is 349 minus
merged-away) and the result is consistent: no chain, related link or feeling
list may name a missing tactic. --allow-partial is for rehearsals only; never
deploy a partial apply.

After --apply:  python3 design/extract-playbook-data.py --apply
"""
import argparse
import glob
import json
import os
import re
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
TIER_RANK = {"Detected": 0, "Pattern-only": 1, "Watch-only": 2, "Reference-only": 3}
TAG_OF = {"Detected": "detected", "Pattern-only": "pattern", "Watch-only": "watch", "Reference-only": "reference"}
COUNT_CONTEXT = re.compile(
    r"(?<![\w.])349(?=(?:[ -](?:named|tactics?|entries|entry|stars|row|instead))|\)?, decoded| by how often)")


def read_const(html, name):
    """Return (value, start, end) of the JSON literal after `const NAME = ` or `const NAME=`."""
    m = re.search(r"const " + name + r"\s*=\s*", html)
    i = m.end()
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
    comp, p0, p1 = read_const(html, "COMPENDIUM")
    recipes, r0, r1 = read_const(html, "RECIPES")
    codex, c0, c1 = read_const(html, "CODEX_COMPLETED")
    narrow, n0, n1 = read_const(html, "NARROW_BY_FEELING")
    assert p1 <= r0 and r1 <= c0, "expected COMPENDIUM, RECIPES, CODEX_COMPLETED in that order"
    assert n1 <= p0 or n0 >= c1 or (r1 <= n0 and n1 <= c0), "NARROW_BY_FEELING overlaps a data array"

    groups = json.load(open(os.path.join(FINAL, "tactic-merges.json")))["groups"]
    canon_of, members_of = {}, {}
    for g in groups:
        members_of[g["canonical"]] = [g["canonical"]] + g["merged"]
        for n in g["merged"]:
            canon_of[n] = g["canonical"]
    canon = lambda n: canon_of.get(n, n)

    final = {}
    for p in sorted(glob.glob(os.path.join(FINAL, "*.json"))):
        b = os.path.basename(p)
        if b == "exemplars.json" or b.startswith(("batch-", "merged-")):
            final.update(json.load(open(p, encoding="utf-8")))
    by_old = {e["name"]: e for e in codex}
    book = [e["name"] for e in codex if e["name"] not in canon_of]
    missing = [n for n in book if n not in final]
    unknown = [n for n in final if n not in set(book)]
    print(f"book: {len(book)} entries ({len(codex)} originals - {len(canon_of)} merged away); "
          f"finished {len(book) - len(missing)}; missing {len(missing)}; unknown {len(unknown)}")
    if unknown:
        sys.exit(f"finished entries that are not in the book: {unknown[:5]}")
    if missing and not a.allow_partial:
        sys.exit(f"{len(missing)} entries still unwritten, e.g. {missing[:5]}. --allow-partial only to rehearse.")

    def remap_related(names, self_name):
        seen, out = set(), []
        for r in names:
            c = canon(r)
            if c == self_name or c in seen:
                continue
            seen.add(c)
            out.append(c)
        return out

    def best_of(group, n):
        return min((by_old[m] for m in group), key=lambda x: (TIER_RANK[x["tier"]], x["name"] != n))

    new_codex = []
    for e in codex:
        n = e["name"]
        if n in canon_of:
            continue
        group = members_of.get(n, [n])
        best = best_of(group, n)
        f = final.get(n)
        out = OrderedDict()
        for k, v in e.items():
            if f and k in WRITTEN:
                out[k] = f[k]
                if k == "safety_note":
                    out["safety_sensitive"] = f["safety_sensitive"]
            elif k in ("tier", "tier_key", "branch", "detectability_note", "detection_notes"):
                out[k] = best[k]
            elif k == "absorbs":
                out[k] = [m for m in group if m != n]
            elif k == "codex_maturity":
                out[k] = "mature" if f else v
            elif k == "human_review_flags":
                flags = []
                for m in group:
                    for x in by_old[m]["human_review_flags"]:
                        if (not f or x not in RESOLVED_FLAGS) and x != "safety_sensitive" and x not in flags:
                            flags.append(x)
                if f and f["safety_sensitive"]:
                    flags.append("safety_sensitive")
                elif not f and "safety_sensitive" in e["human_review_flags"]:
                    flags.append("safety_sensitive")
                out[k] = flags
            elif k == "related_tactics":
                rel = []
                for m in group:
                    rel += by_old[m].get("related_tactics", [])
                out[k] = remap_related(rel, n)[:8]
            elif k in ("aftermath_state", "forensic_only"):
                out[k] = any(by_old[m][k] for m in group)
            else:
                out[k] = v
        new_codex.append(out)
    names = {e["name"] for e in new_codex}

    new_comp = []
    for c in comp:
        n = c["name"]
        if n in canon_of:
            continue
        group = members_of.get(n, [n])
        best = best_of(group, n)
        f = final.get(n)
        out = OrderedDict()
        for k, v in c.items():
            if k == "stub" and f:
                continue
            out[k] = TAG_OF[best["tier"]] if k == "tag" else v
        if f:
            out["what"] = f["short_definition"]
            out["sounds"] = f["what_it_sounds_like"]
            out["nots"] = f["what_it_is_not"]
            out["why"] = f["why_this_matters"]
        new_comp.append(out)

    changed_chains, new_recipes = [], []
    for r in recipes:
        chain, seen = [], set()
        for t in r["c"]:
            c = canon(t)
            if c not in seen:
                seen.add(c)
                chain.append(c)
        if chain != r["c"]:
            changed_chains.append((r["n"], len(r["c"]), len(chain)))
        if len(chain) < 2:
            sys.exit(f"sequence {r['n']!r} would shrink to {chain}; decide by hand")
        new_recipes.append(OrderedDict([("n", r["n"]), ("c", chain), ("d", r["d"])]))
    for nm in (t for r in new_recipes for t in r["c"]):
        assert nm in names, f"sequence names a missing tactic: {nm}"
    freq = {}
    for r in new_recipes:
        for t in r["c"]:
            freq[t] = freq.get(t, 0) + 1
    for c in new_comp:
        if "pats" in c:
            c["pats"] = freq.get(c["name"], 0)

    new_narrow = {}
    for k, lst in narrow.items():
        seen, out = set(), []
        for nm in lst:
            c = canon(nm)
            if c not in seen:
                seen.add(c)
                out.append(c)
        assert all(x in names for x in out), f"feeling list {k} names a missing tactic"
        new_narrow[k] = out
    for e in new_codex:
        assert all(r in names for r in e["related_tactics"]), f"{e['name']}: related names a missing tactic"

    aliases = OrderedDict((m, g["canonical"]) for g in groups for m in g["merged"])
    n_book = len(new_comp)

    pieces = sorted([(p0, p1, dump(new_comp)), (r0, r1, dump(new_recipes)),
                     (c0, c1, dump(new_codex)), (n0, n1, dump(new_narrow))])
    parts, last = [], 0
    for i, j, text in pieces:
        parts.append(html[last:i])
        parts.append(text)
        last = j
    parts.append(html[last:])
    out_html = "".join(parts)
    anchor = "const RECIPES = " + dump(new_recipes) + ";"
    assert out_html.count(anchor) == 1, "could not find the RECIPES statement to attach ALIASES to"
    out_html = out_html.replace(
        anchor,
        anchor + "\n/* merged-away tactic name -> the entry that now covers it */\nconst ALIASES = " + dump(aliases) + ";", 1)
    out_html, nsub = COUNT_CONTEXT.subn(str(n_book), out_html)
    print(f"visible counts rewritten 349 -> {n_book}: {nsub}")
    print(f"sequences changed by the merge: {len(changed_chains)}", changed_chains[:6])
    print("page size:", len(html), "->", len(out_html))
    if a.apply:
        open(HTML, "w", encoding="utf-8").write(out_html)
        print("wrote", HTML)
        print("next: python3 design/patch-decoder-v9-page.py --apply ; python3 design/extract-playbook-data.py --apply")
    else:
        print("dry run -- pass --apply to write")


if __name__ == "__main__":
    main()
