# Noble Father Creations — Standing Rules

**Read `MEMORY.md` first, every session** — it's the actual cross-session
memory in this environment (a fresh container has no access to anything
outside this repo, so plugin-based memory tools don't carry over between
sessions here; this file does). Then `BOOKS.md` for what's actually built
into each book (content, theme, design stance, per-book reference-site
plan — the single file to hand another AI for "what's in each book").
Then `PROJECT-MASTER.md` for full context/history, `sites.json` for the
live project registry, and `chapters.json` for raw chapter data. This file
is the always-on rulebook — treat it as binding, not a suggestion. Update
`MEMORY.md` and `BOOKS.md` as work happens.

**Never apply a design pattern uniformly across all 9 books.** Check each
book's own content/stance first — several make deliberate anti-pattern
choices that are part of their argument (see `BOOKS.md` — Loop and faith
explicitly refuse gamification/tracking; children's book Playground
Protectors is the opposite case and *wants* gamification; Root is a guided
practice, not a chapter book). Read before pasting, every time.

## Self-contained architecture (non-negotiable)

Every book is: no dependencies, no external requests, no storage, fully
offline-capable — including THE HOUSE nav tab. Never add a CDN `<script>` or
`<link>` tag. Always inline:
- Fonts → self-hosted `@font-face` (see `tools/fonts/`), subset/base64 as needed.
- Icons → inline SVG (see `tools/lucide-icons-lucide/icons/`), never an icon font.
- Animation → copy CSS keyframes from `tools/animate-css-animate.css/` piecemeal;
  scroll fades use native `IntersectionObserver`, no library.
- Reading typography → Tufte CSS principles (`tools/edwardtufte-tufte-css/`).

## Design standard

Target: press.stripe.com (typography + a title/cover moment per book),
aeon.co (reading-progress bar, ~60–70 char measure), waitbutwhy.com /
The Marginalian (a real chapter-index page, a resources hub). Confirm/replace
these references with the user's own if named later.

Rules: generous whitespace, max 2 fonts with a dramatic scale, one restrained
accent only, strict 8px spacing grid, subtle micro-interactions (0.2–0.3s
hover/scroll easing). Iterate in passes — structure, type, space, motion,
then a self-critique pass ("what would a $100k agency art director cut?").
Preserve the dark theme, MOVEMENT labels, numbered chapter cards, and THE
HOUSE tab across every book.

## Book system architecture

`chapters.json` is the single source of truth (project, movement, n, title,
blurb, readMin, slug, url). Generate from it, never hand-maintain per page:
the chapter-index/contents page, Prev/Next nav, reading-progress bar, and
THE HOUSE cross-project map.

## Channel routing

- Books → warm, curious, value-first voice.
- Craft/business (NFC wax seals, candles, resin) → visual, premium,
  product-focused voice.
- Music → mood, behind-the-scenes voice.
Tag content by category at creation; never manage channels by hand.

## Clip pipeline (long video → many posts)

Input: timestamped transcript. Output: 30–50 clips (15–90s), each with
start/end time, hook title, category, virality score, caption, 5 hashtags.
Then: Claude writes an FFmpeg batch script to cut + crop to 9:16; Whisper
auto-captions; category tag routes each clip to its channel. Always surface
the top 5–10 "post first" clips. Free/open-source stack only.

## Outreach system

Loop: Analyze (core value, ideal audience, hook) → Find (~20 real targets)
→ Draft (personalized, <150 words, leads with value to *their* audience) →
Track (`outreach-tracker.csv`). **Human-in-the-loop is mandatory** — never
auto-send. Frame: "I made something free that will genuinely help the
people you serve," not self-promotion.

## Deploy hygiene

- Repo is the source of truth wherever a repo exists (currently only `wook`
  — this repo). Live must always match it.
- Never ship build-instruction comments or `#REPLACE`/`data-here`-style
  placeholders to a live page — see `sites.json` → `houseTabLeak` for
  current leak status per project, and `fixes/` for verified corrected HTML
  awaiting redeploy.
- Most projects (loop, scale, faith, playbook, etc.) are Netlify CLI/API
  deploys with **no connected GitHub repo** — confirmed via deploy metadata
  (`commit_ref: null`). A git push cannot fix them; they need a direct
  Netlify redeploy. Treat any such redeploy as a production write requiring
  explicit user go-ahead, same as any other environment-wide change.
- **Only deploy a book when it's actually had a real pass this round** —
  fixed corruption, structural bugs, or a content gap closed. A book that
  still needs a big pass stays on its last deployed version; don't ship it
  just because the branch moved.

## A commit is not a deploy (non-negotiable)

Nearly every bad round on this project has had one shape: **the repo was
right, production was wrong, and nothing said so.** The music page was
rebuilt and sat undeployed while the live one threw on load. The Portals
torch fix was written, committed, and never shipped. The `/statues` rule
existed here while ten links 404'd out there. The Fracture rename was done
in source and stale on eleven live sites. On 2026-08-13 the reverse also
happened — a container reset silently rolled the repo back behind live, so
the next deploy would have *undone* five shipped fixes.

None were hard problems. They were the same invisible one: deploying is a
separate manual act that leaves no receipt, so "fixed" and "shipped" drift
apart quietly and a reader finds out first.

```sh
node scripts/verify-deployed.mjs          # every project
node scripts/verify-deployed.mjs music    # one, by slug
```

It fetches what is actually being served and compares it byte-for-byte to
the `localSource` recorded in `sites.json`. Rules:

1. **Never say a fix is done because it is committed.** It is done when
   `verify-deployed` says that project is in sync. "Committed", "pushed"
   and "live" are three different states and only the third one counts.
2. **Run it at the start of a session too**, not just after deploying —
   that is what catches drift the other way, where live is ahead of the
   repo and a routine deploy would silently regress production.
3. **Drift is never resolved by editing the file until it matches.**
   Work out which side is correct first: ship the repo, or restore what is
   live into the repo. Guessing turns one wrong page into two.
4. `verify-live.mjs` asks "does the live page work?". This asks "is the
   live page the one we wrote?". Both, before calling a round finished.

New project? Give it a `localSource` in `sites.json` in the same breath, or
it is invisible to this check and gets to rot the old way.

## Patch notes & versioning (every deploy-worthy round)

Every site gets a simple version number (`v1`, `v2`, `v3`…, incrementing
once per deployed round of work — not once per commit) plus the date, so
anyone — us in a future session, or a reader coming back — can tell a new
update shipped and what it actually changed, without diffing HTML.

**Two places this lives, always kept in sync:**

1. **On the page itself**, reader-facing. Add a small, unobtrusive
   `<section id="updates">` (or fold it into the book's existing About/
   colophon section if it has one — Fractal, Fracture, and Faith all do)
   with a version badge (`v4 — 2026-08-05`) and a short reverse-chronological
   list of one-line, plain-language entries — no commit-message jargon,
   no internal file paths, just what changed for a reader ("Fixed several
   broken sentences and a missing chapter section," not "§9 sub-label glue
   bug, 4 instances"). This is a resources-hub-style destination
   (Wait-But-Why/Marginalian reference), not a nav tab — reachable, not
   prominent.
2. **`sites.json`**, machine-readable, per project: a `"version"` string
   and a `"changelog"` array of `{date, version, summary}` entries, newest
   first. This is the canonical ledger — when in doubt about what's live
   and when it last changed, read this before guessing.

**Workflow:** after a round of real fixes to a book and before/as part of
deploying it — bump `sites.json`'s version for that project, append a
changelog entry there, and add the matching on-page entry in the book's
own HTML. Both updates happen together, in the same commit, every time —
never let the ledger drift from what the page itself says.

## Tools available in this environment

- **Playwright + Chromium are pre-installed** (`/opt/pw-browsers/chromium`,
  `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`). **Never run `playwright
  install`.** Launch with `executablePath: '/opt/pw-browsers/chromium'`.
  Also available as an MCP server via `.mcp.json` (`@playwright/mcp`) for
  tool-based browser control instead of writing raw scripts.
- **Visual verification pattern** (screenshot at 375px + 1440px, check for
  console errors via a `pageerror` listener, check
  `document.documentElement.scrollWidth > innerWidth + 1` for horizontal
  overflow, check nothing is stuck at `opacity:0` after scroll, re-check
  under `reducedMotion:'reduce'`) — run this before claiming any visual
  change is "verified." Don't describe a screenshot that wasn't actually
  read.
- **Skills in `.claude/skills/`**: `impeccable` (real design/UX skill, 23
  sub-commands — `/impeccable <command> <target>`), `grill-me` (stateless
  planning interview, `/grill-me`), `ponytail` + `ponytail-review` +
  `ponytail-audit` + `ponytail-help` + `ponytail-debt` + `ponytail-gain`
  (over-engineering/bloat detection and prevention) — see
  `.claude/skills/README.md` for what each does and any caveats.
- **Subagents in `.claude/agents/`**: 16 of them, design/UX/writing/code
  review plus impeccable's support crew — see `.claude/agents/README.md`.
- **MCP servers in `.mcp.json`**: `playwright` (browser automation),
  `higgsfield` (image/video gen — needs your own API key, currently a
  placeholder).
- **`garrytan/gastown` is declined**, same reasons as gstack — background
  daemon (Docker container running indefinitely), OpenTelemetry
  architecture, dashboard, multi-repo hook installer. Do not install.

## Agent dispatch discipline (non-negotiable)

No tool exists to check remaining API/session capacity before dispatching
a background agent — confirmed via `ToolSearch`, not assumed. Firing
several agents in parallel has twice this project killed the whole batch
within seconds on a session-wide usage cap, wasting the dispatch and
returning zero output. Throttling dispatch is therefore the only
available lever:

1. **Dispatch one background agent at a time, by default.** Wait for it
   to actually report back (success or failure) before sending the next
   — not just "launched successfully," the real completion.
2. **If a batch is genuinely independent and the user wants speed,** cap
   parallel dispatch at 2, and stagger the sends rather than firing them
   in the same message.
3. **On a session/rate-limit failure:** stop dispatching immediately.
   Do not retry the failed one, and do not send the rest of a planned
   batch "anyway." Check for a reset time in the error; if one is given,
   schedule a single follow-up (`send_later`/`ScheduleWakeup`) for after
   it rather than polling. When capacity returns, resume one at a time,
   not as a fresh mass batch.
4. **A canary before a batch:** when several agents are queued up and
   capacity is uncertain (e.g. right after a prior rate-limit hit), send
   one first and confirm it completes before releasing the rest.

## Safety rules

1. Inspect any third-party repo before installing — report what it does,
   whether it adds hooks/daemons/telemetry/remote-sync, whether it installs
   persistently into `~/.claude/`.
2. Never install telemetry, background daemons, remote "brain" sync, or
   curl-to-shell installers without explicit yes.
3. One-off/scoped/readable commands: just run them. Environment-wide,
   persistent, or production-writing actions: ask first.
4. Stay scoped to the current repo unless global installs/deploys are
   explicitly approved.
5. `garrytan/gstack` is declined, permanently, for this project — telemetry,
   daemons, multi-host auto-registration, curl-to-shell installer.
