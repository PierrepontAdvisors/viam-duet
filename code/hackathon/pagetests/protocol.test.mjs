import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseMessage, setCommand, command, shotUrl, parseShotUrl } from '../duet/static/js/protocol.js';

test('state is normalized with defaults for the optional fields', () => {
  const m = parseMessage(JSON.stringify({ type: 'state', state: 'human_turn', turn: 2, exchanges: 5, length: 'long',
    artist: 'haring', mode: 'duet', handoff: 'held', hand_guard: 'color at the look pose', session: 'abc' }));
  assert.equal(m.type, 'state'); assert.equal(m.turn, 2); assert.equal(m.coverage, 0);
  assert.equal(m.error, null); assert.equal(m.at_look, false); assert.deepEqual(m.artists, ['haring']);
  assert.equal(m.direction, 0); assert.equal(m.energy, 0.5); assert.equal(m.session, 'abc');
});

test('state with a non-string state or a bad turn is dropped', () => {
  assert.equal(parseMessage(JSON.stringify({ type: 'state', state: 7, turn: 1 })), null);
  assert.equal(parseMessage(JSON.stringify({ type: 'state', state: 'idle', turn: 'x' })), null);
});

test('calib needs four numeric marks and a tl index; the fit defaults to identity', () => {
  const marks = [[1, 2], [3, 4], [5, 6], [7, 8]];
  const m = parseMessage(JSON.stringify({ type: 'calib', marks_image: marks, board_tl_index: 3 }));
  assert.deepEqual(m.marks_image, marks); assert.deepEqual(m.image_size, [1280, 720]);
  assert.deepEqual(m.board_mm, [176, 240]); assert.deepEqual(m.cam_to_robot, { ax: 1, bx: 0, ay: 1, by: 0 });
  assert.equal(parseMessage(JSON.stringify({ type: 'calib', marks_image: [[1, 2]], board_tl_index: 0 })), null);
  assert.equal(parseMessage(JSON.stringify({ type: 'calib', marks_image: marks, board_tl_index: 4 })), null);
});

test('polylines keep only numeric points and drop empty strokes', () => {
  const m = parseMessage(JSON.stringify({ type: 'human', polylines: [[[1, 2], ['a', 3], [4, 5]], [], [[6, 7]]], new: 'nope' }));
  assert.deepEqual(m.polylines, [[[1, 2], [4, 5]], [[6, 7]]]); assert.deepEqual(m.new, []); assert.equal(m.found, true);
  const p = parseMessage(JSON.stringify({ type: 'plan', polylines: [[[0, 0], [1, 1]]], color: 'green' }));
  assert.equal(p.color, '#1b8f3a'); assert.equal(p.budget_mm, 0);
});

test('interpretation carries the storybook fields and a known source', () => {
  const m = parseMessage(JSON.stringify({ type: 'interpretation', sees: 'A cat.', adds: 'A hat.', source: 'fallback', latency_s: 7.5 }));
  assert.equal(m.thought, ''); assert.equal(m.quip, ''); assert.equal(m.source, 'fallback'); assert.equal(m.latency_s, 7.5);
  assert.equal(parseMessage(JSON.stringify({ type: 'interpretation', sees: 'x', adds: 'y', source: 'oracle' })).source, 'claude');
});

test('shot fills who and turn from the url when they are missing', () => {
  const m = parseMessage(JSON.stringify({ type: 'shot', url: '/sessions/s1/turn-03-robot.jpg' }));
  assert.equal(m.turn, 3); assert.equal(m.who, 'robot'); assert.equal(m.frame_url, null); assert.equal(m.session, 's1');
  assert.equal(parseMessage(JSON.stringify({ type: 'shot' })), null);
});

test('per-turn messages carry an optional turn number', () => {
  assert.equal(parseMessage(JSON.stringify({ type: 'plan', polylines: [], turn: 3 })).turn, 3);
  assert.equal(parseMessage(JSON.stringify({ type: 'interpretation', sees: 'a', adds: 'b' })).turn, null);
  assert.equal(parseMessage(JSON.stringify({ type: 'human', polylines: [], turn: '2' })).turn, 2);
  assert.equal(parseMessage(JSON.stringify({ type: 'progress', stroke: 1, turn: 4 })).turn, 4);
});

test('progress, video, dock and error are checked', () => {
  assert.equal(parseMessage(JSON.stringify({ type: 'progress', stroke: 2 })).drawn_mm, 0);
  assert.equal(parseMessage(JSON.stringify({ type: 'progress', stroke: 'two' })), null);
  assert.equal(parseMessage(JSON.stringify({ type: 'video' })), null);
  assert.deepEqual(parseMessage(JSON.stringify({ type: 'dock', slots: { green: 'home' } })).reseat, []);
  assert.equal(parseMessage(JSON.stringify({ type: 'error', message: 'no network' })).message, 'no network');
});

test('garbage, unknown types and non-objects are dropped', () => {
  assert.equal(parseMessage('not json'), null);
  assert.equal(parseMessage(JSON.stringify({ type: 'teleport' })), null);
  assert.equal(parseMessage(JSON.stringify([1, 2])), null);
});

test('commands are built with only allowed settings', () => {
  assert.deepEqual(setCommand({ length: 'short', bogus: 1, direction: 45 }), { type: 'set', length: 'short', direction: 45 });
  assert.equal(setCommand({ bogus: 1 }), null);
  assert.deepEqual(command('pause'), { type: 'pause' });
  assert.deepEqual(command('reset_arm'), { type: 'reset_arm' });
  assert.throws(() => command('launch'));
});

test('shot urls round-trip', () => {
  assert.equal(shotUrl('s1', 4, 'human', false), '/sessions/s1/turn-04-human.jpg');
  assert.equal(shotUrl('s1', 4, 'human', true), '/sessions/s1/turn-04-human-frame.jpg');
  assert.deepEqual(parseShotUrl('/sessions/s1/turn-04-human-frame.jpg'), { session: 's1', turn: 4, who: 'human', frame: true });
  assert.equal(parseShotUrl('/sessions/s1/session.mp4'), null);
});

test('feed carries a known source and state carries ending', () => {
  assert.equal(parseMessage(JSON.stringify({ type: 'feed', source: 'held' })).source, 'held');
  assert.equal(parseMessage(JSON.stringify({ type: 'feed', source: 'stale' })).source, 'stale');
  assert.equal(parseMessage(JSON.stringify({ type: 'feed', source: 'frozen' })).source, 'live');
  assert.equal(parseMessage(JSON.stringify({ type: 'state', state: 'human_turn', turn: 0, ending: true })).ending, true);
  assert.equal(parseMessage(JSON.stringify({ type: 'state', state: 'human_turn', turn: 0 })).ending, false);
});

test('end is a command', () => {
  assert.deepEqual(command('end'), { type: 'end' });
});
