# Design bootstrap — read this before any visual work

Paste or attach this at the start of a Claude Code session working on Shae
Stovell's Noble Father Creations projects. It tells you what is installed, how
to activate it, and the standing instructions already agreed with the user.

---

## 0 · Standing instruction (agreed, do not re-ask)

The user has asked three times for maximal work and been given minimal work
twice. **Default to the maximal build.** Specifically:

- **Compositional rebuild, not restyling.** Re-emit the presentation DOM around
  one spatial idea. Do not layer CSS over untouched bones and call it a rebuild.
- **Full arsenal every time** — signature interaction, scroll-driven scenes,
  typographic motion, variable font axes, view transitions, pointer response.
- **Mobile is the primary target**, never the fallback. Their traffic is TikTok.
  Every hover effect needs a touch or tilt equivalent or it does not exist for
  their actual audience.
- **Never ask permission for depth.** Ask only when the answer changes *what*
  gets built, never *how far* it goes.
- **Content and interactive logic are frozen** unless explicitly told otherwise.
  Rewrite presentation generators; never touch prose, data, or engines.

---

## 1 · Installed skills

Invoke with the Skill tool. Global skills work anywhere; project skills only in
this repo.

### Global (`~/.claude/skills/`)
| Skill | Use for |
|---|---|
| `impeccable` | The primary art-direction system. See §2. |
| `emil-design-eng` | UI polish philosophy, component design, invisible details |

### Project (`.agents/skills/`, symlinked to `.claude/skills/`)
| Skill | Use for |
|---|---|
| `redesign-existing-projects` | **Most relevant here.** Upgrading existing sites without breaking function |
| `high-end-visual-design` | Fonts, spacing, shadows, card structures that read expensive |
| `design-taste-frontend` | Anti-generic landing pages; v1 kept as `design-taste-frontend-v1` |
| `gpt-taste` | GSAP motion: scroll pinning, stacking, scrubbing, editorial type |
| `minimalist-ui` | Clean editorial, warm monochrome, no gradients |
| `industrial-brutalist-ui` | Swiss print + military terminal, rigid grids |
| `stitch-design-taste` | Emits a `DESIGN.md` spec for another agent to follow |
| `brandkit` | Brand boards, logo systems, identity decks |
| `imagegen-frontend-web` | One reference image **per section** of a page |
| `imagegen-frontend-mobile` | App screens in phone mockups |
| `image-to-code` | Generate design image first, then build to match it |
| `full-output-enforcement` | **Use on the large single-file books.** Bans `// rest unchanged` truncation |

Verify with `ls ~/.claude/skills .agents/skills`. `skills-lock.json` records
sources and hashes.

---

## 2 · Activating impeccable correctly

```
Skill(skill="impeccable", args="<what you are doing>")
```

Then follow its setup, which is mandatory and in this order:

1. Run `node /root/.claude/skills/impeccable/scripts/context.mjs --target <path>`
   **once per session.** Keep cwd at the project root.
2. Load the reference for the sub-command that owns the request
   (`reference/polish.md`, `reference/bolder.md`, …) or `reference/new-work.md`
   for a new surface.
3. Load `reference/craft-floor.md` **immediately before editing UI** — it
   carries the quality floor and the absolute bans.

Sub-commands: `critique · audit · polish · bolder · quieter · distill · harden ·
onboard · animate · colorize · typeset · layout · delight · overdrive · clarify ·
adapt · optimize · shape · extract · document · live`

**Mechanical detector**, run once when the UI is finished, never mid-design:
```
node /root/.claude/skills/impeccable/scripts/detect.mjs --json <files>
```
It times out on files over ~3MB. That is a tool limit, not a defect — say so
rather than reporting a failure.

**Known-deliberate detector findings on this project** (do not "fix" these):
Fraunces is the pinned brand face; candle glows are literal light sources in
the world; em-dashes are the author's voice; the gilt gradient text is the
existing gold-leaf identity.

---

## 3 · Verification — Playwright

Chromium is pre-installed. **Never run `playwright install`.**

```js
const { chromium } = require('playwright');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
```
Run with `NODE_PATH=$(npm root -g) node - <<'EOF' … EOF`.

**Serve before testing.** Start `python3 -m http.server <port>` from the build
directory in the background. It dies between turns — restart it, and note that
`cd` inside a compound command can silently leave you in the wrong directory
(this caused two false "no changes" results in the original session).

### The standard check, every time
- Screenshot at **375px and 1440px**, then *actually read the screenshots*
- `pageerror` listener — zero console errors
- `document.documentElement.scrollWidth > innerWidth + 1` — no horizontal scroll
- **Nothing left invisible**: query for elements still at `opacity: 0` or a
  non-zero `stroke-dashoffset` after scrolling past them
- Re-check under `reducedMotion: 'reduce'`

### Three bugs this catches, all of which happened here
1. **Reveal engines that hide content permanently.** Always make the drawn or
   visible state the *default* and animation opt-in. Add a scroll sweep that
   force-reveals anything scrolled past.
2. **SPA re-renders orphaning your JS.** Hash-routed documents swap their
   container on every route. Init must re-run via `MutationObserver` on the app
   container plus a `hashchange` listener — not once at load.
3. **Light themes.** Several of these files have a parchment theme as well as
   a dark one. Derive colours from the page's own tokens with `color-mix`,
   never hardcode near-white text.

---

## 4 · Deployment

Netlify, via CLI with `NETLIFY_AUTH_TOKEN` in the environment only — never
written to a file, never committed.

```
export NETLIFY_AUTH_TOKEN='<token>'
npx -y netlify-cli@latest deploy --prod --dir <folder> --site <site-id> --no-build
```

The Netlify MCP `deploy-site` tool routes through `netlify-mcp.netlify.app`,
which returns 404 from this sandbox. Use the CLI with a token instead.

Site map (slug → Netlify site): root→nobleshadows, portals→nfcportals,
divide→thenobledivide, reaction-map→noblereactionmap, sovereign→sovereign-woman,
seals→noblenfcseals, fracture→fractures, playground→playgroundprotector,
fractal→thefractal, festival→wook-in-sheeps-clothing, hub→noblefathercreations.

**These URLs are embedded in sold NFC chips. They must never break.**

---

## 5 · The build pattern that works here

Every project page is one large self-contained HTML file. Do **not** hand-edit
them. The working pattern:

1. Write a Python transform in `scripts/` that takes pristine HTML and returns
   modified HTML. Give it a `MARK` constant and return early if already applied.
2. Rewrite **presentation generators only** — the functions that emit markup.
   Leave data, routing, search, filtering and engines untouched.
3. Wire it into `scripts/rebuild.py`, which rebuilds `site/` and `standalone/`
   from pristine sources every run. Idempotent and reversible.
4. Verify, then commit that pass alone.

Existing transforms: `nf_chrome.py` (site-wide chrome), `nf_hub.py`,
`nf_portals.py`, `nf_root.py`, `nf_divide.py`, `nf_playground.py`,
`nf_elevate.py`, and `faith_*.py`.

---

## 6 · Project rule sets — apply the right one

### The faith project (`faith/index.html`) — FOUR HARD RULES
This file is handed person-to-person, read offline, sometimes in countries that
filter traffic, by people who may be monitored at home.

| Rule | Meaning |
|---|---|
| **No network request, ever** | No CDN, no web font, no `@import`, no `fetch`, no external `<link>`. Inline or `data:` only |
| **No storage of any kind** | No `localStorage`, `sessionStorage`, IndexedDB, cookies, cache, beacons |
| **One file** | The distribution model is one person handing it to another |
| **No engagement mechanics** | It catalogues manipulation; it may not use any. No streaks, badges, autoplay, infinite scroll, urgency |

Also banned there: parallax, scroll-jacking, auto-advance, looping ambient
motion, cursor followers, confetti, typewriter text.

**Critically: do not inject the shared Noble Father chrome into this file.** It
adds a Google Fonts link and would break rule one.

Content is frozen — every sentence is sourced and legally reviewed.

Verify with:
```
occurrences of localStorage / sessionStorage / indexedDB / fetch( / @import /
sendBeacon / XMLHttpRequest / document.cookie   → must be 0
count of 'https://'  → must not increase (baseline 6)
still exactly one file
```

### Everything else
No restrictions. Full arsenal. The four rules above apply to the faith project
**only** — the user stated this explicitly.

---

## 7 · Patterns already built — reuse rather than reinvent

| Name | What it is | Where |
|---|---|---|
| Standing volumes | Book covers as physical objects: spine, page edges, gloss sweep, shelf rail, pooled shadow | `nf_hub.py` |
| The Light Line | Draggable rule wiping between paired day/night photos; pointer, arrow keys and segmented control all in sync | `nf_portals.py` |
| The torch | Cursor-following light revealing a second image only where it falls; drifts and answers tilt on touch | `nf_portals.py` |
| The plumb line | Descending progress rail with a weighted bob; ground darkens with depth | `nf_root.py` |
| The fog gate | Content behind weather — `inert` + `aria-hidden` so one audience genuinely cannot read it, collapsed so the other scrolls past | `nf_playground.py` |
| Three registers | Reference entries where each voice is set differently — observation, the other party's words, the reader's tool | `nf_divide.py` |
| The apex chain | Chain-of-custody diagram terminating in an open link where the data says no mechanism exists | `faith_apex.py` |
| The matrix instrument | 810-cell grid coloured by evidence grade, cross-hair, keyboard-navigable, live readout | `faith_matrix.py` |
| Openings | Covers parting, lights coming up, rooms rising from dark — once per session, reduced-motion inert | `nf_hub.py`, `nf_portals.py`, `nf_root.py` |

---

## 8 · Techniques in use — with the traps

- **View transitions** — `@view-transition { navigation: auto }`, shared element
  via `view-transition-name`. Disable any manual fade when native support exists.
- **Scroll-driven animation** — `animation-timeline: view() / scroll()`, always
  behind `@supports`, with an IntersectionObserver fallback.
- **`@property`** — **required** for any custom property you intend to animate.
  Unregistered properties jump between keyframes instead of interpolating. This
  bit twice: the torch position and the drift path.
- **Variable font axes** — Fraunces carries `SOFT` and `WONK`. Request them in a
  *supplementary* stylesheet after the page's own font link so a failure cannot
  cost the typeface. **Unverifiable in this sandbox — Google Fonts is blocked.**
- **`background-clip: text` cannot be letter-split.** Per-glyph compositing
  makes the text vanish. Animate it whole.
- **`color-mix` with page tokens** for anything that must survive a theme swap.
- **`prefers-reduced-motion`, `prefers-contrast`, `prefers-reduced-transparency`,
  `forced-colors`** — all four, every time.

---

## 9 · Reporting

State what was verified and how. If a check timed out, say so. If a pass is
incomplete, name exactly what is left and why. Do not describe a screenshot you
did not read. The user has correctly called out over-claiming before.
