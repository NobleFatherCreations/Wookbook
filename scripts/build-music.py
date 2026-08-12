#!/usr/bin/env python3
"""
Build The Listening Room (the /music page) from deploy/music/MANIFEST.json.

Why this exists: the previous music page had NO local source in the repo, and its
entire TRACKS/SHELVES catalogue was lost in some deploy -- the live file used
TRACKS 8x and SHELVES 3x and declared neither, so `TRACKS is not defined` threw
and the page rendered as an empty shell (see AUDIT-2026-08-12.md). Everything the
page needs is now committed: this generator, the manifest, the fonts and the
CSS/JS. The mp3s themselves are gitignored but reproducible from the Drive ids in
the manifest.

Outputs (identical bytes):
  deploy/music/index.html            -> what gets uploaded to the noblemusic site
  source/projects/noble-father-music.html  -> the committed copy (localSource)

Run:  python3 scripts/build-music.py
"""

import base64
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'scripts', 'music')

VERSION = 'v2'
VERSION_DATE = '2026-08-12'

# On-page changelog, newest first. Reader-facing language only -- no file paths,
# no commit jargon. Mirrored into sites.json -> projects[music].changelog.
CHANGELOG = [
    ('v2', '2026-08-12',
     'The room is stocked again. Every track is back — 176 of them, sorted onto '
     'six shelves by what each song is for, with real running times read off the '
     'audio itself. The page had been showing an empty shell because its track '
     'list had gone missing; it is now kept with the page so it cannot vanish '
     'again. Rebuilt the player from scratch: a proper now-playing panel with '
     'sleeve art, a live frequency display, a scrub bar that shows what has '
     'loaded, shuffle, volume, and keyboard shortcuts. On a phone the player '
     'opens into a full screen of its own. Added the catalogue of every other '
     'Noble Father project, which this page was missing.'),
    ('v1', 'unknown',
     'The first Listening Room.'),
]

# THE HOUSE catalogue. Order and numbering follow the existing `nf-seal`
# generation on the other nine books so this page does not invent a third
# variant; the two entries that were missing everywhere (The Festie Bible and
# The Casting -- they appeared in 0 of 14 book catalogues) are appended.
# Every href is ABSOLUTE and points at the hub, which resolves from this page's
# own netlify.app address AND from noblefathercreations.com/music.
HOUSE = [
    ('I',    'The Loop',                      'The machine that learns you',      '/loop',       '#6E93B5'),
    ('II',   'The Press',                     'Real wax, a voice inside',         '/press',      '#E8C879'),
    ('III',  'The Portals',                   'Strontium glow, no battery',       '/portals',    '#7FD9D4'),
    ('IV',   'The Root',                      'A shadow work practice',           '/shadowroot', '#D9964A'),
    ('V',    'The Weighing',                  'How to be right about people',     '/scale',      '#9B8FA8'),
    ('VI',   'The Sacred Divide',             '25 traditions, 750 entries',       '/faith',      '#C29A52'),
    ('VII',  'The Fractal',                   'One pattern runs the world',       '/fractal',    '#E5A93C'),
    ('VIII', 'The Fracture',                  'The reading edition',              '/fracture',   '#C9A35B'),
    ('IX',   'The Sovereign Divine Feminine',  'A field guide',                    '/feminine',   '#C85F7E'),
    ('X',    'Playground Protectors',          "Shaela's guide for brave kids",    '/children',   '#FFC23D'),
    ('XI',   'The Festie Codex',              "The gate — attendee's cut",        '/wook',       '#D8FF3D'),
    ('XII',  'The Pattern Decoder',           '349 tactics, decoded',             '/playbook',   '#8A8071'),
    ('XIII', 'The Listening Room',            'Sorted by what each song is for',  '/music',      '#C9A24A'),
    ('XIV',  'The Festie Bible',              'Twelve field guides',              '/festival',   '#9ED8A0'),
    ('XV',   'The Casting',                   'Resin, wax and light',             '/resin',      '#B98FD9'),
]
HUB = 'https://noblefathercreations.com'
HERE = '/music'

ICONS = {
    'prev': '<path d="M19 20 9 12l10-8v16Z"/><path d="M5 4v16" stroke-width="2" '
            'stroke-linecap="round" fill="none"/>',
    'next': '<path d="M5 4l10 8-10 8V4Z"/><path d="M19 4v16" stroke-width="2" '
            'stroke-linecap="round" fill="none"/>',
    'play': '<path d="M7 4.5 20 12 7 19.5v-15Z"/>',
    'pause': '<rect x="6" y="4.5" width="4" height="15" rx="1"/>'
             '<rect x="14" y="4.5" width="4" height="15" rx="1"/>',
    'shuffle': '<path d="M17 4l3 3-3 3M17 14l3 3-3 3M3 7h4l3 4M20 7h-6l-8 10H3m17 0h-3" '
               'fill="none" stroke-width="1.8" stroke-linecap="round" '
               'stroke-linejoin="round"/>',
    'search': '<circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke-width="1.8"/>'
              '<path d="m15.5 15.5 4.5 4.5" fill="none" stroke-width="1.8" '
              'stroke-linecap="round"/>',
    'x': '<path d="m6 6 12 12M18 6 6 18" fill="none" stroke-width="1.8" '
         'stroke-linecap="round"/>',
    'down': '<path d="m6 9 6 6 6-6" fill="none" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round"/>',
    'vol': '<path d="M4 9h3l4-3.5v13L7 15H4V9Z"/><path d="M15 9.5a3.5 3.5 0 0 1 0 5" '
           'fill="none" stroke-width="1.7" stroke-linecap="round"/>',
}


def icon(name, cls=''):
    return ('<svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" '
            'aria-hidden="true"%s>%s</svg>'
            % ((' class="%s"' % cls) if cls else '', ICONS[name]))


def read(path, binary=False):
    mode = 'rb' if binary else 'r'
    kwargs = {} if binary else {'encoding': 'utf-8'}
    with open(os.path.join(SRC, path), mode, **kwargs) as f:
        return f.read()


def font_face(family, filename, weights):
    b64 = base64.b64encode(read(os.path.join('fonts', filename), binary=True)).decode()
    return (
        "@font-face{font-family:'%s';font-style:normal;font-weight:%s;"
        "font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2');"
        "unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,"
        "U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,"
        "U+2212,U+2215,U+FEFF,U+FFFD}" % (family, weights, b64)
    )


def esc(s):
    return html.escape(str(s), quote=True)


def mmss(sec):
    sec = int(round(sec))
    return '%d:%02d' % (sec // 60, sec % 60)


def split_title(title):
    """Split a title into its main line and its mix/version tail.

    The '(' must be preceded by whitespace to count as a subtitle, otherwise a
    title with a mid-word bracket gets torn in half -- "Code(y) Red!" was being
    shown as "Code" with a sub-line of "(y) Red!".
    """
    m = re.match(r'^(.*?\S)\s+(\(.*)$', title)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r'^(.*?\S)\s+·\s+(.*)$', title)
    if m:
        return m.group(1), m.group(2)
    return title, ''


def build():
    man_path = os.path.join(ROOT, 'deploy', 'music', 'MANIFEST.json')
    with open(man_path, encoding='utf-8') as f:
        man = json.load(f)

    shelves = man['shelves']
    base = man['audioBase']

    # Present the catalogue in shelf-rail order, then alphabetically. The
    # manifest stores tracks sorted by shelf *id*, which put The Descent above
    # The Reckoning and disagreed with the rail the reader is looking at.
    order = {s['id']: i for i, s in enumerate(shelves)}
    tracks = sorted(man['tracks'],
                    key=lambda t: (order.get(t['shelf'], 99), t['title'].lower()))
    if not base.startswith('https://'):
        sys.exit('audioBase must be an absolute https URL: got %r' % base)

    # ---- the data island the page reads ---------------------------------
    counts = {}
    for t in tracks:
        counts[t['shelf']] = counts.get(t['shelf'], 0) + 1

    island = {
        'shelves': [{'id': s['id'], 'name': s['name'], 'blurb': s['blurb'],
                     'count': counts.get(s['id'], 0)} for s in shelves],
        'tracks': [{
            'slug': t['slug'],
            'title': t['title'],
            # main/sub are DERIVED here, not read from the manifest, so the rule
            # lives in one committed place
            'main': split_title(t['title'])[0],
            'sub': split_title(t['title'])[1],
            'shelf': t['shelf'],
            'shelfName': t['shelfName'],
            'hue': t['hue'],
            'dur': round(t['duration'], 1),
            # ABSOLUTE, always. A root-relative /audio/x.mp3 resolves against
            # noblefathercreations.com through the /music proxy and 404s.
            'url': base + t['file'],
        } for t in tracks],
    }

    total = sum(t['duration'] for t in tracks)
    hours = int(total // 3600)
    mins = int(round((total % 3600) / 60))

    # ---- assets ---------------------------------------------------------
    fonts = (font_face('Fraunces', 'Fraunces-latin.woff2', '100 900') +
             font_face('Karla', 'Karla-latin.woff2', '400 800'))
    page_css = read('page.css')
    chrome_css = read('chrome.css')
    page_js = read('page.js')
    chrome_js = read('chrome.js')

    # ---- shelf rail ------------------------------------------------------
    rail = ['<button type="button" class="shelf-btn" data-shelf="all" '
            'aria-pressed="true">The Whole Room <span class="c">%d</span></button>'
            % len(tracks)]
    for s in shelves:
        rail.append(
            '<button type="button" class="shelf-btn" data-shelf="%s" '
            'aria-pressed="false">%s <span class="c">%d</span></button>'
            % (esc(s['id']), esc(s['name']), counts.get(s['id'], 0)))

    # ---- THE HOUSE catalogue --------------------------------------------
    rows = []
    for i, (num, title, desc, path, dot) in enumerate(HOUSE):
        here = path == HERE
        href = '#' if here else HUB + path
        cur = ' aria-current="page"' if here else ''
        rows.append(
            '<li class="nf-row%s" style="--nf-i:%d"><a href="%s"%s>'
            '<span class="nf-dot" style="--va:%s" aria-hidden="true"></span>'
            '<span class="nf-num">%s</span>'
            '<span class="nf-vol">%s%s</span>'
            '<span class="nf-desc">%s</span></a></li>'
            % (' nf-here' if here else '', i, href, cur, dot, num, esc(title),
               '<span class="nf-here-dot" aria-hidden="true"></span>' if here else '',
               esc(desc)))

    # ---- changelog -------------------------------------------------------
    log = []
    for v, d, text in CHANGELOG:
        log.append('<li><span class="v num">%s</span><span class="t">%s'
                   '<span class="d num">%s</span></span></li>'
                   % (esc(v), esc(text), esc(d)))

    # ---- transport (reused in the deck and the sheet) --------------------
    def transport(wide_cls=''):
        return (
            '<button type="button" class="tbtn%s" data-act="prev" aria-label="Previous track">%s</button>'
            '<button type="button" class="tbtn tbtn-play" data-act="play" aria-label="Play">'
            '<span class="i-play">%s</span><span class="i-pause">%s</span></button>'
            '<button type="button" class="tbtn" data-act="next" aria-label="Next track">%s</button>'
            '<button type="button" class="tbtn%s" data-act="shuffle" aria-pressed="false" '
            'aria-label="Shuffle">%s</button>'
            % (wide_cls, icon('prev'), icon('play'), icon('pause'),
               icon('next'), wide_cls, icon('shuffle')))

    def scrub(role='seek'):
        return (
            '<div class="scrub">'
            '<span class="scrub-track" aria-hidden="true">'
            '<span class="scrub-buf"></span><span class="scrub-played"></span></span>'
            '<span class="scrub-knob" aria-hidden="true"></span>'
            '<input type="range" min="0" max="1000" value="0" step="1" '
            'data-role="%s" aria-label="Seek">'
            '</div>'
            '<div class="times"><span class="num" data-np="now">0:00</span>'
            '<span class="num t-end" data-np="end">0:00</span></div>' % role)

    def volume():
        return (
            '<div class="vol">%s<div class="vol-slider">'
            '<span class="vol-track" aria-hidden="true"><span class="vol-fill"></span></span>'
            '<input type="range" min="0" max="100" value="85" step="1" '
            'data-role="vol" aria-label="Volume"></div></div>' % icon('vol'))

    viz = ('<canvas class="viz" aria-hidden="true"></canvas>'
           '<div class="viz-fallback" aria-hidden="true">%s</div>'
           % ''.join('<i style="animation-delay:%dms"></i>' % (i * 70)
                     for i in range(18)))

    # ---- the document ----------------------------------------------------
    doc = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Listening Room — Noble Father Creations</title>
<meta name="description" content="%(count)d tracks by Shae Stovell, sorted by what each song is for. Free to stream, nothing to sign up for.">
<meta name="theme-color" content="#0B0910">
<meta property="og:title" content="The Listening Room — Noble Father Creations">
<meta property="og:description" content="%(count)d tracks, %(hours)dh %(mins)dm, sorted by what each song is for.">
<meta property="og:type" content="music.playlist">
<meta property="og:url" content="https://noblefathercreations.com/music">
<link rel="icon" href="data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%%3E%%3Crect width='32' height='32' rx='7' fill='%%230B0910'/%%3E%%3Ccircle cx='16' cy='16' r='9' fill='none' stroke='%%23C9A24A' stroke-width='2'/%%3E%%3Ccircle cx='16' cy='16' r='2.4' fill='%%23C9A24A'/%%3E%%3C/svg%%3E">
<style>%(fonts)s</style>
<style>%(page_css)s</style>
<style>%(chrome_css)s</style>
</head>
<body>
<div class="shell">

<header class="masthead">
  <span class="label">Noble Father Creations &middot; Volume XIII</span>
  <h1>The<br>Listening <em>Room</em></h1>
  <p class="lede">Everything Shae has made, in one place and free to play. The
    shelves are not genres &mdash; they are what a song is <em>for</em>: the
    reckoning, the descent, the frequency, the floor at 2am.</p>
  <p class="tally">
    <span><b class="num">%(count)d</b> tracks</span>
    <span><b class="num">%(hours)dh %(mins)dm</b> of it</span>
    <span><b class="num">%(shelfcount)d</b> shelves</span>
    <span>nothing to sign up for</span>
  </p>
</header>

<main class="room">
  <nav class="rail" aria-label="Shelves">
    <p class="rail-title label">The shelves</p>
    <div class="shelves">%(rail)s</div>
  </nav>

  <section class="stacks" aria-labelledby="shelfName">
    <div class="stacks-head">
      <h2 id="shelfName">The Whole Room</h2>
      <p class="shelf-blurb" id="shelfBlurb">Every track in the room, shelf by shelf.</p>
      <div class="search">
        %(search_icon)s
        <label class="sr" for="search">Search tracks</label>
        <input id="search" type="search" placeholder="Search titles&hellip;"
               autocomplete="off" spellcheck="false">
        <button type="button" class="search-clear" id="searchClear"
                aria-label="Clear search">%(x_icon)s</button>
        <kbd>/</kbd>
      </div>
      <p class="label" id="viewCount" style="margin-top:16px" aria-live="polite">%(count)d tracks</p>
    </div>
    <ol class="list" id="list"></ol>
    <p class="empty" id="empty" hidden>Nothing on this shelf matches that.</p>
  </section>
</main>

<section class="colophon" id="updates" aria-labelledby="updatesTitle">
  <div class="colophon-inner">
    <div>
      <span class="badge num">%(version)s &mdash; %(vdate)s</span>
      <h2 id="updatesTitle">What changed</h2>
      <p>Every version of this page gets a number and a date, so you can tell
        when something new landed without hunting for it.</p>
      <p>The running times here are measured from the audio files themselves,
        not typed in by hand. Where a track exists in more than one mix or
        version, both are kept &mdash; the suffix in the title tells you which.</p>
    </div>
    <ul class="changelog">%(log)s</ul>
  </div>
</section>

<footer class="foot">
  <p>Written, recorded and built by Shae Stovell &mdash;
    <a href="%(hub)s">Noble Father Creations</a>.</p>
  <p>This page asks nothing of you: no account, no tracking, no player that
    follows you around the internet. Press play or don't.</p>
</footer>
</div><!-- /.shell -->

<!-- ============ the deck ============ -->
<aside class="deck" id="deck" aria-label="Player">
  <div class="deck-line" aria-hidden="true"><i></i></div>
  <div class="deck-inner">
    <div class="sleeve" aria-hidden="true"></div>
    <button type="button" class="deck-open" id="deckOpen"
            aria-label="Open the now playing panel">
      <span class="deck-meta">
        <span class="deck-eyebrow" data-np="shelfName">&nbsp;</span>
        <span class="deck-title" data-np="title">Pick something</span>
        <span class="deck-sub" data-np="sub">%(count)d tracks waiting</span>
      </span>
    </button>
    <div class="deck-viz">%(viz)s</div>
    <div class="deck-scrub">%(scrub)s</div>
    <div class="deck-transport">%(transport)s</div>
    <div class="deck-vol">%(volume)s</div>
    <p class="deck-hint"><kbd>space</kbd> play &middot; <kbd>&larr;</kbd><kbd>&rarr;</kbd>
      seek &middot; <kbd>N</kbd> next &middot; <kbd>S</kbd> shuffle</p>
  </div>
</aside>

<!-- ============ the now-playing sheet (phones) ============ -->
<section class="sheet" id="sheet" aria-label="Now playing" aria-hidden="true">
  <button type="button" class="sheet-grip" id="sheetGrip"
          aria-label="Close now playing">%(down_icon)s</button>
  <div class="sheet-art"><div class="sleeve" aria-hidden="true"></div></div>
  <div class="sheet-meta">
    <p class="deck-eyebrow" data-np="shelfName">&nbsp;</p>
    <h2 class="deck-title" data-np="title">Pick something</h2>
    <p class="deck-sub" data-np="sub">&nbsp;</p>
  </div>
  <div class="sheet-controls">
    <div class="sheet-viz">%(viz2)s</div>
    <div>%(scrub2)s</div>
    <div class="sheet-transport">%(transport2)s</div>
    %(volume2)s
    <p class="sheet-keys"><kbd>space</kbd> play &middot; <kbd>&larr;</kbd><kbd>&rarr;</kbd>
      seek &middot; <kbd>N</kbd> next</p>
  </div>
</section>

<audio id="audio" preload="none"></audio>

<script type="application/json" id="catalogue-data">%(island)s</script>

<!-- ============ THE HOUSE ============ -->
<div id="nf-chrome" class="nf-chrome" data-nf-page="music">
<div class="nf-veil" aria-hidden="true"></div>
<button class="nf-seal" type="button" aria-expanded="false" aria-controls="nf-panel"
        aria-label="Open the Catalogue — Noble Father Creations">NF</button>
<div class="nf-scrim" aria-hidden="true"></div>
<nav class="nf-panel" id="nf-panel" aria-label="The Catalogue" aria-hidden="true">
<div class="nf-panel-head"><div><div class="nf-eyebrow">Noble Father Creations</div>
<h2 class="nf-panel-title">The Catalogue</h2></div>
<button class="nf-close" type="button" aria-label="Close the Catalogue">&#10005;</button></div>
<ul class="nf-toc">%(house)s</ul>
<div class="nf-panel-foot">Bound by hand in the study &mdash; fifteen volumes &amp; counting.</div>
</nav></div>

<script>%(chrome_js)s</script>
<script>%(page_js)s</script>
</body>
</html>
"""
    out = doc % {
        'count': len(tracks),
        'hours': hours,
        'mins': mins,
        'shelfcount': len(shelves),
        'fonts': fonts,
        'page_css': page_css,
        'chrome_css': chrome_css,
        'page_js': page_js,
        'chrome_js': chrome_js,
        'rail': ''.join(rail),
        'house': ''.join(rows),
        'log': ''.join(log),
        'island': json.dumps(island, ensure_ascii=False, separators=(',', ':')),
        'version': VERSION,
        'vdate': VERSION_DATE,
        'hub': HUB,
        'search_icon': icon('search'),
        'x_icon': icon('x'),
        'down_icon': icon('down'),
        'viz': viz,
        'viz2': viz,
        'scrub': scrub('seek'),
        'scrub2': scrub('seek'),
        'transport': transport(''),
        'transport2': transport(''),
        'volume': volume(),
        'volume2': volume(),
    }

    # the deck's prev/shuffle are wide-only; tag them after assembly so the
    # transport helper stays a single source of truth
    deck_start = out.index('<div class="deck-transport">')
    deck_end = out.index('</div>', out.index('data-act="shuffle"', deck_start))
    seg = out[deck_start:deck_end]
    seg2 = (seg.replace('class="tbtn" data-act="prev"', 'class="tbtn only-wide" data-act="prev"')
               .replace('class="tbtn" data-act="shuffle"', 'class="tbtn only-wide" data-act="shuffle"'))
    out = out[:deck_start] + seg2 + out[deck_end:]

    targets = [os.path.join(ROOT, 'deploy', 'music', 'index.html'),
               os.path.join(ROOT, 'source', 'projects', 'noble-father-music.html')]
    for p in targets:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(out)

    # ---- guards: fail loudly rather than shipping a broken page ----------
    problems = []
    if 'TRACKS is not defined' in out:
        problems.append('sentinel')
    if '"url":"/' in out or 'src="/audio' in out:
        problems.append('a root-relative audio path slipped in')
    for t in tracks[:5] + tracks[-5:]:
        if base + t['file'] not in out:
            problems.append('missing audio url for %s' % t['slug'])
    for marker in ('#REPLACE', 'data-here', 'TODO:', 'FIXME'):
        if marker in out:
            problems.append('build placeholder left in output: %s' % marker)
    if problems:
        sys.exit('BUILD FAILED: ' + '; '.join(problems))

    print('built %s  (%d tracks, %d shelves, %.1f KB)'
          % (', '.join(os.path.relpath(p, ROOT) for p in targets),
             len(tracks), len(shelves), len(out.encode()) / 1024))


if __name__ == '__main__':
    build()
