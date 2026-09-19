/** The page's side of the Duet WebSocket protocol: validate what arrives, build what is sent. No DOM. */

const num = (v, d = null) => (typeof v === 'number' && Number.isFinite(v) ? v : (typeof v === 'string' && v.trim() !== '' && Number.isFinite(+v) ? +v : d));
const int = (v, d = null) => { const n = num(v, null); return n === null ? d : Math.trunc(n); };
const str = (v, d = '') => (typeof v === 'string' ? v : d);
const strOrNull = (v) => (typeof v === 'string' ? v : null);
const bool = (v, d = false) => (typeof v === 'boolean' ? v : d);
const oneOf = (v, allowed, d) => (allowed.includes(v) ? v : d);
const point = (p) => Array.isArray(p) && p.length >= 2 && num(p[0]) !== null && num(p[1]) !== null;
const pair = (v, d) => (Array.isArray(v) && v.length === 2 && num(v[0]) !== null && num(v[1]) !== null ? [num(v[0]), num(v[1])] : d);

export function polylines(v) {
  if (!Array.isArray(v)) return [];
  return v.filter(Array.isArray).map(pl => pl.filter(point).map(p => [num(p[0]), num(p[1])])).filter(pl => pl.length > 0);
}

export const SHOT_WHO = ['start', 'human', 'robot', 'final'];
const SHOT_RE = /\/sessions\/([^/]+)\/turn-(\d+)-(start|human|robot|final)(-frame)?\.jpg$/;

export function shotUrl(session, turn, who, frame = false) {
  return `/sessions/${session}/turn-${String(turn).padStart(2, '0')}-${who}${frame ? '-frame' : ''}.jpg`;
}

export function parseShotUrl(url) {
  const m = typeof url === 'string' ? url.match(SHOT_RE) : null;
  return m ? { session: m[1], turn: +m[2], who: m[3], frame: !!m[4] } : null;
}

const PARSERS = {
  state(m) {
    if (typeof m.state !== 'string' || int(m.turn) === null) return null;
    return {
      state: m.state, turn: int(m.turn), exchanges: int(m.exchanges, 5), length: oneOf(m.length, ['short', 'medium', 'long'], 'short'),
      artist: str(m.artist, 'haring'), mode: str(m.mode, 'duet'), handoff: oneOf(m.handoff, ['held', 'dock'], 'held'),
      coverage: num(m.coverage, 0), error: strOrNull(m.error), at_look: bool(m.at_look), hand_guard: str(m.hand_guard, ''),
      session: strOrNull(m.session), artists: Array.isArray(m.artists) && m.artists.every(a => typeof a === 'string') && m.artists.length ? m.artists : ['haring'],
      direction: num(m.direction, 0), energy: num(m.energy, 0.5),
    };
  },
  calib(m) {
    const marks = Array.isArray(m.marks_image) && m.marks_image.length === 4 && m.marks_image.every(point)
      ? m.marks_image.map(p => [num(p[0]), num(p[1])]) : null;
    const tl = int(m.board_tl_index);
    if (!marks || tl === null || tl < 0 || tl > 3) return null;
    const f = m.cam_to_robot || {};
    const fit = ['ax', 'bx', 'ay', 'by'].every(k => num(f[k]) !== null) ? { ax: f.ax, bx: f.bx, ay: f.ay, by: f.by } : { ax: 1, bx: 0, ay: 1, by: 0 };
    return { marks_image: marks, board_tl_index: tl, board_mm: pair(m.board_mm, [176, 240]), image_size: pair(m.image_size, [1280, 720]), cam_to_robot: fit };
  },
  human: (m) => ({ polylines: polylines(m.polylines), new: polylines(m.new), found: bool(m.found, true), turn: int(m.turn, null) }),
  interpretation(m) {
    return { sees: str(m.sees), adds: str(m.adds), thought: str(m.thought), quip: str(m.quip),
      source: oneOf(m.source, ['claude', 'fallback', 'ink'], 'claude'), latency_s: num(m.latency_s, null), error: strOrNull(m.error), turn: int(m.turn, null),
      artist: strOrNull(m.artist) };
  },
  plan: (m) => ({ polylines: polylines(m.polylines), color: /^#[0-9a-fA-F]{6}$/.test(m.color || '') ? m.color : '#1b8f3a', budget_mm: num(m.budget_mm, 0), turn: int(m.turn, null),
    artist: strOrNull(m.artist) }),
  progress(m) { const s = int(m.stroke); return s === null ? null : { stroke: s, drawn_mm: num(m.drawn_mm, 0), turn: int(m.turn, null) }; },
  shot(m) {
    if (typeof m.url !== 'string') return null;
    const p = parseShotUrl(m.url) || {};
    const who = oneOf(m.who, SHOT_WHO, p.who || 'human');
    return { url: m.url, frame_url: strOrNull(m.frame_url), turn: int(m.turn, p.turn ?? 0), who, session: p.session || null, artist: strOrNull(m.artist) };
  },
  video: (m) => (typeof m.url === 'string' ? { url: m.url } : null),
  dock: (m) => ({ slots: m.slots && typeof m.slots === 'object' ? m.slots : {}, reseat: Array.isArray(m.reseat) ? m.reseat.filter(s => typeof s === 'string') : [] }),
  error: (m) => (typeof m.message === 'string' ? { message: m.message } : null),
};

/** A validated message object with a `type`, or null when the text is not something the page knows. */
export function parseMessage(text) {
  let raw;
  try { raw = JSON.parse(text); } catch { return null; }
  if (!raw || typeof raw !== 'object' || Array.isArray(raw) || typeof raw.type !== 'string') return null;
  const parse = PARSERS[raw.type];
  if (!parse) return null;
  const body = parse(raw);
  return body ? { type: raw.type, ...body } : null;
}

export const SETTINGS = ['artist', 'length', 'exchanges', 'mode', 'handoff', 'energy', 'direction'];
const COMMANDS = ['pause', 'resume', 'pass', 'clear_error', 'restart', 'reset_arm'];   // restart: start a new session in place (the backend may not know it yet)

export function setCommand(changes) {
  const out = { type: 'set' };
  for (const k of SETTINGS) if (k in changes) out[k] = changes[k];
  return Object.keys(out).length > 1 ? out : null;
}

export function command(kind) {
  if (!COMMANDS.includes(kind)) throw new Error(`unknown command ${kind}`);
  return { type: kind };
}
