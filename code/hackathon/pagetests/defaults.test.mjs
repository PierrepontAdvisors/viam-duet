import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { LIVE_DEFAULTS, DEMO_DEFAULTS, defaultsFor } from '../duet/static/js/ui.js';
import { CLEAN_LEVELS } from '../duet/static/js/picture.js';

const DIR = fileURLToPath(new URL('../duet/static/', import.meta.url));
const read = (name) => readFileSync(DIR + name, 'utf8');

test('the live page keeps its defaults; the demo opens as the 2026-09-20 screenshot: cropped, no ink layer, two greens, wider lines, its levels, sound on', () => {
  assert.deepEqual(LIVE_DEFAULTS, { layers: { robot: true, ink: true, caption: true, chips: true, board: false, clean: true, vector: false },
                                    ink: '#111111', inkWidth: 12, stroke: null, strokeWidth: 14, picture: CLEAN_LEVELS, crop: false, sound: false });
  assert.deepEqual(DEMO_DEFAULTS, { layers: { robot: true, ink: false, caption: true, chips: true, board: false, clean: true, vector: false },
                                    ink: '#37e65b', inkWidth: 38, stroke: '#1fcf4f', strokeWidth: 24,
                                    picture: { brightness: 0, contrast: 0.84, exposure: 1.4 }, crop: true, sound: true });
  assert.equal(defaultsFor(true), DEMO_DEFAULTS); assert.equal(defaultsFor(false), LIVE_DEFAULTS);
});

test('ui.js applies the table it is given: layers, colours, widths, levels, and crop come from it, stored values still win', () => {
  const js = read('js/ui.js');
  assert.match(js, /export function initUI\(app, \{ sendSet, sendCommand, on, replay = false \}\)/);
  assert.match(js, /const D = defaultsFor\(replay\);/);
  assert.match(js, /store\.get\(`layer\.\$\{name\}`, D\.layers\[name\]\)/);
  assert.match(js, /store\.get\('color\.ink', D\.ink\)/);
  assert.match(js, /store\.get\('color\.stroke', D\.stroke\)/);
  assert.match(js, /store\.get\('width\.ink', D\.inkWidth\)/); assert.match(js, /store\.get\('width\.stroke', D\.strokeWidth\)/);
  assert.match(js, /applyPicture\(\{ \.\.\.D\.picture, \.\.\.store\.get\('picture', \{\}\) \}\)/);
  assert.match(js, /if \(D\.crop\) viewer\.setCrop\(true\);/);
  const app = read('js/app.js');
  assert.match(app, /initUI\(app, \{ sendSet, sendCommand, on, replay: !!REPLAY_URL \}\)/);
});

test('app.js wires the hand in replay mode: built at boot, fed cues, cancelled off the human turn and on restart; sound turns on at Start in the demo when nothing is stored or it is remembered on', () => {
  const app = read('js/app.js');
  assert.match(app, /import \{ Hand \} from '\.\/hand\.js\?v=ds9';/);
  assert.match(app, /const SPEED = Number\(new URLSearchParams\(location\.search\)\.get\('speed'\)\) \|\| 1;/);
  assert.match(app, /if \(REPLAY_URL\) \{\n\s*app\.pen = new GhostPen/);
  assert.match(app, /new Player\(replay, feed, \{ speed: SPEED, cue: \(c\) => \{/);
  assert.match(app, /function replayState\(msg, wasPaused\)/);
  assert.match(app, /if \(msg\.type === 'restart' && app\.hand\) app\.hand\.cancel\(\);/);
  assert.match(app, /const wantsSound = stored === null \? defaultsFor\(!!REPLAY_URL\)\.sound : stored;/);
  assert.match(app, /if \(wantsSound && REPLAY_URL\) \$\('start'\)\.addEventListener\('click', \(\) => \{ if \(!app\.sound\.on\) setSound\(true\); \}, \{ once: true \}\)/);
  assert.ok(!/\?v=ds8/.test(app), 'assets at v=ds9');
});

test('app.js in replay mode: a red pen for the hand, the Robot tag on the robot pen, cues routed by key, pause and resume routed by state, the clock click', () => {
  const app = read('js/app.js');
  assert.match(app, /import \{ Clock \} from '\.\/clock\.js\?v=ds9';/);
  assert.match(app, /app\.pen = new GhostPen\(\$\('l-hand'\), \$\('handpath'\), \$\('handpen'\)\);/);
  assert.match(app, /new Hand\(\$\('hand'\), \{ stage: \$\('stage'\), targets: handTarget, tracer: app\.pen, toStage: \(p\) => app\.viewer\.boardToStage\(p\), speed: SPEED \}\)/);
  assert.match(app, /app\.clock = new Clock\(\$\('clock'\), \{ who: \$\('clock-who'\), time: \$\('clock-time'\) \}\);/);
  assert.match(app, /\$\('clock'\)\.onclick = \(\) => sendCommand\(app\.state && app\.state\.state === 'paused' \? 'resume' : 'pause'\);/);
  assert.match(app, /name\.startsWith\('row:'\) \? document\.querySelectorAll\('#artist-menu button'\)\[\+name\.slice\(4\)\]/);
  assert.match(app, /cue: \(c\) => \{ if \(c\.hand\) app\.hand\.run\(c\); if \(c\.clock\) app\.clock\.start\(\{ who: c\.clock, ms: c\.ms \}\); \}/);
  assert.match(app, /const wasPaused = !!\(app\.state && app\.state\.state === 'paused'\);/);
  assert.match(app, /if \(REPLAY_URL\) replayState\(msg, wasPaused\); else if \(\['human_turn', 'finished', 'paused', 'idle'\]\.includes\(msg\.state\)\) app\.ghost\.stop\(\);/);
  const fn = app.slice(app.indexOf('function replayState'), app.indexOf('\n}', app.indexOf('function replayState')));
  assert.match(fn, /if \(msg\.state === 'paused'\) \{ app\.hand\.pause\(\); app\.ghost\.pause\(\); app\.clock\.pause\(\); return; \}/);
  assert.match(fn, /if \(wasPaused\) \{ app\.hand\.resume\(\); app\.ghost\.resume\(\); app\.clock\.resume\(\); return; \}/);
  assert.match(fn, /if \(msg\.state !== 'human_turn'\) app\.hand\.cancel\(\);/);
  assert.match(fn, /if \(\['look', 'finish', 'finished', 'idle'\]\.includes\(msg\.state\)\) app\.clock\.stop\(\);/);
  assert.match(fn, /app\.ghost\.play\(app\.plan\.polylines, \{ durationMs: app\.replay\.drawMs\(app\.plan\.polylines\.length\), onMove: placeTag \}\)/);
  assert.match(app, /const placeTag = \(p\) => \{[^\n]*boardToStage\(p\)[^\n]*classList\.toggle\('hidden', !q\)/);
  assert.ok(!/\?v=ds8/.test(app), 'assets at v=ds9');
});
