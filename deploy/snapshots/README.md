# deploy/snapshots — captured baselines for sites with no source

Every file here is a **byte capture of what a live site was serving**, not a
source file. The distinction matters and the tooling keeps it:

| kind | meaning | who wins on drift |
| --- | --- | --- |
| `localSource` | the file we edit and deploy. The repo is the truth. | the repo — ship it |
| `liveSnapshot` | a capture of a site whose source we do not have. | unknown — investigate |

## Why these exist

Some sites were deployed straight to Netlify and their source was never
kept anywhere. That is not a filing problem, it is a data-loss problem:
`The Listening Room` lost its entire 176-track catalogue exactly this way,
and the page shipped as an empty shell that threw on load until it was
rebuilt from Google Drive. `playbook` had no local source of any kind.

A capture fixes the worse half of that immediately. If one of these Netlify
sites were deleted tomorrow, the page is still here and still deployable.

## What a snapshot does NOT give you

It is not a source you can confidently edit. It is minified/assembled
output, and for `noblereactionmap` there is also a much larger
`source/projects/noble-father-reaction-map.html` (2.9 MB vs 187 KB live)
which is a *different lineage*, not a newer copy of the same thing —
nobody has established which one is intended to be live. That question is
open and recorded in MEMORY.md; do not resolve it by overwriting either
side.

## How the checks treat them

`node scripts/verify-deployed.mjs` compares live against whichever of the
two a project declares:

- against a `localSource`, a difference means **the repo is not shipped**
  and the fix is to deploy.
- against a `liveSnapshot`, a difference means **the site changed and we
  do not know why** — nobody here edited a source, because there isn't
  one. Investigate before touching anything, then re-capture deliberately:

```sh
node scripts/snapshot.mjs nfchq      # re-capture one, on purpose
node scripts/snapshot.mjs --all      # re-baseline everything
```

Re-capturing is an explicit act precisely so drift cannot be silenced by
accident.

## Retiring a snapshot

When a real source appears for one of these, move the project from
`liveSnapshot` to `localSource` in `sites.json` and delete the capture. A
snapshot is scaffolding, not a destination.
