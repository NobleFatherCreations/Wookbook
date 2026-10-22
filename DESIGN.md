---
name: The Pattern Decoder
description: A free, offline guide to 310 manipulation and control tactics, read under one persistent night sky where every tactic is a star.
colors:
  night-ink: "#05070F"
  night-ink-2: "#0A0F1F"
  off-white: "#F4F1EA"
  off-white-2: "rgba(244,241,234,.7)"
  off-white-3: "rgba(244,241,234,.47)"
  hairline: "rgba(244,241,234,.14)"
  hairline-soft: "rgba(244,241,234,.08)"
  fill: "rgba(244,241,234,.045)"
  fill-2: "rgba(244,241,234,.08)"
  star-gold: "#E8C877"
  star-gold-light: "#F3DA97"
  star-ink: "#1B1505"
  ember: "#F2A38A"
  ember-wash: "rgba(242,163,138,.09)"
  ember-line: "rgba(242,163,138,.34)"
  toward: "#9CC9B4"
  away: "#A9B6E6"
  glass: "rgba(10,14,28,.72)"
  twilight-bg: "#F3F3F8"
  twilight-ink: "#11142A"
  twilight-star: "#8A6414"
  twilight-ember: "#A33A1E"
typography:
  display-hero:
    fontFamily: "Astra, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "clamp(46px, 9.2vw, 128px)"
    fontWeight: 300
    lineHeight: 1
    letterSpacing: "0.005em"
  display-beat:
    fontFamily: "Astra, system-ui, sans-serif"
    fontSize: "clamp(44px, 8vw, 112px)"
    fontWeight: 300
    lineHeight: 1.02
    letterSpacing: "0.005em"
  headline:
    fontFamily: "Astra, system-ui, sans-serif"
    fontSize: "clamp(30px, 4.4vw, 52px)"
    fontWeight: 300
    lineHeight: 1.1
  entry-summary:
    fontFamily: "Astra, system-ui, sans-serif"
    fontSize: "clamp(24px, 3vw, 32px)"
    fontWeight: 300
    lineHeight: 1.32
  row-title:
    fontFamily: "Astra, system-ui, sans-serif"
    fontSize: "clamp(28px, 3.6vw, 44px)"
    fontWeight: 300
    lineHeight: 1.1
  body:
    fontFamily: "'Public Sans', system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.6
  lede:
    fontFamily: "'Public Sans', system-ui, sans-serif"
    fontSize: "clamp(19px, 2.3vw, 24px)"
    fontWeight: 400
    lineHeight: 1.5
  script:
    fontFamily: "'Public Sans', system-ui, sans-serif"
    fontSize: "clamp(20px, 2.4vw, 24px)"
    fontWeight: 400
    lineHeight: 1.6
  list-name:
    fontFamily: "'Public Sans', system-ui, sans-serif"
    fontSize: "19px"
    fontWeight: 600
    lineHeight: 1.3
  label:
    fontFamily: "'Public Sans', system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.14em"
rounded:
  sm: "6px"
  md: "14px"
  lg: "24px"
  pill: "999px"
spacing:
  xs: "8px"
  sm: "16px"
  md: "24px"
  lg: "48px"
  xl: "80px"
  xxl: "120px"
components:
  search-pill:
    backgroundColor: "{colors.glass}"
    textColor: "{colors.off-white}"
    typography: "{typography.lede}"
    rounded: "{rounded.pill}"
    height: "60px"
    padding: "0 56px 0 54px"
  button-primary:
    backgroundColor: "{colors.off-white}"
    textColor: "{colors.night-ink}"
    rounded: "{rounded.pill}"
    height: "44px"
    padding: "0 22px"
  button-outline:
    backgroundColor: "transparent"
    textColor: "{colors.off-white}"
    rounded: "{rounded.pill}"
    height: "44px"
    padding: "0 22px"
  chip:
    backgroundColor: "transparent"
    textColor: "{colors.off-white-2}"
    rounded: "{rounded.pill}"
    height: "38px"
    padding: "0 16px"
  chip-selected:
    backgroundColor: "{colors.fill-2}"
    textColor: "{colors.off-white}"
  safety-badge:
    backgroundColor: "{colors.ember-wash}"
    textColor: "{colors.ember}"
    rounded: "{rounded.pill}"
    height: "28px"
    padding: "0 12px"
  list-row:
    backgroundColor: "transparent"
    textColor: "{colors.off-white-2}"
    padding: "26px 0"
  sky-sheet:
    backgroundColor: "{colors.glass}"
    textColor: "{colors.off-white}"
    rounded: "{rounded.lg}"
    padding: "28px"
---

# Design System: The Pattern Decoder

## Overview

**Creative North Star: "The Observatory at Night"**

One canvas sky is fixed behind the whole guide. The 310 tactics are its stars, grouped into ten constellations, and the camera moves with the reader: wide on home, into a constellation on a group page, onto a single star on an entry page, user-controlled on the Sky page. Everything else is quiet type laid over that sky. The restraint is Apple-like: no cards, no boxes, no ornament. Hairlines, space and scale do the structural work, and the glass of a panel appears only where a control must float over the sky.

The reader is often hurting, on a phone, late. So the build orients before it informs: a centered stage with a huge headline and one search pill, then a pinned scroll story during which the sky flies (310 tactics, ten constellations, three focused constellations, "Start anywhere"). Entries open with a short window onto the sky showing the entry's star and its neighbours, then a large summary, then five parts as folded sections (in short, understand it, is this it, what you can do, go deeper), open by default on desktop. Motion is cinematic but never gates content: Calm mode and prefers-reduced-motion stop all motion, and the sky drops to a lite mode on slow devices.

**Key Characteristics:**
- Dark night-sky default (night ink) with a light "twilight" theme that swaps the same roles.
- Astra display, drawn for this product, over Public Sans for reading.
- Gold is for stars, links and active marks; ember is for safety only.
- Typographic list rows between hairlines replace cards.
- Large scale contrast: 128px stage headline down to 17px body.
- Stars read glow gold; saved are ringed; search and guide results light up on the canvas.

## Colors

A restrained night palette: near-black blue ground, one warm off-white for ink, one gold that belongs to stars, one ember that belongs to safety.

### Primary
- **Star Gold** (#E8C877; hover-lift #F3DA97): the only accent. Stars read, active nav marks (the entry TOC rule, story dots), links and sub-labels, the "?" marker in question lists, the script quote rule, selected-guide check, saved-state toggles, focus ring. Text on a gold fill uses Star Ink (#1B1505). In twilight it deepens to #8A6414 for contrast.

### Secondary
- **Ember** (#F2A38A, wash .09, line .34): reserved for safety. The safety badge, the safety callout, the safety dot on rows. Twilight ember is #A33A1E.

### Neutral
- **Night Ink** (#05070F, secondary ground #0A0F1F): the page and sky ground.
- **Off-White** (#F4F1EA): primary text. Secondary reading text is the same at .70 alpha, tertiary and meta at .47.
- **Hairlines** (.14 alpha for structure, .08 for quiet dividers): the only separators. Fills (.045, .08) appear only as hover and selected washes.
- **Lit Glass** (rgba(10,14,28,.72) with blur): search pill, floating sheet, sticky bars. Twilight glass is rgba(248,248,252,.82).
- **Twilight** ground #F3F3F8, ink #11142A.
- **Toward / Away** (#9CC9B4, #A9B6E6): used only to label the two columns of the is-this-it comparison and their bullets. A functional pair, not a second accent.

### Named Rules
**The Star Rule.** Gold appears only where something is a star, a link or an active mark. It never fills a surface or decorates.
**The Ember Rule.** Ember means safety, nothing else. If a tint is not about danger or protection, it is not ember.
**The Alpha Ladder Rule.** Text hierarchy is one off-white at 100, .70 and .47 alpha; do not introduce new greys.

## Typography

**Display Font:** Astra (original, monoline geometric, round caps, letters built like constellations, four-point-star dots on i, j and punctuation; Light 300 and Medium 500; fallback system sans)
**Body Font:** Public Sans (fallback system sans)
**Label:** Public Sans, small, bold, tracked caps (12px, .14em).

**Character:** Astra is the headline voice, thin and starlike; Public Sans is plain and legible for people reading under stress.

### Hierarchy
- **Display** (Light 300, clamp(46px, 9.2vw, 128px), 1.0): the home stage headline, max 11ch. Story beats use clamp(44px, 8vw, 112px).
- **Headline** (Light 300, clamp(30px, 4.4vw, 52px), 1.1): page titles and part headings (part headings clamp to 48px max).
- **Title** (Light 300, clamp(28px, 3.6vw, 44px), 1.1): constellation rows and ways-in rows. Entry summary is Light 300 at clamp(24px, 3vw, 32px), 1.32, max 26em.
- **Body** (Regular 400, 17px, 1.6, measure 66ch): all reading. Scripts and what-you-can-do wording are Public Sans at up to 24px, never Astra, for legibility.
- **List name** (SemiBold 600, 19px, 1.3): tactic names in rows.
- **Label** (SemiBold 600, 12px, .14em, caps): block headings inside an entry (says, is-this-it columns, notes, footer groups).

### Named Rules
**The 24px Floor Rule.** Astra is used at 24px and up. Below that, set Public Sans.
**The Plain Script Rule.** Anything the reader might say aloud or act on is Public Sans.

## Layout

Single centered column system, max 1240px with 28px side padding (20px on phones). Reading column max 760px; entries sit in a 180px sticky table of contents plus a 740px column, collapsing to a sticky chip bar under 1040px. Vertical rhythm is large and generous: sections 120px apart (80px on phones), parts 56px, blocks 44px, with an 8px base grid for small gaps. The home page is a full-viewport stage, a pinned story 460vh tall (420vh on phones) with centered beats and side dots, then typographic lists. Pages that sit on the map (entry, browse, search, patterns) begin with a 200 to 340px window onto the sky and fade the content ground in beneath it; text-heavy pages sit on a 70% night wash. Under 760px a five-tab bar replaces the header nav. Sticky header is transparent until scrolled, then blurred glass with a soft hairline.

## Elevation & Depth

Depth is the sky itself: stars behind, a radial veil to darken the edges, content floating over it. There are no drop shadows. Where a control floats (search pill, Sky sheet, guide bar, sticky chip bar, tab bar) it uses lit glass: translucent night fill, 14 to 24px backdrop blur, a hairline border.

### Named Rules
**The No-Shadow Rule.** Separation comes from hairlines, blur and the sky, never from box-shadow.
**The Glass Only Where Floating Rule.** A surface is glass only if it hovers over the canvas or scrolling content.

## Shapes

Pills for every control (search, buttons, chips, badges, toast: 999px). Circles for icon buttons and stars. Sky sheet 24px, safety callout 14px. Content is never boxed: rows and sections are cut by full-width 1px hairlines. Quoted scripts and says-lists take a 1px left rule (gold for scripts, hairline for says).

## Components

### Search pill
Hero control, 60px tall, 680px max, translucent glass with a .47 alpha border that firms to .70 on focus. Search icon left, clear right. A line of "try" suggestions below sits as underlined text, not chips.

### Buttons
Pill, 44px min. **Primary:** off-white fill, night text. **Outline:** hairline border, hover fill wash. **Ghost:** no border. Press scales to .97 over 120ms; hovers ease over 220ms.

### Chips
Pill, 38px, hairline border, .70 text; selected adds the soft fill wash and brighter border.

### Typographic list rows
The replacement for cards. Constellation rows are a three-column grid (Astra title, plain description, count) between hairlines; hover nudges the row 16px right with a faint fill. Tactic rows are a two-line name plus clamped definition in a multi-column list; hovering the list dims the other rows to .55.

### Entry parts
Five folded sections, each topped by a hairline, an Astra headline and a circular chevron that rotates 90 degrees when open. Body reveals with a 500ms rise.

### Safety callout
The one bordered, tinted block, in ember wash and ember line, with an ember title. It exists because safety must interrupt the quiet.

### Navigation and the sky controls
Header text links in .47 alpha, current page full ink; a Calm toggle (gold when on) and theme toggle. The Sky page overlays group chips, tool buttons and a glass sheet for the selected star. Calm mode flattens the pinned story into a plain stacked column.

### Motion
Ease (.22,.61,.36,1) at 220ms for state; ease-out (.16,1,.3,1) at 500 to 900ms for reveals and beats; story beats cross-fade over 900ms; the camera tween is a cubic ease-in-out. Calm and reduced motion set transitions to 1ms and show everything.

## Do's and Don'ts

### Do:
- **Do** build structure with 1px hairlines (.14 alpha), space and type scale.
- **Do** keep gold for stars, links and active marks; ember for safety only.
- **Do** set Astra at 24px and up, Public Sans everywhere else and for all scripts.
- **Do** let the sky and the camera carry orientation, and keep content visible with Calm mode and reduced motion.
- **Do** keep pills for controls and 44px minimum touch targets.

### Don't:
- **Don't** wrap content in cards or boxed panels; use list rows between hairlines.
- **Don't** use box-shadow.
- **Don't** introduce a second accent or tint a surface gold.
- **Don't** hide content behind animation or let a reveal delay help.

### Not canonized (defects the build carries)
- Tracked-caps `eyebrow` lines above page titles (still present in the CSS): a kicker pattern, not a rule for new surfaces. Label caps are for block headings inside entries only.
- Astra Medium at 22px and 20px in the brand wordmark, breaking the 24px floor.
- Part-circle glyphs such as the literal "?" bullet in question lists: new lists use plain dots.
