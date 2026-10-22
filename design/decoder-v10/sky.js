/* The sky: one persistent canvas behind the whole guide. Every tactic is a star,
   every group a constellation. The page you are on decides where the camera is,
   so moving through the guide is moving through the sky. Redraws only while
   something moves; nothing runs when the tab is hidden or when Calm is on. */
const Sky = (() => {
  const N = D.entries.length;
  const pickLayout = () => D.sky[innerWidth < innerHeight * .85 ? "port" : "land"];
  let S = pickLayout();
  const cv = document.getElementById("sky"), cx = cv.getContext("2d");
  const motionOK = () => !CALM && !matchMedia("(prefers-reduced-motion: reduce)").matches;
  let CALM = store.get("calm", false);
  let W = 0, H = 0, DPR = 1;
  const cam = { x: S.w / 2, y: S.h / 2, k: 1 };           // world centre + pixels per unit
  let tween = null, raf = 0, dirty = true, lastT = 0;
  const st = { dim: 1, focus: null, lit: new Set(), ring: -1, hover: -1, groupFocus: null, interactive: false, labels: false, offY: 0, offX: 0 };
  let appear = 0;                                         // 0..1 entrance
  const visited = new Set(), saved = new Set();
  const rankIn = {}; (() => { const by = {}; D.entries.forEach((e, i) => (by[e.g] = by[e.g] || []).push(i)); for (const g in by) by[g].sort((a, b) => (D.entries[b].pop || 0) - (D.entries[a].pop || 0) || a - b).forEach((i, n) => rankIn[i] = n); })();
  const stars = S.pos.map((p, i) => ({ x: p[0], y: p[1], r: 1.4 + Math.min(3.2, (D.entries[i].pop || 0) * .38), ph: (i * 2.399) % 6.283 }));
  function relayout() { const n = pickLayout(); if (n === S) return false; S = n; layers = null; S.pos.forEach((p, i) => { stars[i].x = p[0]; stars[i].y = p[1]; }); api.S = S; return true; }
  const sprite = {};
  /* Colours come from the page's colourway (CSS custom properties), so the sky and the
     page always agree. Each constellation also has its own light, from the data. */
  const hexRGB = h => [1, 3, 5].map(n => parseInt(h.slice(n, n + 2), 16));
  const ink = () => {
    const cs = getComputedStyle(document.documentElement), v = n => cs.getPropertyValue("--sky-" + n).trim();
    const light = document.documentElement.getAttribute("data-theme") === "light";
    const g = {}; D.groups.forEach(G => { const c = hexRGB(G.c || "#BED0FF"); g[G.k] = (light ? c.map(x => Math.round(x * .5)) : c).join(","); });
    return { star: v("star") || "236,232,220", glow: v("glow") || "190,208,255", brass: v("brass") || "230,198,124", line: v("line") || "190,208,255", dust: v("dust") || "190,208,255", text: v("text") || "236,232,220", plate: v("plate") || "10,14,30", g, light };
  };
  let C = ink();
  let gfT0 = 0, gfLast = null;                            // when the focused constellation last changed: its lines draw themselves in
  let meteor = null, nextMeteor = performance.now() + 5000;
  function makeSprite(rgb) {
    const key = rgb, c = document.createElement("canvas"); c.width = c.height = 64; const g = c.getContext("2d");
    const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, "rgba(" + rgb + ",1)"); gr.addColorStop(.12, "rgba(" + rgb + ",.9)"); gr.addColorStop(.3, "rgba(" + rgb + ",.28)"); gr.addColorStop(1, "rgba(" + rgb + ",0)");
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); sprite[key] = c; return c;
  }
  const spr = rgb => sprite[rgb] || makeSprite(rgb);
  /* Each constellation's faint lines are baked once into a small image (at three scales)
     and blitted, so panning never re-strokes 600 lines. Focused or lit lines are still vector. */
  const LODS = [.3, .55, .9]; let layers = null, layerSig = "";
  function buildLayers() {
    layers = []; layerSig = C.line + "|" + (S === D.sky.port ? "p" : "l");
    const by = {}; S.edges.forEach(([i, j]) => (by[D.entries[i].g] = by[D.entries[i].g] || []).push([i, j]));
    for (const g in by) {
      let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
      by[g].forEach(([i, j]) => [stars[i], stars[j]].forEach(p => { x0 = Math.min(x0, p.x); x1 = Math.max(x1, p.x); y0 = Math.min(y0, p.y); y1 = Math.max(y1, p.y); }));
      x0 -= 6; y0 -= 6; x1 += 6; y1 += 6;
      const per = LODS.map(ls => {
        const c = document.createElement("canvas"); c.width = Math.ceil((x1 - x0) * ls); c.height = Math.ceil((y1 - y0) * ls);
        const k = c.getContext("2d"); k.strokeStyle = "rgb(" + C.line + ")"; k.lineWidth = 1; k.beginPath();
        by[g].forEach(([i, j]) => { k.moveTo((stars[i].x - x0) * ls, (stars[i].y - y0) * ls); k.lineTo((stars[j].x - x0) * ls, (stars[j].y - y0) * ls); });
        k.stroke(); return { ls, c };
      });
      layers.push({ g, x0, y0, per });
    }
  }
  const nebSprite = {};
  function neb(rgb) {
    if (nebSprite[rgb]) return nebSprite[rgb];
    const c = document.createElement("canvas"); c.width = c.height = 128; const g = c.getContext("2d");
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    gr.addColorStop(0, "rgba(" + rgb + ",1)"); gr.addColorStop(1, "rgba(" + rgb + ",0)");
    g.fillStyle = gr; g.fillRect(0, 0, 128, 128); return (nebSprite[rgb] = c);
  }
  /* background dust: fixed points in screen space with tiny parallax */
  let dust = [];
  function seedDust() {
    dust = []; let s = 7;
    const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
    const n = Math.round(W * H / (W < 700 ? 9000 : 5200));
    for (let i = 0; i < n; i++) dust.push({ x: rnd(), y: rnd(), r: .35 + rnd() * .9, a: .18 + rnd() * .5, z: .05 + rnd() * .2 });
  }
  function resize() {
    DPR = Math.min(window.devicePixelRatio || 1, innerWidth < 700 ? 1.5 : 2);
    W = innerWidth; H = innerHeight;
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR); cv.style.width = W + "px"; cv.style.height = H + "px";
    cx.setTransform(DPR, 0, 0, DPR, 0, 0); seedDust(); invalidate();
  }
  const fitK = () => Math.min(W / S.w, H / S.h) * (W < 700 ? 1.18 : 1.02);
  const sx = x => W / 2 + (x - cam.x) * cam.k + st.offX, sy = y => H / 2 + (y - cam.y) * cam.k + st.offY;
  const wx = px => (px - W / 2 - st.offX) / cam.k + cam.x, wy = py => (py - H / 2 - st.offY) / cam.k + cam.y;

  function invalidate() { dirty = true; if (!raf) raf = requestAnimationFrame(frame); }
  const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  function flyTo(x, y, k, ms, offX, offY) {
    st.offX = offX == null ? st.offX : offX; st.offY = offY == null ? st.offY : offY;
    if (!ms || !motionOK()) { cam.x = x; cam.y = y; cam.k = k; tween = null; invalidate(); return; }
    /* arc: pull back a little in the middle of a long flight so it reads as travel */
    const d = Math.hypot((x - cam.x) * cam.k, (y - cam.y) * cam.k);
    tween = { t0: performance.now(), ms, x0: cam.x, y0: cam.y, k0: cam.k, x1: x, y1: y, k1: k, dip: Math.min(.35, d / 4000) };
    invalidate();
  }
  function frame(t) {
    raf = 0;
    if (document.hidden) { return; }
    const dt = Math.min(48, t - (lastT || t)); lastT = t;
    let animating = false;
    if (tween) {
      const p = Math.min(1, (performance.now() - tween.t0) / tween.ms), e = ease(p);
      cam.x = tween.x0 + (tween.x1 - tween.x0) * e; cam.y = tween.y0 + (tween.y1 - tween.y0) * e;
      cam.k = (tween.k0 + (tween.k1 - tween.k0) * e) * (1 - Math.sin(p * Math.PI) * tween.dip);
      if (p >= 1) { cam.k = tween.k1; tween = null; } else animating = true;
    }
    if (vel.x || vel.y) { cam.x += vel.x * dt / cam.k; cam.y += vel.y * dt / cam.k; vel.x *= .93; vel.y *= .93; if (Math.abs(vel.x) < .005 && Math.abs(vel.y) < .005) vel.x = vel.y = 0; else animating = true; clampCam(); }
    if (appear < 1) { appear = Math.min(1, appear + dt / 1500); animating = true; }
    if (st.groupFocus !== gfLast) { gfLast = st.groupFocus; gfT0 = performance.now(); }
    if (st.groupFocus && motionOK() && performance.now() - gfT0 < 1800) animating = true;
    if (!meteor && !lite && alive() && performance.now() > nextMeteor && !tween) {
      const fromL = Math.random() < .5, x = W * (.15 + Math.random() * .7), y = H * (.06 + Math.random() * .3), sp = 380 + Math.random() * 260;
      meteor = { t0: performance.now(), ms: 950, x, y, vx: (fromL ? 1 : -1) * sp, vy: sp * (.35 + Math.random() * .3) };
      nextMeteor = performance.now() + 9000 + Math.random() * 14000;
    }
    if (meteor) animating = true;
    if (animating || dirty || alive()) {
      draw(t);
      /* adapt: if frames keep arriving slower than ~30fps while the camera moves, drop the decorative layers */
      if (!lite && animating && dt > 0) { slow = dt > 30 ? slow + 1 : Math.max(0, slow - 1); if (slow > 14) { lite = true; invalidate(); } }
    }
    dirty = false;
    if (animating) raf = requestAnimationFrame(frame);
    else if (alive()) setTimeout(() => { if (!raf) raf = requestAnimationFrame(frame); }, 90);
  }
  let twinkle = true, lite = false, slow = 0;
  let aliveNow = false;
  const alive = () => twinkle && motionOK() && st.dim > .6 && (document.body.dataset.sky === "" || document.body.dataset.sky === "sky");
  const vel = { x: 0, y: 0 };
  function clampCam() { cam.x = Math.max(0, Math.min(S.w, cam.x)); cam.y = Math.max(0, Math.min(S.h, cam.y)); }

  function draw(t) {
    cx.clearRect(0, 0, W, H);
    const dim = st.dim, ap = appear, time = (t || 0) / 1000; aliveNow = alive();
    /* dust */
    cx.fillStyle = "rgb(" + C.dust + ")";
    if (!lite) for (const d of dust) {
      const x = ((d.x * W - (cam.x - S.w / 2) * cam.k * d.z) % W + W) % W, y = ((d.y * H - (cam.y - S.h / 2) * cam.k * d.z) % H + H) % H;
      cx.globalAlpha = Math.round(d.a * (0.35 + .65 * dim) * ap * (aliveNow ? .78 + .22 * Math.sin(time * .7 + d.x * 40) : 1) * 6) / 6;
      cx.fillRect(x, y, d.r, d.r);
    }
    cx.globalAlpha = 1;
    /* soft nebula at each constellation: one cached glow, scaled */
    if (!lite) for (const g in S.groups) {
      const G = S.groups[g], x = sx(G.x), y = sy(G.y), r = G.r * cam.k * 1.6;
      if (x < -r || x > W + r || y < -r || y > H + r) continue;
      cx.globalAlpha = Math.min(1, (st.groupFocus === g ? .3 : st.groupFocus ? .06 : .15) * (C.light ? .6 : 1) * dim * ap);
      cx.drawImage(neb(C.g[g] || C.glow), x - r, y - r, r * 2, r * 2);
    }
    cx.globalAlpha = 1;
    /* a shooting star, now and then, on the open sky only */
    if (meteor) {
      const p = (performance.now() - meteor.t0) / meteor.ms;
      if (p >= 1) meteor = null; else {
        const hx = meteor.x + meteor.vx * p, hy = meteor.y + meteor.vy * p, len = 160 * Math.sin(p * Math.PI) + 10;
        const n = Math.hypot(meteor.vx, meteor.vy), tx = hx - meteor.vx / n * len, ty = hy - meteor.vy / n * len;
        const gr = cx.createLinearGradient(hx, hy, tx, ty);
        gr.addColorStop(0, "rgba(" + C.star + "," + (.9 * Math.sin(p * Math.PI) * dim) + ")"); gr.addColorStop(1, "rgba(" + C.star + ",0)");
        cx.strokeStyle = gr; cx.lineWidth = 1.4; cx.lineCap = "round"; cx.beginPath(); cx.moveTo(hx, hy); cx.lineTo(tx, ty); cx.stroke(); cx.lineWidth = 1; cx.lineCap = "butt";
      }
    }
    const focusSet = st.focus, fSet = focusSet ? new Set(focusSet) : null;
    const gDim = i => st.groupFocus ? (D.entries[i].g === st.groupFocus ? 1 : .22) : 1;
    /* lines: related links inside a constellation, faint; focused links stronger.
       Batched into a few paths by strength so the canvas strokes four times, not 600. */
    cx.lineWidth = 1;
    const sig = C.line + "|" + (S === D.sky.port ? "p" : "l");
    const useCache = st.clipY == null && cam.k <= LODS[LODS.length - 1] * 1.05;
    if (useCache) {
      if (!layers || layerSig !== sig) buildLayers();
      const lod = LODS.findIndex(ls => ls >= cam.k * .92), intro = Math.max(0, Math.min(1, ap * 1.6 - .5));
      for (const L of layers) {
        const pr = L.per[lod < 0 ? LODS.length - 1 : lod];
        if (st.groupFocus === L.g) continue;
        const a = .2 * dim * intro * (st.groupFocus ? .05 : 1);
        if (a < .01) continue;
        const x = sx(L.x0), y = sy(L.y0), w = pr.c.width / pr.ls * cam.k, h = pr.c.height / pr.ls * cam.k;
        if (x > W || y > H || x + w < 0 || y + h < 0) continue;
        cx.globalAlpha = a; cx.drawImage(pr.c, x, y, w, h);
      }
      cx.globalAlpha = 1;
    }
    const buckets = [[], [], [], []], mine = [];
    const gf = st.groupFocus;
    for (const [i, j] of S.edges) {
      if (gf && D.entries[i].g === gf && D.entries[j].g === gf && !(fSet && fSet.has(i) && fSet.has(j))) { mine.push(i, j); continue; }
      const a = stars[i], b = stars[j];
      const x1 = sx(a.x), y1 = sy(a.y), x2 = sx(b.x), y2 = sy(b.y);
      if ((x1 < -50 && x2 < -50) || (x1 > W + 50 && x2 > W + 50) || (y1 < -50 && y2 < -50) || (y1 > H + 50 && y2 > H + 50)) continue;
      const lit2 = st.lit.has(i) && st.lit.has(j), strong = fSet && fSet.has(i) && fSet.has(j);
      if (useCache && !lit2 && !strong) continue;
      let al = (strong ? .6 : .2) * dim * Math.min(gDim(i), gDim(j)) * Math.max(0, Math.min(1, ap * 1.6 - .5 - (i % 17) / 40));
      if (st.clipY != null) al *= Math.max(0, Math.min(1, (st.clipY - Math.min(y1, y2)) / 70 + 1));
      if (lit2) al = Math.max(al, .5);
      if (al < .02) continue;
      const bk = (strong || lit2) ? 3 : al > .15 ? 2 : al > .08 ? 1 : 0;
      buckets[bk].push(x1, y1, x2, y2, al);
    }
    for (let bk = 0; bk < 4; bk++) {
      const L = buckets[bk]; if (!L.length) continue;
      let sum = 0; for (let q = 4; q < L.length; q += 5) sum += L[q];
      cx.strokeStyle = "rgba(" + (bk === 3 ? C.brass : C.line) + "," + (sum / (L.length / 5)).toFixed(3) + ")";
      cx.beginPath();
      for (let q = 0; q < L.length; q += 5) { cx.moveTo(L[q], L[q + 1]); cx.lineTo(L[q + 2], L[q + 3]); }
      cx.stroke();
    }
    /* the focused constellation, in its own colour, drawing itself edge by edge */
    if (mine.length) {
      const prog = motionOK() ? (performance.now() - gfT0) / 1700 : 9, m = mine.length / 2;
      cx.strokeStyle = "rgba(" + (C.g[gf] || C.line) + "," + (.62 * dim) + ")"; cx.lineWidth = 1.15; cx.beginPath();
      for (let q = 0; q < mine.length; q += 2) {
        const a = stars[mine[q]], b = stars[mine[q + 1]];
        const e = Math.max(0, Math.min(1, (prog - (q / 2) / m * .55) / .45)); if (!e) continue;
        const x1 = sx(a.x), y1 = sy(a.y), x2 = x1 + (sx(b.x) - x1) * e, y2 = y1 + (sy(b.y) - y1) * e;
        if (st.clipY != null && Math.min(y1, y2) > st.clipY) continue;
        cx.moveTo(x1, y1); cx.lineTo(x2, y2);
      }
      cx.stroke(); cx.lineWidth = 1;
    }
    /* cross-constellation links of the focused star */
    if (st.ring >= 0 && st.link) {
      cx.setLineDash([3, 5]);
      for (const j of S.near[st.ring]) {
        const a = stars[st.ring], b = stars[j]; if (Math.hypot(a.x - b.x, a.y - b.y) > 900) continue;
        cx.strokeStyle = "rgba(" + C.brass + "," + (.55 * ap) + ")";
        cx.beginPath(); cx.moveTo(sx(a.x), sy(a.y)); cx.lineTo(sx(b.x), sy(b.y)); cx.stroke();
      }
      cx.setLineDash([]);
    }
    /* sequence being read: brass chain */
    if (st.chain) {
      cx.strokeStyle = "rgba(" + C.brass + ",.8)"; cx.lineWidth = 1.5; cx.beginPath();
      st.chain.forEach((i, n) => { const p = stars[i]; n ? cx.lineTo(sx(p.x), sy(p.y)) : cx.moveTo(sx(p.x), sy(p.y)); }); cx.stroke(); cx.lineWidth = 1;
    }
    /* stars */
    const star = spr(C.star), brass = spr(C.brass);
    const labelQ = [];
    for (let i = 0; i < N; i++) {
      const s = stars[i], x = sx(s.x), y = sy(s.y);
      if (x < -30 || x > W + 30 || y < -30 || y > H + 30) continue;
      const infocus = fSet ? fSet.has(i) : true, lit = st.lit.has(i), vis = visited.has(i), sv = saved.has(i);
      let a = (infocus ? 1 : .35) * gDim(i) * dim;
      if (lit) a = 1;
      const delay = Math.min(1, Math.max(0, ap * 1.8 - (Math.hypot(s.x - S.w / 2, s.y - S.h / 2) / 1800)));
      a *= delay;
      if (st.clipY != null) a *= Math.max(0, Math.min(1, (st.clipY - y) / 70 + 1));
      const tw = aliveNow ? .82 + .18 * Math.sin(time * (.8 + (i % 7) * .13) + s.ph) : 1;
      let near = 0; if (st.px != null) { const dd = Math.hypot(x - st.px, y - st.py); near = dd < 170 ? 1 - dd / 170 : 0; near *= near; a = Math.min(1, a * (1 + near * 1.6)); }
      const mineG = st.groupFocus && D.entries[i].g === st.groupFocus;
      const size = Math.max(6, s.r * cam.k * 8.5) * (lit ? 1.5 : 1) * (i === st.ring ? 1.6 : 1) * (mineG ? 1.35 : 1) * (1 + near * .6) * (i === st.hover ? 1.5 : 1);
      const img = (lit || vis || sv || i === st.ring || i === st.hover) ? brass : mineG ? spr(C.g[st.groupFocus]) : star;
      cx.globalAlpha = Math.min(1, a * tw);
      cx.drawImage(img, x - size, y - size, size * 2, size * 2);
      /* core point */
      cx.globalAlpha = Math.min(1, a * tw * 1.1);
      cx.fillStyle = "rgb(" + ((lit || vis || sv || i === st.ring) ? C.brass : C.star) + ")";
      const cr = Math.max(1.35, s.r * cam.k * (sv ? 1.4 : .95));
      if (cr < 2.2) cx.fillRect(x - cr, y - cr, cr * 2, cr * 2); else { cx.beginPath(); cx.arc(x, y, cr, 0, 6.283); cx.fill(); }
      if (sv) { cx.globalAlpha = a * .7; cx.strokeStyle = "rgb(" + C.brass + ")"; cx.lineWidth = 1; cx.beginPath(); cx.arc(x, y, Math.max(5, s.r * cam.k * 2.2), 0, 6.283); cx.stroke(); }
      if (i === st.ring) {
        const pr = (motionOK() ? (time * .6) % 1 : .5);
        cx.globalAlpha = (1 - pr) * .8; cx.strokeStyle = "rgb(" + C.brass + ")"; cx.beginPath(); cx.arc(x, y, 8 + pr * 26, 0, 6.283); cx.stroke();
      }
      if ((st.clipY == null || y < st.clipY - 10) && (i === st.hover || lit && labelsOn() || i === st.ring || (fSet && fSet.has(i) && st.labels) || (st.labels && cam.k > fitK() * 2.4 && (!st.groupFocus || D.entries[i].g === st.groupFocus)) || (st.groupFocus && st.labels && D.entries[i].g === st.groupFocus && rankIn[i] < (W < 700 ? 7 : 12)))) labelQ.push([i, x, y, a]);
    }
    cx.globalAlpha = 1;
    /* constellation names */
    if (st.names) {
      const fs = W < 700 ? 12 : Math.max(12, Math.min(17, cam.k * 15 + 8)); const nameBoxes = [];
      cx.font = "500 " + fs + "px Astra,system-ui,sans-serif"; cx.textAlign = "center"; cx.textBaseline = "middle";
      for (const g of D.groups) {
        if (st.groupFocus && g.k !== st.groupFocus) continue;
        const G = S.groups[g.k]; const x = sx(G.x), y = sy(G.y - G.r - 40);
        if (x < -80 || x > W + 80 || y < 74 || y > H - 20) continue;
        const on = st.groupFocus === g.k, a = (on ? 1 : .62) * ap * Math.max(.4, dim);
        cx.fillStyle = "rgba(" + (C.g[g.k] || C.brass) + "," + a + ")";
        const label = (W < 700 ? g.short : g.label).toUpperCase(); cx.letterSpacing = W < 700 ? "0.1em" : "0.16em";
        const tw = cx.measureText(label).width; let lx = x;
        if (lx - tw / 2 < 12) lx = 12 + tw / 2; if (lx + tw / 2 > W - 12) lx = W - 12 - tw / 2;
        const av = st.avoid, hit = av && lx + tw / 2 > av.x0 && lx - tw / 2 < av.x1 && y > av.y0 && y < av.y1;
        const clash = nameBoxes.some(b => Math.abs(b[0] - lx) < (b[1] + tw) / 2 + 8 && Math.abs(b[2] - y) < fs + 6);
        if (!hit && !clash && tw < W - 24) { cx.fillText(label, lx, y); nameBoxes.push([lx, tw, y]); }
        cx.letterSpacing = "0px";
      }
    }
    /* star labels */
    if (labelQ.length) {
      cx.font = "500 13px 'Public Sans',system-ui,sans-serif"; cx.textAlign = "left"; cx.textBaseline = "middle";
      const placed = [];
      labelQ.sort((a, b) => (b[0] === st.hover) - (a[0] === st.hover));
      for (const [i, x, y, a] of labelQ) {
        const txt = curly(D.entries[i].n), w = cx.measureText(txt).width + 14;
        let lx = x + 12, ly = y; if (lx + w > W - 8) lx = x - 12 - w;
        if (i !== st.hover && placed.some(p => Math.abs(p[0] - lx) < Math.max(w, p[2]) && Math.abs(p[1] - ly) < 17)) continue;
        placed.push([lx, ly, w]);
        cx.fillStyle = "rgba(" + C.plate + ",.78)";
        const rx = lx - 6, ry = ly - 11; cx.beginPath(); cx.roundRect ? cx.roundRect(rx, ry, w, 22, 11) : cx.rect(rx, ry, w, 22); cx.fill();
        cx.fillStyle = "rgba(" + C.text + ",.95)"; cx.fillText(txt, lx + 1, ly + .5);
      }
    }
  }
  const labelsOn = () => st.labelLit;

  /* ----- interaction (only on the Sky page) ----- */
  let ptrs = new Map(), moved = 0, pinch0 = null, downT = 0, lastMove = null;
  function nearest(px, py, rad) {
    let best = -1, bd = rad * rad;
    for (let i = 0; i < N; i++) { const dx = sx(stars[i].x) - px, dy = sy(stars[i].y) - py, d = dx * dx + dy * dy; if (d < bd) { bd = d; best = i; } }
    return best;
  }
  function down(e) {
    if (!st.interactive) return; cv.setPointerCapture && cv.setPointerCapture(e.pointerId);
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY }); moved = 0; downT = performance.now(); vel.x = vel.y = 0; tween = null;
    if (ptrs.size === 2) { const [a, b] = [...ptrs.values()]; pinch0 = { d: Math.hypot(a.x - b.x, a.y - b.y), k: cam.k }; }
    lastMove = { x: e.clientX, y: e.clientY, t: performance.now() };
  }
  function move(e) {
    if (!st.interactive) return;
    if (!ptrs.has(e.pointerId)) { const i = nearest(e.clientX, e.clientY, 22); if (i !== st.hover) { st.hover = i; cv.style.cursor = i >= 0 ? "pointer" : "grab"; invalidate(); if (api.onHover) api.onHover(i); } return; }
    const p = ptrs.get(e.pointerId), dx = e.clientX - p.x, dy = e.clientY - p.y; p.x = e.clientX; p.y = e.clientY; moved += Math.abs(dx) + Math.abs(dy);
    if (ptrs.size === 2 && pinch0) { const [a, b] = [...ptrs.values()]; const d = Math.hypot(a.x - b.x, a.y - b.y); setK(pinch0.k * d / pinch0.d); }
    else { cam.x -= dx / cam.k; cam.y -= dy / cam.k; clampCam(); const now = performance.now(), dt = Math.max(1, now - lastMove.t); vel.x = -(e.clientX - lastMove.x) / dt * .9; vel.y = -(e.clientY - lastMove.y) / dt * .9; lastMove = { x: e.clientX, y: e.clientY, t: now }; }
    invalidate();
  }
  function up(e) {
    if (!st.interactive) return; const was = ptrs.has(e.pointerId); ptrs.delete(e.pointerId); if (ptrs.size < 2) pinch0 = null;
    if (was && moved < 8 && performance.now() - downT < 500) { const i = nearest(e.clientX, e.clientY, 26); vel.x = vel.y = 0; if (api.onPick) api.onPick(i); }
    else if (performance.now() - lastMove.t > 80) vel.x = vel.y = 0;
    if (!motionOK()) vel.x = vel.y = 0; invalidate();
  }
  function setK(k, ax, ay) {
    const lo = fitK() * .75, hi = fitK() * 7; k = Math.max(lo, Math.min(hi, k));
    if (ax != null) { const wx0 = wx(ax), wy0 = wy(ay); cam.k = k; cam.x += wx0 - wx(ax); cam.y += wy0 - wy(ay); } else cam.k = k;
    clampCam(); st.labels = cam.k > fitK() * 2.4;
  }
  cv.addEventListener("pointerdown", down); cv.addEventListener("pointermove", move); cv.addEventListener("pointerup", up); cv.addEventListener("pointercancel", up);
  cv.addEventListener("pointerleave", () => { if (st.hover >= 0 && !ptrs.size) { st.hover = -1; invalidate(); } });
  cv.addEventListener("wheel", e => { if (!st.interactive) return; e.preventDefault(); setK(cam.k * Math.exp(-e.deltaY * .0016), e.clientX, e.clientY); tween = null; invalidate(); }, { passive: false });
  addEventListener("resize", () => { relayout(); resize(); if (api.onResize) api.onResize(); });
  document.addEventListener("visibilitychange", () => { if (!document.hidden) invalidate(); });
  new MutationObserver(() => { C = ink(); layers = null; invalidate(); if (motionOK() && cv.animate) cv.animate([{ opacity: .2 }, { opacity: 1 }], { duration: 700, easing: "cubic-bezier(.16,1,.3,1)" }); }).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme", "data-skin"] });
  /* the stars nearest the pointer brighten a little, wherever the sky is showing */
  if (matchMedia("(pointer: fine)").matches) {
    addEventListener("pointermove", e => { if (!motionOK() || st.dim < .6) { if (st.px != null) { st.px = null; invalidate(); } return; } st.px = e.clientX; st.py = e.clientY; invalidate(); }, { passive: true });
    document.addEventListener("pointerleave", () => { st.px = null; invalidate(); });
  }

  const api = {
    cam, st, stars, fitK, S, resize, invalidate, flyTo, setK,
    get calm() { return CALM; },
    setCalm(v) { CALM = v; store.set("calm", v); if (v) { tween = null; vel.x = vel.y = 0; } invalidate(); },
    setMarks(v, s) { visited.clear(); saved.clear(); v.forEach(i => visited.add(i)); s.forEach(i => saved.add(i)); invalidate(); },
    set(opts) { Object.assign(st, opts); invalidate(); },
    colorOf: g => C.g[g],
    lit(list, labels) { st.lit = new Set(list || []); st.labelLit = !!labels; invalidate(); },
    skipIntro() { appear = 1; },
    toWorld: (px, py) => [wx(px), wy(py)],
    toScreen: i => [sx(stars[i].x), sy(stars[i].y)],
    nearest, onPick: null, onHover: null, onResize: null,
  };
  twinkle = !(navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 2);
  resize(); cam.k = fitK();
  if (document.fonts) { document.fonts.load('500 14px Astra').then(() => api.invalidate()); document.fonts.ready.then(() => api.invalidate()); }
  return api;
})();
