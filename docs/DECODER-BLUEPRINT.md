# The Pattern Decoder: design and architecture blueprint

The complete picture of what the Pattern Decoder is, how it looks, how it moves, how it is built and
why each choice was made. Current state: **v14, live since 2026-10-24** at
https://noblefathercreations.com/playbook (Netlify site `noblepatterns`). The content itself is in
`docs/DECODER-CODEX.md`. This file describes the product, the design system and the engineering.

---

## 1. What it is, for whom, and the rules it never breaks

**Product.** A free guide to 310 manipulation and control tactics. A reader can search by what
happened, answer two questions, browse ten groups or explore a star map. Every entry helps them check
whether it really fits and what to do.

**Reader.** Someone who is hurting and unsure. They may be tired, frightened or reading in secret, and
they need plain words, a safe way out and nothing that judges them. Every design decision is weighed
against that reader.

**Design principles (in priority order)**
1. Safety and accuracy before beauty. Safety-sensitive entries (105) lead with their safety note. The
   guide never claims to read intent, diagnose or give a verdict. No invented metrics, scores or ratings.
2. Plain words. Labels say what a thing is ("Help me figure it out", "Use this safely"), sentence
   case, no jargon. The reading voice is warm and calm.
3. One world. An observatory at night: every tactic is a star, every group a constellation, and
   moving through the guide is moving through the sky.
4. Restraint with one memorable moment. The sky and the star-to-page morph are the spectacle;
   everything else is quiet, sharp and typographic.
5. Calm is always available. A Calm button and the system's reduced-motion setting stop all motion.

**Non-negotiable engineering rules (from the project's CLAUDE.md)**
- One self-contained HTML file. No CDN, no external fonts or scripts, works offline.
- The only outside request is the approved Cloudflare Web Analytics beacon (shared token).
- Fonts are embedded as base64 `@font-face`, icons are inline SVG, and motion is CSS or native APIs.
  No libraries.
- Every deployed round bumps the version on the page (the "What changed" list) and in `sites.json`
  in the same commit.
- A commit is not a deploy. Live is checked byte for byte against the repo (`npm run deployed`).

---

## 2. Files and build pipeline

| Path (Wookbook repo; mirrored in Books) | Role |
|---|---|
| `content/playbook-data.json` | Source data: entries, categories, recipes (patterns), aliases, guide mappings |
| `content/codex-final/*.json` | The rewritten 310 entries (batches + merged) and `reader-meta.json` (sub-names, settings, sensitivity, script kind, related, popularity) |
| `content/codex-final/source-data-349.json` | Frozen copy of the 349 source tactics; never edit |
| `design/validate-codex-final.py` | Content validator (field shapes, banned phrasing, shared-sentence and boilerplate checks, safety rules); `--complete` for the full set |
| `design/build-decoder-v10.py` | **The build.** Merges data and meta, lays out the sky, embeds fonts and assets, writes the page |
| `design/decoder-v10/shell.html` | Page skeleton: header, canvas, layers, tab bar, dialogs, placeholders `{{FONTS}} {{CSS}} {{DATA}} {{JS}} {{HOUSE}} {{BEACON}}` |
| `design/decoder-v10/app.css` | All styles. Base system, then layered blocks: v13 couture, v14 grimoire (later blocks override earlier ones) |
| `design/decoder-v10/app.js` | Router, views, search, guide, command menu, private reading, pause, reveals, morph |
| `design/decoder-v10/sky.js` | The canvas sky engine, injected into app.js at `//@@SKY@@` |
| `design/decoder-v10/font/build-astra.py` | Draws the Astra typeface from skeleton strokes (fontTools) → Thin/Light/Medium woff2 |
| `design/decoder-v10/assets/` | `astra-{thin,light,medium}.woff2`, `inter-var.woff2` (subset), `cormorant-italic.woff2` (+ OFL), logo, House menu, beacon |
| `content/prose/_raw/playbook-v10.html` | **The built, deployed page** (Books: `instruments/playbook/index.html`, identical) |
| `design/export-decoder-codex.py` | Writes `docs/DECODER-CODEX.md` from the deployed page |

**Build:** `python3 design/build-decoder-v10.py` → about 3.7 MB single file.
**Deploy:** stage a folder containing only `index.html` (a copy of the built page), then run the Netlify
MCP `deploy-site` for site id `8b3d5fdf-49e5-46eb-bb53-97d69039a44e`. Verify with `npm run deployed`
and a curl md5 of both URLs.
**Embedded data** (`<script type="application/json" id="data">`): `entries, groups, settings, recipes,
aliases, narrow, feelings, feelingGroups, sky{land,port}, stop, common, glossary, tries, catToGroup,
cover, wordmark, version, updates`.
**Entry record:** `n` name, `s` slug, `g` group, `w` settings[], `sub` short sub-name, `abs` other names,
`rel` related, `sens` safety-sensitive, `pop` popularity, `kind` script kind (`say`/`self`/`verify`),
`kw` keywords, and `f`, the 24 written fields listed in the codex.

---

## 3. Information architecture and navigation

**Routes (hash-based, all offline):**
`#/` home · `#/sky` explorable sky · `#/browse` · `#/browse/<group>` constellation · `#/entry/<slug>`
· `#/guide` two-question guide · `#/search` full results · `#/common` · `#/all` A–Z · `#/where/<setting>`
· `#/patterns` and `#/patterns/<slug>` · `#/saved` · `#/about` (Use this safely).
Old v9 routes and merged names redirect to the right place.

**Ways in, for someone who doesn't know what to look for**
1. The **command pill** (header centre, ⌘K / Ctrl K, `/`). It searches tactics, constellations and pages
   instantly, with recent reads first. Search matches everyday words and pasted phrases through
   stemming and a synonym map, and falls back to a fuzzy match.
2. **Help me figure it out:** pick where it happens, then which plain descriptions fit. Shows up to 18
   ranked entries and lights them in the sky.
3. **The most common** (24 entries), **Browse** (10 constellations, 7 settings), **A–Z**, and **patterns**.
4. **The sky:** click a star to open it, or click a constellation to fly into it.

**Wayfinding devices**
- **Header:** brand (left), command pill (centre), Help me figure it out, The sky, Browse, Saved, Use
  this safely, then Private, Calm and theme (right). Links collapse at narrower widths.
- **Constellation track** (left column of a group page) and **section track** (left column of an entry):
  numbered 01–05 with a sliding 2px indicator.
- **Pager** on entries: "12 / 23" within the constellation, previous and next, and the **J / K** keys.
- **Reading meridian:** a hairline at the right edge, ticked at each part, with a star at your place.
- **Phones:** a bottom bar with Home, Sky, **Search** (centre), Browse and Saved, plus a sticky chip bar
  for jumping between an entry's five parts.
- Every view sets a document title. Focus moves to the heading after navigation, and there is a skip link.

---

## 4. Layout system

**Wide screens (≥901px): one locked viewport.** The document never scrolls; panes scroll inside it.
- **Home:** one screen. Off-centre statement headline (left, ~9vw in), lede, a large command pill,
  "Try" phrases, three serif text links (Help me figure it out, The most common, Explore the sky), the
  ten constellations with their sigils, and a privacy line.
- **Constellation and entry: split 35 / 65.**
  - Left column: an instrument panel. A window onto the sky (camera centred there), the star's chart
    coordinates, breadcrumb, pager, Save / Share link / Print, and the track.
  - Right column: the reading page, which scrolls independently. Running head with sigil and "No. n
    of 310", then the giant off-centre title, then the bento.
- **Other pages** (search, A–Z, guide, patterns, saved, safety): one glass panel scrolling inside the
  viewport, with the footer at its end.
- **Sky page:** full-screen canvas with an overlaid title, constellation chips, zoom tools and a card for
  the picked star.

**Bento grid** (entries): 6 columns. Column gap clamp(18–36px), row gap clamp(22–56px). Tile spans:
6 (hero, safety, wide lists), 4 (what it is, words you could use), 3 (paired lists), 2 (side notes and
fact tiles), plus tall tiles. Alternate parts step in 7% from the left for asymmetry.
Tiles size themselves by their text: a short prose tile (<190 characters) is set as a large Cormorant
quote.

**Phones (≤900px): the page scrolls normally**, on purpose (address bar, tap-to-top, one-handed reach).
- Entries reorder into print order: sky, coordinates, breadcrumb, folio title, pager, actions, chip bar,
  then the parts.
- The bento becomes 2 tracks. Core reading is full width; short tiles and fact tiles pair at half width.
- Bottom bar: 56px plus the safe area, docked to the edge, sharp, 30px blur.

---

## 5. Colour

**Midnight (default)**

| Token | Value | Use |
|---|---|---|
| `--bg` | `#040508` | scorched-ink ground (plus nebular gradients) |
| `--ink` | `rgba(240,242,245,.95)` | silk body and title text |
| `--ink-2` / `--ink-3` | `.72` / `.50` alpha of the same | secondary / tertiary text |
| `--mint` | `rgba(200,215,210,.8)` | editorial voice: Cormorant labels, subtitles, quotes' marks |
| `--hair` / `--hair-hi` | `rgba(255,255,255,.12)` / `.40` | 0.5px hairline rings / focused ring |
| glass (tiles, panel) | `rgba(255,255,255,.005)` + `blur(40px) saturate(1.35)` | paper-thin sheets |
| `--glass-2` | `rgba(12,13,18,.86)` | dense glass for menus, command menu, bottom bar |
| `--ember` | `#FF9100` solar amber (+ glow `rgba(255,145,0,.28)`) | **the one alert colour**: safety only |
| `--star` | `#D9C59A` | read/saved stars, pressed Save |
| `--toward` / `--away` | `#9CD9BC` / `#AFB8E8` | "signs it might be this" / "probably something else" |

**Daylight:** `#FFFFFF` ground, `#0F0F11` ink, white glass at .42 to .62 with blur,
`--mint` `rgba(44,72,64,.9)`, ember `#B35500`, and dark stars and grain.
**Constellation lights** (each group's own colour, used for its nebula, its lines, its sigil, its
breadcrumb, the track indicator, the pointer aura and the tactic subtitle tints; deepened 40% toward
ink in Daylight):
truth `#9FB2FF` · pressure `#B9A6FF` · control `#86CFEA` · hook `#F0A6CF` · wear `#D7A8F2` · blame
`#D6DC8F` · people `#8FDCB8` · systems `#AFC2DA` · online `#7FE0DA` · society `#A6D99B`.
**Contrast:** every text colour measured ≥4.84:1 (tile labels 8.98 in Midnight, 4.98 in Daylight).

---

## 6. Typography

Three faces, each with one job:

| Face | Source | Use | Setting |
|---|---|---|---|
| **Astra** (original, drawn for this guide) | `font/build-astra.py`; monoline skeleton strokes with round caps; the dots of i, j and the full stop are four-point stars; Thin 100 / Light 300 / Medium 500; capitals, É and & added in v13 | Titles and display | Thin 100, uppercase, tracking .22em (entry and home titles), .18em elsewhere; entry title clamp(46–104px), home clamp(44–108px) |
| **Cormorant Garamond Italic** (OFL, subset, 300–500) | embedded | Editorial voice: quotes ("It can sound like"), sub-names, tile labels, breadcrumbs, section notes, running head, coordinates, counts, the three home links | 14–28px, silver-mint; quotes 21px; short tiles clamp(22–32px) |
| **Inter** variable (OFL, Latin subset) | embedded | All reading text and controls | Body 16.5–17px at **1.85** line height; lists 1.8; summaries 20–25px |

**Rules**
- **Hierarchy by scale contrast:** giant thin titles against 13–14px italic metadata.
- **Scannability:**
  - The first sentence of every explanation is bold (the answer comes first).
  - Long paragraphs are split into two-sentence pieces.
  - Each list item bolds its lead phrase, up to its first comma, colon or dash.
- **Widow control:** `text-wrap: pretty`, plus a non-breaking space between the last two words when
  they are short (≤18 characters together).
- **Auto-fit:** `fitText()` shrinks a headline only if its longest word overflows (minimum 22px). It
  measures with transitions off and masks unwrapped (the `.measuring` class).
- **Drop capital:** the first explanation of each entry opens with an Astra Thin initial 4.4em tall.

---

## 7. Shape, surface and texture

- **Geometry:** border-radius 0 on every element. Only stars, colour swatches, the logo and the shared
  House seal stay round.
- **Hairlines:** true 0.5px, drawn as `box-shadow: inset 0 0 0 .5px var(--edge)` with `border: 0`.
  Chromium renders `border:.5px` as 2 device pixels; the ring renders as 1. `--edge` is a registered
  `@property` colour, so hover and focus animate it.
- **Velvet ground:** `body::before` fixed layer with three soft radial nebulae over `#040508`.
- **Living grain:** `.veil::after` SVG fractal-noise tile translated by `steps(24)` over 1s (24 fps) on one
  composited layer. Static under Calm and reduced motion.
- **Vignette** (`.veil`) and a **pointer light** (`.lumen i`): a 900px radial glow tinted by the current
  constellation that follows the cursor. Moved by transform only.
- No drop shadows, except the soft glow under the safety tile and the amber badge.

---

## 8. The sky engine (`sky.js`)

- **Data:** 310 stars at deterministic positions from the build (`D.sky.land` for wide screens,
  `D.sky.port` for tall ones). Each has a radius from popularity, related-star edges inside each
  constellation, neighbours across constellations, pattern sequences, and group centres and radii.
- **Camera:** each route sets a target (`skyRoute()`). Wide on home, into the constellation on a group
  page, onto the star and its relatives on an entry, fitted to the lit results on search. Flights use an
  ease-in-out tween that pulls back slightly mid-flight.
- **Layers drawn each frame:**
  - Dust with slight parallax, and the tinted nebulae (one cached radial sprite, scaled).
  - The atlas graticule: declination arcs and hour meridians labelled in Cormorant, on the open sky only.
  - Constellation lines: faint lines cached per constellation at 3 zoom levels. The focused
    constellation's lines are vector, in its colour, and draw themselves in edge by edge over 1.7s.
  - Dashed links to related stars, and the pattern chain.
  - Stars: sprite glow plus core. Read and saved stars are gold, saved ones ringed, the ring pulse marks
    the current star.
  - Constellation names, and star labels on sharp plates, kept out from under the header.
- **Fluid magnetism** (fine pointers, open sky):
  - Every star sits on a damped spring (k .075, damping .84 per frame) and drifts ±1.5px.
  - Within 160px of the pointer it is pulled up to 26px toward it, hums slightly, brightens and swells.
  - The nearest few names appear as small labels.
  - Only constellations the pointer touches redraw their lines live.
- **Cosmic stagger:** after every camera move, stars light up outward from where it lands, 12ms apart
  (capped at 1.4s).
- **Interaction:**
  - Sky page: drag (with momentum), pinch, wheel, arrow keys between stars, Enter to open, Escape.
  - Home: click a star (10px hit) to open it; click elsewhere in a constellation to fly into it.
  - Hovering a constellation anywhere previews it in the sky; hovering a tactic lights its star.
- **Clipping:** in split views the sky fades out before the reading pane (`clipX`) and below the sky
  window (`clipY`).
- **Performance:**
  - Redraws only while something moves; nothing runs in a hidden tab.
  - Pixel ratio is capped at 1.5 on phones.
  - Adaptive lite mode drops decorative layers if frames stay slow (below ~25fps on computers, ~30fps
    on phones).
- **Calm and reduced motion:** no twinkle, drift, meteors, ripple, magnet or flights. The camera jumps.

---

## 9. Motion language

- **Easing:**
  - The spring `cubic-bezier(.16,1,.3,1)` for anything that arrives, expands or springs back.
  - `cubic-bezier(.25,.46,.45,.94)` for quick 160–200ms hover colour.
  - `cubic-bezier(.4,0,.6,1)` for exits.
- **Page hand-offs:** View Transitions API. The old page blurs out (320ms) and the new one rises from
  14px with a 12px blur (760ms). The sky, header, tab bar and rail never move.
- **Shared morphs:**
  - The tactic name you tap travels into the entry title (`title`).
  - The star, or tactic card, you choose unfolds into the entry's first tile (`morph`, 920ms).
- **Veil reveal:** headlines rise line by line from behind a clip-path mask while a 10px blur clears
  (1.1s, 110ms per line). Section titles reveal as they scroll into view.
- **Focus veil** (fine pointers): the tile under the pointer scales to 1.01 and its ring brightens to 40%
  white. The others drop to 0.38 opacity at 0.99 scale.
- **Press feedback:**
  - Buttons go to scale .98 (90ms) and spring back over 500ms.
  - A radial aura in the constellation's colour follows the pointer under the edge.
  - Hover adds a 0.35px red–blue split on the label.
- **Small moments:** the track bar glides (700ms), tiles rise into view, the header frosts after scrolling,
  and a rare shooting star crosses the open sky (every 9–23s).
- **The pause:** after about 20 minutes of active reading the sky dims and a quiet card offers a breath.

---

## 10. Components (by class)

- **Navigation:** `.top` header, `.pill` command pill and `.pal` command menu (dialog + combobox/listbox),
  `.tabs` phone bar, `.rail` constellation marks (sheet pages on wide screens).
- **Split view:** `.split`, `.pane-l` with `.sky-window`, `.cartouche` (chart coordinates), `.track` and
  `.ind`. `.pane-r` with `.folio` (`.running`, `.no`, `.title`, `.e-sub`), `.chipbar`, `.sec` and
  `.sec-h`, `.bento`, then `.meridian`.
- **Tiles:**
  - `.tile` in spans s2/s3/s4/s6, plus `.tall`.
  - Variants: `.hero` (summary), `.safe` (amber, safety), `.quote` (sounds like), `.tw`/`.aw` (signs
    either way), `.script` (words you could use, with Copy), `.fact` (small facts), `.initial` (drop
    cap).
  - Automatic classes: `.brief` (large quote) and `.pair` (half width on phones).
  - `.tac` tactic cards on constellation pages; the top 2 by popularity are larger.
- **Other:**
  - `.sigil`: each constellation's mark, from its 7 brightest stars joined by a minimum spanning tree.
    Used in the dock, track and running head, and as a group watermark.
  - `.ed-link`: serif text link on a 0.5px mint rule.
  - `.btn` (base, primary, ghost), `.chip`, `.pg` pager buttons, `.badge.safety`, `.term` and
    `.term-def` inline glossary, `.toast`, `.breath` pause card, `.priv-btn` Private switch.

---

## 11. Privacy, safety and care features

- **No account, no typed data sent anywhere.** Search runs in the page. Queries are never put in the
  address bar.
- **Saved and recent** live in `localStorage` (`fg_*` keys) unless Private is on.
- **Private reading:**
  - Turning it on moves every stored `fg_*` key into memory and deletes it from the device.
  - From then on nothing is written to localStorage, sessionStorage or cookies.
  - Navigation uses `history.replaceState`, so the browser history doesn't grow.
  - It ends on close or reload and has to be turned on again each visit.
  - The browser still records the site visit; the page says so and suggests a private window.
- **Safety-sensitive entries** put the safety note first and steer wording advice toward getting support
  safely. The "Use this safely" page states what the guide is and isn't, and where to get help.
- **Calm mode** and full reduced-motion support. Optional reading pause (can be turned off and back on).
- **Fairness:**
  - Every entry has "What it is not", ordinary explanations, "often mistaken for" and "Using this label
    fairly".
  - The guide asks readers not to use labels to attack, shame or expose anyone.

---

## 12. Accessibility

- Keyboard reaches everything in a logical order.
  - The command menu traps focus and restores it on close.
  - Entries support J/K; the sky supports arrows and Enter.
- Visible focus (1.5px outline), skip link, focus moved to the heading after navigation.
- Split headlines carry an `aria-label` with the full text; decorative layers are `aria-hidden`.
- Canvas content has a text equivalent: every star is an entry reachable through Browse and A–Z.
- All text colours ≥4.5:1; minimum text size 12px (controls) or 13–14px (Cormorant metadata).
- `prefers-reduced-motion`, `prefers-reduced-transparency` (solid panels) and `prefers-contrast: more`
  are all honoured.
- Print stylesheet: one entry, every part, no chrome.

---

## 13. Version history of the design

| Version | What it introduced |
|---|---|
| v9 | Every entry rewritten (310 entries; 39 merged names) |
| v10 | The night sky world (310 stars, 10 constellations, camera per page, Sky page), Calm mode, five-part entries, two-question guide |
| v10.2 | Astra typeface drawn for the guide; Apple-style restraint (typographic lists, no boxes); adaptive sky |
| v11 | Per-constellation colours, ⌘K command menu, constellation rail, J/K pager, word reveals, view-transition hand-offs, line draw-in, pointer starlight |
| v12 | Locked single viewport, 35/65 split with timeline track, bento glass tiles, Midnight/Daylight only, Inter at 1.75, bold leads, line-by-line veil, fluid-magnetism sky, centred command pill |
| v13 | Velvet ground and pointer light, silk text, amber alert, Astra Thin capitals, Cormorant italic, 1.85 leading and widow control, focus veil, star ripple, phone thumb pill, private reading, reading pause |
| v14 (live) | Sharp geometry, paper-thin glass, 24fps grain, folio layout with off-centre titles, sigils, atlas grid, chart coordinates, drop caps, reading meridian, star/card morph, fact tiles, phone print order, zero-trace private, Calm click bug fixed |

---

## 14. Known limits and open checks

See `sites.json` → `playbook.openItems` for the live list. In short:
- Smoothness on real devices: the test browser has no graphics card and ran at 35–42fps.
- Daylight and print not visually re-reviewed on v14.
- No pass with real screen readers yet.
- A clinical read of the safety notes, and a human read of the automatic bolding, are still advised.
- Astra lacks `+` and `%`.

**Lessons that shaped the code** (keep them):
1. Never put an attribute on `<html>` that a delegated `closest()` click handler listens for. It caused
   two bugs: Private toggling on every click, and Calm toggling on every empty-space click.
2. Reduced motion and Calm give every property a 1ms transition, so measure with transitions off.
3. Draw hairlines as inset rings, not 0.5px borders.
