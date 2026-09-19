/** Boot: the WebSocket with snapshot and reconnect, message dispatch, and the modules. */
import { parseMessage, setCommand, command } from './protocol.js?v=ds4';
import { TurnBook } from './story.js?v=ds4';
import { Viewer } from './viewer.js?v=ds4';
import { initUI } from './ui.js?v=ds4';
import { GhostPen } from './preview.js?v=ds4';
import { Sound } from './audio.js?v=ds4';
import { polylinesFromSvg } from './picture.js?v=ds4';
import { homography, applyH, boardOrder, containRect, BOARD_MM } from './geometry.js?v=ds4';

const $ = (id) => document.getElementById(id);
export const app = {
  book: new TurnBook(),
  state: null, currentTurn: null, session: null, robotDone: [], calib: null, human: { polylines: [], new: [] }, plan: null, progress: -1, interpretation: null, dock: null, video: null,
  ws: null, connected: false,
  viewer: null,
  listeners: [],
};
export const on = (fn) => app.listeners.push(fn);
const notify = (msg) => app.listeners.forEach(fn => fn(msg, app));
/** The exchange a per-turn message belongs to. The backend's state.turn counts completed exchanges, so
 *  messages carry their own turn; without it the message is taken to be the current state's. */
const turnOf = (msg) => { const t = msg.turn ?? (app.state ? app.state.turn : 0); app.currentTurn = t; return t; };

export function send(msg) { if (msg && app.ws && app.ws.readyState === 1) app.ws.send(JSON.stringify(msg)); }
export const sendSet = (changes) => send(setCommand(changes));
export const sendCommand = (kind) => send(command(kind));

/** The current plan's strokes are done once the next plan arrives or the piece finishes; keep them. */
function archivePlan() {
  if (!app.plan) return;
  app.robotDone = [...app.robotDone, ...app.plan.polylines];
  app.plan = null; app.progress = -1;
  app.viewer.setDone(app.robotDone); app.viewer.setPlan([], -1);
}
function startSession() {
  app.robotDone = []; app.plan = null; app.progress = -1; app.book = new TurnBook(); app.backfilled = new Set();
  app.viewer.setDone([]); app.viewer.setPlan([], -1);
}

/** A page that joins mid-session only gets the latest plan in the snapshot. The recorder saved every
 *  earlier plan as plan-NN.svg, so fetch the completed turns' robot strokes from there, once each. */
async function backfillPlans(session, completedTurns) {
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

function handle(msg) {
  switch (msg.type) {
    case 'calib': app.calib = msg; app.viewer.setCalib(msg); break;
    case 'state':
      if (msg.session && app.session && msg.session !== app.session) startSession();   // a new piece: forget the last one's strokes
      if (msg.session) app.session = msg.session;
      app.state = msg;
      if (['human_turn', 'finished', 'paused', 'idle'].includes(msg.state)) app.ghost.stop();
      if (msg.state === 'finished') archivePlan();                                        // the signature joins the finished vector
      if (msg.session && msg.turn > 0) backfillPlans(msg.session, msg.turn);
      break;
    case 'human': app.human = msg; app.viewer.setInk(msg.polylines); app.book.note(turnOf(msg), { new: msg.new }); break;
    case 'interpretation': app.interpretation = msg; app.book.note(turnOf(msg), { thought: msg.thought, quip: msg.quip, sees: msg.sees, adds: msg.adds, source: msg.source, latency_s: msg.latency_s }); break;
    case 'plan': archivePlan(); app.plan = msg;
      if (app.state && app.state.state === 'finished') { app.book.note(turnOf(msg), { plan: msg.polylines }); archivePlan(); break; } app.progress = -1; app.viewer.setPlan(msg.polylines, -1); app.book.note(turnOf(msg), { plan: msg.polylines }); (app.backfilled = app.backfilled || new Set()).add(turnOf(msg)); app.ghost.play(msg.polylines); break;
    case 'progress': app.progress = msg.stroke; if (app.plan) app.viewer.setPlan(app.plan.polylines, msg.stroke); turnOf(msg); break;
    case 'shot': {
      const known = app.book.shots.length;
      if (!known) app.book.backfill(msg).forEach(s => app.book.addShot(s));
      app.book.addShot(msg); break;
    }
    case 'video': app.video = msg; break;
    case 'dock': app.dock = msg; break;
    case 'error': break;
  }
  notify(msg);
}

function connect() {
  const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`);
  app.ws = ws;
  ws.onopen = () => { app.connected = true; notify({ type: 'socket', connected: true }); };
  ws.onclose = () => { app.connected = false; notify({ type: 'socket', connected: false }); setTimeout(connect, 1000); };
  ws.onmessage = (e) => { const m = parseMessage(e.data); if (m) handle(m); else console.warn('dropped message', e.data.slice(0, 120)); };
}

export function boot() {
  app.viewer = new Viewer({ stage: $('stage'), pic: $('pic'), base: $('base'), photo: $('photo'), ov: $('ov'), fit: $('fit'),
                            mask: $('mask'), maskpath: $('maskpath'), ink: $('l-ink'), robot: $('l-robot'), done: $('l-done') });
  app.ghost = new GhostPen($('l-ghost'), $('ghostpath'), $('ghostpen'));
  app.viewer.setStream('/stream.mjpg?overlay=0');
  app.ui = initUI(app, { sendSet, sendCommand, on });
  app.sound = new Sound();
  const soundBtn = $('sound');
  const setSound = (onOff) => {
    app.sound.enable(onOff);
    soundBtn.textContent = onOff ? 'Sound on' : 'Sound off'; soundBtn.classList.toggle('on', onOff);
    try { localStorage.setItem('duet.sound', JSON.stringify(onOff)); } catch { /* fine */ }
  };
  soundBtn.onclick = () => setSound(!app.sound.on);
  let remembered = false;
  try { remembered = JSON.parse(localStorage.getItem('duet.sound') || 'false'); } catch { /* fine */ }
  if (remembered) soundBtn.textContent = 'Sound: click to enable';       // audio needs a gesture; the label invites it
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
  connect();
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
