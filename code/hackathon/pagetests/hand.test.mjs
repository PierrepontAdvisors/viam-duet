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

test('traceMs: 56 mm a second between 1.5 and 5 s, divided by speed, 0 for nothing; every hand timing is a quarter slower than first built', () => {
  assert.equal(traceMs([]), 0); assert.equal(traceMs([LINE]), 1500); assert.equal(traceMs([SQ], 1), 2857);
  assert.equal(traceMs([SQ, SQ, SQ], 1), 5000); assert.equal(traceMs([SQ], 2), 1429);
  assert.deepEqual(HAND, { glide: 625, hover: 438, press: 250, hold: 625, rollGlide: 150, rollHover: 125, mmPerSec: 56, traceMin: 1500, traceMax: 5000 });
});

test('plan: a pick draws, lifts and presses the picker, rolls down the rows to the target, presses it, holds, then lifts and presses Go', () => {
  const p = plan({ hand: 'pick', artist: 'haring', row: 2, draw: [LINE] });
  assert.deepEqual(p, [
    { draw: [LINE], ms: 1500 },
    { glide: 'picker', ms: HAND.glide }, { hover: 'picker', ms: HAND.hover }, { press: 'picker', ms: HAND.press },
    { glide: 'row:0', ms: HAND.rollGlide }, { hover: 'row:0', ms: HAND.rollHover },
    { glide: 'row:1', ms: HAND.rollGlide }, { hover: 'row:1', ms: HAND.rollHover },
    { glide: 'row:2', ms: HAND.rollGlide }, { hover: 'row:2', ms: HAND.hover },
    { press: 'row', ms: HAND.press }, { wait: HAND.hold },
    { glide: 'go', ms: HAND.glide }, { hover: 'go', ms: HAND.hover }, { press: 'go', ms: HAND.press }]);
  assert.deepEqual(plan({ hand: 'go', draw: [] }), [{ glide: 'go', ms: HAND.glide }, { hover: 'go', ms: HAND.hover }, { press: 'go', ms: HAND.press }]);
  const off = plan({ hand: 'pick', artist: 'nobody', row: -1, draw: [] });
  assert.deepEqual(off.slice(3, 5), [{ glide: 'row', ms: HAND.glide }, { hover: 'row', ms: HAND.hover }]);   // no roll: straight to the row by name
  assert.equal(plan({ hand: 'go', draw: [LINE] }, 2)[0].ms, 750);
  assert.equal(planMs({ hand: 'go', draw: [LINE] }), 1500 + HAND.glide + HAND.hover + HAND.press);
  assert.equal(planMs({ hand: 'go', draw: [LINE] }, 2), 750 + Math.round(HAND.glide / 2) + Math.round(HAND.hover / 2) + Math.round(HAND.press / 2));
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
  assert.deepEqual(tracer.calls.at(-1), ['play', [LINE], 1500]);                                   // after the stop that every run begins with
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
