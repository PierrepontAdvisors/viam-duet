# Duet Pitch Deck Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A seven-card HTML pitch deck for Duet, in bright Keith Haring plates, that opens from disk with no network on the presenting Mac and is talked through for two minutes before the live demo at 3:30 PM on 2026-09-19.

**Architecture:** Plain HTML, CSS, and a classic script under `docs/duet/pitch/`, nothing installed and no build step. The deck's state machine (card, reveal step, flipbook order) lives in `deck.js` as pure functions on `window.Deck`, guarded so Node can load the file without a DOM and test it; the same file wires keys, clicks, the hash, and the flipbook when a document exists. The look is a reusable SVG squiggle `<pattern>` drifting over one colour plate per card, with bold Fredoka type and content on white paper cards with thick black outlines.

**Tech Stack:** HTML5, CSS container units, inline SVG patterns and symbols, ES5-compatible classic JavaScript, Fredoka (variable woff2 embedded as a data URI), Node 24's built-in test runner (`node --test`) for the checks, the built-in browser for the visual pass.

**Spec:** `docs/superpowers/specs/2026-09-19-duet-pitch-deck-design.md`. Two facts found while planning amend its section 5, and Task 6 writes the amendment: Chrome (the default browser on this Mac) blocks web fonts and `type="module"` scripts loaded over `file://` under its CORS rules, so the font is embedded as a data URI in `fredoka.css` and the script is a classic script; and the photos are already 704 × 960, so they are copied, not downscaled.

---

## File structure

```
docs/duet/pitch/
  index.html        markup for the seven cards, the SVG defs (squiggle motifs, two patterns, three artist symbols), the developer-mode elements, and the two script tags
  deck.css          stage and plates, pattern drift, type, paper cards, chips, bubble, flipbook, counter, developer-mode styles
  fredoka.css       one @font-face with the Fredoka variable woff2 as a base64 data URI (generated once, Task 1)
  deck.js           window.Deck pure state functions, then DOM wiring guarded by typeof document
  dev.js            the D-key developer mode from ~/.claude/rules/common/preview-dev-mode.md, unchanged
  README.md         how to open it and the keys (Task 6)
  img/turn-00-start.jpg, img/turn-01-human.jpg ... img/turn-06-robot.jpg   13 photos copied from code/hackathon/sessions/20260918-190258/
code/hackathon/pagetests/pitch.test.mjs   all checks for the deck, run with the existing page tests
```

Paths below are relative to the repository root `<repo>` unless a step says otherwise. Tests run from `code/hackathon`. Commits go on `feat/duet-design`, the branch already checked out; never stage anything under `code/hackathon/duet/`, `.env`, or `.gitignore`.

---

### Task 1: Test scaffold and assets (photos and the embedded font)

**Files:**
- Create: `code/hackathon/pagetests/pitch.test.mjs`
- Create: `docs/duet/pitch/img/*.jpg` (13 copies)
- Create: `docs/duet/pitch/fredoka.css`

- [ ] **Step 1: Write the failing tests for the assets**

Create `code/hackathon/pagetests/pitch.test.mjs`:

```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

// pagetests/ -> code/hackathon/ -> Viam/ -> docs/duet/pitch/
const DIR = fileURLToPath(new URL('../../../docs/duet/pitch/', import.meta.url));
const read = (name) => readFileSync(DIR + name, 'utf8');

const FLIPBOOK = ['turn-00-start.jpg',
  ...[1, 2, 3, 4, 5, 6].flatMap((n) => [`turn-0${n}-human.jpg`, `turn-0${n}-robot.jpg`])];

test('the 13 flipbook photos from session 20260918-190258 are in img/', () => {
  for (const f of FLIPBOOK) assert.ok(existsSync(DIR + 'img/' + f), `missing img/${f}`);
  assert.equal(readdirSync(DIR + 'img').filter((f) => f.endsWith('.jpg')).length, 13);
});

test('fredoka.css embeds the variable font as a data URI, so file:// in Chrome can use it', () => {
  const css = read('fredoka.css');
  assert.match(css, /font-family:\s*["']Fredoka["']/);
  assert.match(css, /font-weight:\s*400 700/);
  assert.match(css, /url\(data:font\/woff2;base64,[A-Za-z0-9+/=]{1000,}\)\s*format\(["']woff2["']\)/);
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run from `code/hackathon`:

```bash
cd <repo>/code/hackathon && node --test pagetests/pitch.test.mjs
```

Expected: 2 failing tests. The first fails with `missing img/turn-00-start.jpg`; the second throws `ENOENT` for `fredoka.css`.

- [ ] **Step 3: Copy the 13 photos**

```bash
cd <repo> && mkdir -p docs/duet/pitch/img && cp code/hackathon/sessions/20260918-190258/turn-0[0-6]-*.jpg docs/duet/pitch/img/ && ls docs/duet/pitch/img | wc -l && du -sh docs/duet/pitch/img
```

Expected: `13` and about `1.4M`. The originals are 704 × 960, small enough already; nothing is resized.

- [ ] **Step 4: Fetch Fredoka once and write fredoka.css**

The URL is the latin subset of the variable font that Google Fonts serves for `family=Fredoka:wght@400..700` (read on 2026-09-19; 29,704 bytes). If the fetch fails, the fallback stack in `deck.css` renders Chalkboard SE, and the test stays red until the network is back.

```bash
cd <repo>/docs/duet/pitch && S=/private/tmp/claude-501/<repo-slug>/<session>/scratchpad && mkdir -p "$S" && curl -sSf -o "$S/Fredoka.woff2" "https://fonts.gstatic.com/s/fredoka/v17/X7n64b87HvSqjb_WIi2yDCRwoQ_k7367_DWu89XgHPyh.woff2" && file "$S/Fredoka.woff2" && { printf '/* Fredoka variable 400-700, latin subset, from Google Fonts (OFL). Embedded because Chrome blocks web fonts loaded over file://. */\n@font-face { font-family: "Fredoka"; font-style: normal; font-weight: 400 700; font-display: swap; src: url(data:font/woff2;base64,'; base64 -i "$S/Fredoka.woff2" | tr -d '\n'; printf ') format("woff2"); }\n'; } > fredoka.css && wc -c fredoka.css
```

Expected: `file` reports `Web Open Font Format (Version 2)` and `fredoka.css` is about 40,000 bytes.

- [ ] **Step 5: Run the tests to verify they pass**

```bash
cd <repo>/code/hackathon && node --test pagetests/pitch.test.mjs
```

Expected: `pass 2`, `fail 0`.

- [ ] **Step 6: Commit**

```bash
cd <repo> && git add code/hackathon/pagetests/pitch.test.mjs docs/duet/pitch/img docs/duet/pitch/fredoka.css && git commit -m "feat(pitch): deck assets, the 13 session photos and Fredoka embedded for file://"
```

---

### Task 2: deck.js, the state machine and the wiring

**Files:**
- Create: `docs/duet/pitch/deck.js`
- Modify: `code/hackathon/pagetests/pitch.test.mjs` (append)

- [ ] **Step 1: Write the failing tests for the pure functions**

Append to `code/hackathon/pagetests/pitch.test.mjs`:

```js
// deck.js is a classic script for file://; Node loads it in a sandbox with no document,
// which also proves the DOM wiring is guarded.
function loadDeck() {
  const sandbox = { window: {} };
  vm.runInNewContext(read('deck.js'), sandbox);
  return sandbox.window.Deck;
}

test('advance reveals card 1 one line at a time, then moves to card 2', () => {
  const D = loadDeck();
  let s = { card: 1, build: 0 };
  s = D.advance(s); assert.deepEqual(s, { card: 1, build: 1 });
  s = D.advance(s); assert.deepEqual(s, { card: 1, build: 2 });
  s = D.advance(s); assert.deepEqual(s, { card: 1, build: 3 });
  s = D.advance(s); assert.deepEqual(s, { card: 2, build: 0 });
  s = D.advance(s); assert.deepEqual(s, { card: 3, build: 0 });
});

test('advance stops on the last card and never mutates its input', () => {
  const D = loadDeck();
  const last = Object.freeze({ card: 7, build: 0 });
  assert.equal(D.advance(last), last);
  const first = Object.freeze({ card: 1, build: 0 });
  D.advance(first);
  assert.deepEqual(first, { card: 1, build: 0 });
});

test('back hides the latest line on card 1, and from card 2 lands on card 1 fully revealed', () => {
  const D = loadDeck();
  assert.deepEqual(D.back({ card: 1, build: 2 }), { card: 1, build: 1 });
  assert.deepEqual(D.back({ card: 2, build: 0 }), { card: 1, build: 3 });
  assert.deepEqual(D.back({ card: 5, build: 0 }), { card: 4, build: 0 });
  const start = { card: 1, build: 0 };
  assert.equal(D.back(start), start);
});

test('jump clamps to 1..7 and starts that card unrevealed', () => {
  const D = loadDeck();
  assert.deepEqual(D.jump(4), { card: 4, build: 0 });
  assert.deepEqual(D.jump(0), { card: 1, build: 0 });
  assert.deepEqual(D.jump(99), { card: 7, build: 0 });
});

test('parseHash reads #n and falls back to card 1', () => {
  const D = loadDeck();
  assert.equal(D.parseHash('#3'), 3);
  assert.equal(D.parseHash('#12'), 7);
  assert.equal(D.parseHash(''), 1);
  assert.equal(D.parseHash('#nope'), 1);
  assert.equal(D.parseHash(undefined), 1);
});

test('the flipbook lists the 13 photos in turn order, labels them, and holds on the last', () => {
  const D = loadDeck();
  assert.deepEqual(D.FLIPBOOK, FLIPBOOK);
  assert.equal(D.flipLabel(0), 'start');
  assert.equal(D.flipLabel(1), 'turn 1 of 6 · you');
  assert.equal(D.flipLabel(2), 'turn 1 of 6 · Duet');
  assert.equal(D.flipLabel(11), 'turn 6 of 6 · you');
  assert.equal(D.flipLabel(12), 'turn 6 of 6 · Duet');
  assert.equal(D.flipDelay(0), 700);
  assert.equal(D.flipDelay(5), 700);
  assert.equal(D.flipDelay(12), 2000);
  assert.equal(D.nextFlip(3), 4);
  assert.equal(D.nextFlip(12), 0);
});
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd <repo>/code/hackathon && node --test pagetests/pitch.test.mjs
```

Expected: the 2 asset tests pass; the 6 new tests fail with `ENOENT ... deck.js`.

- [ ] **Step 3: Write deck.js**

Create `docs/duet/pitch/deck.js`:

```js
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
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd <repo>/code/hackathon && node --test pagetests/pitch.test.mjs
```

Expected: `pass 8`, `fail 0`.

- [ ] **Step 5: Commit**

```bash
cd <repo> && git add docs/duet/pitch/deck.js code/hackathon/pagetests/pitch.test.mjs && git commit -m "feat(pitch): deck state machine, keys, clicks, hash, and flipbook"
```

---

### Task 3: deck.css, plates, pattern, type, paper

**Files:**
- Create: `docs/duet/pitch/deck.css`
- Modify: `code/hackathon/pagetests/pitch.test.mjs` (append)

- [ ] **Step 1: Write the failing test**

Append to `code/hackathon/pagetests/pitch.test.mjs`:

```js
test('deck.css defines the seven plates, the drifting pattern, and respects reduced motion', () => {
  const css = read('deck.css');
  for (const p of ['plate-yellow', 'plate-red', 'plate-blue', 'plate-green', 'plate-orange', 'plate-cream', 'plate-black']) {
    assert.ok(css.includes('.' + p), `no .${p} rule`);
  }
  assert.match(css, /@keyframes drift/);
  assert.match(css, /prefers-reduced-motion:\s*reduce/);
  assert.match(css, /--yellow:\s*#ffd400/);
  assert.match(css, /--blue:\s*#1f4fd6/);
  assert.ok(css.includes('.dev-badge'), 'developer-mode styles are in deck.css');
});
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd <repo>/code/hackathon && node --test pagetests/pitch.test.mjs
```

Expected: 8 pass, 1 fails with `ENOENT ... deck.css`.

- [ ] **Step 3: Write deck.css**

Create `docs/duet/pitch/deck.css`. Sizes use `cqw` against the 16:9 stage (its height is 56.25cqw), so every card scales with the window.

```css
:root {
  --yellow: #ffd400; --red: #e5322d; --blue: #1f4fd6; --green: #17a34a; --orange: #ff7a00; --cream: #fff4d6;
  --ink: #111; --paper: #fff;
  --robot: #1b8f3a; --human: #c62828;                 /* the page's ink colours, for words about the ink */
  --story: "Fredoka", "Chalkboard SE", "Comic Sans MS", "Segoe Print", sans-serif;
  --tile: 160px;                                       /* the squiggle pattern period */
}
html, body { margin: 0; height: 100%; background: #000; overflow: hidden; }
body { display: flex; align-items: center; justify-content: center; font-family: var(--story); color: var(--ink); }
.defs { position: absolute; width: 0; height: 0; overflow: hidden; }
h1, h2, h3, p, ul, ol, figure { margin: 0; }
ul, ol { padding: 0; list-style: none; }

/* stage: a 16:9 box letterboxed in the viewport, same as the live page */
.stage { position: relative; width: min(100vw, 177.78vh); aspect-ratio: 16 / 9; overflow: hidden; background: #000;
         container-type: inline-size; user-select: none; cursor: default; }

/* cards and plates */
.card { position: absolute; inset: 0; background: var(--plate, #000); opacity: 0; pointer-events: none; transition: opacity .35s ease; }
.card.active { opacity: 1; pointer-events: auto; }
.plate-yellow { --plate: var(--yellow); }
.plate-red    { --plate: var(--red); }
.plate-blue   { --plate: var(--blue); }
.plate-green  { --plate: var(--green); }
.plate-orange { --plate: var(--orange); }
.plate-cream  { --plate: var(--cream); }
.plate-black  { --plate: #000; color: #fff; }

/* the Haring squiggle pattern: one tile, drifting one period so the loop is seamless */
.pattern { position: absolute; left: 0; top: 0; width: calc(100% + var(--tile)); height: calc(100% + var(--tile));
           color: #000; opacity: .14; pointer-events: none; animation: drift 27s linear infinite; }
.plate-cream .pattern { opacity: .10; }
.plate-black .pattern { opacity: 1; }
@keyframes drift { to { transform: translate(calc(-1 * var(--tile)), calc(-1 * var(--tile))); } }
@media (prefers-reduced-motion: reduce) { .pattern { animation: none; } .card { transition: none; } }

/* type */
.content { position: absolute; inset: 0; padding: 5cqw 6cqw; display: flex; flex-direction: column; justify-content: center; gap: 2cqw; }
.key { color: #fff; -webkit-text-stroke: .05em var(--ink); paint-order: stroke fill; }
.plate-black .key { color: var(--yellow); -webkit-text-stroke: 0; }
.paper { background: var(--paper); color: var(--ink); border: .4cqw solid var(--ink); border-radius: 1.6cqw; }

/* card 1, thesis */
.thesis { gap: 2.4cqw; }
.thesis .line { font-size: 5.2cqw; font-weight: 700; line-height: 1.15; opacity: 0; transform: translateY(1cqw);
                transition: opacity .4s ease, transform .4s ease; }
.card[data-build="1"] .line:nth-child(-n+1),
.card[data-build="2"] .line:nth-child(-n+2),
.card[data-build="3"] .line:nth-child(-n+3) { opacity: 1; transform: none; }

/* card 2, what Duet is */
.wordmark { font-size: 12cqw; font-weight: 700; line-height: 1; }
.what .sub { font-size: 4cqw; font-weight: 600; }
.beats { display: flex; gap: 3cqw; font-size: 2.4cqw; font-weight: 600; }
.chips { display: flex; gap: 2cqw; margin-top: 1cqw; }
.chip { display: flex; flex-direction: column; align-items: center; gap: .6cqw; padding: 1cqw 1.6cqw; font-size: 1.8cqw; font-weight: 700; }
.sample { width: 12cqw; height: 7.2cqw; display: block; }

/* card 3, one turn */
.turn { flex-direction: row; align-items: center; justify-content: center; gap: 3cqw; }
.photo { padding: .8cqw; display: flex; flex-direction: column; align-items: center; gap: .6cqw; font-size: 1.8cqw; font-weight: 700; }
.photo img { display: block; height: 38cqw; width: auto; border-radius: .8cqw; }
.bubble { position: relative; max-width: 30cqw; background: var(--yellow); border: .5cqw solid var(--ink);
          border-radius: 48% 52% 46% 54% / 58% 46% 54% 42%; padding: 2.4cqw 2.8cqw; font-size: 1.9cqw; font-weight: 700;
          line-height: 1.15; text-align: center; transform: rotate(-2deg); }
.bubble .adds { margin-top: 1cqw; color: var(--robot); }
.bubble::before, .bubble::after { content: ""; position: absolute; top: 62%; width: 0; height: 0; border-style: solid; border-color: transparent; }
.bubble::before { right: -3.2cqw; border-width: 1.5cqw 0 1.9cqw 3.4cqw; border-left-color: var(--ink); transform: rotate(8deg); }
.bubble::after  { right: -1.8cqw; border-width: .95cqw 0 1.25cqw 2.3cqw; border-left-color: var(--yellow); transform: rotate(8deg); }
.badge { display: inline-block; margin-top: 1.2cqw; padding: .4cqw 1.2cqw; border: .3cqw solid var(--ink); border-radius: 999px;
         background: #fff; font-size: 1.4cqw; }

/* card 4, co-creation */
.cocreate { flex-direction: row; align-items: center; gap: 4cqw; }
.cocreate .words { flex: 1; display: flex; flex-direction: column; gap: 2cqw; }
.cocreate h2 { font-size: 4.6cqw; font-weight: 700; line-height: 1.1; }
.cocreate .under { font-size: 2.4cqw; font-weight: 600; }
.flipwrap { display: flex; flex-direction: column; align-items: center; gap: 1cqw; }
.flip img { height: 40cqw; }
.chip-label { padding: .4cqw 1.4cqw; border: .3cqw solid var(--ink); border-radius: 999px; background: #fff; color: var(--ink);
              font-size: 1.6cqw; font-weight: 700; min-width: 14cqw; text-align: center; }

/* card 5, learning */
.learn h2 { font-size: 4.2cqw; font-weight: 700; line-height: 1.1; }
.lessons { display: flex; flex-direction: column; gap: 1.4cqw; }
.lessons li { display: flex; align-items: center; gap: 2cqw; font-size: 2.3cqw; font-weight: 600; }
.lessons .chip { flex: none; padding: .6cqw 1.2cqw; font-size: 1.4cqw; }
.lessons .sample { width: 9cqw; height: 5.4cqw; }
.learn .footer { font-size: 2.4cqw; font-weight: 700; margin-top: 1cqw; }

/* card 6, how it works */
.how { gap: 1.6cqw; padding: 3.5cqw 5cqw; }
.how h2 { font-size: 4.4cqw; font-weight: 700; line-height: 1; }
.how .sub { font-size: 2.6cqw; font-weight: 600; }
.nodes { display: flex; align-items: stretch; gap: 1cqw; }
.node { flex: 1; padding: 1.2cqw 1.4cqw; font-size: 1.45cqw; line-height: 1.25; font-weight: 500; }
.node h3 { font-size: 2.2cqw; font-weight: 700; margin-bottom: .4cqw; }
.arrow { align-self: center; font-size: 3cqw; font-weight: 700; }
.numbers { display: flex; gap: 1cqw; }
.num { flex: 1; padding: .8cqw 1cqw; display: flex; flex-direction: column; align-items: center; line-height: 1; }
.num b { font-size: 3cqw; }
.num span { font-size: 1.3cqw; font-weight: 600; margin-top: .3cqw; }
.strip { background: var(--ink); color: #fff; font-size: 1.3cqw; font-weight: 600; padding: .7cqw 1.2cqw; border-radius: 999px; text-align: center; }

/* card 7, the build */
.build { align-items: flex-start; }
.build h2 { font-size: 6cqw; font-weight: 700; line-height: 1.05; }
.credit { font-size: 2cqw; font-weight: 600; opacity: .85; }
.cta { margin-top: auto; font-size: 4cqw; font-weight: 700; color: var(--yellow); }

/* counter */
.counter { position: absolute; right: 1.2cqw; bottom: .9cqw; padding: .3cqw .9cqw; border-radius: 999px; background: rgba(0, 0, 0, .35);
           color: #fff; font-size: 1.2cqw; font-weight: 600; pointer-events: none; }

/* developer mode (press D), from ~/.claude/rules/common/preview-dev-mode.md */
body.dev [data-el]{outline:1px dashed rgba(39,67,227,.4);outline-offset:-1px;}
body.dev [data-el]:hover{outline:2px solid #2743E3;background:rgba(39,67,227,.07);cursor:crosshair;}
.dev-badge{position:fixed;top:12px;left:50%;transform:translateX(-50%);z-index:2147483000;display:none;
  padding:7px 14px;font:600 11px/1 system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;
  color:#fff;background:#2743E3;border-radius:999px;box-shadow:0 6px 20px rgba(39,67,227,.35);}
body.dev .dev-badge{display:block;}
.dev-label{position:fixed;z-index:2147483001;display:none;pointer-events:none;padding:4px 8px;
  font:600 11px/1 system-ui,sans-serif;color:#fff;background:#1B221D;border-radius:6px;white-space:nowrap;}
.dev-toast{position:fixed;bottom:70px;left:50%;transform:translateX(-50%) translateY(10px);z-index:2147483002;
  opacity:0;padding:9px 16px;font:600 12px/1 system-ui,sans-serif;color:#fff;background:#1B2FA8;border-radius:999px;
  transition:opacity .2s,transform .2s;pointer-events:none;}
.dev-toast.show{opacity:1;transform:translateX(-50%) translateY(0);}
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
cd <repo>/code/hackathon && node --test pagetests/pitch.test.mjs
```

Expected: `pass 9`, `fail 0`.

- [ ] **Step 5: Commit**

```bash
cd <repo> && git add docs/duet/pitch/deck.css code/hackathon/pagetests/pitch.test.mjs && git commit -m "feat(pitch): Haring plates, drifting squiggle pattern, type and paper styles"
```

---

### Task 4: index.html and dev.js, the seven cards

**Files:**
- Create: `docs/duet/pitch/index.html`
- Create: `docs/duet/pitch/dev.js`
- Modify: `code/hackathon/pagetests/pitch.test.mjs` (append)

- [ ] **Step 1: Write the failing structure tests**

Append to `code/hackathon/pagetests/pitch.test.mjs`:

```js
test('the deck has seven cards in order carrying the agreed copy, with plain apostrophes', () => {
  const h = read('index.html');
  const cards = [...h.matchAll(/<section class="card [^"]*" data-card="(\d)"/g)].map((m) => Number(m[1]));
  assert.deepEqual(cards, [1, 2, 3, 4, 5, 6, 7]);
  const copy = [
    'Anyone can now study with the greatest minds in history.',
    'Nobody could make art with them.',
    'Until <span class="key">today</span>.',
    'A robot arm that draws <span class="key">with</span> you.',
    'You make a mark.', 'It looks, understands, and answers.', 'In the hand of an artist you choose.',
    'A big bold amoeba-like creature with loops and eye-holes sprawls across the board.',
    "I'll add a small green spiral accent inside the lower loop body to give the creature a pulsing core.",
    '8 s to look and decide',
    'Everyone leaves with a one-of-a-kind piece, made with a <span class="key">partner</span>.',
    'Six exchanges. Two artists. One of them was a robot.',
    'And you learn their language by <span class="key">answering back</span>.',
    'One continuous outline, then motion ticks. Your blob becomes a figure.',
    "Your mark's edges run out to a grid. You start seeing the rectangle in everything.",
    'Dashes stream around your mark like water around a rock.',
    "You don't study the technique. You have a conversation in it.",
    'Look. Understand. Answer. Draw.', '<span class="key">Viam</span> under every step.',
    'Viam camera component.', 'Claude Opus 5.', 'Viam motion service.',
    'viam-server owns the arm', 'app.viam.com',
    '<span class="key">One person.</span> Two days. Claude and Viam.',
    'Nicholas Fjellberg Swerdlowe', 'Draw one mark. Duet answers.',
  ];
  for (const line of copy) assert.ok(h.includes(line), `copy missing: ${line}`);
  assert.ok(!/[‘’]/.test(h), 'use plain apostrophes so quotes are searchable');
});

test('every local file the deck references exists, and the four support files are linked', () => {
  const h = read('index.html');
  const refs = [...h.matchAll(/(?:src|href)="([^"#:]+)"/g)].map((m) => m[1]);
  assert.ok(refs.length >= 8, 'expected local references');
  for (const r of refs) assert.ok(existsSync(DIR + r), `referenced but missing: ${r}`);
  for (const f of ['fredoka.css', 'deck.css', 'deck.js', 'dev.js']) assert.ok(refs.includes(f), `${f} not linked`);
  assert.ok(refs.includes('img/turn-01-human.jpg') && refs.includes('img/turn-01-robot.jpg'), 'card 3 photos');
  assert.ok(!/type="module"/.test(h), 'module scripts do not load over file:// in Chrome');
});

test('developer mode is wired: badge, label, toast, and unique data-el names on the cards', () => {
  const h = read('index.html');
  for (const s of ['class="dev-badge"', 'id="devLabel"', 'id="devToast"']) assert.ok(h.includes(s), s);
  const names = [...h.matchAll(/data-el="([^"]+)"/g)].map((m) => m[1]);
  assert.ok(names.length >= 30, `only ${names.length} data-el names`);
  assert.equal(new Set(names).size, names.length, 'data-el names must be unique');
  for (let n = 1; n <= 7; n++) assert.ok(names.some((x) => x.startsWith(`card ${n} `)), `card ${n} has no data-el`);
  const dev = read('dev.js');
  assert.match(dev, /keydown/);
  assert.match(dev, /classList\.toggle\('dev'\)/);
});
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd <repo>/code/hackathon && node --test pagetests/pitch.test.mjs
```

Expected: 9 pass, 3 fail with `ENOENT ... index.html`.

- [ ] **Step 3: Write dev.js**

Create `docs/duet/pitch/dev.js`, the rule's snippet as a file:

```js
/* Developer mode (press D): hover shows an element's data-el name, click copies it.
   From ~/.claude/rules/common/preview-dev-mode.md. */
(function(){
  var label=document.getElementById('devLabel'),toast=document.getElementById('devToast'),tT=null;
  function isDev(){return document.body.classList.contains('dev');}
  function copy(t){if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t)['catch'](fb);}else fb();
    function fb(){var a=document.createElement('textarea');a.value=t;a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);a.select();try{document.execCommand('copy');}catch(e){}document.body.removeChild(a);}}
  function toastMsg(m){toast.textContent=m;toast.classList.add('show');if(tT)clearTimeout(tT);tT=setTimeout(function(){toast.classList.remove('show');},1400);}
  document.addEventListener('keydown',function(e){var t=e.target;if(t&&t.matches&&t.matches('input,textarea,[contenteditable]'))return;
    if(e.key==='d'||e.key==='D'){document.body.classList.toggle('dev');if(!isDev())label.style.display='none';}});
  document.addEventListener('mousemove',function(e){if(!isDev()){label.style.display='none';return;}
    var el=e.target.closest?e.target.closest('[data-el]'):null;
    if(el){label.textContent=el.getAttribute('data-el');label.style.display='block';
      label.style.left=Math.min(e.clientX+12,window.innerWidth-label.offsetWidth-8)+'px';label.style.top=(e.clientY+14)+'px';}
    else label.style.display='none';});
  document.addEventListener('click',function(e){if(!isDev())return;
    var el=e.target.closest?e.target.closest('[data-el]'):null;if(!el)return;
    e.preventDefault();e.stopPropagation();var n=el.getAttribute('data-el');copy(n);toastMsg('Copied: '+n);},true);
})();
```

- [ ] **Step 4: Write index.html**

Create `docs/duet/pitch/index.html`. Apostrophes are plain ASCII on purpose (the test checks). The `<svg class="defs">` holds five squiggle motifs, the two patterns built from them, and the three artist symbols used on cards 2 and 5.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Duet, a robot arm that draws with you</title>
<link rel="stylesheet" href="fredoka.css">
<link rel="stylesheet" href="deck.css">
</head>
<body>

<svg class="defs" aria-hidden="true" focusable="false">
  <defs>
    <!-- Haring-style motifs on a 160 x 160 tile; the wave and zigzag meet their own ends at the tile edge -->
    <path id="m-wave" d="M0 24 q10 -14 20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0"/>
    <path id="m-zig" d="M0 140 l10 -14 l10 14 l10 -14 l10 14 l10 -14 l10 14 l10 -14 l10 14 l10 -14 l10 14 l10 -14 l10 14 l10 -14 l10 14 l10 -14 l10 14"/>
    <path id="m-ticks" d="M96 56 l-10 -10 M110 50 l0 -14 M124 56 l10 -10 M90 70 l-14 0 M130 70 l14 0"/>
    <path id="m-dots" d="M30 70 l.01 0 M50 100 l.01 0" stroke-width="10"/>
    <path id="m-arcs" d="M14 56 a18 18 0 0 1 36 0 M60 116 a14 14 0 0 0 28 0"/>
    <pattern id="squiggle" width="160" height="160" patternUnits="userSpaceOnUse">
      <g fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
        <use href="#m-wave"/><use href="#m-zig"/><use href="#m-ticks"/><use href="#m-dots"/><use href="#m-arcs"/>
      </g>
    </pattern>
    <pattern id="squiggle-bright" width="160" height="160" patternUnits="userSpaceOnUse">
      <g fill="none" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
        <use href="#m-wave" stroke="#ffd400"/><use href="#m-zig" stroke="#e5322d"/><use href="#m-ticks" stroke="#1f4fd6"/>
        <use href="#m-dots" stroke="#17a34a"/><use href="#m-arcs" stroke="#ff7a00"/>
      </g>
    </pattern>
    <!-- artist stroke grammars, as chips -->
    <symbol id="s-vangogh" viewBox="0 0 100 60">
      <g fill="none" stroke="#1f4fd6" stroke-width="4" stroke-linecap="round">
        <path d="M6 40 q7 -9 14 -3"/><path d="M24 32 q7 -9 14 -3"/><path d="M42 24 q7 -9 14 -3"/><path d="M60 18 q9 -4 13 5"/>
        <path d="M76 30 q3 9 -4 13"/><path d="M66 46 q-9 3 -12 -4"/><path d="M54 36 q-3 -7 4 -11"/>
        <path d="M8 54 q7 -9 14 -3"/><path d="M28 50 q7 -9 14 -3"/><path d="M80 52 q7 -9 14 -3"/><path d="M84 10 q7 -9 14 -3"/>
      </g>
    </symbol>
    <symbol id="s-mondrian" viewBox="0 0 100 60">
      <g fill="none" stroke="#1f4fd6" stroke-width="4" stroke-linecap="square"><path d="M30 0 V60 M70 0 V60 M0 20 H100 M0 42 H100"/></g>
      <g fill="none" stroke="#e5322d" stroke-width="3" stroke-linecap="round"><path d="M32 40 L52 22 M42 40 L62 22 M52 40 L68 26 M32 30 L40 22"/></g>
    </symbol>
    <symbol id="s-haring" viewBox="0 0 100 60">
      <g fill="none" stroke="#17a34a" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M32 20 q10 -14 26 -6 q14 8 10 22 q-6 14 -22 14 q-16 -2 -18 -14 q-2 -10 4 -16 z"/>
        <path d="M24 12 l-8 -6 M46 6 l-1 -6 M68 14 l8 -6 M76 36 l9 2 M22 44 l-8 6 M50 54 l2 6"/>
      </g>
    </symbol>
  </defs>
</svg>

<div class="stage" data-el="stage">

  <section class="card plate-yellow" data-card="1" data-el="card 1 — thesis">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <div class="content thesis">
      <p class="line" data-el="card 1 line 1">Anyone can now study with the greatest minds in history.</p>
      <p class="line" data-el="card 1 line 2">Nobody could make art with them.</p>
      <p class="line" data-el="card 1 line 3">Until <span class="key">today</span>.</p>
    </div>
  </section>

  <section class="card plate-red" data-card="2" data-el="card 2 — what Duet is">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <div class="content what">
      <h1 class="wordmark" data-el="card 2 wordmark">Duet</h1>
      <p class="sub" data-el="card 2 subtitle">A robot arm that draws <span class="key">with</span> you.</p>
      <ul class="beats">
        <li data-el="card 2 beat 1">You make a mark.</li>
        <li data-el="card 2 beat 2">It looks, understands, and answers.</li>
        <li data-el="card 2 beat 3">In the hand of an artist you choose.</li>
      </ul>
      <div class="chips">
        <figure class="paper chip" data-el="card 2 chip — Van Gogh"><svg class="sample" viewBox="0 0 100 60"><use href="#s-vangogh" width="100" height="60"/></svg><figcaption>Van Gogh</figcaption></figure>
        <figure class="paper chip" data-el="card 2 chip — Mondrian"><svg class="sample" viewBox="0 0 100 60"><use href="#s-mondrian" width="100" height="60"/></svg><figcaption>Mondrian</figcaption></figure>
        <figure class="paper chip" data-el="card 2 chip — Keith Haring"><svg class="sample" viewBox="0 0 100 60"><use href="#s-haring" width="100" height="60"/></svg><figcaption>Keith Haring</figcaption></figure>
      </div>
    </div>
  </section>

  <section class="card plate-blue" data-card="3" data-el="card 3 — one turn">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <div class="content turn">
      <figure class="paper photo" data-el="card 3 photo — your mark">
        <img src="img/turn-01-human.jpg" alt="The visitor's red mark on the board">
        <figcaption>Your mark</figcaption>
      </figure>
      <div class="bubble" data-el="card 3 speech bubble">
        <p class="sees" data-el="card 3 speech bubble — sees">A big bold amoeba-like creature with loops and eye-holes sprawls across the board.</p>
        <p class="adds" data-el="card 3 speech bubble — adds">I'll add a small green spiral accent inside the lower loop body to give the creature a pulsing core.</p>
        <span class="badge" data-el="card 3 badge — latency">8 s to look and decide</span>
      </div>
      <figure class="paper photo" data-el="card 3 photo — the answer">
        <img src="img/turn-01-robot.jpg" alt="The board after the robot's green spiral">
        <figcaption>Duet answers</figcaption>
      </figure>
    </div>
  </section>

  <section class="card plate-green" data-card="4" data-el="card 4 — co-creation">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <div class="content cocreate">
      <div class="words">
        <h2 data-el="card 4 headline">Everyone leaves with a one-of-a-kind piece, made with a <span class="key">partner</span>.</h2>
        <p class="under" data-el="card 4 line">Six exchanges. Two artists. One of them was a robot.</p>
      </div>
      <div class="flipwrap">
        <figure class="paper photo flip" data-el="card 4 flipbook image"><img id="flip" src="img/turn-00-start.jpg" alt="The board, turn by turn"></figure>
        <span class="chip-label" id="flipLabel" data-el="card 4 flipbook counter">start</span>
      </div>
    </div>
  </section>

  <section class="card plate-orange" data-card="5" data-el="card 5 — learning">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <div class="content learn">
      <h2 data-el="card 5 headline">And you learn their language by <span class="key">answering back</span>.</h2>
      <ul class="lessons">
        <li data-el="card 5 lesson — Haring">
          <figure class="paper chip"><svg class="sample" viewBox="0 0 100 60"><use href="#s-haring" width="100" height="60"/></svg><figcaption>Haring</figcaption></figure>
          <p>One continuous outline, then motion ticks. Your blob becomes a figure.</p>
        </li>
        <li data-el="card 5 lesson — Mondrian">
          <figure class="paper chip"><svg class="sample" viewBox="0 0 100 60"><use href="#s-mondrian" width="100" height="60"/></svg><figcaption>Mondrian</figcaption></figure>
          <p>Your mark's edges run out to a grid. You start seeing the rectangle in everything.</p>
        </li>
        <li data-el="card 5 lesson — Van Gogh">
          <figure class="paper chip"><svg class="sample" viewBox="0 0 100 60"><use href="#s-vangogh" width="100" height="60"/></svg><figcaption>Van Gogh</figcaption></figure>
          <p>Dashes stream around your mark like water around a rock.</p>
        </li>
      </ul>
      <p class="footer" data-el="card 5 footer">You don't study the technique. You have a conversation in it.</p>
    </div>
  </section>

  <section class="card plate-cream" data-card="6" data-el="card 6 — how it works">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <div class="content how">
      <h2 data-el="card 6 title">Look. Understand. Answer. Draw.</h2>
      <p class="sub" data-el="card 6 subtitle"><span class="key">Viam</span> under every step.</p>
      <ol class="nodes">
        <li class="paper node" data-el="card 6 node — Look"><h3>Look</h3><p>Viam camera component. RealSense colour and depth, aligned, from the wrist. The board is found again every turn.</p></li>
        <li class="arrow" aria-hidden="true">&rarr;</li>
        <li class="paper node" data-el="card 6 node — Understand"><h3>Understand</h3><p>Claude Opus 5. One photo in, two sentences and strokes out.</p></li>
        <li class="arrow" aria-hidden="true">&rarr;</li>
        <li class="paper node" data-el="card 6 node — Answer"><h3>Answer</h3><p>The artist's grammar styles the strokes. The planner clips and budgets them, in board millimetres mapped into Viam's world frame.</p></li>
        <li class="arrow" aria-hidden="true">&rarr;</li>
        <li class="paper node" data-el="card 6 node — Draw"><h3>Draw</h3><p>Viam motion service. Every move planned around the table and wall obstacles, linear constraints on pen-down, arm and gripper components over the Python SDK.</p></li>
      </ol>
      <ul class="numbers">
        <li class="paper num" data-el="card 6 number — 8 s"><b>8 s</b><span>to look and decide</span></li>
        <li class="paper num" data-el="card 6 number — 2 mm"><b>2 mm</b><span>calibration</span></li>
        <li class="paper num" data-el="card 6 number — tests"><b>120</b><span>tests</span></li>
        <li class="paper num" data-el="card 6 number — direct moves"><b>0</b><span>direct arm moves</span></li>
      </ul>
      <p class="strip" data-el="card 6 Viam strip">viam-server owns the arm's control box &middot; machine configured in app.viam.com &middot; Python SDK from a laptop &middot; motion service with obstacles &middot; camera, arm, gripper components</p>
    </div>
  </section>

  <section class="card plate-black" data-card="7" data-el="card 7 — the build">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle-bright)"/></svg>
    <div class="content build">
      <h2 data-el="card 7 headline"><span class="key">One person.</span> Two days. Claude and Viam.</h2>
      <p class="credit" data-el="card 7 credit">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; September 2026</p>
      <p class="cta" data-el="card 7 footer — rig instruction">Draw one mark. Duet answers.</p>
    </div>
  </section>

  <div class="counter" id="counter" data-el="slide counter">1 / 7</div>
</div>

<div class="dev-badge">DEV MODE &middot; click an element to copy its name &middot; press D to exit</div>
<div class="dev-label" id="devLabel"></div>
<div class="dev-toast" id="devToast"></div>

<script src="deck.js"></script>
<script src="dev.js"></script>
</body>
</html>
```

- [ ] **Step 5: Run the whole page suite to verify everything passes**

```bash
cd <repo>/code/hackathon && node --test 'pagetests/*.test.mjs' 2>&1 | tail -8
```

Expected: the deck's 12 tests pass and the existing page tests still pass (`fail 0`).

- [ ] **Step 6: Commit**

```bash
cd <repo> && git add docs/duet/pitch/index.html docs/duet/pitch/dev.js code/hackathon/pagetests/pitch.test.mjs && git commit -m "feat(pitch): the seven cards, artist chips, speech bubble, flipbook, developer mode"
```

---

### Task 5: Browser pass, screenshots, offline check

No new files. This task looks at the deck, fixes what reads wrong, and leaves one screenshot per card for Nicholas.

- [ ] **Step 1: Open the deck over file:// in the built-in browser**

Navigate the built-in browser (`mcp__Claude_Browser__navigate`) to:

```
file://<repo>/docs/duet/pitch/index.html#1
```

If the built-in browser refuses `file://`, serve the folder instead and open `http://localhost:8010/#1`:

```bash
cd <repo>/docs/duet/pitch && python3 -m http.server 8010
```

Expected: the yellow plate with the squiggle pattern, no text yet, counter `1 / 7`, no console errors (`mcp__Claude_Browser__read_console_messages` with `onlyErrors: true` returns nothing).

- [ ] **Step 2: Step through every card with the keyboard and screenshot each**

Press Right arrow three times and confirm the three thesis lines appear one at a time with "today" in white with a black keyline. Then for each card, press Right and take a screenshot. Save them (via the Playwright tools' `browser_take_screenshot` with a `filename`, or by copying the built-in browser's captures) as:

```
code/hackathon/captures/pitch-1.png ... code/hackathon/captures/pitch-7.png
```

Check per card, against the spec's section 2 and 3:
- Card 1: the three lines build; Left arrow hides the last one; Right from card 2's start returns you to card 1 fully revealed via Left.
- Card 2: wordmark, subtitle with "with" keylined, three beats on one row, three chips with the dashes, grid, and outline visible.
- Card 3: two portrait photos on paper cards, the bubble between them with the tail toward "Duet answers", the "adds" sentence in the robot green, the badge.
- Card 4: the flipbook cycles through 13 photos with the label changing (`start`, `turn 1 of 6 · you`, ...), holds about 2 s on the finished piece, loops.
- Card 5: three lessons each with a chip, footer line.
- Card 6: four nodes with arrows on one row, four numbers, the black strip, all text legible on cream.
- Card 7: black plate, multicolour squiggles, white type, yellow "One person." and yellow "Draw one mark. Duet answers." at the bottom.
- The counter reads `N / 7` and the URL hash is `#N` on every card.

If the pattern competes with the type on any plate, lower `.pattern` opacity in `deck.css` (never shrink the type); if a card overflows at a 1280 × 720 window, reduce that card's font sizes in `deck.css` by one step and re-check.

- [ ] **Step 3: Check the other controls**

- Press `5` then `Home` then `End`: cards 5, 1 (unrevealed), 7.
- Click the right two thirds of the stage: advance. Click the left third: back.
- Press `F`: the stage fills the screen; `F` again returns.
- Press `D`: the badge appears; hovering the bubble shows `card 3 speech bubble`; clicking it shows `Copied: card 3 speech bubble` and does not advance the deck; `D` again exits.

- [ ] **Step 4: Offline check**

With the deck open over `file://`, list the network requests (`mcp__Claude_Browser__read_network_requests`). Expected: only `file://` URLs for the html, the two stylesheets, the two scripts, and `img/*.jpg`; nothing to `fonts.googleapis.com` or `fonts.gstatic.com`. In the Elements or computed styles the headline's rendered font is Fredoka, not Chalkboard SE.

- [ ] **Step 5: Commit any fixes and the screenshots**

```bash
cd <repo> && git add docs/duet/pitch code/hackathon/captures/pitch-*.png && git commit -m "feat(pitch): browser pass, sizes tuned, one screenshot per card"
```

If nothing changed in the deck, commit only the screenshots with the same message.

---

### Task 6: Final numbers, README, checklist line, spec amendment

**Files:**
- Modify: `docs/duet/pitch/index.html` (the test count, only if it differs)
- Create: `docs/duet/pitch/README.md`
- Modify: `notes/hackathon/05-morning-checklist.md` (append one line)
- Modify: `docs/superpowers/specs/2026-09-19-duet-pitch-deck-design.md` (section 5)

- [ ] **Step 1: Confirm the test count on card 6**

```bash
cd <repo>/code/hackathon && .venv/bin/python -m pytest -q 2>&1 | tail -1
```

Expected: a line like `120 passed, N warnings in 18s`. If the number of passed tests is not 120, change the `<b>120</b>` in the `card 6 number — tests` element of `docs/duet/pitch/index.html` to that number. The Node test does not pin the number, so no test changes.

- [ ] **Step 2: Write the README**

Create `docs/duet/pitch/README.md`:

```markdown
# Duet pitch deck

Seven cards, about two minutes, then the live demo. Spec: `docs/superpowers/specs/2026-09-19-duet-pitch-deck-design.md`.

Open it (offline is fine; the font is embedded):

    open docs/duet/pitch/index.html

Keys: Right, space, or a click on the right two thirds advances; Left or a click on the left third goes back;
1 to 7 jump; Home and End; F fullscreen; D developer mode (hover shows an element's name, click copies it).
Card 1 reveals three lines before it advances. Card 7 stays on screen during the demo.

Checks: `cd code/hackathon && node --test 'pagetests/*.test.mjs'`
```

- [ ] **Step 3: Add the checklist line**

Append to `notes/hackathon/05-morning-checklist.md`:

```markdown
- Pitch deck before demos: `open docs/duet/pitch/index.html`, press F, rehearse the seven cards once with the arm parked. Card 7 stays up while you draw.
```

- [ ] **Step 4: Amend section 5 of the spec**

In `docs/superpowers/specs/2026-09-19-duet-pitch-deck-design.md`, replace the file tree in section 5 with:

```
docs/duet/pitch/
  index.html        the seven cards, the SVG motifs and patterns, the artist symbols, the developer-mode elements
  deck.css          plates, pattern, type, paper, chips, bubble, flipbook, counter, developer-mode styles
  fredoka.css       @font-face with Fredoka (variable 400 to 700, latin) as a base64 data URI
  deck.js           window.Deck state functions, then DOM wiring guarded by typeof document
  dev.js            the D-key developer mode
  README.md         how to open it and the keys
  img/turn-00-start.jpg ... img/turn-06-robot.jpg   the 13 photos, copied unchanged (704 x 960)
```

and add this paragraph under it:

```
Amended 2026-09-19 while planning: Chrome, the default browser on the presenting Mac, blocks web fonts and module scripts loaded over file:// under its CORS rules. So the font is embedded as a data URI in its own stylesheet, the script is a classic script, and its pure state functions are exposed on window.Deck so Node can test them without a DOM. The photos are already 704 x 960 and are copied, not downscaled.
```

- [ ] **Step 5: Run the checks one last time**

```bash
cd <repo>/code/hackathon && node --test 'pagetests/*.test.mjs' 2>&1 | tail -4
```

Expected: `fail 0`.

- [ ] **Step 6: Commit**

```bash
cd <repo> && git add docs/duet/pitch/README.md docs/duet/pitch/index.html notes/hackathon/05-morning-checklist.md docs/superpowers/specs/2026-09-19-duet-pitch-deck-design.md && git commit -m "docs(pitch): README, checklist line, spec section 5 amended for file:// in Chrome"
```

---

## Self-review

**Spec coverage.** Section 1 decisions: deck first (card 7 stays up, Task 4 and README), the "with" framing (card 2 copy), thesis opening (card 1), co-creation headline and learning second (cards 4 and 5), one technical card with Viam in each step (card 6), the build as the close with the rig footer (card 7), one self-contained folder with no framework or CDN (Tasks 1 to 4), bright Haring plates (Task 3). Section 2 copy: every quoted line is in Task 4's markup and pinned by its test. Section 3 look: stage, plates and tokens, pattern with opacities and drift and reduced motion, keylined key word, paper outlines, chips as SVG, flipbook preload, limited motion, all in Task 3 and 4. Section 4 controls: every row of the table is in `deck.js` (Task 2), the hash and counter too, developer mode in Task 4, checked in Task 5. Section 5 files: amended in Task 6 for the file:// facts. Section 6 verification: Node test (Tasks 1 to 4), browser pass with screenshots, legibility, and offline check (Task 5), test count confirmed (Task 6). Section 7 out of scope: nothing under `code/hackathon/duet/` is touched. Section 8 git: small commits on `feat/duet-design`.

**Placeholders.** None; every code step carries the file's full content.

**Consistency.** `window.Deck` exposes `CARDS`, `BUILDS`, `FLIPBOOK`, `advance`, `back`, `jump`, `parseHash`, `flipLabel`, `flipDelay`, `nextFlip`, and the tests in Task 2 call exactly those. The markup uses `#flip`, `#flipLabel`, `#counter`, `.stage`, `.card[data-card]`, and `data-build`, which is what `deck.js` looks up and `deck.css` styles. The plate classes in the markup match the seven in `deck.css` and the Task 3 test. The `.cocreate .words` wrapper in the CSS matches the markup on card 4.

---

## Amendment, 2026-09-19 late morning: generated plates and heroes

Nicholas asked for images made with Nano Banana 2 through the Gemini API. The spec's sections 1, 3, 5 and 6 were amended. This adds Task 7 (the generator, run first because it takes a few minutes) and changes Tasks 3 and 4 as written below. The Node test gains one more check. The key is `GEMINI_API_KEY` in `code/hackathon/.env` (gitignored, already written); it is never put in a URL, a tracked file, or a command line.

### Task 7: gen_images.py, the generator (run before Task 3)

**Files:**
- Create: `docs/duet/pitch/gen_images.py`
- Modify: `code/hackathon/pagetests/pitch.test.mjs` (append)

- [ ] **Step 1: Write the failing test**

Append to `code/hackathon/pagetests/pitch.test.mjs`:

```js
const PLATES = [1, 2, 3, 4, 5, 6, 7].map((n) => `plate-${n}.jpg`);
const HEROES = ['hero-thesis.jpg', 'hero-duet.jpg', 'hero-build.jpg'];

test('the generator exists, keeps the key out of the repo, and never names the artist', () => {
  const py = read('gen_images.py');
  assert.match(py, /GEMINI_API_KEY/);
  assert.ok(!/AQ\.[A-Za-z0-9_-]{20,}/.test(py), 'no key literal in the script');
  assert.ok(!/Haring/.test(py), 'prompts describe the grammar, they do not name the artist');
  assert.match(py, /gemini-3\.1-flash-image/);
  for (const n of [...PLATES, ...HEROES]) assert.ok(py.includes(n.replace('.jpg', '')), `job ${n} missing`);
});

test('the seven plates and three heroes were generated', () => {
  for (const f of [...PLATES, ...HEROES]) assert.ok(existsSync(DIR + 'img/' + f), `missing img/${f}`);
});
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd <repo>/code/hackathon && node --test pagetests/pitch.test.mjs 2>&1 | grep -E "^# (pass|fail)"
```

Expected: the two new tests fail (`ENOENT ... gen_images.py`, then missing images).

- [ ] **Step 3: Write the generator**

Create `docs/duet/pitch/gen_images.py`:

```python
"""Generate the deck's plate textures and hero illustrations with Nano Banana 2.

Reads GEMINI_API_KEY from code/hackathon/.env (gitignored), sends it in a header, writes JPEGs
into img/ beside this file. Skips images that already exist unless --force is given.

    python3 docs/duet/pitch/gen_images.py                # everything missing
    python3 docs/duet/pitch/gen_images.py plate-3        # one image
    python3 docs/duet/pitch/gen_images.py --force hero-duet
"""
import base64
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"
ENV = HERE.parents[2] / "code" / "hackathon" / ".env"
MODEL = "gemini-3.1-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
JPEG_QUALITY = "88"

GRAMMAR = (
    "1980s New York subway-chalk street-art style: thick uniform black outlines, flat bright colours, "
    "no shading, no gradients, short radiating motion ticks around anything that moves, playful and bold. "
    "No text, no letters, no logos, no watermark."
)
PLATE = (
    "An all-over pattern of hand-drawn black marks on a pure white background, spread evenly edge to edge "
    "with no focal point and no empty areas: wavy squiggles, zigzags, short radiating tick clusters, dots, "
    "small open arcs{extra}. Thick round-capped marker strokes, all the same weight. Black on white only, "
    "no colour, no figures, no text."
)
PLATES = {
    "plate-1": PLATE.format(extra=", a few small spirals"),
    "plate-2": PLATE.format(extra=", a few tiny hearts drawn in one line"),
    "plate-3": PLATE.format(extra=", a few small stars drawn in one line"),
    "plate-4": PLATE.format(extra=", a few short dashed curves"),
    "plate-5": PLATE.format(extra=", a few small lightning bolts"),
    "plate-6": PLATE.format(extra=", a few small crosses"),
    "plate-7": (
        "An all-over pattern of hand-drawn marks on a pure black background, spread evenly edge to edge with "
        "no focal point: wavy squiggles, zigzags, short radiating tick clusters, dots and small open arcs, each "
        "mark in one of five flat colours: yellow #ffd400, red #e5322d, blue #1f4fd6, green #17a34a, orange "
        "#ff7a00. Thick round-capped marker strokes, all the same weight. No figures, no text."
    ),
}
HEROES = {
    "hero-thesis": (
        "One simple outlined figure standing, holding an open book in one hand and a fat marker in the other, "
        "radiating ticks around the head as if lit up by an idea. Yellow figure on a pure white background. " + GRAMMAR
    ),
    "hero-duet": (
        "A simple outlined person and a simple outlined six-jointed robot arm drawing together on the same small "
        "whiteboard lying flat on a table, each holding a marker, motion ticks around both hands, one continuous "
        "loopy line on the board joining their two marks. Red person, green robot arm, pure white background. " + GRAMMAR
    ),
    "hero-build": (
        "A simple outlined figure dancing with both arms up beside a simple outlined robot arm holding a marker, "
        "radiating ticks around both, a few confetti dots. Yellow figure, green arm, pure white background. " + GRAMMAR
    ),
}
JOBS = {**{k: (v, "16:9") for k, v in PLATES.items()}, **{k: (v, "1:1") for k, v in HEROES.items()}}


def api_key() -> str:
    for line in ENV.read_text().splitlines():
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit(f"GEMINI_API_KEY not found in {ENV}")


def generate(prompt: str, aspect: str, key: str) -> tuple[bytes, str]:
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect, "imageSize": "2K"},
        },
    }
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"{MODEL} HTTP {e.code}: {e.read().decode(errors='replace')[:600]}")
    for part in d.get("candidates", [{}])[0].get("content", {}).get("parts", []):
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"]), part["inlineData"]["mimeType"]
    sys.exit(f"no image in the response: {json.dumps(d)[:600]}")


def to_jpeg(src: Path, dst: Path) -> None:
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", JPEG_QUALITY, str(src), "--out", str(dst)],
        check=True, capture_output=True,
    )
    src.unlink()


def main(argv: list[str]) -> None:
    force = "--force" in argv
    names = [a for a in argv if not a.startswith("--")] or list(JOBS)
    unknown = [n for n in names if n not in JOBS]
    if unknown:
        sys.exit(f"unknown job(s): {unknown}; choose from {list(JOBS)}")
    key = api_key()
    IMG.mkdir(exist_ok=True)
    for name in names:
        prompt, aspect = JOBS[name]
        out = IMG / f"{name}.jpg"
        if out.exists() and not force:
            print(f"keep  {out.name}")
            continue
        data, mime = generate(prompt, aspect, key)
        tmp = IMG / f"{name}.{'png' if 'png' in mime else 'bin'}"
        tmp.write_bytes(data)
        to_jpeg(tmp, out)
        print(f"wrote {out.name} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1:])
```

- [ ] **Step 4: Generate everything (a few minutes; each call is about 10 to 20 seconds)**

```bash
cd <repo> && python3 docs/duet/pitch/gen_images.py
```

Expected: ten `wrote ...` lines. If a call fails with HTTP 400 mentioning `imageSize`, remove `"imageSize": "2K"` from `generate()` and run again. Look at each image (the Read tool shows them): a plate must be evenly covered with no big blank area, no figures and no letters; a hero must be one clear subject on white with no text. Re-roll a poor one with `--force <name>`; two re-rolls is the budget, after that the SVG fallback or no hero is the answer.

- [ ] **Step 5: Run the tests to verify they pass**

```bash
cd <repo>/code/hackathon && node --test pagetests/pitch.test.mjs 2>&1 | grep -E "^# (pass|fail)"
```

Expected: `fail 0` for the two generator tests (the rest depend on the tasks already done).

- [ ] **Step 6: Commit**

```bash
cd <repo> && git add docs/duet/pitch/gen_images.py docs/duet/pitch/img/plate-*.jpg docs/duet/pitch/img/hero-*.jpg code/hackathon/pagetests/pitch.test.mjs && git commit -m "feat(pitch): Nano Banana 2 plate textures and hero illustrations, generator kept in the repo"
```

### Changes to Task 3 (deck.css)

Add these rules to `deck.css` when writing it. The plate image multiplies over the CSS colour so the colour stays exact; the SVG pattern hides once the image has loaded.

```css
/* generated plate texture over the colour; the SVG pattern below it is the fallback */
.plate-img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; mix-blend-mode: multiply; opacity: .14;
             pointer-events: none; animation: breathe 30s ease-in-out infinite alternate; }
.plate-cream .plate-img { opacity: .10; }
.plate-black .plate-img { mix-blend-mode: normal; opacity: 1; }
.card.plated .pattern { display: none; }
@keyframes breathe { to { transform: scale(1.04); } }
@media (prefers-reduced-motion: reduce) { .plate-img { animation: none; } }

/* heroes on paper, right column of cards 1, 2 and 7 */
.hero { flex: none; padding: .8cqw; }
.hero img { display: block; width: 26cqw; height: 26cqw; object-fit: cover; border-radius: .8cqw; }
.words { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2cqw; }
```

and replace these three card rules:

```css
/* card 1, thesis: lines left, hero right */
.thesis { flex-direction: row; align-items: center; gap: 4cqw; }
.thesis .words { gap: 2.4cqw; }
.thesis .line { font-size: 4.8cqw; font-weight: 700; line-height: 1.15; opacity: 0; transform: translateY(1cqw);
                transition: opacity .4s ease, transform .4s ease; }
.card[data-build="1"] .line:nth-child(-n+1),
.card[data-build="2"] .line:nth-child(-n+2),
.card[data-build="3"] .line:nth-child(-n+3) { opacity: 1; transform: none; }

/* card 2, what Duet is: words left, hero right; beats stacked */
.what { flex-direction: row; align-items: center; gap: 4cqw; }
.what .words { gap: 1.4cqw; }
.wordmark { font-size: 10cqw; font-weight: 700; line-height: 1; }
.what .sub { font-size: 3.6cqw; font-weight: 600; }
.beats { display: flex; flex-direction: column; gap: .3cqw; font-size: 2.3cqw; font-weight: 600; }
.what .hero img { width: 30cqw; height: 30cqw; }

/* card 7, the build: words left, hero right */
.build { flex-direction: row; align-items: center; gap: 4cqw; }
.build h2 { font-size: 5.6cqw; font-weight: 700; line-height: 1.05; }
.credit { font-size: 2cqw; font-weight: 600; opacity: .85; }
.cta { margin-top: 3cqw; font-size: 4cqw; font-weight: 700; color: var(--yellow); }
```

Add `.plate-img` to the Task 3 test's expectations:

```js
  assert.ok(css.includes('.plate-img') && css.includes('.card.plated .pattern'), 'plate image layer with SVG fallback');
```

### Changes to Task 4 (index.html)

Directly after every card's `<svg class="pattern" ...>` line add the plate image, numbered by card (1 to 7):

```html
    <img class="plate-img" src="img/plate-1.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
```

Replace card 1's content with:

```html
    <div class="content thesis">
      <div class="words">
        <p class="line" data-el="card 1 line 1">Anyone can now study with the greatest minds in history.</p>
        <p class="line" data-el="card 1 line 2">Nobody could make art with them.</p>
        <p class="line" data-el="card 1 line 3">Until <span class="key">today</span>.</p>
      </div>
      <figure class="paper hero" data-el="card 1 hero — figure with a book and a marker"><img src="img/hero-thesis.jpg" alt=""></figure>
    </div>
```

Wrap card 2's wordmark, subtitle, beats and chips in `<div class="words"> ... </div>` and add after it:

```html
      <figure class="paper hero" data-el="card 2 hero — person and robot arm drawing together"><img src="img/hero-duet.jpg" alt=""></figure>
```

Wrap card 7's headline, credit and cta in `<div class="words"> ... </div>` and add after it:

```html
      <figure class="paper hero" data-el="card 7 hero — dancing figure beside the arm"><img src="img/hero-build.jpg" alt=""></figure>
```

Add to the Task 4 reference test:

```js
  for (let n = 1; n <= 7; n++) assert.ok(refs.includes(`img/plate-${n}.jpg`), `plate ${n} not referenced`);
  for (const h of ['hero-thesis', 'hero-duet', 'hero-build']) assert.ok(refs.includes(`img/${h}.jpg`), `${h} not referenced`);
```

The Task 5 browser pass adds: every plate shows its texture at the intended opacity with no SVG doubling once loaded; type stays legible over each plate (lower `.plate-img` opacity, never the type); the three heroes sit on paper cards without overflowing at 1280 × 720. Task 6's spec section 5 paragraph already lists the new files.
