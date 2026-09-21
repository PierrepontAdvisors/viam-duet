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
  assert.equal(D.renumber('\n  04 · X', 3), '03 · X');
  assert.equal(D.renumber('4 · X', 12), '12 · X');
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
  const frozen = Object.freeze({ card: 4, build: 2 });
  D.back(frozen, deck);
  assert.deepEqual(frozen, { card: 4, build: 2 });
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
  assert.ok(!/data-build(?!s)/.test(js), 'no data-build attribute: .shown is the single source of truth for reveals');
  assert.ok(js.indexOf('setup(parseCut') < js.indexOf("querySelectorAll('.card video')"), 'the cut runs before media is collected');
  assert.match(js, /!!flipCard && flipCard\.classList/);
  assert.match(js, /if \(p && p\.catch\)/);
  assert.match(js, /e\.metaKey \|\| e\.ctrlKey \|\| e\.altKey/);
  assert.match(js, /replaceState\(null, '', '#' \+ state\.card\)/);
  assert.ok(!/innerHTML/.test(js));
});
/* ---- the page ---- */
const sectionsOf = (h) => h.split(/<section class="card /).slice(1);
const specsFromHtml = (h) => [...h.matchAll(/<section class="card [^"]*" data-card="(\d+)"([^>]*)>/g)].map((m) => ({
  cut: (/data-cut="(\d+)"/.exec(m[2]) || [, ''])[1],
  builds: parseInt((/data-builds="(\d+)"/.exec(m[2]) || [, '0'])[1], 10),
}));

test('the page links the pitch\'s font, stylesheet and developer mode, then its own, as classic scripts', () => {
  const h = read('index.html');
  assert.match(h, /<title>A robot that draws back<\/title>/);
  for (const f of ['../pitch/fredoka.css', '../pitch/deck.css', 'class.css']) assert.ok(h.includes(`<link rel="stylesheet" href="${f}">`), `${f} linked`);
  assert.ok(h.includes('<script src="class.js"></script>') && h.includes('<script src="../pitch/dev.js"></script>'), 'scripts');
  assert.ok(!/type="module"/.test(h), 'module scripts do not load over file:// in Chrome');
  assert.ok(!h.includes('deck.js"'), 'the pitch\'s navigation is not loaded');
  for (const id of ['id="squiggle"', 'id="squiggle-bright"', 'id="logo"']) assert.ok(h.includes(id), `svg def ${id}`);
  assert.ok(!/[‘’]/.test(h), 'use plain apostrophes so quotes are searchable');
});

test('Act 1: the title, the hackathon, the other teams, the diner', () => {
  const h = read('index.html');
  const s = sectionsOf(h);
  assert.ok(s.length >= 4);
  const copy = [
    'A robot that draws <span class="key">back</span>.', 'Two days at a robot hackathon.',
    'Friday 9 am to Saturday 6 pm. Doors lock at night.', 'Teams of 2 or 3. A real robot arm each.', 'Demo at 3:30. Awards at 5.',
    'My dad was an architect. He always had a pen.',
    'At the diner, while we waited for the food, we\'d draw together.',
    'He\'d draw. I\'d draw on top. He\'d draw again. Until the food came.',
    'I didn\'t figure out that\'s where this came from until halfway through building it.',
  ];
  for (const line of copy) assert.ok(h.includes(line), `copy missing: ${line}`);
  assert.ok(s[0].includes('src="img/setup.jpg"'), 'card 1 hero is the arm photo');
  assert.ok(s[1].includes('src="img/door.jpg"') && s[1].includes('src="img/crowd.jpg"'), 'card 2 shows the door and the room');
  const videos = [...s[2].matchAll(/<video ([^>]*)>/g)].map((m) => m[1]);
  assert.equal(videos.length, 4, 'card 3 has four clips');
  videos.forEach((attrs, i) => {
    for (const a of ['muted', 'loop', 'playsinline', 'preload="auto"']) assert.ok(attrs.includes(a), `clip ${i + 1} ${a}`);
    assert.ok(!/\bautoplay\b/.test(attrs), `clip ${i + 1} has no autoplay: class.js plays it on its card`);
    assert.ok(attrs.includes(`src="video/team-${i + 1}.mp4"`), `clip ${i + 1} source`);
  });
  assert.ok(/class="card split lines plate-black"/.test('class="card ' + s[3].slice(0, 60)), 'card 4 is the black text card');
  assert.equal((s[3].match(/class="line reveal headline" data-step="(\d)"/g) || []).length, 4, 'card 4 reveals four lines');
  assert.ok(s[3].includes('data-builds="4"'), 'card 4 declares four reveals');
});

test('class.css: reveals, the half template, no stray font sizes, no redefinition of the pitch\'s tokens', () => {
  const css = read('class.css');
  assert.match(css, /\.reveal \{ opacity: 0;/);
  assert.match(css, /\.reveal\.shown \{ opacity: 1; transform: none; \}/);
  assert.match(css, /\.stage \.card\.active\.triptych \.module\.reveal \{ animation: none; \}/);
  assert.match(css, /\.split\.half \.words \{ grid-column: 1 \/ 7; \}/);
  assert.match(css, /\.split\.half\.photo-left \.figure \{ grid-column: 1 \/ 6; grid-row: 1; \}/);
  assert.ok(!/\.card\.active \.(modules|triptych|split)\b/.test(css), 'a card\'s template class compounds with .card.active; it is never a descendant');
  const sizes = [...css.matchAll(/font-size:\s*([^;}]+)/g)].map((m) => m[1].trim());
  for (const v of sizes) assert.match(v, /^var\(--(display|headline|body|caption)\)$/, `font-size "${v}" is not a token`);
  assert.ok(!/^:root \{[^}]*--(display|headline|body|caption):/m.test(css), 'the type scale stays in deck.css');
  assert.match(css, /\.oneturn \.cap \{[^}]*color: var\(--ink\)/);
  assert.match(css, /\.watch \.closing \{[^}]*color: var\(--ink\)/);
  assert.match(css, /\.clip \.cap \{[^}]*color: var\(--ink\)/);
});

test('Act 2: the setup with callouts, one turn with three verbs, the two code panels, the flipbook', () => {
  const h = read('index.html');
  const s = sectionsOf(h);
  assert.ok(s.length >= 8);
  const copy = [
    'You draw. It looks. It thinks. It draws back.',
    '1 · a camera on the wrist', '2 · a gripper holding a green marker', '3 · the board: red is a person, green is the robot', '4 · the laptop running the code',
    '>LOOK<', '>THINK<', '>DRAW<', 'the camera takes a photo', 'the arm follows the points',
    'A crowded world of creatures, flowers and dancing figures.',
    'A small green dancing figure in the open lower-right space to balance the crowd.',
    '8 seconds to look and decide', 'Claude says',
    'Your turtle and my robot follow the same thing: a list of points.', 'Your turtle', 'My robot (simplified)',
    'Play with it after: viam-duet.vercel.app',
  ];
  for (const line of copy) assert.ok(h.includes(line), `copy missing: ${line}`);
  // card 5: a photo-left half card, four dots on the photo and four list items, all reveals 1..4
  assert.ok(/^split half photo-left callouts /.test(s[4]), 'card 5 template');
  assert.ok(s[4].includes('data-builds="4"'));
  assert.deepEqual([...s[4].matchAll(/class="dot reveal" data-step="(\d)"/g)].map((m) => m[1]), ['1', '2', '3', '4']);
  assert.deepEqual([...s[4].matchAll(/class="paper body line reveal" data-step="(\d)"/g)].map((m) => m[1]), ['1', '2', '3', '4']);
  assert.ok(s[4].includes('src="img/setup.jpg"'));
  // card 6: the pitch's triptych, each module a reveal with its verb
  assert.ok(/^triptych oneturn /.test(s[5]), 'card 6 template');
  assert.ok(s[5].includes('data-builds="3"'));
  assert.deepEqual([...s[5].matchAll(/class="module m\d reveal" data-step="(\d)"/g)].map((m) => m[1]), ['1', '2', '3']);
  assert.ok(s[5].includes('src="../pitch/img/turn-07-human.jpg"') && s[5].includes('src="../pitch/img/turn-07-robot.jpg"'), 'card 6 uses the crowded-world turn');
  assert.match(s[5], /<div class="paper bubble body"[^>]*>\s*<span class="caption says"/, 'card 6 names the speaker at the top of its bubble');
  // card 7: two <pre> panels, verbatim
  const turtle = [
    'import turtle', 't = turtle.Turtle()', 'points = [(40, 0), (40, 40),', '          (0, 40), (0, 0)]',
    't.penup()', 't.goto(0, 0)', 't.pendown()', 'for x, y in points:', '    t.goto(x, y)', 't.penup()',
  ].join('\n');
  const robot = [
    'stroke = points_from_claude()', '# e.g. [(0, 0), (40, 0), (40, 40)]', 'x, y = stroke[0]',
    'pen_up()', 'move_to(x, y)', 'pen_down()', 'for x, y in stroke[1:]:', '    move_to(x, y)', 'pen_up()',
  ].join('\n');
  assert.ok(s[6].includes(`<pre>${turtle}</pre>`), 'turtle panel verbatim');
  assert.ok(s[6].includes(`<pre>${robot}</pre>`), 'robot panel verbatim');
  assert.equal((s[6].match(/<pre>/g) || []).length, 2);
  // card 8: the flipbook elements the wiring looks for
  assert.ok(s[7].includes('id="flip"') && s[7].includes('id="flipLabel"'), 'card 8 flipbook');
  assert.ok(s[7].includes('src="../pitch/img/turn-00-start.jpg"'), 'the flipbook starts on the blank board');
});
