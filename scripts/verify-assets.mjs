#!/usr/bin/env node
/* =====================================================================
   verify-assets — is all the CONTENT actually there?

   WHY THIS EXISTS, SEPARATELY FROM THE OTHER TWO

   verify-live asks "does the page work?". verify-deployed asks "is the
   page the one we wrote?". Both can pass on a page that is quietly
   missing most of its content, and that has happened here twice:

   - The Listening Room served a page that loaded fine while 107 of its
     176 tracks 404'd, because the deploy tool silently caps out around
     450MB and each attempt atomically replaced the previous track set.
     The page looked right. Two thirds of the music was gone.
   - The Casting's photographs are the product. A partial image deploy is
     not a cosmetic problem, it is a shop with empty shelves.

   An inventory is only intact if every item in the manifest answers. So
   this walks the manifests and asks for every single file.

   USAGE
     node scripts/verify-assets.mjs            # music + casting
     node scripts/verify-assets.mjs music
     node scripts/verify-assets.mjs casting
     node scripts/verify-assets.mjs --sample 40    # spot-check N per set

   Exit non-zero if anything in an inventory is missing or the wrong size.
   ===================================================================== */

import { readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const execFileP = promisify(execFile);
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

const argv = process.argv.slice(2);
const SAMPLE = argv.includes('--sample')
  ? Number(argv[argv.indexOf('--sample') + 1]) || 0 : 0;
const WHICH = argv.filter((a) => !a.startsWith('-') && !/^\d+$/.test(a));
const want = (n) => (WHICH.length ? WHICH.includes(n) : true);

const C = process.stdout.isTTY
  ? { d: '\x1b[2m', r: '\x1b[0m', g: '\x1b[32m', y: '\x1b[33m', red: '\x1b[31m', b: '\x1b[1m' }
  : { d: '', r: '', g: '', y: '', red: '', b: '' };

/* One HEAD per file, with a ranged GET fallback: some CDN paths refuse
   HEAD outright, and a refusal must not be mistaken for a missing file. */
async function head(url) {
  const run = (args) => execFileP('curl', args, { maxBuffer: 1 << 22 })
    .then(({ stdout }) => stdout.trim()).catch(() => '');
  let out = await run(['-sS', '-o', '/dev/null', '-w', '%{http_code} %{size_download} %{header_json}',
    '-I', '-L', '--max-time', '45', url]);
  let code = Number(out.split(' ')[0]);
  let len = null;
  const m = out.match(/"content-length":\s*\[\s*"(\d+)"/i);
  if (m) len = Number(m[1]);
  if (code >= 200 && code < 400) return { code, len };

  out = await run(['-sS', '-o', '/dev/null', '-w', '%{http_code}',
    '-r', '0-0', '-L', '--max-time', '45', url]);
  code = Number(out);
  if (code === 206 || (code >= 200 && code < 400)) return { code: 200, len: null };
  return { code: code || 0, len: null };
}

async function inParallel(items, worker, width = 16) {
  const out = new Array(items.length);
  let i = 0;
  await Promise.all(Array.from({ length: Math.min(width, items.length) }, async () => {
    while (i < items.length) {
      const k = i++;
      out[k] = await worker(items[k], k);
    }
  }));
  return out;
}

function thin(list) {
  if (!SAMPLE || SAMPLE >= list.length) return list;
  const step = list.length / SAMPLE;
  return Array.from({ length: SAMPLE }, (_, k) => list[Math.floor(k * step)]);
}

const report = [];

/* ---------------------------------------------------------------- music */
async function music() {
  const mp = path.join(ROOT, 'deploy/music/MANIFEST.json');
  if (!existsSync(mp)) { console.log(`  ${C.y}?${C.r} music: no MANIFEST.json`); return; }
  const man = JSON.parse(await readFile(mp, 'utf8'));
  const base = man.audioBase;
  const all = man.tracks.map((t) => ({
    name: t.file, url: base + t.file, bytes: t.bytes, title: t.title,
  }));
  const list = thin(all);

  console.log(`\n${C.b}The Listening Room${C.r} ${C.d}— ${all.length} tracks in the manifest`
    + `${list.length !== all.length ? `, checking ${list.length}` : ''}${C.r}`);

  const res = await inParallel(list, async (t) => ({ t, ...(await head(t.url)) }));
  const missing = res.filter((r) => r.code !== 200);
  /* A track that answers but with the wrong length is a truncated upload --
     it plays for a few seconds and stops, which is worse than a 404
     because nothing reports it. */
  const wrongSize = res.filter((r) => r.code === 200 && r.len != null && r.len !== r.t.bytes);

  const okBytes = res.filter((r) => r.code === 200).reduce((a, r) => a + r.t.bytes, 0);
  console.log(`  playable      : ${res.length - missing.length} / ${list.length}`);
  console.log(`  ${C.d}audio served  : ${(okBytes / 1e6).toFixed(0)} MB${C.r}`);
  for (const r of missing.slice(0, 12)) {
    console.log(`  ${C.red}✗${C.r} ${r.code || 'no answer'}  ${r.t.name} ${C.d}${r.t.title}${C.r}`);
  }
  if (missing.length > 12) console.log(`  ${C.d}…and ${missing.length - 12} more${C.r}`);
  for (const r of wrongSize.slice(0, 8)) {
    console.log(`  ${C.red}✗${C.r} truncated  ${r.t.name} ${C.d}served ${r.len} of ${r.t.bytes} bytes${C.r}`);
  }
  report.push({ set: 'music', total: list.length, missing: missing.length,
                wrongSize: wrongSize.length });
}

/* -------------------------------------------------------------- casting */
async function casting() {
  /* The Casting lives in its own repo; its data file is the inventory. */
  const cand = ['/workspace/castings/data/statues.json',
                path.join(ROOT, 'deploy/casting/statues.json')];
  const dp = cand.find((p) => existsSync(p));
  if (!dp) {
    console.log(`\n${C.y}?${C.r} The Casting: data/statues.json not on disk`);
    console.log(`  ${C.d}clone github.com/NobleFatherCreations/castings to /workspace/castings to check it${C.r}`);
    report.push({ set: 'casting', skipped: true });
    return;
  }
  const raw = JSON.parse(await readFile(dp, 'utf8'));
  const pieces = raw.pieces || (Array.isArray(raw) ? raw : Object.values(raw)[0]);
  const ORIGIN = 'https://incandescent-kataifi-cde77d.netlify.app';

  /* Every size of every angle, because the srcset can hand any of them to
     a reader -- checking only the master would miss a whole missing tier. */
  const seen = new Set(), all = [];
  for (const p of pieces) {
    for (const a of p.angles || []) {
      for (const u of [a.master, ...(a.sizes || []).map((s) => s.src)]) {
        if (u && !seen.has(u)) { seen.add(u); all.push({ name: u, url: ORIGIN + u, id: p.id }); }
      }
    }
  }
  const list = thin(all);
  console.log(`\n${C.b}The Casting${C.r} ${C.d}— ${pieces.length} pieces, ${all.length} image files`
    + `${list.length !== all.length ? `, checking ${list.length}` : ''}${C.r}`);

  const res = await inParallel(list, async (t) => ({ t, ...(await head(t.url)) }), 20);
  const missing = res.filter((r) => r.code !== 200);
  console.log(`  reachable     : ${res.length - missing.length} / ${list.length}`);
  const badPieces = [...new Set(missing.map((r) => r.t.id))];
  for (const r of missing.slice(0, 12)) {
    console.log(`  ${C.red}✗${C.r} ${r.code || 'no answer'}  ${r.t.name}`);
  }
  if (missing.length > 12) console.log(`  ${C.d}…and ${missing.length - 12} more${C.r}`);
  if (badPieces.length) console.log(`  ${C.red}pieces affected: ${badPieces.slice(0, 20).join(', ')}${C.r}`);
  report.push({ set: 'casting', total: list.length, missing: missing.length,
                pieces: pieces.length });
}

console.log(`\n${C.b}Noble Father Creations — is all the content actually there?${C.r}`);
if (want('music')) await music();
if (want('casting')) await casting();

console.log(`\n${C.b}── summary ─────────────────────────────────────────${C.r}`);
let bad = 0;
for (const r of report) {
  if (r.skipped) { console.log(`  ${r.set.padEnd(8)} skipped — inventory not on disk`); continue; }
  const problems = (r.missing || 0) + (r.wrongSize || 0);
  bad += problems;
  const mark = problems ? `${C.red}✗${C.r}` : `${C.g}✓${C.r}`;
  console.log(`  ${mark} ${r.set.padEnd(8)} ${r.total - (r.missing || 0)}/${r.total} present`
    + (r.wrongSize ? `, ${r.wrongSize} truncated` : ''));
}
if (bad) {
  console.log(`\n${C.red}${C.b}Content is missing from a live site.${C.r}`);
  console.log(`${C.d}  Music and The Casting both exceed what the MCP deploy tool can upload in`);
  console.log(`  one zip (~450MB). Use netlify-cli, which sends only changed files:`);
  console.log(`    netlify deploy --prod --dir=<publish dir> --site=<siteId>${C.r}\n`);
  process.exit(1);
}
console.log(`\n${C.g}${C.b}Every item in every inventory is present and the right size.${C.r}\n`);
