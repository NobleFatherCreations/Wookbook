/* ==========================================================================
   The Listening Room — player + catalogue
   No dependencies, no storage, no external requests beyond the audio files
   themselves (which are ABSOLUTE urls: this page is served both at
   noblemusic.netlify.app and, proxied, at noblefathercreations.com/music, and a
   root-relative path resolves against whichever host is in the address bar).
   ========================================================================== */
(function () {
  'use strict';

  /* ---- data ------------------------------------------------------------- */
  /* CATALOGUE is emitted as a JSON island by scripts/build-music.py. Reading it
     through a guard means a missing or malformed block shows a readable message
     instead of throwing a pageerror and leaving an empty shell -- which is the
     exact failure that took this page down (TRACKS used 8x, declared 0x). */
  var TRACKS = [];
  var SHELVES = [];
  var dataOK = false;
  try {
    var island = document.getElementById('catalogue-data');
    var parsed = island ? JSON.parse(island.textContent) : null;
    if (parsed && Array.isArray(parsed.tracks) && parsed.tracks.length &&
        Array.isArray(parsed.shelves) && parsed.shelves.length) {
      TRACKS = parsed.tracks;
      SHELVES = parsed.shelves;
      dataOK = true;
    }
  } catch (err) {
    dataOK = false;
  }

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) {
    return Array.prototype.slice.call((r || document).querySelectorAll(s));
  };

  var listEl = $('#list');
  var emptyEl = $('#empty');

  if (!dataOK) {
    if (emptyEl) {
      emptyEl.hidden = false;
      emptyEl.textContent = 'The catalogue could not be read. Nothing is lost — reload the page.';
    }
    return;
  }

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ---- helpers ---------------------------------------------------------- */
  function mmss(sec) {
    if (!isFinite(sec) || sec < 0) sec = 0;
    var m = Math.floor(sec / 60);
    var s = Math.floor(sec % 60);
    return m + ':' + (s < 10 ? '0' : '') + s;
  }
  function setAll(key, value) {
    $$('[data-np="' + key + '"]').forEach(function (el) { el.textContent = value; });
  }
  function norm(s) {
    return String(s).toLowerCase().normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  /* ---- state ----------------------------------------------------------- */
  var shelf = 'all';
  var query = '';
  var view = TRACKS.slice();       // the current filtered+ordered view
  var currentId = null;            // slug of the loaded track
  var shuffle = false;
  var scrubbing = false;

  var audio = $('#audio');
  var deck = $('#deck');
  var sheet = $('#sheet');

  /* ==========================================================================
     Rendering the list
     ========================================================================== */
  function matches(t) {
    if (shelf !== 'all' && t.shelf !== shelf) return false;
    if (!query) return true;
    return norm(t.title).indexOf(query) > -1 || norm(t.shelfName).indexOf(query) > -1;
  }

  function render() {
    view = TRACKS.filter(matches);

    var shelfMeta = shelf === 'all'
      ? { name: 'The Whole Room',
          blurb: 'Every track in the room, shelf by shelf, in the order they sit on the rail.' }
      : SHELVES.filter(function (s) { return s.id === shelf; })[0];

    /* NB: only the stacks heading changes here. The deck's eyebrow shows the
       CURRENT TRACK's shelf, which has nothing to do with what is filtered. */
    $('#shelfName').textContent = shelfMeta.name;
    $('#shelfBlurb').textContent = shelfMeta.blurb;

    var total = view.reduce(function (a, t) { return a + t.dur; }, 0);
    var h = Math.floor(total / 3600);
    var m = Math.round((total % 3600) / 60);
    $('#viewCount').textContent = view.length + (view.length === 1 ? ' track' : ' tracks') +
      (total ? ' · ' + (h ? h + 'h ' : '') + m + 'm' : '');

    var frag = document.createDocumentFragment();
    view.forEach(function (t, i) {
      var li = document.createElement('li');
      li.className = 'row';
      li.dataset.id = t.slug;
      /* cap the stagger: item 200 must not wait seven seconds to appear */
      li.style.setProperty('--i', Math.min(i, 14));

      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'row-btn';
      btn.setAttribute('aria-label', 'Play ' + t.title + ', ' + mmss(t.dur));

      var n = document.createElement('span');
      n.className = 'row-n num';
      n.textContent = i + 1;

      var eq = document.createElement('span');
      eq.className = 'eq';
      eq.setAttribute('aria-hidden', 'true');
      eq.innerHTML = '<i></i><i></i><i></i>';

      var main = document.createElement('span');
      main.className = 'row-main';
      var title = document.createElement('span');
      title.className = 'row-title';
      title.textContent = t.main;
      main.appendChild(title);
      var subText = [t.sub, t.shelfName].filter(Boolean).join(' · ');
      if (subText) {
        var sub = document.createElement('span');
        sub.className = 'row-sub';
        sub.textContent = subText;
        main.appendChild(sub);
      }

      var time = document.createElement('span');
      time.className = 'row-time num';
      time.textContent = mmss(t.dur);

      btn.appendChild(n);
      btn.appendChild(eq);
      btn.appendChild(main);
      btn.appendChild(time);
      li.appendChild(btn);
      frag.appendChild(li);
    });

    listEl.textContent = '';
    listEl.appendChild(frag);
    emptyEl.hidden = view.length > 0;
    markCurrent();
  }

  function markCurrent() {
    $$('.row', listEl).forEach(function (li) {
      if (li.dataset.id === currentId) {
        li.setAttribute('data-current', '');
        if (audio && !audio.paused) li.setAttribute('data-playing', '');
        else li.removeAttribute('data-playing');
      } else {
        li.removeAttribute('data-current');
        li.removeAttribute('data-playing');
      }
    });
  }

  /* clicking anywhere on a row plays it */
  listEl.addEventListener('click', function (e) {
    var li = e.target.closest ? e.target.closest('.row') : null;
    if (!li) return;
    var t = byId(li.dataset.id);
    if (!t) return;
    if (t.slug === currentId) { toggle(); return; }
    load(t, true);
  });

  function byId(id) {
    for (var i = 0; i < TRACKS.length; i++) if (TRACKS[i].slug === id) return TRACKS[i];
    return null;
  }

  /* ==========================================================================
     Shelf rail + search
     ========================================================================== */
  $$('.shelf-btn').forEach(function (b) {
    b.addEventListener('click', function () {
      shelf = b.dataset.shelf;
      $$('.shelf-btn').forEach(function (o) {
        o.setAttribute('aria-pressed', String(o === b));
      });
      render();
    });
  });

  var searchInput = $('#search');
  var searchClear = $('#searchClear');
  var searchTimer = null;
  searchInput.addEventListener('input', function () {
    if (searchTimer) clearTimeout(searchTimer);
    /* short debounce only: typing must never feel like it is waiting on us */
    searchTimer = setTimeout(function () {
      query = norm(searchInput.value.trim());
      if (query) searchClear.setAttribute('data-on', '');
      else searchClear.removeAttribute('data-on');
      render();
    }, 90);
  });
  searchClear.addEventListener('click', function () {
    searchInput.value = '';
    query = '';
    searchClear.removeAttribute('data-on');
    render();
    searchInput.focus();
  });

  /* ==========================================================================
     Loading and playing
     ========================================================================== */
  function load(t, play) {
    currentId = t.slug;
    audio.src = t.url;
    setAll('title', t.main);
    /* the eyebrow already shows the shelf, so falling back to it here just
       printed the same words twice; the artist is the record-sleeve convention */
    setAll('sub', t.sub || 'Shae Stovell');
    setAll('shelfName', t.shelfName);
    setAll('end', mmss(t.dur));
    setAll('now', '0:00');
    setProgress(0, 0);
    $$('.sleeve').forEach(function (s) { s.style.setProperty('--h', t.hue); });
    if (sheet) sheet.style.setProperty('--h', t.hue);
    markCurrent();
    if (play) start();
  }

  /* Autoplay never fires on load. start() is only ever reached from a real
     user gesture (click, key, or the ended handler continuing a queue the user
     already started). */
  function start() {
    ensureSpectrum();
    var p = audio.play();
    if (p && p.catch) p.catch(function () { paint(); });
  }

  function toggle() {
    if (!currentId) { if (view.length) load(view[0], true); return; }
    if (audio.paused) start(); else audio.pause();
  }

  function step(delta) {
    if (!view.length) return;
    var i = -1;
    for (var k = 0; k < view.length; k++) if (view[k].slug === currentId) { i = k; break; }
    if (shuffle && view.length > 1) {
      var j = i;
      while (j === i) j = Math.floor(Math.random() * view.length);
      load(view[j], true);
      return;
    }
    if (i < 0) { load(view[0], true); return; }
    var next = (i + delta + view.length) % view.length;
    load(view[next], true);
  }

  $$('[data-act="play"]').forEach(function (b) {
    b.addEventListener('click', toggle);
  });
  $$('[data-act="next"]').forEach(function (b) {
    b.addEventListener('click', function () { step(1); });
  });
  $$('[data-act="prev"]').forEach(function (b) {
    b.addEventListener('click', function () {
      /* first press restarts, a second one steps back — the familiar behaviour */
      if (audio.currentTime > 3) { audio.currentTime = 0; return; }
      step(-1);
    });
  });
  $$('[data-act="shuffle"]').forEach(function (b) {
    b.addEventListener('click', function () {
      shuffle = !shuffle;
      $$('[data-act="shuffle"]').forEach(function (o) {
        o.setAttribute('aria-pressed', String(shuffle));
      });
    });
  });

  function paint() {
    var on = !audio.paused && !audio.ended;
    if (on) { deck.setAttribute('data-playing', ''); if (sheet) sheet.setAttribute('data-playing', ''); }
    else { deck.removeAttribute('data-playing'); if (sheet) sheet.removeAttribute('data-playing'); }
    $$('[data-act="play"]').forEach(function (b) {
      b.setAttribute('aria-label', on ? 'Pause' : 'Play');
    });
    markCurrent();
    if (on) startLoop();
  }
  audio.addEventListener('play', paint);
  audio.addEventListener('pause', paint);
  audio.addEventListener('ended', function () { step(1); });

  /* Last-resort safety net. Enabling crossOrigin is what lets the analyser read
     the audio, but if the host turns out NOT to allow it the media itself fails
     to load -- and playback matters infinitely more than the visualisation. So
     the first media error while crossOrigin is set drops it and reloads. */
  audio.addEventListener('error', function () {
    if (!audio.crossOrigin || !currentId) return;
    var t = byId(currentId);
    if (!t) return;
    audio.removeAttribute('crossorigin');
    audio.crossOrigin = null;
    spectrum = false;
    vizMode('fallback');
    audio.src = t.url;
    var p = audio.play();
    if (p && p.catch) p.catch(function () {});
  });

  /* ==========================================================================
     Scrub bar — continuous feedback while dragging, commit on release
     ========================================================================== */
  /* Either argument may be omitted; an omitted one is left untouched, so a
     `progress` event can update the buffered bar without resetting the playhead. */
  function setProgress(played, buffered) {
    $$('.scrub, .deck-line').forEach(function (el) {
      if (played !== undefined) el.style.setProperty('--played', played);
      if (buffered !== undefined) el.style.setProperty('--buffered', buffered);
    });
  }

  function bufferedFraction() {
    if (!audio.duration || !audio.buffered || !audio.buffered.length) return 0;
    var t = audio.currentTime;
    for (var i = 0; i < audio.buffered.length; i++) {
      if (audio.buffered.start(i) <= t && t <= audio.buffered.end(i)) {
        return Math.min(1, audio.buffered.end(i) / audio.duration);
      }
    }
    return Math.min(1, audio.buffered.end(audio.buffered.length - 1) / audio.duration);
  }

  var seeks = $$('[data-role="seek"]');
  seeks.forEach(function (input) {
    input.addEventListener('pointerdown', function () { scrubbing = true; });
    input.addEventListener('input', function () {
      scrubbing = true;
      var f = Number(input.value) / 1000;
      setProgress(f);
      var d = audio.duration || (byId(currentId) ? byId(currentId).dur : 0);
      setAll('now', mmss(f * d));
      seeks.forEach(function (o) { if (o !== input) o.value = input.value; });
    });
    input.addEventListener('change', function () {
      var d = audio.duration;
      if (d) audio.currentTime = (Number(input.value) / 1000) * d;
      scrubbing = false;
    });
    /* a pointer released outside the input still ends the scrub */
    input.addEventListener('pointerup', function () { scrubbing = false; });
    input.addEventListener('pointercancel', function () { scrubbing = false; });
  });

  audio.addEventListener('timeupdate', function () {
    if (scrubbing) return;
    var d = audio.duration;
    if (!d) return;
    var f = audio.currentTime / d;
    setProgress(f, bufferedFraction());
    setAll('now', mmss(audio.currentTime));
    seeks.forEach(function (o) { o.value = String(Math.round(f * 1000)); });
  });
  audio.addEventListener('progress', function () {
    if (audio.duration) setProgress(undefined, bufferedFraction());
  });
  audio.addEventListener('loadedmetadata', function () {
    if (audio.duration) setAll('end', mmss(audio.duration));
  });

  /* ==========================================================================
     Volume
     ========================================================================== */
  var vols = $$('[data-role="vol"]');
  function applyVol(v) {
    audio.volume = v;
    $$('.vol-slider').forEach(function (el) { el.style.setProperty('--vol', v); });
    vols.forEach(function (o) { o.value = String(Math.round(v * 100)); });
  }
  vols.forEach(function (input) {
    input.addEventListener('input', function () { applyVol(Number(input.value) / 100); });
  });
  applyVol(0.85);

  /* ==========================================================================
     The now-playing sheet (mobile)
     ========================================================================== */
  var sheetOpen = false;
  function openSheet() {
    if (!sheet || sheetOpen) return;
    sheetOpen = true;
    sheet.setAttribute('data-open', '');
    sheet.removeAttribute('aria-hidden');
    document.body.classList.add('sheet-open');
    var g = $('#sheetGrip');
    if (g) g.focus({ preventScroll: true });
  }
  function shutSheet() {
    if (!sheet || !sheetOpen) return;
    sheetOpen = false;
    sheet.removeAttribute('data-open');
    sheet.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('sheet-open');
    var o = $('#deckOpen');
    if (o) o.focus({ preventScroll: true });
  }
  var deckOpen = $('#deckOpen');
  if (deckOpen) deckOpen.addEventListener('click', openSheet);
  var sheetGrip = $('#sheetGrip');
  if (sheetGrip) sheetGrip.addEventListener('click', shutSheet);

  /* ==========================================================================
     Keyboard shortcuts — the page advertises these, so they must all work
     ========================================================================== */
  document.addEventListener('keydown', function (e) {
    var t = e.target;
    var typing = t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' ||
                       t.isContentEditable);
    if (e.key === '/' && !typing) { e.preventDefault(); searchInput.focus(); return; }
    if (e.key === 'Escape') {
      if (sheetOpen) { shutSheet(); return; }
      if (t === searchInput) { searchInput.blur(); return; }
    }
    if (typing) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;

    switch (e.key) {
      case ' ':
      case 'Spacebar':
        e.preventDefault(); toggle(); break;
      case 'ArrowRight':
        if (audio.duration) { e.preventDefault(); audio.currentTime = Math.min(audio.duration, audio.currentTime + 5); }
        break;
      case 'ArrowLeft':
        if (audio.duration) { e.preventDefault(); audio.currentTime = Math.max(0, audio.currentTime - 5); }
        break;
      case 'n': case 'N': step(1); break;
      case 'p': case 'P': step(-1); break;
      case 's': case 'S':
        shuffle = !shuffle;
        $$('[data-act="shuffle"]').forEach(function (o) {
          o.setAttribute('aria-pressed', String(shuffle));
        });
        break;
    }
  });

  /* ==========================================================================
     Visualisation — real AnalyserNode, with an honest fallback
     --------------------------------------------------------------------------
     Cross-origin media taints a MediaElementSource: the analyser then returns
     silence (all zeros) rather than failing loudly. So we (a) only attach the
     analyser when a CORS probe says the audio host allows it, and (b) still
     watch for an all-zero stream and retire the canvas if it happens. The
     fallback is driven by playback state, never a dead canvas.
     ========================================================================== */
  var ac = null, analyser = null, freq = null, smooth = null;
  var spectrum = false, probeOK = false, zeroFrames = 0;
  var attempted = false, looping = false;

  function vizMode(mode) {
    deck.setAttribute('data-viz', mode);
    if (sheet) sheet.setAttribute('data-viz', mode);
  }
  vizMode('fallback');

  /* Probe whether the audio host permits CORS reads. If it does, the element
     can carry crossOrigin and the analyser gets real data. If it does not, we
     never set crossOrigin -- setting it without permission would break
     PLAYBACK, which matters far more than the visualisation. */
  (function probe() {
    if (!window.fetch || !TRACKS.length) return;
    try {
      fetch(TRACKS[0].url, { method: 'GET', mode: 'cors', headers: { Range: 'bytes=0-0' } })
        .then(function (r) { if (r.ok || r.status === 206) probeOK = true; })
        .catch(function () { probeOK = false; });
    } catch (err) { probeOK = false; }
  })();

  function ensureSpectrum() {
    /* createMediaElementSource may only ever be called once per element, so a
       failed attempt is never retried. */
    if (spectrum || attempted || !probeOK) return;
    var Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    attempted = true;
    try {
      if (!audio.crossOrigin) {
        /* setting crossOrigin requires reloading the media for it to apply */
        var at = audio.currentTime, wasPlaying = !audio.paused;
        audio.crossOrigin = 'anonymous';
        var src = audio.src;
        audio.src = src;
        audio.currentTime = at || 0;
        if (wasPlaying) { var q = audio.play(); if (q && q.catch) q.catch(function () {}); }
      }
      ac = new Ctx();
      var node = ac.createMediaElementSource(audio);
      analyser = ac.createAnalyser();
      analyser.fftSize = 1024;
      analyser.smoothingTimeConstant = 0.72;
      node.connect(analyser);
      analyser.connect(ac.destination);
      freq = new Uint8Array(analyser.frequencyBinCount);
      spectrum = true;
      vizMode('spectrum');
      startLoop();
    } catch (err) {
      spectrum = false;
      vizMode('fallback');
    }
    if (ac && ac.state === 'suspended' && ac.resume) ac.resume();
  }

  var BARS = 44;
  /* The draw loop only exists while there is a real spectrum to draw. With the
     CSS fallback there is nothing for JS to do, so no frames are burned. */
  function startLoop() {
    if (looping || !spectrum) return;
    looping = true;
    requestAnimationFrame(tick);
  }

  function tick() {
    if (!spectrum || audio.paused || audio.ended) { looping = false; return; }
    analyser.getByteFrequencyData(freq);
    var sum = 0;
    for (var i = 0; i < freq.length; i++) sum += freq[i];
    if (sum === 0) {
      /* tainted or genuinely silent: give it a moment, then stop pretending */
      if (++zeroFrames > 90) {
        spectrum = false;
        vizMode('fallback');
        looping = false;
        return;
      }
    } else {
      zeroFrames = 0;
      drawBars();
    }
    requestAnimationFrame(tick);
  }

  function drawBars() {
    if (!smooth) { smooth = new Float32Array(BARS); }
    $$('canvas.viz').forEach(function (cv) {
      if (!cv.offsetParent) return;                 // not on screen: skip the work
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      var w = cv.clientWidth, h = cv.clientHeight;
      if (!w || !h) return;
      if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) {
        cv.width = Math.round(w * dpr);
        cv.height = Math.round(h * dpr);
      }
      var g = cv.getContext('2d');
      if (!g) return;
      g.setTransform(dpr, 0, 0, dpr, 0, 0);
      g.clearRect(0, 0, w, h);
      var grad = g.createLinearGradient(0, h, 0, 0);
      grad.addColorStop(0, '#7E6733');
      grad.addColorStop(1, '#E8C879');
      g.fillStyle = grad;
      var bw = w / BARS;
      var barW = Math.max(1.5, bw - 2);
      /* logarithmic bin mapping: low end gets the resolution it deserves */
      for (var b = 0; b < BARS; b++) {
        var lo = Math.floor(Math.pow(b / BARS, 1.8) * freq.length);
        var hi = Math.max(lo + 1, Math.floor(Math.pow((b + 1) / BARS, 1.8) * freq.length));
        var peak = 0;
        for (var k = lo; k < hi && k < freq.length; k++) if (freq[k] > peak) peak = freq[k];
        var target = peak / 255;
        smooth[b] += (target - smooth[b]) * 0.34;     // decay, so it is not jittery
        var bh = Math.max(1.5, smooth[b] * h);
        g.fillRect(b * bw + (bw - barW) / 2, h - bh, barW, bh);
      }
    });
  }

  /* ==========================================================================
     Boot
     ========================================================================== */
  render();
  /* Preselect a track so the deck is never blank, but DO NOT play it. */
  if (TRACKS.length) load(TRACKS[0], false);
  paint();

  /* reduced-motion changes take effect without a reload */
  if (reduced.addEventListener) {
    reduced.addEventListener('change', function () { markCurrent(); });
  }
})();
