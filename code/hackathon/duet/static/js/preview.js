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
