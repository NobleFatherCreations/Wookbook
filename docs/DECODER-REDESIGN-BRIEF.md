# The Pattern Decoder: redesign brief

Three parts. **Part A** is the prompt to paste into another chat (attach `Pattern-Decoder-v14-complete.zip`
and this file). **Part B** is a first-pass analysis with measurements from the live build, so the other AI
starts from facts, not impressions. **Part C** is a prioritised set of improvement ideas. Everything concerns the
interface (layout, navigation, motion, visual system, performance), never the written content.

Measured on the live page, 2026-10-24: Chromium 141, 1440×900 and 390×844 (phone at 4× CPU slowdown).

---

## Part A. The prompt (copy from here)

```text
ROLE
You are a principal product designer and front-end engineer with a specialism in reading-heavy interfaces for
vulnerable users, and a track record of making dense reference products calm. You are reviewing a finished,
live product and proposing how to rebuild its interface from the ground up. You are not here to flatter it or to
defend past decisions.

THE PRODUCT
The Pattern Decoder (https://noblefathercreations.com/playbook) is a free, offline guide to 310 manipulation and
control tactics. Reader: someone who is hurting and unsure. They may be tired, frightened, reading in secret on a
phone, on a shared device, and may not know what to search for. Job: help them put a name to what is happening,
check honestly whether it fits, and find a safe next step. It is a reading aid, never a diagnosis or a verdict.

WHAT YOU HAVE
Attached: Pattern-Decoder-v14-complete.zip. Start with README.md, then docs/DECODER-BLUEPRINT.md (the full design
and architecture as built), docs/DECODER-CODEX.md (every entry, every field: the content), docs/PRODUCT.md,
and docs/DECODER-REDESIGN-BRIEF.md Parts B and C (a first-pass analysis with measurements: verify it, do not
trust it). deployed/index.html is the live page; open it in a browser and use it for real before you form a view.
design/decoder-v10/ holds the source (shell.html, app.css, app.js, sky.js). `python3 design/build-decoder-v10.py`
rebuilds the page byte for byte. verify/ holds the checks used before each release.

SCOPE
FROZEN, do not propose changes to: the written content, the 5-part data model, the 310 entries and their fields,
the safety framing, the single-file offline architecture (no CDN, no external requests, no frameworks, fonts
embedded; the one allowed outside request is the Cloudflare analytics beacon), the validation logic.
OPEN, challenge freely: layout, information architecture, navigation, wayfinding, visual system, typography
treatment, colour, motion, interaction, the role of the star map, mobile behaviour, accessibility, performance,
onboarding, empty and error states, and how the UI presents (not changes) the existing content.

THE OWNER'S STATED TASTE (context, not commandments)
Observatory-at-night world; sharp 0px geometry; paper-thin glass with 0.5px hairlines; scorched-ink ground with
24fps film grain; Astra (an original thin geometric display face) in tracked capitals; Cormorant italic for
quotes and labels; Inter body at 1.85; one alert colour (amber) reserved for safety; each constellation has its
own colour; locked single viewport on desktop. They asked for "haute-couture", "not generic SaaS". Where one of
these tastes works against the reader, say so plainly with evidence and offer an alternative that keeps the spirit.

KNOWN TRAPS (do not rediscover)
1. Never put an attribute on <html> that a delegated closest() click handler also matches: it caused two bugs.
2. Calm and reduced-motion give every property a 1ms transition: measure sizes with transitions off.
3. Chromium draws border:.5px as 2 device px; hairlines are inset box-shadow rings.
4. The stylesheet is five layered rounds of overrides (v10..v14); .h1 is defined six times. Treat it as debt.

METHOD (do all of it, in order)
1. USE IT. Complete these as the reader would, on a 390px phone and a 1440px desktop, timing yourself and
   counting taps: (a) "my partner keeps changing what happened" with no idea what to search; (b) find what a
   "silent treatment" is and read the whole entry; (c) compare two look-alike tactics; (d) leave quickly because
   someone walked in; (e) return the next day to something you read. Record where you hesitated, got lost or
   felt overloaded. Screenshot every state.
2. MEASURE. Re-run verify/ and add your own: load and interaction timing on a throttled phone, long tasks,
   battery/CPU cost of the always-moving layers, contrast, tap-target sizes, keyboard order, screen-reader
   announcements (use real VoiceOver/NVDA/TalkBack if you can; say so if you cannot), reading length per entry.
3. CRITIQUE. Use Nielsen's 10 heuristics, cognitive-load theory, WCAG 2.2 AA, and trauma-informed design
   principles (choice, control, predictability, no surprises, no pressure, easy exit). Give every finding a
   severity (blocker / major / minor), who it hurts, evidence, and effort to fix.
4. REIMAGINE. Propose the interface from a blank page, at three ambition levels: POLISH (change nothing
   structural), RESTRUCTURE (new layout and navigation, same visual world), REIMAGINE (a different primary
   metaphor if you think the observatory is the wrong spine; defend it). For each level give ASCII wireframes of
   home, a constellation page, an entry (desktop and phone), search, and the guide; a design-token set; a motion
   spec with a hard budget (what moves, when, why, and what is OFF by default); and a navigation model.
5. PROVE IT. For your recommended level, build or mock the one or two highest-risk interactions (for example the
   entry reading model, or the map-to-page transition) as a working prototype in a single HTML file, and show it
   beats the current one on the tasks in step 1.

RULES FOR YOUR ANSWER
- Evidence over opinion. Quote numbers, screenshots and file/line references. Mark anything unverified as such.
- No generic advice ("improve contrast", "add whitespace"). Every recommendation names the element, the change
  and the reason, and says what it costs.
- Do not invent metrics, scores or claims about readers. Do not weaken safety features to look cleaner.
- Honest trade-offs: for each major recommendation state what we lose.
- Prefer removing to adding. Cap the motion. A calm reader beats an impressed one.
- Keep it implementable: say how it maps onto the existing build (which files change, what can be reused).

DELIVERABLES (in this order, one document)
1. Verdict in 10 lines: what the interface gets right, what fails the reader, and the single biggest change.
2. Task-test log from step 1.
3. Findings table (severity, area, evidence, fix, effort).
4. Pros and cons of the current design (keep / cut / change).
5. The three-level proposals with wireframes, tokens, motion spec, navigation model.
6. Your recommended path, with a phased plan (what ships first and why), risks, and the decisions you need
   from the owner.
7. A test plan: visual regression at five breakpoints, axe-core, performance budget, real-device checks, and how
   to guard against regressions.
8. Targets: state measurable goals (for example time to first meaningful paint on a 4× throttled phone, taps to a
   first entry, total long-task time, taps to leave the site) and how each will be measured.

Begin by confirming what you were given and what you could not run. Then proceed.
```

---

## Part B. First-pass analysis

### What was measured

| Fact | Value |
|---|---|
| Page size, transferred (compressed) | 1.27 MB; 3.59 MB uncompressed, of which **90% is the embedded data** (3.2 MB JSON) |
| Fonts embedded | Astra ×3 (15 KB), Inter variable (59 KB), Cormorant italic (25 KB) = about 99 KB |
| Code | CSS 66 KB / 802 lines; app.js 86 KB; sky.js 31 KB |
| CSS layering | 33 selectors defined 3+ times; `.h1`, `.stage-h`, `.sky-h`: 6 times each; 49 `!important`; 24 media blocks |
| Desktop load | DOMContentLoaded 1.3 s; home headline visible 1.4 s; longest main-thread task 347 ms |
| Phone (4× CPU slowdown) | DOMContentLoaded 3.0 s; headline visible **3.4 s**; longest task **836 ms**; 1.1 s of long tasks in total |
| Memory / DOM | 13–14 MB heap; 455 nodes on home, 391 on an entry |
| An entry ("Gaslighting") | 29 tiles, about 1,730 words, **11.3 screens** tall on desktop, **16.5 screens** on a phone |
| Taps to a first entry | Home → constellation → entry = 2; Search = type + Enter; guide = 4+ |
| Contrast | Lowest measured text colour 4.98:1 (Daylight tile labels); every checked text colour passes AA in both themes |
| Always-running layers | Canvas sky (twinkle, magnet, meteors), pointer light, 24fps grain, reveal and ripple animations |

### Pros (keep)

1. **Fast and robust for what it is.** One 1.3 MB file, no network dependency, works offline, 13 MB of memory.
2. **A real concept with one real signature.** A sky where every tactic is a star is memorable and fits the
   subject. The star-to-page morph and the camera flights are the product's best moments.
3. **Care is built in.** Safety-first entries (105), Calm mode, Private reading that writes nothing, optional
   reading pause, honest "what it is not" language, no scores or verdicts.
4. **Disciplined typography for reading.** Inter at 1.85, bold first sentences, widow control, a 66-character
   measure, tabular figures. The reading blocks are easy on the eye.
5. **Strong accessibility baseline.** Keyboard reaches everything, focus is managed, command menu traps and restores
   focus, contrast passes, reduced motion and reduced transparency are honoured.
6. **Multiple ways in.** Search by everyday words, a two-question guide, browse, A–Z, "most common", sky.
7. **Coherent identity.** Constellation colours and sigils tie navigation, content and map together.
8. **Process safety nets.** 310/310 render checks, a byte-for-byte deploy checker, a documented blueprint.

### Cons (change)

| # | Problem | Why it matters to the reader | Severity | Effort |
|---|---|---|---|---|
| 1 | **An entry is a long scroll in disguise.** 29 tiles, 1,730 words, 11–16 screens. The bento looks scannable but reading order is still top to bottom, and every tile has similar visual weight. | The "30-second read" is only the first screen; a distressed reader meets 16 phone screens of lists. | Major | Medium |
| 2 | **The best path is the quietest control.** "Help me figure it out" is the most useful route for someone who does not know what to look for, yet v14 set it as a small italic link equal to two others. | The people who most need guidance are least likely to find it. | Major | Small |
| 3 | **No quick exit.** Nothing lets someone leave instantly and cleanly. Private mode is a switch, not an escape. | In a controlling relationship, being seen with this page can be dangerous. | Major (safety) | Small |
| 4 | **Too much moves at once.** Grain, pointer light, sky drift, magnet, meteors, veil reveals, ripple, morph, focus veil. Calm is opt-in, icon-only. | Contradicts "one memorable moment". Competes with reading, costs battery, and can be dysregulating for the audience. | Major | Small–Medium |
| 5 | **The sky is wallpaper on most pages.** Outside the Sky page and home it sits in a small window with names hidden. Star positions carry no meaning, and the chart coordinates (e.g. 14ʰ 24ᵐ +68.7°) are derived from layout, so they imply precision that is not there. | A map should answer questions ("what is near this?"). Decorative semantics in a safety guide risk mistrust. | Major | Medium |
| 6 | **Tracked thin capitals for long titles.** "STALKING & SURVEILLANCE (POST-SEPARATION)" at weight 100, 0.22em, uppercase loses word shape; fine for 12 characters, hard at 40. | Titles are the first thing a stressed reader decodes. | Major | Small |
| 7 | **Small italic labels.** Cormorant italic at 13–14px for tile labels, coordinates and counts has a small x-height. | Passes contrast but fails comfort on low-end phones and for older readers. | Minor–Major | Small |
| 8 | **Three type families and five layered CSS rounds.** v10–v14 overrides, `!important` everywhere, universal `*` radius rule. | Every new change risks regressions; it already caused the Calm bug and several overflow bugs. | Major (engineering) | Medium |
| 9 | **Everything is parsed up front.** 3.2 MB of JSON on the main thread: 347 ms desktop, 836 ms on a throttled phone, headline visible at 3.4 s. | The first seconds are the most anxious ones. | Major on low-end phones | Medium |
| 10 | **Navigation has two mental models.** Desktop: header links, command menu, left tracks, rail. Phone: bottom bar and chip bar. The command menu is invisible to touch users. | Learning cost, and "where am I in the guide?" has no persistent answer. | Major | Medium |
| 11 | **The guide has two questions and a list.** No reason is shown for each match, no way to refine, results are not compared. | A person who cannot name it needs help narrowing, not a flat list of 18. | Major | Medium |
| 12 | **Related tactics are prose, not comparison.** Close relatives are chips and a paragraph. | "Is it this or that?" is the hardest question; text is the weakest tool for it. | Major | Medium |
| 13 | **No onboarding for the metaphor.** Nothing tells a first-time reader what stars and constellations mean. | Metaphors that need guessing add load. | Minor | Small |
| 14 | **The locked desktop viewport has costs.** Scroll lives in an inner pane, so no page-level scroll restoration, no native "scroll to top", odd wheel behaviour near the pane edge. | Small friction for every long read. | Minor | Small |
| 15 | **Hidden state.** Private ends on reload; Saved is local only; no obvious way to see what is stored. | Surprise is the enemy for this audience. | Minor | Small |
| 16 | **No regression net in the repo.** The checks live in scratch scripts (now in the zip). | The next change can break what was just fixed. | Major (engineering) | Small |

---

## Part C. Ideas to improve it

Grouped by ambition. Ideas marked ★ are the ones I would do first.

### Polish (no structural change)

- ★ **Quick exit.** A persistent small control and an Escape-Escape shortcut that replaces the page with a neutral
  one and clears Private state.
- ★ **Restore the guide to prominence.** One filled primary action, "Help me figure it out", then search. Keep the
  serif links for the secondary routes.
- ★ **Sentence-case Astra for titles over about 20 characters**; keep thin capitals for short ones and section heads.
  Raise Cormorant labels to 16px.
- ★ **Motion budget.** Default on: sky drift, star-to-page morph, press feedback. Default off: meteors, grain,
  pointer light, ripple (offer "Atmosphere" as a switch). Auto-calm on low battery, low-end devices and
  `prefers-reduced-motion`.
- Label the coordinates as decorative or drop them; replace with something true (the star's constellation and
  how many tactics are near it).
- Keyboard map overlay on `?`; a visible Search affordance on phones' header.

### Restructure (new layout and navigation, same world)

- ★ **Answer-first entry with progressive depth.** The entry opens as one summary card (what it is, what it sounds
  like, safety). The other four parts become a segmented control or stepper with a progress marker, each part
  limited to about six blocks, long lists collapsed behind "show all". Target: first screen answers the question;
  full read is 4–5 screens, not 16.
- ★ **One navigation model on every size.** A persistent dock of five doors (Home, Search, Guide, Sky, Saved) plus
  Safety, with the command menu as an accelerator, not the primary route. A "path" breadcrumb that includes
  "Back to results".
- **Self-check, not verdict.** In "Is this it?", make the signs checkable. Ticking shows a plain "fits several /
  fits few" band with the caveat, stored nowhere. This reuses existing content, and is where a reader actually
  makes their decision.
- **Compare mode.** Pick two related tactics and show them in two aligned columns (what it is, sounds like, the
  difference). The data (`how_to_distinguish_from_related`, `rel`) already exists.
- **Guide as a conversation with reasons.** Three to four short steps, show "why this matched", allow undo, and
  end on a short list of three with a "see more".
- **Phone: a bottom sheet entry.** Tapping a star or card raises a sheet over the map instead of a new page, with
  detents (peek / half / full) so the reader never loses the map.
- **Reading preferences.** A single panel: text size, line spacing, tracking, font (Inter / system), contrast,
  motion. Persisted unless Private.

### Reimagine (a different spine)

- **Semantic-zoom atlas.** Make the map the primary UI, with real meaning: closeness = how often two tactics are
  confused (use `rel` and false-positive links), zoom level 1 shows ten constellations, level 2 tactic names, level
  3 one-line definitions, and the page opens in place. This turns decoration into the best discovery tool.
- **Situation threads.** Let a reader start from a situation ("I am being isolated") and walk a curated 4–5 tactic
  path that reuses the 109 patterns, shown as a timeline rather than a list.
- **A book mode.** Offer a linear, paginated reading mode (swipe through entries within a constellation) for those
  who want to read, not explore.

### Visual system and engineering

- ★ **Rewrite the CSS from tokens, once.** Semantic tokens (surface, text, line, accent, alert), one layer, no
  `!important`, components (Tile, Pill, Track, Sigil, Sheet). Expect about a 40% smaller stylesheet and no more
  override fights.
- ★ **Lazy-parse the data.** Store per-constellation JSON in `<script type="text/plain">` blocks and parse on demand
  (still one file, still offline). Cut the 347 ms (836 ms phone) startup task and the 3.4 s phone wait.
- Move the sky to an `OffscreenCanvas` worker where supported, so the main thread stays free for reading.
- `content-visibility: auto` on tiles; pause all ambient work when off-screen, hidden, or after idle.
- A small automated net in the repo: Playwright visual regression at five breakpoints, axe-core, a performance
  budget, and `verify-deployed.mjs` in CI.

### Suggested order

1. **Now (days):** quick exit; restore the guide's prominence; sentence-case long titles; motion budget; label
   size; coordinates fix; regression scripts into the repo.
2. **Next (weeks):** answer-first entry; one navigation model; lazy-parse; CSS rewrite from tokens; reading
   preferences; guide with reasons.
3. **Later:** self-check, compare mode, bottom-sheet phone model, semantic-zoom atlas, situation threads.

### Decisions needed from the owner

1. Is a calmer default (grain, meteors and pointer light off) acceptable, given the "haute-couture" brief?
2. May the entry become a stepper with collapsed lists, given the current "everything visible" bento?
3. Is the star map decoration, or navigation? The answer decides whether to invest in the semantic-zoom atlas.
4. Quick exit and Private by default: yes, no, or a first-run choice?

### Honest caveats

- Measurements are from a software-rendered browser. Real frame rates, battery use and screen-reader behaviour are
  not yet verified.
- No user testing has been done with the actual audience; every claim about readers above is a design hypothesis.
- Several v14 choices (submerged links, tracked capitals, grain, locked viewport) were direct owner requests. This
  analysis flags where they cost the reader; it does not override the owner.
