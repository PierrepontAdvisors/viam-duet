import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

// pagetests/ -> code/hackathon/ -> Viam/ -> docs/duet/class/
const DIR = fileURLToPath(new URL('../../../docs/duet/class/', import.meta.url));
const ROOT = fileURLToPath(new URL('../../../', import.meta.url));
const read = (name) => readFileSync(DIR + name, 'utf8');

const TURNS = 10;
const FLIPBOOK = ['turn-00-start.jpg',
  ...Array.from({ length: TURNS }, (_, i) => String(i + 1).padStart(2, '0'))
    .flatMap((nn) => [`turn-${nn}-human.jpg`, `turn-${nn}-robot.jpg`])];

// the fourteen cards as class.js reads them from the page: which are cut at ten minutes, and how many reveals each has
const SPECS = [
  { cut: '', builds: 0 }, { cut: '', builds: 0 }, { cut: '20', builds: 0 }, { cut: '', builds: 4 },
  { cut: '', builds: 4 }, { cut: '', builds: 3 }, { cut: '', builds: 0 }, { cut: '', builds: 0 },
  { cut: '20', builds: 0 }, { cut: '', builds: 0 }, { cut: '20', builds: 0 }, { cut: '20', builds: 0 },
  { cut: '', builds: 0 }, { cut: '', builds: 2 },
];

// class.js is a classic script for file://; Node runs it with a bare `window` and no `document`,
// which also proves the DOM wiring is guarded. Same realm, so deepEqual can compare its objects.
function loadDeck() {
  const window = {};
  new Function('window', read('class.js'))(window);
  return window.ClassDeck;
}

test('the full deck is fourteen cards with reveals on 4, 5, 6 and 14; the cut keeps ten and renumbers the reveals', () => {
  const D = loadDeck();
  assert.deepEqual(D.deckOf(D.keep(SPECS, 0)), { cards: 14, builds: { 4: 4, 5: 4, 6: 3, 14: 2 } });
  assert.deepEqual(D.deckOf(D.keep(SPECS, 10)), { cards: 10, builds: { 3: 4, 4: 4, 5: 3, 10: 2 } });
  assert.equal(D.keep(SPECS, 10).length, 10);
  assert.equal(D.parseCut(''), 0);
  assert.equal(D.parseCut('?cut=10'), 10);
  assert.equal(D.parseCut('?notes=1&cut=10'), 10);
  assert.equal(D.parseCut('?cut=20'), 0);
  assert.equal(D.parseCut(undefined), 0);
});

test('renumber rewrites the two-digit prefix of a kicker', () => {
  const D = loadDeck();
  assert.equal(D.renumber('04 · Why I built this', 3), '03 · Why I built this');
  assert.equal(D.renumber('14 · One piece of advice', 10), '10 · One piece of advice');
  assert.equal(D.renumber('01 · Duet', 1), '01 · Duet');
});

test('advance reveals card 4 one line at a time, then moves on', () => {
  const D = loadDeck();
  const deck = D.deckOf(D.keep(SPECS, 0));
  let s = { card: 4, build: 0 };
  s = D.advance(s, deck); assert.deepEqual(s, { card: 4, build: 1 });
  s = D.advance(s, deck); assert.deepEqual(s, { card: 4, build: 2 });
  s = D.advance(s, deck); assert.deepEqual(s, { card: 4, build: 3 });
  s = D.advance(s, deck); assert.deepEqual(s, { card: 4, build: 4 });
  s = D.advance(s, deck); assert.deepEqual(s, { card: 5, build: 0 });
  assert.deepEqual(D.advance({ card: 1, build: 0 }, deck), { card: 2, build: 0 });
});

test('advance stops on the last card of either deck and never mutates its input', () => {
  const D = loadDeck();
  const full = D.deckOf(D.keep(SPECS, 0));
  const cut = D.deckOf(D.keep(SPECS, 10));
  const last14 = Object.freeze({ card: 14, build: 2 });
  assert.equal(D.advance(last14, full), last14);
  const last10 = Object.freeze({ card: 10, build: 2 });
  assert.equal(D.advance(last10, cut), last10);
  assert.deepEqual(D.advance({ card: 10, build: 0 }, full), { card: 11, build: 0 });
  const first = Object.freeze({ card: 1, build: 0 });
  D.advance(first, full);
  assert.deepEqual(first, { card: 1, build: 0 });
});

test('back hides the latest reveal, and from the next card lands on the previous one fully revealed', () => {
  const D = loadDeck();
  const deck = D.deckOf(D.keep(SPECS, 0));
  assert.deepEqual(D.back({ card: 4, build: 2 }, deck), { card: 4, build: 1 });
  assert.deepEqual(D.back({ card: 5, build: 0 }, deck), { card: 4, build: 4 });
  assert.deepEqual(D.back({ card: 7, build: 0 }, deck), { card: 6, build: 3 });
  assert.deepEqual(D.back({ card: 9, build: 0 }, deck), { card: 8, build: 0 });
  const start = { card: 1, build: 0 };
  assert.equal(D.back(start, deck), start);
});

test('jump clamps to the deck and starts that card unrevealed; parseHash reads #n', () => {
  const D = loadDeck();
  const full = D.deckOf(D.keep(SPECS, 0));
  const cut = D.deckOf(D.keep(SPECS, 10));
  assert.deepEqual(D.jump(6, full), { card: 6, build: 0 });
  assert.deepEqual(D.jump(0, full), { card: 1, build: 0 });
  assert.deepEqual(D.jump(99, full), { card: 14, build: 0 });
  assert.deepEqual(D.jump(14, cut), { card: 10, build: 0 });
  assert.equal(D.parseHash('#3', full), 3);
  assert.equal(D.parseHash('#12', cut), 10);
  assert.equal(D.parseHash('', full), 1);
  assert.equal(D.parseHash('#nope', full), 1);
  assert.equal(D.parseHash(undefined, full), 1);
});

test('notes are off unless ?notes=1 (a screen-share must not show them)', () => {
  const D = loadDeck();
  assert.equal(D.parseNotes(''), false);
  assert.equal(D.parseNotes('?cut=10'), false);
  assert.equal(D.parseNotes('?notes=1'), true);
  assert.equal(D.parseNotes('?cut=10&notes=1'), true);
  assert.equal(D.parseNotes('?notes=0'), false);
});

test('the flipbook lists the 21 pitch photos in turn order, labels them, and holds on the last', () => {
  const D = loadDeck();
  assert.deepEqual(D.FLIPBOOK, FLIPBOOK);
  assert.equal(D.PITCH_IMG, '../pitch/img/');
  assert.equal(D.flipLabel(0), 'start');
  assert.equal(D.flipLabel(1), 'turn 1 of 10 · you');
  assert.equal(D.flipLabel(2), 'turn 1 of 10 · Duet');
  assert.equal(D.flipLabel(20), 'turn 10 of 10 · Duet');
  assert.equal(D.flipDelay(0), 700);
  assert.equal(D.flipDelay(20), 2000);
  assert.equal(D.nextFlip(3), 4);
  assert.equal(D.nextFlip(20), 0);
  for (const f of FLIPBOOK) assert.ok(existsSync(DIR + '../pitch/img/' + f), `pitch photo missing: ${f}`);
});

test('the wiring: cut prunes and renumbers cards, reveals follow data-step, media runs only on its card, keys 1-9 and 0', () => {
  const js = read('class.js');
  assert.match(js, /if \(typeof document === 'undefined'\) return;/);
  assert.match(js, /parseCut\(location\.search\)/);
  assert.match(js, /el\.parentNode\.removeChild\(el\)/);
  assert.match(js, /setAttribute\('data-card', String\(i \+ 1\)\)/);
  assert.match(js, /renumber\(k\.textContent, i \+ 1\)/);
  assert.match(js, /querySelectorAll\('\[data-step\]'\)/);
  assert.match(js, /classList\.toggle\('shown'/);
  assert.match(js, /v\.play\(\)/);
  assert.match(js, /v\.pause\(\)/);
  assert.match(js, /clearTimeout\(flipTimer\)/);
  assert.match(js, /case '0': set\(jump\(10, deck\)\); return;/);
  assert.match(js, /\/\^\[1-9\]\$\//);
  assert.match(js, /case 'f': case 'F': toggleFullscreen\(\); return;/);
  assert.match(js, /stage\.classList\.toggle\('shownotes', parseNotes\(location\.search\)\)/);
  assert.ok(!/case 'p':/.test(js) && !/case 'n':/.test(js), 'no autoplay or notes keys: the class deck is only ever talked through');
  assert.ok(!/id="play"|getElementById\('play'\)/.test(js), 'no play button');
});
