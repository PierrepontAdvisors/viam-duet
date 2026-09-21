/** The turn clock: a chip that names who is on, counts their seconds, and fills over the half's scripted
 *  time. `formatSeconds` and `fraction` are pure; `Clock` drives the chip. Replay mode only. */

export function formatSeconds(ms) { return `${(Math.max(0, ms) / 1000).toFixed(1)} s`; }

/** How much of the bar to fill: 0 to 1, and full when there is no total to measure against. */
export function fraction(elapsed, total) {
  if (!(total > 0)) return 1;
  return Math.min(1, Math.max(0, elapsed / total));
}

const LABEL = { visitor: 'Human', robot: 'Robot', paused: 'Paused' };
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
