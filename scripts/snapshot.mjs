#!/usr/bin/env node
/* =====================================================================
   snapshot — re-baseline a site that has no source, deliberately.

   Some sites were deployed straight to the host and their source was
   never kept. For those, sites.json records a `liveSnapshot`: a byte
   capture, so the page is recoverable if the host loses it and so
   verify-deployed can tell when it changed.

   Re-capturing has to be an explicit act. If drift could be cleared by
   the same command that runs the check, the check would quietly rubber
   stamp every change and mean nothing -- which is the failure mode this
   whole set of scripts exists to prevent.

     node scripts/snapshot.mjs nfchq        # one project, by slug
     node scripts/snapshot.mjs --all        # re-baseline everything
     node scripts/snapshot.mjs --list       # what is snapshot-backed

   Before re-baselining, know WHY the page changed. If you cannot say,
   do not run this.
   ===================================================================== */

import { readFile, writeFile } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const execFileP = promisify(execFile);
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const argv = process.argv.slice(2);
const ALL = argv.includes('--all');
const LIST = argv.includes('--list');
const picks = argv.filter((a) => !a.startsWith('-'));

const sites = JSON.parse(await readFile(path.join(ROOT, 'sites.json'), 'utf8'));
const all = [
  ...sites.projects.map((p) => ({ slug: p.slug, url: p.url, snap: p.liveSnapshot })),
  ...(sites.craftBusiness || []).map((c) => ({ slug: c.netlifySite, url: c.url, snap: c.liveSnapshot })),
].filter((t) => t.snap);

if (LIST || (!ALL && !picks.length)) {
  console.log('\nSnapshot-backed sites (no source exists for these):\n');
  for (const t of all) console.log(`  ${t.slug.padEnd(18)} ${t.snap}\n${' '.repeat(20)}${t.url}`);
  console.log(`\n  ${all.length} total. Re-capture one with:  node scripts/snapshot.mjs <slug>\n`);
  process.exit(0);
}

const todo = ALL ? all : all.filter((t) => picks.includes(t.slug));
if (!todo.length) {
  console.error(`\nNothing matched. Known: ${all.map((t) => t.slug).join(', ')}\n`);
  process.exit(1);
}

for (const t of todo) {
  const dest = path.join(ROOT, t.snap);
  const { stdout } = await execFileP('curl', [
    '-sS', '--compressed', '-L', '--max-time', '180',
    '-w', '\\n%{http_code}', t.url,
  ], { maxBuffer: 1 << 29 }).catch(() => ({ stdout: '' }));

  const cut = stdout.lastIndexOf('\n');
  const code = Number(stdout.slice(cut + 1));
  const body = stdout.slice(0, cut);
  if (code !== 200 || !body) {
    console.log(`  ✗ ${t.slug}: fetch failed (${code || 'no answer'}) — baseline left alone`);
    continue;
  }
  const before = await readFile(dest, 'utf8').catch(() => null);
  await writeFile(dest, body);
  const delta = before === null ? 'new capture'
    : before === body ? 'no change'
    : `${Buffer.byteLength(body) - Buffer.byteLength(before)} bytes different`;
  console.log(`  ✓ ${t.slug.padEnd(18)} ${Buffer.byteLength(body)} bytes  (${delta})`);
}
console.log('\nCommit the change so the new baseline is the one everyone checks against.\n');
