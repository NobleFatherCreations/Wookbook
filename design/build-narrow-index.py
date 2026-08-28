#!/usr/bin/env python3
"""
Freeze the deterministic index behind the Decoder's "Narrow it down"
multiple-choice walkthrough.

WHY THIS EXISTS
---------------
Measured on this corpus, free-text search resolved only ~6/15 natural
paraphrases to the right entry. Lexical matching over prose is inherently
lossy, so the walkthrough must not do any at runtime.

An earlier attempt derived new facet dimensions ("where did this happen",
"what has it done to you") by keyword-matching each entry's prose. It was
discarded because the output proved it worthless: the resulting tags matched
349/349 entries for `family`, 349/349 for `resources` and 349/349 for
`overtime`. A tag that matches everything narrows nothing, and worse, it
*looks* like it is working. That is exactly the silent-wrongness failure this
build is meant to eliminate, so the approach was dropped rather than tuned.

What ships instead is built ONLY from data a human actually authored:
  * FEELING_GROUPS / FEELINGS (6 contexts, 35 statements) -- already written,
    reviewed and shipping in the page today.
  * `category` -- the authored 24-way taxonomy, exact and mutually exclusive.
  * `safety_note` -- passed through from the clinically reviewed field,
    never re-inferred.

No new clinical claim is introduced here, and nothing is guessed at runtime.
The scoring that currently happens live in `feelingMatches()` is executed
once, HERE, and frozen to an explicit `feeling -> [entry names]` table. At
runtime the app does set union/intersection over frozen lists: no scoring, no
thresholds, no way to "miss".

THE INVARIANT THE UI RELIES ON
------------------------------
The walkthrough derives each question's options FROM THE SET STILL MATCHING,
and renders an option only when >= 1 entry sits behind it. That makes a
zero-result dead end impossible by construction rather than merely unlikely.
This script guarantees the inputs to that hold, asserting at the bottom that:
  * every one of the 35 feelings resolves to a non-empty entry list
  * every entry named in the index exists in the corpus
  * every one of the 6 groups has >= 2 feelings (a group with one option is
    not a choice)
  * every entry is reachable from at least one feeling, OR is reachable via
    the category axis -- nothing may be strandable
"""

import json
import re
import collections
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "content" / "prose" / "_raw" / "playbook.html"
DATA = ROOT / "content" / "playbook-data.json"
OUT = ROOT / "content" / "playbook-narrow-index.json"

# How many entries a single feeling may resolve to. The live implementation
# used 14. Kept identical so freezing changes nothing a reader would see.
PER_FEELING_CAP = 14


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def read_js_arrays():
    """Pull FEELINGS / FEELING_GROUPS out of the page by evaluating them.

    They are JS object literals containing apostrophes inside prose labels,
    so regex-to-JSON conversion mangles them; node parses them exactly.
    """
    script = r"""
const fs=require('fs');
const s=fs.readFileSync(process.argv[1],'utf8');
const grab=(n)=>{const i=s.indexOf('const '+n+'=[');const j=s.indexOf('\n];',i);
  return s.slice(i+('const '+n+'=').length, j+2);};
process.stdout.write(JSON.stringify({
  FEELINGS: eval(grab('FEELINGS')),
  FEELING_GROUPS: eval(grab('FEELING_GROUPS')),
}));
"""
    out = subprocess.run(["node", "-e", script, str(PAGE)],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def feeling_matches(f, compendium, codex_by):
    """Byte-for-byte port of the page's live `feelingMatches()`.

    Kept deliberately identical -- including the +0.5 nudge for `detected`
    entries and the top-14 cut -- so that freezing the result is a pure
    refactor. If this ever diverges from the page, the page is the spec.
    """
    scored = []
    for e in compendium:
        c = codex_by.get(e["name"], {})
        hay = norm(" ".join(str(x) for x in [
            e.get("name"), e.get("what"),
            c.get("plain_language_summary"), c.get("short_definition"),
            " ".join(c.get("what_it_sounds_like") or []),
            " ".join(c.get("what_it_is") or []),
        ] if x))
        score = 0.0
        if e.get("cat") in f["cats"]:
            score += 3
        for k in f["kw"]:
            if k in norm(e["name"]):
                score += 3
            elif k in hay:
                score += 1
        if e.get("tag") == "detected":
            score += 0.5
        if score > 0:
            scored.append((score, e["name"]))
    # JS `.sort((a,b)=>b.score-a.score)` is stable in modern engines, so ties
    # keep corpus order; Python's stable sort on the negated score matches.
    scored.sort(key=lambda t: -t[0])
    return [n for _, n in scored[:PER_FEELING_CAP]]


def main():
    js = read_js_arrays()
    feelings, groups = js["FEELINGS"], js["FEELING_GROUPS"]

    data = json.loads(DATA.read_text(encoding="utf-8"))
    compendium = data["compendium"]
    codex_by = {c["name"]: c for c in data["codex_completed"]}
    all_names = {e["name"] for e in compendium}

    # ---- freeze feeling -> entries -------------------------------------
    by_feeling = {}
    for f in feelings:
        by_feeling[f["key"]] = feeling_matches(f, compendium, codex_by)

    # ---- category axis (exact, authored) --------------------------------
    by_category = collections.defaultdict(list)
    for e in compendium:
        by_category[e["cat"]].append(e["name"])

    # ---- safety flag, passed through from the reviewed field -------------
    safety = sorted(
        n for n in all_names
        if (codex_by.get(n, {}).get("safety_note")
            and "No elevated safety concern"
            not in codex_by[n]["safety_note"])
    )

    # Only `byFeeling` is actually emitted for the page to embed. Groups,
    # feelings, categories and the safety flag are all already present in the
    # page and recomputable there EXACTLY (they are authored fields, not
    # scored), so shipping copies would just create two sources of truth that
    # can drift. byFeeling is the one thing that cannot be recomputed without
    # re-running the lossy scorer, which is the whole point of freezing it.
    index = {"byFeeling": by_feeling}

    # Built for verification below, not shipped.
    full = {
        "groups": [{"k": g["key"], "l": g["label"]} for g in groups],
        "feelings": [{"k": f["key"], "g": f["group"], "l": f["label"]}
                     for f in feelings],
        "byFeeling": by_feeling,
        "byCategory": {k: sorted(v) for k, v in sorted(by_category.items())},
        "safety": safety,
    }
    index_full = full

    # ================== invariants the runtime UI depends on ==============
    # 1. No feeling may resolve to nothing -- an option that leads nowhere is
    #    exactly the dead end this design exists to make impossible.
    empty = [k for k, v in by_feeling.items() if not v]
    assert not empty, f"feelings resolving to zero entries: {empty}"

    # 2. Every name in the index must exist in the corpus, or a click would
    #    route to a 'not found' view.
    for k, names in by_feeling.items():
        unknown = [n for n in names if n not in all_names]
        assert not unknown, f"feeling {k} names unknown entries: {unknown}"
    for cat, names in index_full["byCategory"].items():
        unknown = [n for n in names if n not in all_names]
        assert not unknown, f"category {cat} names unknown entries: {unknown}"

    # 3. A group offering a single option is not a choice.
    per_group = collections.Counter(f["group"] for f in feelings)
    thin = {g: n for g, n in per_group.items() if n < 2}
    assert not thin, f"groups with fewer than 2 feelings: {thin}"

    # 4. Every group named by a feeling must exist, and vice versa.
    gkeys = {g["key"] for g in groups}
    assert set(per_group) <= gkeys, f"feelings reference unknown groups: {set(per_group) - gkeys}"
    assert gkeys <= set(per_group), f"groups with no feelings at all: {gkeys - set(per_group)}"

    # 5. Nothing may be strandable: every entry must be reachable through at
    #    least one axis. The category axis covers all 349 by construction,
    #    which is precisely why it is the walkthrough's guaranteed fallback.
    reachable = set()
    for names in by_feeling.values():
        reachable |= set(names)
    for names in index_full["byCategory"].values():
        reachable |= set(names)
    assert reachable == all_names, f"unreachable entries: {sorted(all_names - reachable)[:10]}"

    OUT.write_text(json.dumps(index, ensure_ascii=False,
                              separators=(",", ":"), sort_keys=True) + "\n",
                   encoding="utf-8")

    only_via_category = all_names - set().union(*by_feeling.values())
    print(f"wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size:,} bytes)")
    print(f"  groups            {len(groups)}")
    print(f"  feelings          {len(feelings)}  "
          f"(per group: {dict(per_group)})")
    print(f"  entries via feelings   {len(all_names) - len(only_via_category)}/349")
    print(f"  entries only via category {len(only_via_category)}/349")
    print(f"  categories        {len(index_full['byCategory'])}")
    print(f"  safety-sensitive  {len(safety)}/349")
    sizes = sorted(len(v) for v in by_feeling.values())
    print(f"  feeling set sizes min={sizes[0]} max={sizes[-1]}")
    print("\nall invariants hold")


if __name__ == "__main__":
    main()
