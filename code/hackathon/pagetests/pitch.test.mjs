import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

// pagetests/ -> code/hackathon/ -> Viam/ -> docs/duet/pitch/
const DIR = fileURLToPath(new URL('../../../docs/duet/pitch/', import.meta.url));
const read = (name) => readFileSync(DIR + name, 'utf8');

const TURNS = 10;
const FLIPBOOK = ['turn-00-start.jpg',
  ...Array.from({ length: TURNS }, (_, i) => String(i + 1).padStart(2, '0'))
    .flatMap((nn) => [`turn-${nn}-human.jpg`, `turn-${nn}-robot.jpg`])];
const PLATES = [1, 2, 3, 4, 5, 6, 7].map((n) => `plate-${n}.jpg`);
const HEROES = ['hero-thesis.jpg', 'hero-duet.jpg', 'hero-build.jpg'];

test('the 21 flipbook photos and the final piece from session 20260919-151119 are in img/', () => {
  for (const f of [...FLIPBOOK, 'turn-10-final.jpg']) assert.ok(existsSync(DIR + 'img/' + f), `missing img/${f}`);
  assert.equal(readdirSync(DIR + 'img').filter((f) => /^turn-.*\.jpg$/.test(f)).length, 22);
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

test('the flipbook lists the 21 photos in turn order, labels them, and holds on the last', () => {
  const D = loadDeck();
  assert.deepEqual(D.FLIPBOOK, FLIPBOOK);
  assert.equal(D.flipLabel(0), 'start');
  assert.equal(D.flipLabel(1), 'turn 1 of 10 · you');
  assert.equal(D.flipLabel(2), 'turn 1 of 10 · Duet');
  assert.equal(D.flipLabel(19), 'turn 10 of 10 · you');
  assert.equal(D.flipLabel(20), 'turn 10 of 10 · Duet');
  assert.equal(D.flipDelay(0), 700);
  assert.equal(D.flipDelay(12), 700);
  assert.equal(D.flipDelay(20), 2000);
  assert.equal(D.nextFlip(3), 4);
  assert.equal(D.nextFlip(20), 0);
});

test('autoplay: cycle wraps to card 1, playDelay follows reveals, cards and speed', () => {
  const D = loadDeck();
  assert.deepEqual(D.SPEEDS, [0.5, 1, 1.5, 2]);
  assert.deepEqual(D.cycle({ card: 1, build: 0 }), { card: 1, build: 1 });
  assert.deepEqual(D.cycle({ card: 6, build: 0 }), { card: 7, build: 0 });
  assert.deepEqual(D.cycle({ card: 7, build: 0 }), { card: 1, build: 0 });
  assert.equal(D.playDelay({ card: 1, build: 0 }, 1), 2000);
  assert.equal(D.playDelay({ card: 1, build: 3 }, 1), 6000);
  assert.equal(D.playDelay({ card: 4, build: 0 }, 1), 12000);
  assert.equal(D.playDelay({ card: 2, build: 0 }, 2), 3000);
  assert.equal(D.playDelay({ card: 2, build: 0 }, 0.5), 12000);
});

test('the play button and speed dropdown sit inside the stage, and the pops follow --speed and --stagger', () => {
  const h = read('index.html');
  const stage = h.slice(h.indexOf('<div class="stage"'), h.indexOf('<div class="dev-badge"'));
  assert.ok(/<button id="play"[^>]*class="pill"/.test(stage), 'play button is a pill');
  assert.ok(/<select id="speed"/.test(stage), 'speed dropdown');
  for (const v of ['0.5', '1', '1.5', '2']) assert.ok(stage.includes(`<option value="${v}"`), `speed option ${v}`);
  const css = read('deck.css');
  assert.ok(css.includes('.playbar'), 'playbar styles');
  assert.ok(css.includes('.stage.playing { --stagger:'), 'play mode slows the stagger');
  assert.match(css, /animation-delay: calc\(var\(--i, 2\) \* var\(--stagger, 80ms\) \/ var\(--speed, 1\)\)/);
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
    'Anyone can now study with the greatest minds.',
    'Nobody could make art with them.',
    'Until <span class="key">today</span>.',
    'A robot arm that draws <span class="key">with</span> you.',
    'You make a mark. It answers back.',
    'A crowded world of creatures, flowers and dancing figures.',
    'A small green dancing figure in the open lower-right space to balance the crowd.',
    'about 8 seconds to look and decide', 'Claude says', 'Your mark', 'Duet answers',
    'Everyone leaves with a piece made with a <span class="key">partner</span>.',
    'Ten exchanges. Two artists. One of them was a robot.',
    'You learn their language by <span class="key">answering back</span>.',
    'Your blob becomes a figure.', 'Your edges run out to a grid.', 'Dashes stream around your mark.',
    'Your own artist', 'Describe a style. Duet draws in it.',
    'Look. Think. Answer. Draw.', '<span class="key">Viam</span> under every step.',
    'The camera takes a photo of the board.', 'Claude decides what to add.',
    "The artist's style becomes strokes.", 'The Viam motion service draws them.',
    '<span class="key">One person.</span> Two days. Claude and Viam.',
    'Nicholas Fjellberg Swerdlowe', 'Next: artists you <span class="key">train yourself</span>.',
  ];
  for (const line of copy) assert.ok(h.includes(line), `copy missing: ${line}`);
  assert.match(h, /<div class="paper bubble body"[^>]*>\s*<span class="caption says"/, 'card 3 names the speaker at the top of its bubble');
  assert.ok(!/[‘’]/.test(h), 'use plain apostrophes so quotes are searchable');
});

test('card 7 is the vision card: the rig line is gone, the next step and a way into the demo are on it', () => {
  const h = read('index.html');
  const card7 = h.split(/<section class="card /)[7].split('</section>')[0];
  assert.ok(!card7.includes('Draw one mark. Duet answers.'), 'the in-room rig instruction is gone');
  assert.ok(!card7.includes('class="cta'), 'no cta element');
  assert.match(card7, /<p class="vision body" data-el="card 7 next">Next: artists you <span class="key">train yourself<\/span>\.<\/p>/);
  assert.match(card7, /<a class="pill demo" href="\.\.\/demo\/" data-el="card 7 demo link — play the demo">/);
  const css = read('deck.css');
  assert.ok(!css.includes('.cta {'), 'the cta rule went with its element');
  assert.match(css, /\.vision \{ color: #fff; margin-top: var\(--s1\); \}/);
  assert.ok(!/(^|\n)\.next \{/.test(css), 'no bare .next rule: it would restyle card 5\'s pill next badge');
  assert.match(css, /\.pill\.demo \{[^}]*background: var\(--green\)/);
});

test('every local file the deck references exists, and the four support files are linked', () => {
  const h = read('index.html');
  const matches = [...h.matchAll(/(src|href)="([^"#:]+)"/g)];
  const refs = matches.map((m) => m[2]);
  assert.ok(refs.length >= 8, 'expected local references');
  for (const [, attr, r] of matches) {
    if (attr === 'href' && r.startsWith('../')) continue; // links that leave the folder are the showcase site's (../ home, ../demo/), resolved only when the deck is served from site/presentation/
    assert.ok(existsSync(DIR + r), `referenced but missing: ${r}`);
  }
  for (const f of ['fredoka.css', 'deck.css', 'deck.js', 'dev.js']) assert.ok(refs.includes(f), `${f} not linked`);
  assert.ok(refs.includes('img/turn-07-human.jpg') && refs.includes('img/turn-07-robot.jpg'), 'card 3 photos are the Haring turn of the latest run');
  assert.ok(refs.includes('img/turn-10-final.jpg'), 'card 7 shows the finished piece');
  for (let n = 1; n <= 7; n++) assert.ok(refs.includes(`img/plate-${n}.jpg`), `plate ${n} not referenced`);
  for (const hero of ['hero-thesis', 'hero-duet']) assert.ok(refs.includes(`img/${hero}.jpg`), `${hero} not referenced`);
  assert.ok(!/type="module"/.test(h), 'module scripts do not load over file:// in Chrome');
  assert.deepEqual([...h.matchAll(/href="(\.\.\/[^"]*)"/g)].map((m) => m[1]).sort(), ['../', '../demo/'], 'exactly two links leave the deck folder');
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
  assert.match(css, /--display: 8cqw; --headline: 5\.4cqw; --body: 3\.1cqw; --caption: 1\.9cqw;/, 'big-room type scale');
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
    assert.ok(/class="band foot">\s*<span class="strip"[^>]*>(<a [^>]*>)?Nicholas Fjellberg Swerdlowe/.test(s), `card ${i + 1} footer carries the name and hackathon line`);
    assert.ok(!s.includes('Viam Fine Motor Skills · 2026'), `card ${i + 1} old footer line gone`);
  });
  assert.ok(/class="name"[^>]*>\s*<svg class="logo/.test(sections[1]), 'card 2 large logo');
  const css = read('deck.css');
  assert.ok(css.includes('.wash {') && css.includes('.plate-black .wash'), 'wash rules');
  assert.ok(css.includes('.plate-black .logo'), 'logo turns white on black');
});

test('card 6 steps carry icons, card 5 has four modules, motion is defined', () => {
  const h = read('index.html');
  for (const id of ['i-look', 'i-think', 'i-answer', 'i-draw', 'i-own']) {
    assert.ok(h.includes(`<symbol id="${id}"`), `symbol ${id}`);
    assert.ok(h.includes(`href="#${id}"`), `${id} is used`);
  }
  const sections = h.split(/<section class="card /).slice(1);
  assert.equal((sections[4].match(/class="paper mod/g) || []).length, 4, 'card 5 has four modules');
  assert.ok(sections[4].includes('Your own artist') && sections[4].includes('>Coming next<'), 'fourth module is marked Coming next');
  assert.equal((sections[5].match(/class="viam caption"/g) || []).length, 0, 'card 6 Viam lines folded into the boxes for the big room');
  assert.ok(sections[5].includes('<span class="key">Viam</span> under every step.'), 'card 6 still credits Viam');
  assert.ok(!sections[4].includes('class="pill prompt"'), 'card 5 prompt pill dropped for the big room');
  assert.ok(!sections[5].includes('class="paper mod num"'), 'numbers row removed');
  const css = read('deck.css');
  assert.match(css, /@keyframes pop/);
  assert.match(css, /prefers-reduced-motion: reduce\)[^}]*\{[^}]*\.card\.active \* \{ animation: none !important; \}/);
});

test('notes: parseNotes reads ?notes=0 as hidden and everything else as shown', () => {
  const D = loadDeck();
  assert.equal(D.parseNotes(''), true);
  assert.equal(D.parseNotes('?speed=2'), true);
  assert.equal(D.parseNotes('?notes=0'), false);
  assert.equal(D.parseNotes('?notes=1'), true);
  assert.equal(D.parseNotes('?a=1&notes=0'), false);
});

test('notes: N and the Notes pill toggle them; the stage learns the setting from the URL at load', () => {
  const js = read('deck.js');
  assert.match(js, /case 'n':[\s\S]{0,40}setNotes\(!notes\);\s*return;/);
  assert.match(js, /notesBtn\.addEventListener\('click'/);
  assert.match(js, /stage\.classList\.toggle\('shownotes', on\)/);
  assert.match(js, /setNotes\(parseNotes\(location\.search\)\)/);
  const h = read('index.html');
  assert.match(h, /<button id="notes" class="pill" type="button" aria-pressed="true" data-el="playbar — notes button">Notes<\/button>/);
});

test('notes: a fourth card row holds a paper speech bubble, shown only with the stage shownotes class, and the photos make room', () => {
  const css = read('deck.css');
  assert.match(css, /\.card \{[^}]*grid-template-rows: auto minmax\(0, 1fr\) auto;/);
  assert.match(css, /\.notes \{ display: none;/);
  assert.match(css, /\.stage\.shownotes \.notes \{ display: flex; \}/);
  assert.match(css, /\.notes p \{[^}]*--caption: 1\.45cqw; font-size: var\(--caption\);/);
  assert.match(css, /\.notes p::before/);
  assert.match(css, /\.notes p::after/);
  assert.match(css, /\.plate-black \.notes p::before \{ border-top-color: #fff; \}/);
  assert.match(css, /\.stage\.shownotes \.photo img \{ height: 22cqw; \}/);
  assert.match(css, /\.stage\.shownotes \.flip img \{ height: 23cqw; \}/);
  assert.match(css, /\.stage\.shownotes \.build \.photo img \{ height: 20cqw; \}/);
  assert.match(css, /\.stage\.shownotes \.what \.hero img \{ width: 26cqw; height: 26cqw; \}/);
  assert.match(css, /\.triptych \.m2 \.bubble \{ --body: 2\.8cqw; \}/);
});

test('notes: every card carries the spoken part in its own aside, in the present tense of the day', () => {
  const h = read('index.html');
  const sections = h.split(/<section class="card /).slice(1);
  assert.equal(sections.length, 7);
  const frameLine = 'The two-minute pitch, as given at Viam\'s Fine Motor Skills hackathon, New York, September 19, 2026. Click the right side to advance, the left to go back.';
  const LINES = {
    1: [frameLine, 'Duet puts a partner at the table.'],
    2: ['in the hand of an artist you choose.'],
    3: ['A real turn from last night.'],
    4: ['Everyone who sits down leaves with a piece they made with a partner.'],
    5: ['You have a conversation in it.'],
    6: ['Viam\'s motion service draws them safely around the table.'],
    7: ['so it can sketch with my grandchildren the way he sketched with me.'],
  };
  sections.forEach((s, i) => {
    const n = i + 1;
    assert.equal((s.match(/<aside class="notes"/g) || []).length, 1, `card ${n} has one notes aside`);
    assert.ok(s.includes(`data-el="card ${n} notes — the spoken part"`), `card ${n} notes are named`);
    assert.match(s, /<\/div>\s*\n\s*<aside class="notes"/, `card ${n} notes sit directly after the content, before the footer`);
    const head = s.slice(0, s.indexOf('<aside class="notes"'));
    assert.equal((head.match(/<div\b/g) || []).length, (head.match(/<\/div>/g) || []).length, `card ${n} notes are a direct child of the card`);
    assert.ok(s.indexOf('<aside class="notes"') < s.indexOf('<footer class="band foot"'), `card ${n} notes sit above the footer`);
    for (const line of LINES[n]) assert.ok(s.includes(line), `card ${n} note missing: ${line}`);
  });
});
