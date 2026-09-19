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

const q = (s, n = 40) => { const v = String(s ?? ''); return `"${v.length > n ? `${v.slice(0, n - 1)}…` : v}"`; };
const fix = (v, d) => (isNum(v) ? v.toFixed(d) : '?');
const count = (v) => (Array.isArray(v) ? v.length : 0);
const artist = (m) => (typeof m.artist === 'string' && m.artist ? ` · ${m.artist}` : '');   // the turn's artist, when the message names one

const SUMMARY = {
  state: (m) => [`${m.state} · turn ${m.turn} of ${m.exchanges ?? '?'}`, m.at_look ? 'at look' : null, m.error ? `error: ${m.error}` : null].filter(Boolean).join(' · '),
  progress: (m) => `stroke ${m.stroke} · ${m.drawn_mm ?? 0} mm`,
  interpretation: (m) => (m.source === 'fallback' ? `fallback · ${m.error || 'outline and ticks around the new mark'}`
    : `${m.source || 'claude'} ${fix(m.latency_s, 1)} s · sees ${q(m.sees)} · adds ${q(m.adds)}`) + artist(m),
  plan: (m) => `${count(m.polylines)} strokes · ${countPoints(m.polylines)} points · budget ${m.budget_mm ?? 0} mm · ${m.color || ''}` + artist(m),
  human: (m) => `${count(m.polylines)} strokes · ${count(m.new)} new · ${m.found === false ? 'not found' : 'found'}`,
  shot: (m) => `${m.who || '?'} · turn ${m.turn ?? '?'}${m.frame_url ? ' · +frame' : ''}` + artist(m),
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

/** The drawer's summary numbers. */
export function header(entries, now, connected) {
  const ins = entries.filter(e => e.dir === 'in');
  const opens = entries.filter(e => e.dir === 'ws' && e.type === 'open').length;
  return { connected, sinceLastMs: ins.length ? now - ins[ins.length - 1].t : null, received: ins.length,
           sent: entries.filter(e => e.dir === 'out').length, reconnects: Math.max(0, opens - 1), dropped: ins.filter(e => !e.ok).length };
}

/** Connected and disconnected stretches across the window, from the socket events in time order. With no
 *  events the window takes `connected`. Before the first known event nothing is drawn, unless the log has hit
 *  its cap (older events fell off), when the state is taken to be the opposite of that event. */
function socketBands(entries, now, windowMs, connected) {
  const events = entries.filter(e => e.dir === 'ws' && e.t <= now).map(e => ({ t: e.t, connected: e.type === 'open' }));
  if (!events.length) return [{ x0: 0, x1: 1, connected }];
  const start = now - windowMs, frac = (t) => (t - start) / windowMs;
  let state = entries.length >= CAP ? !events[0].connected : null, from = start;
  const out = [];
  for (const ev of events) {
    if (ev.t <= start) { state = ev.connected; continue; }
    if (state !== null) out.push({ x0: frac(from), x1: frac(ev.t), connected: state });
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
