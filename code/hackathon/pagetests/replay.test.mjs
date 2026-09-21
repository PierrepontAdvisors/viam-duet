import { test } from 'node:test';
import assert from 'node:assert/strict';
import { schedule, words, clip, drawMs, Player, PACE, WORDS, DEFAULT_ARTIST } from '../duet/static/js/replay.js';
import { planMs } from '../duet/static/js/hand.js';

const SQ = [[40, 40], [80, 40], [80, 80], [40, 80], [40, 40]];
const LINE = [[100, 100], [140, 100]];
const REPLAY = {
  session: 'sess', base: 'sessions/sess', exchanges: 2, length: 'medium', frames: { start: true, final: true },
  calib: { marks_image: [[1, 2], [3, 4], [5, 6], [7, 8]], board_tl_index: 3, board_mm: [176, 240], image_size: [1280, 720], cam_to_robot: { ax: 1, bx: 0, ay: 1, by: 0 } },
  video: 'sessions/sess/session.mp4',
  turns: [
    { turn: 1, artist: 'mimic', source: 'ink', latency_s: 0, coverage: 0.05, sees: 'Your new mark, ready to echo.', adds: 'a copy beside it, shifted', color: '#1b8f3a', new: [SQ], plan: [SQ, LINE], frames: { human: true, robot: true } },
    { turn: 2, artist: 'haring', source: 'claude', latency_s: 6.7, coverage: 0.11, sees: 'A crowded world of creatures, flowers and dancing figures.', adds: 'A small green dancing figure in the open lower-right space to balance the crowd.', color: '#1b8f3a', new: [LINE], plan: [LINE], frames: { human: true, robot: false } },
  ],
};
/** A fake sleep that advances a clock and yields one macrotask, so a test can act between ticks. */
const tickSleep = (advance) => () => new Promise(r => setTimeout(() => { advance(); r(); }, 0));
const tick = () => new Promise(r => setTimeout(r, 0));
const emits = (steps) => steps.filter(s => s.emit).map(s => s.emit);
const waits = (steps) => steps.filter(s => s.wait !== undefined);

test('words: ink artists speak from their banks by exchange, Claude turns take the build words or a clipped line', () => {
  assert.deepEqual(words({ turn: 1, artist: 'mimic' }), { thought: 'Let me try that…', quip: 'Copycat!' });
  assert.deepEqual(words({ turn: 5, artist: 'shader' }), { thought: WORDS.shader.thoughts[0], quip: WORDS.shader.quips[1] });
  assert.deepEqual(words({ turn: 7, artist: 'haring', thought: 'A crowd!', quip: 'A dancer!' }), { thought: 'A crowd!', quip: 'A dancer!' });
  const w = words(REPLAY.turns[1]);
  assert.ok(w.thought.endsWith('…') && w.thought.split(' ').length <= 7, w.thought);
  assert.ok(w.quip.endsWith('…') && w.quip.split(' ').length <= 9, w.quip);
  assert.equal(clip('one two three', 8), 'one two three'); assert.equal(clip('a, b, c, d', 2), 'a, b…');
});

test('schedule: look and the start shot, then per turn the states and messages the socket would carry', () => {
  const steps = schedule(REPLAY);
  const m = emits(steps);
  assert.equal(m[0].type, 'state'); assert.equal(m[0].state, 'look'); assert.equal(m[0].turn, 0); assert.equal(m[0].session, 'sess'); assert.equal(m[0].artist, 'abstract');
  assert.deepEqual(m[1], { type: 'shot', url: 'sessions/sess/turn-00-start.jpg', turn: 0, who: 'start', frame_url: 'sessions/sess/turn-00-start-frame.jpg' });
  const states = m.filter(x => x.type === 'state').map(x => `${x.state}:${x.turn}`);
  assert.deepEqual(states, ['look:0', 'human_turn:0', 'capture:0', 'interpret:0', 'plan:0', 'robot_draw:0', 'look:1',
                            'human_turn:1', 'capture:1', 'interpret:1', 'plan:1', 'robot_draw:1', 'look:2', 'finish:2', 'finished:2']);
  const human = m.filter(x => x.type === 'human');
  assert.deepEqual(human[0].new, [SQ]); assert.deepEqual(human[1].polylines, [SQ, LINE]); assert.equal(human[1].turn, 2);
  const shots = m.filter(x => x.type === 'shot').map(x => `${x.turn}-${x.who}${x.frame_url ? '' : '!'}${x.artist ? '@' + x.artist : ''}`);
  assert.deepEqual(shots, ['0-start', '1-human@mimic', '1-robot@mimic', '2-human@haring', '2-robot!@haring', '2-final@haring']);
  const interp = m.filter(x => x.type === 'interpretation');
  assert.equal(interp[0].source, 'ink'); assert.equal(interp[0].quip, 'Copycat!'); assert.equal(interp[0].artist, 'mimic'); assert.equal(interp[0].turn, 1);
  assert.equal(interp[1].latency_s, 6.7); assert.equal(interp[1].artist, 'haring');
  const plans = m.filter(x => x.type === 'plan');
  assert.deepEqual(plans[0].polylines, [SQ, LINE]); assert.equal(plans[0].color, '#1b8f3a'); assert.equal(plans[0].budget_mm, 1200); assert.equal(plans[0].artist, 'mimic');
  const progress = m.filter(x => x.type === 'progress');
  assert.deepEqual(progress.map(p => `${p.turn}:${p.stroke}`), ['1:0', '1:1', '2:0']);
  assert.equal(progress[1].drawn_mm, 200);                              // 160 mm square plus a 40 mm line
  assert.deepEqual(m.filter(x => x.type === 'feed').map(x => x.source), ['live', 'held', 'live', 'held', 'live', 'held', 'live']);
  assert.deepEqual(m[m.length - 1], { type: 'video', url: 'sessions/sess/session.mp4' });
  const finished = m.filter(x => x.state === 'finished')[0];
  assert.equal(finished.coverage, 0.11); assert.equal(finished.exchanges, 2); assert.equal(finished.hand_guard, 'off');
});

test('schedule: the picker setting is Abstract, then each exchange\'s artist; a cue per human turn picks on a switch, else Go', () => {
  assert.equal(DEFAULT_ARTIST, 'abstract');
  const steps = schedule(REPLAY);
  const cues = steps.filter(s => s.cue && s.cue.hand).map(({ cue }) => ({ hand: cue.hand, artist: cue.artist }));
  assert.deepEqual(cues, [{ hand: 'pick', artist: 'mimic' }, { hand: 'pick', artist: 'haring' }]);
  const same = schedule({ ...REPLAY, turns: [REPLAY.turns[0], { ...REPLAY.turns[1], artist: 'mimic' }] });
  assert.deepEqual(same.filter(s => s.cue && s.cue.hand).map(s => s.cue.hand), ['pick', 'go']);
  const states = emits(steps).filter(x => x.type === 'state').map(x => `${x.state}:${x.artist}`);
  assert.deepEqual(states.slice(0, 8), ['look:abstract', 'human_turn:abstract', 'capture:mimic', 'interpret:mimic', 'plan:mimic', 'robot_draw:mimic', 'look:mimic', 'human_turn:mimic']);
  assert.equal(states[8], 'capture:haring');
  const i = steps.findIndex(s => s.emit && s.emit.state === 'human_turn');
  assert.ok(steps[i + 1].cue, 'the cue follows the human_turn state');
  assert.deepEqual(steps[i + 3], { wait: PACE.human, on: 'pass' });                       // after the hand cue and the clock cue
  assert.equal(PACE.human, 16000);
});

test('schedule: the hand cue carries the roster row and the drawable strokes; a clock cue follows it and each capture with the half\'s time', () => {
  const speck = [[10, 10], [12, 11]];                                  // 2.2 mm: a trace fragment, not a mark
  const r = { ...REPLAY, turns: [{ ...REPLAY.turns[0], new: [SQ, speck] }, REPLAY.turns[1]] };
  const cues = schedule(r).filter(s => s.cue).map(s => s.cue);
  assert.deepEqual(cues[0], { hand: 'pick', artist: 'mimic', row: 1, draw: [SQ] });
  assert.deepEqual(cues[1], { clock: 'visitor', ms: planMs(cues[0]) });
  assert.deepEqual(cues[2], { clock: 'robot', ms: PACE.capture + PACE.thinkInk + PACE.plan + PACE.settle + drawMs(2) });
  assert.deepEqual(cues[3], { hand: 'pick', artist: 'haring', row: 2, draw: [LINE] });
  assert.equal(cues[5].ms, PACE.capture + PACE.thinkClaude + PACE.plan + PACE.settle + drawMs(1));
  const fast = schedule(r, 2).filter(s => s.cue).map(s => s.cue);
  assert.equal(fast[1].ms, planMs(fast[0], 2));
  assert.equal(fast[2].ms, Math.round((PACE.capture + PACE.thinkInk + PACE.plan + PACE.settle) / 2) + drawMs(2, 2));
  const steps = schedule(r);
  const h = steps.findIndex(s => s.emit && s.emit.state === 'human_turn');
  assert.ok(steps[h + 1].cue.hand && steps[h + 2].cue.clock === 'visitor' && steps[h + 3].on === 'pass', 'hand cue, clock cue, then the wait');
  const c = steps.findIndex(s => s.emit && s.emit.state === 'capture');
  assert.equal(steps[c + 1].cue.clock, 'robot');
  const off = schedule({ ...r, artists: ['haring'] }).filter(s => s.cue && s.cue.hand)[0].cue;
  assert.equal(off.row, -1, 'an artist off the roster has no row');
});

test('drawMs: 350 ms a stroke, never under 3 s or over 12 s, divided by the speed; the player carries its speed', () => {
  assert.equal(drawMs(0), 0); assert.equal(drawMs(2), PACE.drawMin); assert.equal(drawMs(10), 3500); assert.equal(drawMs(40), PACE.drawMax);
  assert.equal(drawMs(10, 2), 1750);
  assert.equal(new Player(REPLAY, () => {}, { speed: 4 }).drawMs(10), 875);
});

test('schedule: the human turn waits on Go, drawing is paced by stroke count within bounds, speed divides every wait', () => {
  const steps = schedule(REPLAY);
  const w = waits(steps);
  assert.equal(w[0].wait, PACE.look);
  assert.deepEqual(w[1], { wait: PACE.human, on: 'pass' });
  const draw1 = w.filter((x, i) => steps.indexOf(x) > steps.findIndex(s => s.emit && s.emit.state === 'robot_draw') && !x.on).slice(0, 2);
  assert.equal(draw1[0].wait + draw1[1].wait, PACE.drawMin);          // two strokes still take the minimum drawing time
  const fast = waits(schedule(REPLAY, 2));
  assert.deepEqual(fast.map(x => x.wait), w.map(x => Math.round(x.wait / 2)));
  const other = schedule(REPLAY, 1, 'sess-r2');
  assert.equal(emits(other)[0].session, 'sess-r2');
  assert.equal(emits(other)[1].url, 'sessions/sess/turn-00-start.jpg');    // the files do not move between runs
});

test('Player: boot primes the page, start runs the piece, pass cuts the human wait, restart starts a new session id', async () => {
  let clock = 0;
  const seen = [];
  const player = new Player(REPLAY, (m) => seen.push(m), { now: () => clock, sleep: tickSleep(() => { clock += 100; }) });
  player.boot();
  assert.equal(seen[0].type, 'calib'); assert.equal(seen[1].state, 'human_turn'); assert.equal(seen[1].turn, 0); assert.equal(seen[1].session, 'sess');
  const p = player.start();
  for (let i = 0; i < 12; i++) await tick();                           // into the first human turn
  assert.equal(player.lastState.state, 'human_turn');
  player.command({ type: 'pass' });                                   // Go cuts its four seconds short
  await p;
  const states = seen.filter(m => m.type === 'state').map(m => m.state);
  assert.equal(states[states.length - 1], 'finished'); assert.equal(seen[seen.length - 1].type, 'video');
  assert.ok(clock < 60000, `took ${clock} ms of scripted time`);
  seen.length = 0;
  player.command({ type: 'restart' });
  await tick();
  assert.equal(seen[0].state, 'look'); assert.equal(seen[0].session, 'sess-r2');
  player.command({ type: 'end' });
  while (player.running) await tick();
  const after = seen.filter(m => m.type === 'state').map(m => m.state);
  assert.ok(after.includes('finish') && after[after.length - 1] === 'finished' && !after.includes('human_turn'), after.join(','));
});

test('Player: pause holds the clock and shows Paused, resume restores the state, other settings are ignored', async () => {
  let clock = 0;
  const seen = [];
  const player = new Player(REPLAY, (m) => seen.push(m), { now: () => clock, sleep: tickSleep(() => { clock += 100; }) });
  const p = player.start();
  await tick();
  const n = seen.length;
  player.command({ type: 'set', length: 'short' });
  assert.equal(seen.length, n, 'a length setting changes nothing');
  player.command({ type: 'pause' });
  assert.equal(seen[seen.length - 1].state, 'paused');
  const at = seen.length;
  for (let i = 0; i < 40; i++) await tick();                           // four scripted seconds pass
  assert.equal(seen.length, at, 'nothing moves while paused');
  player.command({ type: 'resume' });
  assert.equal(seen[seen.length - 1].state, 'look');
  player.stop();
  await p;
});

test('Player: cues reach the callback, boot starts on Abstract, a pick relabels the state until capture, restart forgets it', async () => {
  let clock = 0;
  const seen = [], cues = [];
  const player = new Player(REPLAY, (m) => seen.push(m), { now: () => clock, sleep: tickSleep(() => { clock += 100; }), cue: (c) => cues.push(c) });
  player.boot();
  assert.equal(seen[1].state, 'human_turn'); assert.equal(seen[1].artist, 'abstract');
  const p = player.start();
  for (let i = 0; i < 12; i++) await tick();                           // into the first human turn
  assert.equal(player.lastState.state, 'human_turn'); assert.equal(player.lastState.artist, 'abstract');
  assert.equal(cues.length, 2); assert.equal(cues[0].hand, 'pick'); assert.equal(cues[0].artist, 'mimic'); assert.equal(cues[1].clock, 'visitor');
  player.command({ type: 'set', artist: 'shader' });                   // a visitor's pick, or the hand's
  assert.equal(seen[seen.length - 1].state, 'human_turn'); assert.equal(seen[seen.length - 1].artist, 'shader');
  player.command({ type: 'set', artist: 'nobody' });                   // not on the roster: ignored
  assert.equal(seen[seen.length - 1].artist, 'shader');
  player.command({ type: 'pass' });
  await tick(); await tick();
  const capture = seen.filter(m => m.state === 'capture')[0];
  assert.equal(capture.artist, 'mimic', 'the recording draws');
  assert.equal(player.pick, null);
  while (!(player.lastState && player.lastState.state === 'human_turn' && player.lastState.turn === 1)) await tick();
  assert.equal(player.lastState.artist, 'mimic', 'the setting after exchange 1');
  player.command({ type: 'set', artist: 'vangogh' });
  assert.equal(player.lastState.artist, 'vangogh');
  player.command({ type: 'restart' });
  await tick();
  assert.equal(player.pick, null); assert.equal(player.lastState.state, 'look'); assert.equal(player.lastState.artist, 'abstract');
  player.stop();
  await p;
});

test('schedule: a mark opens each half of an exchange and the finish, so the Player can seek to it', () => {
  const steps = schedule(REPLAY);
  const marks = steps.map((s, i) => (s.mark ? { ...s.mark, i } : null)).filter(Boolean);
  assert.deepEqual(marks.map(m => `${m.turn}:${m.who}`), ['1:human', '1:robot', '2:human', '2:robot', '2:finish']);
  for (const m of marks) {
    const next = steps[m.i + 1].emit;
    assert.equal(next && next.state, m.who === 'human' ? 'human_turn' : m.who === 'robot' ? 'capture' : 'finish', `${m.turn}:${m.who} sits right before its state`);
  }
});

test('Player: seek moves the run by half-exchanges under a new session, feeding what came before at once; clamped at both ends; ignored before Start', async () => {
  let clock = 0;
  const seen = [], cues = [];
  const player = new Player(REPLAY, (m) => seen.push(m), { now: () => clock, sleep: tickSleep(() => { clock += 100; }), cue: (c) => cues.push(c) });
  player.boot();
  player.command({ type: 'seek', delta: 1 });
  assert.ok(!player.running, 'a seek before Start does nothing');
  const p = player.start();
  for (let i = 0; i < 12; i++) await tick();                           // into the first human turn
  assert.equal(player.half, 0); assert.equal(player.lastState.state, 'human_turn');
  seen.length = 0; cues.length = 0;
  player.command({ type: 'seek', delta: 1 });                          // → 1:robot
  assert.equal(player.half, 1);
  assert.equal(seen[0].state, 'look'); assert.equal(seen[0].session, 'sess-r2', 'a new session so the page rebuilds');
  const states = seen.filter(m => m.type === 'state').map(m => m.state);
  assert.deepEqual(states, ['look', 'human_turn', 'capture'], 'everything before the mark at once, then the half begins');
  assert.equal(seen.filter(m => m.type === 'shot').length, 2, 'the start and the human shot were fed');
  assert.deepEqual(cues.map(c => c.clock || c.hand), ['robot'], 'no cues for the skipped stretch, the robot clock cue for this half');
  await tick();
  seen.length = 0; cues.length = 0;
  player.command({ type: 'seek', delta: 1 });                          // → 2:human
  assert.equal(player.half, 2);
  const s2 = seen.filter(m => m.type === 'state').map(m => `${m.state}:${m.turn}`);
  assert.equal(s2[s2.length - 1], 'human_turn:1'); assert.ok(s2.includes('robot_draw:0') && s2.includes('look:1'));
  assert.equal(seen.filter(m => m.type === 'plan').length, 1, 'turn 1\'s plan was fed so its strokes are back');
  assert.deepEqual(cues.map(c => c.clock || c.hand), ['pick', 'visitor']);
  player.command({ type: 'seek', delta: -10 });                        // clamps at the first half
  assert.equal(player.half, 0); assert.equal(player.lastState.state, 'human_turn'); assert.equal(player.lastState.turn, 0);
  player.command({ type: 'seek', delta: 10 });                         // clamps at the finish
  assert.equal(player.half, 4); assert.equal(player.lastState.state, 'finish');
  while (player.running) await tick();
  assert.equal(player.lastState.state, 'finished');
  player.command({ type: 'seek', delta: -1 });                         // after the end: the recording starts again at the chosen half
  assert.equal(player.half, 3); assert.ok(player.running); assert.equal(player.lastState.state, 'capture'); assert.equal(player.lastState.turn, 1);
  player.stop();
  await p;
});
