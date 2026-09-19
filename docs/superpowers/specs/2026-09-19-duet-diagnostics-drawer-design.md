# Duet live page: diagnostics drawer

Date: 2026-09-19, evening at the table. Status: approved section by section in chat; awaiting Nicholas's review of this file. Branch `feat/duet-design`. Parent specs: `2026-09-18-duet-page-design.md` (the page, §8 operator panel, §9 protocol, §14 addendum) and `2026-09-19-duet-app-design-system.md` (tokens, toy-press buttons).

## 1. Summary and decisions

The operator has no way to see the connection while the demo runs: the only behind-the-scenes readout is three mono status lines at the bottom of the controls panel. This spec adds a diagnostics drawer that shows everything the page streams, as a timeline and a log, opened by a gear-icon button with a status light beside it. Nothing new is streamed; the page records what already crosses its one WebSocket and shows it.

Decisions made in the brainstorm:

- **Own drawer, second corner button.** A gear-icon button joins "Controls" at the bottom right. It opens a diagnostics drawer separate from the controls panel; the two are mutually exclusive so they never overlap.
- **The graph is a message timeline.** Time runs left to right over the last three minutes; one lane per message kind with a mark per message, state marks labelled, and a socket band underneath showing connected and reconnecting periods.
- **The table is a message log.** Newest first, one row per message with a one-line summary taken from the message; the last 200 entries in memory, nothing persisted. A summary line above gives the socket state and counts.
- **Rows expand to the raw JSON**, pretty-printed, with arrays of points folded to "12 strokes, 340 points".
- **Bottom drawer in the panel's spot.** Full width, half the stage height, over the bottom of the picture. Opening it closes the controls panel and vice versa.
- **Status light** beside the gear: green while the socket is connected, red while it is reconnecting, a brief brighter blink on each incoming message. Two states only; a quiet socket is normal while the visitor draws, so there is no "stale" amber.
- **Both directions are recorded.** Incoming frames, socket open and close events, and the commands the page sends (set, pause, resume, pass, restart, reset_arm, clear_error), so a round trip reads as an out row followed by the state that answers it.
- **No backend change.** The recorder hooks the socket callbacks in the page before the parser, so it also sees fields the page ignores today (the state message's `camera_errors` and `camera_error`) and frames the parser drops.

Out of scope, on purpose: new backend messages, MJPEG frame monitoring (a page cannot observe per-frame arrivals from an `img`), filtering or pausing the log, persistence, export, a charting library.

## 2. The corner row: gear and status light

The corner button "Controls" (class `gear`, id `gear`) moves into a small flex row `.corner` at the stage's bottom right, `z-index` 6, together with:

- **The status light** `#light`: a dot about 0.9 cqw across with the ink border, red by default (`--red`), green with the class `on` (`--green`), and a 120 ms flash to `--yellow` with the class `blink`. The view adds `on` on socket open, removes it on close, and toggles `blink` for each incoming frame. Under `prefers-reduced-motion: reduce` the blink is not shown.
- **The gear** `#diag-gear`: a corner button with the classes `gear icon`, an inline SVG gear of about 1.4 cqw using `currentColor`, `aria-label="Diagnostics"`, `title="Diagnostics (G)"`. It keeps the corner button's paper fill, ink border, and toy-press shadow.
- **Controls** `#gear`, unchanged in look and behaviour.

`body.controls .corner, body.diagnostics .corner { display: none }` replaces today's `body.controls .gear { display: none }`: both drawers hide the corner row and carry their own Hide button. The `.gear` rule keeps its `z-index: 6` so the welcome-page test's assertion still holds; the row positions the buttons. The corner row sits over the welcome page (z 4) as the Controls button does today.

## 3. The drawer

`<section class="diag" id="diag">` inside the stage, after the panel: `position: absolute; left: 0; right: 0; bottom: 0; height: 50%; z-index: 5`, the panel's translucent white and frame-stroke top border, mono type (`--mono`) with the panel's small-caps labels (`--story`). Shown by `body.diagnostics` (not `body.diag`: the body would then match the drawer's own `.diag { display: none }` rule and hide the page). Three bands, a flex column:

1. **Header**, 2.4 cqw tall: the label "Diagnostics" (the panel's `.lbl` style), the summary in mono (`#diag-summary`, section 5 `header`), and a Hide button (`#diag-hide`, styled like the panel's Hide).
2. **Timeline**: an SVG `#diag-timeline` with a fixed `viewBox` (1000 by 92 units) and a matching CSS `aspect-ratio`, full width, so nothing stretches. About a third of the drawer's height.
3. **Log**: `.diag-log`, `flex: 1; min-height: 0; overflow: auto`, holding the table (section 7).

Open and close live in `ui.js` beside the panel's toggle: `toggleDiag(force)` sets `body.diagnostics`, removes `body.controls`, tells the view (`view.setOpen(bool)`), and re-places the bubble; `toggleControls` removes `body.diagnostics` when it opens the panel. Bindings: the gear opens, Hide closes, key `G` toggles (with the existing key guard for inputs), `?view=diag` opens at load as `?view=console` does for the panel. The bubble's floor becomes the top of whichever of the panel or the drawer is open.

## 4. Recording

`app.js` records at the socket, before parsing, from page load on. `app.diag = { entries: [], seq: 0 }`; `record(make)` increments `seq`, appends `make(Date.now(), seq)` with the pure `append`, and hands the new list to the view.

- `ws.onmessage`: `const m = parseMessage(e.data)`; record `frameEntry(e.data, m, t, seq)`; blink the light; then dispatch `m` as today (or warn when null).
- `ws.onopen`: record `socketEntry('open', null, t, seq)`; light on.
- `ws.onclose`: record `socketEntry('close', e.code, t, seq)`; light off.
- `send(msg)`: when the message actually goes out, record `sentEntry(msg, t, seq)`.

An entry is `{ seq, t, dir, type, turn, size, ok, raw }`:

| dir | type | turn | size | ok | raw |
|---|---|---|---|---|---|
| `in` | the frame's `type` string, or `?` when absent or not JSON | the frame's `turn` when numeric, else null | the text's length in characters | true when `parseMessage` accepted it | the parsed JSON object, or the text when it is not JSON |
| `out` | the command's `type` | null | the sent text's length | true | the command object |
| `ws` | `open` or `close` | null | 0 | true | `{ code }` for close, `{}` for open |

Entries are immutable; `append` returns a new array.

## 5. The pure module `diag.js`

No DOM. Constants: `CAP = 200`, `WINDOW_MS = 180000`, `TICK_MS = 30000`, `LANES = ['out', 'error', 'state', 'progress', 'plan', 'interpretation', 'human', 'shot', 'dock', 'calib', 'video']`.

- `frameEntry(text, parsed, t, seq)`, `sentEntry(cmd, t, seq)`, `socketEntry(event, code, t, seq)`: the constructors of section 4.
- `append(entries, entry)`: a new array, oldest first, holding at most `CAP` entries (the oldest fall off).
- `summarize(entry)`: one line per kind. state: `human_turn · turn 2 of 5 · at look · error: …` (error only when set). progress: `stroke 3 · 412 mm`. interpretation: `claude 6.4 s · sees "…" · adds "…"` or `fallback · <error>`. plan: `4 strokes · 212 points · budget 1200 mm · #1b8f3a`. human: `6 strokes · 2 new · found`. shot: `human · turn 2` plus `+frame` when a frame url is present. error: the message. dock: the slots and any reseat list. calib: `4 marks · tl 1 · fit ax 0.967 ay 0.991`. video: the url. out: the command as compact JSON. ws: `open` or `close <code>`. A frame whose JSON has an unknown type: `unknown type`; not JSON: `not JSON: <first 60 characters>`; a known type the parser refused: `dropped by the parser`.
- `fold(value)`: a deep copy in which any array that is a list of points (arrays of two or more numbers) or a list of such lists, with more than eight points in total, becomes the string `N strokes, M points` (`1 stroke` for a single polyline). Everything else, including `board_mm` and the four `marks_image` points, is kept.
- `clock(t)`: `HH:MM:SS.t` local time.
- `header(entries, now, connected)`: `{ connected, sinceLastMs, received, sent, reconnects, dropped }`: `sinceLastMs` is the age of the newest `in` entry or null; `received` and `sent` are counts of `in` and `out` entries; `reconnects` counts `open` events after the first; `dropped` counts `in` entries with `ok` false.
- `timeline(entries, now, windowMs, connected)`: `{ lanes, bands, ticks }`. `lanes` is one object per `LANES` entry in that order, `{ type, marks: [{ x, label }] }`, `x = 1 - (now - t) / windowMs` for entries inside the window, `label` the state name for state marks and null otherwise; `out` marks fall in the `out` lane, `in` marks in the lane of their type, and `in` frames of unknown type or refused by the parser in the `error` lane. `bands` is a list of `{ x0, x1, connected }` covering the window without gaps, built from the `ws` entries in time order: the state before the first known event is the opposite of that event, and with no `ws` entries at all the whole window takes `connected`. `ticks` are `{ x, label }` every `TICK_MS`, labelled `−2:30` … `−0:30` and `now`.

## 6. The timeline drawing

`diagview.js` turns `timeline()` into SVG once a second while the drawer is open and on every new entry, and does nothing while it is closed. Lane labels in mono at the left in ink; a hairline per lane; marks as small ink rectangles, red in the `error` lane; state labels in small mono above their marks; the socket band along the bottom, green at low opacity where connected and solid red where not; ticks as faint vertical lines with their labels under the band. Colours come from the tokens only.

## 7. The log table and detail

A `table.log` in mono, header row sticky, body scrolling in `.diag-log`. Columns: time (`clock`), dir (`in`, `out`, `ws`), type, turn, size, summary. Newest row on top. Row classes: `err` for the `error` type and for `in` entries with `ok` false (red text), `out` for sent commands (the panel's yellow, faint), `ws` for socket events. Every cell is escaped as the panel's status lines are; the raw text is data, never markup.

- **Redraw rule**: the table rebuilds only when an entry arrives, never on the clock, so it does not flicker while being read. The header and timeline are the only parts on the one-second tick.
- **Detail**: clicking a row toggles a `tr.detail` beneath it with a `pre` holding `JSON.stringify(fold(raw), null, 2)`. The view keeps a `Set` of expanded `seq` numbers, so a detail survives redraws until its entry falls off the cap. `ws` rows have nothing to expand.
- **Dev mode**: the corner row, light, gear, drawer, header, summary, timeline and table carry `data-el` names.

## 8. Files

- New `duet/static/js/diag.js` (section 5) and `duet/static/js/diagview.js`: `initDiagView({ light, summary, svg, tbody })` returning `{ setOpen, setConnected, blink, onEntry }`; it holds the expanded set and the interval.
- `duet/static/index.html`: the corner row with the light and both buttons, the drawer markup after the panel, asset version bumped to `ds6` on the stylesheet and script links and the module imports.
- `duet/static/duet.css`: `.corner`, `.light`, `.gear.icon`, `.diag` and its bands, `.diag-timeline`, `table.log` and row tints, the reduced-motion rule for the blink.
- `duet/static/js/app.js`: `app.diag`, `record`, the four hooks, the view boot before `connect()`.
- `duet/static/js/ui.js`: `toggleDiag`, the exclusion in `toggleControls`, gear and Hide bindings, key `G`, `?view=diag`, the bubble floor.
- `pagetests/README.md`: the key line gains G.
- `docs/superpowers/specs/2026-09-18-duet-page-design.md`: one pointer bullet in §14 to this spec.

## 9. Testing

`pagetests/diag.test.mjs`, Node, no DOM:

- `append` caps at 200, keeps order, returns a new array and leaves the input untouched.
- `frameEntry` on a state frame, a not-JSON frame, an unknown-type frame, and a known type the parser refuses; `sentEntry` and `socketEntry` shapes.
- `summarize` for every message kind in `LANES`, a dropped frame, an out row and a close.
- `fold` collapses a plan's polylines and a human's `new`, keeps `board_mm` and four `marks_image` points, and leaves scalars and strings alone.
- `header`: counts, reconnects after two closes and three opens, dropped, and `sinceLastMs` from the newest `in` entry only.
- `timeline`: marks at the right fraction, lanes present and ordered even when empty, entries outside the window dropped, state labels on state marks, refused frames in the `error` lane, bands for "never any event" (whole window in `connected`), "close then open inside the window" (green, red, green), and "still disconnected" (red to the right edge); ticks every 30 s with the `now` label last.

`pagetests/diagnostics.test.mjs`, markup and wiring in the style of `welcome.test.mjs`: the corner row holds the light, the gear (with an SVG and `aria-label`) and Controls, inside the stage; the drawer follows the panel and has the header, timeline SVG with the fixed `viewBox`, and the table with six headings; the CSS hides `.corner` under both body classes and gives `.diag` `z-index: 5`; `app.js` calls `frameEntry` in `onmessage` before dispatch and `socketEntry` in `onopen` and `onclose`; `ui.js` binds `G`, `?view=diag`, and removes the other class in each toggle. Every `data-el` name in the new markup is unique.

Live, against the fake runner (`python -m duet.run --fake --port 8001`): the light is green and blinks as messages arrive; G opens the drawer and closes the panel if it was open; a turn shows its marks and rows (state labels along the state lane, progress ticks, one plan, one interpretation); expanding the plan row shows `N strokes, M points`; stopping the runner turns the light red, adds a close row and a red band, and a reconnect after restart adds open rows and the band goes green; the bubble sits above the open drawer. The existing 130 backend tests and 67 page tests keep passing; the backend has no changes.

## 10. Rollout

Page only. The next `python -m duet.run` (or `demo.sh`) serves it; an open page needs one reload to fetch the `ds6` assets.
