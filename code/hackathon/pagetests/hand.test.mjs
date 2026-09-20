import { test } from 'node:test';
import assert from 'node:assert/strict';
import { plan, Hand, HAND } from '../duet/static/js/hand.js';

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
const tick = (ms = 2) => new Promise(r => setTimeout(r, ms));

test('plan: a pick settles, opens the picker, presses the row, holds, presses Go; a Go cue goes straight to Go; speed divides', () => {
  const pick = plan({ hand: 'pick', artist: 'mimic' });
  assert.deepEqual(pick, [{ wait: HAND.settle }, { glide: 'picker', ms: HAND.glide }, { press: 'picker', ms: HAND.press },
                          { glide: 'row', ms: HAND.glide }, { press: 'row', ms: HAND.press }, { wait: HAND.hold },
                          { glide: 'go', ms: HAND.glide }, { press: 'go', ms: HAND.press }]);
  assert.deepEqual(plan({ hand: 'go' }), [{ wait: HAND.settleGo }, { glide: 'go', ms: HAND.glide }, { press: 'go', ms: HAND.press }]);
  assert.deepEqual(plan({ hand: 'pick', artist: 'mimic' }, 2)[1], { glide: 'picker', ms: HAND.glide / 2 });
  assert.equal(plan({ hand: 'go' }, 0)[0].wait, HAND.settleGo);         // a zero speed is taken as 1
});

function rig({ menuOpen = false, pickerHidden = false, goHidden = false } = {}) {
  const stage = fake('stage', { rect: { left: 100, top: 50, width: 800, height: 450 } });
  const picker = fake('picker', { hidden: pickerHidden, rect: { left: 120, top: 100, width: 60, height: 20 } });
  const row = fake('row', { hidden: !menuOpen, rect: { left: 120, top: 130, width: 200, height: 20 } });
  const go = fake('go', { hidden: goHidden, rect: { left: 300, top: 100, width: 80, height: 30 } });
  picker.click = () => { picker.clicks += 1; row.classList[row.offsetParent ? 'add' : 'remove']('hidden'); };   // toggles the menu
  row.click = () => { row.clicks += 1; row.classList.add('hidden'); };                                        // a pick closes the menu
  const el = fake('hand', { hidden: true });
  const hand = new Hand(el, { stage, targets: (name) => ({ picker, row, go })[name], speed: 1000 });          // every wait rounds to a millisecond
  return { hand, el, picker, row, go };
}

test('Hand: a pick glides to and presses the picker, the row, then Go, with the fingertip on each centre, then hides', async () => {
  const { hand, el, picker, row, go } = rig();
  hand.run({ hand: 'pick', artist: 'mimic' });
  assert.ok(!el.classList.contains('hidden'), 'the hand shows at once');
  await tick(40);
  assert.deepEqual([picker.clicks, row.clicks, go.clicks], [1, 1, 1]);
  assert.equal(el.style.left, '240px'); assert.equal(el.style.top, '65px');                                   // Go's centre against the stage
  assert.ok(el.classList.contains('hidden'), 'hidden once the plan is done');
});

test('Hand: it presses what it sees: no toggle on a menu a visitor opened, reopen one that closed, skip a hidden target, cancel hides', async () => {
  const open = rig({ menuOpen: true });
  open.hand.run({ hand: 'pick', artist: 'mimic' });
  await tick(40);
  assert.deepEqual([open.picker.clicks, open.row.clicks, open.go.clicks], [0, 1, 1]);
  const closed = rig();
  closed.picker.click = () => { closed.picker.clicks += 1; if (closed.picker.clicks > 1) closed.row.classList.remove('hidden'); };   // a visitor closes the menu right after the first press
  closed.hand.run({ hand: 'pick', artist: 'mimic' });
  await tick(40);
  assert.equal(closed.picker.clicks, 2, 'pressed again to reopen'); assert.equal(closed.row.clicks, 1);
  const browsing = rig({ pickerHidden: true });
  browsing.hand.run({ hand: 'pick', artist: 'mimic' });
  await tick(40);
  assert.deepEqual([browsing.picker.clicks, browsing.row.clicks, browsing.go.clicks], [0, 0, 1]);
  const gone = rig();
  gone.hand.run({ hand: 'go' });
  gone.hand.cancel();
  await tick(40);
  assert.equal(gone.go.clicks, 0); assert.ok(gone.el.classList.contains('hidden'));
});
