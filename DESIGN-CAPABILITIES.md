# What you can ask me for, design-wise

Plain-language menu of everything installed and everything I proved out on this
project. Written for you, not for Claude — the companion file
`CLAUDE-DESIGN-BOOTSTRAP.md` is the one you hand to a new chat.

---

## The short version

You have **16 design skills**, a **browser I can drive and screenshot with**,
and a **deploy pipeline**. In practice that means you can ask for three levels
of work, and it helps a lot if you say which one you want:

| Level | What you get | Say it like |
|---|---|---|
| **Polish** | Same layout, better craft — spacing, type, hover states, motion | "polish this page" |
| **Elevate** | New effects and interactions layered onto the existing structure | "add effects to this" |
| **Rebuild** | The page's structure is re-composed around one spatial idea | "rebuild this — full arsenal" |

If you don't say, I'll assume **Rebuild**. That's the standing instruction from
this project. If you only want a light touch, say so or you'll get a lot.

---

## The 16 skills, in English

### The main one
**`impeccable`** — an award-tier art-direction system. It has sub-commands, and
naming one gets you a very specific kind of pass:

| Ask for… | What it does |
|---|---|
| `critique` | Reviews a design and scores it against UX heuristics |
| `audit` | Technical check — accessibility, performance, responsive |
| `polish` | Final quality pass before shipping |
| `bolder` | Takes something safe and makes it loud |
| `quieter` | Takes something loud and calms it down |
| `distill` | Strips complexity back to essence |
| `harden` | Error states, edge cases, i18n, production readiness |
| `onboard` | First-run flows, empty states |
| `animate` | Purposeful motion |
| `colorize` | Adds strategic colour to something monochrome |
| `typeset` | Typography and hierarchy |
| `layout` | Spacing, rhythm, visual hierarchy |
| `delight` | Personality and memorable touches |
| `overdrive` | Pushes past conventional limits |
| `clarify` | Rewrites UX copy, labels, error messages |
| `adapt` | Responsive across devices |
| `optimize` | Diagnoses and fixes UI performance |
| `shape` | Plans UX before any code is written |

It also carries a **mechanical detector** that scans finished work for design
anti-patterns and tells me what's wrong. I ran it on your pages throughout.

### Taste and direction
- **`emil-design-eng`** — Emil Kowalski's philosophy on UI polish, component
  design, and the invisible details that make software feel considered.
- **`design-taste-frontend`** — anti-generic landing pages and portfolios.
  Reads the brief, infers a direction, avoids anything that looks templated.
- **`design-taste-frontend-v1`** — the older version, kept for compatibility.
- **`gpt-taste`** — heavy GSAP motion engineering: scroll pinning, stacking,
  scrubbing, editorial typography, big section spacing.
- **`high-end-visual-design`** — the exact fonts, spacing, shadows and card
  structures that make a site feel expensive. Blocks the cheap defaults.

### Specific looks
- **`minimalist-ui`** — clean editorial, warm monochrome, no gradients.
- **`industrial-brutalist-ui`** — Swiss print meets military terminal. Rigid
  grids, extreme type contrast, analog degradation.
- **`stitch-design-taste`** — generates a `DESIGN.md` spec enforcing premium
  standards, for handing to another tool or agent.

### Brand and imagery
- **`brandkit`** — brand guideline boards, logo systems, identity decks.
- **`imagegen-frontend-web`** — generates one reference image *per section* of
  a landing page for a developer to build from.
- **`imagegen-frontend-mobile`** — the same for app screens, in phone mockups.
- **`image-to-code`** — generates the design image first, studies it, then
  builds the page to match.

### Working on what exists
- **`redesign-existing-projects`** — audits a live site, finds the generic
  AI-looking patterns, upgrades without breaking function. **This is the one
  that matches most of what we did on your books.**
- **`full-output-enforcement`** — stops me truncating long code with
  "// rest unchanged". Useful on your 2–10MB single-file books.

---

## What the browser gives you

Playwright is installed with Chromium. I can:

- **Screenshot any page** at any width and actually look at it
- **Click through flows** — I walked your Root practice five steps deep
- **Drive interactions** — I tested the Portals light-line drag by simulating it
- **Catch console errors** — this is how I found the Reaction Map crash
- **Detect layout bugs** — horizontal overflow, invisible elements, contrast

**Why this matters:** I do not guess whether something looks right. Ask me to
verify and I will screenshot it, review my own screenshots, and fix what I see.
When I say "verified", that is what happened.

---

## What I can deploy

Netlify. Given a token I can push any folder live to any of your sites, and I
did — all 11 are live from this session.

---

## Things I proved out here that you can ask for by name

These are patterns I built and tested on your work. Referencing them is faster
than describing them:

- **"Standing volumes"** — book covers rendered as physical objects with
  spines, page edges, shelf rails and pooling shadows
- **"The Light Line"** — a draggable rule that wipes between two photos of the
  same object (your day/night pendants)
- **"The torch"** — a light that follows the cursor and reveals a second image
  only where it falls
- **"The plumb line"** — a progress rail that descends with a weighted bob
- **"The fog gate"** — content sealed behind weather that one audience can
  clear and another scrolls past, genuinely unreadable until opened
- **"Codex plates"** — reference entries where each register gets its own voice
- **"The apex chain"** — a chain diagram that terminates in an open link where
  the data says no mechanism exists
- **"The opening"** — covers parting, lights coming up, rooms rising out of dark

---

## Limits worth knowing

- **Fonts don't load in my sandbox.** Google Fonts is blocked, so I've never
  seen your pages render in real Fraunces. Anything font-dependent needs your
  eyes on a real device.
- **Hover effects don't exist on phones.** If your traffic is TikTok, tell me
  and I'll build the touch or tilt equivalent — I did this for the Portals.
- **Image generation needs your approval** on the Artlist connector before I
  can call it, and it spends your credits.
- **I can't see your custom domain's DNS.** Deploys succeed; domain config is
  yours.
- **There is no "McLaren" skill.** Nothing by that name is installed — you may
  be thinking of one of the 13 taste-skill entries above.

---

## How to get the most out of me

1. **Say the level** — polish, elevate, or rebuild.
2. **Name the constraint if there is one.** Your faith project has four hard
   rules; everything else has none. I will apply the wrong ruleset if you don't
   tell me which project I'm in.
3. **Tell me what must not change.** I default to never touching your prose or
   your interactive logic, but say it if it matters.
4. **Ask me to verify.** "Screenshot it and fix what you find" turns a guess
   into a checked result.
5. **Point at a named pattern** from the list above when one fits.
