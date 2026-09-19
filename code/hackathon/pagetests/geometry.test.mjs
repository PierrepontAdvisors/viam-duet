import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  solve, homography, applyH, matrix3d, boardOrder, containRect, cropTransform,
  insetMaskPath, centroid, bubblePosition, fitInverse, polylineLength, pointAlong,
} from '../duet/static/js/geometry.js';

// tonight's calibration.json, verbatim
const MARKS = [[369.8368835449219, 175.6464385986328], [859.6172485351562, 178.4642791748047],
               [858.4447021484375, 524.3256225585938], [379.13238525390625, 530.5430297851562]];
const TL = 3;
const close = (a, b, eps = 1e-6) => assert.ok(Math.abs(a - b) < eps, `${a} vs ${b}`);

test('solve inverts a small linear system', () => {
  const x = solve([[2, 1], [1, 3]], [3, 5]);
  close(x[0], 0.8); close(x[1], 1.4);
});

test('boardOrder follows vision.board_quad: tl is the tape at board_tl_index, tr its nearer neighbor', () => {
  const [tl, tr, br, bl] = boardOrder(MARKS, TL);
  assert.deepEqual(tl, MARKS[3]); assert.deepEqual(tr, MARKS[0]);
  assert.deepEqual(br, MARKS[1]); assert.deepEqual(bl, MARKS[2]);
});

test('homography maps the four source corners exactly onto the destination quad', () => {
  const src = [[0, 0], [176, 0], [176, 240], [0, 240]];
  const dst = boardOrder(MARKS, TL);
  const h = homography(src, dst);
  src.forEach((p, i) => { const q = applyH(h, p); close(q[0], dst[i][0], 1e-4); close(q[1], dst[i][1], 1e-4); });
  const mid = applyH(h, [88, 120]);
  assert.ok(mid[0] > 600 && mid[0] < 630 && mid[1] > 340 && mid[1] < 365);
});

test('matrix3d lays the homography out column-major with w in the fourth row', () => {
  const h = [1, 2, 3, 4, 5, 6, 7, 8];
  assert.equal(matrix3d(h), 'matrix3d(1,4,0,7, 2,5,0,8, 0,0,1,0, 3,6,0,1)');
});

test('containRect centers a 16:9 image in a wider and in a taller stage', () => {
  assert.deepEqual(containRect(1600, 900, 1280, 720), { s: 1.25, ox: 0, oy: 0 });
  assert.deepEqual(containRect(1280, 1000, 1280, 720), { s: 1, ox: 0, oy: 140 });
  assert.deepEqual(containRect(1000, 720, 1280, 720), { s: 0.78125, ox: 0, oy: 78.75 });
});

test('cropTransform scales the quad box to 90 percent of the stage and centers it', () => {
  const quad = [[100, 100], [300, 100], [300, 200], [100, 200]];
  const { z, tx, ty } = cropTransform(quad, 800, 450);
  close(z, Math.min(800 * 0.9 / 200, 450 * 0.9 / 100));
  close(z * 200 + tx, 400); close(z * 150 + ty, 225);
});

test('insetMaskPath is a huge rect with an even-odd hole at the mapped inset', () => {
  const h = homography([[0, 0], [176, 0], [176, 240], [0, 240]], [[0, 0], [176, 0], [176, 240], [0, 240]]);
  const d = insetMaskPath(h, 800, 450);
  assert.ok(d.startsWith('M-800 -450 H1600 V900 H-800 Z M'));
  assert.ok(d.includes('15.0 15.0') && d.includes('161.0 225.0'));
});

test('centroid averages every point of every polyline and defaults to the board center', () => {
  assert.deepEqual(centroid([[[0, 0], [10, 0]], [[10, 10]]]), [20 / 3, 10 / 3]);
  assert.deepEqual(centroid([]), [88, 120]);
});

test('bubblePosition sits on the nearer side of the board at the anchor height, clamped', () => {
  const quad = [[300, 100], [500, 100], [500, 350], [300, 350]];
  const opts = { W: 800, H: 450, bw: 190, bh: 80, topMin: 30, floor: 430 };
  const left = bubblePosition([350, 200], quad, opts);
  assert.equal(left.onRight, false); close(left.x, 300 - 0.036 * 800 - 190); close(left.y, 160);
  const right = bubblePosition([480, 20], quad, opts);
  assert.equal(right.onRight, true); close(right.x, 500 + 0.036 * 800); close(right.y, 30);
  const low = bubblePosition([350, 440], quad, opts);
  close(low.y, 430 - 80);
});

test('fitInverse turns cam_to_robot into the SVG matrix that maps robot mm back to camera mm', () => {
  const s = fitInverse({ ax: 2, bx: 4, ay: 4, by: 8 });
  assert.equal(s, 'matrix(0.5 0 0 0.25 -2 -2)');
});

test('polylineLength and pointAlong walk a path in millimeters', () => {
  const pls = [[[0, 0], [10, 0]], [[0, 10], [0, 20]]];
  close(polylineLength(pls), 20);
  assert.deepEqual(pointAlong(pls, 5), { p: [5, 0], stroke: 0 });
  assert.deepEqual(pointAlong(pls, 15), { p: [0, 15], stroke: 1 });
  assert.deepEqual(pointAlong(pls, 99), { p: [0, 20], stroke: 1 });
});
