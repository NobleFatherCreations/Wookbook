#!/usr/bin/env python3
"""Apply a clinical/psychological review's verdicts to the staged drafts.

Run from the repo root: python3 design/apply-psych-review.py [--apply]
Dry-run (default) validates content/drafting/psych-review-output.json and
reports what it would do, without writing anything.

What this does and does not do
-------------------------------
Reads verdicts (approved / denied / needs_revision) from the review output
and applies them to content/playbook-drafts.json:

  approved       -> approved: true. This is the only verdict that changes
                    an entry's approval state.
  denied         -> approved stays false. The reviewer's rationale is
                    recorded on the entry as review_verdict / review_note.
  needs_revision -> approved stays false, same recording. Not auto-fixed --
                    a needs_revision verdict is a request for a human or a
                    fresh drafting pass, never something this script resolves
                    on its own.

Every entry in the drafts file must receive a verdict; the run refuses to
apply if any are missing, so a partial review can never look like a completed
one.
"""
import argparse
import json
import os
import sys
from collections import Counter, OrderedDict

ROOT = os.path.join(os.path.dirname(__file__), "..")
DRAFTS = os.path.join(ROOT, "content", "playbook-drafts.json")
REVIEW = os.path.join(ROOT, "content", "drafting", "psych-review-output.json")

VALID_VERDICTS = {"approved", "denied", "needs_revision"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(REVIEW):
        print("missing %s -- nothing to apply" % os.path.relpath(REVIEW, ROOT))
        return 1

    review = json.load(open(REVIEW, encoding="utf-8"))
    verdicts = {}
    problems = []
    for row in review:
        name, item_type = row.get("name"), row.get("item_type")
        verdict = row.get("verdict")
        if verdict not in VALID_VERDICTS:
            problems.append("invalid verdict %r on %s/%s" % (verdict, item_type, name))
            continue
        if not (row.get("rationale") or "").strip():
            problems.append("empty rationale on %s/%s" % (item_type, name))
        key = (item_type, name)
        if key in verdicts:
            problems.append("duplicate verdict for %s/%s" % (item_type, name))
        verdicts[key] = row

    drafts = json.load(open(DRAFTS, encoding="utf-8"), object_pairs_hook=OrderedDict)

    missing = []
    for h in drafts["hooks"]:
        if ("hook", h["name"]) not in verdicts:
            missing.append("hook: %s" % h["name"])
    for c in drafts["codex_fields"]:
        if ("codex", c["name"]) not in verdicts:
            missing.append("codex: %s" % c["name"])

    print("review covers %d verdicts (%d hooks, %d codex expected)"
          % (len(verdicts), len(drafts["hooks"]), len(drafts["codex_fields"])))
    if problems:
        print("\nPROBLEMS (%d):" % len(problems))
        for p in problems[:20]:
            print("  x %s" % p)
        if len(problems) > 20:
            print("  ... and %d more" % (len(problems) - 20))
    if missing:
        print("\nMISSING VERDICTS (%d) -- refusing to apply a partial review:"
              % len(missing))
        for m in missing[:20]:
            print("  ! %s" % m)
        if len(missing) > 20:
            print("  ... and %d more" % (len(missing) - 20))

    tally = Counter(row["verdict"] for row in verdicts.values())
    print("\nverdicts: %s" % ", ".join("%s %d" % (k, v)
                                       for k, v in tally.most_common()))

    if problems or missing:
        print("\nrefusing to apply -- fix the review output first")
        return 1

    for h in drafts["hooks"]:
        v = verdicts[("hook", h["name"])]
        h["approved"] = v["verdict"] == "approved"
        h["review_verdict"] = v["verdict"]
        h["review_note"] = v["rationale"]

    for c in drafts["codex_fields"]:
        v = verdicts[("codex", c["name"])]
        c["approved"] = v["verdict"] == "approved"
        c["review_verdict"] = v["verdict"]
        c["review_note"] = v["rationale"]

    if not args.apply:
        print("\ndry run -- pass --apply to write the verdicts into "
              "content/playbook-drafts.json")
        return 0

    drafts["reviewed_by"] = "clinical/psychological review, see PSYCH-REVIEW.md"
    json.dump(drafts, open(DRAFTS, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    open(DRAFTS, "a", encoding="utf-8").write("\n")
    print("\nwrote verdicts into %s" % os.path.relpath(DRAFTS, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
