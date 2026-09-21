# Duet demo: hand draws, presses like a person, names, turn clock with pause: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** In the showcase demo's replay, the hand draws the visitor's recorded mark with a red marker, lifts and squashes the buttons it presses, rolls down the menu row by row, wears a "Visitor" pill while the robot's dot wears "Robot", and a turn clock chip counts each half of an exchange and pauses the whole piece on a click.

**Architecture:** The replay schedule's hand cue grows `draw` and `row`, and two clock cues join it. `hand.js` grows draw, hover, and press-on-release steps, a roll through the rows, and pause/resume; the visitor's trace reuses `GhostPen`, which gains `onMove`, `pause`, and `resume`. A new `clock.js` holds the chip's pure parts and its runner. `app.js` routes cues by key, places the Robot tag from the robot pen's `onMove`, and pauses or resumes the hand, both pens, and the clock from the `paused` state.

**Tech Stack:** Vanilla ES modules under `code/hackathon/duet/static/js/`, CSS in `duet.css` sized in `cqw`, Node's test runner (`node --test 'pagetests/*.test.mjs'` from `code/hackathon`), `site/build.py` to copy the page into `site/demo/`.

Spec: `docs/superpowers/specs/2026-09-20-duet-demo-hand-draws-design.md`. Parent: `2026-09-20-duet-demo-hand-design.md`, implemented by `docs/superpowers/plans/2026-09-20-duet-demo-hand.md`. Work in `.worktrees/showcase-site` on `feat/showcase-site`. Paths are relative to the repository root; run tests from `code/hackathon`.

---

## File structure

| File | Responsibility | Change |
| --- | --- | --- |
| `code/hackathon/duet/static/js/hand.js` | `traceMs`, `plan`, `planMs` (pure); `Hand` runner | rewritten: draw, hover, press-on-release, roll, pause/resume |
| `code/hackathon/duet/static/js/replay.js` | schedule and Player | `draw`, `row`, clock cues, `PACE.human` |
| `code/hackathon/duet/static/js/preview.js` | `GhostPen` | `onMove`, `pause`, `resume`, injectable frames |
| `code/hackathon/duet/static/js/clock.js` | **new**: `formatSeconds`, `fraction`, `Clock` | the turn clock |
| `code/hackathon/duet/static/index.html` | markup | marker, Visitor tag, Robot tag, clock chip, red pen layer; `?v=ds9` |
| `code/hackathon/duet/static/duet.css` | styles | hover/active twins, marker, tags, clock, red pen layer |
| `code/hackathon/duet/static/js/app.js` | boot and dispatch | pen, tag, clock, cue routing, pause routing, clock click; `?v=ds9` |
| every other `js/*.js` | imports | `?v=ds8` → `?v=ds9` |
| `code/hackathon/pagetests/hand.test.mjs` | rewritten | plan and runner with a manual scheduler |
| `code/hackathon/pagetests/replay.test.mjs` | updated | cue contents, clock cues |
| `code/hackathon/pagetests/preview.test.mjs` | **new** | `GhostPen` with stubbed frames |
| `code/hackathon/pagetests/clock.test.mjs` | **new** | `clock.js` |
| `code/hackathon/pagetests/style.test.mjs`, `defaults.test.mjs`, `diagnostics.test.mjs` | updated | markup, CSS, wiring, version |
| `site/demo/**` | generated | rebuilt |

Order matters: Task 1 (`hand.js`) comes first because `replay.js` imports `planMs` from it in Task 2.

---

### Task 1: `hand.js`: trace time, the new plan, and the runner with hover, press-on-release, draw, and pause

**Files:**
- Rewrite: `code/hackathon/duet/static/js/hand.js`
- Rewrite: `code/hackathon/pagetests/hand.test.mjs`

- [ ] **Step 1: Write the failing tests**

Replace `code/hackathon/pagetests/hand.test.mjs` with:

```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { plan, planMs, traceMs, Hand, HAND } from '../duet/static/js/hand.js';

/** A stand-in for an element: a class list, a style, a rect, a click log, and visibility as offsetParent. */
function fake(name, { hidden = false, rect = { left: 0, top: 0, width: 10, height: 10 } } = {}) {
  const classes = new Set(hidden ? ['hidden'] : []);
  return {
    name, style: {}, clicks: 0, rect,
    classList: { add: (c) => classes.add(c), remove: (c) => classes.delete(c), contains: (c) => classes.has(c) },
    get offsetParent() { return classes.has('hidden') ? null : {}; },
    getBoundingClientRect() { return this.rect; },
    click() { this.clicks += 1; },
  };
}
/** A manual scheduler: `next()` runs the earliest pending callback and moves the clock to it. */
function scheduler() {
  let clock = 0;
  const q = [];
  return {
    now: () => clock,
    set: (fn, ms) => { const id = { fn, at: clock + ms }; q.push(id); return id; },
    clear: (id) => { const i = q.indexOf(id); if (i >= 0) q.splice(i, 1); },
    next() { q.sort((a, b) => a.at - b.at); const id = q.shift(); if (!id) return false; clock = id.at; id.fn(); return true; },
    pending: () => q.length,
  };
}
const SQ = [[40, 40], [80, 40], [80, 80], [40, 80], [40, 40]];        // 160 mm
const LINE = [[100, 100], [140, 100]];                                 // 40 mm

test('traceMs: 70 mm a second between 1.2 and 4 s, divided by speed, 0 for nothing', () => {
  assert.equal(traceMs([]), 0); assert.equal(traceMs([LINE]), 1200); assert.equal(traceMs([SQ], 1), 2286);
  assert.equal(traceMs([SQ, SQ, SQ], 1), 4000); assert.equal(traceMs([SQ], 2), 1143);
});

test('plan: a pick draws, lifts and presses the picker, rolls down the rows to the target, presses it, holds, then lifts and presses Go', () => {
  const p = plan({ hand: 'pick', artist: 'haring', row: 2, draw: [LINE] });
  assert.deepEqual(p, [
    { draw: [LINE], ms: 1200 },
    { glide: 'picker', ms: HAND.glide }, { hover: 'picker', ms: HAND.hover }, { press: 'picker', ms: HAND.press },
    { glide: 'row:0', ms: HAND.rollGlide }, { hover: 'row:0', ms: HAND.rollHover },
    { glide: 'row:1', ms: HAND.rollGlide }, { hover: 'row:1', ms: HAND.rollHover },
    { glide: 'row:2', ms: HAND.rollGlide }, { hover: 'row:2', ms: HAND.hover },
    { press: 'row', ms: HAND.press }, { wait: HAND.hold },
    { glide: 'go', ms: HAND.glide }, { hover: 'go', ms: HAND.hover }, { press: 'go', ms: HAND.press }]);
  assert.deepEqual(plan({ hand: 'go', draw: [] }), [{ glide: 'go', ms: HAND.glide }, { hover: 'go', ms: HAND.hover }, { press: 'go', ms: HAND.press }]);
  const off = plan({ hand: 'pick', artist: 'nobody', row: -1, draw: [] });
  assert.deepEqual(off.slice(3, 5), [{ glide: 'row', ms: HAND.glide }, { hover: 'row', ms: HAND.hover }]);   // no roll: straight to the row by name
  assert.equal(plan({ hand: 'go', draw: [LINE] }, 2)[0].ms, 600);
  assert.equal(planMs({ hand: 'go', draw: [LINE] }), 1200 + HAND.glide + HAND.hover + HAND.press);
  assert.equal(planMs({ hand: 'go', draw: [LINE] }, 2), 600 + Math.round(HAND.glide / 2) + Math.round(HAND.hover / 2) + Math.round(HAND.press / 2));
});

function rig({ menuOpen = false, pickerHidden = false } = {}) {
  const s = scheduler();
  const stage = fake('stage', { rect: { left: 100, top: 50, width: 800, height: 450 } });
  const picker = fake('picker', { hidden: pickerHidden, rect: { left: 120, top: 100, width: 60, height: 20 } });
  const rows = [0, 1, 2].map(i => fake(`row${i}`, { hidden: !menuOpen, rect: { left: 120, top: 130 + 30 * i, width: 200, height: 20 } }));
  const go = fake('go', { rect: { left: 300, top: 100, width: 80, height: 30 } });
  const setMenu = (open) => rows.forEach(r => r.classList[open ? 'remove' : 'add']('hidden'));
  picker.click = () => { picker.clicks += 1; setMenu(rows[0].offsetParent === null); };      // toggles the menu
  rows[2].click = () => { rows[2].clicks += 1; setMenu(false); };                               // a pick closes the menu
  const tracer = { calls: [], play(strokes, o) { this.calls.push(['play', strokes, o.durationMs]); this.onMove = o.onMove; o.onMove([88, 120]); },
                   stop() { this.calls.push(['stop']); }, pause() { this.calls.push(['pause']); }, resume() { this.calls.push(['resume']); } };
  const el = fake('hand', { hidden: true });
  const targets = (name, cue) => name === 'picker' ? picker : name === 'go' ? go : name === 'row' ? rows[2] : name.startsWith('row:') ? rows[+name.slice(4)] : null;
  const hand = new Hand(el, { stage, targets, tracer, toStage: ([x, y]) => [x * 2, y * 2], speed: 1, now: s.now, timers: { set: s.set, clear: s.clear } });
  return { hand, el, picker, rows, go, tracer, s, cue: { hand: 'pick', artist: 'haring', row: 2, draw: [LINE] } };
}

test('Hand: the draw step plays the tracer and the hand follows its tip with the marker out; then it lifts, squashes, and clicks on the release', () => {
  const { hand, el, picker, rows, go, tracer, s, cue } = rig();
  hand.run(cue);
  assert.deepEqual(tracer.calls, [['play', [LINE], 1200]]);
  assert.ok(el.classList.contains('draw'), 'the marker shows while drawing');
  assert.equal(el.style.left, '176px'); assert.equal(el.style.top, '240px');                           // toStage([88, 120])
  s.next();                                                                                            // draw done → glide picker
  assert.ok(!el.classList.contains('draw'));
  assert.equal(el.style.left, '50px'); assert.equal(el.style.top, '60px');
  s.next();                                                                                            // arrived → hover picker
  assert.ok(picker.classList.contains('hover')); assert.equal(picker.clicks, 0);
  s.next();                                                                                            // hover held → press picker
  assert.ok(picker.classList.contains('active') && el.classList.contains('press')); assert.equal(picker.clicks, 0, 'not yet: the click fires on the release');
  s.next();                                                                                            // release → click → menu opens → glide row:0
  assert.equal(picker.clicks, 1); assert.ok(!picker.classList.contains('active') && !picker.classList.contains('hover') && !el.classList.contains('press'));
  assert.equal(rows[0].offsetParent !== null, true, 'the menu is open');
  s.next(); assert.ok(rows[0].classList.contains('hover'));                                            // hover row:0
  s.next(); s.next(); assert.ok(!rows[0].classList.contains('hover') && rows[1].classList.contains('hover'));   // glide row:1, hover row:1
  s.next(); s.next(); assert.ok(rows[2].classList.contains('hover'));                                  // glide row:2, hover row:2 (long)
  s.next(); assert.ok(rows[2].classList.contains('active'));                                           // press row
  s.next(); assert.equal(rows[2].clicks, 1); assert.equal(rows[2].offsetParent, null, 'the pick closed the menu');   // release → wait
  s.next(); assert.equal(el.style.left, '240px'); assert.equal(el.style.top, '65px');                 // glide go
  s.next(); assert.ok(go.classList.contains('hover'));                                                 // hover go
  s.next(); assert.ok(go.classList.contains('active'));                                                // press go
  s.next(); assert.equal(go.clicks, 1); assert.ok(el.classList.contains('hidden'), 'hidden once the plan is done');
  assert.equal(s.pending(), 0);
});

test('Hand: pause holds the pending step and the tracer, resume finishes it; cancel stops the tracer and clears every class', () => {
  const { hand, el, picker, rows, tracer, s, cue } = rig();
  hand.run(cue);
  s.next(); s.next();                                                                                  // hovering the picker
  hand.pause();
  assert.deepEqual(tracer.calls.slice(-1), [['pause']]);
  assert.equal(s.pending(), 0, 'nothing scheduled while paused'); assert.ok(picker.classList.contains('hover'), 'the lift stays');
  hand.resume();
  assert.deepEqual(tracer.calls.slice(-1), [['resume']]);
  assert.equal(s.pending(), 1);
  s.next(); assert.ok(picker.classList.contains('active'));                                            // the press follows as planned
  s.next(); s.next(); assert.ok(rows[0].classList.contains('hover'));
  hand.cancel();
  assert.deepEqual(tracer.calls.slice(-1), [['stop']]);
  assert.ok(!rows[0].classList.contains('hover') && !picker.classList.contains('active') && el.classList.contains('hidden') && !el.classList.contains('draw'));
  assert.equal(s.pending(), 0);
  hand.pause(); hand.resume();                                                                         // idle: no-ops
  assert.equal(s.pending(), 0);
});

test('Hand: it presses what it sees: no toggle on a menu a visitor opened, reopen one that closed, skip a hidden target', () => {
  const open = rig({ menuOpen: true });
  open.hand.run(open.cue);
  while (open.s.next());
  assert.equal(open.picker.clicks, 0); assert.equal(open.rows[2].clicks, 1); assert.equal(open.go.clicks, 1);
  const closed = rig();
  closed.picker.click = () => { closed.picker.clicks += 1; if (closed.picker.clicks > 1) closed.rows.forEach(r => r.classList.remove('hidden')); };   // a visitor closes it right after the first press
  closed.hand.run(closed.cue);
  while (closed.s.next());
  assert.equal(closed.picker.clicks, 2, 'pressed again to reopen'); assert.equal(closed.rows[2].clicks, 1);
  const browsing = rig({ pickerHidden: true });
  browsing.hand.run(browsing.cue);
  while (browsing.s.next());
  assert.equal(browsing.picker.clicks, 0); assert.equal(browsing.rows[2].clicks, 0); assert.equal(browsing.go.clicks, 1);
});
```

- [ ] **Step 2: Run the tests to see them fail**

Run (from `code/hackathon`): `node --test pagetests/hand.test.mjs`
Expected: FAIL, `planMs` and `traceMs` are not exported.

- [ ] **Step 3: Rewrite `hand.js`**

Replace `code/hackathon/duet/static/js/hand.js` with:

```js
/** The demo's hand: a cartoon pointer that shows the recorded visitor's part during the human turn: it draws
 *  their mark with a red marker, then presses the page's own buttons the way a finger would, lifting and
 *  squashing them. `traceMs`, `plan`, and `planMs` are pure; `Hand` moves the element and drives the DOM.
 *  Replay mode only. */
import { polylineLength } from './geometry.js?v=ds9';

export const HAND = { glide: 500, hover: 350, press: 200, hold: 500, rollGlide: 120, rollHover: 100, mmPerSec: 70, traceMin: 1200, traceMax: 4000 };

/** How long the hand takes to draw `strokes` (board mm): 70 mm a second, within 1.2 to 4 s, divided by `speed`. */
export function traceMs(strokes, speed = 1) {
  const len = polylineLength(strokes || []);
  if (!len) return 0;
  const div = speed > 0 ? speed : 1;
  return Math.round(Math.min(HAND.traceMax, Math.max(HAND.traceMin, (len / HAND.mmPerSec) * 1000)) / div);
}

/** Steps for a cue: `{ draw: strokes, ms }`, `{ glide: target, ms }`, `{ hover: target, ms }`, `{ press: target, ms }`,
 *  `{ wait: ms }`. Targets: `picker`, `go`, `row` (the cue's artist), `row:<i>` (the i-th menu row, on the way down).
 *  A pick rolls from the first row to `cue.row`, lifting each; an unknown row (-1) goes straight to the row by name. */
export function plan(cue, speed = 1) {
  const div = speed > 0 ? speed : 1;
  const ms = (v) => Math.round(v / div);
  const strokes = (cue && cue.draw) || [];
  const draw = strokes.length ? [{ draw: strokes, ms: traceMs(strokes, div) }] : [];
  const go = [{ glide: 'go', ms: ms(HAND.glide) }, { hover: 'go', ms: ms(HAND.hover) }, { press: 'go', ms: ms(HAND.press) }];
  if (!(cue && cue.hand === 'pick')) return [...draw, ...go];
  const last = typeof cue.row === 'number' ? cue.row : -1;
  const roll = [];
  if (last < 0) roll.push({ glide: 'row', ms: ms(HAND.glide) }, { hover: 'row', ms: ms(HAND.hover) });
  for (let i = 0; i <= last; i++) roll.push({ glide: `row:${i}`, ms: ms(HAND.rollGlide) }, { hover: `row:${i}`, ms: ms(i === last ? HAND.hover : HAND.rollHover) });
  return [...draw, { glide: 'picker', ms: ms(HAND.glide) }, { hover: 'picker', ms: ms(HAND.hover) }, { press: 'picker', ms: ms(HAND.press) },
          ...roll, { press: 'row', ms: ms(HAND.press) }, { wait: ms(HAND.hold) }, ...go];
}

/** The whole plan's time, for the turn clock. */
export const planMs = (cue, speed = 1) => plan(cue, speed).reduce((sum, s) => sum + (s.ms ?? s.wait ?? 0), 0);

const onScreen = (el) => !!el && el.offsetParent !== null;
const realTimers = { set: (fn, ms) => setTimeout(fn, ms), clear: (id) => clearTimeout(id) };

/** `targets(name, cue)` resolves a target name to the page's element or null; `tracer` is the visitor's ghost pen
 *  (`play`, `stop`, `pause`, `resume`); `toStage(p)` turns a board point into stage pixels, null before calibration.
 *  The hand presses what it sees: it does not toggle a menu a visitor already opened, reopens one that closed
 *  under it, and skips a target that is off screen. `pause()` holds the pending step, `resume()` finishes it,
 *  `cancel()` stops everything and hides the hand. */
export class Hand {
  constructor(el, { stage, targets, tracer = null, toStage = () => null, speed = 1, now = () => Date.now(), timers = realTimers }) {
    this.el = el; this.stage = stage; this.targets = targets; this.tracer = tracer; this.toStage = toStage; this.speed = speed;
    this.now = now; this.timers = timers;
    this.timer = null; this.pending = null; this.paused = false; this.token = 0; this.hovered = null; this.pressed = null;
  }
  target(name, cue) { const el = this.targets(name, cue); return onScreen(el) ? el : null; }
  run(cue) {
    this.cancel();
    const steps = plan(cue, this.speed), token = ++this.token;
    this.moveTo(this.stage);                              // over the board while hidden, as if drawing the mark; no glide from where it last was
    this.el.classList.remove('hidden');
    const step = (i) => {
      if (token !== this.token) return;
      this.release();
      if (i >= steps.length) { this.hide(); return; }
      const s = steps[i];
      let ms = s.ms ?? s.wait ?? 0, pressed = null;
      if (s.draw) { if (!this.draw(s.draw, ms)) ms = 0; }
      else if (s.glide) { const t = this.target(s.glide, cue); if (t) this.moveTo(t); else ms = 0; }
      else if (s.hover) { if (!this.hover(s.hover, cue)) ms = 0; }
      else if (s.press) { pressed = this.press(s.press, cue); if (!pressed) ms = 0; }
      this.after(ms, () => { if (pressed) { this.unhover(); pressed.click(); } step(i + 1); });   // a press clicks on the release
    };
    step(0);
  }
  after(ms, fn) {
    this.pending = { fn, due: this.now() + ms };
    this.timer = this.timers.set(() => { this.timer = null; this.pending = null; fn(); }, ms);
  }
  /** The fingertip on the target's centre, in stage pixels. */
  moveTo(target) {
    const r = target.getBoundingClientRect(), s = this.stage.getBoundingClientRect();
    this.moveToPoint(r.left - s.left + r.width / 2, r.top - s.top + r.height / 2);
  }
  moveToPoint(x, y) { this.el.style.left = `${x}px`; this.el.style.top = `${y}px`; }
  /** The marker out, the tracer drawing, the fingertip on the pen's point. True when there is something to draw. */
  draw(strokes, ms) {
    if (!this.tracer || !ms) return false;
    this.el.classList.add('draw');
    this.tracer.play(strokes, { durationMs: ms, onMove: (p) => { const q = p && this.toStage(p); if (q) this.moveToPoint(q[0], q[1]); } });
    return true;
  }
  hover(name, cue) {
    this.unhover();
    const el = this.target(name, cue);
    if (!el) return false;
    el.classList.add('hover'); this.hovered = el;
    return true;
  }
  unhover() { if (this.hovered) { this.hovered.classList.remove('hover'); this.hovered = null; } }
  /** The target squashed under the hand. Returns the element to click on the release, or null. */
  press(name, cue) {
    if (name === 'picker' && this.target('row', cue)) return null;                          // the menu is already open
    if (name === 'row' && !this.target('row', cue)) { const p = this.target('picker', cue); if (!p) return null; p.click(); }   // reopen it
    const el = this.target(name, cue);
    if (!el) return null;
    el.classList.add('active'); this.el.classList.add('press'); this.pressed = el;
    return el;
  }
  /** The end of a press or a draw: the squash and the marker go. */
  release() {
    if (this.pressed) { this.pressed.classList.remove('active'); this.pressed = null; }
    this.el.classList.remove('press'); this.el.classList.remove('draw');
  }
  pause() {
    if (this.paused || !this.pending) return;
    this.paused = true;
    this.timers.clear(this.timer); this.timer = null;
    this.left = Math.max(0, this.pending.due - this.now());
    if (this.tracer) this.tracer.pause();
  }
  resume() {
    if (!this.paused) return;
    this.paused = false;
    const { fn } = this.pending;
    this.after(this.left, fn);
    if (this.tracer) this.tracer.resume();
  }
  hide() { this.release(); this.el.classList.add('hidden'); }
  cancel() {
    this.token += 1;
    if (this.timer) this.timers.clear(this.timer);
    this.timer = null; this.pending = null; this.paused = false;
    this.unhover();
    if (this.tracer) this.tracer.stop();
    this.hide();
  }
}
```

- [ ] **Step 4: Run the tests**

Run: `node --test pagetests/hand.test.mjs`
Expected: all pass. Note the `?v=ds9` import: Node ignores the query on a file path, and Task 6 moves every other import to `ds9` too.

- [ ] **Step 5: Commit**

```bash
git add code/hackathon/duet/static/js/hand.js code/hackathon/pagetests/hand.test.mjs
git commit -m "feat(page): the hand draws the mark through a tracer, lifts and squashes what it presses, rolls down the menu, and can pause"
```

---

### Task 2: The schedule's `draw`, `row`, and clock cues

**Files:**
- Modify: `code/hackathon/duet/static/js/replay.js`
- Modify: `code/hackathon/pagetests/replay.test.mjs`

- [ ] **Step 1: Update the tests**

In `code/hackathon/pagetests/replay.test.mjs`:

Change the import lines at the top to:

```js
import { schedule, words, clip, drawMs, Player, PACE, WORDS, DEFAULT_ARTIST } from '../duet/static/js/replay.js';
import { planMs } from '../duet/static/js/hand.js';
```

In the test `schedule: the picker setting is Abstract, …` replace the two cue assertions:

```js
  const cues = steps.filter(s => s.cue && s.cue.hand).map(({ cue }) => ({ hand: cue.hand, artist: cue.artist }));
  assert.deepEqual(cues, [{ hand: 'pick', artist: 'mimic' }, { hand: 'pick', artist: 'haring' }]);
  const same = schedule({ ...REPLAY, turns: [REPLAY.turns[0], { ...REPLAY.turns[1], artist: 'mimic' }] });
  assert.deepEqual(same.filter(s => s.cue && s.cue.hand).map(s => s.cue.hand), ['pick', 'go']);
```

and its last line `assert.equal(PACE.human, 6000);` to `assert.equal(PACE.human, 14000);`.

Add after that test:

```js
test('schedule: the hand cue carries the roster row and the drawable strokes; a clock cue follows it and each capture with the half\'s time', () => {
  const speck = [[10, 10], [12, 11]];                                  // 2.2 mm: a trace fragment, not a mark
  const r = { ...REPLAY, turns: [{ ...REPLAY.turns[0], new: [SQ, speck] }, REPLAY.turns[1]] };
  const cues = schedule(r).filter(s => s.cue).map(s => s.cue);
  assert.deepEqual(cues[0], { hand: 'pick', artist: 'mimic', row: 1, draw: [SQ] });
  assert.deepEqual(cues[1], { clock: 'visitor', ms: planMs(cues[0]) });
  assert.deepEqual(cues[2], { clock: 'robot', ms: PACE.capture + PACE.thinkInk + PACE.plan + PACE.settle + drawMs(2) });
  assert.deepEqual(cues[3], { hand: 'pick', artist: 'haring', row: 2, draw: [LINE] });
  assert.equal(cues[5].ms, PACE.capture + PACE.thinkClaude + PACE.plan + PACE.settle + drawMs(1));
  const fast = schedule(r, 2).filter(s => s.cue).map(s => s.cue);
  assert.equal(fast[1].ms, planMs(fast[0], 2));
  assert.equal(fast[2].ms, Math.round((PACE.capture + PACE.thinkInk + PACE.plan + PACE.settle) / 2) + drawMs(2, 2));
  const steps = schedule(r);
  const h = steps.findIndex(s => s.emit && s.emit.state === 'human_turn');
  assert.ok(steps[h + 1].cue.hand && steps[h + 2].cue.clock === 'visitor' && steps[h + 3].on === 'pass', 'hand cue, clock cue, then the wait');
  const c = steps.findIndex(s => s.emit && s.emit.state === 'capture');
  assert.equal(steps[c + 1].cue.clock, 'robot');
  const off = schedule({ ...r, artists: ['haring'] }).filter(s => s.cue && s.cue.hand)[0];
  assert.equal(off.row, -1, 'an artist off the roster has no row');
});
```

In the Player test `Player: cues reach the callback, …` replace `assert.deepEqual(cues, [{ hand: 'pick', artist: 'mimic' }]);` with:

```js
  assert.equal(cues.length, 2); assert.equal(cues[0].hand, 'pick'); assert.equal(cues[0].artist, 'mimic'); assert.equal(cues[1].clock, 'visitor');
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `node --test pagetests/replay.test.mjs`
Expected: FAIL on the cue shapes and `PACE.human`.

- [ ] **Step 3: Change the schedule**

In `code/hackathon/duet/static/js/replay.js`:

Add the import as the first code line after the doc comment:

```js
import { planMs } from './hand.js?v=ds9';
```

Change `PACE.human` to `14000` and add the fragment threshold under `BUDGET_MM`:

```js
const BUDGET_MM = { short: 400, medium: 1200, long: 4000 };
const MIN_FRAGMENT_MM = 6;       // the camera trace leaves specks around a mark; the hand draws only what a person would
```

Replace the loop body of `schedule` from `for (const t of turns) {` through `setting = artist;\n  }` with:

```js
  for (const t of turns) {
    const n = t.turn, artist = t.artist;
    const st = (state, turn, who = artist) => e(stateMsg(replay, state, turn, who, session, coverage));
    const draw = (t.new || []).filter(pl => strokeLength(pl) >= MIN_FRAGMENT_MM);
    const handCue = artist === setting ? { hand: 'go', draw } : { hand: 'pick', artist, row: roster.indexOf(artist), draw };
    steps.push(st('human_turn', n - 1, setting), { cue: handCue }, { cue: { clock: 'visitor', ms: planMs(handCue, div) } }, w(PACE.human, 'pass'));
    ink = [...ink, ...(t.new || [])];
    const plan = t.plan || [], think = t.source === 'ink' ? PACE.thinkInk : PACE.thinkClaude;
    steps.push(st('capture', n - 1), { cue: { clock: 'robot', ms: Math.round((PACE.capture + think + PACE.plan + PACE.settle) / div) + drawMs(plan.length, div) } },
               shot(n, 'human', artist, (t.frames || {}).human !== false),
               e({ type: 'human', polylines: ink, new: t.new || [], found: true, turn: n }), w(PACE.capture));
    const { thought, quip } = words(t);
    steps.push(st('interpret', n - 1), w(think),
               e({ type: 'interpretation', sees: t.sees || '', adds: t.adds || '', thought, quip, source: t.source || 'claude',
                   latency_s: t.latency_s ?? null, error: null, turn: n, artist }));
    steps.push(st('plan', n - 1), e({ type: 'plan', polylines: plan, color: t.color || '#1b8f3a', budget_mm: BUDGET_MM[replay.length] || 4000, turn: n, artist }), w(PACE.plan));
    steps.push(st('robot_draw', n - 1), e({ type: 'feed', source: 'held' }));
    const per = plan.length ? drawMs(plan.length) / plan.length : 0;
    let drawn = 0;
    plan.forEach((pl, i) => { drawn += strokeLength(pl); steps.push(w(per), e({ type: 'progress', stroke: i, drawn_mm: Math.round(drawn), turn: n })); });
    coverage = t.coverage ?? coverage;
    steps.push(shot(n, 'robot', artist, (t.frames || {}).robot !== false), st('look', n), e({ type: 'feed', source: 'live' }), w(PACE.settle));
    setting = artist;
  }
```

and add `const roster = replay.artists || ARTISTS;` right after `const frames = replay.frames || {};`. Update the doc comment above `schedule` so its cue sentence reads:

```js
 *  holds until Go or the time is up, `{ cue }` tells the page what the recorded visitor did and how long each
 *  half takes: `{ hand: 'pick', artist, row, draw }` when they switched artist, `{ hand: 'go', draw }` otherwise,
 *  with `draw` their strokes (specks under 6 mm dropped) and `row` the artist's roster index; `{ clock: 'visitor' | 'robot', ms }`
 *  at each human turn and each capture with that half's scripted time. The picker's
```

- [ ] **Step 4: Run all the tests**

Run: `node --test 'pagetests/*.test.mjs'`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add code/hackathon/duet/static/js/replay.js code/hackathon/pagetests/replay.test.mjs
git commit -m "feat(replay): the hand cue carries the strokes to draw and the roster row; clock cues time each half of an exchange"
```

---

### Task 3: `GhostPen`: `onMove`, `pause`, `resume`

**Files:**
- Rewrite: `code/hackathon/duet/static/js/preview.js`
- Create: `code/hackathon/pagetests/preview.test.mjs`

- [ ] **Step 1: Write the failing test**

Create `code/hackathon/pagetests/preview.test.mjs`:

```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { GhostPen } from '../duet/static/js/preview.js';

const node = () => { const a = {}, classes = new Set(); return { style: {}, attrs: a, setAttribute: (k, v) => { a[k] = v; }, classList: { add: (c) => classes.add(c), remove: (c) => classes.delete(c), contains: (c) => classes.has(c) } }; };
/** Fake frames: `frame(ms)` advances the clock and runs the pending callback once. */
function frames() {
  let clock = 0, pending = null, id = 0;
  return {
    now: () => clock,
    raf: (cb) => { pending = cb; return ++id; },
    caf: () => { pending = null; },
    frame: (ms) => { clock += ms; const cb = pending; pending = null; if (cb) cb(clock); },
    get queued() { return pending !== null; },
  };
}
const LINE = [[0, 0], [100, 0]];                       // 100 mm

test('GhostPen: onMove reports the pen point each frame and null at the end; the trace is paced to durationMs', () => {
  const f = frames(), group = node(), path = node(), pen = node(), seen = [];
  const g = new GhostPen(group, path, pen, { raf: f.raf, caf: f.caf, now: f.now });
  g.play([LINE], { durationMs: 1000, onMove: (p) => seen.push(p) });
  assert.ok(!group.classList.contains('idle') && f.queued);
  f.frame(250); assert.deepEqual(seen[0], [25, 0]); assert.equal(path.attrs.d, 'M0.00 0.00 L25.00 0.00');
  f.frame(750); assert.deepEqual(seen.slice(-2), [[100, 0], null]); assert.equal(pen.style.display, 'none'); assert.ok(!f.queued);
});

test('GhostPen: pause holds the trace, resume finishes the rest over the remaining time, stop reports null once', () => {
  const f = frames(), group = node(), path = node(), pen = node(), seen = [];
  const g = new GhostPen(group, path, pen, { raf: f.raf, caf: f.caf, now: f.now });
  g.play([LINE], { durationMs: 1000, onMove: (p) => seen.push(p) });
  f.frame(500); assert.deepEqual(seen.at(-1), [50, 0]);
  g.pause(); assert.ok(!f.queued, 'no frame while paused');
  f.frame(3000);                                       // time passes with nothing drawn
  g.resume(); assert.ok(f.queued);
  f.frame(250); assert.deepEqual(seen.at(-1), [75, 0], 'continues from where it was');
  f.frame(250); assert.deepEqual(seen.slice(-2), [[100, 0], null]);
  seen.length = 0;
  g.play([LINE], { durationMs: 1000, onMove: (p) => seen.push(p) });
  f.frame(100);
  g.stop(); assert.deepEqual(seen.at(-1), null); assert.ok(group.classList.contains('idle')); assert.equal(path.attrs.d, '');
  g.stop(); g.pause(); g.resume(); assert.equal(seen.filter(p => p === null).length, 1, 'idle calls do nothing');
});
```

- [ ] **Step 2: Run the test to see it fail**

Run: `node --test pagetests/preview.test.mjs`
Expected: FAIL: `requestAnimationFrame is not defined` (the options are not honoured yet).

- [ ] **Step 3: Rewrite `preview.js`**

Replace `code/hackathon/duet/static/js/preview.js` with:

```js
/** The ghost pen: traces the whole plan once at a constant speed, ahead of the real arm. In replay mode it
 *  is the arm: `play(plan, { durationMs })` paces the trace to the scripted drawing time. A second instance
 *  is the visitor's marker in the demo. `onMove(p)` reports the pen's board point each frame and null when
 *  the trace ends or stops; `pause()` and `resume()` hold the trace and finish it over the time that was left. */
import { polylineLength, pointAlong, tracePath } from './geometry.js?v=ds9';

const browserFrames = {
  raf: (cb) => requestAnimationFrame(cb), caf: (id) => cancelAnimationFrame(id), now: () => performance.now(),
};

export class GhostPen {
  constructor(group, path, pen, { mmPerSec = 60, raf = browserFrames.raf, caf = browserFrames.caf, now = browserFrames.now } = {}) {
    this.group = group; this.path = path; this.pen = pen; this.mmPerSec = mmPerSec;
    this.raf = raf; this.caf = caf; this.now = now;
    this.frame = null; this.playing = false; this.pausedAt = null; this.onMove = null;
    this.group.classList.add('idle');
  }

  play(polylines, { durationMs = 0, onMove = null } = {}) {
    this.stop();
    const total = polylineLength(polylines);
    if (!total) return;
    this.polylines = polylines; this.total = total; this.onMove = onMove;
    this.speed = durationMs > 0 ? total / (durationMs / 1000) : this.mmPerSec;
    this.group.classList.remove('idle');
    this.start = this.now(); this.playing = true; this.pausedAt = null;
    this.pen.style.display = '';
    this.frame = this.raf((t) => this.tick(t));
  }

  tick(t) {
    const dist = Math.min(this.total, ((t - this.start) / 1000) * this.speed);
    const { p } = pointAlong(this.polylines, dist);
    this.path.setAttribute('d', tracePath(this.polylines, dist));
    this.pen.setAttribute('cx', p[0].toFixed(2)); this.pen.setAttribute('cy', p[1].toFixed(2));
    if (this.onMove) this.onMove(p);
    if (dist < this.total) { this.frame = this.raf((t2) => this.tick(t2)); return; }
    this.frame = null; this.playing = false; this.pen.style.display = 'none';
    this.done();
  }

  /** The end of a trace, by finishing or by `stop`: the listener hears null once. */
  done() { const cb = this.onMove; this.onMove = null; if (cb) cb(null); }

  pause() {
    if (!this.playing || this.pausedAt !== null) return;
    if (this.frame !== null) this.caf(this.frame);
    this.frame = null; this.pausedAt = this.now();
  }

  resume() {
    if (this.pausedAt === null) return;
    this.start += this.now() - this.pausedAt;             // the time paused never happened, as far as the trace is concerned
    this.pausedAt = null;
    this.frame = this.raf((t) => this.tick(t));
  }

  stop() {
    if (this.frame !== null) this.caf(this.frame);
    this.frame = null; this.pausedAt = null;
    const was = this.playing; this.playing = false;
    this.group.classList.add('idle');
    this.path.setAttribute('d', '');
    if (was) this.done();
  }
}
```

- [ ] **Step 4: Run the tests**

Run: `node --test pagetests/preview.test.mjs`
Expected: all pass. The first test's second frame lands exactly on the end (1000 ms), so `[100, 0]` then `null` arrive in that frame.

- [ ] **Step 5: Commit**

```bash
git add code/hackathon/duet/static/js/preview.js code/hackathon/pagetests/preview.test.mjs
git commit -m "feat(page): the ghost pen reports its point, pauses, and resumes; frames and the clock are injectable"
```

---

### Task 4: `clock.js`

**Files:**
- Create: `code/hackathon/duet/static/js/clock.js`
- Create: `code/hackathon/pagetests/clock.test.mjs`

- [ ] **Step 1: Write the failing test**

Create `code/hackathon/pagetests/clock.test.mjs`:

```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { formatSeconds, fraction, Clock } from '../duet/static/js/clock.js';

const el = () => { const classes = new Set(['hidden']), vars = {}, dataset = {}; return { dataset, vars, textContent: '',
  classList: { add: (c) => classes.add(c), remove: (c) => classes.delete(c), contains: (c) => classes.has(c) }, style: { setProperty: (k, v) => { vars[k] = v; } } }; };

test('formatSeconds and fraction', () => {
  assert.equal(formatSeconds(0), '0.0 s'); assert.equal(formatSeconds(8432), '8.4 s'); assert.equal(formatSeconds(-5), '0.0 s');
  assert.equal(fraction(0, 1000), 0); assert.equal(fraction(250, 1000), 0.25); assert.equal(fraction(2000, 1000), 1); assert.equal(fraction(5, 0), 1);
});

test('Clock: start shows and counts, past the total the bar stays full, pause freezes and relabels, resume continues, stop hides', () => {
  let clock = 0;
  const timers = { set: (fn) => ({ fn }), clear: () => {} };
  const chip = el(), who = el(), time = el();
  const c = new Clock(chip, { who, time, now: () => clock, timers });
  c.start({ who: 'visitor', ms: 2000 });
  assert.ok(!chip.classList.contains('hidden')); assert.equal(chip.dataset.who, 'visitor'); assert.equal(who.textContent, 'Visitor'); assert.equal(time.textContent, '0.0 s');
  clock = 500; c.render(); assert.equal(chip.vars['--fill'], 0.25); assert.equal(time.textContent, '0.5 s');
  clock = 3000; c.render(); assert.equal(chip.vars['--fill'], 1); assert.equal(time.textContent, '3.0 s');
  c.pause(); assert.equal(chip.dataset.who, 'paused'); assert.equal(who.textContent, 'Paused');
  clock = 9000; c.render(); assert.equal(time.textContent, '3.0 s', 'frozen');
  c.resume(); assert.equal(chip.dataset.who, 'visitor'); assert.equal(who.textContent, 'Visitor');
  clock = 9500; c.render(); assert.equal(time.textContent, '3.5 s');
  c.start({ who: 'robot', ms: 1000 });
  assert.equal(chip.dataset.who, 'robot'); assert.equal(who.textContent, 'Robot'); assert.equal(time.textContent, '0.0 s');
  c.stop(); assert.ok(chip.classList.contains('hidden'));
  c.pause(); c.resume(); c.render(); assert.ok(chip.classList.contains('hidden'), 'idle calls do nothing');
});
```

- [ ] **Step 2: Run the test to see it fail**

Run: `node --test pagetests/clock.test.mjs`
Expected: FAIL, the module does not exist.

- [ ] **Step 3: Write `clock.js`**

Create `code/hackathon/duet/static/js/clock.js`:

```js
/** The turn clock: a chip that names who is on, counts their seconds, and fills over the half's scripted
 *  time. `formatSeconds` and `fraction` are pure; `Clock` drives the chip. Replay mode only. */

export function formatSeconds(ms) { return `${(Math.max(0, ms) / 1000).toFixed(1)} s`; }

/** How much of the bar to fill: 0 to 1, and full when there is no total to measure against. */
export function fraction(elapsed, total) {
  if (!(total > 0)) return 1;
  return Math.min(1, Math.max(0, elapsed / total));
}

const LABEL = { visitor: 'Visitor', robot: 'Robot', paused: 'Paused' };
const realTimers = { set: (fn, ms) => setInterval(fn, ms), clear: (id) => clearInterval(id) };

export class Clock {
  constructor(el, { who, time, now = () => Date.now(), interval = 100, timers = realTimers }) {
    this.el = el; this.whoEl = who; this.timeEl = time; this.now = now; this.interval = interval; this.timers = timers;
    this.timer = null; this.paused = false; this.who = 'visitor'; this.total = 0; this.elapsed = 0; this.last = 0;
  }
  start({ who, ms }) {
    this.stop();
    this.who = who; this.total = ms; this.elapsed = 0; this.last = this.now();
    this.el.classList.remove('hidden');
    this.timer = this.timers.set(() => this.render(), this.interval);
    this.render();
  }
  render() {
    if (this.timer === null) return;
    const t = this.now();
    if (!this.paused) this.elapsed += t - this.last;
    this.last = t;
    const who = this.paused ? 'paused' : this.who;
    this.el.dataset.who = who; this.whoEl.textContent = LABEL[who];
    this.timeEl.textContent = formatSeconds(this.elapsed);
    this.el.style.setProperty('--fill', fraction(this.elapsed, this.total));
  }
  pause() { if (this.timer === null || this.paused) return; this.render(); this.paused = true; this.render(); }
  resume() { if (!this.paused) return; this.last = this.now(); this.paused = false; this.render(); }
  stop() {
    if (this.timer !== null) this.timers.clear(this.timer);
    this.timer = null; this.paused = false;
    this.el.classList.add('hidden');
  }
}
```

- [ ] **Step 4: Run the test**

Run: `node --test pagetests/clock.test.mjs`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add code/hackathon/duet/static/js/clock.js code/hackathon/pagetests/clock.test.mjs
git commit -m "feat(page): clock.js: the turn clock's format, fill, and runner"
```

---

### Task 5: Markup and styles: marker, tags, clock chip, red pen layer, hover and active twins

**Files:**
- Modify: `code/hackathon/duet/static/index.html`
- Modify: `code/hackathon/duet/static/duet.css`
- Modify: `code/hackathon/pagetests/style.test.mjs`

- [ ] **Step 1: Write the failing test**

Append to `code/hackathon/pagetests/style.test.mjs`:

```js
test('the hand draws and is named: a marker in its SVG, a Visitor tag, a red pen layer; the robot dot has a Robot tag; the clock chip sits after the state chip', () => {
  const h = read('index.html');
  assert.match(h, /<g class="marker">\s*<rect[^>]*\/>\s*<path[^>]*\/>\s*<\/g>/, 'the marker: a barrel and a tip');
  assert.ok(h.indexOf('class="marker"') > h.indexOf('class="skin"') && h.indexOf('class="marker"') < h.indexOf('</svg>', h.indexOf('id="hand"')), 'the marker paints over the finger');
  assert.match(h, /<span class="tag">Visitor<\/span>\s*<\/div>/, 'the Visitor tag ends the hand element');
  assert.match(h, /<span class="tag hidden" id="pen-tag" data-el="tag — robot pen">Robot<\/span>/);
  assert.match(h, /<g class="hand-ink" id="l-hand" data-el="layer — the hand's red trace"><path id="handpath"\/><circle id="handpen" r="2\.2"\/><\/g>/);
  assert.ok(h.indexOf('id="l-hand"') > h.indexOf('id="l-ghost"') && h.indexOf('id="l-hand"') < h.indexOf('</g>\n    </svg>'), 'inside the board fit, after the ghost');
  assert.match(h, /id="state"[^\n]*<\/span>\n\s*<button class="chip white clock hidden" id="clock" title="Pause or resume the piece" data-el="chip — turn clock">\s*<i class="fill"><\/i><b id="clock-who">Visitor<\/b> <span id="clock-time">0\.0 s<\/span>\s*<\/button>/);
  const css = read('duet.css');
  assert.match(css, /button\.chip:hover, button\.chip\.hover \{/); assert.match(css, /button\.chip:active, button\.chip\.active \{/);
  assert.match(css, /\.go:hover, \.go\.hover, \.welcome-start:not\(:disabled\):hover \{/); assert.match(css, /\.go:active, \.go\.active, \.welcome-start:not\(:disabled\):active \{/);
  assert.match(css, /\.hand \.marker \{ display: none; \} \.hand\.draw \.marker \{ display: block; \}/);
  assert.match(css, /\.tag \{[^}]*pointer-events: none;[^}]*white-space: nowrap;/);
  assert.match(css, /\.hand \.tag \{ left: 3\.4cqw; top: 5\.4cqw; \}/); assert.match(css, /#pen-tag \{ z-index: 4; transform: translate\(1cqw, 1cqw\); \}/);
  assert.match(css, /\.clock \{ position: relative; overflow: hidden; \}/);
  assert.match(css, /\.clock \.fill \{[^}]*width: calc\(var\(--fill, 0\) \* 100%\);[^}]*background: var\(--human\);/);
  assert.match(css, /\.clock\[data-who="robot"\] \.fill \{ background: var\(--robot\); \}/);
  assert.match(css, /\.clock\[data-who="paused"\] \.fill \{ animation: blink 1s ease-in-out infinite; \}/);
  assert.match(css, /\.ov \.hand-ink path \{ stroke: var\(--human\); stroke-width: 1\.2; opacity: \.9; \} \.ov \.hand-ink circle \{ display: none; \}/);
});
```

- [ ] **Step 2: Run the test to see it fail**

Run: `node --test pagetests/style.test.mjs`
Expected: the new test FAILs on the marker.

- [ ] **Step 3: Change the markup**

In `code/hackathon/duet/static/index.html`:

After the `l-ghost` line (`<g class="ghost" id="l-ghost" …></g>`) add:

```html
        <g class="hand-ink" id="l-hand" data-el="layer — the hand's red trace"><path id="handpath"/><circle id="handpen" r="2.2"/></g>
```

After the state chip line (`<span class="chip white" id="state" data-el="chip — state">Connecting…</span>`) add:

```html
    <button class="chip white clock hidden" id="clock" title="Pause or resume the piece" data-el="chip — turn clock">
      <i class="fill"></i><b id="clock-who">Visitor</b> <span id="clock-time">0.0 s</span>
    </button>
```

In the hand element, after the `<path class="line" …/>` line and before `</svg>`, add the marker, and after `</svg>` add the tag, so the element reads:

```html
  <div class="hand hidden" id="hand" data-el="demo hand">
    <svg viewBox="0 0 60 72" aria-hidden="true">
      <rect class="cuff" x="19" y="56" width="37" height="14" rx="4"/>
      <path class="skin" d="…unchanged…"/>
      <path class="line" d="M30.5 30.5v9M40.5 31.5v9M50 33.5v8"/>
      <g class="marker">
        <rect x="9.5" y="7" width="9" height="40" rx="3" fill="#e5322d" stroke="#111" stroke-width="2.5"/>
        <path d="M14 1.5l-4.5 6.5h9z" fill="#111"/>
      </g>
    </svg>
    <span class="tag">Visitor</span>
  </div>
```

(keep the existing `skin` path's `d` exactly as it is). After the hand element add:

```html
  <span class="tag hidden" id="pen-tag" data-el="tag — robot pen">Robot</span>
```

- [ ] **Step 4: Change the styles**

In `code/hackathon/duet/static/duet.css`:

After `.ov .ghost.idle { display: none; }` add:

```css
.ov .hand-ink path { stroke: var(--human); stroke-width: 1.2; opacity: .9; } .ov .hand-ink circle { display: none; }   /* the hand is the pen */
```

After `.hand.press { … }` add:

```css
.hand .marker { display: none; } .hand.draw .marker { display: block; }
/* names: a caption pill on the hand, and one that rides the robot's pen dot */
.tag { position: absolute; font: 700 1.2cqw/1 var(--story); padding: .35cqw .8cqw; border: .25cqw solid var(--ink); border-radius: 999px;
       background: var(--paper); color: var(--ink); pointer-events: none; white-space: nowrap; }
.hand .tag { left: 3.4cqw; top: 5.4cqw; }
#pen-tag { z-index: 4; transform: translate(1cqw, 1cqw); }
/* the turn clock: who is on and their seconds, over a bar that fills across the chip */
.clock { position: relative; overflow: hidden; }
.clock .fill { position: absolute; inset: 0; width: calc(var(--fill, 0) * 100%); background: var(--human); opacity: .25; transition: width .1s linear; }
.clock[data-who="robot"] .fill { background: var(--robot); }
.clock[data-who="paused"] .fill { animation: blink 1s ease-in-out infinite; }
.clock > b, .clock > span { position: relative; }
```

Change the four toy-press rules to their class twins:

```css
button.chip:hover, button.chip.hover { transform: translate(-.15cqw, -.15cqw) rotate(-1deg); box-shadow: .45cqw .45cqw 0 var(--ink); }
button.chip:active, button.chip.active { transform: translate(.15cqw, .15cqw); box-shadow: 0 0 0 var(--ink); }
```

and

```css
.go:hover, .go.hover, .welcome-start:not(:disabled):hover { transform: translate(-.2cqw, -.2cqw) rotate(-1.5deg); box-shadow: .7cqw .7cqw 0 var(--ink); }
.go:active, .go.active, .welcome-start:not(:disabled):active { transform: translate(.3cqw, .3cqw); box-shadow: .1cqw .1cqw 0 var(--ink); }
```

- [ ] **Step 5: Run the tests**

Run: `node --test pagetests/style.test.mjs`
Expected: all pass. If the existing test `buttons are toy presses…` fails on its `.go:hover, .welcome-start…` pattern, update that assertion to `/\.go:hover, \.go\.hover, \.welcome-start:not\(:disabled\):hover \{[^}]*box-shadow: \.7cqw \.7cqw 0 var\(--ink\)/`.

- [ ] **Step 6: Commit**

```bash
git add code/hackathon/duet/static/index.html code/hackathon/duet/static/duet.css code/hackathon/pagetests/style.test.mjs
git commit -m "feat(page): the hand's marker and Visitor tag, the Robot tag, the red trace layer, the clock chip, and class twins for the toy press"
```

---

### Task 6: Wire it in `app.js`; bump assets to `ds9`

**Files:**
- Modify: `code/hackathon/duet/static/js/app.js`
- Modify: `code/hackathon/duet/static/index.html` and every `code/hackathon/duet/static/js/*.js` (`?v=ds8` → `?v=ds9`)
- Modify: `code/hackathon/pagetests/defaults.test.mjs`, `code/hackathon/pagetests/diagnostics.test.mjs`, `code/hackathon/pagetests/style.test.mjs`

- [ ] **Step 1: Write the failing tests**

Append to `code/hackathon/pagetests/defaults.test.mjs`:

```js
test('app.js in replay mode: a red pen for the hand, the Robot tag on the robot pen, cues routed by key, pause and resume routed by state, the clock click', () => {
  const app = read('js/app.js');
  assert.match(app, /import \{ Clock \} from '\.\/clock\.js\?v=ds9';/);
  assert.match(app, /app\.pen = new GhostPen\(\$\('l-hand'\), \$\('handpath'\), \$\('handpen'\)\);/);
  assert.match(app, /new Hand\(\$\('hand'\), \{ stage: \$\('stage'\), targets: handTarget, tracer: app\.pen, toStage: \(p\) => app\.viewer\.boardToStage\(p\), speed: SPEED \}\)/);
  assert.match(app, /app\.clock = new Clock\(\$\('clock'\), \{ who: \$\('clock-who'\), time: \$\('clock-time'\) \}\);/);
  assert.match(app, /\$\('clock'\)\.onclick = \(\) => sendCommand\(app\.state && app\.state\.state === 'paused' \? 'resume' : 'pause'\);/);
  assert.match(app, /name\.startsWith\('row:'\) \? document\.querySelectorAll\('#artist-menu button'\)\[\+name\.slice\(4\)\]/);
  assert.match(app, /cue: \(c\) => \{ if \(c\.hand\) app\.hand\.run\(c\); if \(c\.clock\) app\.clock\.start\(\{ who: c\.clock, ms: c\.ms \}\); \}/);
  assert.match(app, /const wasPaused = !!\(app\.state && app\.state\.state === 'paused'\);/);
  assert.match(app, /if \(REPLAY_URL\) replayState\(msg, wasPaused\); else if \(\['human_turn', 'finished', 'paused', 'idle'\]\.includes\(msg\.state\)\) app\.ghost\.stop\(\);/);
  const fn = app.slice(app.indexOf('function replayState'), app.indexOf('\n}', app.indexOf('function replayState')));
  assert.match(fn, /if \(msg\.state === 'paused'\) \{ app\.hand\.pause\(\); app\.ghost\.pause\(\); app\.clock\.pause\(\); return; \}/);
  assert.match(fn, /if \(wasPaused\) \{ app\.hand\.resume\(\); app\.ghost\.resume\(\); app\.clock\.resume\(\); return; \}/);
  assert.match(fn, /if \(msg\.state !== 'human_turn'\) app\.hand\.cancel\(\);/);
  assert.match(fn, /if \(\['look', 'finish', 'finished', 'idle'\]\.includes\(msg\.state\)\) app\.clock\.stop\(\);/);
  assert.match(fn, /app\.ghost\.play\(app\.plan\.polylines, \{ durationMs: app\.replay\.drawMs\(app\.plan\.polylines\.length\), onMove: placeTag \}\)/);
  assert.match(app, /const placeTag = \(p\) => \{[^\n]*boardToStage\(p\)[^\n]*classList\.toggle\('hidden', !q\)/);
  assert.ok(!/\?v=ds8/.test(app), 'assets at v=ds9');
});
```

In `code/hackathon/pagetests/style.test.mjs` change `assert.ok(!/\?v=ds7/.test(h), 'the page moved to v=ds8 with the hand');` to `assert.ok(!/\?v=ds8/.test(h), 'the page moved to v=ds9 with the drawing hand');`. In the earlier defaults test change `assert.match(app, /import \{ Hand \} from '\.\/hand\.js\?v=ds8';/);` to `ds9` and its `assert.ok(!/\?v=ds7/.test(app), 'assets at v=ds8');` to `assert.ok(!/\?v=ds8/.test(app), 'assets at v=ds9');`; also replace the old `cue: (c) => app.hand && app.hand.run(c)` assertion there with `assert.match(app, /new Player\(replay, feed, \{ speed: SPEED, cue: \(c\) => \{/);`, the old `if \(app\.hand && msg\.state !== 'human_turn'\) app\.hand\.cancel\(\);` assertion with `assert.match(app, /function replayState\(msg, wasPaused\)/);`, and the old `if \(REPLAY_URL\) app\.hand = new Hand\(…speed: SPEED \}\);` assertion with `assert.match(app, /if \(REPLAY_URL\) \{\n\s*app\.pen = new GhostPen/);`, since the hand is now built inside a replay-only block. In `code/hackathon/pagetests/diagnostics.test.mjs` replace every `ds8` with `ds9` (the test title and the four patterns).

- [ ] **Step 2: Run the tests to see them fail**

Run: `node --test pagetests/defaults.test.mjs pagetests/style.test.mjs pagetests/diagnostics.test.mjs`
Expected: the version and wiring assertions FAIL.

- [ ] **Step 3: Bump the version**

From `code/hackathon`:

```bash
sed -i '' 's/?v=ds8/?v=ds9/g' duet/static/index.html duet/static/js/*.js
grep -rn 'v=ds8' duet/static || echo "no ds8 left"
```

Expected: `no ds8 left`. (`hand.js`, `replay.js`, and `preview.js` already import at `ds9` from Tasks 1 to 3.)

- [ ] **Step 4: Wire `app.js`**

In `code/hackathon/duet/static/js/app.js`:

Add after the `Hand` import:

```js
import { Clock } from './clock.js?v=ds9';
```

In the `app` object change `feed: null, replay: null, hand: null,` to:

```js
  feed: null, replay: null, hand: null, pen: null, clock: null,
```

Replace the `case 'state':` block in `handle` (from `case 'state':` through its `break;`) with:

```js
    case 'state': {
      const wasPaused = !!(app.state && app.state.state === 'paused');
      if (msg.session && app.session && msg.session !== app.session) { startSession(); msg.fresh = true; }   // a new piece: forget the last one's strokes, and tell the listeners
      if (msg.session) app.session = msg.session;
      app.state = msg;
      if (REPLAY_URL) replayState(msg, wasPaused); else if (['human_turn', 'finished', 'paused', 'idle'].includes(msg.state)) app.ghost.stop();
      if (msg.state === 'finished') archivePlan();                                        // the signature joins the finished vector
      if (msg.session && msg.turn > 0) backfillPlans(msg.session, msg.turn);
      break;
    }
```

Add before `function handle(msg) {`:

```js
/** The Robot tag rides the robot pen's dot: a board point places it, null hides it. */
const placeTag = (p) => { const tag = $('pen-tag'), q = p && app.viewer.boardToStage(p); tag.classList.toggle('hidden', !q); if (q) { tag.style.left = `${q[0]}px`; tag.style.top = `${q[1]}px`; } };

/** Replay: the hand, the two pens, and the clock follow the state. A pause holds them where they are and the
 *  first state after it resumes them; a resumed robot_draw keeps its trace instead of starting it again. */
function replayState(msg, wasPaused) {
  if (msg.state === 'paused') { app.hand.pause(); app.ghost.pause(); app.clock.pause(); return; }
  if (wasPaused) { app.hand.resume(); app.ghost.resume(); app.clock.resume(); return; }
  if (msg.state !== 'human_turn') app.hand.cancel();                                    // the visitor's part is over
  if (['human_turn', 'finished', 'idle'].includes(msg.state)) app.ghost.stop();
  if (['look', 'finish', 'finished', 'idle'].includes(msg.state)) app.clock.stop();
  if (msg.state === 'robot_draw' && app.plan && app.replay) app.ghost.play(app.plan.polylines, { durationMs: app.replay.drawMs(app.plan.polylines.length), onMove: placeTag });   // the ghost pen is the arm
}
```

In `startReplay` change the Player line to:

```js
    app.replay = new Player(replay, feed, { speed: SPEED, cue: (c) => { if (c.hand) app.hand.run(c); if (c.clock) app.clock.start({ who: c.clock, ms: c.ms }); } });
```

In `boot()` replace the `handTarget` and `app.hand` lines with:

```js
  const handTarget = (name, cue) => (name === 'picker' ? $('artist-btn') : name === 'go' ? $('go')
    : name.startsWith('row:') ? document.querySelectorAll('#artist-menu button')[+name.slice(4)]
    : document.querySelector(`#artist-menu button[data-v="${CSS.escape(cue.artist || '')}"]`));
  if (REPLAY_URL) {
    app.pen = new GhostPen($('l-hand'), $('handpath'), $('handpen'));
    app.hand = new Hand($('hand'), { stage: $('stage'), targets: handTarget, tracer: app.pen, toStage: (p) => app.viewer.boardToStage(p), speed: SPEED });
    app.clock = new Clock($('clock'), { who: $('clock-who'), time: $('clock-time') });
    $('clock').onclick = () => sendCommand(app.state && app.state.state === 'paused' ? 'resume' : 'pause');
  }
```

`GhostPen` is already imported. The `send()` guard `if (msg.type === 'restart' && app.hand) app.hand.cancel();` stays.

- [ ] **Step 5: Run all the tests**

Run: `node --test 'pagetests/*.test.mjs'`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add code/hackathon/duet/static code/hackathon/pagetests
git commit -m "feat(page): the demo's hand draws with a red pen and wears Visitor, the robot dot wears Robot, the turn clock counts each half and pauses the piece; assets at v=ds9"
```

---

### Task 7: Rebuild the site and walk the demo

**Files:**
- Modify: `site/demo/**` (generated)

- [ ] **Step 1: Rebuild**

From the repository root:

```bash
/Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/code/hackathon/.venv/bin/python site/build.py --session 20260919-151119 --sessions /Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/code/hackathon/sessions
git diff --stat site/demo/replay.json
```

Expected: `site written to …: session 20260919-151119, 10 turns, …` and an empty diff for `replay.json`.

- [ ] **Step 2: Walk the demo**

With the `showcase` server on port 8090 (`preview_start` name `showcase` from the main checkout's launch config), open `http://localhost:8090/demo/` in the browser pane, and after each check read the console for errors:

1. Press Start. Within about a second the hand appears over the board with the red marker and the "Visitor" pill, a red line grows along the first mark, and the hand's fingertip rides its end. Screenshot it mid-stroke. The clock chip reads `Visitor` with the seconds counting and a red bar filling.
2. The hand reaches the picker: it lifts (translate and larger shadow, check with `getComputedStyle($('artist-btn')).transform` not `none` while `#artist-btn.hover`), squashes, and the menu opens on the release. The hand steps down the rows; each row on the way carries `hover` for a beat (poll `#artist-menu button.hover` every 50 ms and collect the `data-v` values: `abstract` then `mimic`). Screenshot with a row lifted.
3. On the Mimic press the label reads `as Mimic ▾`; the hand lifts and squashes Go; the state moves to `Let me look…` and the red trace is gone (`#handpath` has an empty `d`, `#l-hand` carries `idle`). The clock now reads `Robot` with a green bar.
4. During `My turn! Hands off, please` the "Robot" pill sits beside the moving dot (`#pen-tag` not hidden, its `left`/`top` changing between two reads a second apart). It hides when the trace ends.
5. Click the clock chip while the robot draws: the state chip reads `Paused`, the clock reads `Paused` with frozen seconds and a blinking bar, the dot's `cx` stops changing, the tag stays. Click again: everything moves on and the trace finishes without restarting (the `d` of `#ghostpath` keeps growing from where it was, never shrinks).
6. On the next human turn click the clock while the hand is gliding or drawing: the hand stops where it is, the marker stays out if it was drawing, the red line stops growing. Click again: it continues and finishes the turn.
7. `?speed=2`: the whole thing runs twice as fast, the clock totals halve, the hand still lands its presses.
8. `read_console_messages` with `onlyErrors`: none.

- [ ] **Step 3: Commit the built site**

```bash
git add site/demo
git commit -m "chore(site): rebuild the demo with the drawing hand, the names, and the turn clock"
```

---

## Self-review

- **Spec coverage.** §2 cues: Task 2. §3 plan and runner: Task 1. §4 CSS twins: Task 5. §5 the red pen, `GhostPen` changes, the marker: Tasks 3, 5, 6. §6 tags: Tasks 5, 6. §7 clock: Tasks 4, 5, 6. §8 pause: Tasks 1, 3, 4, 6. §9 versions and site: Tasks 6, 7. §10 tests: each task carries its own; the walk is Task 7.
- **Names.** `traceMs`, `plan`, `planMs`, `HAND` (Task 1) are what Task 2 imports (`planMs`) and Task 6 relies on (`Hand` options `tracer`, `toStage`, `timers`, `now`). `GhostPen` options `raf`, `caf`, `now` and methods `pause`, `resume`, `onMove` (Task 3) match Task 1's tracer contract and Task 6's calls. `Clock` options `who`, `time`, `timers`, `now` and methods `start`, `render`, `pause`, `resume`, `stop` (Task 4) match Task 6. Element ids `l-hand`, `handpath`, `handpen`, `pen-tag`, `clock`, `clock-who`, `clock-time` (Task 5) match Task 6 and the tests.
- **Import cycle.** `replay.js` imports `hand.js`; `hand.js` imports only `geometry.js`. No cycle.
- **The press's click on the release.** The parent plan's runner clicked at once; Task 1 changes that, and Task 1's tests pin the new order. The rules for a menu a visitor opened or closed still hold because `press` checks the rows at the moment of the press.
