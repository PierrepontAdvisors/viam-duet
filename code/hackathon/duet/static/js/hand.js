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
