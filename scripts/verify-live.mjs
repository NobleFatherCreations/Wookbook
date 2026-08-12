#!/usr/bin/env node
/* =====================================================================
   verify-live.mjs — the pre-deploy gate for Noble Father Creations.

     node scripts/verify-live.mjs                      # live
     node scripts/verify-live.mjs http://localhost:8099 # a mirror
     npm run verify -- http://localhost:8099

   Every check here exists because something shipped broken without it.
   Nothing in this file infers from source; it renders each page in
   Chromium and measures. Exit code is non-zero if anything fails.

     1  HTTP 200
     2  zero pageerror / console error / request failure
          -> `TRACKS is not defined` (music) and the Festie Bible's lost
             SCENARIO_INDEX were both undeclared data consts. A page that
             throws is a page that shipped empty.
     3  every internal link resolves (crawled one level deep)
          -> /statues 404'd through the hub while the CSS loaded fine, so
             the fix "looked" complete and every button on the page was dead.
     4  every subresource 200s
     5  a way out to the hub exists, and which nav generation it uses
          -> three generations shipped simultaneously (nf-seal / nh-* / none)
     6  no horizontal overflow
     7  nothing stuck invisible
     8  one canonical name per project
     9  a few per-page structural asserts (see PAGE_ASSERTS)

   Run at 1440x900, at 390x844 with isMobile+hasTouch, and once under
   reducedMotion:'reduce'. The touch context is not optional: a narrow
   viewport ALONE still reports `hover: hover`, which is exactly why a
   touch-only Portals bug was wrongly called unreproducible.

   Chromium only in this environment. Never run `playwright install`.
   ===================================================================== */

import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { readFile, writeFile, mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const execFileP = promisify(execFile);
const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..');

/* Playwright is a symlink in ./node_modules here, but resolve the global
   install too so the script runs from anywhere in this environment. */
let chromium;
try {
  ({ chromium } = await import('playwright'));
} catch {
  ({ chromium } = await import('/opt/node22/lib/node_modules/playwright/index.mjs'));
}

/* ---------------------------------------------------------------- args */

const argv = process.argv.slice(2);
const flags = new Map();
let baseArg = null;
for (const a of argv) {
  if (a.startsWith('--')) {
    const [k, v] = a.slice(2).split('=');
    flags.set(k, v === undefined ? true : v);
  } else baseArg = a;
}
const BASE = (baseArg || flags.get('base') || 'https://noblefathercreations.com').replace(/\/$/, '');
const BASE_ORIGIN = new URL(BASE + '/').origin;
const IS_LOCAL = /^(localhost|127\.0\.0\.1|\[::1\])(:|$)/.test(new URL(BASE + '/').host);
const DEPTH = Number(flags.get('depth') ?? 1);
const SUBPAGES = Number(flags.get('subpages') ?? 2);   // rendered sub-pages per seed
const NAV_TIMEOUT = Number(flags.get('timeout') ?? 90000);
const ONLY = flags.get('only') ? String(flags.get('only')).split(',') : null;
const JSON_OUT = flags.get('json') || null;
const VERBOSE = !!flags.get('verbose');

const ALL_TARGETS = [
  '/', '/feminine', '/children', '/wook', '/fractal', '/fracture', '/faith',
  '/loop', '/scale', '/playbook', '/shadowroot', '/music', '/portals',
  '/press', '/festival', '/resin',
];
const TARGETS = flags.get('pages')
  ? String(flags.get('pages')).split(',').map((p) => (p.startsWith('/') ? p : '/' + p))
  : ALL_TARGETS;

/* Hosts that are "us". A link to any of these is an internal link, and in
   mirror mode it is rewritten onto BASE so the mirror answers it. The list
   comes from sites.json so a new project cannot be silently left out. */
const HUB_HOSTS = new Set(['noblefathercreations.com', 'www.noblefathercreations.com']);
const PROJECT_HOSTS = new Set();
try {
  const reg = JSON.parse(await readFile(path.join(REPO, 'sites.json'), 'utf8'));
  const walk = (v) => {
    if (Array.isArray(v)) v.forEach(walk);
    else if (v && typeof v === 'object') {
      if (typeof v.url === 'string') {
        try { PROJECT_HOSTS.add(new URL(v.url).host); } catch { /* not a url */ }
      }
      if (typeof v.netlifySite === 'string') PROJECT_HOSTS.add(v.netlifySite + '.netlify.app');
      Object.values(v).forEach(walk);
    }
  };
  walk(reg);
} catch (e) {
  console.error('! could not read sites.json for the host list:', e.message);
}
PROJECT_HOSTS.add('noblemusic.netlify.app');      // the audio origin, absolute by design
for (const h of HUB_HOSTS) PROJECT_HOSTS.add(h);

/* Only in mirror mode do we pretend our own netlify hosts live on BASE. */
function rewriteToBase(u) {
  try {
    const url = new URL(u);
    if (url.origin === BASE_ORIGIN) return url.href;
    if (HUB_HOSTS.has(url.host) || (IS_LOCAL && PROJECT_HOSTS.has(url.host))) {
      return BASE + url.pathname + url.search;
    }
    return null;   // external — not ours to assert on
  } catch { return null; }
}

/* ----------------------------------------------------------- transport */
/* Chromium in this sandbox cannot open an outbound socket (measured:
   ERR_CONNECTION_RESET on every https origin, including example.com) while
   `curl` reaches out fine through the agent proxy. So when the browser
   can't reach BASE, every request is fulfilled from curl instead. That is
   what makes a live run possible here at all — and it is transparent, so
   the same script works unchanged wherever the browser does have a network. */

const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' +
          'Chrome/126.0.0.0 Safari/537.36 nfc-verify/1';
let TMP;

async function curlOnce(args) {
  try {
    const { stdout } = await execFileP('curl', args, { maxBuffer: 1 << 28 });
    return stdout;
  } catch (e) {
    return null;
  }
}

async function curlStatus(url) {
  for (let i = 0; i < 3; i++) {
    const out = await curlOnce(['-sS', '-o', '/dev/null', '-w', '%{http_code}',
      '-A', UA, '-L', '--max-time', '45', '-I', url]);
    const code = Number(out);
    if (code >= 200 && code < 400) return code;
    /* HEAD is refused by some handlers; a 1-byte range GET settles it. */
    const out2 = await curlOnce(['-sS', '-o', '/dev/null', '-w', '%{http_code}',
      '-A', UA, '-L', '--max-time', '45', '-r', '0-0', url]);
    const code2 = Number(out2);
    if (code2 === 206) return 200;
    if (code2 >= 200 && code2 < 400) return code2;
    if (code >= 400 || code2 >= 400) return Math.max(code, code2);
    await new Promise((r) => setTimeout(r, 500 * (i + 1)));   // proxy hiccup
  }
  return 0;
}

async function curlBody(url) {
  const stem = path.join(TMP, 'r' + Math.random().toString(36).slice(2));
  for (let i = 0; i < 3; i++) {
    const out = await curlOnce(['-sS', '--compressed', '-A', UA, '-L',
      '--max-time', '120', '-D', stem + '.h', '-o', stem + '.b',
      '-w', '%{http_code}', url]);
    const code = Number(out);
    if (!code) { await new Promise((r) => setTimeout(r, 500 * (i + 1))); continue; }
    const rawH = await readFile(stem + '.h', 'utf8').catch(() => '');
    const body = await readFile(stem + '.b').catch(() => Buffer.alloc(0));
    const headers = {};
    /* -L leaves every hop in the dump; the last block is the real one. */
    const block = rawH.trim().split(/\r?\n\r?\n/).pop() || '';
    for (const line of block.split(/\r?\n/).slice(1)) {
      const m = /^([^:]+):\s*(.*)$/.exec(line);
      if (!m) continue;
      const k = m[1].toLowerCase();
      /* curl already decompressed and dechunked; passing these on lies to
         Chromium about the bytes it is being handed. */
      if (['content-encoding', 'content-length', 'transfer-encoding',
           'connection', 'keep-alive'].includes(k)) continue;
      headers[k] = m[2];
    }
    return { status: code, headers, body };
  }
  return null;
}

async function nativeStatus(url) {
  for (const method of ['HEAD', 'GET']) {
    try {
      const r = await fetch(url, { method, redirect: 'follow' });
      if (r.body) await r.body.cancel().catch(() => {});
      if (method === 'HEAD' && (r.status === 405 || r.status === 501)) continue;
      return r.status;
    } catch { /* try GET, then give up */ }
  }
  return 0;
}

let VIA_CURL = !!flags.get('via-curl');
const statusOf = (u) => (VIA_CURL ? curlStatus(u) : nativeStatus(u));

/* -------------------------------------------------------- page asserts */
/* Small structural facts that a render can prove and a diff cannot. These
   are the specific regressions this round fixed, kept as permanent guards. */

const PAGE_ASSERTS = {
  '/music': [{
    name: 'catalogue rendered (176 rows, 6 shelves)',
    when: 'all',
    fn: () => {
      const rows = document.querySelectorAll('.row').length;
      const shelves = document.querySelectorAll('[data-shelf]').length - 1;  // minus "all"
      if (rows !== 176) return `expected 176 .row, found ${rows}`;
      if (shelves !== 6) return `expected 6 shelves, found ${shelves}`;
      return null;
    },
  }, {
    name: 'no root-relative audio (audio lives on its own origin)',
    when: 'desktop',
    fn: () => {
      const bad = [...document.querySelectorAll('audio,audio source')]
        .map((e) => e.getAttribute('src')).filter((s) => s && s.startsWith('/'));
      return bad.length ? `root-relative audio src: ${bad[0]}` : null;
    },
  }],

  '/portals': [{
    /* --tr starts at 0px and was only raised by :hover. A zero-radius
       radial-gradient mask is engine-dependent: Blink paints the last stop
       (day survives) and WebKit paints transparent (day masked away), which
       is why every piece read NIGHT ONLY on iPhone. On touch the mask must
       be off outright, not merely given a different radius. */
    name: 'torch mask off on touch (no degenerate zero-radius mask)',
    when: 'touch',
    fn: () => {
      const bad = [];
      for (const p of document.querySelectorAll('.pv-piece')) {
        for (const d of p.querySelectorAll('.day')) {
          const m = getComputedStyle(d).maskImage || getComputedStyle(d).webkitMaskImage;
          if (m && m !== 'none') bad.push(`${p.className.split(' ')[1] || 'piece'}: ${m.slice(0, 70)}`);
        }
      }
      return bad.length ? `${bad.length} .day still masked on touch — ${bad[0]}` : null;
    },
  }, {
    name: 'torch mask present on desktop (effect not lost)',
    when: 'desktop',
    fn: () => {
      const el = document.querySelector('.pv-piece.pv-torch .day');
      if (!el) return null;   // torch class is added by script; absent is not a fault
      const m = getComputedStyle(el).maskImage || getComputedStyle(el).webkitMaskImage;
      return m && m.includes('gradient') ? null : `desktop lost the torch mask (mask-image: ${m})`;
    },
  }],

  '/resin': [{
    name: 'gallery rendered (400+ pieces, styles applied)',
    when: 'all',
    fn: () => {
      const styled = getComputedStyle(document.body).backgroundColor;
      if (styled === 'rgba(0, 0, 0, 0)') return 'body has no background — stylesheet did not arrive';
      return null;
    },
  }],
};

/* ------------------------------------------------------- in-page probes */
/* Everything below runs inside the page. Pages here are up to 14MB of
   inlined HTML, so nothing serialises the document out to node. */

const PROBE = {
  links: () => {
    const out = [];
    for (const a of document.querySelectorAll('a[href]')) {
      const raw = a.getAttribute('href');
      if (!raw) continue;
      if (/^(mailto:|tel:|javascript:|data:|blob:|#)/i.test(raw.trim())) continue;
      try { out.push(new URL(raw, location.href).href); } catch { /* unparseable */ }
    }
    return [...new Set(out)];
  },

  overflow: () => ({
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth: window.innerWidth,
  }),

  nav: () => {
    const seal = !!document.querySelector('.nf-seal');
    const old = !!document.querySelector('.nh-word, #nh-drawer, .nh-tab');
    const hubLink = [...document.querySelectorAll('a[href]')].some((a) => {
      const h = a.getAttribute('href') || '';
      return /noblefathercreations\.com\/?($|[?#])/.test(h) || h === '/' || h === '/#' ;
    });
    return { seal, old, hubLink };
  },

  naming: () => {
    const html = document.documentElement.innerHTML;
    const hits = [];
    for (const bad of ['Fracture Everywhere', 'All Fracture']) {
      if (html.includes(bad)) hits.push(bad);
    }
    return hits;
  },

  /* Anything with a real box that is transparent or hidden and is NOT
     declared closed. Closed drawers/lightboxes announce themselves with
     [hidden] / aria-hidden / inert / pointer-events:none — an element that
     is invisible without any of those is a fade that never fired. */
  invisible: () => {
    const out = [];
    const closed = (el) => el.closest('[hidden],[aria-hidden="true"],[inert],dialog:not([open]),template');
    for (const el of document.querySelectorAll('body *')) {
      const tag = el.tagName;
      if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'LINK' || tag === 'TEMPLATE'
          || tag === 'DEFS' || tag === 'SVG' || tag === 'PATH') continue;
      const r = el.getBoundingClientRect();
      if (r.width * r.height < 900) continue;
      const cs = getComputedStyle(el);
      const invisible = cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0;
      if (!invisible) continue;
      if (cs.pointerEvents === 'none') continue;      // decorative / closed overlay
      if (closed(el)) continue;
      if (el.textContent.trim() === '' && tag !== 'IMG' && tag !== 'PICTURE') continue;
      let sel = tag.toLowerCase();
      if (el.id) sel += '#' + el.id;
      if (el.classList.length) sel += '.' + [...el.classList].slice(0, 3).join('.');
      out.push({ sel, w: Math.round(r.width), h: Math.round(r.height),
                 opacity: cs.opacity, visibility: cs.visibility,
                 delay: cs.animationDelay, anim: cs.animationName });
      if (out.length >= 12) break;
    }
    return out;
  },
};

/* Push the page through its IntersectionObserver fades before judging what
   is invisible, then come back to the top. */
async function settle(page) {
  await page.evaluate(async () => {
    const step = Math.max(320, window.innerHeight * 0.9);
    const end = document.documentElement.scrollHeight;
    for (let y = 0; y < end + step; y += step) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 60));
    }
    window.scrollTo(0, 0);
    await new Promise((r) => setTimeout(r, 500));
  }).catch(() => {});
}

/* --------------------------------------------------------------- runner */

const PASSES = [
  { id: 'desktop', label: '1440x900',
    ctx: { viewport: { width: 1440, height: 900 } } },
  { id: 'touch', label: '390x844 touch',
    ctx: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true,
           deviceScaleFactor: 2 } },
  { id: 'reduce', label: 'reduced-motion',
    ctx: { viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' } },
];
const RUN_PASSES = ONLY ? PASSES.filter((p) => ONLY.includes(p.id)) : PASSES;

const results = [];          // one row per (path, pass)
const linkStatus = new Map();  // url -> status, checked once globally
const discovered = new Map();  // url -> seed that found it
let subRendered = 0;

function fail(row, check, detail) {
  row.failures.push({ check, detail });
}

async function visit(browser, pass, url, label, { seed = true } = {}) {
  const row = { path: label, pass: pass.id, status: null, nav: '-', failures: [],
                links: 0, subresources: 0, ms: 0 };
  const t0 = Date.now();
  const ctx = await browser.newContext({
    ...pass.ctx,
    ignoreHTTPSErrors: true,
    userAgent: pass.ctx.isMobile
      ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 ' +
        '(KHTML, like Gecko) CriOS/126.0.0.0 Mobile/15E148 Safari/604.1'
      : UA,
  });

  if (VIA_CURL) {
    await ctx.route('**/*', async (route) => {
      const req = route.request();
      const u = req.url();
      if (!/^https?:/i.test(u)) return route.continue();
      const r = await curlBody(u);
      if (!r) return route.abort('failed');
      await route.fulfill({ status: r.status, headers: r.headers, body: r.body });
    });
  }
  if (IS_LOCAL) {
    /* Mirror mode: our own separately-deployed origins are served by the
       mirror. The music page's audio URLs are absolute by design. */
    await ctx.route('**/*', async (route) => {
      const u = route.request().url();
      const to = rewriteToBase(u);
      if (to && to !== u) return route.continue({ url: to });
      return route.fallback();
    });
  }

  const page = await ctx.newPage();
  const errors = [];
  const badRes = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + String(e.message || e).split('\n')[0]));
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push('console: ' + m.text().slice(0, 200));
  });
  page.on('requestfailed', (r) => {
    const f = r.failure();
    /* An aborted media/range request is normal; a failed script is not. */
    if (f && /ERR_ABORTED/.test(f.errorText) && r.resourceType() === 'media') return;
    badRes.push(`${r.resourceType()} FAILED ${f ? f.errorText : '?'} ${r.url().slice(0, 120)}`);
  });
  page.on('response', (r) => {
    row.subresources++;
    if (r.status() >= 400) badRes.push(`${r.request().resourceType()} ${r.status()} ${r.url().slice(0, 120)}`);
  });

  let resp = null;
  try {
    resp = await page.goto(url, { waitUntil: 'load', timeout: NAV_TIMEOUT });
  } catch (e) {
    try { resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: NAV_TIMEOUT }); }
    catch (e2) { fail(row, 'HTTP', `navigation failed: ${String(e2.message).split('\n')[0]}`); }
  }
  row.status = resp ? resp.status() : null;
  if (row.status !== 200) fail(row, 'HTTP', `status ${row.status}`);

  if (resp) {
    await page.waitForTimeout(900);
    await settle(page);

    /* 3 — links */
    const links = await page.evaluate(PROBE.links).catch(() => []);
    for (const raw of links) {
      const internal = rewriteToBase(raw);
      if (!internal) continue;
      row.links++;
      if (!discovered.has(internal)) discovered.set(internal, label);
    }

    /* 5 — a way out */
    const nav = await page.evaluate(PROBE.nav).catch(() => ({}));
    row.nav = nav.seal ? 'nf-seal' : nav.old ? 'nh-* (old)' : nav.hubLink ? 'hub link only' : 'NONE';
    if (!nav.seal && !nav.old && !nav.hubLink) fail(row, 'nav', 'no route back to the hub');

    /* 6 — overflow */
    const o = await page.evaluate(PROBE.overflow).catch(() => null);
    if (o && o.scrollWidth > o.innerWidth + 1) {
      fail(row, 'overflow', `scrollWidth ${o.scrollWidth} > innerWidth ${o.innerWidth}`);
    }

    /* 7 — stuck invisible */
    const inv = await page.evaluate(PROBE.invisible).catch(() => []);
    if (inv.length) {
      fail(row, 'invisible', inv.map((i) => `${i.sel} ${i.w}x${i.h} opacity:${i.opacity} vis:${i.visibility}` +
        (i.anim !== 'none' ? ` anim:${i.anim} delay:${i.delay}` : '')).join(' | '));
    }

    /* 8 — one canonical name */
    const names = await page.evaluate(PROBE.naming).catch(() => []);
    if (names.length) fail(row, 'naming', `stale project name on page: ${names.join(', ')}`);

    /* 9 — per-page structural asserts */
    for (const a of (PAGE_ASSERTS[label] || [])) {
      if (a.when !== 'all' && a.when !== pass.id) continue;
      const msg = await page.evaluate(a.fn).catch((e) => 'probe threw: ' + e.message);
      if (msg) fail(row, 'assert', `${a.name}: ${msg}`);
    }
  }

  /* 2 + 4 */
  if (errors.length) fail(row, 'js', [...new Set(errors)].slice(0, 6).join(' | '));
  if (badRes.length) fail(row, 'subresource', [...new Set(badRes)].slice(0, 6).join(' | '));

  row.ms = Date.now() - t0;
  results.push(row);

  /* Crawl one level: render a couple of newly-found same-origin HTML pages
     from this seed, with the same assertions applied. */
  if (seed && DEPTH > 0 && SUBPAGES > 0) {
    const kids = [];
    for (const [u, from] of discovered) {
      if (from !== label) continue;
      const p = new URL(u).pathname;
      if (/\.(css|js|json|png|jpe?g|webp|svg|mp3|m4a|ico|xml|txt|pdf|zip|woff2?)$/i.test(p)) continue;
      if (p === new URL(url).pathname) continue;
      if (results.some((r) => r.path === p && r.pass === pass.id)) continue;
      if (kids.every((k) => k !== u)) kids.push(u);
      if (kids.length >= SUBPAGES) break;
    }
    for (const k of kids) {
      subRendered++;
      await visit(browser, pass, k, new URL(k).pathname, { seed: false });
    }
  }

  await page.close();
  await ctx.close();
  return row;
}

/* ----------------------------------------------------------------- main */

TMP = await mkdtemp(path.join(tmpdir(), 'nfc-verify-'));
const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium',
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--autoplay-policy=no-user-gesture-required'],
});

/* Can the browser reach BASE at all? If not, fall back to curl transport
   rather than reporting 16 phantom failures. */
if (!VIA_CURL) {
  const probe = await browser.newContext({ ignoreHTTPSErrors: true });
  const pp = await probe.newPage();
  try {
    await pp.goto(BASE + '/', { waitUntil: 'commit', timeout: 25000 });
  } catch (e) {
    if (!IS_LOCAL) {
      VIA_CURL = true;
      console.log(`i browser cannot reach ${BASE} directly (${String(e.message).split('\n')[0].slice(0, 60)});`);
      console.log('i routing every request through curl + the agent proxy instead.\n');
    }
  }
  await probe.close();
}

console.log(`Noble Father Creations — verify\n  base:      ${BASE}`);
console.log(`  transport: ${VIA_CURL ? 'curl (browser has no direct network)' : 'direct'}`);
console.log(`  passes:    ${RUN_PASSES.map((p) => p.label).join(', ')}`);
console.log(`  pages:     ${TARGETS.length}\n`);

for (const pass of RUN_PASSES) {
  console.log(`── ${pass.label} ${'─'.repeat(Math.max(0, 46 - pass.label.length))}`);
  for (const t of TARGETS) {
    const row = await visit(browser, pass, BASE + (t === '/' ? '/' : t), t);
    const mark = row.failures.length ? 'FAIL' : 'PASS';
    console.log(`  ${mark}  ${row.path.padEnd(22)} ${String(row.status).padEnd(4)} ` +
                `${String(row.nav).padEnd(13)} ${String(row.links).padStart(3)} links  ` +
                `${(row.ms / 1000).toFixed(1)}s`);
    for (const f of row.failures) console.log(`        · ${f.check}: ${f.detail}`);
  }
  console.log('');
}

/* --- 3: every internal link discovered anywhere, checked once ---------- */

console.log(`── internal links (${discovered.size} unique) ${'─'.repeat(20)}`);
const linkFailures = [];
const urls = [...discovered.keys()];
const CONC = VIA_CURL ? 6 : 16;
let done = 0;
await Promise.all(Array.from({ length: CONC }, async () => {
  while (urls.length) {
    const u = urls.pop();
    const s = await statusOf(u);
    linkStatus.set(u, s);
    done++;
    if (s !== 200 && s !== 206) {
      linkFailures.push({ url: u, status: s, from: discovered.get(u) });
      console.log(`  FAIL ${String(s).padEnd(4)} ${u}   (linked from ${discovered.get(u)})`);
    } else if (VERBOSE) console.log(`  ok   ${s}  ${u}`);
  }
}));
if (!linkFailures.length) console.log(`  all ${done} internal links resolve 200.`);
console.log('');

/* ------------------------------------------------------------- summary */

const pageFails = results.filter((r) => r.failures.length);
console.log('── summary ' + '─'.repeat(46));
console.log(`  page renders : ${results.length} (${TARGETS.length} targets x ${RUN_PASSES.length} passes` +
            `${subRendered ? ` + ${subRendered} crawled sub-pages` : ''})`);
console.log(`  page failures: ${pageFails.length}`);
console.log(`  link failures: ${linkFailures.length} of ${done}`);

const navByPath = new Map();
for (const r of results) if (!navByPath.has(r.path)) navByPath.set(r.path, r.nav);
const gens = {};
for (const [p, n] of navByPath) (gens[n] ||= []).push(p);
console.log('  nav generation split:');
for (const [n, ps] of Object.entries(gens)) console.log(`    ${String(n).padEnd(14)} ${ps.join(' ')}`);

if (JSON_OUT) {
  await writeFile(JSON_OUT, JSON.stringify({ base: BASE, viaCurl: VIA_CURL, results,
    links: [...linkStatus].map(([url, status]) => ({ url, status, from: discovered.get(url) })) }, null, 1));
  console.log(`\n  wrote ${JSON_OUT}`);
}

await browser.close();
await rm(TMP, { recursive: true, force: true });

const bad = pageFails.length + linkFailures.length;
console.log(bad ? `\nFAILED — ${bad} problem(s). Do not deploy.` : '\nPASSED — clean.');
process.exit(bad ? 1 : 0);
