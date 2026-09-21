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
