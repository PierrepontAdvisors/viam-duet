import { test } from 'node:test';
import assert from 'node:assert/strict';
import { CAP, LANES, WINDOW_MS, TICK_MS, append, frameEntry, sentEntry, socketEntry, summarize, fold, clock, header, timeline } from '../duet/static/js/diag.js';

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

const inn = (obj, ok = true) => frameEntry(JSON.stringify(obj), ok ? obj : null, 0, 0);
const PL = [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]];

test('summarize gives one line per kind', () => {
  assert.equal(summarize(inn({ type: 'state', state: 'human_turn', turn: 2, exchanges: 5, at_look: true, error: null })), 'human_turn · turn 2 of 5 · at look');
  assert.equal(summarize(inn({ type: 'state', state: 'paused', turn: 1, exchanges: 5, at_look: false, error: 'recover timed out' })), 'paused · turn 1 of 5 · error: recover timed out');
  assert.equal(summarize(inn({ type: 'progress', stroke: 3, drawn_mm: 412 })), 'stroke 3 · 412 mm');
  assert.equal(summarize(inn({ type: 'interpretation', source: 'claude', latency_s: 6.42, sees: 'A cat.', adds: 'A hat.' })), 'claude 6.4 s · sees "A cat." · adds "A hat."');
  assert.equal(summarize(inn({ type: 'interpretation', source: 'fallback', error: 'timeout' })), 'fallback · timeout');
  assert.equal(summarize(inn({ type: 'interpretation', source: 'ink', latency_s: 0.02, sees: 'A loop.', adds: 'An echo.', artist: 'mimic' })), 'ink 0.0 s · sees "A loop." · adds "An echo." · mimic');
  assert.equal(summarize(inn({ type: 'plan', polylines: [PL], budget_mm: 400, color: '#1b8f3a', artist: 'haring' })), '1 strokes · 5 points · budget 400 mm · #1b8f3a · haring');
  assert.equal(summarize(inn({ type: 'shot', url: '/s/turn-01-robot.jpg', who: 'robot', turn: 1, artist: 'shader' })), 'robot · turn 1 · shader');
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

test('bands: a close then an open inside the window reads red, green; nothing is drawn before the first event of a complete log', () => {
  const entries = [at(150, socketEntry('close', 1006, 0, 1)), at(175, socketEntry('open', null, 0, 2))];
  assert.deepEqual(timeline(entries, 200, 100, true).bands, [{ x0: 0.5, x1: 0.75, connected: false }, { x0: 0.75, x1: 1, connected: true }]);
});

test('bands: once the log has hit its cap, the state before the first kept event is the opposite of that event', () => {
  const filler = Array.from({ length: CAP - 2 }, (_, i) => at(100 + i * 0.1, inn({ type: 'progress', stroke: i })));
  const entries = [...filler, at(150, socketEntry('close', 1006, 0, 1)), at(175, socketEntry('open', null, 0, 2))];
  assert.equal(entries.length, CAP);
  assert.deepEqual(timeline(entries, 200, 100, true).bands, [
    { x0: 0, x1: 0.5, connected: true }, { x0: 0.5, x1: 0.75, connected: false }, { x0: 0.75, x1: 1, connected: true },
  ]);
});

test('bands: still disconnected runs red to the right edge; events before the window set the opening state', () => {
  const entries = [at(50, socketEntry('open', null, 0, 1)), at(180, socketEntry('close', 1006, 0, 2))];
  assert.deepEqual(timeline(entries, 200, 100, false).bands, [{ x0: 0, x1: 0.8, connected: true }, { x0: 0.8, x1: 1, connected: false }]);
});
