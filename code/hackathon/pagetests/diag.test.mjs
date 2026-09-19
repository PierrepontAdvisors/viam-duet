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
