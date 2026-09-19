/** Boot: the WebSocket with snapshot and reconnect, message dispatch, and the modules. */
import { parseMessage, setCommand, command } from './protocol.js';
import { TurnBook } from './story.js';
import { Viewer } from './viewer.js';
import { initUI } from './ui.js';

const $ = (id) => document.getElementById(id);
export const app = {
  book: new TurnBook(),
  state: null, calib: null, human: { polylines: [], new: [] }, plan: null, progress: -1, interpretation: null, dock: null, video: null,
  ws: null, connected: false,
  viewer: null,
  listeners: [],
};
export const on = (fn) => app.listeners.push(fn);
const notify = (msg) => app.listeners.forEach(fn => fn(msg, app));
const turnOf = (msg) => (msg.turn ?? (app.state ? app.state.turn : 0));

export function send(msg) { if (msg && app.ws && app.ws.readyState === 1) app.ws.send(JSON.stringify(msg)); }
export const sendSet = (changes) => send(setCommand(changes));
export const sendCommand = (kind) => send(command(kind));

function handle(msg) {
  switch (msg.type) {
    case 'calib': app.calib = msg; app.viewer.setCalib(msg); break;
    case 'state': app.state = msg; break;
    case 'human': app.human = msg; app.viewer.setInk(msg.polylines); app.book.note(turnOf(msg), { new: msg.new }); break;
    case 'interpretation': app.interpretation = msg; app.book.note(turnOf(msg), { thought: msg.thought, quip: msg.quip, sees: msg.sees, adds: msg.adds, source: msg.source, latency_s: msg.latency_s }); break;
    case 'plan': app.plan = msg; app.progress = -1; app.viewer.setPlan(msg.polylines, -1); app.book.note(turnOf(msg), { plan: msg.polylines }); break;
    case 'progress': app.progress = msg.stroke; if (app.plan) app.viewer.setPlan(app.plan.polylines, msg.stroke); break;
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
                            mask: $('mask'), maskpath: $('maskpath'), ink: $('l-ink'), robot: $('l-robot') });
  app.viewer.setStream('/stream.mjpg?overlay=0');
  app.ui = initUI(app, { sendSet, sendCommand, on });
  connect();
}

boot();
