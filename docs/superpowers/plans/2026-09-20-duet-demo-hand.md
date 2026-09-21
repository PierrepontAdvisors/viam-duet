# Duet demo hand, openable picker, and demo defaults: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** In the showcase demo's replay, a cartoon hand opens the artist picker, presses the recorded visitor's artist, and presses Go; the visitor can use the picker themselves during playback; the controls panel opens with the demo's own defaults, sound on.

**Architecture:** The replay schedule gains a `cue` step per exchange; the Player passes cues to a callback and echoes a visitor's artist pick into the state until capture. A new `hand.js` turns a cue into timed steps (pure `plan()`) and a `Hand` runner that glides one element and fires real clicks on the page's own buttons. `ui.js` picks a default table by mode; `app.js` wires the hand and the sound default in replay mode.

**Tech Stack:** Vanilla ES modules under `code/hackathon/duet/static/js/`, CSS in `duet.css` sized in `cqw`, Node's built-in test runner (`node --test 'pagetests/*.test.mjs'`, run from `code/hackathon`), `site/build.py` (stdlib Python) to copy the page into `site/demo/`.

Spec: `docs/superpowers/specs/2026-09-20-duet-demo-hand-design.md`. Work in the worktree `.worktrees/showcase-site` on branch `feat/showcase-site`. All paths below are relative to the repository root unless a command says otherwise. Run tests from `code/hackathon`.

---

## File structure

| File | Responsibility | Change |
| --- | --- | --- |
| `code/hackathon/duet/static/js/replay.js` | schedule (pure) and Player | cue steps, the setting, `cue` callback, the pick echo |
| `code/hackathon/duet/static/js/hand.js` | **new**: `plan()` pure, `Hand` runner | the demo hand |
| `code/hackathon/duet/static/index.html` | page markup | the hand element with its SVG; `?v=ds8` |
| `code/hackathon/duet/static/duet.css` | page styles | hand styles; remove the picker's blocking rule |
| `code/hackathon/duet/static/js/ui.js` | chips, picker, panel, keys | default tables by mode, `replay` option, crop default |
| `code/hackathon/duet/static/js/app.js` | boot, dispatch | hand wiring, cue and cancel, sound default, `replay` to `initUI`; `?v=ds8` |
| every other `js/*.js` | imports | `?v=ds7` → `?v=ds8` |
| `code/hackathon/pagetests/replay.test.mjs` | schedule and Player tests | updated and extended |
| `code/hackathon/pagetests/hand.test.mjs` | **new** | `plan()` and `Hand` with a fake DOM |
| `code/hackathon/pagetests/style.test.mjs` | markup and CSS checks | hand rules, blocking rule gone |
| `code/hackathon/pagetests/defaults.test.mjs` | **new** | the default tables and their wiring |
| `site/demo/**` | the built demo | rebuilt by `site/build.py` |

---

### Task 1: The schedule's cues and setting

**Files:**
- Modify: `code/hackathon/duet/static/js/replay.js` (the `schedule` function, lines 45–80)
- Test: `code/hackathon/pagetests/replay.test.mjs`

- [ ] **Step 1: Update the existing schedule test and add the cue test**

In `code/hackathon/pagetests/replay.test.mjs`, change the first assertion line of the test `schedule: look and the start shot, …` so the first look state carries Abstract:

```js
  assert.equal(m[0].type, 'state'); assert.equal(m[0].state, 'look'); assert.equal(m[0].turn, 0); assert.equal(m[0].session, 'sess'); assert.equal(m[0].artist, 'abstract');
```

Add `DEFAULT_ARTIST` to the import line:

```js
import { schedule, words, clip, drawMs, Player, PACE, WORDS, DEFAULT_ARTIST } from '../duet/static/js/replay.js';
```

Add this test after the `schedule: look and the start shot, …` test:

```js
test('schedule: the picker setting is Abstract, then each exchange\'s artist; a cue per human turn picks on a switch, else Go', () => {
  assert.equal(DEFAULT_ARTIST, 'abstract');
  const steps = schedule(REPLAY);
  const cues = steps.filter(s => s.cue).map(s => s.cue);
  assert.deepEqual(cues, [{ hand: 'pick', artist: 'mimic' }, { hand: 'pick', artist: 'haring' }]);
  const same = schedule({ ...REPLAY, turns: [REPLAY.turns[0], { ...REPLAY.turns[1], artist: 'mimic' }] });
  assert.deepEqual(same.filter(s => s.cue).map(s => s.cue), [{ hand: 'pick', artist: 'mimic' }, { hand: 'go' }]);
  const states = emits(steps).filter(x => x.type === 'state').map(x => `${x.state}:${x.artist}`);
  assert.deepEqual(states.slice(0, 8), ['look:abstract', 'human_turn:abstract', 'capture:mimic', 'interpret:mimic', 'plan:mimic', 'robot_draw:mimic', 'look:mimic', 'human_turn:mimic']);
  assert.equal(states[8], 'capture:haring');
  const i = steps.findIndex(s => s.emit && s.emit.state === 'human_turn');
  assert.ok(steps[i + 1].cue, 'the cue follows the human_turn state');
  assert.deepEqual(steps[i + 2], { wait: PACE.human, on: 'pass' });
  assert.equal(PACE.human, 6000);
});
```

- [ ] **Step 2: Run the tests to see them fail**

Run (from `code/hackathon`): `node --test pagetests/replay.test.mjs`
Expected: FAIL. `DEFAULT_ARTIST` is undefined, `m[0].artist` is `'mimic'`, no cue steps, `PACE.human` is 4000.

- [ ] **Step 3: Change the schedule**

In `code/hackathon/duet/static/js/replay.js`, change `PACE.human` to 6000 and add the default artist export right under `ARTISTS`:

```js
export const PACE = { look: 1000, human: 6000, capture: 1000, thinkInk: 1200, thinkClaude: 3500, plan: 1500,
                      strokeMs: 350, drawMin: 3000, drawMax: 12000, settle: 1200, finish: 2000 };
export const ARTISTS = ['abstract', 'mimic', 'haring', 'mondrian', 'vangogh', 'architect', 'designer', 'shader'];
/** The picker's setting before the first exchange: the live page's default. */
export const DEFAULT_ARTIST = 'abstract';
```

Replace the doc comment and body of `schedule` with:

```js
/** The piece as steps: `{ emit: msg }` sends a message, `{ wait: ms }` holds, `{ wait, on: 'pass' }`
 *  holds until Go or the time is up, `{ cue }` tells the page's hand what the recorded visitor did
 *  (`{ hand: 'pick', artist }` when they switched artist, `{ hand: 'go' }` otherwise). The picker's
 *  setting is Abstract before the first exchange and each exchange's artist after it; the states before
 *  a capture carry the setting, the rest the exchange's artist. `speed` divides every wait. */
export function schedule(replay, speed = 1, session = replay.session) {
  const base = replay.base || `sessions/${replay.session}`;
  const div = speed > 0 ? speed : 1;
  const w = (ms, on) => ({ wait: Math.round(ms / div), ...(on ? { on } : {}) });
  const e = (msg) => ({ emit: msg });
  const shot = (turn, who, artist, frame) => e({ type: 'shot', url: `${base}/turn-${pad(turn)}-${who}.jpg`, turn, who,
                                                 frame_url: frame ? `${base}/turn-${pad(turn)}-${who}-frame.jpg` : null, ...(artist ? { artist } : {}) });
  const turns = [...(replay.turns || [])].sort((a, b) => a.turn - b.turn);
  const frames = replay.frames || {};
  let setting = DEFAULT_ARTIST;
  const steps = [e(stateMsg(replay, 'look', 0, setting, session)), shot(0, 'start', null, !!frames.start), e({ type: 'feed', source: 'live' }), w(PACE.look)];
  let ink = [], coverage = 0;
  for (const t of turns) {
    const n = t.turn, artist = t.artist;
    const st = (state, turn, who = artist) => e(stateMsg(replay, state, turn, who, session, coverage));
    steps.push(st('human_turn', n - 1, setting), { cue: artist === setting ? { hand: 'go' } : { hand: 'pick', artist } }, w(PACE.human, 'pass'));
    ink = [...ink, ...(t.new || [])];
    steps.push(st('capture', n - 1), shot(n, 'human', artist, (t.frames || {}).human !== false),
               e({ type: 'human', polylines: ink, new: t.new || [], found: true, turn: n }), w(PACE.capture));
    const { thought, quip } = words(t);
    steps.push(st('interpret', n - 1), w(t.source === 'ink' ? PACE.thinkInk : PACE.thinkClaude),
               e({ type: 'interpretation', sees: t.sees || '', adds: t.adds || '', thought, quip, source: t.source || 'claude',
                   latency_s: t.latency_s ?? null, error: null, turn: n, artist }));
    const plan = t.plan || [];
    steps.push(st('plan', n - 1), e({ type: 'plan', polylines: plan, color: t.color || '#1b8f3a', budget_mm: BUDGET_MM[replay.length] || 4000, turn: n, artist }), w(PACE.plan));
    steps.push(st('robot_draw', n - 1), e({ type: 'feed', source: 'held' }));
    const per = plan.length ? drawMs(plan.length) / plan.length : 0;
    let drawn = 0;
    plan.forEach((pl, i) => { drawn += strokeLength(pl); steps.push(w(per), e({ type: 'progress', stroke: i, drawn_mm: Math.round(drawn), turn: n })); });
    coverage = t.coverage ?? coverage;
    steps.push(shot(n, 'robot', artist, (t.frames || {}).robot !== false), st('look', n), e({ type: 'feed', source: 'live' }), w(PACE.settle));
    setting = artist;
  }
  const done = turns.length;
  steps.push(e(stateMsg(replay, 'finish', done, setting, session, coverage)), e({ type: 'feed', source: 'held' }), w(PACE.finish));
  if (done && frames.final) steps.push(shot(done, 'final', setting, true));
  steps.push(e(stateMsg(replay, 'finished', done, setting, session, coverage)), e({ type: 'feed', source: 'live' }));
  if (replay.video) steps.push(e({ type: 'video', url: replay.video }));
  return steps;
}
```

- [ ] **Step 4: Run the tests**

Run: `node --test pagetests/replay.test.mjs`
Expected: the two schedule tests pass. The Player tests still pass (cue steps are neither `emit` nor `wait`, so `start()` ignores them for now; the `wait` method is not reached for them).

- [ ] **Step 5: Commit**

```bash
git add code/hackathon/duet/static/js/replay.js code/hackathon/pagetests/replay.test.mjs
git commit -m "feat(replay): the schedule keeps the picker setting and emits a cue per human turn: pick on a switch, Go otherwise"
```

---

### Task 2: The Player's cue callback and the pick echo

**Files:**
- Modify: `code/hackathon/duet/static/js/replay.js` (the `Player` class, from `const realSleep`)
- Test: `code/hackathon/pagetests/replay.test.mjs`

- [ ] **Step 1: Write the failing tests**

Rename the last test in `replay.test.mjs` and add a `set` assertion, then add a new test. Replace the test `Player: pause holds the clock and shows Paused, resume restores the state, settings are ignored` with:

```js
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
  assert.deepEqual(cues, [{ hand: 'pick', artist: 'mimic' }]);
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
  assert.equal(player.pick, null); assert.equal(seen[seen.length - 1].artist, 'abstract');
  player.stop();
  await p;
});
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `node --test pagetests/replay.test.mjs`
Expected: FAIL. `cues` stays empty, `seen[1].artist` is `'mimic'`, the `set` does not echo.

- [ ] **Step 3: Change the Player**

Replace the `Player` class in `code/hackathon/duet/static/js/replay.js` with:

```js
/** The states that show the picker's setting; a visitor's pick relabels them until the capture. */
const PICKABLE = ['look', 'human_turn'];

/** Runs the schedule and answers the page's commands. `feed(msg)` is the page's message handler; `cue(c)`
 *  gets each cue step for the page's hand. */
export class Player {
  constructor(replay, feed, { speed = 1, sleep = realSleep, now = () => Date.now(), cue = () => {} } = {}) {
    this.replay = replay; this.rawFeed = feed; this.speed = speed; this.sleep = sleep; this.now = now; this.cue = cue;
    this.run = 1; this.token = 0; this.running = false; this.paused = false; this.passed = false; this.ended = false;
    this.lastState = null; this.pick = null;
  }
  sessionId() { return this.run <= 1 ? this.replay.session : `${this.replay.session}-r${this.run}`; }
  /** The page paces its ghost pen to this so the simulated arm finishes as the last progress lands. */
  drawMs(strokeCount) { return drawMs(strokeCount, this.speed); }
  feed(msg) {
    if (msg.type === 'state') {
      if (msg.state === 'capture') this.pick = null;                                  // the recording draws
      if (this.pick && PICKABLE.includes(msg.state)) msg = { ...msg, artist: this.pick };
      this.lastState = msg;
    }
    this.rawFeed(msg);
  }
  /** Before Start: the calibration and a first state so the page renders and the welcome's Start is live. */
  boot() {
    if (this.replay.calib) this.feed({ type: 'calib', ...this.replay.calib });
    this.feed(stateMsg(this.replay, 'human_turn', 0, DEFAULT_ARTIST, this.sessionId()));
    this.feed({ type: 'feed', source: 'live' });
  }
  async start() {
    if (this.running) return;
    this.running = true; this.paused = false; this.ended = false;
    const token = ++this.token;
    let jumped = false;                                   // End: skip ahead to the finish once, then play it out
    for (const step of schedule(this.replay, this.speed, this.sessionId())) {
      if (token !== this.token) return;
      if (this.ended && !jumped) { if (step.emit && step.emit.state === 'finish') jumped = true; else continue; }
      if (step.emit) { this.feed(step.emit); continue; }
      if (step.cue) { this.cue(step.cue); continue; }
      await this.wait(step.wait, step.on, token);
    }
    if (token === this.token) this.running = false;
  }
  async wait(ms, on, token) {
    if (on === 'pass') this.passed = false;
    let remaining = ms, last = this.now();
    while (token === this.token) {
      if (this.ended || (on === 'pass' && this.passed)) return;
      const t = this.now();
      if (!this.paused) remaining -= t - last;          // the clock stands still while paused
      last = t;
      if (remaining <= 0) return;
      await this.sleep(TICK_MS);
    }
  }
  stop() { this.token += 1; this.running = false; }
  restart() { this.stop(); this.pick = null; this.run += 1; this.start(); }
  command(msg) {
    switch (msg && msg.type) {
      case 'pass': this.passed = true; break;
      case 'pause': if (this.running && !this.paused) { this.paused = true; const s = this.lastState; if (s) this.rawFeed({ ...s, state: 'paused' }); } break;
      case 'resume': if (this.paused) { this.paused = false; if (this.lastState) this.rawFeed(this.lastState); } break;
      case 'restart': this.restart(); break;
      case 'end': if (this.running) this.ended = true; break;
      case 'set': {                          // an artist pick shows on the label until the capture; other settings mean nothing to a recording
        const roster = this.replay.artists || ARTISTS;
        if (typeof msg.artist === 'string' && roster.includes(msg.artist)) { this.pick = msg.artist; if (this.lastState) this.feed({ ...this.lastState }); }
        break;
      }
      default: break;                       // arm commands mean nothing to a recording
    }
  }
}
```

Note: the `wait` for `on === 'pass'` resets `passed` at its start, as before. A pick's `set` does not touch it.

- [ ] **Step 4: Run the tests**

Run: `node --test pagetests/replay.test.mjs`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add code/hackathon/duet/static/js/replay.js code/hackathon/pagetests/replay.test.mjs
git commit -m "feat(replay): the Player hands cues to the page and echoes an artist pick into the state until the capture"
```

---

### Task 3: `hand.js`: the plan and the runner

**Files:**
- Create: `code/hackathon/duet/static/js/hand.js`
- Test: `code/hackathon/pagetests/hand.test.mjs`

- [ ] **Step 1: Write the failing tests**

Create `code/hackathon/pagetests/hand.test.mjs`:

```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { plan, Hand, HAND } from '../duet/static/js/hand.js';

/** A stand-in for an element: a class list, a style, a rect, a click log, and visibility as offsetParent. */
function fake(name, { hidden = false, rect = { left: 0, top: 0, width: 10, height: 10 } } = {}) {
  const classes = new Set(hidden ? ['hidden'] : []);
  return {
    name, style: {}, clicks: 0, rect,
    classList: { add: (c) => classes.add(c), remove: (c) => classes.delete(c), contains: (c) => classes.has(c) },
    get offsetParent() { return classes.has('hidden') ? null : {}; },
    getBoundingClientRect() { return this.rect; },
    click() { this.clicks += 1; },
  };
}
const tick = (ms = 2) => new Promise(r => setTimeout(r, ms));

test('plan: a pick settles, opens the picker, presses the row, holds, presses Go; a Go cue goes straight to Go; speed divides', () => {
  const pick = plan({ hand: 'pick', artist: 'mimic' });
  assert.deepEqual(pick, [{ wait: HAND.settle }, { glide: 'picker', ms: HAND.glide }, { press: 'picker', ms: HAND.press },
                          { glide: 'row', ms: HAND.glide }, { press: 'row', ms: HAND.press }, { wait: HAND.hold },
                          { glide: 'go', ms: HAND.glide }, { press: 'go', ms: HAND.press }]);
  assert.deepEqual(plan({ hand: 'go' }), [{ wait: HAND.settleGo }, { glide: 'go', ms: HAND.glide }, { press: 'go', ms: HAND.press }]);
  assert.deepEqual(plan({ hand: 'pick', artist: 'mimic' }, 2)[1], { glide: 'picker', ms: HAND.glide / 2 });
  assert.equal(plan({ hand: 'go' }, 0)[0].wait, HAND.settleGo);         // a zero speed is taken as 1
});

function rig({ menuOpen = false, pickerHidden = false, goHidden = false } = {}) {
  const stage = fake('stage', { rect: { left: 100, top: 50, width: 800, height: 450 } });
  const picker = fake('picker', { hidden: pickerHidden, rect: { left: 120, top: 100, width: 60, height: 20 } });
  const row = fake('row', { hidden: !menuOpen, rect: { left: 120, top: 130, width: 200, height: 20 } });
  const go = fake('go', { hidden: goHidden, rect: { left: 300, top: 100, width: 80, height: 30 } });
  picker.click = () => { picker.clicks += 1; row.classList[row.offsetParent ? 'add' : 'remove']('hidden'); };   // toggles the menu
  row.click = () => { row.clicks += 1; row.classList.add('hidden'); };                                        // a pick closes the menu
  const el = fake('hand', { hidden: true });
  const hand = new Hand(el, { stage, targets: (name) => ({ picker, row, go })[name], speed: 1000 });          // every wait rounds to a millisecond
  return { hand, el, picker, row, go };
}

test('Hand: a pick glides to and presses the picker, the row, then Go, with the fingertip on each centre, then hides', async () => {
  const { hand, el, picker, row, go } = rig();
  hand.run({ hand: 'pick', artist: 'mimic' });
  assert.ok(!el.classList.contains('hidden'), 'the hand shows at once');
  await tick(40);
  assert.deepEqual([picker.clicks, row.clicks, go.clicks], [1, 1, 1]);
  assert.equal(el.style.left, '240px'); assert.equal(el.style.top, '65px');                                   // Go's centre against the stage
  assert.ok(el.classList.contains('hidden'), 'hidden once the plan is done');
});

test('Hand: it presses what it sees: no toggle on a menu a visitor opened, reopen one that closed, skip a hidden target, cancel hides', async () => {
  const open = rig({ menuOpen: true });
  open.hand.run({ hand: 'pick', artist: 'mimic' });
  await tick(40);
  assert.deepEqual([open.picker.clicks, open.row.clicks, open.go.clicks], [0, 1, 1]);
  const closed = rig();
  closed.picker.click = () => { closed.picker.clicks += 1; if (closed.picker.clicks > 1) closed.row.classList.remove('hidden'); };   // a visitor closes the menu right after the first press
  closed.hand.run({ hand: 'pick', artist: 'mimic' });
  await tick(40);
  assert.equal(closed.picker.clicks, 2, 'pressed again to reopen'); assert.equal(closed.row.clicks, 1);
  const browsing = rig({ pickerHidden: true });
  browsing.hand.run({ hand: 'pick', artist: 'mimic' });
  await tick(40);
  assert.deepEqual([browsing.picker.clicks, browsing.row.clicks, browsing.go.clicks], [0, 0, 1]);
  const gone = rig();
  gone.hand.run({ hand: 'go' });
  gone.hand.cancel();
  await tick(40);
  assert.equal(gone.go.clicks, 0); assert.ok(gone.el.classList.contains('hidden'));
});
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `node --test pagetests/hand.test.mjs`
Expected: FAIL, the module does not exist.

- [ ] **Step 3: Write `hand.js`**

Create `code/hackathon/duet/static/js/hand.js`:

```js
/** The demo's hand: a cartoon pointer that shows the recorded visitor's part during the human turn.
 *  `plan()` is pure (a cue in, timed steps out); `Hand` moves the element and presses the page's own
 *  buttons, so the picker and Go behave exactly as they do for a person. Replay mode only. */

export const HAND = { settle: 700, settleGo: 900, glide: 500, press: 220, hold: 500 };

/** Steps for a cue: `{ wait: ms }`, `{ glide: target, ms }`, `{ press: target, ms }`; targets are `picker`,
 *  `row` (the cue's artist), and `go`. The settle stands for the visitor drawing their mark. `speed` divides. */
export function plan(cue, speed = 1) {
  const div = speed > 0 ? speed : 1;
  const ms = (v) => Math.round(v / div);
  if (cue && cue.hand === 'pick') {
    return [{ wait: ms(HAND.settle) }, { glide: 'picker', ms: ms(HAND.glide) }, { press: 'picker', ms: ms(HAND.press) },
            { glide: 'row', ms: ms(HAND.glide) }, { press: 'row', ms: ms(HAND.press) }, { wait: ms(HAND.hold) },
            { glide: 'go', ms: ms(HAND.glide) }, { press: 'go', ms: ms(HAND.press) }];
  }
  return [{ wait: ms(HAND.settleGo) }, { glide: 'go', ms: ms(HAND.glide) }, { press: 'go', ms: ms(HAND.press) }];
}

const onScreen = (el) => !!el && el.offsetParent !== null;

/** `targets(name, cue)` resolves a target name to the page's element or null. The hand presses what it sees:
 *  it does not toggle a menu a visitor already opened, reopens one that closed under it, and skips a target
 *  that is off screen. `cancel()` stops the run and hides the hand. */
export class Hand {
  constructor(el, { stage, targets, speed = 1 }) {
    this.el = el; this.stage = stage; this.targets = targets; this.speed = speed; this.timer = null; this.token = 0;
  }
  target(name, cue) { const el = this.targets(name, cue); return onScreen(el) ? el : null; }
  run(cue) {
    this.cancel();
    const steps = plan(cue, this.speed), token = ++this.token;
    this.el.classList.remove('hidden');
    const step = (i) => {
      if (token !== this.token) return;
      this.el.classList.remove('press');
      if (i >= steps.length) { this.hide(); return; }
      const s = steps[i];
      let ms = s.ms ?? s.wait ?? 0;
      if (s.glide) { const t = this.target(s.glide, cue); if (t) this.moveTo(t); else ms = 0; }
      else if (s.press && !this.press(s.press, cue)) ms = 0;
      this.timer = setTimeout(() => step(i + 1), ms);
    };
    step(0);
  }
  /** The fingertip on the target's centre, in stage pixels. */
  moveTo(target) {
    const r = target.getBoundingClientRect(), s = this.stage.getBoundingClientRect();
    this.el.style.left = `${r.left - s.left + r.width / 2}px`;
    this.el.style.top = `${r.top - s.top + r.height / 2}px`;
  }
  /** True when something was pressed. */
  press(name, cue) {
    if (name === 'picker' && this.target('row', cue)) return false;                       // the menu is already open
    if (name === 'row' && !this.target('row', cue)) { const p = this.target('picker', cue); if (!p) return false; p.click(); }   // reopen it
    const el = this.target(name, cue);
    if (!el) return false;
    this.el.classList.add('press');
    el.click();
    return true;
  }
  hide() { this.el.classList.remove('press'); this.el.classList.add('hidden'); }
  cancel() { this.token += 1; if (this.timer) clearTimeout(this.timer); this.timer = null; this.hide(); }
}
```

- [ ] **Step 4: Run the tests**

Run: `node --test pagetests/hand.test.mjs`
Expected: all pass. At speed 1000 every wait rounds to a millisecond or less, so a whole run is over well within the 40 ms the tests give it.

- [ ] **Step 5: Commit**

```bash
git add code/hackathon/duet/static/js/hand.js code/hackathon/pagetests/hand.test.mjs
git commit -m "feat(page): hand.js: a pure plan for the demo hand and a runner that presses the page's own buttons"
```

---

### Task 4: The hand's markup and styles; the picker unblocked

**Files:**
- Modify: `code/hackathon/duet/static/index.html` (after the `#home` button, line 72)
- Modify: `code/hackathon/duet/static/duet.css` (the picker rules near line 58; the replay rules at the end)
- Test: `code/hackathon/pagetests/style.test.mjs`

- [ ] **Step 1: Write the failing tests**

Append to `code/hackathon/pagetests/style.test.mjs`:

```js
test('the demo hand: an element in the stage with the pointing-hand SVG, above the menu, out of the way of a real pointer, still under reduced motion', () => {
  const h = read('index.html');
  assert.match(h, /<div class="hand hidden" id="hand" data-el="demo hand">\s*<svg viewBox="0 0 60 72" aria-hidden="true">/);
  assert.ok(h.includes('class="skin"') && h.includes('class="cuff"'), 'the hand has skin and a cuff');
  assert.ok(h.indexOf('id="hand"') > h.indexOf('id="artist-menu"') && h.indexOf('id="hand"') < h.indexOf('id="caption"'), 'after the CTA row, before the bubble');
  const css = read('duet.css');
  assert.match(css, /\.hand \{[^}]*z-index: 5;[^}]*pointer-events: none;/);
  assert.match(css, /\.hand \{[^}]*transition: left \.5s ease, top \.5s ease/);
  assert.match(css, /\.hand\.press \{ transform: [^}]*scale\(\.88\)/);
  assert.match(css, /prefers-reduced-motion: reduce\) \{ \.hand \{ transition: none; \} \.hand\.press \{ transform: translate\(-1\.17cqw, -\.17cqw\); \} \}/);
  assert.ok(!css.includes('#artist-btn { pointer-events: none; }'), 'the picker takes clicks in replay mode');
});
```

- [ ] **Step 2: Run the test to see it fail**

Run: `node --test pagetests/style.test.mjs`
Expected: the new test FAILs on the first assertion (no hand element).

- [ ] **Step 3: Add the markup**

In `code/hackathon/duet/static/index.html`, right after the line

```html
  <button class="go home hidden" id="home" data-el="return to home button">Return to home</button>
```

insert:

```html
  <div class="hand hidden" id="hand" data-el="demo hand">
    <svg viewBox="0 0 60 72" aria-hidden="true">
      <rect class="cuff" x="19" y="56" width="37" height="14" rx="4"/>
      <path class="skin" d="M14 2c-3.4 0-6 2.6-6 6v32c-2-2-5.4-2.4-7.4-.5-1.5 1.5-1 3.6.5 5.1l10 12.4c4 4.6 9 6.8 15 6.8h12c8 0 14-6.2 14-14.2v-14c0-3-2.5-5.5-5.5-5.5-1.5 0-3 .6-4 1.6-.6-2.6-3-4.6-5.8-4.6-1.7 0-3.3.7-4.4 1.9-.9-2.3-3.1-3.9-5.6-3.9-1.3 0-2.5.4-3.5 1.1V8c0-3.4-2.7-6-6-6z"/>
      <path class="line" d="M30.5 30.5v9M40.5 31.5v9M50 33.5v8"/>
    </svg>
  </div>
```

- [ ] **Step 4: Add the styles and drop the blocking rule**

In `code/hackathon/duet/static/duet.css`, after the line `.menu .chip.on { background: var(--yellow); }` add:

```css
/* the demo's hand: a cartoon pointer over the stage, its fingertip on the point it is sent to; it never
   takes a click, so a real pointer can use the same buttons while it moves */
.hand { position: absolute; left: 50%; top: 50%; width: 5cqw; height: 6cqw; z-index: 5; pointer-events: none;
        transform: translate(-1.17cqw, -.17cqw); transform-origin: 1.17cqw .17cqw; transition: left .5s ease, top .5s ease, transform .12s ease;
        filter: drop-shadow(.3cqw .3cqw 0 rgba(0, 0, 0, .35)); }
.hand svg { display: block; width: 100%; height: 100%; overflow: visible; }
.hand .skin { fill: var(--cream); stroke: var(--ink); stroke-width: 3.5; stroke-linejoin: round; stroke-linecap: round; }
.hand .line { fill: none; stroke: var(--ink); stroke-width: 3; stroke-linecap: round; }
.hand .cuff { fill: var(--red); stroke: var(--ink); stroke-width: 3.5; }
.hand.press { transform: translate(-1.17cqw, -.17cqw) scale(.88); }
@media (prefers-reduced-motion: reduce) { .hand { transition: none; } .hand.press { transform: translate(-1.17cqw, -.17cqw); } }
```

Delete the line `body.replay #artist-btn { pointer-events: none; }` near the end of the file.

- [ ] **Step 5: Run the tests**

Run: `node --test pagetests/style.test.mjs`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add code/hackathon/duet/static/index.html code/hackathon/duet/static/duet.css code/hackathon/pagetests/style.test.mjs
git commit -m "feat(page): the demo hand's markup and styles; the artist picker takes clicks in replay mode"
```

---

### Task 5: The default tables in `ui.js`

**Files:**
- Modify: `code/hackathon/duet/static/js/ui.js` (top of file and the first 40 lines of `initUI`)
- Test: `code/hackathon/pagetests/defaults.test.mjs`

- [ ] **Step 1: Write the failing test**

Create `code/hackathon/pagetests/defaults.test.mjs`:

```js
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
```

- [ ] **Step 2: Run the test to see it fail**

Run: `node --test pagetests/defaults.test.mjs`
Expected: FAIL, `LIVE_DEFAULTS` is not exported.

- [ ] **Step 3: Add the tables and use them**

In `code/hackathon/duet/static/js/ui.js`, replace the line

```js
const LAYER_DEFAULTS = { robot: true, ink: true, caption: true, chips: true, board: false, clean: true, vector: false };
```

with:

```js
/** The page's defaults where the visitor's browser has nothing stored. The live page shows every layer over the
 *  camera; the showcase demo opens as Nicholas's screenshot of 2026-09-20 shows: cropped to the board, no ink
 *  layer (the photos already show the ink), two greens and wider lines, its own levels, sound on. A stroke
 *  colour in the table is locked: a plan's colour does not replace it. */
export const LIVE_DEFAULTS = { layers: { robot: true, ink: true, caption: true, chips: true, board: false, clean: true, vector: false },
                               ink: '#111111', inkWidth: 12, stroke: null, strokeWidth: 14, picture: CLEAN_LEVELS, crop: false, sound: false };
export const DEMO_DEFAULTS = { layers: { ...LIVE_DEFAULTS.layers, ink: false }, ink: '#37e65b', inkWidth: 38, stroke: '#1fcf4f', strokeWidth: 24,
                               picture: { brightness: 0, contrast: 0.84, exposure: 1.4 }, crop: true, sound: true };
export const defaultsFor = (replay) => (replay ? DEMO_DEFAULTS : LIVE_DEFAULTS);
```

Change the signature and the first line of `initUI`:

```js
export function initUI(app, { sendSet, sendCommand, on, replay = false }) {
  const D = defaultsFor(replay);
  const view = { source: 'live', index: -1, playing: false, timer: null, thinkingSince: 0, strokeLocked: false, lastError: null, autoplayed: null, relaunching: false };
```

In the layers loop, change `store.get(\`layer.${name}\`, LAYER_DEFAULTS[name])` to `store.get(\`layer.${name}\`, D.layers[name])`.

Change the colour and width lines:

```js
  inkColor.value = store.get('color.ink', D.ink); stage.style.setProperty('--vec-ink', inkColor.value);
  inkColor.oninput = () => { stage.style.setProperty('--vec-ink', inkColor.value); store.set('color.ink', inkColor.value); };
  const lockedStroke = store.get('color.stroke', D.stroke);
  if (lockedStroke) { view.strokeLocked = true; strokeColor.value = lockedStroke; stage.style.setProperty('--vec-stroke', lockedStroke); }
```

and

```js
  inkWidth.value = store.get('width.ink', D.inkWidth); strokeWidth.value = store.get('width.stroke', D.strokeWidth); applyWidths();
```

Change the picture line `applyPicture({ ...CLEAN_LEVELS, ...store.get('picture', {}) });` to:

```js
  applyPicture({ ...D.picture, ...store.get('picture', {}) });
```

After the export-SVG block (before `// ---- chips ----`) add:

```js
  // ---- view ----
  if (D.crop) viewer.setCrop(true);                                   // the demo starts cropped; crop is not stored
```

In `code/hackathon/duet/static/js/app.js` change the `initUI` call to:

```js
  app.ui = initUI(app, { sendSet, sendCommand, on, replay: !!REPLAY_URL });
```

- [ ] **Step 4: Run all the tests**

Run: `node --test 'pagetests/*.test.mjs'`
Expected: all pass (`CLEAN_LEVELS` is already imported in `ui.js`).

- [ ] **Step 5: Commit**

```bash
git add code/hackathon/duet/static/js/ui.js code/hackathon/duet/static/js/app.js code/hackathon/pagetests/defaults.test.mjs
git commit -m "feat(page): default tables by mode: the demo opens cropped, without the ink layer, with its greens, widths, levels"
```

---

### Task 6: Wire the hand and the sound default in `app.js`; bump the asset version

**Files:**
- Modify: `code/hackathon/duet/static/js/app.js`
- Modify: every `code/hackathon/duet/static/js/*.js` import and `code/hackathon/duet/static/index.html` (`?v=ds7` → `?v=ds8`)
- Test: `code/hackathon/pagetests/defaults.test.mjs`, `code/hackathon/pagetests/style.test.mjs`

- [ ] **Step 1: Write the failing test**

Append to `code/hackathon/pagetests/defaults.test.mjs`:

```js
test('app.js wires the hand in replay mode: built at boot, fed cues, cancelled off the human turn and on restart; sound turns on at Start when nothing is stored', () => {
  const app = read('js/app.js');
  assert.match(app, /import \{ Hand \} from '\.\/hand\.js\?v=ds8';/);
  assert.match(app, /const SPEED = Number\(new URLSearchParams\(location\.search\)\.get\('speed'\)\) \|\| 1;/);
  assert.match(app, /if \(REPLAY_URL\) app\.hand = new Hand\(\$\('hand'\), \{ stage: \$\('stage'\), targets: handTarget, speed: SPEED \}\);/);
  assert.match(app, /new Player\(replay, feed, \{ speed: SPEED, cue: \(c\) => app\.hand && app\.hand\.run\(c\) \}\)/);
  assert.match(app, /if \(app\.hand && msg\.state !== 'human_turn'\) app\.hand\.cancel\(\);/);
  assert.match(app, /if \(msg\.type === 'restart' && app\.hand\) app\.hand\.cancel\(\);/);
  assert.match(app, /const wantsSound = stored === null \? defaultsFor\(!!REPLAY_URL\)\.sound : stored;/);
  assert.match(app, /\$\('start'\)\.addEventListener\('click', \(\) => \{ if \(!app\.sound\.on\) setSound\(true\); \}, \{ once: true \}\)/);
  assert.ok(!/\?v=ds7/.test(app), 'assets at v=ds8');
});
```

And in `style.test.mjs` the first test already checks `duet.css?v=\w+`; add one line to it after the `tokens load before` assertion:

```js
  assert.ok(!/\?v=ds7/.test(h), 'the page moved to v=ds8 with the hand');
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `node --test pagetests/defaults.test.mjs pagetests/style.test.mjs`
Expected: the two new assertions FAIL.

- [ ] **Step 3: Bump the version everywhere**

From `code/hackathon`:

```bash
sed -i '' 's/?v=ds7/?v=ds8/g' duet/static/index.html duet/static/js/*.js
grep -rn 'v=ds7' duet/static || echo "no ds7 left"
```

Expected: `no ds7 left`.

- [ ] **Step 4: Wire the hand and the sound default**

In `code/hackathon/duet/static/js/app.js`:

Add the import after the `GhostPen` import:

```js
import { Hand } from './hand.js?v=ds8';
```

Change the `initUI` import to bring `defaultsFor`:

```js
import { initUI, defaultsFor } from './ui.js?v=ds8';
```

After the `REPLAY_URL` constant add:

```js
/** `?speed=2` runs the recording, and the hand, twice as fast. */
const SPEED = Number(new URLSearchParams(location.search).get('speed')) || 1;
```

In the `app` object add `hand: null,` after `feed: null, replay: null,`.

Change `send`:

```js
export function send(msg) {
  if (!msg) return;
  if (app.replay) {                                                  // the recording answers Go, Pause, Start, and an artist pick
    if (msg.type === 'restart' && app.hand) app.hand.cancel();
    app.replay.command(msg); record((t, seq) => sentEntry(msg, t, seq)); return;
  }
  if (!(app.ws && app.ws.readyState === 1)) return;
  app.ws.send(JSON.stringify(msg));
  record((t, seq) => sentEntry(msg, t, seq));
}
```

In `handle`, case `'state'`, add as the first line after `app.state = msg;`:

```js
      if (app.hand && msg.state !== 'human_turn') app.hand.cancel();                 // the visitor's part is over
```

In `startReplay`, replace the `speed` line and the Player construction:

```js
    const feed = (msg) => { const text = JSON.stringify(msg); const m = parseMessage(text); record((t, seq) => frameEntry(text, m, t, seq)); app.diagView.blink(); if (m) handle(m); };
    app.replay = new Player(replay, feed, { speed: SPEED, cue: (c) => app.hand && app.hand.run(c) });
```

(delete the old `const speed = Number(new URLSearchParams(location.search).get('speed')) || 1;` line.)

In `boot()`, after `app.ghost = new GhostPen(...)`, add:

```js
  const handTarget = (name, cue) => (name === 'picker' ? $('artist-btn') : name === 'go' ? $('go')
    : document.querySelector(`#artist-menu button[data-v="${CSS.escape(cue.artist || '')}"]`));
  if (REPLAY_URL) app.hand = new Hand($('hand'), { stage: $('stage'), targets: handTarget, speed: SPEED });
```

Replace the sound block from `let remembered = false;` through the `if (remembered) …` line with:

```js
  let stored = null;
  try { stored = JSON.parse(localStorage.getItem('duet.sound')); } catch { /* fine */ }
  const wantsSound = stored === null ? defaultsFor(!!REPLAY_URL).sound : stored;
  if (wantsSound) soundBtn.textContent = 'Sound: click to enable';        // audio needs a gesture; the label invites it
  if (wantsSound && stored === null) $('start').addEventListener('click', () => { if (!app.sound.on) setSound(true); }, { once: true });   // the demo: Start is the gesture
```

- [ ] **Step 5: Run all the tests**

Run: `node --test 'pagetests/*.test.mjs'`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add code/hackathon/duet/static
git commit -m "feat(page): the demo hand runs on the Player's cues and stops off the human turn; sound on at Start in the demo; assets at v=ds8"
```

---

### Task 7: Rebuild the site and walk the demo in the browser

**Files:**
- Modify: `site/demo/**` (generated)

- [ ] **Step 1: Rebuild the demo folder**

From the repository root (the worktree has no `sessions/` folder; the recordings live in the main checkout):

```bash
code/hackathon/.venv/bin/python site/build.py --session 20260919-151119 --sessions <main checkout>/code/hackathon/sessions
git status --short site | head -20
git diff --stat site/demo/replay.json
```

Expected: `site written to …: session 20260919-151119, 10 turns, …`. `site/demo/static/**`, `site/demo/index.html` changed; `replay.json` unchanged (empty diff stat). If `replay.json` differs, run the build with plain `python3` instead and compare again; commit whichever matches the current file, since this work does not change the recording.

- [ ] **Step 2: Walk the demo**

The local server from earlier serves `site/` on port 8090 (`preview_start` name `showcase`). Reload `http://localhost:8090/demo/` in the browser pane with a cleared `localStorage` for the origin (`localStorage.clear()` then reload) so the defaults apply, then:

1. Read the page: the artist chip is `as Abstract ▾` and disabled until Start; the body has the `crop` class; the Layers row shows Ink off; the ink swatch is `#37e65b`, the strokes swatch `#1fcf4f`, the width sliders 38 and 24; Bright `+0.00`, Contrast `0.84`, Exposure `+1.4`; the sound chip reads `Sound: click to enable`.
2. Press Start. The sound chip reads `Sound on`. Within a second the hand appears, glides to the picker, the menu opens, the hand glides to Mimic, the menu closes with the chip reading `as Mimic ▾`, the hand glides to Go and presses it, the state chip turns to `Let me look…`. Take a screenshot while the menu is open.
3. On exchange 2 (`as Mimic ▾`), the hand goes straight to Go.
4. On exchange 3, before the hand moves, click the picker yourself and pick Haring: the chip reads `as Haring ▾`. The hand still presses Go; at capture the picker reads `Mimic is looking…`.
5. `read_console_messages` with `onlyErrors`: none.
6. Press Home in the top-right row, then Play the demo again: the welcome's Start runs the piece again from Abstract.

- [ ] **Step 3: Commit the built site**

```bash
git add site/demo
git commit -m "chore(site): rebuild the demo with the hand, the openable picker, and the demo defaults"
```

---

## Self-review

- **Spec coverage.** §2 schedule and Player: Tasks 1 and 2. §3 hand module, markup, styles: Tasks 3 and 4; wiring in `app.js`: Task 6. §4 the blocking rule: Task 4. §5 defaults and sound: Tasks 5 and 6. §6 versions and the site: Tasks 6 and 7. §7 tests: each task carries its own; the browser walk is Task 7.
- **Names.** `DEFAULT_ARTIST`, `PICKABLE`, `Player.pick`, `Player.cue` (Tasks 1–2); `plan`, `Hand`, `HAND`, `Hand.run/cancel/press/moveTo/target` (Task 3); `LIVE_DEFAULTS`, `DEMO_DEFAULTS`, `defaultsFor` (Task 5, imported in Task 6); `handTarget`, `SPEED`, `app.hand` (Task 6). The `targets(name, cue)` signature of Task 3 matches `handTarget` in Task 6.
- **Cue on End.** With `ended` set, `start()` skips every step until the `finish` emit, cue steps included, so the hand never runs during a jump to the end. Cancelling on the `finish` state hides a hand mid-run.
