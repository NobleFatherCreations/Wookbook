/* The seal + THE HOUSE catalogue drawer. Trimmed from the current `nf-seal`
   generation: drawer open/close, arrow-key traversal, and the ink-veil exit.
   The split-text / count-up / scroll-reveal / ribbon engines were dropped --
   this page carries its own motion. */
(function () {
  var root = document.getElementById('nf-chrome');
  if (!root) return;
  var seal = root.querySelector('.nf-seal'),
      scrim = root.querySelector('.nf-scrim'),
      panel = root.querySelector('.nf-panel'),
      close = root.querySelector('.nf-close');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function open() {
    root.classList.add('nf-open');
    seal.setAttribute('aria-expanded', 'true');
    panel.removeAttribute('aria-hidden');
    close.focus({ preventScroll: true });
  }
  function shut() {
    root.classList.remove('nf-open');
    seal.setAttribute('aria-expanded', 'false');
    panel.setAttribute('aria-hidden', 'true');
    seal.focus({ preventScroll: true });
  }
  seal.addEventListener('click', open);
  close.addEventListener('click', shut);
  scrim.addEventListener('click', shut);

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && root.classList.contains('nf-open')) { shut(); return; }
    if (!root.classList.contains('nf-open')) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      var links = [].slice.call(panel.querySelectorAll('.nf-row a'));
      var i = links.indexOf(document.activeElement);
      var next = e.key === 'ArrowDown'
        ? (i + 1) % links.length
        : (i - 1 + links.length) % links.length;
      links[next].focus();
      e.preventDefault();
    }
  });

  /* ink-veil exit: same-origin links leave through the dark. Where the browser
     does real cross-document view transitions, stand down and let it morph. */
  var veil = root.querySelector('.nf-veil');
  var nativeVT = !!document.startViewTransition &&
                 CSS.supports('view-transition-name', 'nf-seal');
  document.addEventListener('click', function (e) {
    if (nativeVT || reduced || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey ||
        e.button !== 0) return;
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a || a.target === '_blank') return;
    var href = a.getAttribute('href');
    if (!href || href.charAt(0) === '#' || /^(mailto|tel|javascript):/.test(href)) return;
    var u;
    try { u = new URL(a.href, location.href); } catch (_) { return; }
    if (u.origin !== location.origin) return;
    if (u.pathname === location.pathname && u.hash) return;
    e.preventDefault();
    veil.classList.add('nf-veil-out');
    setTimeout(function () { location.href = a.href; }, 190);
  }, true);
  window.addEventListener('pageshow', function (e) {
    if (e.persisted) veil.classList.remove('nf-veil-out');
  });
})();
