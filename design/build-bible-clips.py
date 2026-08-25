#!/usr/bin/env python3
"""Build the Festie Bible short-form manifest from its 149 scenarios.

Run from the repo root: python3 design/build-bible-clips.py [--apply]
Dry-run (default) prints the report, writes nothing.
--apply writes content/bible-clips.json.

Why this book, and why it is not shaped like the Decoder's
----------------------------------------------------------
The Festie Bible was the least visible project in the repo -- no BOOKS.md
section, no chapters.json record, no prose extraction -- and it turns out to
hold the strongest short-form material in the catalogue. All 149 scenarios
carry a `hook` field, median 24 characters, every one inside the 80-character
budget. The Pattern Decoder manages that on 112 of 349.

It is also organised on an axis nothing else here uses: twelve guides by
WHO YOU ARE at the festival (women attendees, men attendees, first-timers,
LGBTQ+ attendees, live painters, musicians, vendors, staff, harm reduction,
camp leads, promoters, health and safety) rather than by topic. A clip can
therefore be aimed at a real audience rather than a subject.

127 of 149 scenarios also carry a `clinical` field naming the same tactics
The Pattern Decoder catalogues -- so the two books already cross-reference,
and a viewer arriving from either can be handed the other.

The structural difference that matters
--------------------------------------
The Decoder gives every entry a disconfirming beat (`what_it_is_not`): the
innocent thing that looks the same. **The Bible has no equivalent field.**
That is reported here, not invented: for a harm-reduction book read by people
in an unfamiliar and sometimes unsafe setting, over-reading a stranger's
ordinary friendliness has its own cost. The `move` and `truth` fields carry
some of that work ("A connection that's real will still be real after you
check in with camp") and are used as the closing beats, but they are not a
disconfirming case and should not be presented as one.

The five beats, and the field each comes from:

  1 HOOK   hook           what someone actually says, 24 chars median
  2 SCENE  scene          the situation, trimmed to its first sentence
  3 TELLS  tells[0]       the first signal
  4 SAY    say            the words to use back, verbatim
  5 TRUTH  truth          the closing line

`check` (the guide's own acronym prompt) is carried on every record as the
call back to the book, since it only makes sense once you know the acronym.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, OrderedDict

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "content", "festie-bible-data.json")
OUT = os.path.join(ROOT, "content", "bible-clips.json")

HOOK_MAX_CHARS = 80

# Listening Room shelves. The Bible is festival material end to end, so most
# of it sits on The Festival Floor; the sections about aftermath and harm sit
# elsewhere. Sections come from the book's own arc (CAPTURE, CONTROL, ...).
SHELF_BY_SECTION = {
    "CAPTURE": "The Festival Floor",
    "CONTROL": "The Descent",
    "CONSENT": "The Tender Room",
    "CRISIS": "The Reckoning",
    "COMMUNITY": "The Festival Floor",
    "AFTERMATH": "The Tender Room",
    "RECOVERY": "The Tender Room",
}


def first_sentence(text, limit=220):
    if not text:
        return None
    text = text.strip()
    m = re.match(r"(.{30,%d}?[.!?])(\s|$)" % limit, text)
    return (m.group(1) if m else text[:limit]).strip()


def build(guide, scenario):
    hook = (scenario.get("hook") or "").strip()
    tells = [t.strip() for t in (scenario.get("tells") or [])
             if isinstance(t, str) and t.strip()]
    beats = OrderedDict([
        ("hook", hook or None),
        ("scene", first_sentence(scenario.get("scene"))),
        ("tells", tells[0] if tells else None),
        ("say", (scenario.get("say") or "").strip() or None),
        ("truth", (scenario.get("truth") or "").strip() or None),
    ])
    missing = [k for k, v in beats.items() if not v]
    if missing:
        stage = "needs_source"
    elif len(hook) <= HOOK_MAX_CHARS:
        stage = "shoot_ready"
    else:
        stage = "needs_hook"

    return OrderedDict([
        ("name", scenario.get("archetype") or hook),
        ("hook_line", hook),
        ("guide", guide.get("slug")),
        ("role", guide.get("role")),
        ("acronym", guide.get("acronym")),
        ("section", scenario.get("section")),
        ("clinical", scenario.get("clinical")),
        ("shelf", SHELF_BY_SECTION.get(scenario.get("section"),
                                       "The Festival Floor")),
        ("beats", beats),
        ("check", (scenario.get("check") or "").strip()),
        ("move", (scenario.get("move") or "").strip()),
        ("dark_title", scenario.get("darkTitle")),
        ("has_dark_version", bool((scenario.get("dark") or "").strip())),
        ("has_disconfirming_beat", False),
        ("stage", stage),
        ("hook_chars", len(hook)),
        ("needs_review", missing),
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    data = json.load(open(SRC, encoding="utf-8"))
    clips, guides = [], data.get("guides", [])
    for guide in guides:
        for scenario in guide.get("scenarios") or []:
            clips.append(build(guide, scenario))

    # One clip per guide, cycling, so the release reads as twelve audiences
    # being served rather than one guide being worked through.
    buckets = OrderedDict()
    for clip in clips:
        buckets.setdefault(clip["guide"], []).append(clip)
    ordered = []
    while any(buckets.values()):
        for slug in list(buckets):
            if buckets[slug]:
                ordered.append(buckets[slug].pop(0))

    ready = [c for c in ordered if c["stage"] == "shoot_ready"]
    print("The Festie Bible -- short-form manifest")
    print("  %d scenarios across %d role guides" % (len(clips), len(guides)))
    print("    %3d shoot-ready   hook <=%d chars, every beat present"
          % (len(ready), HOOK_MAX_CHARS))
    for stage in ("needs_hook", "needs_source"):
        n = sum(1 for c in ordered if c["stage"] == stage)
        if n:
            print("    %3d %s" % (n, stage))
    print()

    lengths = sorted(c["hook_chars"] for c in clips)
    print("  hook length: median %d, max %d, all under budget: %s"
          % (lengths[len(lengths) // 2], lengths[-1],
             "yes" if lengths[-1] <= HOOK_MAX_CHARS else "no"))
    linked = sum(1 for c in clips if c["clinical"])
    print("  %d of %d name a Pattern Decoder tactic in `clinical`"
          % (linked, len(clips)))
    print()

    print("  by guide:")
    for guide in guides:
        rows = [c for c in clips if c["guide"] == guide["slug"]]
        print("    %-8s %-28s %2d scenarios" % (guide["slug"],
                                                guide["role"][:28], len(rows)))
    print()
    print("  first 10 in release order (one per guide, cycling):")
    for i, c in enumerate(ordered[:10], 1):
        print("    %2d. %-34s %-22s %s"
              % (i, (c["hook_line"] or "")[:34], c["role"][:22], c["section"]))

    if not args.apply:
        print("\ndry run -- pass --apply to write %s" % os.path.relpath(OUT, ROOT))
        return 0

    payload = OrderedDict([
        ("note", "Short-form manifest for The Festie Bible. Every beat is "
                 "copied from the book's own scenario fields; no line is "
                 "written here. Regenerate rather than hand-editing."),
        ("source", "content/festie-bible-data.json"),
        ("beats", ["hook: hook", "scene: scene (first sentence)",
                   "tells: tells[0]", "say: say", "truth: truth"]),
        ("caveat", "Unlike The Pattern Decoder, this book has no "
                   "disconfirming field -- nothing that names the innocent "
                   "behaviour that looks the same. `move` and `truth` soften "
                   "the read but are not a disconfirming case. Worth writing "
                   "one before these ship at volume."),
        ("counts", {"total": len(clips), "shoot_ready": len(ready),
                    "cross_linked_to_decoder": linked}),
        ("clips", ordered),
    ])
    json.dump(payload, open(OUT, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    open(OUT, "a", encoding="utf-8").write("\n")
    print("\nwrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
