# Noble Father Creations — what changed, project by project

A review brief. Twelve HTML files, all self-contained, all openable straight
from disk by double-clicking. This document explains what each one was, what
was done to it, and what to look at.

**Ground rule observed throughout:** not one word of written content, and not
one line of interactive logic, was altered in any file. Every change is
presentation. Where a page had render functions that emit markup, those were
rewritten; the data, routing, search, filtering and engines were left alone.

---

## How to review these

Open each file directly in a browser. Two things will not reproduce in a
screenshot and need a real device:

1. **Motion.** Most of the work is in arrivals, transitions and interactions.
   Stills cannot show it.
2. **Typefaces.** These load Fraunces and other faces from Google Fonts. The
   environment they were built in blocked that, so they were never seen in the
   real typeface during development. On a normal connection they will look
   meaningfully finer than they did to the builder.

Check on a phone as well as a desktop. The primary audience arrives from
TikTok, so mobile is the intended experience, not a fallback.

---

## 1 · The Catalogue — `noble-father-catalogue.html`
*The hub. Compositional rebuild, codename "The Study".*

**Was:** a centred text hero over a gradient, then a uniform grid of book cards.
Critically, a 479px full-width brand banner sat above everything, so the first
half-screen a visitor met was empty dark.

**Now:**
- The banner was lifted out of the document flow and hung as the room's back
  wall, masked into shadow. That reclaimed the entire first screen.
- The hero is a room, not centred text — layered depth with a warm glow, a
  light beam, dust motes and a double vignette, each layer parallaxing at its
  own rate on scroll.
- **Every book is now a physical object**: bound spine catching light, cream
  page-edge block, a specular sweep across the cover, standing on a brass shelf
  rail with its shadow pooling beneath. Approach one and it lifts and rotates.
- Cards replaced by alternating rare-book catalogue entries — real catalogue
  numeral, hook in italic display, full description, spec tags, ruled link.
- Section heads became chapter openings: outlined numeral in the margin, mono
  kicker, display title, brass rule, uncovered by a travelling light.
- On arrival, two leather covers part off a lit gold seam. Once per session.
- An engraved ring draws itself around the pressed seal; the headline arrives a
  character at a time; the colophon numerals count up.

**Content correction found and applied:** Music and Support were both numbered
№ 03. Support is now № 04. Volume numerals now come from the real NFC
catalogue codes rather than a running count.

**Look at:** the first 1.5 seconds; the Library section on desktop.

---

## 2 · The Portals — `noble-father-portals.html`
*The commerce page. Compositional rebuild, codename "The Vitrine".*

This is the revenue page and got the most attention.

**Was:** every pendant photographed twice — once in daylight, once glowing —
and that pairing was buried behind a hover state most visitors would never
trigger. The product's entire promise was invisible.

**Now — the signature interaction, "the Light Line":**
A brass rule sits across each pendant with **daylight on one side and the
glowing photo on the other**. Drag it to take the room dark. It arrives already
half-revealed, so the duality reads in the first second with no instruction.
Driven by pointer drag, arrow keys, and a Daylight / Lights-out control — all
three stay in sync, as does the global "Cut the lights" switch.

**Also:**
- **The torch.** On pointer devices a soft light follows the cursor and reveals
  the glow *only where it falls* — sweeping a torch over the piece in a dark
  room. On phones there is no cursor, so the light drifts on its own path and
  answers device tilt where the browser offers a reading.
- Resin refraction — an SVG displacement filter bends light at the piece's edge
  while it is handled.
- The piece stands on a lit plinth with its shadow pooling.
- The composition is set as a jeweller's certificate: hairline rules, roman
  numerals, layer names in the display face.
- The apex reveal gets its own glow-washed band.
- Each of the 17 sets drives its own accent colour through kicker, numerals,
  rail tab and apex wash.
- Enquiry became a two-column close with a primary gilt action.

**Worth a decision:** there is no price anywhere on this page. "Enquire" is a
legitimate choice for one-of-one work, but if price bands would convert better
that is a small change.

**Look at:** drag the brass line across a pendant. That is the page.

---

## 3 · The Root — `noble-father-root.html`
*A guided shadow-work practice. Compositional rebuild, codename "The Descent".*

**Was:** the practice is about following one reaction *down* to the belief
underneath, and nothing on the page moved downward. Every one of its eighteen
steps used an identical card.

**Now — each step knows which step it is and looks like itself:**
- **A plumb line** descends beside the reader with a brass **bob** marking the
  current depth. Branch steps show as sage nodes.
- **The ground darkens as the thread is followed** — a depth variable drives
  the page's ambient light, so going deeper is felt.
- Each new question rises past from below, blur to sharp.
- **The breath step became a breathing exercise.** The copy says "In for four.
  Hold for four. Out for four" — there is now a ring that breathes on exactly
  that twelve-second count.
- **The body step arranges into a figure** — head, jaw, throat down the centre;
  shoulders, chest, hands across; stomach below — with a spine hairline. Same
  chips, but the reader now points at a body.
- The tally became a balance with a brass fulcrum.
- Naming the belief is set as a ceremony; the commitment is a signed rule.
- Insights are margin notes with a brass diamond, not slabs with fat bars.
- The final record is a leaf of aged paper with a wax seal in the corner.

**Note for review:** the opening screen is deliberately restrained; most of the
transformation reveals itself as you answer. Go three or four steps in on
desktop before judging it.

---

## 4 · The Sacred Divide — `noble-father-divide.html`
*A coercive-control reference across 25 traditions. Compositional rebuild.*

**Was:** every tactic entry carries three passages — how it appears, the defense
you will hear, and the counter — and all three were set identically in one grey
column. That threw away the entire point of the artifact.

**Now — three registers, three voices:**
- **How it appears** — evidentiary, gilt rule, hanging marks
- **The defense you will hear** — quoted, italic, deliberately de-emphasised,
  because these are the abuser's words
- **The counter** — boxed, bolded, the highest contrast on the plate, because a
  reader in trouble needs to find it in two seconds

Entries became numbered plates with the evidence grade struck as a stamp and a
chevron that rotates open.

**This file has both a parchment theme and a dark theme.** The first pass made
the counter nearly invisible on light; every colour now derives from the page's
own tokens and contrast was verified in both.

**Also corrected:** the file's `<title>` still read "The Coercive Control Codex"
from an earlier draft. Now titled correctly.

**Look at:** open any tradition on the tactic route and compare the three
registers.

---

## 5 · Playground Protectors — `noble-father-playground.html`
*A children's book about manipulation. Effects and a novel access mechanic.*

**The grown-up fog — the significant piece.** This book is written for two
readers at once, and some passages talk *about* children rather than to them.
Those are now sealed behind drifting cloud. While the fog is up the content is
marked `inert` **and** `aria-hidden`, so a child genuinely cannot read it — not
by squinting, not with a screen reader. The block also collapses to 280px so a
child flicks past it in one scroll. A grown-up taps once and it clears for the
visit.

**Also:**
- Power-up bursts fire a conic starburst of rays outward, once
- Panels, cards and plates land like comic frames, staggered
- Speech bubbles spring; move cards slide in; mission titles arrive letter by
  letter with a tilt
- **Weather per world** — each of the four worlds carries seven drifting orbs
  on independent paths in its own colour, so the book changes climate
- **Confetti on lighting a mission** — hooked to the book's *own* bulb
  mechanic, so lighting a mission pops the bulb and throws 26 pieces in the
  brand colours

**Still outstanding:** the request for AI-rendered character scenes per chapter
was not fulfilled. The image-generation connector requires an approval that was
never granted in session. The cover art was extracted and is ready to serve as
a character reference when that is approved.

---

## 6 · The faith project — `faith-index.html`
*A 3.13MB offline reference work. Five of eight planned passes complete.*

This file operates under four hard rules that apply to **it alone**: no network
request ever, no storage of any kind, one file, and no engagement mechanics. It
is handed person to person, read offline, sometimes by people who are monitored
at home. It deliberately receives **none** of the shared site chrome, because
that would add a font link and break rule one.

**Pass 02 — the apex chain (the highest-value artifact).**
Each apex row is a chain of custody for an office: who holds it, who chose
them, who can remove them. The third link is the one that matters and in the
record it is frequently absent. Three terminal states, classified from each
row's own words and never asserted:
- *intact* — a mechanism exists and is used → closed link
- *nominal* — exists on paper, never exercised → hairline ghost link
- *broken* — no mechanism at all → **the link hangs open in oxblood**

On Christianity that yields two open chains and two never-exercised ghosts.

**Pass 03 — the matrix as an instrument.**
810 cells (27 traditions × 30 tactics) were identical bullets carrying no
information. Each is now filled by its own evidence grade — **107 codified, 195
sourced, 511 structural, 1 ungraded**. Row and column light as a cross-hair.
The grid is one tab stop; arrow keys move the caret, Home/End jump to row ends,
Enter opens the tactic. A live readout names the cell. Real header scopes, a
caption explaining the control, per-cell labels.

**Passes 01, 07, 08** — directional view transitions (deeper rises from below,
back settles from above), oldstyle figures in prose and lining tabular figures
in tables, hanging punctuation, `prefers-contrast` /
`prefers-reduced-transparency` / `forced-colors` all answered, a 12.4px minimum
enforced everywhere, and print that inverts the dark registers cleanly.

**Verified:** 15 routes, zero console errors, **zero external requests**, zero
text below 12.4px, zero horizontal overflow at 360/390/768/1280/1920, data
intact, and under reduced motion nothing is left hidden.

**Not done — passes 04, 05, 06:** the pipeline flow with its disclosure cut-off
marked, the cycle ring, the sourcing gradient chart, the Disclosure Scorecard
grid, the five district glyphs, the generated cover plate, and hub composition
tuning. These were stopped deliberately rather than guessed at — each needs a
different data shape read out of the file, and inventing a structure risks a
diagram asserting something the record does not say.

---

## 7 · The remaining five
`seals` · `fractal` · `fracture` · `sovereign` · `festival` ·
plus `reaction-map`

These received the shared design system rather than individual rebuilds:

- **The Catalogue navigation** — a wax seal on every page opening a leather
  table of contents with per-volume accent gems
- **Ink-veil arrivals** and cross-document view transitions, with the seal as a
  shared element so it holds still while the page changes
- **Per-page elevation layers** written against each page's own selectors —
  breathing seal die on The Press, cover entrances and pull-quote marks on The
  Fractal, brass chapter rules on Sovereign, a Fraunces drop cap on The Fracture, zine-style hard-shadow buttons on the Festie Codex

**A real bug was found and fixed on the Reaction Map.** A variable was used
before its declaration, which silently killed roughly 600 lines of setup — the
Undertow checklist never rendered, the AI analyser never wired up, the tour
never auto-started. That failure was live. It now works.

---

## What to be sceptical of

- **Nothing here was seen in its real typeface.** Font loading was blocked
  throughout the build.
- **Hover effects do not exist on phones.** The Portals torch has a touch and
  tilt equivalent; other hover states simply will not fire for mobile visitors.
- **Variable font axis animation is unverified.** Fraunces' SOFT and WONK axes
  are requested and animated, but were never seen rendering. It degrades to
  nothing if the axes fail to load.
- **The custom domain was not resolving** at the end of the session. Every
  Netlify subdomain serves correctly, so it is a DNS or domain-config matter.

---

## Deployment state

All eleven site pages were deployed live during the session and verified
serving. The faith project has not been deployed anywhere.
