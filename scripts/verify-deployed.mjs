#!/usr/bin/env node
/* =====================================================================
   verify-deployed — is what we committed actually the thing on the web?

   WHY THIS EXISTS

   Nearly every bad afternoon on this project has had the same shape: the
   repo was right, production was wrong, and nothing said so. The music
   page was rebuilt and sat undeployed while the live one threw on load.
   The Portals torch fix was written, committed, and never shipped. The
   /statues proxy rule existed here while ten links 404'd out there. The
   Fracture rename was done in source and stale on eleven live sites.

   None of those were hard problems. They were all the same invisible one:
   deploying is a separate manual act that leaves no receipt, so "fixed"
   and "shipped" drift apart silently and nobody finds out until a reader
   does.

   verify-live.mjs asks "does the live page work?". This asks the other
   question, the one that kept biting: "is the live page the one we
   actually wrote?" Run it and you cannot not know.

   USAGE
     node scripts/verify-deployed.mjs           # every project
     node scripts/verify-deployed.mjs music     # one, by slug
     node scripts/verify-deployed.mjs --quiet   # only report drift

   Exit code is non-zero if anything has drifted, so it can gate a deploy.
   ===================================================================== */

import { readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const execFileP = promisify(execFile);
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

const args = process.argv.slice(2);
const QUIET = args.includes('--quiet');
const ONLY = args.filter((a) => !a.startsWith('-'));

const C = process.stdout.isTTY
  ? { d: '\x1b[2m', r: '\x1b[0m', g: '\x1b[32m', y: '\x1b[33m', red: '\x1b[31m', b: '\x1b[1m' }
  : { d: '', r: '', g: '', y: '', red: '', b: '' };

/* The browser cannot reach these hosts from inside the sandbox but curl
   can, through the agent proxy -- same reason verify-live falls back to it. */
async function fetchLive(url) {
  try {
    const { stdout } = await execFileP('curl', [
      '-sS', '--compressed', '-L', '--max-time', '90',
      '-A', 'Mozilla/5.0 (verify-deployed)', url,
    ], { maxBuffer: 1 << 29 });
    return stdout;
  } catch {
    return null;
  }
}

/* Byte-equality is the honest test for the books: each is a single
   self-contained file, so the file we committed IS the deployable. Where
   that is not true the reason is recorded per project, not papered over. */
function compare(localText, liveText) {
  if (liveText === null) return { state: 'unreachable' };
  if (localText === liveText) return { state: 'sync' };

  const lb = Buffer.byteLength(localText), wb = Buffer.byteLength(liveText);
  let i = 0;
  const max = Math.min(localText.length, liveText.length);
  while (i < max && localText[i] === liveText[i]) i++;
  const line = localText.slice(0, i).split('\n').length;
  const near = (s) => s.slice(i, i + 60).replace(/\s+/g, ' ').trim();
  return {
    state: 'drift', localBytes: lb, liveBytes: wb, delta: lb - wb,
    atLine: line, localAt: near(localText), liveAt: near(liveText),
  };
}

const sites = JSON.parse(await readFile(path.join(ROOT, 'sites.json'), 'utf8'));

/* One flat list out of the three places a deployable can be described. */
const targets = [
  { slug: 'hub', title: sites.hub.title, url: sites.hub.url,
    localSource: sites.hub.localSource, note: sites.hub.deployNote },
  ...sites.projects.map((p) => ({
    slug: p.slug, title: p.title, url: p.url,
    localSource: p.localSource, note: p.deployNote,
  })),
  ...(sites.craftBusiness || []).map((c) => ({
    slug: c.netlifySite, title: c.title, url: c.url,
    localSource: c.localSource, note: c.deployNote,
  })),
].filter((t) => (ONLY.length ? ONLY.includes(t.slug) : true));

console.log(`\n${C.b}Noble Father Creations — is the repo what is live?${C.r}`);
console.log(`${C.d}  comparing each project's committed source against the bytes being served${C.r}\n`);

const drifted = [], unreachable = [], unchecked = [], synced = [];

for (const t of targets) {
  const label = (t.slug || '?').padEnd(14);

  if (!t.localSource) {
    unchecked.push({ ...t, why: 'no localSource recorded in sites.json' });
    if (!QUIET) console.log(`  ${C.y}?${C.r}  ${label} ${C.d}no local source recorded — nothing to compare${C.r}`);
    continue;
  }
  const abs = path.join(ROOT, t.localSource);
  if (!existsSync(abs)) {
    unchecked.push({ ...t, why: `localSource missing on disk: ${t.localSource}` });
    if (!QUIET) console.log(`  ${C.y}?${C.r}  ${label} ${C.d}${t.localSource} is not in this repo${C.r}`);
    continue;
  }

  const [local, live] = [await readFile(abs, 'utf8'), await fetchLive(t.url)];
  const r = compare(local, live);

  if (r.state === 'sync') {
    synced.push(t);
    if (!QUIET) console.log(`  ${C.g}✓${C.r}  ${label} ${C.d}live matches ${t.localSource}${C.r}`);
  } else if (r.state === 'unreachable') {
    unreachable.push(t);
    console.log(`  ${C.y}!${C.r}  ${label} ${C.y}could not fetch ${t.url}${C.r}`);
  } else {
    drifted.push({ ...t, ...r });
    const dir = r.delta > 0 ? `repo has ${r.delta} bytes MORE` : `live has ${-r.delta} bytes more`;
    console.log(`  ${C.red}✗${C.r}  ${label} ${C.red}DRIFTED${C.r} — ${dir}`);
    console.log(`     ${C.d}first difference around line ${r.atLine}${C.r}`);
    console.log(`     ${C.d}repo: ${r.localAt || '(end of file)'}${C.r}`);
    console.log(`     ${C.d}live: ${r.liveAt || '(end of file)'}${C.r}`);
    if (t.note) console.log(`     ${C.d}deploy note: ${t.note.split('.')[0]}.${C.r}`);
  }
}

console.log(`\n${C.b}── summary ─────────────────────────────────────────${C.r}`);
console.log(`  in sync    : ${synced.length}`);
console.log(`  drifted    : ${drifted.length}`);
console.log(`  unreachable: ${unreachable.length}`);
console.log(`  unchecked  : ${unchecked.length}`);

if (drifted.length) {
  console.log(`\n${C.red}${C.b}These are fixed here and NOT fixed for a reader:${C.r}`);
  for (const d of drifted) console.log(`  · ${d.slug} — ${d.url}`);
  console.log(`\n${C.d}  A commit is not a deploy. Ship these, then run this again.${C.r}\n`);
  process.exit(1);
}
if (unreachable.length) {
  console.log(`\n${C.y}Some sites could not be reached, so drift is unknown for them.${C.r}\n`);
  process.exit(2);
}
console.log(`\n${C.g}${C.b}Every project with a committed source is live as committed.${C.r}\n`);
