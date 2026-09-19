import { test } from 'node:test';
import assert from 'node:assert/strict';
import { levelsFor, NEUTRAL_LEVELS, CLEAN_LEVELS, svgDocument, pathData } from '../duet/static/js/picture.js';

const close = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) < eps, `${a} vs ${b}`);

test('neutral levels are the identity', () => {
  const { slope, intercept } = levelsFor(NEUTRAL_LEVELS);
  close(slope, 1); close(intercept, 0);
});

test('the clean-board preset reproduces the tuned filter: slope 1.9, intercept -0.38', () => {
  const { slope, intercept } = levelsFor(CLEAN_LEVELS);
  close(slope, 1.9); close(intercept, -0.38);
});

test('contrast pivots around mid gray, brightness shifts, exposure doubles per stop', () => {
  const c = levelsFor({ brightness: 0, contrast: 2, exposure: 0 });
  close(c.slope * 0.5 + c.intercept, 0.5);                       // mid gray stays put
  const b = levelsFor({ brightness: 0.1, contrast: 1, exposure: 0 });
  close(b.slope, 1); close(b.intercept, 0.1);
  const e = levelsFor({ brightness: 0, contrast: 1, exposure: 1 });
  close(e.slope, 2); close(e.intercept, 0);
  const d = levelsFor({});                                       // missing fields mean neutral
  close(d.slope, 1); close(d.intercept, 0);
});

test('pathData writes an SVG path in board millimeters, two decimals', () => {
  assert.equal(pathData([[0, 0], [10.123, 20.456]]), 'M0.00 0.00 L10.12 20.46');
});

test('svgDocument holds the ink and the robot strokes with their colors and widths', () => {
  const svg = svgDocument({ ink: [[[0, 0], [10, 0]]], robot: [[[5, 5], [5, 15]], [[1, 1]]],
    inkColor: '#111111', strokeColor: '#1b8f3a', inkWidth: 1.2, strokeWidth: 2.5 });
  assert.ok(svg.startsWith('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 176 240" width="176mm" height="240mm">'));
  assert.ok(svg.includes('<rect x="0" y="0" width="176" height="240" fill="#fff"/>'));
  assert.ok(svg.includes('<g id="ink" fill="none" stroke="#111111" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">'));
  assert.ok(svg.includes('<path d="M0.00 0.00 L10.00 0.00"/>'));
  assert.ok(svg.includes('<g id="robot" fill="none" stroke="#1b8f3a" stroke-width="2.5"'));
  assert.ok(svg.includes('<path d="M5.00 5.00 L5.00 15.00"/>'));
  assert.equal((svg.match(/<path /g) || []).length, 2, 'a one-point stroke is skipped');
  assert.ok(svg.trimEnd().endsWith('</svg>'));
});

test('svgDocument can leave out the paper and refuses bad colors', () => {
  const svg = svgDocument({ ink: [], robot: [], inkColor: 'red; }<', strokeColor: '#abc', paper: false });
  assert.ok(!svg.includes('<rect'));
  assert.ok(svg.includes('stroke="#111111"') && svg.includes('stroke="#1b8f3a"'), 'defaults replace invalid colors');
});
