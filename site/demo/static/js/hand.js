/** The demo's hand: a cartoon pointer that shows the recorded visitor's part during the human turn: it draws
 *  their mark with a red marker, then presses the page's own buttons the way a finger would, lifting and
 *  squashing them. `traceMs`, `plan`, and `planMs` are pure; `Hand` moves the element and drives the DOM.
 *  Replay mode only. */
import { polylineLength } from './geometry.js?v=ds10';

/** A quarter slower than first built, so every lift, squash, and stroke reads at a glance. */
export const HAND = { glide: 625, hover: 438, press: 250, hold: 625, rollGlide: 150, rollHover: 125, mmPerSec: 56, traceMin: 1500, traceMax: 5000 };

/** How long the hand takes to draw `strokes` (board mm): 56 mm a second, within 1.5 to 5 s, divided by `speed`. */
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
    this.timer = null; this.pending = null; this.paused = false; this.token = 0; this.hovered = null; this.pressed = null; this.drawing = false;
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
    this.el.classList.add('draw'); this.drawing = true;
    // the trace's last frame can land after this step's timer: once the step is over, the pen's points no longer move the hand
    this.tracer.play(strokes, { durationMs: ms, onMove: (p) => { if (!this.drawing) return; const q = p && this.toStage(p); if (q) this.moveToPoint(q[0], q[1]); } });
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
    this.el.classList.remove('press'); this.el.classList.remove('draw'); this.drawing = false;
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
