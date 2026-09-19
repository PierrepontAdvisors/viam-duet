/** Pure geometry for the Duet page: board millimeters to stage pixels and back. No DOM here. */

export const BOARD_MM = [176, 240];
export const INSET_MM = 15;
export const BOARD_CENTER = [88, 120];

/** Gaussian elimination with partial pivoting. A is n x n, b is n. */
export function solve(A, b) {
  const n = b.length, M = A.map((row, i) => [...row, b[i]]);
  for (let c = 0; c < n; c++) {
    let p = c;
    for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
    [M[c], M[p]] = [M[p], M[c]];
    if (Math.abs(M[c][c]) < 1e-12) throw new Error('singular system');
    for (let r = 0; r < n; r++) {
      if (r === c) continue;
      const f = M[r][c] / M[c][c];
      for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k];
    }
  }
  return M.map((row, i) => row[n] / row[i]);
}

/** The 3x3 homography (as 8 numbers, h33 = 1) taking four source points onto four destination points. */
export function homography(src, dst) {
  const A = [], b = [];
  for (let i = 0; i < 4; i++) {
    const [x, y] = src[i], [u, v] = dst[i];
    A.push([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.push(u);
    A.push([0, 0, 0, x, y, 1, -v * x, -v * y]); b.push(v);
  }
  return solve(A, b);
}

export function applyH(h, [x, y]) {
  const w = h[6] * x + h[7] * y + 1;
  return [(h[0] * x + h[1] * y + h[2]) / w, (h[3] * x + h[4] * y + h[5]) / w];
}

/** CSS matrix3d for a homography: columns are (a,b,0,w) per input axis, z passes through. */
export function matrix3d(h) {
  return `matrix3d(${h[0]},${h[3]},0,${h[6]}, ${h[1]},${h[4]},0,${h[7]}, 0,0,1,0, ${h[2]},${h[5]},0,1)`;
}

/** Same rule as vision.board_quad: tl is the mark at tlIndex, tr its nearer neighbor (the short edge). */
export function boardOrder(marks, tlIndex) {
  const d = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
  const tl = marks[tlIndex], nxt = marks[(tlIndex + 1) % 4], prv = marks[(tlIndex + 3) % 4];
  const [tr, bl] = d(nxt, tl) <= d(prv, tl) ? [nxt, prv] : [prv, nxt];
  return [tl, tr, marks[(tlIndex + 2) % 4], bl];
}

/** Where object-fit: contain puts an iw x ih image inside a W x H box. */
export function containRect(W, H, iw, ih) {
  const s = Math.min(W / iw, H / ih);
  return { s, ox: (W - iw * s) / 2, oy: (H - ih * s) / 2 };
}

/** Zoom and shift that make the quad's bounding box fill `fill` of the stage, centered. */
export function cropTransform(quad, W, H, fill = 0.9) {
  const xs = quad.map(p => p[0]), ys = quad.map(p => p[1]);
  const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
  const z = Math.min(W * fill / (maxX - minX), H * fill / (maxY - minY));
  return { z, tx: W / 2 - z * (minX + maxX) / 2, ty: H / 2 - z * (minY + maxY) / 2 };
}

/** White everywhere except the drawable area: a huge rect with an even-odd hole at the mapped inset. */
export function insetMaskPath(h, W, H, inset = INSET_MM, board = BOARD_MM) {
  const [bw, bh] = board;
  const corners = [[inset, inset], [bw - inset, inset], [bw - inset, bh - inset], [inset, bh - inset]];
  const hole = corners.map(p => applyH(h, p).map(v => v.toFixed(1)).join(' ')).join(' L');
  return `M${-W} ${-H} H${2 * W} V${2 * H} H${-W} Z M${hole} Z`;
}

/** Mean of every point of every polyline; the board center when there are none. */
export function centroid(polylines) {
  const pts = polylines.flat();
  if (!pts.length) return [...BOARD_CENTER];
  return [pts.reduce((s, p) => s + p[0], 0) / pts.length, pts.reduce((s, p) => s + p[1], 0) / pts.length];
}

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

/**
 * Bubble placement on the stage: beside the board on the side nearer to the anchor, centered on the
 * anchor's height, clamped between the chips (topMin) and the floor (panel or stage bottom).
 */
export function bubblePosition([ax, ay], quadStage, { W, H, bw, bh, topMin, floor }) {
  const xs = quadStage.map(p => p[0]), left = Math.min(...xs), right = Math.max(...xs);
  const gap = 0.036 * W, margin = 0.016 * W;
  const onRight = ax > W / 2;
  const x = onRight ? Math.min(right + gap, W - bw - margin) : Math.max(left - gap - bw, margin);
  return { x, y: clamp(ay - bh / 2, topMin, floor - bh), onRight };
}

/** Robot-board mm back to camera-board mm: cam = (robot - b) / a per axis, as an SVG matrix. */
export function fitInverse({ ax, bx, ay, by }) {
  return `matrix(${1 / ax} 0 0 ${1 / ay} ${-bx / ax} ${-by / ay})`;
}

export function polylineLength(polylines) {
  let total = 0;
  for (const pl of polylines) for (let i = 1; i < pl.length; i++) total += Math.hypot(pl[i][0] - pl[i - 1][0], pl[i][1] - pl[i - 1][1]);
  return total;
}

/** The point `dist` millimeters along the concatenated polylines, and which stroke it is in. */
export function pointAlong(polylines, dist) {
  let left = dist, last = { p: [...BOARD_CENTER], stroke: 0 };
  for (let s = 0; s < polylines.length; s++) {
    const pl = polylines[s];
    for (let i = 1; i < pl.length; i++) {
      const [a, b] = [pl[i - 1], pl[i]], seg = Math.hypot(b[0] - a[0], b[1] - a[1]);
      if (left <= seg) { const t = seg ? left / seg : 0; return { p: [a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])], stroke: s }; }
      left -= seg;
    }
    if (pl.length) last = { p: [...pl[pl.length - 1]], stroke: s };
  }
  return last;
}
/** SVG path data for the first `dist` millimeters of the plan: whole strokes, then a partial one. */
export function tracePath(polylines, dist) {
  let left = dist;
  const parts = [];
  for (const pl of polylines) {
    if (pl.length < 2) continue;
    const pts = [pl[0]];
    let cut = false;
    for (let i = 1; i < pl.length && !cut; i++) {
      const a = pl[i - 1], b = pl[i], seg = Math.hypot(b[0] - a[0], b[1] - a[1]);
      if (left >= seg) { pts.push(b); left -= seg; }
      else { const t = seg ? left / seg : 0; pts.push([a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])]); left = 0; cut = true; }
    }
    parts.push('M' + pts.map(([x, y]) => `${x.toFixed(2)} ${y.toFixed(2)}`).join(' L'));
    if (cut || left <= 0) break;
  }
  return parts.join(' ');
}
