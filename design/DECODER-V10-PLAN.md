# Pattern Decoder v10 — architecture and design plan

Goal (the author, 2026-10-22): helpful and easy to understand for people of all
levels; easy to navigate even when people don't know what to look for; beautiful,
with high attention to detail. Clarity, ease of use, and real value.

## Who arrives, and how

| Arrives as | Knows | Needs first |
|---|---|---|
| Hurting, unsure | a feeling, a phrase someone said | "describe it" search, guided questions |
| Has a word | "gaslighting", "love bombing" | instant name search, aliases |
| Curious / studying | nothing specific | browse by kind, the most common ones |
| Helper / advocate | a case | full entry, print, share a link |

## Baseline findings (v9, 2026-10-22)

- Phone: the search box is below the fold, under the cover plate and an animated title.
- Nav labels mean nothing to a newcomer: Start, Core, Index, Map, Patterns, Trail.
- Entry page is 6,100px tall on a phone; most sections are unlabeled-looking
  accordions; the full changelog is printed under every entry.
- 24 categories, several of them mixed bags ("Control structural",
  "Discard / institutional"); casing inconsistent.
- Name quotes render as closing quotes ("”I Know Best”").
- 4.4 MB single file: data 3.5 MB, cover 209 KB, fonts 253 KB, app ~60 KB.
  4x-throttled phone CPU: ~2.2 s to interactive from a local file.
- Three fonts (IM Fell, Public Sans, Space Mono); the house rule is two.

## Site map (hash routes; every old route keeps working)

```
Home                         #/
├── Find it
│   ├── Search / describe    #/search/<q>         (name, alias, phrase someone said)
│   ├── Help me figure it out #/guide             (3 short questions -> a short list)
│   └── The most common      #/common             (old #/core redirects here)
├── Browse
│   ├── By what it does      #/browse, #/browse/<group>      (~8 reader groups)
│   ├── By where it happens  #/where/<setting>               (relationship, family, work...)
│   └── A–Z                  #/all
├── Entry                    #/entry/<slug>       (aliases redirect)
├── How tactics combine      #/patterns, #/patterns/<name>
├── Saved & recent           #/saved              (old #/trail redirects here)
└── Use this safely          #/about
```

Header: logo/home, Search, Browse, Saved; "Use this safely" always one tap away.
Phone: a bottom bar (Home, Search, Browse, Saved) and, on entry pages, a sections
button. The House (Noble Father Creations) menu is kept unchanged.

## Entry page (one page, all sections, four clear parts)

1. Title, plain-words subtitle for jargon names, group crumb, safety badge.
2. **In short**: plain summary + two or three "sounds like" lines.
3. **Is this it?** may be it / may not be it side by side; what it is not and
   ordinary explanations; questions to ask yourself; less vs more concerning;
   what shows up over time.
4. **What you can do**: a boundary script you can copy; five response options
   as cards; how to read their response; what real repair looks like; safety note
   (raised to the top when the entry is safety-sensitive).
5. **Go deeper**: how it works, how it can affect you, how it differs from its
   neighbours (linked), how the label gets misused, related tactics, patterns it
   belongs to.

A sticky section index (chips) jumps between parts; every part is open by default
on desktop and one tap away on a phone. Previous/next within the group, back to the
group, related tactics. Back always returns to the exact scroll position.

## Visual direction

Keep: the celestial-chart identity, dark sky theme (light "twilight" theme too,
following the system), brass as the one accent, numbered/labelled sections.
Change: two fonts only (IM Fell English for titles, Public Sans for everything
else); cover plate becomes a calm title moment that never pushes search below the
fold; one 8px grid; 60–70 character measure; quieter cards with more space.

## Motion

Native View Transitions between list and entry (title morphs), 200–250 ms ease-out,
interruptible; scroll-linked section highlight; nothing essential behind motion;
all of it off under reduced motion.

## Build

`design/build-decoder-v10.py` generates one self-contained HTML file from
`content/playbook-data.json`, `content/codex-final/reader-meta.json` (groups,
settings, plain subtitles, everyday search words), and assets lifted from the
v9 page (fonts, cover, wordmark, House menu). No CDN; the Cloudflare beacon stays.
Entries render on demand. Draft output: `content/prose/_raw/playbook-v10.html`;
it replaces `playbook.html` only when it ships.

## Order

0 baseline (done) → 1 content audit (`content/codex-final/CONTENT-AUDIT.md`) →
2 reader metadata (groups, settings, subtitles, search words) → 3 build →
4 motion → 5 phone / accessibility / speed → 6 QA + art-director cut → 7 ship v10
(deploy only with the author's go-ahead).
