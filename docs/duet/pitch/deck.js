/* Duet pitch deck. A classic script so it runs over file:// in Chrome; the pure state
   functions hang off window.Deck so the Node tests can load this file without a DOM. */
(function () {
  'use strict';

  var CARDS = 7;
  var BUILDS = { 1: 3 };               // card -> reveal steps before advance moves on
  var FLIP_MS = 700;                   // per flipbook photo
  var FLIP_HOLD_MS = 2000;             // on the finished piece
  var FLIPBOOK = ['turn-00-start.jpg'];
  for (var n = 1; n <= 6; n++) {
    FLIPBOOK.push('turn-0' + n + '-human.jpg', 'turn-0' + n + '-robot.jpg');
  }

  function clamp(card) { return Math.min(CARDS, Math.max(1, card)); }
  function builds(card) { return BUILDS[card] || 0; }

  function advance(s) {
    if (s.build < builds(s.card)) return { card: s.card, build: s.build + 1 };
    if (s.card < CARDS) return { card: s.card + 1, build: 0 };
    return s;
  }
  function back(s) {
    if (s.build > 0) return { card: s.card, build: s.build - 1 };
    if (s.card > 1) return { card: s.card - 1, build: builds(s.card - 1) };
    return s;
  }
  function jump(card) { return { card: clamp(card), build: 0 }; }
  function parseHash(hash) {
    var m = /^#(\d+)$/.exec(hash || '');
    return m ? clamp(parseInt(m[1], 10)) : 1;
  }
  function flipLabel(i) {
    if (i === 0) return 'start';
    return 'turn ' + Math.ceil(i / 2) + ' of 6 · ' + (i % 2 ? 'you' : 'Duet');
  }
  function flipDelay(i) { return i === FLIPBOOK.length - 1 ? FLIP_HOLD_MS : FLIP_MS; }
  function nextFlip(i) { return (i + 1) % FLIPBOOK.length; }

  window.Deck = {
    CARDS: CARDS, BUILDS: BUILDS, FLIPBOOK: FLIPBOOK,
    advance: advance, back: back, jump: jump, parseHash: parseHash,
    flipLabel: flipLabel, flipDelay: flipDelay, nextFlip: nextFlip
  };

  if (typeof document === 'undefined') return;   // Node tests stop here

  /* ---- wiring ---- */
  var state = { card: 1, build: 0 };
  var stage, counter, flipImg, flipLabelEl, cards;

  function render() {
    cards.forEach(function (el) {
      var n = parseInt(el.getAttribute('data-card'), 10);
      var active = n === state.card;
      el.classList.toggle('active', active);
      if (active) el.setAttribute('data-build', String(state.build));
    });
    counter.textContent = state.card + ' / ' + CARDS;
    if (parseHash(location.hash) !== state.card) history.replaceState(null, '', '#' + state.card);
  }
  function set(next) {
    if (next === state) return;
    state = next;
    render();
  }

  function onKey(e) {
    var t = e.target;
    if (t && t.matches && t.matches('input,textarea,[contenteditable]')) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    switch (e.key) {
      case 'ArrowRight': case ' ': case 'PageDown': e.preventDefault(); set(advance(state)); return;
      case 'ArrowLeft': case 'PageUp': e.preventDefault(); set(back(state)); return;
      case 'Home': set(jump(1)); return;
      case 'End': set(jump(CARDS)); return;
      case 'f': case 'F': toggleFullscreen(); return;
      default:
        if (/^[1-7]$/.test(e.key)) set(jump(parseInt(e.key, 10)));
    }
  }
  function onClick(e) {
    if (document.body.classList.contains('dev')) return;   // developer mode owns clicks
    var r = stage.getBoundingClientRect();
    var x = (e.clientX - r.left) / r.width;
    set(x < 1 / 3 ? back(state) : advance(state));
  }
  function toggleFullscreen() {
    if (document.fullscreenElement) { document.exitFullscreen(); return; }
    if (stage.requestFullscreen) stage.requestFullscreen();
    else if (stage.webkitRequestFullscreen) stage.webkitRequestFullscreen();
  }
  function preload() {
    FLIPBOOK.forEach(function (name) { var im = new Image(); im.src = 'img/' + name; });
  }
  function runFlipbook() {
    var i = 0;
    function show() {
      flipImg.src = 'img/' + FLIPBOOK[i];
      flipLabelEl.textContent = flipLabel(i);
      setTimeout(function () { i = nextFlip(i); show(); }, flipDelay(i));
    }
    show();
  }

  document.addEventListener('DOMContentLoaded', function () {
    stage = document.querySelector('.stage');
    counter = document.getElementById('counter');
    flipImg = document.getElementById('flip');
    flipLabelEl = document.getElementById('flipLabel');
    cards = Array.prototype.slice.call(document.querySelectorAll('.card'));
    state = { card: parseHash(location.hash), build: 0 };
    document.addEventListener('keydown', onKey);
    stage.addEventListener('click', onClick);
    window.addEventListener('hashchange', function () {
      var card = parseHash(location.hash);
      if (card !== state.card) set(jump(card));
    });
    preload();
    render();
    runFlipbook();
  });
})();
