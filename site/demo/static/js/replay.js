/** Replay mode: a recorded session as the same protocol messages the socket would carry, on a clock.
 *  `schedule()` is pure (replay.json in, steps out); `Player` runs the steps and takes the page's
 *  commands. The showcase site loads this module; the live page never does. */
import { planMs } from './hand.js?v=ds9';

export const PACE = { look: 1000, human: 14000, capture: 1000, thinkInk: 1200, thinkClaude: 3500, plan: 1500,
                      strokeMs: 350, drawMin: 3000, drawMax: 12000, settle: 1200, finish: 2000 };
export const ARTISTS = ['abstract', 'mimic', 'haring', 'mondrian', 'vangogh', 'architect', 'designer', 'shader'];
/** The picker's setting before the first exchange: the live page's default. */
export const DEFAULT_ARTIST = 'abstract';
/** The ink artists' own word banks, indexed by exchange exactly as duet/styles/{mimic,shader}.py do. */
export const WORDS = {
  mimic: { thoughts: ['Let me try that…', 'Watch this…', 'One more, my way…'],
           quips: ['Copycat!', 'Like this?', 'Two of a kind!', 'Your move, again.'] },
  shader: { thoughts: ['Where does the light fall?', 'A little shadow…'],
            quips: ['Let me shade that in.', 'Darker here, lighter there.', 'Dots, dots, dots!'] },
};
const BUDGET_MM = { short: 400, medium: 1200, long: 4000 };
const MIN_FRAGMENT_MM = 6;       // the camera trace leaves specks around a mark; the hand draws only what a person would

/** How long the scripted arm draws a plan of n strokes, in ms at the given speed: 350 ms a stroke within 3 to 12 s. */
export function drawMs(strokeCount, speed = 1) {
  if (!strokeCount) return 0;
  return Math.round(Math.min(PACE.drawMax, Math.max(PACE.drawMin, strokeCount * PACE.strokeMs)) / (speed > 0 ? speed : 1));
}

const pad = (n) => String(n).padStart(2, '0');
const strokeLength = (pl) => pl.reduce((s, p, i) => (i ? s + Math.hypot(p[0] - pl[i - 1][0], p[1] - pl[i - 1][1]) : 0), 0);

/** The first `max` words of a sentence, with an ellipsis when it was cut. */
export function clip(text, max = 8) {
  const w = String(text || '').replace(/\s+/g, ' ').trim().split(' ').filter(Boolean);
  if (w.length <= max) return w.join(' ');
  return `${w.slice(0, max).join(' ').replace(/[,.;:]$/, '')}…`;
}

/** The thought and quip for a recorded turn: the ink artists' banks, the build's words for a Claude
 *  turn when it has them, else lines cut from what Claude saw and added. */
export function words(turn) {
  const bank = WORDS[turn.artist];
  const i = Math.max(0, (turn.turn || 1) - 1);
  if (bank) return { thought: turn.thought || bank.thoughts[i % bank.thoughts.length], quip: turn.quip || bank.quips[i % bank.quips.length] };
  return { thought: turn.thought || clip(turn.sees, 6), quip: turn.quip || clip(turn.adds, 8) };
}

export function stateMsg(replay, state, turn, artist, session, coverage = 0) {
  return { type: 'state', state, turn, coverage, error: null, at_look: !['robot_draw', 'finish'].includes(state),
           hand_guard: 'off', session, artists: replay.artists || ARTISTS, artist, length: replay.length || 'long',
           exchanges: replay.exchanges || (replay.turns || []).length, mode: 'duet', handoff: 'held', energy: 0.5, direction: 0, ending: false };
}

/** The piece as steps: `{ emit: msg }` sends a message, `{ wait: ms }` holds, `{ wait, on: 'pass' }`
 *  holds until Go or the time is up, `{ cue }` tells the page what the recorded visitor did and how long each
 *  half takes: `{ hand: 'pick', artist, row, draw }` when they switched artist, `{ hand: 'go', draw }` otherwise,
 *  with `draw` their strokes (specks under 6 mm dropped) and `row` the artist's roster index; `{ clock: 'visitor' | 'robot', ms }`
 *  at each human turn and each capture with that half's scripted time. The picker's
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
  const roster = replay.artists || ARTISTS;
  let setting = DEFAULT_ARTIST;
  const steps = [e(stateMsg(replay, 'look', 0, setting, session)), shot(0, 'start', null, !!frames.start), e({ type: 'feed', source: 'live' }), w(PACE.look)];
  let ink = [], coverage = 0;
  for (const t of turns) {
    const n = t.turn, artist = t.artist;
    const st = (state, turn, who = artist) => e(stateMsg(replay, state, turn, who, session, coverage));
    const draw = (t.new || []).filter(pl => strokeLength(pl) >= MIN_FRAGMENT_MM);
    const handCue = artist === setting ? { hand: 'go', draw } : { hand: 'pick', artist, row: roster.indexOf(artist), draw };
    steps.push(st('human_turn', n - 1, setting), { cue: handCue }, { cue: { clock: 'visitor', ms: planMs(handCue, div) } }, w(PACE.human, 'pass'));
    ink = [...ink, ...(t.new || [])];
    const plan = t.plan || [], think = t.source === 'ink' ? PACE.thinkInk : PACE.thinkClaude;
    steps.push(st('capture', n - 1), { cue: { clock: 'robot', ms: Math.round((PACE.capture + think + PACE.plan + PACE.settle) / div) + drawMs(plan.length, div) } },
               shot(n, 'human', artist, (t.frames || {}).human !== false),
               e({ type: 'human', polylines: ink, new: t.new || [], found: true, turn: n }), w(PACE.capture));
    const { thought, quip } = words(t);
    steps.push(st('interpret', n - 1), w(think),
               e({ type: 'interpretation', sees: t.sees || '', adds: t.adds || '', thought, quip, source: t.source || 'claude',
                   latency_s: t.latency_s ?? null, error: null, turn: n, artist }));
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

const realSleep = (ms) => new Promise((r) => setTimeout(r, ms));
const TICK_MS = 100;

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
