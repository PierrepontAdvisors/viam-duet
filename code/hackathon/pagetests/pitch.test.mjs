import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

// pagetests/ -> code/hackathon/ -> Viam/ -> docs/duet/pitch/
const DIR = fileURLToPath(new URL('../../../docs/duet/pitch/', import.meta.url));
const read = (name) => readFileSync(DIR + name, 'utf8');

const FLIPBOOK = ['turn-00-start.jpg',
  ...[1, 2, 3, 4, 5, 6].flatMap((n) => [`turn-0${n}-human.jpg`, `turn-0${n}-robot.jpg`])];
const PLATES = [1, 2, 3, 4, 5, 6, 7].map((n) => `plate-${n}.jpg`);
const HEROES = ['hero-thesis.jpg', 'hero-duet.jpg', 'hero-build.jpg'];

test('the 13 flipbook photos from session 20260918-190258 are in img/', () => {
  for (const f of FLIPBOOK) assert.ok(existsSync(DIR + 'img/' + f), `missing img/${f}`);
  assert.equal(readdirSync(DIR + 'img').filter((f) => /^turn-.*\.jpg$/.test(f)).length, 13);
});

test('fredoka.css embeds the variable font as a data URI, so file:// in Chrome can use it', () => {
  const css = read('fredoka.css');
  assert.match(css, /font-family:\s*["']Fredoka["']/);
  assert.match(css, /font-weight:\s*400 700/);
  assert.match(css, /url\(data:font\/woff2;base64,[A-Za-z0-9+/=]{1000,}\)\s*format\(["']woff2["']\)/);
});

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

// deck.js is a classic script for file://; Node runs it here with a bare `window` and no
// `document`, which also proves the DOM wiring is guarded. It runs in this realm (not a vm
// context) so deepEqual can compare the objects it returns.
function loadDeck() {
  const window = {};
  new Function('window', read('deck.js'))(window);
  return window.Deck;
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
  assert.ok(css.includes('.plate-img') && css.includes('.card.plated .pattern'), 'plate image layer with SVG fallback');
});

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
    'The camera on the wrist photographs the board.', 'Viam · the camera component streams colour and depth from the wrist.',
    'Claude reads the drawing and decides what to add.', 'Viam · the frame reaches Claude through the Python SDK.',
    "The artist's style turns that idea into strokes.", "Viam · board millimetres map into the machine's world frame.",
    'The arm draws them, planned safely around the table.', 'Viam · the motion service plans every move around the table and wall.',
    'Your own artist', 'Bold comic-book lines with halftone dots', 'Describe a style in one sentence. Duet answers in it.',
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
  for (let n = 1; n <= 7; n++) assert.ok(refs.includes(`img/plate-${n}.jpg`), `plate ${n} not referenced`);
  for (const hero of ['hero-thesis', 'hero-duet', 'hero-build']) assert.ok(refs.includes(`img/${hero}.jpg`), `${hero} not referenced`);
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

test('every card carries the master page: frame, kicker, wordmark, footer with a counter', () => {
  const h = read('index.html');
  const kickers = ['01 · Thesis', '02 · What Duet is', '03 · One turn', '04 · Co-creation', '05 · Learning', '06 · How it works', '07 · The build'];
  const sections = h.split(/<section class="card /).slice(1);
  assert.equal(sections.length, 7);
  sections.forEach((s, i) => {
    assert.ok(s.includes('class="kicker"') && s.includes(kickers[i]), `card ${i + 1} kicker "${kickers[i]}"`);
    assert.equal((s.match(/class="wordmark"/g) || []).length, 1, `card ${i + 1} has one wordmark`);
    assert.ok(/class="band foot"/.test(s) && /class="counter"/.test(s), `card ${i + 1} footer with counter`);
    assert.ok(/class="frame"/.test(s), `card ${i + 1} frame`);
    assert.ok(/class="card (split|triptych|modules) /.test('class="card ' + s.slice(0, 40)), `card ${i + 1} uses a template class`);
  });
  assert.ok(!/id="counter"/.test(h), 'the stage-level counter is gone');
});

test('deck.css is built on the tokens: four type sizes, three templates, no stray font sizes', () => {
  const css = read('deck.css');
  for (const t of ['--display', '--headline', '--body', '--caption', '--s1', '--s4', '--paper-radius', '--paper-border', '--paper-pad', '--gutter', '--frame-inset']) {
    assert.ok(css.includes(t + ':'), `token ${t} is defined`);
  }
  for (const c of ['.split', '.triptych', '.modules', '.frame', '.kicker', '.wordmark', '.band']) assert.ok(css.includes(c), `rule ${c}`);
  const sizes = [...css.matchAll(/font-size:\s*([^;}]+)/g)].map((m) => m[1].trim());
  assert.ok(sizes.length >= 8, 'font sizes are set through the tokens');
  for (const v of sizes) assert.match(v, /^var\(--(display|headline|body|caption)\)$/, `font-size "${v}" is not a token`);
});

test('the toy logo replaces the Duet word in the header and on card 2, footers carry the name, every frame has a wash', () => {
  const h = read('index.html');
  const sym = h.slice(h.indexOf('<symbol id="logo"'), h.indexOf('</symbol>', h.indexOf('<symbol id="logo"')));
  assert.ok(sym.length > 0, 'symbol #logo exists');
  assert.equal((sym.match(/<rect /g) || []).length, 4, 'four blocks');
  for (const ch of ['>D<', '>U<', '>E<', '>T<']) assert.ok(sym.includes(ch), `block letter ${ch}`);
  assert.ok(sym.includes('currentColor'), 'ink parts use currentColor');
  const sections = h.split(/<section class="card /).slice(1);
  sections.forEach((s, i) => {
    assert.ok(/class="wordmark"[^>]*>\s*<svg class="logo/.test(s), `card ${i + 1} header logo`);
    assert.ok(s.includes('class="wash"'), `card ${i + 1} wash`);
    assert.ok(!s.includes('foot-logo'), `card ${i + 1} has no footer logo`);
    assert.ok(/class="band foot">\s*<span class="strip"[^>]*>Nicholas Fjellberg Swerdlowe/.test(s), `card ${i + 1} footer carries the name and hackathon line`);
    assert.ok(!s.includes('Viam Fine Motor Skills · 2026'), `card ${i + 1} old footer line gone`);
  });
  assert.ok(/class="name"[^>]*>\s*<svg class="logo/.test(sections[1]), 'card 2 large logo');
  const css = read('deck.css');
  assert.ok(css.includes('.wash {') && css.includes('.plate-black .wash'), 'wash rules');
  assert.ok(css.includes('.plate-black .logo'), 'logo turns white on black');
});

test('card 6 steps carry icons and Viam lines, card 5 has four modules, motion is defined', () => {
  const h = read('index.html');
  for (const id of ['i-look', 'i-think', 'i-answer', 'i-draw', 'i-own']) {
    assert.ok(h.includes(`<symbol id="${id}"`), `symbol ${id}`);
    assert.ok(h.includes(`href="#${id}"`), `${id} is used`);
  }
  const sections = h.split(/<section class="card /).slice(1);
  assert.equal((sections[4].match(/class="paper mod/g) || []).length, 4, 'card 5 has four modules');
  assert.ok(sections[4].includes('Your own artist') && sections[4].includes('>Next<'), 'fourth module is marked Next');
  assert.equal((sections[5].match(/class="viam caption"/g) || []).length, 4, 'card 6 has four Viam lines');
  assert.ok(!sections[5].includes('class="paper mod num"'), 'numbers row removed');
  const css = read('deck.css');
  assert.match(css, /@keyframes pop/);
  assert.match(css, /prefers-reduced-motion: reduce\)[^}]*\{[^}]*\.card\.active \* \{ animation: none !important; \}/);
});
