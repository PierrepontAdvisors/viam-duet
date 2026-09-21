/** Boot: the WebSocket with snapshot and reconnect, message dispatch, and the modules. */
import { parseMessage, setCommand, command } from './protocol.js?v=ds9';
import { TurnBook } from './story.js?v=ds9';
import { Viewer } from './viewer.js?v=ds9';
import { initUI, defaultsFor } from './ui.js?v=ds9';
import { GhostPen } from './preview.js?v=ds9';
import { Hand } from './hand.js?v=ds9';
import { Clock } from './clock.js?v=ds9';
import { Sound } from './audio.js?v=ds9';
import { polylinesFromSvg } from './picture.js?v=ds9';
import { homography, applyH, boardOrder, containRect, BOARD_MM } from './geometry.js?v=ds9';

import { append, frameEntry, sentEntry, socketEntry } from './diag.js?v=ds9';
import { initDiagView } from './diagview.js?v=ds9';

const $ = (id) => document.getElementById(id);
/** The showcase site sets <meta name="duet-replay" content="replay.json">: no socket, a recording drives the page. */
const REPLAY_URL = (document.querySelector('meta[name="duet-replay"]') || {}).content || null;
/** `?speed=2` runs the recording, and the hand, twice as fast. */
const SPEED = Number(new URLSearchParams(location.search).get('speed')) || 1;
export const app = {
  book: new TurnBook(),
  state: null, currentTurn: null, session: null, robotDone: [], calib: null, human: { polylines: [], new: [] }, plan: null, progress: -1, interpretation: null, dock: null, video: null,
  feed: null, replay: null, hand: null, pen: null, clock: null,
  ws: null, connected: false,
  diag: { entries: [], seq: 0 }, diagView: null,
  viewer: null,
  listeners: [],
};
export const on = (fn) => app.listeners.push(fn);
const notify = (msg) => app.listeners.forEach(fn => fn(msg, app));
/** The exchange a per-turn message belongs to. The backend's state.turn counts completed exchanges, so
 *  messages carry their own turn; without it the message is taken to be the current state's. */
const turnOf = (msg) => { const t = msg.turn ?? (app.state ? app.state.turn : 0); app.currentTurn = t; return t; };

/** Diagnostics: every frame in, every command out, and the socket's own events, kept for the drawer. */
function record(make) {
  const seq = app.diag.seq + 1;
  app.diag = { entries: append(app.diag.entries, make(Date.now(), seq)), seq };
  if (app.diagView) app.diagView.onEntry(app.diag.entries);
}
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
export const sendSet = (changes) => send(setCommand(changes));
export const sendCommand = (kind) => send(command(kind));
/** Arrow keys in the demo: the recording moves by a half-exchange, after what animates on its own has stopped. */
function seek(delta) {
  if (!app.replay) return;
  app.hand.cancel(); app.ghost.stop(); app.clock.stop();
  send({ type: 'seek', delta });
}

/** The current plan's strokes are done once the next plan arrives or the piece finishes; keep them. */
function archivePlan() {
  if (!app.plan) return;
  app.robotDone = [...app.robotDone, ...app.plan.polylines];
  app.plan = null; app.progress = -1;
  app.viewer.setDone(app.robotDone); app.viewer.setPlan([], -1);
}
function startSession() {
  app.robotDone = []; app.plan = null; app.progress = -1; app.book = new TurnBook(); app.backfilled = new Set();
  app.video = null; app.human = { polylines: [], new: [] }; app.interpretation = null; app.dock = null;   // feed stays: it is about the rig, not the piece
  app.viewer.setInk([]); app.viewer.setDone([]); app.viewer.setPlan([], -1);
}

/** A page that joins mid-session only gets the latest plan in the snapshot. The recorder saved every
 *  earlier plan as plan-NN.svg, so fetch the completed turns' robot strokes from there, once each. */
async function backfillPlans(session, completedTurns) {
  if (REPLAY_URL) return;                                  // every plan arrives from the recording in order
  app.backfilled = app.backfilled || new Set();
  for (let t = 1; t <= completedTurns; t++) {
    if (app.backfilled.has(t) || (app.book.get(t) || {}).plan) continue;
    app.backfilled.add(t);
    try {
      const r = await fetch(`/sessions/${session}/plan-${String(t).padStart(2, '0')}.svg`);
      if (!r.ok) continue;
      const { robot } = polylinesFromSvg(await r.text());
      if (!robot.length) continue;
      app.book.note(t, { plan: robot, backfilled: true });
      app.robotDone = [...app.robotDone, ...robot];
      app.viewer.setDone(app.robotDone);
    } catch { /* the file is optional; the live layer still works */ }
  }
}

/** The Robot tag rides the robot pen's dot: a board point places it, null hides it. */
const placeTag = (p) => { const tag = $('pen-tag'), q = p && app.viewer.boardToStage(p); tag.classList.toggle('hidden', !q); if (q) { tag.style.left = `${q[0]}px`; tag.style.top = `${q[1]}px`; } };

/** Replay: the hand, the two pens, and the clock follow the state. A pause holds them where they are and the
 *  first state after it resumes them; a resumed robot_draw keeps its trace instead of starting it again. */
function replayState(msg, wasPaused) {
  if (msg.state === 'paused') { app.hand.pause(); app.ghost.pause(); app.clock.pause(); return; }
  if (wasPaused) { app.hand.resume(); app.ghost.resume(); app.clock.resume(); return; }
  if (msg.state !== 'human_turn') app.hand.cancel();                                    // the visitor's part is over
  if (['human_turn', 'finished', 'idle'].includes(msg.state)) app.ghost.stop();
  if (['look', 'finish', 'finished', 'idle'].includes(msg.state)) app.clock.stop();
  if (msg.state === 'robot_draw' && app.plan && app.replay) app.ghost.play(app.plan.polylines, { durationMs: app.replay.drawMs(app.plan.polylines.length), onMove: placeTag });   // the ghost pen is the arm
}

function handle(msg) {
  switch (msg.type) {
    case 'calib': app.calib = msg; app.viewer.setCalib(msg); break;
    case 'state': {
      const wasPaused = !!(app.state && app.state.state === 'paused');
      if (msg.session && app.session && msg.session !== app.session) { startSession(); msg.fresh = true; }   // a new piece: forget the last one's strokes, and tell the listeners
      if (msg.session) app.session = msg.session;
      app.state = msg;
      if (REPLAY_URL) replayState(msg, wasPaused); else if (['human_turn', 'finished', 'paused', 'idle'].includes(msg.state)) app.ghost.stop();
      if (msg.state === 'finished') archivePlan();                                        // the signature joins the finished vector
      if (msg.session && msg.turn > 0) backfillPlans(msg.session, msg.turn);
      break;
    }
    case 'human': app.human = msg; app.viewer.setInk(msg.polylines); app.book.note(turnOf(msg), { new: msg.new }); break;
    case 'interpretation': app.interpretation = msg; app.book.note(turnOf(msg), { thought: msg.thought, quip: msg.quip, sees: msg.sees, adds: msg.adds, source: msg.source, latency_s: msg.latency_s, ...(msg.artist ? { artist: msg.artist } : {}) }); break;
    case 'plan': archivePlan(); app.plan = msg;
      if (msg.artist) app.book.note(turnOf(msg), { artist: msg.artist });
      if (app.state && app.state.state === 'finished') { app.book.note(turnOf(msg), { plan: msg.polylines }); archivePlan(); break; } app.progress = -1; app.viewer.setPlan(msg.polylines, -1); app.book.note(turnOf(msg), { plan: msg.polylines }); (app.backfilled = app.backfilled || new Set()).add(turnOf(msg)); if (!REPLAY_URL) app.ghost.play(msg.polylines); break;   // live: a preview ahead of the arm; replay: the pen waits for robot_draw
    case 'progress': app.progress = msg.stroke; if (app.plan) app.viewer.setPlan(app.plan.polylines, msg.stroke); turnOf(msg); break;
    case 'shot': {
      const known = app.book.shots.length;
      if (!known) app.book.backfill(msg).forEach(s => app.book.addShot(s));
      if (msg.artist && msg.who !== 'start') app.book.note(msg.turn, { artist: msg.artist });
      if (REPLAY_URL && msg.frame_url) { app.viewer.streamUrl = msg.frame_url; if (app.viewer.live) app.viewer.showLive(); }   // the latest camera frame stands in for the stream
      app.book.addShot(msg); break;
    }
    case 'video': app.video = msg; break;
    case 'feed': app.feed = msg; break;
    case 'dock': app.dock = msg; break;
    case 'error': break;
  }
  notify(msg);
}

function connect() {
  const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`);
  app.ws = ws;
  ws.onopen = () => { app.connected = true; record((t, seq) => socketEntry('open', null, t, seq)); app.diagView.setConnected(true); notify({ type: 'socket', connected: true }); };
  ws.onclose = (e) => { app.connected = false; record((t, seq) => socketEntry('close', e.code, t, seq)); app.diagView.setConnected(false); notify({ type: 'socket', connected: false }); setTimeout(connect, 1000); };
  ws.onmessage = (e) => {
    const m = parseMessage(e.data);
    record((t, seq) => frameEntry(e.data, m, t, seq)); app.diagView.blink();
    if (m) handle(m); else console.warn('dropped message', e.data.slice(0, 120));
  };
}

/** Replay: load the recording and the player, then drive `handle` as the socket would. */
async function startReplay(url) {
  document.body.classList.add('replay');
  for (const id of ['site-home', 'welcome-home']) { const el = $(id); if (el) el.classList.remove('hidden'); }
  try {
    const [{ Player }, replay] = await Promise.all([import('./replay.js?v=ds9'), fetch(url).then(r => { if (!r.ok) throw new Error(`${r.status} for ${url}`); return r.json(); })]);
    const feed = (msg) => { const text = JSON.stringify(msg); const m = parseMessage(text); record((t, seq) => frameEntry(text, m, t, seq)); app.diagView.blink(); if (m) handle(m); };
    app.replay = new Player(replay, feed, { speed: SPEED, cue: (c) => { if (c.hand) app.hand.run(c); if (c.clock) app.clock.start({ who: c.clock, ms: c.ms }); } });
    app.connected = true; app.diagView.setConnected(true); notify({ type: 'socket', connected: true });
    app.replay.boot();
  } catch (err) {
    console.error(err); notify({ type: 'error', message: `the recording did not load: ${err.message}` });
  }
}

export function boot() {
  app.viewer = new Viewer({ stage: $('stage'), pic: $('pic'), base: $('base'), photo: $('photo'), ov: $('ov'), fit: $('fit'),
                            mask: $('mask'), maskpath: $('maskpath'), ink: $('l-ink'), robot: $('l-robot'), done: $('l-done') });
  app.ghost = new GhostPen($('l-ghost'), $('ghostpath'), $('ghostpen'));
  const handTarget = (name, cue) => (name === 'picker' ? $('artist-btn') : name === 'go' ? $('go')
    : name.startsWith('row:') ? document.querySelectorAll('#artist-menu button')[+name.slice(4)]
    : document.querySelector(`#artist-menu button[data-v="${CSS.escape(cue.artist || '')}"]`));
  if (REPLAY_URL) {
    app.pen = new GhostPen($('l-hand'), $('handpath'), $('handpen'));
    app.hand = new Hand($('hand'), { stage: $('stage'), targets: handTarget, tracer: app.pen, toStage: (p) => app.viewer.boardToStage(p), speed: SPEED });
    app.clock = new Clock($('clock'), { who: $('clock-who'), time: $('clock-time') });
    $('clock').onclick = () => sendCommand(app.state && app.state.state === 'paused' ? 'resume' : 'pause');
  }
  if (!REPLAY_URL) app.viewer.setStream('/stream.mjpg?overlay=0');
  app.diagView = initDiagView({ light: $('light'), summary: $('diag-summary'), svg: $('diag-timeline'), tbody: $('diag-rows') });
  app.ui = initUI(app, { sendSet, sendCommand, seek, on, replay: !!REPLAY_URL });
  app.sound = new Sound();
  const soundBtn = $('sound');
  const setSound = (onOff) => {
    app.sound.enable(onOff);
    soundBtn.textContent = onOff ? 'Sound on' : 'Sound off'; soundBtn.classList.toggle('on', onOff);
    try { localStorage.setItem('duet.sound', JSON.stringify(onOff)); } catch { /* fine */ }
  };
  soundBtn.onclick = () => setSound(!app.sound.on);
  let stored = null;
  try { stored = JSON.parse(localStorage.getItem('duet.sound')); } catch { /* fine */ }
  const wantsSound = stored === null ? defaultsFor(!!REPLAY_URL).sound : stored;
  if (wantsSound) soundBtn.textContent = 'Sound: click to enable';        // audio needs a gesture; the label invites it
  if (wantsSound && REPLAY_URL) $('start').addEventListener('click', () => { if (!app.sound.on) setSound(true); }, { once: true });   // the demo: Start is the first gesture, so sound comes on there
  on((msg) => {
    const s = app.sound;
    if (msg.type === 'interpretation') s.speak(msg.thought);
    else if (msg.type === 'progress') s.click();
    else if (msg.type === 'state') {
      s.hum(msg.state === 'capture' || msg.state === 'interpret');
      if (msg.state === 'human_turn' && app.prevState !== 'human_turn') s.chime('yours');
      if (msg.state === 'robot_draw' && app.prevState !== 'robot_draw') s.chime('mine');
      if (msg.state === 'plan' && app.prevState !== 'plan') { const rec = app.book.get(app.currentTurn ?? msg.turn); if (rec) s.speak(rec.quip); }
      app.prevState = msg.state;
    }
  });
  if (REPLAY_URL) startReplay(REPLAY_URL); else connect();
}

boot();

/** `?selftest=1`: the geometry against the served calibration, reported in the console. */
async function selftest() {
  const ok = (name, pass) => console.log(`%c${pass ? 'PASS' : 'FAIL'}%c ${name}`, `color:${pass ? '#1b8f3a' : '#c62828'};font-weight:700`, '');
  const calib = await (await fetch('/calibration.json')).json();
  const quad = boardOrder(calib.marks_image, calib.board_tl_index);
  const corners = [[0, 0], [BOARD_MM[0], 0], [BOARD_MM[0], BOARD_MM[1]], [0, BOARD_MM[1]]];
  const h = homography(corners, quad);
  ok('calibration corners map to the SVG corners within 0.5 px',
     corners.every((c, i) => { const q = applyH(h, c); return Math.hypot(q[0] - quad[i][0], q[1] - quad[i][1]) < 0.5; }));
  const d = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
  ok('board order: tr is the nearer neighbor of tl (the short edge)', d(quad[0], quad[1]) <= d(quad[0], quad[3]));
  ok('contain rect is exact for a 16:9 stage', JSON.stringify(containRect(1600, 900, 1280, 720)) === JSON.stringify({ s: 1.25, ox: 0, oy: 0 }));
  ok('contain rect is exact for a 4:3 stage', JSON.stringify(containRect(1280, 960, 1280, 720)) === JSON.stringify({ s: 1, ox: 0, oy: 120 }));
}
if (new URLSearchParams(location.search).get('selftest') === '1') selftest();
