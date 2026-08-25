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
  4 NOT-THIS  what_it_is_not          when this is NOT what's happening
  5 CLOSE     boundary_script          what to say instead

Beat 4 is the point of the series. Every other account that names manipulation
tactics stops at beat 3, because doubt costs retention. Including the
disconfirming case is what makes this a reference work rather than an outrage
feed, and it is what keeps each entry's own misuse_warning true once the entry
leaves the book: "one example is a signal to examine, not proof of motive."

Which field it comes from matters more than it looks. `this_may_not_be_it_when`
is present on all 349 entries and is the obvious choice -- and it holds only
**20 distinct lines across 1,745 items**. Sourcing beat 4 there would end all
349 clips on the same sentence. `what_it_is_not` (178 distinct) and
`common_false_positives` (916 distinct, 911 of them used exactly once) carry
the entry-specific version:

    Gaslighting  "One-off disagreement about facts is normal; people genuinely
                  misremember. It's the *pattern* of attacking your sanity."
    Trivializing "Occasionally people do overreact, and saying so once, gently,
                  can be honest feedback."

So beat 4 takes the first line that is unique to this entry, and a clip whose
only available line is shared is marked `needs_disconfirm` rather than shipped
with boilerplate.

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
import re
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

MATURITY_RANK = {"mature": 0, "developing": 1, "needs_review": 2,
                 "reference_stub": 3}
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

# The book grades its own entries, and the grading is load-bearing for a
# release. `codex_maturity` splits 349 into mature 81 / needs_review 143 /
# reference_stub 101 / developing 24, and `human_review_flags` marks specific
# risks on every single entry. Cutting a clip from an entry the book itself
# calls a stub publishes something its author has not finished.
#
# Two flags stop a clip outright:
#
#   reference_stub             the entry is scaffolding, not a finished entry.
#                              101 of them, and 17 currently pass every other
#                              readiness test, so nothing else would catch it.
#   manipulation_playbook_risk naming the mechanism this precisely is usable
#                              as instruction. 51 entries. Whether to publish
#                              those at all is the author's call, not a
#                              pipeline's.
#
# Two more change how a clip is cut rather than whether:
#
#   safety_sensitive           the entry's safety_note has to be on screen.
#   high_false_positive_risk   beat 4 -- the disconfirming case -- stops being
#                              a nice editorial choice and becomes required.
#                              65 of the shoot-ready set carry this.
HOLD_FLAGS = {"manipulation_playbook_risk"}
HOLD_MATURITY = {"reference_stub"}
PRODUCTION_FLAGS = {"safety_sensitive", "high_false_positive_risk"}


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


# Boundaries the author already put in the sentence. Splitting here is
# choosing where the writer's own clause ends -- it is not a rewrite, and
# nothing is ever cut mid-phrase. Comma splits are restricted to the
# connectives that begin a trailing subordinate clause, because a bare comma
# is just as likely to be separating items in a list.
CLAUSE_BREAK = re.compile(
    r"\s*[—;:]\s*"
    r"|,\s+(?=so |which |making |leaving |until |while |before |after )")


def lead_clause(text):
    """The first clause of `text`, or None if it is not shorter than the whole.

    Used only on short_definition, which is the one field that is distinct on
    all 349 entries. what_it_sounds_like is 99% distinct but long on
    Reference-only entries; this_may_be_it_when and pattern_over_time_signs
    look promising (100% of entries have a line under the budget) and are in
    fact boilerplate -- 20 and 15 distinct lines respectively across the whole
    corpus, so they identify nothing.
    """
    if not text:
        return None
    parts = [p.strip().rstrip(".,;:—") for p in CLAUSE_BREAK.split(text)]
    parts = [p for p in parts if p]
    if not parts:
        return None
    head = parts[0]
    return head if len(head) < len(text.strip()) else None


def first_unique(entry, fields, shared):
    """First line from `fields` that no other entry also uses.

    `shared` is computed from the corpus rather than hard-coded, so a field
    that becomes boilerplate later is caught without editing this file.
    """
    for field in fields:
        value = entry.get(field)
        items = value if isinstance(value, list) else [value]
        for item in items:
            if not isinstance(item, str):
                continue
            line = item.strip()
            if line and line not in shared:
                return line, field
    return None, None


def first(lst):
    for item in lst or []:
        if isinstance(item, str) and item.strip():
            return item.strip()
    return None


def build(entry, shared=frozenset()):
    hook, alts = pick_hook(entry.get("what_it_sounds_like") or [])
    hook_source = "what_it_sounds_like"

    # If the entry's own spoken lines are all too long to read in three
    # seconds -- which is the normal case outside the Detected tier, where
    # the field holds descriptions rather than quotes -- fall back to the
    # opening clause of short_definition. Only accept it if it actually fits;
    # a truncation that still overruns helps nobody.
    if not hook or len(hook) > HOOK_MAX_CHARS:
        lead = lead_clause((entry.get("short_definition") or "").strip())
        if lead and len(lead) <= HOOK_MAX_CHARS:
            if hook:
                alts = [hook] + alts
            hook, hook_source = lead, "short_definition (lead clause)"
    not_this, not_this_source = first_unique(
        entry, ("what_it_is_not", "common_false_positives", "less_concerning_if"),
        shared)
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

    if stage == "shoot_ready" and not not_this:
        stage = "needs_disconfirm"

    maturity = entry.get("codex_maturity") or "unknown"
    flags = sorted(entry.get("human_review_flags") or [])
    holds = sorted(set(flags) & HOLD_FLAGS)
    if maturity in HOLD_MATURITY:
        holds.append("maturity:%s" % maturity)
    requires = sorted(set(flags) & PRODUCTION_FLAGS)
    gate = "hold" if holds else "clear"
    if gate == "hold":
        stage = "held"

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
        ("hook_source", hook_source),
        ("not_this_source", not_this_source),
        ("hook_alternates", alts),
        ("short_definition", (entry.get("short_definition") or "").strip()),
        ("summary", (entry.get("plain_language_summary") or "").strip()),
        ("misuse_warning", entry.get("misuse_warning") or []),
        ("safety_note", (entry.get("safety_note") or "").strip()),
        ("related_tactics", entry.get("related_tactics") or []),
        ("stage", stage),
        ("release_gate", gate),
        ("held_because", holds),
        ("production_requires", requires),
        ("codex_maturity", maturity),
        ("review_flags", flags),
        ("hook_chars", len(hook) if hook else 0),
        ("needs_review", missing),
    ])


def interleave(clips):
    """One clip per category, cycling, Detected tier first within each."""
    buckets = defaultdict(list)
    for clip in clips:
        buckets[clip["category"]].append(clip)
    for cat in buckets:
        buckets[cat].sort(key=lambda c: (
            0 if c["stage"] == "shoot_ready" else 1,
            MATURITY_RANK.get(c["codex_maturity"], 9),
            len(c["production_requires"]),
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
    entries = data["codex_completed"]

    # Any line that appears on more than one entry identifies nothing,
    # whatever field it sits in. Derive that from the corpus so a field
    # turning into boilerplate later is caught automatically.
    counts = Counter()
    for entry in entries:
        for field in ("what_it_is_not", "common_false_positives",
                      "less_concerning_if"):
            value = entry.get(field)
            items = value if isinstance(value, list) else [value]
            for item in items:
                if isinstance(item, str) and item.strip():
                    counts[item.strip()] += 1
    shared = frozenset(line for line, n in counts.items() if n > 1)

    clips = interleave([build(e, shared) for e in entries])

    ready = [c for c in clips if c["stage"] == "shoot_ready"]
    needs_hook = [c for c in clips if c["stage"] == "needs_hook"]
    blocked = [c for c in clips if c["stage"] == "needs_source"]
    held = [c for c in clips if c["stage"] == "held"]
    no_disconfirm = [c for c in clips if c["stage"] == "needs_disconfirm"]

    print("Pattern Decoder -- short-form release manifest")
    print("  %d tactics" % len(clips))
    print("    %3d shoot-ready   every beat present, hook <=%d chars"
          % (len(ready), HOOK_MAX_CHARS))
    print("    %3d needs-hook    complete, but the opening line needs choosing"
          % len(needs_hook))
    print("    %3d needs-source  a beat has no field to draw from"
          % len(blocked))
    print("    %3d held          the book grades this entry as unfinished or "
          "risky" % len(held))
    print("    %3d needs-disconfirm  no what_it_is_not line unique to this "
          "entry" % len(no_disconfirm))
    print()

    sources = Counter(c["not_this_source"] for c in ready)
    if sources:
        print("  beat 4 drawn from:")
        for field, n in sources.most_common():
            print("    %-30s %3d" % (field, n))
        print()

    if held:
        reasons = Counter(r for c in held for r in c["held_because"])
        print("  held, by the book's own grading:")
        for reason, n in reasons.most_common():
            print("    %-34s %3d" % (reason, n))
        print()

    requires = Counter(r for c in ready for r in c["production_requires"])
    if requires:
        print("  shoot-ready clips with a production requirement:")
        for req, n in requires.most_common():
            note = {"safety_sensitive": "put safety_note on screen",
                    "high_false_positive_risk": "beat 4 is mandatory"}.get(req, "")
            print("    %-30s %3d   %s" % (req, n, note))
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
