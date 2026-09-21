/** Picture adjustments and the vector export. Pure: no DOM here.
 *
 *  The three sliders drive one linear levels map per channel, out = slope * in + intercept:
 *  contrast pivots around mid gray, brightness shifts, exposure multiplies by 2 per stop. */
import { BOARD_MM } from './geometry.js?v=ds9';

export const NEUTRAL_LEVELS = { brightness: 0, contrast: 1, exposure: 0 };
/** Tonight's tuned clean-board look on the whiteboard at the look pose. */
export const CLEAN_LEVELS = { brightness: 0.07, contrast: 1.9, exposure: 0 };

export function levelsFor({ brightness = 0, contrast = 1, exposure = 0 } = {}) {
  const slope = contrast * 2 ** exposure;
  return { slope, intercept: 0.5 - 0.5 * contrast + brightness };
}

const HEX = /^#[0-9a-fA-F]{6}$/;
const DEFAULT_INK = '#111111', DEFAULT_STROKE = '#1b8f3a';
const color = (c, d) => (HEX.test(c || '') ? c : d);
const width = (w, d) => (typeof w === 'number' && Number.isFinite(w) && w > 0 ? w : d);

export function pathData(polyline) {
  return 'M' + polyline.map(([x, y]) => `${x.toFixed(2)} ${y.toFixed(2)}`).join(' L');
}

function group(id, polylines, stroke, strokeWidth) {
  const paths = polylines.filter(pl => pl.length >= 2).map(pl => `  <path d="${pathData(pl)}"/>`);
  return [`<g id="${id}" fill="none" stroke="${stroke}" stroke-width="${strokeWidth}" stroke-linecap="round" stroke-linejoin="round">`, ...paths, '</g>'].join('\n');
}

/** A standalone SVG of the piece: the person's ink and the robot's strokes, in board millimeters. */
export function svgDocument({ ink = [], robot = [], inkColor, strokeColor, inkWidth, strokeWidth, paper = true } = {}) {
  const [w, h] = BOARD_MM;
  const lines = [`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}mm" height="${h}mm">`];
  if (paper) lines.push(`<rect x="0" y="0" width="${w}" height="${h}" fill="#fff"/>`);
  lines.push(group('ink', ink, color(inkColor, DEFAULT_INK), width(inkWidth, 1.2)));
  lines.push(group('robot', robot, color(strokeColor, DEFAULT_STROKE), width(strokeWidth, 1.4)));
  lines.push('</svg>');
  return lines.join('\n') + '\n';
}

const PATH_RE = /<path\b[^>]*\bd="([^"]+)"[^>]*\bstroke="([^"]+)"/g;
const NUM_RE = /-?\d+(?:\.\d+)?/g;

/** A saved plan SVG (`plan-NN.svg`) back into polylines: black paths are the traced human ink,
 *  green paths the robot's strokes, both in robot-board millimeters. One-point paths are dropped. */
export function polylinesFromSvg(text) {
  const ink = [], robot = [];
  for (const m of String(text).matchAll(PATH_RE)) {
    const nums = (m[1].match(NUM_RE) || []).map(Number);
    const pl = [];
    for (let i = 0; i + 1 < nums.length; i += 2) pl.push([nums[i], nums[i + 1]]);
    if (pl.length < 2) continue;
    (m[2] === 'green' || m[2] === '#1b8f3a' ? robot : ink).push(pl);
  }
  return { ink, robot };
}
