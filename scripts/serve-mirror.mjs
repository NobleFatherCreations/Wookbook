#!/usr/bin/env node
/* =====================================================================
   serve-mirror.mjs — serve the WHOLE site tree from local sources, at the
   same paths the hub serves them, so `verify-live.mjs` can gate a round
   BEFORE anything is deployed.

       node scripts/serve-mirror.mjs 8099
       node scripts/verify-live.mjs http://localhost:8099

   Routes mirror source/projects/noble-father-catalogue._redirects. Each
   book is a single self-contained HTML file, so the mapping is one line
   per project; The Casting is the one real multi-file site and is served
   from its own repo checkout, including the root-relative /assets, /data
   and /statues prefixes it owns.

   `--fetch-missing` pulls any route with no local source (currently only
   /playbook) from live once and caches it under .mirror-cache/, so the
   gate can still cover it. That gap is itself a finding: a live-only file
   is how the music catalogue was lost.
   ===================================================================== */

import { createServer } from 'node:http';
import { readFile, stat, mkdir, writeFile } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const execFileP = promisify(execFile);
const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CASTINGS = process.env.CASTINGS_DIR || '/workspace/castings';
const CACHE = path.join(REPO, '.mirror-cache');

const PORT = Number(process.argv.find((a) => /^\d+$/.test(a)) || 8099);
const FETCH_MISSING = process.argv.includes('--fetch-missing');

/* One entry per proxied path in the hub's _redirects. Values are repo-relative
   files; `null` means there is no local source (see --fetch-missing). */
const ROUTES = {
  '/':            'source/projects/noble-father-catalogue.html',
  '/feminine':    'source/projects/noble-father-sovereign.html',
  '/children':    'source/projects/noble-father-playground.html',
  '/wook':        'source/projects/noble-father-festival.html',      // Festie CODEX
  '/fractal':     'source/projects/noble-father-fractal.html',
  '/fracture':    'source/projects/noble-father-fracture.html',
  '/faith':       'source/projects/faith-index.html',
  '/loop':        'fixes/loop.html',
  '/scale':       'fixes/scale.html',
  '/playbook':    null,                                             // live-only
  '/shadowroot':  'source/projects/noble-father-root.html',
  '/music':       'deploy/music/index.html',
  '/portals':     'source/projects/noble-father-portals.html',
  '/press':       'source/projects/noble-father-seals.html',
  '/festival':    'source/projects/noble-father-festiebible.html',   // Festie BIBLE
  '/resin':       path.join(CASTINGS, 'index.html'),
};
const LIVE_FOR = { '/playbook': 'https://noblepatterns.netlify.app/' };

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.webp': 'image/webp',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
  '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.woff2': 'font/woff2',
  '.mp3': 'audio/mpeg', '.m4a': 'audio/mp4', '.wav': 'audio/wav',
  '.xml': 'application/xml; charset=utf-8', '.txt': 'text/plain; charset=utf-8',
  '.avif': 'image/avif', '.gif': 'image/gif',
};

async function exists(p) { try { await stat(p); return true; } catch { return false; } }

async function fetchMissing(route) {
  const url = LIVE_FOR[route];
  if (!url) return null;
  await mkdir(CACHE, { recursive: true });
  const dest = path.join(CACHE, route.slice(1) + '.html');
  if (await exists(dest)) return dest;
  if (!FETCH_MISSING) return null;
  process.stdout.write(`  fetching ${route} from ${url} (no local source) ... `);
  try {
    const { stdout } = await execFileP('curl',
      ['-sS', '-L', '--compressed', '--max-time', '90', url],
      { maxBuffer: 1 << 28, encoding: 'buffer' });
    await writeFile(dest, stdout);
    console.log(`${stdout.length} bytes -> ${path.relative(REPO, dest)}`);
    return dest;
  } catch (e) { console.log('failed: ' + e.message); return null; }
}

/* Resolve a request path to a file on disk. */
async function resolveFile(pathname) {
  const clean = decodeURIComponent(pathname.split('?')[0]).replace(/\/+$/, '') || '/';

  /* The Casting owns three root prefixes; see the _redirects comment. */
  if (/^\/(assets|data|statues)(\/|$)/.test(clean)) {
    const abs = path.join(CASTINGS, path.normalize(clean));
    if (!abs.startsWith(CASTINGS)) return null;
    if (await exists(abs)) {
      const s = await stat(abs);
      if (s.isDirectory()) {
        const idx = path.join(abs, 'index.html');
        if (await exists(idx)) return idx;
      } else return abs;
    }
    /* /statues and /statues/:id both serve the gallery, as they do on Netlify. */
    if (/^\/statues(\/[^/]*)?$/.test(clean)) return path.join(CASTINGS, 'statues/index.html');
    return null;
  }
  for (const f of ['/sitemap.xml', '/robots.txt', '/netlify.toml']) {
    if (clean === f) return path.join(CASTINGS, f.slice(1));
  }

  /* The music page references its audio at an absolute origin; verify-live
     rewrites that origin onto this mirror, which lands here. */
  if (/^\/audio\//.test(clean)) {
    const abs = path.join(REPO, 'deploy/music', path.normalize(clean));
    return (await exists(abs)) ? abs : null;
  }

  /* Alternate spellings kept as real 301s on the hub — treat as the target. */
  if (clean === '/portal') return resolveFile('/portals');
  if (clean === '/seals') return resolveFile('/press');

  const route = clean === '' ? '/' : clean;
  if (route in ROUTES) {
    const v = ROUTES[route];
    if (v === null) return fetchMissing(route);
    const abs = path.isAbsolute(v) ? v : path.join(REPO, v);
    return (await exists(abs)) ? abs : null;
  }
  /* /slug/* — every book is one file, so anything under a book slug that is
     not a real file is the book itself (matching the /slug/* rewrite). */
  const seg = '/' + route.split('/')[1];
  if (seg in ROUTES && ROUTES[seg]) {
    const v = ROUTES[seg];
    if (path.isAbsolute(v)) {
      const abs = path.join(path.dirname(v), path.normalize(route.slice(seg.length)));
      if (await exists(abs)) return abs;
    }
    return resolveFile(seg);
  }
  return null;
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');
  let file = null;
  try { file = await resolveFile(url.pathname); } catch { /* 404 below */ }
  if (!file) {
    res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
    return res.end(`404 ${url.pathname}\n`);
  }
  let body;
  try { body = await readFile(file); }
  catch { res.writeHead(404).end('404\n'); return; }
  const type = TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream';
  const headers = {
    'content-type': type,
    'content-length': body.length,
    /* deploy/music/_headers sets this live; the analyser needs it. */
    'access-control-allow-origin': '*',
    'cache-control': 'no-store',
  };
  if (req.method === 'HEAD') { res.writeHead(200, headers); return res.end(); }
  res.writeHead(200, headers);
  res.end(body);
});

/* Report which routes have no local source before serving anything. */
const missing = [];
for (const [r, v] of Object.entries(ROUTES)) {
  if (v === null) { missing.push(r); continue; }
  const abs = path.isAbsolute(v) ? v : path.join(REPO, v);
  if (!(await exists(abs))) missing.push(`${r} (${v} not found)`);
}
if (missing.length) console.log(`! no local source: ${missing.join(', ')}`);
if (!(await exists(path.join(CASTINGS, 'index.html')))) {
  console.log(`! The Casting checkout not found at ${CASTINGS} — /resin, /statues, /assets, /data will 404`);
}
for (const r of Object.keys(LIVE_FOR)) await fetchMissing(r);

server.listen(PORT, () => console.log(`mirror on http://localhost:${PORT}`));
