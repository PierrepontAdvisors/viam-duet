# Duet demo: the hand draws the mark, presses like a person, wears a name, and a turn clock that pauses the piece

Date: 2026-09-20, late evening. Status: approved in a brainstorm round (labels, marker, rollovers, the clock's form, and the clock as the pause control chosen by Nicholas). Branch `feat/showcase-site`, worktree `.worktrees/showcase-site`. Parent spec: `2026-09-20-duet-demo-hand-design.md` (the hand, the openable picker, the demo defaults), which this extends; the page's replay mode is in `2026-09-20-duet-showcase-site-design.md`.

## 1. What changes

Five things, all in replay mode only. The live page keeps its behaviour.

1. **The hand draws the visitor's mark.** Each human turn opens with the hand holding a red marker and tracing the exchange's recorded strokes on the board, at the pace of a person, before it reaches for the picker or Go. The red trace vanishes as the capture photo, which shows the real mark, arrives.
2. **The hand presses like a person.** Buttons lift when the hand arrives and squash when it presses, the same toy-press the stylesheet gives a real pointer. On its way down the menu the hand pauses a beat on every row above its target, so each row lifts in turn.
3. **Names.** A "Visitor" pill rides below and right of the hand. A "Robot" pill follows the robot's pen dot while it draws.
4. **A turn clock.** A chip after the state chip reads "Visitor" or "Robot" with the seconds so far, and a bar behind the text fills over the turn's scripted time, red for the visitor and green for the robot. It hides between turns.
5. **The clock pauses the piece.** Clicking the clock pauses the whole replay; clicking again resumes. The hand, both pens, and the clock hold where they are.

## 2. Cues and pace (`duet/static/js/replay.js`)

`PACE.human` rises to 14 s, still a ceiling that the hand's Go press ends early. The hand cue grows:

```
{ cue: { hand: 'pick', artist: 'shader', row: 7, draw: [...] } }     the artist's index in the roster, and the strokes to draw
{ cue: { hand: 'go', draw: [...] } }
```

`draw` is the exchange's `new` strokes from `replay.json` with fragments shorter than 6 mm dropped (the camera trace leaves specks around a mark; the hand draws only what a person would). `row` is `roster.indexOf(artist)`, and -1 when the artist is not on the roster, in which case the hand skips the roll and presses the row it finds by name.

Two clock cues join the schedule, one after the hand cue at each human turn and one right after each `capture` state:

```
{ cue: { clock: 'visitor', ms } }     ms = planMs(handCue, speed): the hand's whole plan summed, drawing included
{ cue: { clock: 'robot', ms } }       ms = (capture + think + plan + settle) / speed + drawMs(plan strokes, speed)
```

where `think` is `thinkInk` or `thinkClaude` by the turn's source. The schedule imports `plan`'s sum, `planMs`, from `hand.js` for the visitor's total; `hand.js` imports nothing from `replay.js`. The Player passes every cue to the same callback; the page routes by key (`hand`, `clock`).

## 3. The hand's plan (`duet/static/js/hand.js`)

Steps, all `ms` divided by `speed`:

| Step | Meaning |
| --- | --- |
| `{ draw: strokes, ms }` | the marker traces the strokes over `ms`; the hand follows the pen's tip |
| `{ glide: target, ms }` | move the fingertip to the target's centre |
| `{ hover: target, ms }` | the target lifts (class `hover`) and holds |
| `{ press: target, ms }` | the target squashes (class `active`) for `ms`, then the click fires on the release and both classes come off |
| `{ wait: ms }` | hold still |

Targets: `picker` (`#artist-btn`), `go` (`#go`), `row` (the menu button whose `data-v` is the cue's artist), and `row:<i>` (the i-th menu button, for the roll).

```
pick:  draw traceMs(strokes)
       glide picker 500 → hover picker 350 → press picker 200
       for i in 0..row:  glide row:i 120 → hover row:i 100     (the last hover, on the target row, holds 350)
       press row 200 → wait 500
       glide go 500 → hover go 350 → press go 200
go:    draw traceMs(strokes) → glide go 500 → hover go 350 → press go 200
```

`traceMs(strokes, speed)`: the strokes' length at 70 mm per second, held between 1.2 s and 4 s, divided by `speed`; 0 for no strokes, and a draw step of 0 ms is skipped. `planMs(cue, speed)` sums a plan's `ms` and `wait` values.

**The runner.** `new Hand(el, { stage, targets, tracer, toStage, speed })`. `tracer` is a pen with `play(strokes, { durationMs, onMove })`, `stop()`, `pause()`, `resume()` (the visitor's red ghost pen, §5); `toStage(p)` turns a board point into stage pixels, null before calibration. The rules of the parent spec stand (skip a hidden target, do not toggle a menu a visitor opened, reopen one that closed). New:

- `draw`: adds class `draw` to the hand (the marker shows), calls `tracer.play(strokes, { durationMs: ms, onMove })`; `onMove(p)` moves the fingertip to `toStage(p)` when that is not null; the class comes off at the next step.
- `hover`: takes `hover` off the previously lifted element, adds it to the target. A hidden target takes no time.
- `press`: adds `active` at once; after `ms` removes `active` and `hover` and calls `click()`. So the menu opens, the row is chosen, and Go fires on the release, as they would under a finger.
- `pause()`: clears the pending step, remembers the time left on it, pauses the tracer, leaves the classes as they are. `resume()`: continues the pending step with the time left, resumes the tracer. `cancel()` also stops the tracer and takes `draw`, `hover`, and `active` off whatever carries them.

## 4. Hover and press without a pointer (`duet.css`)

The stylesheet's hover and active rules gain class twins so the hand can trigger them:

```
button.chip:hover, button.chip.hover { …the same lift… }
button.chip:active, button.chip.active { …the same squash… }
.go:hover, .go.hover, .welcome-start:not(:disabled):hover { … }
.go:active, .go.active, .welcome-start:not(:disabled):active { … }
```

Nothing else about the toy press changes; the transitions are the same `.12s`, and under reduced motion they are off as today, so a lift is a jump.

## 5. Drawing (`preview.js`, `index.html`, `duet.css`, `app.js`)

**The visitor's pen.** A second `GhostPen`, `app.pen`, on a new group inside the board fit: `<g class="hand-ink" id="l-hand"><path id="handpath"/><circle id="handpen" r="2.2"/></g>` after `l-ghost`. Its path draws in the visitor's red, `stroke: var(--human)`, width 1.2, opacity .9; its circle is hidden by CSS, because the hand is the pen. `cancel()` on the hand stops it, so the trace disappears when the capture state arrives and the photo takes over; nothing is kept, the recording's `human` message still carries the ink for the Ink layer as today.

**`GhostPen` gains three things.** `play(polylines, { durationMs, onMove })` calls `onMove(p)` with the pen's board point on every frame and `onMove(null)` when the trace ends; `stop()` calls `onMove(null)` too when a trace was running. `pause()` cancels the animation frame and notes the time; `resume()` shifts the trace's start by the time paused and continues, so the remaining distance takes the remaining time. The start time becomes an instance field for that.

**The marker.** The hand's SVG gains `<g class="marker">`: a red barrel along the index finger and an ink tip cone whose point is the fingertip, so the hotspot is the marker's tip. Shown only while the hand carries the `draw` class.

## 6. Names (`index.html`, `duet.css`, `app.js`)

A `.tag` is a caption-size pill: `font: 700 1.2cqw/1 var(--story)`, paper on ink border, radius 999px, `pointer-events: none`, `white-space: nowrap`, absolutely positioned.

- **Visitor**: `<span class="tag">Visitor</span>` inside `#hand`, at `left: 3.4cqw; top: 5.4cqw` of the hand, so it moves, hides, and squashes with the hand.
- **Robot**: `<span class="tag hidden" id="pen-tag">Robot</span>` in the stage at `z-index: 4`. In replay mode `app.js` plays the robot's ghost pen with `onMove: (p) => …`: a point places the tag at `viewer.boardToStage(p)` offset by `1cqw, 1cqw` and shows it; null hides it. The live page passes no `onMove` and never shows the tag.

## 7. The turn clock (`duet/static/js/clock.js`, `index.html`, `duet.css`, `app.js`)

**Markup**, after the state chip in the top-left row:

```html
<button class="chip white clock hidden" id="clock" title="Pause or resume the piece" data-el="chip — turn clock">
  <i class="fill"></i><b id="clock-who">Visitor</b> <span id="clock-time">0.0 s</span>
</button>
```

**Styles.** `.clock { position: relative; overflow: hidden; }`; `.clock .fill { position: absolute; inset: 0; width: calc(var(--fill, 0) * 100%); background: var(--human); opacity: .25; transition: width .1s linear; }`; `.clock[data-who="robot"] .fill { background: var(--robot); }`; `.clock[data-who="paused"] .fill { animation: blink 1s ease-in-out infinite; }` (the page's blink keyframes); the text sits above the fill with `position: relative`. As a `button.chip` it has the toy press.

**`clock.js`.** Pure: `formatSeconds(ms)` gives `'8.4 s'` (one decimal, never negative); `fraction(elapsed, total)` gives 0 to 1, and 1 when `total` is 0. `new Clock(el, { who, time, now })` with `start({ who, ms })`, `pause()`, `resume()`, `stop()`, and `render()`. `start` shows the chip, sets `data-who` to `visitor` or `robot`, the label to "Visitor" or "Robot", and begins counting from zero on a 100 ms interval: each tick sets `--fill` from `fraction(elapsed, ms)` and the time text. Past `ms` the bar stays full and the seconds keep counting. `pause` freezes the count, sets `data-who` to `paused` and the label to "Paused"; `resume` restores who and continues; `stop` clears the interval and hides the chip.

**Routing in `app.js`.** A `clock` cue starts the clock. State `look`, `finish`, `finished`, or `idle` stops it. A visitor's pick re-sends `human_turn` and touches no clock, because only cues start it. The clock chip's click sends `pause` when the state is not paused and `resume` when it is.

## 8. Pause (`app.js`, `Player`)

The Player already holds its own clock on `pause` and re-sends the last state on `resume`. The page adds the rest, in replay mode, on each `state` message, remembering whether the previous state was `paused`:

- state `paused`: `hand.pause()`, `ghost.pause()` (the robot's pen; the visitor's pen pauses through the hand), `clock.pause()`. The live page keeps stopping the ghost on `paused` as today.
- the first state after `paused`: `hand.resume()`, `ghost.resume()`, `clock.resume()`; a resumed `robot_draw` does **not** call `ghost.play` again, which today would restart the trace from the beginning.
- any other state: as before, a state that is not `human_turn` cancels the hand; `robot_draw` plays the robot's pen with the tag's `onMove`.

Go and the picker hide in the paused state already, so nothing else can move the piece while it is paused. `restart` still cancels the hand and, through the `look` state, stops the clock.

## 9. Versions and the site

Every `?v=ds8` becomes `?v=ds9`. `site/build.py` runs again with the same session; `replay.json` is unchanged.

## 10. Tests

- `replay.test.mjs`: the hand cue carries `row` and the filtered `draw` (a 5 mm fragment dropped, a longer one kept); the clock cues follow the hand cue and the capture state with the expected `ms` at speed 1 and 2; `PACE.human` is 14000.
- `hand.test.mjs`: `traceMs` bounds and speed; `planMs`; the pick plan's expansion including the roll for `row: 1` and `row: 7` and no roll for `row: -1`; the runner with a fake tracer: the draw step plays the tracer with `onMove` and moves the hand to `toStage(p)`, hover adds and moves the class, press adds `active` then clicks on the release, pause holds a pending step and resume finishes it, cancel stops the tracer and clears the classes.
- `preview.test.mjs`, new: with stubbed `requestAnimationFrame` and `performance.now`, `onMove` reports points and then null; pause and resume finish the trace over the remaining time; stop reports null.
- `clock.test.mjs`, new: `formatSeconds`, `fraction`, and the runner against a fake element with an injected `now`: start, past-total fill, pause label and frozen time, resume, stop hides.
- `style.test.mjs`: the hover and active class twins, the marker group, the two tags, the clock chip and its fill rules, the red pen layer, `v=ds9`.
- `defaults.test.mjs` (the `app.js` wiring test): the pen, the tag placement, the clock routing, the pause routing, the clock's click.
- A browser walk of the demo: the hand draws the first mark in red and the trace vanishes at capture; rows lift as it rolls; the Robot tag rides the dot; the clock counts and fills; a click on the clock freezes the hand mid-glide, the pen mid-stroke, and the clock, and a second click resumes all three; the console stays clean.
