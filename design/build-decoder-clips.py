#!/usr/bin/env python3
"""Build the Pattern Decoder short-form release manifest from the book's own data.

Run from the repo root: python3 design/build-decoder-clips.py [--apply]
Dry-run (default) prints the release report, writes nothing.
--apply writes content/decoder-clips.json.

What this produces
------------------
One clip record per tactic, assembled entirely out of fields the book already
contains. No line here is written by this script; every string is copied from
content/playbook-data.json. If a beat has no source field, the clip is marked
needs_review rather than filled in.

The five-beat clip, and the field each beat comes from:

  1 HOOK      what_it_sounds_like[]    a line the viewer has heard before
  2 NAME      name + category          what it is called
  3 MECHANISM why_this_matters         why it works, in the book's own words
  4 NOT-THIS  this_may_not_be_it_when  when this is NOT what's happening
  5 CLOSE     boundary_script          what to say instead

Beat 4 is the point of the series. Every other account that names manipulation
tactics stops at beat 3, because doubt costs retention. This book carries a
this_may_not_be_it_when and a common_false_positives field on all 349 entries,
so the disconfirming case is available for free -- and including it is what
makes the series honest rather than another outrage feed. It is also the beat
that keeps the misuse_warning true: "one example is a signal to examine, not
proof of motive."

Ordering
--------
Release order is not virality-scored. It is: one clip per category, cycling,
so the first pass across the corpus is broad rather than deep, and no single
category dominates the opening weeks. Within a category, Detected-tier entries
go first -- those are the ones the live tool can actually flag in pasted text,
so a viewer who arrives at the site can immediately do the thing the clip
described.
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict, OrderedDict

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "content", "playbook-data.json")
OUT = os.path.join(ROOT, "content", "decoder-clips.json")

# Listening Room shelves, by the register a category actually reads in --
# see BOOKS.md for what each shelf holds. Used to pick a bed track without
# licensing anything.
SHELF_BY_CATEGORY = {
    "Reality Distortion": "The Descent",
    "Accountability Evasion": "The Reckoning",
    "Attachment & Affection Control": "The Tender Room",
    "Attack & Erosion": "The Reckoning",
    "Confusion / rhetoric": "The Frequency",
    "Control & Domination": "The Reckoning",
    "Control structural": "The Reckoning",
    "Cult & Thought Reform": "The Descent",
    "Deception": "The Frequency",
    "Devaluation structural": "The Descent",
    "Digital": "The Frequency",
    "Digital & AI": "The Frequency",
    "Discard / institutional": "The Descent",
    "Espionage & Influence Operations": "The Frequency",
    "Guilt & Obligation Leverage": "The Tender Room",
    "Hooking structural": "The Tender Room",
    "Idealization structural": "The Tender Room",
    "Identity & Conditioning": "The Descent",
    "Institutional & Process": "The Reckoning",
    "Isolation / social": "The Descent",
    "Organizational & Institutional": "The Reckoning",
    "Political & Propaganda": "The Frequency",
    "Pressure & Coercion": "The Reckoning",
    "Social Warfare & Triangulation": "The Reckoning",
}

TIER_RANK = {"Detected": 0, "Pattern-only": 1, "Watch-only": 2, "Reference-only": 3}

# A hook has to be *read* in about three seconds, muted, on a phone. Measured
# across the corpus, 80 characters is where a line stops fitting that.
#
# This threshold does more work than it looks like it does, because
# what_it_sounds_like is not one kind of field. On Detected-tier entries it
# holds actual spoken lines ("It's your fault." / "You'll thank me later.") --
# median 22 characters, and 81 of 81 come in under the limit. On
# Reference-only entries it holds *descriptions* of a signal ("Following a
# specific characterization, the target experiences a wave of harassment
# from people who cite...") -- median 106 characters, and only 6 of 244 fit.
#
# So the tier field, which exists to say what the live tool can detect in
# pasted text, turns out to also predict whether an entry can be cut without
# an editorial pass. That is what splits the corpus into shoot-ready and
# needs-a-hook, and it is why release order follows the tiers.
HOOK_MAX_CHARS = 80


def pick_hook(sounds):
    """Shortest distinct line -- the one that fits on screen at 3 seconds.

    Short wins because the hook has to be read, not heard: most of this is
    watched muted, and a line the viewer recognises has to land before they
    decide to swipe. All the other lines are kept as alternates so a clip can
    be recut without going back to the data.
    """
    lines = [s.strip() for s in sounds if isinstance(s, str) and s.strip()]
    seen, uniq = set(), []
    for line in lines:
        key = line.lower()
        if key not in seen:
            seen.add(key)
            uniq.append(line)
    if not uniq:
        return None, []
    ordered = sorted(uniq, key=lambda s: (len(s), s))
    return ordered[0], ordered[1:]


def first(lst):
    for item in lst or []:
        if isinstance(item, str) and item.strip():
            return item.strip()
    return None


def build(entry):
    hook, alts = pick_hook(entry.get("what_it_sounds_like") or [])
    not_this = first(entry.get("this_may_not_be_it_when"))
    close = (entry.get("boundary_script") or "").strip() or None
    mechanism = (entry.get("why_this_matters") or "").strip() or None

    missing = [n for n, v in (("hook", hook), ("mechanism", mechanism),
                              ("not_this", not_this), ("close", close)) if not v]

    # Shoot-ready means: every beat present, and the hook is a line short
    # enough to read rather than a description that needs rewriting first.
    # Anything else is still a good clip -- it just needs a human to choose
    # the opening, which is editorial work this script must not fake.
    usable_hook = bool(hook) and len(hook) <= HOOK_MAX_CHARS
    if missing:
        stage = "needs_source"
    elif usable_hook:
        stage = "shoot_ready"
    else:
        stage = "needs_hook"

    return OrderedDict([
        ("name", entry["name"]),
        ("category", entry["category"]),
        ("tier", entry["tier"]),
        ("shelf", SHELF_BY_CATEGORY.get(entry["category"], "The Wider Catalogue")),
        ("beats", OrderedDict([
            ("hook", hook),
            ("name", entry["name"]),
            ("mechanism", mechanism),
            ("not_this", not_this),
            ("close", close),
        ])),
        ("hook_alternates", alts),
        ("summary", (entry.get("plain_language_summary") or "").strip()),
        ("misuse_warning", entry.get("misuse_warning") or []),
        ("safety_note", (entry.get("safety_note") or "").strip()),
        ("related_tactics", entry.get("related_tactics") or []),
        ("stage", stage),
        ("hook_chars", len(hook) if hook else 0),
        ("needs_review", missing),
    ])


def interleave(clips):
    """One clip per category, cycling, Detected tier first within each."""
    buckets = defaultdict(list)
    for clip in clips:
        buckets[clip["category"]].append(clip)
    for cat in buckets:
        buckets[cat].sort(key=lambda c: (0 if c["stage"] == "shoot_ready" else 1,
                                         TIER_RANK.get(c["tier"], 9), c["name"]))

    order, cats = [], sorted(buckets)
    while any(buckets[c] for c in cats):
        for cat in cats:
            if buckets[cat]:
                order.append(buckets[cat].pop(0))
    return order


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="write content/decoder-clips.json (default: dry run)")
    ap.add_argument("--weekly", type=int, default=5,
                    help="clips per week, for the schedule report (default 5)")
    args = ap.parse_args()

    if not os.path.exists(SRC):
        print("missing %s -- run design/extract-playbook-data.py --apply first"
              % os.path.relpath(SRC, ROOT))
        return 1

    data = json.load(open(SRC, encoding="utf-8"))
    clips = interleave([build(e) for e in data["codex_completed"]])

    ready = [c for c in clips if c["stage"] == "shoot_ready"]
    needs_hook = [c for c in clips if c["stage"] == "needs_hook"]
    blocked = [c for c in clips if c["stage"] == "needs_source"]

    print("Pattern Decoder -- short-form release manifest")
    print("  %d tactics" % len(clips))
    print("    %3d shoot-ready   every beat present, hook <=%d chars"
          % (len(ready), HOOK_MAX_CHARS))
    print("    %3d needs-hook    complete, but the opening line needs choosing"
          % len(needs_hook))
    print("    %3d needs-source  a beat has no field to draw from"
          % len(blocked))
    print()

    print("  hook usability by tier (why the split falls where it does):")
    for tier in ("Detected", "Pattern-only", "Watch-only", "Reference-only"):
        group = [c for c in clips if c["tier"] == tier]
        if not group:
            continue
        fits = sum(1 for c in group if c["hook_chars"] <= HOOK_MAX_CHARS)
        med = sorted(c["hook_chars"] for c in group)[len(group) // 2]
        print("    %-15s %3d entries  %3d usable (%3d%%)  median %3d chars"
              % (tier, len(group), fits, round(100 * fits / len(group)), med))
    print()

    unmapped = sorted({c["category"] for c in clips
                       if c["shelf"] == "The Wider Catalogue"})
    if unmapped:
        print("  categories with no shelf mapping: %s" % ", ".join(unmapped))
        print()

    print("  by tier:")
    for tier, n in Counter(c["tier"] for c in clips).most_common():
        print("    %-16s %3d" % (tier, n))
    print()

    print("  the shooting queue -- first %d shoot-ready, in release order:"
          % min(12, len(ready)))
    for i, c in enumerate(ready[:12], 1):
        print("    %2d. %-30s %-30s %s"
              % (i, c["name"][:30], c["category"][:30], c["shelf"]))
    print()

    covered = len({c["category"] for c in ready})
    print("  shoot-ready spans %d of %d categories" % (covered, len(set(
        c["category"] for c in clips))))
    thin = sorted(cat for cat in {c["category"] for c in clips}
                  if not any(r["category"] == cat for r in ready))
    if thin:
        print("  no shoot-ready entry in: %s" % ", ".join(thin))
    print()

    if blocked:
        print("  needs-source (a beat has no field):")
        for c in blocked[:20]:
            print("    %-32s missing: %s" % (c["name"][:32],
                                             ", ".join(c["needs_review"])))
        print()

    for label, n in (("shoot-ready only", len(ready)), ("whole corpus", len(clips))):
        weeks = (n + args.weekly - 1) // args.weekly
        print("  %-17s at %d/week: %3d weeks (%.1f years)"
              % (label, args.weekly, weeks, weeks / 52))

    if not args.apply:
        print("\ndry run -- pass --apply to write %s"
              % os.path.relpath(OUT, ROOT))
        return 0

    payload = OrderedDict([
        ("note", ("Short-form release manifest for The Pattern Decoder. Every "
                  "beat is copied from the book's own fields via "
                  "design/build-decoder-clips.py -- no line is written here. "
                  "Regenerate rather than hand-editing.")),
        ("source", "content/playbook-data.json"),
        ("beats", ["hook: what_it_sounds_like",
                   "name: name + category",
                   "mechanism: why_this_matters",
                   "not_this: this_may_not_be_it_when",
                   "close: boundary_script"]),
        ("hook_max_chars", HOOK_MAX_CHARS),
        ("counts", {"total": len(clips), "shoot_ready": len(ready),
                    "needs_hook": len(needs_hook),
                    "needs_source": len(blocked)}),
        ("clips", clips),
    ])
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("\nwrote %s (%.1f MB)"
          % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
