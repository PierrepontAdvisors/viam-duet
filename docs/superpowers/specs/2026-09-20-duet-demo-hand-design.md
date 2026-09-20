# Duet demo: a hand that picks the artist, a picker the visitor can open, and the demo's own defaults

Date: 2026-09-20, evening. Status: approved in a brainstorm round (pointer, cadence, and visitor-pick rules chosen by Nicholas; the panel defaults set from his screenshot). Branch `feat/showcase-site`, worktree `.worktrees/showcase-site`. Parent specs: `2026-09-20-duet-showcase-site-design.md` (replay mode and the site), `2026-09-19-duet-artists-design.md` (the picker), `2026-09-18-duet-page-design.md` (the page).

## 1. What changes

The showcase demo replays a recorded session. Today its artist picker is a read-only label: the replay sets each exchange's artist before the visitor's turn, and a rule blocks the picker's clicks. Three things change, all in replay mode only. The live page keeps its behaviour and its defaults.

1. **A hand shows the visitor's part.** During each human turn a cartoon hand glides to the picker, opens it, presses the artist the recorded visitor chose, then glides to Go and presses it. It opens the picker only on the exchanges where the recorded visitor switched artist (1, 5, 7, 8 and 10 in the session on the site: Mimic, Shader, Haring, Mimic, Van Gogh); on the others it goes straight to Go. The page boots with the picker on Abstract, the live default, so exchange 1 shows a pick.
2. **The picker works.** A visitor can open it, read the roster, and pick, during playback and while the hand moves. The label follows their pick until the turn is captured; then the recorded artist's name takes over, because the recording cannot redraw. Go keeps working as it does: it ends the human wait.
3. **The demo has its own defaults.** The controls panel opens the way the screenshot shows: cropped to the board, the ink layer off, the two greens and the wider lines, the picture levels, and sound on. A visitor's own changes still persist in their browser, as they do today.

## 2. The schedule and the Player (`duet/static/js/replay.js`)

`schedule()` keeps a *setting*, the artist the picker shows: `abstract` before the first exchange, then the recorded artist of each exchange once it is done, as the live backend keeps the setting between turns. The `look` and `human_turn` states before an exchange carry the setting; `capture` and everything after carry the exchange's recorded artist. Right after each `human_turn` state the schedule emits a cue step, a third kind of step beside `emit` and `wait`:

```
{ cue: { hand: 'pick', artist: 'mimic' } }     when the exchange's artist differs from the setting
{ cue: { hand: 'go' } }                          otherwise
```

Then the human wait as before, `{ wait: PACE.human, on: 'pass' }`, with `PACE.human` raised from 4 s to 6 s: it is now a ceiling that the hand's Go press, or a visitor's, ends early.

`Player` takes a `cue` callback in its options (default: nothing) and calls it with the cue when it reaches a cue step. It also keeps a *pick*, null until a `set` command with an artist arrives (from the hand's press on a row, or a visitor's). On a pick it stores the artist and feeds the last state again with `artist` replaced, so the label reads the choice at once; while a pick is held, every `look` and `human_turn` state it emits carries it; a `capture` state clears it. `restart` clears it too. `boot()` feeds the first `human_turn` with `abstract`.

The Pause and Resume commands are unchanged. They only come from the panel's Run row, which replay mode hides, so the hand does not need to survive a pause.

## 3. The hand (`duet/static/js/hand.js`, new; `index.html`; `duet.css`)

**Markup.** One element inside the stage, after the CTA row: `<div class="hand hidden" id="hand" data-el="demo hand">` holding an inline SVG of a pointing cartoon hand: ink outline at the frame stroke, cream fill, a cuff, the index finger up and to the left. Its hotspot is the fingertip at the element's top-left corner. About 6 cqw tall. `position: absolute`, `z-index: 5` (above the menu's 4, below the corner buttons' 6), `pointer-events: none` so it never takes a click, `transition: left .5s ease, top .5s ease`. A `.press` class squashes it for 220 ms (scale .88 about the fingertip). Under `prefers-reduced-motion: reduce` the transition and the squash are off; the hand jumps.

**The plan, pure.** `plan(cue, speed = 1)` returns timed steps:

```
pick:  settle 700 → glide picker 500 → press picker 220 → glide row 500 → press row 220 → hold 500 → glide go 500 → press go
go:    settle 900 → glide go 500 → press go
```

`{ glide: target, ms }` and `{ press: target, ms }`, targets `picker`, `row`, `go`; every `ms` divided by `speed`. The settle stands for the visitor drawing their mark before they reach for the page.

**The runner.** `new Hand(el, { targets, speed })` where `targets` resolves a name to a DOM element or null: `picker` is `#artist-btn`, `row` is the menu button whose `data-v` is the cue's artist, `go` is `#go`. `run(cue)` cancels any run in progress, shows the hand, then walks the plan on `setTimeout`. A glide sets `left`/`top` to the target's centre in stage pixels (the target's rect against the stage's rect). A press adds `.press` for its duration and calls the target's `click()`, so the page's own handlers do the work: the picker button opens the menu, the row sends `set artist` and closes it, Go sends `pass`.

The hand presses what it sees:

- pressing the picker when the menu is already open is skipped (a visitor opened it);
- pressing a row when the menu is hidden first presses the picker again (a visitor closed it);
- a step whose target is missing or hidden is skipped (the picker hides while a visitor browses photos; Go stays until the turn ends);
- `cancel()` clears the timer, removes `.press`, and hides the hand.

`app.js` creates the hand in `boot()` when the page is in replay mode, passes `cue: (c) => app.hand.run(c)` to the Player, and cancels the hand on every `state` message whose state is not `human_turn`, and on `restart` (`send` sees the command before the Player does).

## 4. The visitor's clicks (`duet.css`, `ui.js`)

The rule `body.replay #artist-btn { pointer-events: none; }` goes. Nothing else in the picker changes: it opens in `human_turn` because `pickerText` says so, the row's click sends `set`, and `send()` already routes commands to the Player. The hand's `pointer-events: none` keeps it out of the way of a real pointer.

## 5. The demo's defaults (`ui.js`, `app.js`)

In replay mode, and only where the visitor's browser has nothing stored for the setting, the page starts with:

| Setting | Live page | Demo |
| --- | --- | --- |
| View | full | crop to the board |
| Layers | plan, ink, bubble, chips, clean on; board, ink only off | ink off; the rest as live |
| Ink colour, width | `#111111`, 12 | `#37e65b`, 38 |
| Strokes colour, width | `#1b8f3a`, 14, follows each plan's colour | `#1fcf4f`, 24, locked (a plan's colour does not replace it) |
| Picture | brightness +0.07, contrast 1.90, exposure 0 (the clean preset) | brightness 0.00, contrast 0.84, exposure +1.4 |
| Sound | off | on |

The colours and widths were read from the screenshot: the two swatches sampled as `#37e65b` and `#1fcf4f`, the width sliders sat at 38 and 24 of 4 to 40; the picture row's own labels gave its three values. `initUI` receives `replay: true` from `app.js` (it knows before the Player loads, from the meta tag) and picks the demo's default table. Crop is not stored today and stays that way: the demo simply starts cropped.

Sound needs a gesture before the browser lets audio play. With nothing stored, the demo turns sound on at the welcome's Start press, the first click every visitor makes, and the chip reads "Sound on" from then. The chip still toggles it, and the choice is stored as today. The `Sound: click to enable` label for a remembered on-state is unchanged.

## 6. Versions and the site

Every `?v=ds7` tag in `index.html` and the module imports becomes `?v=ds8`, since the styles and scripts change. `site/build.py` runs again with the same session so `site/demo/` carries the new page; `replay.json` is unchanged by this work.

## 7. Tests

- `pagetests/replay.test.mjs`: the schedule's cues per exchange (a pick on a switch, Go otherwise, Abstract before the first), the setting on `look` and `human_turn` and the recorded artist from `capture` on, the Player's `cue` callback, a `set` echoing the state with the pick, `capture` and `restart` clearing it, and `boot` on Abstract.
- `pagetests/hand.test.mjs`, new: `plan()` for both cues, the order of targets, and the division by speed.
- `pagetests/style.test.mjs`: the picker's blocking rule is gone; the hand's element, its `pointer-events: none`, and its reduced-motion rule are present.
- `pagetests/welcome.test.mjs` or a new `defaults.test.mjs`: `ui.js` carries the demo default table with these values and applies it only in replay mode.
- A browser walk of the demo on the local server: Start, the hand opens the picker and picks Mimic, presses Go; a visitor's pick relabels the button and the recorded name returns at capture; the panel opens with the demo defaults; the console stays clean.
