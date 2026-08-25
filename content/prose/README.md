# Extracted book/tool prose

The actual written content of every Noble Father Creations book and tool,
pulled straight out of each project's own shipped source and stripped of
all HTML/CSS/JS — nothing invented, nothing summarized. This exists so any
AI (or human) can read the real words of a book without having to parse an
8MB single-file HTML app to find them.

Regenerate any time a book's content changes:
`python3 design/extract-prose-master.py --apply` (dry-run without `--apply`
prints word counts only, writes nothing).

## Naming

**Every file here is named after the project's `slug` in `sites.json`** —
the same key used by the `BOOKS.md` heading and the live URL. Before
2026-08-25 this directory used its own names, and one of them collided:
`festival.md` held The Festie *Codex*, while slug `festival` belongs to The
Festie *Bible*, a different project. Four files were renamed
(`festival`→`wook`, `sovereign`→`feminine`, `playground`→`children`,
`root`→`shadowroot`); `design/audit-registry.py` now fails if the rule breaks
again. See `INDEX.md` for the full lookup, aliases included.

The Festie Bible has no prose file — its content is structured data in
`content/festie-bible-data.json`, not chapter prose.

## Coverage — complete, all 11 projects

| File | Words | Source | Method |
|---|---:|---|---|
| `wook.md` | 250,974 | `source/projects/noble-father-festival.html` | static HTML |
| `faith.md` | 301,305 | `source/projects/faith-index.html` | `window.CODEX_DATA` JS object |
| `fracture.md` | 87,815 | `source/projects/noble-father-fracture.html` | static HTML |
| `fractal.md` | 74,682 | `source/projects/noble-father-fractal.html` | `const DATA` JS object |
| `feminine.md` | 52,175 | `source/projects/noble-father-sovereign.html` | static HTML |
| `children.md` | 47,128 | `source/projects/noble-father-playground.html` | static HTML |
| `loop.md` | 25,727 | `fixes/loop.html` | `BODIES[n]` template literals |
| `scale.md` | 18,781 | `fixes/scale.html` | `BODIES[n]` template literals |
| `playbook.md` | 11,387 | `content/prose/_raw/playbook.html` (fetched live — no git source exists) | `COMPENDIUM` JSON array |
| `shadowroot.md` | 340 | `source/projects/noble-father-root.html` | state-machine prompts |
| `music.md` | 46 | `content/prose/_raw/music.html` (fetched live — no git source exists) | static HTML |

**870,360 words total.** `ALL-BOOKS.md` is every file above concatenated
into one document.

## How `faith.md` got solved

The Coercive Control Codex's 27 traditions weren't in static HTML or a
cleanly-named data object like every other book. The renderer functions
all referenced `D.religions`, but `D` itself wasn't assigned at any
`const D=`/`var D=` I could find by searching directly — because it isn't
one. Tracing every reference back by hand (not guessing) turned up
`const D = window.CODEX_DATA;` — a plain alias to a genuine global assigned
much earlier in the file: `window.CODEX_DATA = {"religions": [...], ...}`,
a clean, complete JSON object once you know where to look. It holds all 27
traditions (opening, overview, origin, authority, money, exit, timeline,
demographics, and ~20 more fields each) plus the book's ~60-field shared
framework (tactics catalogue, red flags, exit procedure, glossary, and the
rest of the apparatus applied identically across all 27). All of it is in
`faith.md` now, nothing summarized or left out — verified against the
6 raw occurrences of the word "undefined" in the output, all of which
turned out to be the book's own prose discussing doctrinal ambiguity, not
extraction artifacts.

## Two files have no git-tracked source at all

`playbook` (The Pattern Decoder) and `music` (The Listening Room) were
never checked into this repo — `sites.json` has always recorded their
`localSource` as none. Both were fetched live from
`noblefathercreations.com/playbook` and `/music` and saved to
`content/prose/_raw/` specifically so this extraction has a reproducible
input; that raw HTML is a mirror of what's currently live, not a source of
truth the way the git-tracked books are — if either project changes, these
go stale until re-fetched.

## `shadowroot.md` and `music.md` are short on purpose

The Root is an 18-step guided practice moved through once, not browsed
like chapters — its real content is short prompts, not long-form prose.
The Listening Room is a music page; the only text on it is framing copy,
not "chapters." Both extracted everything that exists; neither is missing
content the way `faith.md` is.
