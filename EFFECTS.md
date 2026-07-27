# Noble Father Creations — effects reference

Every visual and interaction effect added, what it does, and exactly where it
lives. Source of truth is `scripts/`; each entry names the file that emits it.

All motion is gated behind `prefers-reduced-motion` and degrades to a static
page. No content, copy, or interactive logic was altered on any page.

---

## Site-wide — every one of the 11 pages
*(`scripts/nf_chrome.py`)*

| Effect | What it does | Where |
|---|---|---|
| **The Catalogue seal** | Wax seal, bottom-right. Hover lifts + rotates it; press stamps it down. Idle ember pulse on a 7s loop. | Every page |
| **Catalogue panel** | Leather table-of-contents slides in. Gilt page-edge down the leading edge, dashed stitching inset, per-volume accent gem keyed to each book's own palette. Arrow keys move between rows, Escape closes. | Every page |
| **Ink veil** | Page arrivals rise out of darkness with a warm bloom lighting from below (420ms in / 180ms out). | Every page |
| **View transitions** | Real cross-document morphing where the browser supports it; the seal is a named shared element so it stays put while the page changes. Falls back to the veil elsewhere. | Every page |
| **Bookmark ribbon** | Brass strip across the top fills as you read. Runs natively on the compositor where `animation-timeline: scroll()` is supported. | Hub, Fracture, Festie, Playground, Reaction Map |
| **Scroll reveal** | Content eases up out of dark, blur-to-sharp, staggered. Oversized blocks excluded; a sweep fallback force-reveals anything scrolled past so nothing can ever stay hidden. | Hub, Fracture, Playground |
| **Letter split** | `data-nf-split` splits a headline into characters with a staggered rise + 3D tilt. | Hub, Portals |
| **Count-up numerals** | `data-nf-count` counts a number up on first view, cubic ease-out. | Hub colophon |
| **Gold-leaf sweep** | `.nf-leaf` travels a light gradient across gilt letterforms on a 7s loop. | Hub, Portals |
| **Fraunces variable axes** | Supplementary stylesheet requests the `SOFT` and `WONK` axes so letterforms soften and lean, not just change weight. Added *after* each page's own font link so a failure can't cost the typeface. | Hub, Portals |

---

## The Catalogue — the hub (`/`)
*(`scripts/nf_hub.py` — "The Study")*

**Compositional rebuild**, not styling. The presentation DOM was re-emitted.

| Effect | What it does |
|---|---|
| **Opening covers** | Two leather halves swing back off a lit gold seam on first arrival. Once per session (`sessionStorage`), skipped entirely under reduced motion. |
| **The room** | Hero is layered depth: brand plate hung as a back wall at natural aspect and masked into dark, warm glow, light beam, dust motes, double vignette. Each layer parallaxes at its own rate on scroll and the whole plate recedes. |
| **Reclaimed dead space** | The brand banner was a 479px full-width block pushing all content below the fold. Lifted out of flow and repurposed as the room's back wall. |
| **Drawn ring** | An engraved SVG ring draws itself (`stroke-dashoffset`) around the pressed seal, with a dashed inner tick ring fading in behind it. |
| **Standing volumes** | Every book is a physical object: bound spine catching light, cream page-edge block, specular candlelight sweep across the cover, brass shelf rail, shadow pooling beneath. Lifts and rotates toward the reader on approach. |
| **Chapter openings** | Outlined numeral in the margin, mono kicker, display title, brass rule. Titles are uncovered by a travelling light mask driven by native `animation-timeline: view()`. |
| **Variable-axis titles** | Volume titles animate `SOFT`/`WONK` on hover. |
| **Magnetic links** | `.st-vol-open` and `.st-enter` lean toward the pointer, release on leave. |
| **Corrected numbering** | Music and Support were both № 03. Support is now № 04. Volume numerals now come from the real NFC catalogue codes. |

---

## The Portals — `/portals`
*(`scripts/nf_portals.py` — "The Vitrine")*

**Compositional rebuild.** The two presentation generators (`reveal`, `panelHTML`)
were re-emitted; `SETS`, the image map, rotator navigation, drawer and night
switch are byte-for-byte unchanged.

| Effect | What it does |
|---|---|
| **The Light Line** | *The signature interaction.* A brass rule across each pendant with daylight on one side and the glowing photo on the other. Drag it to take the room dark. Arrives already half-revealed so the product's promise reads instantly. Driven by pointer drag, arrow keys, and the Daylight / Lights-out control — all three stay in sync, as does the global "Cut the lights" switch. |
| **The torch** | On pointer devices, a soft light follows the cursor and reveals the glow *only where it falls* — sweeping a torch over the piece in a dark room. Composes with the Light Line. |
| **Mobile torch** | No cursor to follow, so the light drifts on a 9s path of its own and answers device tilt where the browser offers a reading. Null orientation events are ignored so a bad reading can't pin the light. |
| **Registered properties** | `--tx`, `--ty`, `--tr` are declared with `@property` so the light interpolates smoothly instead of jumping between keyframes. |
| **Resin refraction** | SVG `feTurbulence` + `feDisplacementMap` bends light at the piece's edge while it's being handled. |
| **Pointer tilt** | Hero piece and thumbnails tilt with real perspective; suspended while the line is being dragged. |
| **The lamp cursor** | The arrow is replaced by a small warm light while over any pendant. |
| **Lights-up opening** | The shopfront comes up out of black on arrival, once per session. |
| **Standing presentation** | Piece on a lit plinth with shadow pooling; composition set as a jeweller's certificate (hairline rules, roman numerals); apex reveal in its own glow-washed band; four-up thumbnail grid; two-column enquiry with a primary gilt action. |
| **Per-set accent** | Each of the 17 sets drives its own glow colour through the kicker gem, layer numerals, rail tab and apex wash. |
| **Magnetic buttons** | Enquiry buttons lean toward the hand. |
| **Letter-split set names** | Set names re-letter themselves as each set slides in. |

---

## The Root — `/root`
*(`scripts/nf_root.py` — "The Descent")*

The practice is about following a reaction *down*; nothing on the page moved
downward. `shell()`, `renderRail()` and the record markup were re-emitted. The
branching engine, sixteen themes, storage layer and step graph are untouched.

| Effect | What it does |
|---|---|
| **The plumb line** | The progress rail is a rope descending, with a brass **bob** — a weighted sphere — marking your current depth. Branch steps show as sage nodes. The bob drops in with a slight overshoot on each step. |
| **Depth darkening** | `--rt-depth` is set from how far into the thread you are; the page ground darkens and the candle glow narrows as you descend. |
| **Rising questions** | Each new step rises past you from below, blur-to-sharp. |
| **Mobile depth gauge** | The row of dots became a measured gauge with a lit bob at the current position. |
| **Margin-note insights** | Insights are no longer a slab with a thick coloured bar — they're set as an italic margin note with a hairline and a small brass diamond, colour-keyed (candle / sage / violet). |
| **Tactile answers** | Option pills lift and glow on hover, compress on press. |
| **The record** | The final record is a leaf of aged paper with a gold hairline at the head and a wax seal pressed into the corner. |

---

## The Divide — `/divide`
*(`scripts/nf_divide.py` — "The Codex")*

`secHead`, `relEntryHTML` and `box` were re-emitted. Data, routing, search,
filtering, grading and case linking untouched.

| Effect | What it does |
|---|---|
| **Three registers** | *The important one.* Every tactic entry carries three passages that were previously set identically. They are now three distinct voices: **how it appears** (evidentiary, gilt rule, hanging marks), **the defense you will hear** (quoted, italic, deliberately de-emphasised — it's the abuser's mouth), **the counter** (boxed, bolded, highest contrast on the plate — it's the reader's weapon). |
| **Codex plates** | Entries became numbered plates with a chevron that rotates on open and an unfurl animation on the body. |
| **Evidence stamps** | Grade badges struck as mono stamps; "Sourced" tier carries the sage accent. |
| **Theme-safe colour** | Every colour derives from the page's own `--gilt` / `--ink` tokens via `color-mix`, so the plate holds in both the parchment and the ink theme. Contrast verified in both. |
| **Chapter openings** | Section heads gained a gilt rule and balanced display titles. |

---

## Playground Protectors — `/playground`
*(`scripts/nf_playground.py`)*

| Effect | What it does |
|---|---|
| **The grown-up fog** | *The signature mechanic.* Passages written **about** children rather than **to** them are sealed behind drifting cloud. The block also collapses to 280px so a child flicks past it in one scroll. While fogged the content is `inert` **and** `aria-hidden` — a child genuinely cannot read it, by eye or by screen reader. A grown-up taps the chip once and it clears, remembered for the session. Applies to "To the grown-ups" and the parents' tip section. |
| **Power-up bursts** | `POWER-UP!` scales in with a slight over-rotate, and a conic starburst of rays fires outward once behind it. |
| **Comic panel landings** | Panels, power-ups, cards and plates rise and settle as they come into view, staggered in threes. A scroll sweep guarantees nothing stays invisible. |
| **Springing speech bubbles** | Say-bubbles pop from 82% scale on entry. |
| **Sliding moves** | Move cards slide in from the left, staggered. |
| **Letter-by-letter titles** | Mission headings arrive a character at a time with a small rotation. |
| **Weather per world** | Each of the four worlds carries seven drifting coloured orbs on independent 20–40s paths — world 1 mint, 2 tangerine, 3 sky, 4 grape — so the book changes climate as you move through it. |
| **Confetti on lighting a mission** | A `MutationObserver` watches the book's own bulbs; when one lights, it pops with an overshoot and throws 26 pieces of real confetti in the book's six brand colours. |
| **Springy map chips** | Mission chips on the adventure map lift and tilt on hover, compress on tap. |

---

## Deliberate exceptions

- **The gilt line is not letter-split.** `background-clip: text` does not survive
  per-glyph compositing — the words vanish. It rises whole with the shimmer instead.
- **Fraunces, candle glows, em-dashes** flag on the design detector and are all
  intentional: the pinned brand face, literal light sources in the world, and the
  author's own voice.
- **No canvas or WebGL.** These are 2–10MB single files read mostly on phones from
  TikTok. Everything above is transform/opacity/filter work that stays on the GPU.

## Verified

All 11 pages at 375px and 1440px: no console errors, no horizontal scroll,
navigation intact, no element left invisible after scroll. The Divide's plate
contrast checked in both light and dark themes.

## Not verifiable in this environment

- **Google Fonts is blocked here**, so the Fraunces `SOFT`/`WONK` axis animation
  has never been seen rendering. It degrades to nothing if the axes fail to load.
- **Device tilt** on the Portals needs a real phone.
