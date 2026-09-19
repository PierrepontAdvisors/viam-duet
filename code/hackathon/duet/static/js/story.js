/** The storybook layer's words and bookkeeping: what the chips and bubbles say in each state, and the
 *  per-turn record of thoughts, quips, ink, plans, and photos. No DOM here. */
import { centroid, BOARD_CENTER } from './geometry.js?v=ds6';
import { shotUrl } from './protocol.js?v=ds6';

export const PLACEHOLDERS = ['Hmm…', 'Looking closely…', 'What could it be?', 'I see lines…'];
export const PLACEHOLDER_MS = 1500;

export const FIXED = {
  start: 'Your turn! Draw one mark, then press Go.',
  reseat: 'Please pop the marker back in its cap.',
  noQuip: 'Here we go!',
  oldThought: 'Hmm, what was this?',
  oldQuip: 'I remember this one!',
};

/* ---- artists: the picker's names and one-line descriptions, in the backend's display order ---- */
export const ARTIST_INFO = {
  abstract: ['Abstract', 'Clean shapes that answer yours'],
  mimic: ['Mimic', 'Copies what you just drew'],
  haring: ['Haring', 'Bold outlines and motion ticks'],
  mondrian: ['Mondrian', 'Straight lines, grids, boxes'],
  vangogh: ['Van Gogh', 'Swirls of curved dashes'],
  architect: ['Architect', 'Walls, doors, stairs, rooflines'],
  designer: ['Designer', 'Rounded housings and parts'],
  shader: ['Shader', 'Fills your shapes with dots'],
};
export function artistName(id) {
  if (ARTIST_INFO[id]) return ARTIST_INFO[id][0];
  return id ? id.charAt(0).toUpperCase() + id.slice(1) : '';
}
const LOOKING = ['capture', 'interpret'], DRAWING = ['plan', 'robot_draw'];
/** The artist picker's label and whether it opens. `setting` is the current artist setting, `turnArtist`
 *  the artist fixed for the exchange in progress (null until the backend has said), `shot` the browsed
 *  photo or null when the live picture shows. Null hides the picker. */
export function pickerText(state, setting, turnArtist, shot) {
  if (shot) return shot.who === 'robot' && shot.artist ? { text: `${artistName(shot.artist)} drew this`, open: false } : null;
  if (state === 'human_turn') return { text: `as ${artistName(setting)} ▾`, open: true };
  const who = artistName(turnArtist || setting);
  if (LOOKING.includes(state)) return { text: `${who} is looking…`, open: false };
  if (DRAWING.includes(state)) return { text: `${who} is drawing`, open: false };
  return null;
}

// chip: [text, tone]; bubble: [kind, text | null for "thought or placeholder" | 'quip' for the turn's quip]
const TABLE = {
  idle: { chip: ['Getting ready…', 'white'], bubble: ['speech', 'One moment…'] },
  look: { chip: ['Getting ready…', 'white'], bubble: ['speech', 'One moment…'] },
  human_turn: { chip: ['Your turn!', 'green'], bubble: ['speech', FIXED.start] },
  capture: { chip: ['Let me look…', 'white'], bubble: ['thought', null] },
  interpret: { chip: ['Let me look…', 'white'], bubble: ['thought', null] },
  plan: { chip: ['I have an idea!', 'yellow'], bubble: ['speech', 'quip'] },
  robot_draw: { chip: ['My turn! Hands off, please', 'red'], bubble: ['speech', 'quip'] },
  finish: { chip: ['Signing…', 'green'], bubble: ['speech', 'All done! Thank you.'] },
  finished: { chip: ['The end', 'yellow'], bubble: ['speech', 'That was fun. Play it back?'] },
  paused: { chip: ['Paused', 'red'], bubble: ['speech', 'One moment, please.'] },
};

export function chipFor(state) {
  const e = TABLE[state];
  return e ? { text: e.chip[0], tone: e.chip[1] } : { text: String(state).replace(/_/g, ' '), tone: 'white' };
}

export function placeholderAt(ms) {
  return PLACEHOLDERS[Math.floor(ms / PLACEHOLDER_MS) % PLACEHOLDERS.length];
}

/** What the bubble shows for a live session state. `record` is this turn's TurnBook entry or null. */
export function bubbleForState(state, record, { reseat = false, elapsedMs = 0 } = {}) {
  if (reseat) return { kind: 'speech', text: FIXED.reseat };
  const [kind, spec] = (TABLE[state] || TABLE.idle).bubble;
  if (spec === null) return { kind, text: (record && record.thought) || placeholderAt(elapsedMs) };
  if (spec === 'quip') return { kind, text: (record && record.quip) || FIXED.noQuip };
  return { kind, text: spec };
}

/** What the bubble shows while browsing a turn photo: the story follows the photo, not the state. */
export function bubbleForShot(who, record) {
  if (who === 'start') return { kind: 'speech', text: FIXED.start };
  if (who === 'human') return { kind: 'thought', text: (record && record.thought) || FIXED.oldThought };
  return { kind: 'speech', text: (record && record.quip) || FIXED.oldQuip };
}

const WHO_ORDER = { start: 0, human: 1, robot: 2, final: 3 };

export class TurnBook {
  constructor() { this.turns = new Map(); this.shots = []; }

  note(turn, fields) {
    this.turns.set(turn, { ...(this.turns.get(turn) || {}), ...fields });
  }

  get(turn) { return this.turns.get(turn) || null; }

  indexOf(turn, who) { return this.shots.findIndex(s => s.turn === turn && s.who === who); }

  /** Insert or replace a shot, keep story order, return its index. */
  addShot(shot) {
    const i = this.indexOf(shot.turn, shot.who);
    if (i >= 0) this.shots[i] = shot; else this.shots.push(shot);
    this.shots.sort((a, b) => a.turn - b.turn || WHO_ORDER[a.who] - WHO_ORDER[b.who]);
    return this.indexOf(shot.turn, shot.who);
  }

  /** The shots that must exist before `latest` in a normal session, built from the url pattern. */
  backfill(latest) {
    if (!latest.session) return [];
    const frames = !!latest.frame_url, out = [];
    const make = (turn, who) => ({ url: shotUrl(latest.session, turn, who), frame_url: frames ? shotUrl(latest.session, turn, who, true) : null, turn, who, session: latest.session });
    if (latest.turn > 0 || WHO_ORDER[latest.who] > 0) out.push(make(0, 'start'));
    for (let t = 1; t <= latest.turn; t++) {
      for (const who of ['human', 'robot']) {
        if (t < latest.turn || WHO_ORDER[who] < WHO_ORDER[latest.who]) out.push(make(t, who));
      }
    }
    return out;
  }

  loopSchedule(perFrameMs = 1000, holdLastMs = 2000) {
    return this.shots.map((_, i) => (i === this.shots.length - 1 ? holdLastMs : perFrameMs));
  }
}

/** Where a bubble points, in board mm: a thought at this turn's new ink, a speech at the plan. */
export function anchorFor(kind, record) {
  if (kind === 'thought') return centroid((record && record.new) || []);
  if (kind === 'speech') return centroid((record && record.plan) || []);
  return [...BOARD_CENTER];
}

/* ---- welcome page ---- */
export const FRESH_STATES = ['idle', 'start'];   // not look: the loop passes through look after every robot turn
export const WELCOME_RETURN_MS = 8000;
/** The welcome page's button for a state: its label and whether it can be pressed. `waiting` is set after
 *  Start was pressed on a finished session, until a new session's state arrives. */
export function welcomeButton(state, waiting = false) {
  if (waiting) return { label: 'Starting soon…', enabled: false };
  if (state === 'human_turn' || state === 'finished') return { label: 'Start', enabled: true };
  return { label: 'Getting ready…', enabled: false };
}
/** The welcome returns when a fresh session begins after a session that was under way or finished:
 *  a restarted process or a restart in place looks like idle or start arriving after anything else. */
export function welcomeReturns(prev, next) {
  return FRESH_STATES.includes(next) && prev != null && !FRESH_STATES.includes(prev);
}
