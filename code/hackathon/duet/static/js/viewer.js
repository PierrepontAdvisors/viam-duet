/** The picture layer: the camera frame (live or a saved one), a turn photo projected onto the board,
 *  the overlay SVG registered through the calibration, the clean-board mask, and the crop zoom. */
import { homography, applyH, matrix3d, boardOrder, containRect, cropTransform, insetMaskPath, fitInverse, BOARD_MM } from './geometry.js?v=ds10';

const SVG = 'http://www.w3.org/2000/svg';
const BOARD_RECT = [[0, 0], [BOARD_MM[0], 0], [BOARD_MM[0], BOARD_MM[1]], [0, BOARD_MM[1]]];

/** Replace a group's children with one <path> per polyline; `cls(i)` may return a class name. */
export function drawPolylines(group, polylines, cls = () => '') {
  group.replaceChildren();
  polylines.forEach((pl, i) => {
    if (pl.length < 2) return;
    const p = document.createElementNS(SVG, 'path');
    p.setAttribute('d', 'M' + pl.map(([x, y]) => `${x.toFixed(2)} ${y.toFixed(2)}`).join(' L'));
    const c = cls(i); if (c) p.setAttribute('class', c);
    group.appendChild(p);
  });
}

export class Viewer {
  constructor(el) {
    this.el = el;                     // { stage, pic, base, photo, ov, fit, mask, maskpath, ink, robot, done }
    this.calib = null; this.crop = false; this.live = true; this.streamUrl = null; this.h = null;
    this.onRegister = null;           // called after every registration, for the bubble placement
    el.base.addEventListener('load', () => this.register());
    el.base.addEventListener('error', () => this.retryStream());
    new ResizeObserver(() => this.register()).observe(el.stage);
  }

  setCalib(calib) {
    this.calib = calib;
    this.el.fit.setAttribute('transform', fitInverse(calib.cam_to_robot));   // robot mm -> camera mm
    this.register();
  }

  setStream(url) { this.streamUrl = url; this.showLive(); }

  showLive() {
    this.live = true;
    this.el.photo.classList.add('hidden');
    if (this.streamUrl && this.el.base.dataset.src !== this.streamUrl) { this.el.base.dataset.src = this.streamUrl; this.el.base.src = this.streamUrl; }
  }

  /** A saved turn: the raw frame when the recorder kept one, else the warped photo projected onto the board. */
  showShot(shot) {
    this.live = false;
    if (shot.frame_url) {
      this.el.photo.classList.add('hidden');
      if (this.el.base.dataset.src !== shot.frame_url) { this.el.base.dataset.src = shot.frame_url; this.el.base.src = shot.frame_url; }
    } else {
      if (this.el.photo.dataset.src !== shot.url) { this.el.photo.dataset.src = shot.url; this.el.photo.src = shot.url; }
      this.el.photo.classList.remove('hidden');
    }
  }

  retryStream() {
    if (!this.live || !this.streamUrl) return;
    setTimeout(() => { if (this.live) this.el.base.src = `${this.streamUrl}${this.streamUrl.includes('?') ? '&' : '?'}t=${Date.now()}`; }, 1000);
  }

  setCrop(on) { this.crop = on; document.body.classList.toggle('crop', on); this.register(); }

  setInk(polylines) { drawPolylines(this.el.ink, polylines); }

  /** Robot strokes from earlier turns of this session, always solid. */
  setDone(polylines) { drawPolylines(this.el.done, polylines); }

  /** Strokes up to and including `done` are drawn solid, the rest dashed. */
  setPlan(polylines, done) { drawPolylines(this.el.robot, polylines, i => (i <= done ? '' : 'queued')); }

  register() {
    const { stage, pic, ov, photo, mask, maskpath } = this.el;
    if (!this.calib) return;
    const W = stage.clientWidth, H = stage.clientHeight;
    if (!W || !H) return;
    const [iw, ih] = this.calib.image_size;
    const { s, ox, oy } = containRect(W, H, iw, ih);
    const quad = boardOrder(this.calib.marks_image, this.calib.board_tl_index).map(([x, y]) => [x * s + ox, y * s + oy]);
    const h = homography(BOARD_RECT, quad), m = matrix3d(h);
    ov.style.transform = m; photo.style.transform = m;
    mask.setAttribute('viewBox', `0 0 ${W} ${H}`); maskpath.setAttribute('d', insetMaskPath(h, W, H));
    let z = 1, tx = 0, ty = 0;
    if (this.crop) ({ z, tx, ty } = cropTransform(quad, W, H));
    pic.style.transform = this.crop ? `translate(${tx}px, ${ty}px) scale(${z})` : '';
    Object.assign(this, { h, z, tx, ty, W, H, quadStage: quad.map(([x, y]) => [z * x + tx, z * y + ty]) });
    if (this.onRegister) this.onRegister();
  }

  /** Board millimeters to stage pixels, crop included. Null before the first calibration. */
  boardToStage(p) {
    if (!this.h) return null;
    const [x, y] = applyH(this.h, p);
    return [this.z * x + this.tx, this.z * y + this.ty];
  }
}
