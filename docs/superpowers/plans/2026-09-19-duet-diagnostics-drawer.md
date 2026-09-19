# Duet Diagnostics Drawer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A gear-icon corner button with a socket status light opens a drawer that shows everything the Duet page streams, as a message timeline and a log with raw JSON detail. Page only; the backend is untouched.

**Architecture:** A pure module `diag.js` (no DOM) holds the entry constructors, the capped `append`, the per-kind `summarize`, the point-folding `fold`, and the `header` and `timeline` computations. A view module `diagview.js` turns those into the light's classes, the header text, an inline SVG, and a table, redrawing once a second only while the drawer is open. `app.js` records at the socket callbacks before the parser and in `send`; `ui.js` owns open and close, the mutual exclusion with the controls panel, key `G` and `?view=diag`.

**Tech Stack:** Vanilla ES modules served by the FastAPI static mount, CSS with container-query units, Node 24's test runner (`node --test 'pagetests/*.test.mjs'`), the fake runner (`python -m duet.run --fake`) for the live check. Spec: `docs/superpowers/specs/2026-09-19-duet-diagnostics-drawer-design.md`.

All paths below are relative to `code/hackathon/`. Run commands from there. Commit with pathspecs (other sessions work on this branch); the branch is `feat/duet-design`.

---

## File structure

- Create `duet/static/js/diag.js`: entries, `append`, `summarize`, `fold`, `clock`, `header`, `timeline`. Pure.
- Create `duet/static/js/diagview.js`: `initDiagView({ light, summary, svg, tbody })` returning `{ setOpen, setConnected, blink, onEntry }`.
- Create `pagetests/diag.test.mjs` (pure module) and `pagetests/diagnostics.test.mjs` (markup, CSS, wiring).
- Modify `duet/static/index.html`: corner row with light and both buttons; drawer after the panel; `?v=ds6`.
- Modify `duet/static/duet.css`: `.corner`, `.light`, `.gear.icon`, the drawer, the timeline, the log table.
- Modify `duet/static/js/app.js`: `app.diag`, `record`, hooks in `send`, `onopen`, `onclose`, `onmessage`; boot the view.
- Modify `duet/static/js/ui.js`: `toggleDiag`, exclusion in `toggleControls`, bindings, key `G`, `?view=diag`, bubble floor.
- Modify `pagetests/README.md`: key line.

---

### Task 1: entries and the capped append

**Files:**
- Create: `duet/static/js/diag.js`
- Test: `pagetests/diag.test.mjs`

- [ ] **Step 1: Write the failing tests**

```js
// pagetests/diag.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { CAP, LANES, append, frameEntry, sentEntry, socketEntry } from '../duet/static/js/diag.js';

const STATE = JSON.stringify({ type: 'state', state: 'human_turn', turn: 2, exchanges: 5, at_look: true, camera_errors: 3 });

test('frameEntry keeps the raw object, the type and turn, the size and whether the parser took it', () => {
  const e = frameEntry(STATE, { type: 'state' }, 1000, 7);
  assert.equal(e.seq, 7); assert.equal(e.t, 1000); assert.equal(e.dir, 'in'); assert.equal(e.type, 'state');
  assert.equal(e.turn, 2); assert.equal(e.size, STATE.length); assert.equal(e.ok, true); assert.equal(e.raw.camera_errors, 3);
});

test('frameEntry on text that is not JSON keeps the text and marks it dropped', () => {
  const e = frameEntry('hello', null, 1, 1);
  assert.equal(e.type, '?'); assert.equal(e.turn, null); assert.equal(e.ok, false); assert.equal(e.raw, 'hello');
  const arr = frameEntry('[1,2]', null, 1, 2);
  assert.equal(arr.type, '?'); assert.equal(arr.raw, '[1,2]');
});

test('frameEntry on an unknown type or a refused known type is a parsed object that is not ok', () => {
  const u = frameEntry(JSON.stringify({ type: 'oracle' }), null, 1, 1);
  assert.equal(u.type, 'oracle'); assert.equal(u.ok, false); assert.deepEqual(u.raw, { type: 'oracle' });
  const r = frameEntry(JSON.stringify({ type: 'state', state: 7, turn: 'x' }), null, 1, 2);
  assert.equal(r.type, 'state'); assert.equal(r.ok, false); assert.equal(r.turn, null);
});

test('sentEntry and socketEntry shapes', () => {
  const s = sentEntry({ type: 'set', length: 'long' }, 5, 3);
  assert.deepEqual(s, { seq: 3, t: 5, dir: 'out', type: 'set', turn: null, size: '{"type":"set","length":"long"}'.length, ok: true, raw: { type: 'set', length: 'long' } });
  assert.deepEqual(socketEntry('open', null, 6, 4), { seq: 4, t: 6, dir: 'ws', type: 'open', turn: null, size: 0, ok: true, raw: {} });
  assert.deepEqual(socketEntry('close', 1006, 7, 5).raw, { code: 1006 });
});

test('append caps at CAP, keeps order, and never mutates its input', () => {
  assert.equal(CAP, 200);
  let entries = [];
  for (let i = 1; i <= CAP + 5; i++) {
    const next = append(entries, socketEntry('open', null, i, i));
    assert.notEqual(next, entries); assert.equal(entries.length, Math.min(i - 1, CAP));
    entries = next;
  }
  assert.equal(entries.length, CAP); assert.equal(entries[0].seq, 6); assert.equal(entries[CAP - 1].seq, CAP + 5);
});

test('lanes are the fixed kinds with out first', () => {
  assert.deepEqual(LANES, ['out', 'error', 'state', 'progress', 'plan', 'interpretation', 'human', 'shot', 'dock', 'calib', 'video']);
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `node --test pagetests/diag.test.mjs`
Expected: FAIL, "Cannot find module .../diag.js".

- [ ] **Step 3: Write the module**

```js
// duet/static/js/diag.js
/** Diagnostics data: what crossed the socket, summarized for a log and laid out for a timeline. No DOM. */

export const CAP = 200;                 // entries kept
export const WINDOW_MS = 180000;        // the timeline's window
export const TICK_MS = 30000;           // time ticks on the timeline
export const LANES = ['out', 'error', 'state', 'progress', 'plan', 'interpretation', 'human', 'shot', 'dock', 'calib', 'video'];
const KINDS = LANES.filter(k => k !== 'out');   // the message types the page knows

const isNum = (v) => typeof v === 'number' && Number.isFinite(v);
const isPoint = (p) => Array.isArray(p) && p.length >= 2 && p.every(isNum);
const isPolyline = (v) => Array.isArray(v) && v.length > 0 && v.every(isPoint);
const isPolylines = (v) => Array.isArray(v) && v.length > 0 && v.every(isPolyline);
const countPoints = (pls) => (Array.isArray(pls) ? pls.reduce((n, pl) => n + (Array.isArray(pl) ? pl.length : 0), 0) : 0);

function asObject(text) {
  try { const v = JSON.parse(text); return v && typeof v === 'object' && !Array.isArray(v) ? v : null; } catch { return null; }
}

/** An incoming frame: `text` as received, `parsed` the parser's result (null when it refused it). */
export function frameEntry(text, parsed, t, seq) {
  const raw = asObject(text);
  return { seq, t, dir: 'in', type: raw && typeof raw.type === 'string' ? raw.type : '?', turn: raw && isNum(raw.turn) ? raw.turn : null,
           size: text.length, ok: parsed !== null, raw: raw ?? text };
}
export function sentEntry(cmd, t, seq) {
  return { seq, t, dir: 'out', type: typeof cmd.type === 'string' ? cmd.type : '?', turn: null, size: JSON.stringify(cmd).length, ok: true, raw: cmd };
}
export function socketEntry(event, code, t, seq) {
  return { seq, t, dir: 'ws', type: event, turn: null, size: 0, ok: true, raw: event === 'close' ? { code } : {} };
}
/** A new list holding the newest CAP entries, oldest first. */
export function append(entries, entry) {
  const out = [...entries, entry];
  return out.length > CAP ? out.slice(out.length - CAP) : out;
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `node --test pagetests/diag.test.mjs`
Expected: `ℹ pass 6`, `ℹ fail 0`.

- [ ] **Step 5: Commit**

```bash
git add duet/static/js/diag.js pagetests/diag.test.mjs
git commit -m "feat(page): diagnostics entries and the capped append" -- duet/static/js/diag.js pagetests/diag.test.mjs
```

---

### Task 2: summarize, fold, clock

**Files:**
- Modify: `duet/static/js/diag.js`
- Test: `pagetests/diag.test.mjs`

- [ ] **Step 1: Add the failing tests**

Append to `pagetests/diag.test.mjs` (extend the import line to `import { CAP, LANES, append, frameEntry, sentEntry, socketEntry, summarize, fold, clock } from '../duet/static/js/diag.js';`):

```js
const inn = (obj, ok = true) => frameEntry(JSON.stringify(obj), ok ? obj : null, 0, 0);
const PL = [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]];

test('summarize gives one line per kind', () => {
  assert.equal(summarize(inn({ type: 'state', state: 'human_turn', turn: 2, exchanges: 5, at_look: true, error: null })), 'human_turn · turn 2 of 5 · at look');
  assert.equal(summarize(inn({ type: 'state', state: 'paused', turn: 1, exchanges: 5, at_look: false, error: 'recover timed out' })), 'paused · turn 1 of 5 · error: recover timed out');
  assert.equal(summarize(inn({ type: 'progress', stroke: 3, drawn_mm: 412 })), 'stroke 3 · 412 mm');
  assert.equal(summarize(inn({ type: 'interpretation', source: 'claude', latency_s: 6.42, sees: 'A cat.', adds: 'A hat.' })), 'claude 6.4 s · sees "A cat." · adds "A hat."');
  assert.equal(summarize(inn({ type: 'interpretation', source: 'fallback', error: 'timeout' })), 'fallback · timeout');
  assert.equal(summarize(inn({ type: 'plan', polylines: [PL, PL], budget_mm: 1200, color: '#1b8f3a' })), '2 strokes · 10 points · budget 1200 mm · #1b8f3a');
  assert.equal(summarize(inn({ type: 'human', polylines: [PL, PL, PL], new: [PL], found: true })), '3 strokes · 1 new · found');
  assert.equal(summarize(inn({ type: 'human', polylines: [], new: [], found: false })), '0 strokes · 0 new · not found');
  assert.equal(summarize(inn({ type: 'shot', url: '/s/turn-02-human.jpg', who: 'human', turn: 2, frame_url: '/s/f.jpg' })), 'human · turn 2 · +frame');
  assert.equal(summarize(inn({ type: 'error', message: 'board shifted' })), 'board shifted');
  assert.equal(summarize(inn({ type: 'dock', slots: { A: 'green', B: 'empty' }, reseat: ['A'] })), 'slots A:green B:empty · reseat A');
  assert.equal(summarize(inn({ type: 'dock', slots: {}, reseat: [] })), 'slots none');
  assert.equal(summarize(inn({ type: 'calib', marks_image: [[1, 2], [3, 4], [5, 6], [7, 8]], board_tl_index: 1, cam_to_robot: { ax: 0.9673, bx: 8.46, ay: 0.991, by: 8.34 } })), '4 marks · tl 1 · fit ax 0.967 ay 0.991');
  assert.equal(summarize(inn({ type: 'video', url: '/sessions/x/session.mp4' })), '/sessions/x/session.mp4');
});

test('summarize for dropped frames, out rows and socket events', () => {
  assert.equal(summarize(frameEntry('garbage{', null, 0, 0)), 'not JSON: garbage{');
  assert.equal(summarize(inn({ type: 'oracle' }, false)), 'unknown type');
  assert.equal(summarize(inn({ type: 'state', state: 7 }, false)), 'dropped by the parser');
  assert.equal(summarize(sentEntry({ type: 'set', length: 'long' }, 0, 0)), '{"type":"set","length":"long"}');
  assert.equal(summarize(socketEntry('open', null, 0, 0)), 'open');
  assert.equal(summarize(socketEntry('close', 1006, 0, 0)), 'close 1006');
});

test('fold collapses big point lists and keeps small ones and scalars', () => {
  const plan = { type: 'plan', polylines: [PL, PL], budget_mm: 1200 };
  assert.deepEqual(fold(plan), { type: 'plan', polylines: '2 strokes, 10 points', budget_mm: 1200 });
  assert.deepEqual(fold({ new: [PL], polylines: [PL, PL] }), { new: [PL], polylines: '2 strokes, 10 points' });   // five points: under the eight-point rule
  const calib = { marks_image: [[1, 2], [3, 4], [5, 6], [7, 8]], board_mm: [176, 240], cam_to_robot: { ax: 1 } };
  assert.deepEqual(fold(calib), calib);
  assert.deepEqual(fold([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12], [13, 14], [15, 16], [17, 18]]), '1 stroke, 9 points');
  assert.equal(fold('text'), 'text'); assert.equal(fold(null), null); assert.equal(fold(3), 3);
});

test('clock is local HH:MM:SS.t', () => {
  const d = new Date(2026, 8, 19, 14, 5, 9, 712);
  assert.equal(clock(d.getTime()), '14:05:09.7');
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `node --test pagetests/diag.test.mjs`
Expected: FAIL, "does not provide an export named 'summarize'".

- [ ] **Step 3: Add the functions to `diag.js`**

```js
const q = (s, n = 40) => { const v = String(s ?? ''); return `"${v.length > n ? `${v.slice(0, n - 1)}…` : v}"`; };
const fix = (v, d) => (isNum(v) ? v.toFixed(d) : '?');
const count = (v) => (Array.isArray(v) ? v.length : 0);

const SUMMARY = {
  state: (m) => [`${m.state} · turn ${m.turn} of ${m.exchanges ?? '?'}`, m.at_look ? 'at look' : null, m.error ? `error: ${m.error}` : null].filter(Boolean).join(' · '),
  progress: (m) => `stroke ${m.stroke} · ${m.drawn_mm ?? 0} mm`,
  interpretation: (m) => (m.source === 'fallback' ? `fallback · ${m.error || 'outline and ticks around the new mark'}`
    : `claude ${fix(m.latency_s, 1)} s · sees ${q(m.sees)} · adds ${q(m.adds)}`),
  plan: (m) => `${count(m.polylines)} strokes · ${countPoints(m.polylines)} points · budget ${m.budget_mm ?? 0} mm · ${m.color || ''}`,
  human: (m) => `${count(m.polylines)} strokes · ${count(m.new)} new · ${m.found === false ? 'not found' : 'found'}`,
  shot: (m) => `${m.who || '?'} · turn ${m.turn ?? '?'}${m.frame_url ? ' · +frame' : ''}`,
  error: (m) => String(m.message ?? ''),
  dock: (m) => {
    const slots = Object.entries(m.slots || {}).map(([k, v]) => `${k}:${v}`).join(' ') || 'none';
    return `slots ${slots}${Array.isArray(m.reseat) && m.reseat.length ? ` · reseat ${m.reseat.join(', ')}` : ''}`;
  },
  calib: (m) => { const f = m.cam_to_robot || {}; return `${count(m.marks_image)} marks · tl ${m.board_tl_index} · fit ax ${fix(f.ax, 3)} ay ${fix(f.ay, 3)}`; },
  video: (m) => String(m.url ?? ''),
};

/** One line for the log's summary column. */
export function summarize(e) {
  if (e.dir === 'ws') return e.type === 'close' ? `close ${e.raw.code ?? ''}`.trim() : 'open';
  if (e.dir === 'out') return JSON.stringify(e.raw);
  if (typeof e.raw === 'string') return `not JSON: ${e.raw.slice(0, 60)}`;
  if (!KINDS.includes(e.type)) return 'unknown type';
  if (!e.ok) return 'dropped by the parser';
  return SUMMARY[e.type](e.raw);
}

/** A copy for the detail view: lists of points with more than eight points become "N strokes, M points". */
export function fold(v) {
  if (isPolylines(v) && countPoints(v) > 8) return `${v.length} stroke${v.length === 1 ? '' : 's'}, ${countPoints(v)} points`;
  if (isPolyline(v) && v.length > 8) return `1 stroke, ${v.length} points`;
  if (Array.isArray(v)) return v.map(fold);
  if (v && typeof v === 'object') return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, fold(x)]));
  return v;
}

/** Local time as HH:MM:SS.t */
export function clock(t) {
  const d = new Date(t), p = (n) => String(n).padStart(2, '0');
  return `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}.${Math.floor(d.getMilliseconds() / 100)}`;
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `node --test pagetests/diag.test.mjs`
Expected: `ℹ pass 10`, `ℹ fail 0`.

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(page): diagnostics summaries, folded JSON, and the clock" -- duet/static/js/diag.js pagetests/diag.test.mjs
```

---

### Task 3: header and timeline

**Files:**
- Modify: `duet/static/js/diag.js`
- Test: `pagetests/diag.test.mjs`

- [ ] **Step 1: Add the failing tests**

Extend the import to include `header, timeline, WINDOW_MS, TICK_MS` and append:

```js
const at = (t, e) => ({ ...e, t });

test('header counts received, sent, reconnects and dropped, and ages the newest incoming entry', () => {
  const entries = [
    at(0, socketEntry('open', null, 0, 1)), at(10, inn({ type: 'state', state: 'idle', turn: 0 })), at(20, sentEntry({ type: 'pass' }, 0, 3)),
    at(30, socketEntry('close', 1006, 0, 4)), at(40, socketEntry('open', null, 0, 5)), at(50, frameEntry('junk', null, 0, 6)),
    at(60, socketEntry('close', 1006, 0, 7)), at(70, socketEntry('open', null, 0, 8)), at(80, inn({ type: 'progress', stroke: 1 })),
  ];
  assert.deepEqual(header(entries, 1080, true), { connected: true, sinceLastMs: 1000, received: 3, sent: 1, reconnects: 2, dropped: 1 });
  assert.deepEqual(header([], 5, false), { connected: false, sinceLastMs: null, received: 0, sent: 0, reconnects: 0, dropped: 0 });
});

test('timeline places marks as fractions of the window, keeps every lane in order, and drops old entries', () => {
  const now = 1000000, W = WINDOW_MS;
  const entries = [
    at(now - W - 1, inn({ type: 'progress', stroke: 0 })),                    // too old
    at(now - W / 2, inn({ type: 'state', state: 'capture', turn: 1 })),
    at(now, inn({ type: 'progress', stroke: 2 })),
    at(now - W / 4, sentEntry({ type: 'pause' }, 0, 0)),
    at(now - W / 4, inn({ type: 'oracle' }, false)),
    at(now - W / 8, frameEntry('junk', null, 0, 0)),
  ];
  const { lanes } = timeline(entries, now, W, true);
  assert.deepEqual(lanes.map(l => l.type), LANES);
  const lane = (k) => lanes.find(l => l.type === k).marks;
  assert.deepEqual(lane('state'), [{ x: 0.5, label: 'capture' }]);
  assert.deepEqual(lane('progress'), [{ x: 1, label: null }]);
  assert.deepEqual(lane('out'), [{ x: 0.75, label: null }]);
  assert.deepEqual(lane('error'), [{ x: 0.75, label: null }, { x: 0.875, label: null }]);
  assert.deepEqual(lane('plan'), []);
});

test('timeline ticks every TICK_MS with now last', () => {
  const { ticks } = timeline([], 0, WINDOW_MS, true);
  const near = (a, b) => Math.abs(a - b) < 1e-9;
  assert.deepEqual(ticks.map(t => t.label), ['−2:30', '−2:00', '−1:30', '−1:00', '−0:30', 'now']);
  ticks.forEach((t, i) => assert.ok(near(t.x, (i + 1) / 6), `tick ${i} at ${t.x}`));
  assert.equal(TICK_MS, 30000);
});

test('bands: no socket events means the whole window takes the current state', () => {
  assert.deepEqual(timeline([], 100, 100, true).bands, [{ x0: 0, x1: 1, connected: true }]);
  assert.deepEqual(timeline([inn({ type: 'progress', stroke: 1 })], 100, 100, false).bands, [{ x0: 0, x1: 1, connected: false }]);
});

test('bands: a close then an open inside the window reads green, red, green', () => {
  const entries = [at(150, socketEntry('close', 1006, 0, 1)), at(175, socketEntry('open', null, 0, 2))];
  assert.deepEqual(timeline(entries, 200, 100, true).bands, [
    { x0: 0, x1: 0.5, connected: true }, { x0: 0.5, x1: 0.75, connected: false }, { x0: 0.75, x1: 1, connected: true },
  ]);
});

test('bands: still disconnected runs red to the right edge; events before the window set the opening state', () => {
  const entries = [at(50, socketEntry('open', null, 0, 1)), at(180, socketEntry('close', 1006, 0, 2))];
  assert.deepEqual(timeline(entries, 200, 100, false).bands, [{ x0: 0, x1: 0.8, connected: true }, { x0: 0.8, x1: 1, connected: false }]);
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `node --test pagetests/diag.test.mjs`
Expected: FAIL, "does not provide an export named 'header'".

- [ ] **Step 3: Add the functions to `diag.js`**

```js
/** The drawer's summary numbers. */
export function header(entries, now, connected) {
  const ins = entries.filter(e => e.dir === 'in');
  const opens = entries.filter(e => e.dir === 'ws' && e.type === 'open').length;
  return { connected, sinceLastMs: ins.length ? now - ins[ins.length - 1].t : null, received: ins.length,
           sent: entries.filter(e => e.dir === 'out').length, reconnects: Math.max(0, opens - 1), dropped: ins.filter(e => !e.ok).length };
}

/** Connected and disconnected stretches across the window, from the socket events in time order. The state
 *  before the first known event is the opposite of that event; with no events the window takes `connected`. */
function socketBands(entries, now, windowMs, connected) {
  const events = entries.filter(e => e.dir === 'ws' && e.t <= now).map(e => ({ t: e.t, connected: e.type === 'open' }));
  if (!events.length) return [{ x0: 0, x1: 1, connected }];
  const start = now - windowMs, frac = (t) => (t - start) / windowMs;
  let state = !events[0].connected, from = start;
  const out = [];
  for (const ev of events) {
    if (ev.t <= start) { state = ev.connected; continue; }
    out.push({ x0: frac(from), x1: frac(ev.t), connected: state });
    from = ev.t; state = ev.connected;
  }
  out.push({ x0: frac(from), x1: 1, connected: state });
  return out.filter(b => b.x1 > b.x0);
}

/** Lanes, socket bands and time ticks for the timeline; every x is a fraction of the window, now at 1. */
export function timeline(entries, now, windowMs, connected) {
  const lanes = LANES.map(type => ({ type, marks: [] }));
  const lane = Object.fromEntries(lanes.map(l => [l.type, l]));
  for (const e of entries) {
    if (e.dir === 'ws' || e.t > now || now - e.t > windowMs) continue;
    const target = e.dir === 'out' ? 'out' : (e.ok && e.type in lane ? e.type : 'error');
    lane[target].marks.push({ x: 1 - (now - e.t) / windowMs, label: e.dir === 'in' && e.ok && e.type === 'state' ? e.raw.state : null });
  }
  const ticks = [];
  for (let back = windowMs - TICK_MS; back >= TICK_MS; back -= TICK_MS) {
    ticks.push({ x: 1 - back / windowMs, label: `−${Math.floor(back / 60000)}:${String(Math.floor((back % 60000) / 1000)).padStart(2, '0')}` });
  }
  ticks.push({ x: 1, label: 'now' });
  return { lanes, bands: socketBands(entries, now, windowMs, connected), ticks };
}
```

The marks are pushed onto arrays created inside this call, so the input entries are never mutated.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `node --test pagetests/diag.test.mjs`
Expected: `ℹ pass 16`, `ℹ fail 0`. The tick test compares fractions with a tolerance (see its `near` helper) because `1 - 150000/180000` is not exactly `1/6` in floating point.

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(page): diagnostics header numbers and timeline layout" -- duet/static/js/diag.js pagetests/diag.test.mjs
```

---

### Task 4: markup and styles for the corner row and the drawer

**Files:**
- Modify: `duet/static/index.html` (the gear button line, after the panel's closing `</div>`, every `?v=ds5`)
- Modify: `duet/static/duet.css` (lines 80-82 and new rules after the `.status` rules)
- Test: `pagetests/diagnostics.test.mjs`

- [ ] **Step 1: Write the failing structure tests**

```js
// pagetests/diagnostics.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const DIR = fileURLToPath(new URL('../duet/static/', import.meta.url));
const read = (name) => readFileSync(DIR + name, 'utf8');

test('the corner row holds the light, the gear and Controls, inside the stage', () => {
  const h = read('index.html');
  const i = h.indexOf('<div class="corner"');
  assert.ok(i > h.indexOf('<div class="stage"') && i < h.indexOf('<div class="panel"'), 'corner row before the panel, inside the stage');
  const row = h.slice(i, h.indexOf('</div>', i));
  assert.match(row, /<span class="light" id="light"/);
  assert.match(row, /<button class="gear icon" id="diag-gear" title="Diagnostics \(G\)" aria-label="Diagnostics"[^>]*>\s*<svg viewBox="0 0 24 24" aria-hidden="true">/);
  assert.match(row, /<button class="gear" id="gear" title="Show controls \(C\)"/);
  assert.ok(row.indexOf('id="light"') < row.indexOf('id="diag-gear"') && row.indexOf('id="diag-gear"') < row.indexOf('id="gear"'), 'light, gear, Controls in that order');
});

test('the drawer follows the panel with a header, the fixed-viewBox timeline and a six-column table', () => {
  const h = read('index.html');
  const i = h.indexOf('<section class="diag" id="diag"');
  assert.ok(i > h.indexOf('id="status3"') && i < h.indexOf('<div class="dev-badge">'), 'after the panel, before the dev badge');
  const d = h.slice(i, h.indexOf('</section>', i));
  assert.match(d, /<span class="lbl">Diagnostics<\/span>/);
  assert.match(d, /<span class="diag-summary" id="diag-summary"/);
  assert.match(d, /<button id="diag-hide"[^>]*>Hide<\/button>/);
  assert.match(d, /<svg class="diag-timeline" id="diag-timeline" viewBox="0 0 1000 92"/);
  assert.match(d, /<table class="log">\s*<thead><tr><th>time<\/th><th>dir<\/th><th>type<\/th><th>turn<\/th><th>size<\/th><th>summary<\/th><\/tr><\/thead><tbody id="diag-rows">/);
});

test('every data-el name in the page is unique', () => {
  const names = [...read('index.html').matchAll(/data-el="([^"]+)"/g)].map(m => m[1]);
  const dupes = names.filter((n, i) => names.indexOf(n) !== i);
  assert.deepEqual(dupes, []);
  for (const n of ['corner buttons', 'status light — socket', 'diagnostics toggle button', 'diagnostics drawer', 'diagnostics — summary', 'diagnostics — timeline', 'diagnostics — log', 'hide diagnostics button']) assert.ok(names.includes(n), n);
});

test('styles: the corner row hides under both drawers, the drawer shares the panel layer, the light has three looks', () => {
  const css = read('duet.css');
  assert.match(css, /\.corner \{[^}]*z-index: 6/);
  assert.match(css, /body\.controls \.corner, body\.diag \.corner \{ display: none; \}/);
  assert.ok(!css.includes('body.controls .gear { display: none; }'), 'the old per-button hide is gone');
  assert.match(css, /\.diag \{[^}]*z-index: 5/);
  assert.match(css, /body\.diag \.diag \{ display: flex; \}/);
  assert.match(css, /\.light \{[^}]*background: var\(--red\)/);
  assert.match(css, /\.light\.on \{ background: var\(--green\); \}/);
  assert.match(css, /\.light\.blink \{ background: var\(--yellow\); \}/);
  assert.match(css, /prefers-reduced-motion: reduce\) \{ \.light\.on\.blink \{ background: var\(--green\); \} \}/);
  assert.match(css, /\.diag-timeline \{[^}]*aspect-ratio: 1000 \/ 92/);
});

test('assets are versioned ds6 so open pages fetch the new scripts', () => {
  const h = read('index.html');
  assert.ok(!h.includes('?v=ds5'), 'no ds5 left');
  assert.match(h, /src="\/static\/js\/app\.js\?v=ds6"/);
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `node --test pagetests/diagnostics.test.mjs`
Expected: FAIL on every test (no corner row, no drawer, ds5 present).

- [ ] **Step 3: Edit `index.html`**

Replace the line

```html
  <button class="gear" id="gear" title="Show controls (C)" data-el="controls toggle button">Controls</button>
```

with

```html
  <div class="corner" data-el="corner buttons">
    <span class="light" id="light" title="Socket reconnecting" data-el="status light — socket"></span>
    <button class="gear icon" id="diag-gear" title="Diagnostics (G)" aria-label="Diagnostics" data-el="diagnostics toggle button"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg></button>
    <button class="gear" id="gear" title="Show controls (C)" data-el="controls toggle button">Controls</button>
  </div>
```

After the panel's closing `</div>` (the line after `id="status3"`), before the stage's closing `</div>`, insert:

```html
  <section class="diag" id="diag" data-el="diagnostics drawer">
    <div class="diag-head" data-el="diagnostics — header">
      <span class="lbl">Diagnostics</span>
      <span class="diag-summary" id="diag-summary" data-el="diagnostics — summary"></span>
      <button id="diag-hide" data-el="hide diagnostics button">Hide</button>
    </div>
    <svg class="diag-timeline" id="diag-timeline" viewBox="0 0 1000 92" data-el="diagnostics — timeline"></svg>
    <div class="diag-log" data-el="diagnostics — log">
      <table class="log"><thead><tr><th>time</th><th>dir</th><th>type</th><th>turn</th><th>size</th><th>summary</th></tr></thead><tbody id="diag-rows"></tbody></table>
    </div>
  </section>
```

Replace every `?v=ds5` with `?v=ds6` (four occurrences: three stylesheet links and the script).

- [ ] **Step 4: Edit `duet.css`**

Replace lines 80-82 (the `.gear` position rule, its hover, and `body.controls .gear { display: none; }`) with:

```css
.corner { position: absolute; right: 1.6cqw; bottom: 1.4cqw; z-index: 6; display: flex; gap: .6cqw; align-items: center; }
body.controls .corner, body.diag .corner { display: none; }
.gear { position: relative; z-index: 6; font: 700 1cqw/1 var(--story); letter-spacing: .1em; text-transform: uppercase;
        padding: .5cqw 1cqw; background: var(--paper); color: var(--ink); border: .25cqw solid var(--ink); border-radius: 999px; cursor: pointer; opacity: .8; }
.gear:hover { opacity: 1; }
.gear.icon { padding: .4cqw; display: flex; }
.gear.icon svg { width: 1.4cqw; height: 1.4cqw; display: block; }
.light { width: .9cqw; height: .9cqw; border-radius: 50%; border: .15cqw solid var(--ink); background: var(--red); }
.light.on { background: var(--green); }
.light.blink { background: var(--yellow); }
@media (prefers-reduced-motion: reduce) { .light.on.blink { background: var(--green); } }
```

After the two `.status` rules (line 109), add:

```css

/* diagnostics drawer: everything the page streams, as a timeline and a log; it shares the bottom with the panel */
.diag { position: absolute; left: 0; right: 0; bottom: 0; height: 50%; z-index: 5; display: none; flex-direction: column; gap: .6cqw;
        padding: .8cqw 1.6cqw 1cqw; background: rgba(255,255,255,.94); border-top: var(--frame-stroke) solid var(--ink);
        font-family: var(--mono); color: var(--ink); }
body.diag .diag { display: flex; }
.diag-head { display: flex; gap: 1cqw; align-items: center; height: 2.4cqw; flex: 0 0 auto; }
.diag .lbl { font: 700 .85cqw/1 var(--story); letter-spacing: .12em; text-transform: uppercase; color: var(--ink); }
.diag-summary { flex: 1; font: .85cqw/1.5 var(--mono); color: #555; }
.diag-summary b { color: var(--ink); font-weight: 600; } .diag-summary .err { color: var(--red); font-weight: 700; } .diag-summary .ok { color: var(--green); }
.diag-head button { flex: 0 0 auto; height: 100%; font: 700 .95cqw/1 var(--story); letter-spacing: .04em; text-transform: uppercase; padding: 0 .7cqw;
                    background: transparent; color: var(--ink); border: .2cqw solid var(--ink); border-radius: 999px; cursor: pointer;
                    box-shadow: .18cqw .18cqw 0 var(--ink); transition: transform .12s ease, box-shadow .12s ease; }
.diag-head button:hover { transform: translate(-.12cqw, -.12cqw) rotate(-1deg); box-shadow: .32cqw .32cqw 0 var(--ink); }
.diag-head button:active { transform: translate(.12cqw, .12cqw); box-shadow: 0 0 0 var(--ink); }
.diag-timeline { width: 100%; aspect-ratio: 1000 / 92; flex: 0 0 auto; display: block; }
.diag-timeline text { font: 600 6px var(--mono); fill: var(--ink); }   /* viewBox units */
.diag-timeline text.tick { fill: #777; font-size: 5.5px; } .diag-timeline text.mark { font-size: 5px; }
.diag-timeline line.lane { stroke: rgba(0,0,0,.12); stroke-width: .6; }
.diag-timeline line.tick { stroke: rgba(0,0,0,.15); stroke-width: .6; stroke-dasharray: 2 2; }
.diag-timeline rect.mark { fill: var(--ink); } .diag-timeline rect.mark.err { fill: var(--red); }
.diag-timeline rect.band.ok { fill: var(--green); opacity: .45; } .diag-timeline rect.band.err { fill: var(--red); }
.diag-log { flex: 1 1 auto; min-height: 0; overflow: auto; border-top: .1cqw solid rgba(0,0,0,.15); }
table.log { width: 100%; border-collapse: collapse; table-layout: fixed; font: .8cqw/1.4 var(--mono); color: var(--ink); }
table.log th { position: sticky; top: 0; background: #fff; text-align: left; font-weight: 600; padding: .15cqw .5cqw; color: #555; }
table.log th:nth-child(1) { width: 7cqw; } table.log th:nth-child(2) { width: 3cqw; } table.log th:nth-child(3) { width: 9cqw; }
table.log th:nth-child(4) { width: 3.5cqw; } table.log th:nth-child(5) { width: 4.5cqw; }
table.log td { padding: .1cqw .5cqw; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
table.log tr.row { cursor: pointer; } table.log tr.row:hover td { background: rgba(0,0,0,.04); }
table.log tr.err td { color: var(--red); } table.log tr.out td { background: rgba(255,212,0,.25); } table.log tr.ws td { color: #555; font-style: italic; }
table.log tr.detail td { white-space: normal; }
table.log tr.detail pre { margin: 0 0 .3cqw; font: .72cqw/1.35 var(--mono); white-space: pre-wrap; max-height: 12cqw; overflow: auto;
                          background: #f6f6f6; padding: .4cqw .6cqw; border-radius: .4cqw; }
```

- [ ] **Step 5: Run the structure tests and the whole page suite**

Run: `node --test 'pagetests/*.test.mjs'`
Expected: all pass; `welcome.test.mjs` still finds `.gear {` with `z-index: 6` and `style.test.mjs` still finds the versioned links.

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(page): corner row with the socket light and a gear, and the diagnostics drawer markup and styles" -- duet/static/index.html duet/static/duet.css pagetests/diagnostics.test.mjs
```

---

### Task 5: the view module

**Files:**
- Create: `duet/static/js/diagview.js`
- Test: `pagetests/diagnostics.test.mjs`

- [ ] **Step 1: Add the failing source test**

Append to `pagetests/diagnostics.test.mjs`:

```js
test('diagview redraws the table only on entries, ticks once a second only while open, and escapes every cell', () => {
  const js = read('js/diagview.js');
  assert.match(js, /export function initDiagView\(\{ light, summary, svg, tbody \}\)/);
  assert.match(js, /return \{ setOpen, setConnected, blink, onEntry \};/);
  assert.match(js, /setInterval\(tick, 1000\)/);
  assert.ok(!/setInterval\(renderTable/.test(js), 'the table is not on the clock');
  assert.match(js, /light\.classList\.toggle\('on', onOff\)/);
  assert.match(js, /light\.classList\.add\('blink'\)/);
  assert.match(js, /esc\(summarize\(e\)\)/);
  assert.match(js, /esc\(JSON\.stringify\(fold\(e\.raw\), null, 2\)\)/);
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `node --test pagetests/diagnostics.test.mjs`
Expected: FAIL, "ENOENT ... diagview.js".

- [ ] **Step 3: Write the module**

```js
// duet/static/js/diagview.js
/** The diagnostics drawer's DOM: the status light, the header numbers, the timeline SVG, and the log table.
 *  Redraws once a second while open; the table only when an entry arrives, so it never flickers while read. */
import { WINDOW_MS, summarize, fold, clock, header, timeline } from './diag.js?v=ds6';

const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const VB_W = 1000, VB_H = 92, LABEL_W = 92, BAND_H = 8, TICK_H = 10;   // viewBox units
const BLINK_MS = 120;
const f1 = (n) => n.toFixed(1);
const toggled = (set, v) => { const out = new Set(set); if (out.has(v)) out.delete(v); else out.add(v); return out; };

export function initDiagView({ light, summary, svg, tbody }) {
  const view = { open: false, connected: false, entries: [], expanded: new Set(), timer: null, blinkTimer: null };

  function renderHeader() {
    const h = header(view.entries, Date.now(), view.connected);
    const since = h.sinceLastMs === null ? 'no message yet' : `${(h.sinceLastMs / 1000).toFixed(1)} s since last message`;
    summary.innerHTML = `socket <b class="${h.connected ? 'ok' : 'err'}">${h.connected ? 'connected' : 'reconnecting'}</b> · ${since}`
      + ` · <b>${h.received}</b> received · <b>${h.sent}</b> sent · <b>${h.reconnects}</b> reconnects · <b class="${h.dropped ? 'err' : ''}">${h.dropped}</b> dropped`;
  }

  function renderTimeline() {
    const { lanes, bands, ticks } = timeline(view.entries, Date.now(), WINDOW_MS, view.connected);
    const plotW = VB_W - LABEL_W, laneH = (VB_H - BAND_H - TICK_H) / lanes.length, bandY = VB_H - TICK_H - BAND_H;
    const px = (x) => LABEL_W + x * plotW;
    const parts = [];
    for (const tk of ticks) {
      parts.push(`<line class="tick" x1="${f1(px(tk.x))}" y1="0" x2="${f1(px(tk.x))}" y2="${bandY + BAND_H}"/>`);
      parts.push(`<text class="tick" x="${f1(px(tk.x))}" y="${VB_H - 2}" text-anchor="${tk.x >= 1 ? 'end' : 'middle'}">${esc(tk.label)}</text>`);
    }
    lanes.forEach((lane, i) => {
      const y = i * laneH, base = f1(y + laneH * 0.78);
      parts.push(`<text class="lane" x="0" y="${base}">${esc(lane.type)}</text>`);
      parts.push(`<line class="lane" x1="${LABEL_W}" y1="${f1(y + laneH / 2)}" x2="${VB_W}" y2="${f1(y + laneH / 2)}"/>`);
      for (const m of lane.marks) {
        parts.push(`<rect class="mark${lane.type === 'error' ? ' err' : ''}" x="${f1(px(m.x) - 1)}" y="${f1(y + 1)}" width="2" height="${f1(laneH - 2)}"/>`);
        if (m.label) parts.push(`<text class="mark" x="${f1(px(m.x) + 2.5)}" y="${base}">${esc(m.label)}</text>`);
      }
    });
    for (const b of bands) parts.push(`<rect class="band ${b.connected ? 'ok' : 'err'}" x="${f1(px(b.x0))}" y="${bandY}" width="${f1((b.x1 - b.x0) * plotW)}" height="${BAND_H}"/>`);
    svg.innerHTML = parts.join('');
  }

  function rowHtml(e) {
    const cls = ['row', e.dir === 'in' && (e.type === 'error' || !e.ok) ? 'err' : '', e.dir === 'out' ? 'out' : '', e.dir === 'ws' ? 'ws' : ''].filter(Boolean).join(' ');
    const row = `<tr class="${cls}" data-seq="${e.seq}"><td>${clock(e.t)}</td><td>${e.dir}</td><td>${esc(e.type)}</td><td>${e.turn ?? ''}</td><td>${e.size}</td><td title="${esc(summarize(e))}">${esc(summarize(e))}</td></tr>`;
    const detail = view.expanded.has(e.seq) && e.dir !== 'ws'
      ? `<tr class="detail" data-seq="${e.seq}"><td colspan="6"><pre>${esc(JSON.stringify(fold(e.raw), null, 2))}</pre></td></tr>` : '';
    return row + detail;
  }
  function renderTable() { tbody.innerHTML = [...view.entries].reverse().map(rowHtml).join(''); }
  tbody.addEventListener('click', (ev) => {
    const tr = ev.target.closest('tr.row'); if (!tr) return;
    const seq = +tr.dataset.seq, entry = view.entries.find(x => x.seq === seq);
    if (!entry || entry.dir === 'ws') return;
    view.expanded = toggled(view.expanded, seq);
    renderTable();
  });

  function tick() { renderHeader(); renderTimeline(); }
  function setOpen(onOff) {
    view.open = onOff;
    clearInterval(view.timer); view.timer = null;
    if (!onOff) return;
    tick(); renderTable();
    view.timer = setInterval(tick, 1000);
  }
  function setConnected(onOff) {
    view.connected = onOff;
    light.classList.toggle('on', onOff); light.title = onOff ? 'Socket connected' : 'Socket reconnecting';
    if (view.open) tick();
  }
  function blink() {
    light.classList.add('blink'); clearTimeout(view.blinkTimer);
    view.blinkTimer = setTimeout(() => light.classList.remove('blink'), BLINK_MS);
  }
  function onEntry(entries) { view.entries = entries; if (view.open) { renderTable(); tick(); } }
  return { setOpen, setConnected, blink, onEntry };
}
```

- [ ] **Step 4: Run the tests**

Run: `node --test 'pagetests/*.test.mjs'`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add duet/static/js/diagview.js
git commit -m "feat(page): diagnostics view; light, header, timeline svg and the log table with folded detail" -- duet/static/js/diagview.js pagetests/diagnostics.test.mjs
```

---

### Task 6: record at the socket, wire the drawer

**Files:**
- Modify: `duet/static/js/app.js` (imports, `app`, `send`, `connect`, `boot`)
- Modify: `duet/static/js/ui.js` (`placeBubble` floor, panel toggles, keys, `?view=`, return)
- Modify: `pagetests/README.md` line 12
- Test: `pagetests/diagnostics.test.mjs`

- [ ] **Step 1: Add the failing wiring tests**

Append to `pagetests/diagnostics.test.mjs`:

```js
test('app.js records every frame before dispatch, both socket events, and every sent command', () => {
  const js = read('js/app.js');
  assert.match(js, /import \{ append, frameEntry, sentEntry, socketEntry \} from '\.\/diag\.js\?v=ds6';/);
  assert.match(js, /import \{ initDiagView \} from '\.\/diagview\.js\?v=ds6';/);
  assert.match(js, /import \{ initUI \} from '\.\/ui\.js\?v=ds6';/);
  const onmessage = js.slice(js.indexOf('ws.onmessage'), js.indexOf('\n}', js.indexOf('ws.onmessage')));
  assert.ok(onmessage.indexOf('frameEntry(e.data, m, t, seq)') < onmessage.indexOf('if (m) handle(m)'), 'recorded before dispatch');
  assert.match(onmessage, /app\.diagView\.blink\(\)/);
  assert.match(js, /ws\.onopen = \(\) => \{[^\n]*socketEntry\('open', null, t, seq\)[^\n]*setConnected\(true\)/);
  assert.match(js, /ws\.onclose = \(e\) => \{[^\n]*socketEntry\('close', e\.code, t, seq\)[^\n]*setConnected\(false\)/);
  assert.match(js, /app\.ws\.send\(JSON\.stringify\(msg\)\);\n\s*record\(\(t, seq\) => sentEntry\(msg, t, seq\)\);/);
  assert.ok(js.indexOf('app.diagView = initDiagView(') < js.indexOf('app.ui = initUI('), 'the view exists before the UI needs it');
});

test('ui.js opens one drawer at a time, binds G and ?view=diag, and floors the bubble on whichever is open', () => {
  const js = read('js/ui.js');
  assert.match(js, /function toggleDiag\(force\) \{\n\s*const onOff = document\.body\.classList\.toggle\('diag', force\);\n\s*if \(onOff\) document\.body\.classList\.remove\('controls'\);\n\s*app\.diagView\.setOpen\(onOff\);/);
  assert.match(js, /function toggleControls\(force\) \{\n\s*const onOff = document\.body\.classList\.toggle\('controls', force\);\n\s*if \(onOff\) closeDiag\(\);/);
  assert.match(js, /\$\('diag-gear'\)\.onclick = \(\) => toggleDiag\(true\); \$\('diag-hide'\)\.onclick = \(\) => toggleDiag\(false\);/);
  assert.match(js, /e\.key === 'g' \|\| e\.key === 'G'\) toggleDiag\(\)/);
  assert.match(js, /if \(view0 === 'diag'\) toggleDiag\(true\);/);
  assert.match(js, /const open = document\.body\.classList\.contains\('controls'\) \? \$\('panel'\) : document\.body\.classList\.contains\('diag'\) \? \$\('diag'\) : null;/);
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `node --test pagetests/diagnostics.test.mjs`
Expected: the two new tests FAIL.

- [ ] **Step 3: Edit `app.js`**

Imports: change `import { initUI } from './ui.js?v=ds4';` to `?v=ds6` and add after the geometry import:

```js
import { append, frameEntry, sentEntry, socketEntry } from './diag.js?v=ds6';
import { initDiagView } from './diagview.js?v=ds6';
```

In `app`, after `ws: null, connected: false,` add `diag: { entries: [], seq: 0 }, diagView: null,`.

Replace `send`:

```js
/** Diagnostics: every frame in, every command out, and the socket's own events, kept for the drawer. */
function record(make) {
  const seq = app.diag.seq + 1;
  app.diag = { entries: append(app.diag.entries, make(Date.now(), seq)), seq };
  if (app.diagView) app.diagView.onEntry(app.diag.entries);
}
export function send(msg) {
  if (!(msg && app.ws && app.ws.readyState === 1)) return;
  app.ws.send(JSON.stringify(msg));
  record((t, seq) => sentEntry(msg, t, seq));
}
```

Replace the three socket callbacks in `connect`:

```js
  ws.onopen = () => { app.connected = true; record((t, seq) => socketEntry('open', null, t, seq)); app.diagView.setConnected(true); notify({ type: 'socket', connected: true }); };
  ws.onclose = (e) => { app.connected = false; record((t, seq) => socketEntry('close', e.code, t, seq)); app.diagView.setConnected(false); notify({ type: 'socket', connected: false }); setTimeout(connect, 1000); };
  ws.onmessage = (e) => {
    const m = parseMessage(e.data);
    record((t, seq) => frameEntry(e.data, m, t, seq)); app.diagView.blink();
    if (m) handle(m); else console.warn('dropped message', e.data.slice(0, 120));
  };
```

In `boot`, before `app.ui = initUI(...)`:

```js
  app.diagView = initDiagView({ light: $('light'), summary: $('diag-summary'), svg: $('diag-timeline'), tbody: $('diag-rows') });
```

`connect()` runs at the end of `boot`, after the view exists, so the callbacks can use `app.diagView` without a guard.

- [ ] **Step 4: Edit `ui.js`**

In `placeBubble`, replace the `floor` line with:

```js
    const open = document.body.classList.contains('controls') ? $('panel') : document.body.classList.contains('diag') ? $('diag') : null;
    const floor = open ? viewer.H - open.offsetHeight - cq : viewer.H - 1.6 * cq;
```

Replace `toggleControls` and its bindings line:

```js
  function toggleControls(force) {
    const onOff = document.body.classList.toggle('controls', force);
    if (onOff) closeDiag();
    $('gear').title = onOff ? '' : 'Show controls (C)';
    placeBubble(currentBubble());
  }
  function closeDiag() { document.body.classList.remove('diag'); app.diagView.setOpen(false); }
  function toggleDiag(force) {
    const onOff = document.body.classList.toggle('diag', force);
    if (onOff) document.body.classList.remove('controls');
    app.diagView.setOpen(onOff);
    placeBubble(currentBubble());
  }
  $('gear').onclick = () => toggleControls(true); $('hide').onclick = () => toggleControls(false);
  $('diag-gear').onclick = () => toggleDiag(true); $('diag-hide').onclick = () => toggleDiag(false);
```

In the key handler, after the `c` line add:

```js
    else if (e.key === 'g' || e.key === 'G') toggleDiag();
```

Replace the `?view=console` line with:

```js
  const view0 = new URLSearchParams(location.search).get('view') || '';
  if (view0 === 'console') toggleControls(true);
  if (view0 === 'diag') toggleDiag(true);
```

Return `toggleDiag` too: `return { showLive, showShot, play, stopLoop, toggleControls, toggleDiag, renderAll };`.

`pagetests/README.md` line 12 becomes: `Keys on the page: arrows step photos, space plays the loop, L live, C controls, G diagnostics, Z crop, D developer mode.` and the harness line gains ` (or ?view=diag for the diagnostics drawer)` after `?view=console`.

- [ ] **Step 5: Run every page test**

Run: `node --test 'pagetests/*.test.mjs'`
Expected: `ℹ fail 0`; 67 earlier tests plus 16 in diag and 7 in diagnostics.

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(page): record the stream at the socket and wire the diagnostics drawer; gear, Hide, G, ?view=diag" -- duet/static/js/app.js duet/static/js/ui.js pagetests/README.md pagetests/diagnostics.test.mjs
```

---

### Task 7: live check on the fake runner and the backend suite

**Files:** none changed unless the check finds a bug.

- [ ] **Step 1: Backend tests still pass (the served page is asserted on)**

Run: `.venv/bin/python -m pytest -q tests`
Expected: 130 passed.

- [ ] **Step 2: Start the fake runner on a spare port**

Run in the background: `.venv/bin/python -m duet.run --fake --port 8001 --exchanges 2`
Expected: `Duet on http://localhost:8001`.

- [ ] **Step 3: Walk the page in the built-in browser**

Open `http://localhost:8001/`. Check, in order:

1. The corner row shows a green light, the gear and Controls; the light flickers as messages arrive.
2. Press `G`: the drawer opens with the header ("socket connected · … received"), the timeline (eleven lanes, green band), rows in the log. Press `C`: the panel replaces the drawer. Press `G`: the drawer replaces the panel. Hide closes it and the corner row returns.
3. Let a turn run: the state lane shows labelled marks, progress marks appear as the fake arm draws, one plan row and one interpretation row per turn. Click the plan row: the detail shows `"polylines": "N strokes, M points"`. Click again: it folds.
4. Press Pause in the panel, then open the drawer: an `out` row `{"type":"pause"}` sits just above the `state` row `paused`.
5. Stop the runner (Ctrl-C): the light turns red, a `ws close` row appears, the band turns red at the right, the header says reconnecting. Start it again: `ws open` rows follow, the band goes green, the light is green.
6. With the drawer open, the bubble sits above it (not hidden behind).
7. Press `D` and hover the gear, the light, the drawer parts: their `data-el` names show.

Fix anything that fails, add a test for it where a pure function is at fault, and commit.

- [ ] **Step 4: Stop the runner and confirm the tree**

Run: `git status --short`
Expected: only the two untracked `notes/hackathon/0[67]-*.md` files that were already there.
