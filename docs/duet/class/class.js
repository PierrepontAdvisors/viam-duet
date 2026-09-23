/* Duet class deck. A classic script so it runs over file:// in Chrome; the pure state functions
   hang off window.ClassDeck so the Node tests can load this file without a DOM. Unlike deck.js
   the card count comes from the page (?cut=10 drops the cards marked data-cut="20"), so every
   pure function takes the deck it works on. */
(function () {
  'use strict';

  var PITCH_IMG = '../pitch/img/';     // the flipbook photos live with the pitch deck
  var FLIP_MS = 700;                   // per flipbook photo
  var FLIP_HOLD_MS = 2000;             // on the finished piece
  var TURNS = 10;                      // exchanges in the flipbook session
  var FLIPBOOK = ['turn-00-start.jpg'];
  for (var n = 1; n <= TURNS; n++) {
    var nn = (n < 10 ? '0' : '') + n;
    FLIPBOOK.push('turn-' + nn + '-human.jpg', 'turn-' + nn + '-robot.jpg');
  }

  /* ---- the deck: a card count and the reveal steps per card ---- */
  function parseCut(search) {          // ?cut=10 is the ten-minute version; anything else is the full deck
    var m = /[?&]cut=(\d+)/.exec(search || '');
    return m && m[1] === '10' ? 10 : 0;
  }
  function keep(specs, cut) {          // specs: [{cut: '20' | '', builds: k}] in page order
    return specs.filter(function (c) { return !(cut === 10 && c.cut === '20'); });
  }
  function deckOf(specs) {
    var steps = {};
    specs.forEach(function (c, i) { if (c.builds) steps[i + 1] = c.builds; });
    return { cards: specs.length, builds: steps };
  }
  function renumber(kicker, card) {    // "04 · Why I built this" becomes "03 · ..." in the cut
    return kicker.replace(/^\s*\d+/, (card < 10 ? '0' : '') + card);
  }

  function clamp(card, deck) { return Math.min(deck.cards, Math.max(1, card)); }
  function builds(card, deck) { return deck.builds[card] || 0; }

  function advance(s, deck) {
    if (s.build < builds(s.card, deck)) return { card: s.card, build: s.build + 1 };
    if (s.card < deck.cards) return { card: s.card + 1, build: 0 };
    return s;
  }
  function back(s, deck) {
    if (s.build > 0) return { card: s.card, build: s.build - 1 };
    if (s.card > 1) return { card: s.card - 1, build: builds(s.card - 1, deck) };
    return s;
  }
  function jump(card, deck) { return { card: clamp(card, deck), build: 0 }; }
  function parseHash(hash, deck) {
    var m = /^#(\d+)$/.exec(hash || '');
    return m ? clamp(parseInt(m[1], 10), deck) : 1;
  }
  function flipLabel(i) {
    if (i === 0) return 'start';
    return 'turn ' + Math.ceil(i / 2) + ' of ' + TURNS + ' · ' + (i % 2 ? 'you' : 'Duet');
  }
  function flipDelay(i) { return i === FLIPBOOK.length - 1 ? FLIP_HOLD_MS : FLIP_MS; }
  function nextFlip(i) { return (i + 1) % FLIPBOOK.length; }

  window.ClassDeck = {
    PITCH_IMG: PITCH_IMG, FLIPBOOK: FLIPBOOK,
    parseCut: parseCut, keep: keep, deckOf: deckOf, renumber: renumber,
    advance: advance, back: back, jump: jump, parseHash: parseHash,
    flipLabel: flipLabel, flipDelay: flipDelay, nextFlip: nextFlip
  };

  if (typeof document === 'undefined') return;   // Node tests stop here

  /* ---- wiring ---- */
  var deck, state = { card: 1, build: 0 };
  var stage, cards, counters, flipImg, flipLabelEl, flipCard, flipTimer = null, videos;

  function specOf(el) {
    return { cut: el.getAttribute('data-cut') || '', builds: parseInt(el.getAttribute('data-builds') || '0', 10) };
  }
  /* drop the cut cards from the page, then number what is left: data-card, the kicker prefix, the counter */
  function setup(cut) {
    var all = Array.prototype.slice.call(document.querySelectorAll('.card'));
    cards = [];
    all.forEach(function (el) {
      if (keep([specOf(el)], cut).length) cards.push(el); else el.parentNode.removeChild(el);   // one-element keep: same rule as the deck
    });
    cards.forEach(function (el, i) {
      el.setAttribute('data-card', String(i + 1));
      var k = el.querySelector('.kicker');
      if (k) k.textContent = renumber(k.textContent, i + 1);
    });
    deck = deckOf(cards.map(specOf));
  }

  function render() {
    cards.forEach(function (el, i) {
      var active = i + 1 === state.card;
      el.classList.toggle('active', active);
      Array.prototype.forEach.call(el.querySelectorAll('[data-step]'), function (r) {
        r.classList.toggle('shown', active && parseInt(r.getAttribute('data-step'), 10) <= state.build);
      });
    });
    counters.forEach(function (el) { el.textContent = state.card + ' / ' + deck.cards; });
    if (parseHash(location.hash, deck) !== state.card) history.replaceState(null, '', '#' + state.card);
    media();
  }
  function set(next) {
    if (next === state) return;
    state = next;
    render();
  }

  /* the flipbook and the four clips run only while their card is up */
  function media() {
    var flipping = !!flipCard && flipCard.classList.contains('active');
    if (flipping && flipTimer === null) runFlipbook();
    if (!flipping && flipTimer !== null) { clearTimeout(flipTimer); flipTimer = null; }
    videos.forEach(function (v) {
      var up = v.closest('.card').classList.contains('active');
      if (up) { var p = v.play(); if (p && p.catch) p.catch(function () {}); } else v.pause();   // play() rejects when pause() interrupts it, or when a local-only clip is missing on a fresh clone; the console already shows the failed load
    });
  }
  function runFlipbook() {
    var i = 0;
    function show() {
      flipImg.src = PITCH_IMG + FLIPBOOK[i];
      flipLabelEl.textContent = flipLabel(i);
      flipTimer = setTimeout(function () { i = nextFlip(i); show(); }, flipDelay(i));
    }
    show();
  }
  function preload() {
    FLIPBOOK.forEach(function (name) { var im = new Image(); im.src = PITCH_IMG + name; });
  }

  function onKey(e) {
    var t = e.target;
    if (t && t.matches && t.matches('input,textarea,select,[contenteditable]')) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    switch (e.key) {
      case 'ArrowRight': case ' ': case 'PageDown': e.preventDefault(); set(advance(state, deck)); return;
      case 'ArrowLeft': case 'PageUp': e.preventDefault(); set(back(state, deck)); return;
      case 'Home': set(jump(1, deck)); return;
      case 'End': set(jump(deck.cards, deck)); return;
      case 'f': case 'F': toggleFullscreen(); return;
      case '0': set(jump(10, deck)); return;
      default:
        if (/^[1-9]$/.test(e.key)) set(jump(parseInt(e.key, 10), deck));
    }
  }
  function onClick(e) {
    if (document.body.classList.contains('dev')) return;   // developer mode owns clicks
    if (e.target.closest && e.target.closest('a[href]')) return;   // links own their clicks
    var r = stage.getBoundingClientRect();
    var x = (e.clientX - r.left) / r.width;
    set(x < 1 / 3 ? back(state, deck) : advance(state, deck));
  }
  function toggleFullscreen() {
    if (document.fullscreenElement) { document.exitFullscreen(); return; }
    if (stage.requestFullscreen) stage.requestFullscreen();
    else if (stage.webkitRequestFullscreen) stage.webkitRequestFullscreen();
  }

  document.addEventListener('DOMContentLoaded', function () {
    stage = document.querySelector('.stage');
    setup(parseCut(location.search));
    counters = Array.prototype.slice.call(document.querySelectorAll('.counter'));
    flipImg = document.getElementById('flip');
    flipLabelEl = document.getElementById('flipLabel');
    flipCard = flipImg ? flipImg.closest('.card') : null;
    videos = Array.prototype.slice.call(document.querySelectorAll('.card video'));
    state = { card: parseHash(location.hash, deck), build: 0 };
    document.addEventListener('keydown', onKey);
    stage.addEventListener('click', onClick);
    /* a hidden pane or a backgrounded window refuses to start a video; try again when it comes back */
    document.addEventListener('visibilitychange', function () { if (!document.hidden) media(); });
    window.addEventListener('hashchange', function () {
      var card = parseHash(location.hash, deck);
      if (card !== state.card) set(jump(card, deck));
    });
    preload();
    render();
  });
})();
