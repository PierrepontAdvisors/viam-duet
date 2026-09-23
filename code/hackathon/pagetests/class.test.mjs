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
  assert.ok(!/notes/i.test(js), 'no notes mode: the deck is only ever screen-shared');
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
    'Friday 9 am to Saturday 6 pm.', 'Teams of 2 or 3. A real arm each.', 'Demo at 3:30. Awards at 5.',
    'My dad was an architect. He always had a pen.',
    'At the diner, waiting for the food, we drew on the placemat.',
    'He\'d draw. I\'d draw on top. Until the food came.',
    'Halfway through building it, I saw where the idea came from.',
  ];
  for (const line of copy) assert.ok(h.includes(line), `copy missing: ${line}`);
  assert.ok(s[0].includes('src="img/setup.jpg"'), 'card 1 hero is the arm photo');
  assert.ok(s[1].includes('src="img/door.jpg"') && s[1].includes('src="img/crowd.jpg"'), 'card 2 shows the door and the room');
  const videos = [...s[2].matchAll(/<video ([^>]*)>/g)].map((m) => m[1]);
  assert.equal(videos.length, 4, 'card 3 has four clips');
  for (const [i, cap] of ['Stacking Jenga', 'Throwing a ball', 'Catching a ball', 'Fencing'].entries()) {
    assert.ok(s[2].includes(`data-el="card 3 caption — team ${i + 1}">${cap}</p>`), `clip ${i + 1} caption "${cap}"`);
  }
  videos.forEach((attrs, i) => {
    for (const a of ['muted', 'loop', 'playsinline', 'preload="auto"']) assert.ok(attrs.includes(a), `clip ${i + 1} ${a}`);
    assert.ok(!/\bautoplay\b/.test(attrs), `clip ${i + 1} has no autoplay: class.js plays it on its card`);
    assert.ok(attrs.includes(`src="video/team-${i + 1}.mp4"`), `clip ${i + 1} source`);
  });
  assert.ok(s[3].startsWith('modules story diner plate-black"'), 'card 4 is a black story card');
  assert.deepEqual([...s[3].matchAll(/class="panel paper reveal" data-step="(\d)"/g)].map((m) => m[1]), ['1', '2', '3', '4'], 'card 4 reveals four panels');
  for (let n = 1; n <= 4; n++) assert.ok(s[3].includes(`src="img/story-4-${n}.jpg"`), `card 4 panel ${n} picture`);
  assert.equal((s[3].match(/<figcaption class="cap body"/g) || []).length, 4, 'each panel carries its line as a caption');
  assert.ok(s[3].includes('data-builds="4"'), 'card 4 declares four reveals');
});

test('class.css: reveals, the half template, no stray font sizes, no redefinition of the pitch\'s tokens', () => {
  const css = read('class.css');
  assert.match(css, /\.reveal \{ opacity: 0;/);
  assert.match(css, /\.reveal\.shown \{ opacity: 1; transform: none; \}/);
  assert.match(css, /\.stage \.card\.active\.triptych \.module\.reveal \{ animation: none; \}/);
  assert.match(css, /\.split\.half \.words \{ grid-column: 1 \/ 7; \}/);
  assert.match(css, /\.split\.half\.photo-left \.figure \{ grid-column: 1 \/ 6; grid-row: 1; \}/);
  assert.match(css, /\.panels \{ display: grid; grid-template-columns: repeat\(12, minmax\(0, 1fr\)\); column-gap: var\(--gutter\); align-items: stretch; \}/, 'panel rows are the 12-column grid with one height per row');
  assert.match(css, /\.panels\.four > \* \{ grid-column: span 3; \}/);
  assert.ok(!/shownotes|\.notes\b/.test(css), 'no notes mode');
  assert.ok(!/--pad-y/.test(css), 'the master page keeps deck.css\'s --pad-y (4cqw) against its 3cqw frame inset, so the header and footer sit 1cqw INSIDE the frame; overriding it puts the bands on top of the frame line');
  assert.match(css, /\.panel img \{[^}]*max-height: 21cqw; object-fit: contain;/, 'a panel picture is capped and never squashed');
  assert.ok(!/(^|\n)\.strip\b/.test(css), 'the footer span is also .strip');
  assert.match(css, /\.panel \.cap \{[^}]*color: var\(--ink\)/);
  assert.ok(!/\.lines \.line|\.big \.display|\.advice \.words|\.logfields/.test(css), 'the text-only layouts are gone with their cards');
  assert.ok(!/\.card\.active \.(modules|triptych|split)\b/.test(css), 'a card\'s template class compounds with .card.active; it is never a descendant');
  const sizes = [...css.matchAll(/font-size:\s*([^;}]+)/g)].map((m) => m[1].trim());
  for (const v of sizes) assert.match(v, /^var\(--(display|headline|body|caption)\)$/, `font-size "${v}" is not a token`);
  assert.ok(!/^:root \{[^}]*--(display|headline|body|caption):/m.test(css), 'the type scale stays in deck.css');
  assert.match(css, /\.oneturn \.cap \{[^}]*color: var\(--ink\)/);
  assert.match(css, /\.watch \.closing \{[^}]*color: var\(--ink\)/);
  assert.match(css, /\.clip \.cap \{[^}]*color: var\(--ink\)/);
  assert.match(css, /\.errline \{[^}]*color: var\(--human\)/);
  assert.match(css, /\.takeaway \{[^}]*background: var\(--yellow\)/);
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
    'Tracy and my robot follow the same thing: a list of points.', 'Tracy (your turtle)', 'My robot (simplified)',
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
    'from turtle import *', 'points = [(40, 0), (40, 40),', '          (0, 40), (0, 0)]',
    'penup()', 'goto(0, 0)', 'pendown()', 'for x, y in points:', '    goto(x, y)', 'penup()',
  ].join('\n');
  const robot = [
    'stroke = points_from_claude()', '# Claude picks the shape; we just walk it', 'x, y = stroke[0]',
    'pen_up()', 'move_to(x, y)', 'pen_down()', 'for x, y in stroke[1:]:', '    move_to(x, y)', 'pen_up()',
  ].join('\n');
  assert.ok(s[6].includes(`<pre>${turtle}</pre>`), 'turtle panel verbatim');
  assert.ok(s[6].includes(`<pre>${robot}</pre>`), 'robot panel verbatim');
  assert.equal((s[6].match(/<pre>/g) || []).length, 2);
  // card 8: the flipbook elements the wiring looks for
  assert.ok(s[7].includes('id="flip"') && s[7].includes('id="flipLabel"'), 'card 8 flipbook');
  assert.ok(s[7].includes('src="../pitch/img/turn-00-start.jpg"'), 'the flipbook starts on the blank board');
});

test('Act 3: three failures, the log, what it felt like, the advice', () => {
  const h = read('index.html');
  const s = sectionsOf(h);
  assert.equal(s.length, 14);
  const copy = [
    'The robot crushed the pen.', 'Measure with the robot\'s hand, not yours.',
    'The smart trigger that wasn\'t.', 'Go, robot!', 'The simple thing is allowed to win.',
    'The error you\'ll get too.', 'SyntaxError: \'return\' outside function', 'The error message is the clue, not the insult.',
    'I wrote down every problem.', '>PLAN<', '>CODE<', '>TEST<', '>DEBUG<', '>REVISE<',
    '>What I saw<', '>What I tried<', '>What fixed it<', '>Why it worked<', 'This is what debugging actually is.',
    'One person.', 'Two days.', '<span class="key">Honorable mention.</span>',
    'You already know <span class="key">enough</span> to start.', 'Start with the smallest thing that works, then make it bigger.',
  ];
  for (const line of copy) assert.ok(h.includes(line), `copy missing: ${line}`);
  const excerpt = ['class Palletizer:', '    def obstacles(self):', '        boxes = self.placed_boxes()', '    return WorldState(boxes)'].join('\n');
  assert.ok(s[10].includes(`<pre>${excerpt}</pre>`), 'card 11 excerpt verbatim');
  assert.ok(s[12].includes('src="img/medal.jpg"'), 'card 13 shows the medal');
  assert.ok(s[13].includes('data-builds="2"'), 'card 14 reveals two lines');
  assert.deepEqual([...s[13].matchAll(/class="panel paper reveal" data-step="(\d)"/g)].map((m) => m[1]), ['1', '2']);
  for (const [card, pics] of [[8, ['story-9']], [9, ['story-10-1', 'story-10-2']], [10, ['story-11']], [11, ['story-12']], [13, ['story-14-1', 'story-14-2']]]) {
    for (const p of pics) assert.ok(s[card].includes(`src="img/${p}.jpg"`), `card ${card + 1} shows ${p}`);
  }
  assert.ok(s[10].includes('</pre><p class="errline body"'), 'card 11 keeps the error line inside the code panel');
  for (const [i, allowed] of [[8, 2], [10, 2], [11, 12]]) {   // cards 9, 11, 12: a headline and a takeaway under the pictures (12 adds the loop and the four log fields)
    const under = s[i].slice(s[i].indexOf('<div class="under">'), s[i].indexOf('</div>', s[i].indexOf('<div class="under">')));
    const blocks = (under.match(/<(h2|p|li)\b/g) || []).length;
    assert.ok(blocks <= allowed, `card ${i + 1} carries ${blocks} text blocks under its pictures (max ${allowed}): the pictures carry the card`);
  }
  assert.ok(!s[9].includes('<div class="under">') && (s[9].match(/<figcaption/g) || []).length === 2, 'card 10 is two captioned panels, nothing under them');
});

test('the page declares the cut and the reveals exactly as the tests model them, in order', () => {
  const h = read('index.html');
  assert.deepEqual(specsFromHtml(h), SPECS);
  const numbers = [...h.matchAll(/<section class="card [^"]*" data-card="(\d+)"/g)].map((m) => Number(m[1]));
  assert.deepEqual(numbers, Array.from({ length: 14 }, (_, i) => i + 1));
});

test('every card carries the master page: frame, wash, kicker, wordmark, footer with a counter, and no notes aside', () => {
  const h = read('index.html');
  const kickers = ['01 · Duet', '02 · What a hackathon is', '03 · What other teams built', '04 · Why I built this', '05 · What Duet is', '06 · One turn',
    '07 · It\'s just points', '08 · Watch it', '09 · What broke', '10 · What broke', '11 · What broke', '12 · The log', '13 · What it felt like', '14 · One piece of advice'];
  const s = sectionsOf(h);
  assert.equal(s.length, 14);
  s.forEach((c, i) => {
    const n = i + 1;
    assert.ok(c.includes('class="kicker"') && c.includes(`>${kickers[i]}<`), `card ${n} kicker "${kickers[i]}"`);
    assert.equal((c.match(/class="wordmark"/g) || []).length, 1, `card ${n} has one wordmark`);
    assert.ok(/class="wordmark"[^>]*>\s*<svg class="logo/.test(c), `card ${n} header logo`);
    assert.ok(/class="band foot"/.test(c) && c.includes(`<span class="counter">${n} / 14</span>`), `card ${n} footer counter`);
    assert.ok(c.includes('Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026'), `card ${n} footer strip`);
    assert.ok(/class="frame"/.test(c) && c.includes('class="wash"') && c.includes('class="pattern"') && c.includes('class="plate-img"'), `card ${n} plate layers`);
    assert.ok(/^(split|triptych|modules) /.test(c), `card ${n} uses a pitch template class`);
    assert.ok(!c.includes('<aside'), `card ${n} carries no notes aside: the words live in script.md`);
  });
  // plates cycle 1..7 with card 4 on black
  const plates = s.map((c) => /plate-(\d)\.jpg/.exec(c)[1]);
  assert.deepEqual(plates, ['1', '2', '3', '7', '5', '6', '7', '1', '2', '3', '4', '5', '6', '7']);
  assert.ok(/^modules story diner plate-black/.test(s[3]) && /^modules code plate-black/.test(s[6]) && /^modules story advice plate-black/.test(s[13]), 'cards 4, 7 and 14 are black');
});

test('developer mode is wired: badge, label, toast, and unique data-el names on every card', () => {
  const h = read('index.html');
  for (const x of ['class="dev-badge"', 'id="devLabel"', 'id="devToast"']) assert.ok(h.includes(x), x);
  const names = [...h.matchAll(/data-el="([^"]+)"/g)].map((m) => m[1]);
  assert.ok(names.length >= 90, `only ${names.length} data-el names`);
  assert.equal(new Set(names).size, names.length, 'data-el names must be unique');
  for (let n = 1; n <= 14; n++) assert.ok(names.some((x) => x.startsWith(`card ${n} `)), `card ${n} has no data-el`);
});

test('every local file the deck references exists, except the local-only assets, which are gitignored instead', () => {
  const h = read('index.html');
  const refs = [...h.matchAll(/(?:src|href)="([^"#:]+)"/g)].map((m) => m[1]);
  const localOnly = ['video/team-1.mp4', 'video/team-2.mp4', 'video/team-3.mp4', 'video/team-4.mp4', 'img/crowd.jpg', 'img/medal.jpg'];
  const ignore = readFileSync(ROOT + '.gitignore', 'utf8').split('\n');
  for (const r of new Set(refs)) {
    if (localOnly.includes(r)) {
      const rule = r.startsWith('video/') ? 'docs/duet/class/video/' : 'docs/duet/class/' + r;
      assert.ok(ignore.includes(rule), `${r} is local-only and must be gitignored as ${rule}`);
      continue;
    }
    assert.ok(existsSync(DIR + r), `referenced but missing: ${r}`);
  }
  for (const r of localOnly) assert.ok(refs.includes(r), `${r} is referenced`);
  assert.ok(refs.includes('img/setup.jpg') && refs.includes('img/door.jpg'), 'the two committed photos');
  assert.equal(refs.filter((r) => r.startsWith('../pitch/img/plate-')).length, 14, 'every card has a plate');
  assert.ok(ignore.includes('hackathon-videos/'), 'the source drop folder is gitignored');
});

test('the pitch deck is untouched by this work', () => {
  const pitch = fileURLToPath(new URL('../../../docs/duet/pitch/', import.meta.url));
  const js = readFileSync(pitch + 'deck.js', 'utf8');
  assert.match(js, /var CARDS = 7;/);
  assert.ok(!/ClassDeck/.test(js));
});

test('the story pictures: eleven panels in img/, each on its card, generated in the pitch grammar without naming an artist', () => {
  const pics = ['story-4-1', 'story-4-2', 'story-4-3', 'story-4-4', 'story-9', 'story-10-1', 'story-10-2', 'story-11', 'story-12', 'story-14-1', 'story-14-2'];
  const h = read('index.html');
  for (const p of pics) {
    assert.ok(existsSync(DIR + `img/${p}.jpg`), `missing img/${p}.jpg`);
    assert.equal((h.match(new RegExp(`src="img/${p}\\.jpg"`, 'g')) || []).length, 1, `${p} is on exactly one card`);
  }
  const py = read('gen_images.py');
  for (const p of pics) assert.ok(py.includes(`"${p}"`), `job ${p} in gen_images.py`);
  assert.ok(!/AQ\.[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{20,}/.test(py), 'no key literal');
  assert.ok(!/Haring|Mondrian|Van Gogh/.test(py), 'prompts describe the grammar, they do not name an artist');
  assert.match(py, /GEMINI_API_KEY/);
  assert.match(py, /pitch\.GRAMMAR|GRAMMAR = pitch\.GRAMMAR/);
});

test('talk.md is the run-of-show (pre-flight, the ten-minute list, likely questions) and points at the script', () => {
  const t = read('talk.md');
  for (const line of ['## Pre-flight', '?cut=10', 'https://viam-duet.vercel.app', 'Optimize for video clip', '## The 10-minute version', '## Likely questions', 'script.md']) assert.ok(t.includes(line), line);
  for (const line of ['Did you write all the code?', 'How did Claude and the robot communicate?',
    'Did you use an AI agent, APIs, or something else?', 'How do you manage your time and stay organized?',
    'What is different about working alone versus with a team?', 'How long have you been coding?']) {
    assert.ok(t.includes(line), `Q&A missing: ${line}`);
  }
  assert.equal((t.match(/^### \d+ · /gm) || []).length, 0, 'the per-slide words live in script.md, not here');
});

test('script.md: fourteen slides with times adding to 17:15, the cut marked, the truth beats, no jargon, short sentences', () => {
  const t = read('script.md');
  const heads = [...t.matchAll(/^## (\d+) · .* \((\d+):(\d\d)\)/gm)];
  assert.equal(heads.length, 14, 'one heading per slide with a time');
  assert.deepEqual(heads.map((m) => Number(m[1])), Array.from({ length: 14 }, (_, i) => i + 1));
  const total = heads.reduce((s, m) => s + Number(m[2]) * 60 + Number(m[3]), 0);
  assert.equal(total, 16 * 60 + 45, 'targets add to 16:45');
  for (const n of [3, 9, 11, 12]) assert.match(t, new RegExp(`^## ${n} · .*not in the ten-minute version`, 'm'), `slide ${n} is marked cut`);
  for (const line of ['an AI that can look at a photo and tell you what\'s in it', 'honorable mention', 'I didn\'t win', 'simplified',
    'You already know enough to start', 'Eight entries by Friday night', '[click]', 'product manager',
    'never been a professional programmer']) assert.ok(t.includes(line), `script missing: ${line}`);
  assert.ok(!/motion service|inverse kinematics|WebRTC|polyline|inference/i.test(t), 'no jargon');
  const spoken = t.split('\n').filter((l) => l && !l.startsWith('#') && !l.startsWith('*') && !l.startsWith('_') && !l.startsWith('---'));
  const words = spoken.join(' ').split(/\s+/).length;
  assert.ok(words < 1700, `spoken words ${words}: at a slow pace this must stay well inside twenty minutes`);
  const long = spoken.flatMap((l) => l.split(/(?<=[.!?])\s+/)).filter((sen) => sen.split(/\s+/).length > 30);
  assert.deepEqual(long, [], 'no sentence over thirty words');
});

test('README: how to open it, the keys, the cut, the assets, and what stays out of git', () => {
  const r = read('README.md');
  for (const line of ['open docs/duet/class/index.html', '?cut=10', 'build_assets.py', 'hackathon-videos/', 'crowd.jpg', 'medal.jpg', 'video/', 'node --test']) {
    assert.ok(r.includes(line), `README missing: ${line}`);
  }
});
