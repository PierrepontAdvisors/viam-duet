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
