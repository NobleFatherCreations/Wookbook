# deploy/music — The Listening Room

This directory is the **whole** deployable payload for the `noblemusic` Netlify
site, which is served at its own address and, through the hub's proxy rewrite, at
`noblefathercreations.com/music`.

```
deploy/music/
  index.html      generated — do not hand-edit (see "Rebuilding")
  _headers        CORS for /audio/* so the frequency display can read the audio
  MANIFEST.json   the catalogue: every track's Drive id, size, duration, title
  audio/          176 mp3s — GITIGNORED, not in the repo (1.26 GB)
```

## NOT DEPLOYED YET

Nothing here has been pushed or deployed. The user asked for deploying to stop
until everything is verified. When that go-ahead comes, treat it as a production
write and get it explicitly.

## Rebuilding the page

`index.html` is generated. Edit the sources, never the output:

| Edit this | For |
| --- | --- |
| `scripts/music/page.css` | layout, type, motion |
| `scripts/music/page.js` | player, catalogue, visualisation |
| `scripts/music/chrome.css` / `chrome.js` | the seal + THE HOUSE drawer |
| `scripts/build-music.py` | page structure, THE HOUSE list, version + changelog |
| `MANIFEST.json` | track titles, shelves, durations |

```sh
python3 scripts/build-music.py
```

That writes **two identical files**: this `index.html` and
`source/projects/noble-father-music.html` (the committed copy registered as
`localSource` in `sites.json`). The build refuses to finish if a root-relative
audio path or a `#REPLACE`-style placeholder made it into the output.

## Why the source is committed

The previous version of this page had no local source anywhere in the repo. Its
entire `TRACKS`/`SHELVES` catalogue was lost in some earlier deploy — the live
file used `TRACKS` 8 times and `SHELVES` 3 times and declared neither, so
`TRACKS is not defined` threw on load and the page rendered as an empty shell.
See `AUDIT-2026-08-12.md`. Everything needed to rebuild is now in git.

## The one hard rule: absolute audio URLs

Every audio URL is absolute:

```
https://noblemusic.netlify.app/audio/<slug>.mp3
```

A root-relative `/audio/foo.mp3` resolves against **whichever host is in the
address bar**. Through the `/music` proxy that is `noblefathercreations.com`,
which has no `/audio`, so every track 404s. This is exactly what broke the
Casting site twice on 2026-08-12. Absolute URLs work from both addresses.

`audioBase` in `MANIFEST.json` is asserted to start with `https://` at build time.

## Deploying (when approved)

A plain static upload of this directory to the `noblemusic` site
(`netlifySiteId: 05683d2c-cb07-43cb-8e2c-d8cd380c0287`). It has **no connected
GitHub repo** (`commit_ref: null`), so a git push cannot update it — it needs a
direct Netlify deploy of this folder as the publish directory.

The audio is ~1.26 GB across 176 files; expect the first upload to be slow.

## Restoring `audio/` from Drive

The mp3s are gitignored. `MANIFEST.json` has a `driveId`, `file` and `bytes` for
every track, so the folder is fully reproducible:

```sh
mkdir -p deploy/music/audio
python3 - <<'EOF'
import json, subprocess
m = json.load(open('deploy/music/MANIFEST.json'))
for t in m['tracks']:
    subprocess.run(['curl', '-sSL',
        'https://drive.google.com/uc?export=download&id=' + t['driveId'],
        '-o', 'deploy/music/audio/' + t['file']], check=True)
EOF
```

Then verify each file is real audio and the right size:

```sh
python3 - <<'EOF'
import json, os, subprocess
m = json.load(open('deploy/music/MANIFEST.json'))
for t in m['tracks']:
    p = 'deploy/music/audio/' + t['file']
    size = os.path.getsize(p)
    kind = subprocess.run(['file','-b',p], capture_output=True, text=True).stdout.strip()
    if size != t['bytes'] or 'Audio' not in kind:
        print('BAD', t['file'], size, t['bytes'], kind)
EOF
```

Source Drive folder: `14TecSqJSZOlYlT7bHPsKqBdHsGdUC0ea` ("MP3 music"), publicly
link-readable. Files over ~100 MB return a virus-scan interstitial instead of
bytes and need the `confirm`/`uuid` form re-posted — none of these tracks are
that large (the biggest is ~13 MB).

## Provenance of the data

- **Durations and byte sizes are measured** from the audio with `ffprobe`. None
  are estimated.
- **Titles are derived from the Drive filenames.** The ID3 tags carry only a
  Suno `comment`; 173 of 176 files have no title tag. Mix and version suffixes
  are preserved (`· Version 2`, `(Remastered)`, `(Chuckee Cheesin Mix)`).
- **`created` and `sunoId` are read** from that ID3 comment. `sunoId` is what
  identified 7 pairs of files that were the same generation saved under two
  names; each pair was collapsed to one track and the other name kept in
  `alsoKnownAs`.
- **Shelf assignment is inferred** from title keywords. It is the one editorial
  layer here — there is no genre metadata in these files.
