/* Duet pitch deck. A classic script so it runs over file:// in Chrome; the pure state
   functions hang off window.Deck so the Node tests can load this file without a DOM. */
(function () {
  'use strict';

  var CARDS = 7;
  var BUILDS = { 1: 3 };               // card -> reveal steps before advance moves on
  var FLIP_MS = 700;                   // per flipbook photo
  var FLIP_HOLD_MS = 2000;             // on the finished piece
  var TURNS = 10;                      // exchanges in the flipbook session
  var FLIPBOOK = ['turn-00-start.jpg'];
  for (var n = 1; n <= TURNS; n++) {
    var nn = (n < 10 ? '0' : '') + n;
    FLIPBOOK.push('turn-' + nn + '-human.jpg', 'turn-' + nn + '-robot.jpg');
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
    return 'turn ' + Math.ceil(i / 2) + ' of ' + TURNS + ' · ' + (i % 2 ? 'you' : 'Duet');
  }
  function flipDelay(i) { return i === FLIPBOOK.length - 1 ? FLIP_HOLD_MS : FLIP_MS; }
  function nextFlip(i) { return (i + 1) % FLIPBOOK.length; }

  /* autoplay: cycle through every reveal and card, paced by a speed multiplier */
  var SPEEDS = [0.5, 1, 1.5, 2];       // the dropdown's multipliers
  var REVEAL_MS = 2000;                // per reveal step (card 1's lines), at 1x
  var DWELL_MS = 6000;                 // per card, at 1x
  var DWELL_BY_CARD = { 4: 12000 };    // the flipbook card gets most of a loop

  function cycle(s) {                  // advance, but the last card wraps to the first
    var next = advance(s);
    return next === s ? jump(1) : next;
  }
  function playDelay(s, speed) {
    var ms = s.build < builds(s.card) ? REVEAL_MS : (DWELL_BY_CARD[s.card] || DWELL_MS);
    return Math.round(ms / speed);
  }

  window.Deck = {
    CARDS: CARDS, BUILDS: BUILDS, FLIPBOOK: FLIPBOOK,
    advance: advance, back: back, jump: jump, parseHash: parseHash,
    flipLabel: flipLabel, flipDelay: flipDelay, nextFlip: nextFlip,
    SPEEDS: SPEEDS, cycle: cycle, playDelay: playDelay
  };

  if (typeof document === 'undefined') return;   // Node tests stop here

  /* ---- wiring ---- */
  var state = { card: 1, build: 0 };
  var stage, counters, flipImg, flipLabelEl, cards;
  var playing = false, speed = 1, timer = null, playBtn, speedSel;

  function render() {
    cards.forEach(function (el) {
      var n = parseInt(el.getAttribute('data-card'), 10);
      var active = n === state.card;
      el.classList.toggle('active', active);
      if (active) el.setAttribute('data-build', String(state.build));
    });
    counters.forEach(function (el) { el.textContent = state.card + ' / ' + CARDS; });
    if (parseHash(location.hash) !== state.card) history.replaceState(null, '', '#' + state.card);
  }
  function set(next) {
    if (next === state) return;
    state = next;
    render();
    schedule();                        // a manual move restarts the autoplay clock
  }

  /* ---- autoplay ---- */
  function schedule() {
    if (timer) { clearTimeout(timer); timer = null; }
    if (!playing) return;
    timer = setTimeout(function () { set(cycle(state)); }, playDelay(state, speed));
  }
  function setPlaying(on) {
    playing = on;
    stage.classList.toggle('playing', on);
    if (playBtn) {
      playBtn.textContent = on ? '\u275A\u275A Pause' : '\u25B6 Play';
      playBtn.setAttribute('aria-pressed', String(on));
    }
    schedule();
  }
  function setSpeed(v) {
    speed = v;
    stage.style.setProperty('--speed', String(v));
    if (speedSel && speedSel.value !== String(v)) speedSel.value = String(v);
    schedule();
  }

  function onKey(e) {
    var t = e.target;
    if (t && t.matches && t.matches('input,textarea,select,[contenteditable]')) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    switch (e.key) {
      case 'p': case 'P': setPlaying(!playing); return;
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
    if (e.target.closest && e.target.closest('.playbar, a[href]')) return;   // the controls and every link own their clicks
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
    counters = Array.prototype.slice.call(document.querySelectorAll('.counter'));
    flipImg = document.getElementById('flip');
    flipLabelEl = document.getElementById('flipLabel');
    cards = Array.prototype.slice.call(document.querySelectorAll('.card'));
    playBtn = document.getElementById('play');
    speedSel = document.getElementById('speed');
    if (playBtn) playBtn.addEventListener('click', function () { setPlaying(!playing); playBtn.blur(); });
    if (speedSel) speedSel.addEventListener('change', function () { setSpeed(parseFloat(speedSel.value)); speedSel.blur(); });
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
