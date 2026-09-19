/** The ghost pen: traces the whole plan once at a constant speed, ahead of the real arm. */
import { polylineLength, pointAlong, tracePath } from './geometry.js';

export class GhostPen {
  constructor(group, path, pen, { mmPerSec = 60 } = {}) {
    this.group = group; this.path = path; this.pen = pen; this.speed = mmPerSec; this.raf = null;
    this.group.classList.add('idle');
  }

  play(polylines) {
    this.stop();
    const total = polylineLength(polylines);
    if (!total) return;
    this.group.classList.remove('idle');
    const start = performance.now();
    const tick = (now) => {
      const dist = Math.min(total, ((now - start) / 1000) * this.speed);
      const { p } = pointAlong(polylines, dist);
      this.path.setAttribute('d', tracePath(polylines, dist));
      this.pen.setAttribute('cx', p[0].toFixed(2)); this.pen.setAttribute('cy', p[1].toFixed(2));
      if (dist < total) this.raf = requestAnimationFrame(tick);
      else { this.raf = null; this.pen.style.display = 'none'; }
    };
    this.pen.style.display = '';
    this.raf = requestAnimationFrame(tick);
  }

  stop() {
    if (this.raf) cancelAnimationFrame(this.raf);
    this.raf = null;
    this.group.classList.add('idle');
    this.path.setAttribute('d', '');
  }
}
