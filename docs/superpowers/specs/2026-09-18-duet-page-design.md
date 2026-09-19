# Duet page: design

Date: 2026-09-18 (evening of day 1). Status: approved in brainstorming with the visual companion; implemented on `feat/duet-page` (plan 5); awaiting integration with the backend's `web.py`. Branch `feat/duet-page`, worked in the linked worktree `.worktrees/duet-page`. Parent spec: `docs/superpowers/specs/2026-09-18-duet-design.md`, sections 9 and 15. This document replaces plan 3's page markup (task 3, step 4) and keeps its protocol. The interactive mockup that was approved is reproducible from `docs/duet/mockups/` (see section 12).

## 1. Summary and decisions

The page is the picture. One full-bleed view of the wrist camera fills a 16:9 stage, and everything else is drawn on top of it: Claude's words in a storybook bubble, the state and exchange counter as pill chips, the robot's plan and the person's traced ink registered exactly onto the board, and an operator panel that slides over the bottom of the picture when a small corner button is pressed. Nothing lives outside the frame.

Decisions made during brainstorming, in order:

- **One page, two audiences.** Visitors see the stage. The operator opens the controls panel inside the frame with the corner button, the `C` key, or by loading `/?view=console`. No second route.
- **Visual direction: bold, then storybook.** Haring's black outlines and flat yellow, green, and red were chosen over a gallery placard and a dark studio look, then softened into a cartoon children's-book style: rounded lettering, pill chips with thick outlines, a tilted badge, and comic bubbles.
- **Full-bleed camera.** A minimal stage with the camera at its native 16:9, uncropped, beat a two-tile layout and a headline layout.
- **Every image is landscape and framed like the camera.** Turn photos are shown in the camera's framing, never as the portrait board warp. The raw look-pose frame is preferred; the warped photo is projected onto the board's quad as the fallback.
- **Layers, sources, loop.** Plan strokes, human ink, bubble, chips, and a board outline can each be toggled. The base image can be the live stream or any turn photo, and the turn photos play as a flipbook loop with the stitched video's timing.
- **Claude speaks in a few storybook words.** A white thought cloud while it looks, a yellow speech bubble when it answers. The full sentences move to the operator panel.
- **Full view or crop to board.** A zoom that keeps registration.
- **Eight additions**, all page-side: thinking animation, animated path preview, vector view with the person's drawing vectorized, a pen-down button, sound and voice with a mute, a light-direction chooser, a clean-board layer (pure white paper, vivid marker, frame and corner tape hidden), and bubbles placed beside the strokes they talk about.
- **Out of scope for the demo:** shading and hatching, Mondrian and Van Gogh grammars (backend work, the page shows them greyed until the backend reports them), the public tunnel and token, the live-data particle panel, the gallery, captions burned into the video.

File ownership tonight: this design owns `code/hackathon/duet/static/` only. The overnight backend session owns every `duet/*.py`, `tests/`, and `config.py`. The protocol below was agreed with that session message by message and is the contract.

## 2. The stage

The stage is a 16:9 box, black, letterboxed inside the viewport (black bars above and below on a taller screen, at the sides on a wider one). Every size on the stage is in container-query width units (`cqw`), so the same markup reads on a phone, a laptop, and a projector.

Layers, bottom to top:

1. **Picture layer** (`.pic`): the base image, the projected turn photo, and the overlay SVG. This whole layer is what "crop to board" zooms.
2. **Chips**: top-left a yellow "Duet" badge tilted three degrees and the state pill; top-right the exchange counter pill, "Exchange 3 of 5" with the number in red.
3. **Bubble**: beside the board on the side nearer to what it talks about, at that height, with the tail or thought-dots pointing toward it (section 7, item 8). In crop mode it shrinks. It never overlaps the chips at the top or the panel when open.
4. **Go button** (held mode, human turn only): a large green pill under the state chip reading "Go, robot!"; sends `pass`.
5. **Corner button** bottom-right, translucent, "Controls". Hidden while the panel is open.
6. **Panel**: translucent black over the bottom of the picture, rows described in section 8.
7. **Developer mode** badge, label, and toast per the preview convention.

Style tokens: yellow `#ffd400`, green `#1b8f3a`, red `#c62828`, ink `#111`, black `#000`, white `#fff`. Storybook face `"Fredoka"` from Google Fonts with `"Chalkboard SE"`, `"Comic Sans MS"`, `"Segoe Print"`, `sans-serif` as fallbacks, so the page still looks right offline. Chips: pill radius, `.35cqw` black border, weight 700, sentence case. Speech bubble: yellow, `.5cqw` border, irregular radii, a two-triangle tail, rotated two degrees. Thought cloud: white, irregular radii, two trailing dots drawn with pseudo-elements. The panel uses plain Helvetica and small caps labels: it is for the operator, not the story.

## 3. What the visitor sees in each state

| Session state | State chip | Bubble | Picture |
| --- | --- | --- | --- |
| `idle`, `look` | "Getting ready…" (white) | speech: "One moment…" | live |
| `human_turn` | "Your turn!" (green) | speech: "Your turn! Draw one mark." | live; in held mode the Go button shows |
| `capture`, `interpret` | "Let me look…" (white) | thought cloud, pulsing, cycling placeholder lines every 1.5 s: "Hmm…", "Looking closely…", "What could it be?", "I see lines…" | live |
| `interpretation` arrives | unchanged | thought cloud shows Claude's `thought` | live |
| `plan` | "I have an idea!" (yellow) | speech bubble shows `quip` | live; ghost pen animates the whole path once |
| `robot_draw` | "My turn! Hands off, please" (red) | speech: `quip` | live; strokes fill solid as `progress` arrives |
| `finish` | "Signing…" (green) | speech: "All done! Thank you." | live |
| `finished` | "The end" (yellow) | speech: "That was fun. Play it back?" | the loop starts on its own after 3 s |
| `paused` | "Paused" (red) | speech: "One moment, please." | live; the panel shows the error text |
| `dock.reseat` non-empty | unchanged | speech: "Please pop the marker back in its cap." | live |

When the operator browses turn photos, the bubble follows the photo, not the state: a human photo shows the thought cloud with that turn's `thought`, a robot photo shows the speech bubble with that turn's `quip`, the start photo shows "Your turn! Draw one mark." The page keeps a per-turn record of `thought`, `quip`, `sees`, `adds`, and `source` from the interpretation messages it has seen; for turns before the page connected, the snapshot gives only the latest interpretation, so older turns show the fixed lines "Hmm, what was this?" (thought) and "I remember this one!" (speech).

Fallback turns (`source: "fallback"`) show the backend's fixed lines, which arrive in `thought` and `quip` like any other.

## 4. Sources and the loop

The base image is one of:

- **Live**: `<img src="/stream.mjpg?overlay=0">`. The page draws its own plan layer, so the server's overlay is turned off to avoid double lines. On `error` the image reloads after one second with a cache-busting query.
- **A turn frame**: from a `shot` message. `frame_url` (the raw 1280×720 look-pose frame) is used when present. When it is null, the warped `url` photo (704×960, the board at 4 px/mm) is projected onto the board's quad over the last live frame, using the same transform as the strokes. Either way the picture is landscape and framed like the camera.
- **The loop**: all shots in order (start, then human and robot per turn), one second each, the last held two seconds, then wrap. Same timing as `session.mp4`. Space plays and stops; arrows step; `L` returns to live.

The page builds the shot list from every `shot` message it receives (they carry `turn` and `who`), and on connect from the snapshot's latest shot it back-fills the earlier ones by URL pattern `/sessions/<id>/turn-NN-<who>.jpg` (and `-frame.jpg`), probing with `HEAD` requests, so a page opened mid-session still has the whole story.

When the `video` message arrives, the panel shows a "Video" link to the MP4 (download or open). The in-page loop remains the primary playback.

## 5. Registration

All strokes and photos land on the board in the camera frame through one transform.

- **Calibration** comes from the `calib` message in the snapshot (also `GET /calibration.json`): `marks_image` (four corners in image pixels), `board_tl_index`, `board_mm` `[176, 240]`, `image_size` `[1280, 720]`, `cam_to_robot` `{ax, bx, ay, by}`. If a new `calib` arrives, it replaces the old one and the transform is recomputed.
- **Board order** follows `vision.board_quad`: the board's top-left is `marks_image[board_tl_index]`; its top-right is whichever neighbor is nearer (the short edge); bottom-right is the opposite corner. Result: `[tl, tr, br, bl]` in image pixels.
- **Displayed rectangle**: the stream image is drawn with `object-fit: contain`; the page computes the scale and offset from the stage size and `image_size`, and observes resizes.
- **Homography**: the overlay SVG is 176×240 CSS px with `viewBox 0 0 176 240`; the page solves the 8-equation system mapping its four corners to the displayed quad and applies the result as a CSS `matrix3d`. The projected photo `<img>` is 176×240 CSS px too and takes the same matrix.
- **Coordinate frames**: `human`, `plan`, and the plan SVGs are in robot-board millimeters (the `cam_to_robot` fit already applied). The strokes sit inside a group with `transform="matrix(1/ax 0 0 1/ay -bx/ax -by/ay)"` that converts them back to camera-board millimeters before the homography. The board outline layer and the projected photo are already in camera-board millimeters and skip that group.
- **Accuracy**: the backend says the marks drift a few pixels between captures; `marks_image` is good to about 10 px. The board-outline layer exists to check this by eye.

Without a `calib` message the picture still shows, the overlay layers hide, and the panel notes "no calibration".

## 6. Layers

Toggles in the panel, each remembered in `localStorage`:

- **Plan**: robot strokes from `plan.polylines` in `plan.color`. Strokes with index at or below `progress.stroke` are solid; the rest dashed.
- **Ink**: every human polyline from `human.polylines`, in ink black. This is the person's drawing, vectorized, and it is what the vector view shows.
- **Bubble**, **Chips**: the storybook layer. Off gives a clean picture for a photo.
- **Board**: yellow outline of the board and the dashed 15 mm inset. Off by default; a calibration check.
- **Clean board**: on by default. A levels filter on the picture (`feComponentTransfer`, linear slope 1.9 and intercept -0.38 on each channel, then `saturate(1.7)`) stretches the gray paper to pure white and makes the marker vivid, and a white mask with an even-odd hole covers everything outside the 15 mm inset: frame, corner tape, desk, arm. The hole is the inset rectangle mapped through the same homography as the strokes, drawn as an untransformed SVG inside the picture layer, so it follows crop and recalibration and never suffers a perspective flip. With it off the raw camera shows.
- **Ink only** (the vector view): hides the base image and the projected photo and paints the board area paper-white with a soft gray outside, so only vectors remain: the person's ink and the robot's strokes, registered as before. Two color pickers, one for ink and one for the robot's strokes, change the display only; the robot holds one green marker regardless. Defaults: ink `#111`, strokes `plan.color`.

**Full view or crop to board**: crop zooms the picture layer so the board's bounding box fills 90 % of the frame, centered, with a 0.45 s ease. Because the photo and strokes live inside the picture layer, they stay registered. `Z` toggles.

## 7. The six additions

1. **Thinking animation.** During `capture` and `interpret` the thought cloud scales between 100 % and 104 % on a 1.6 s loop, its dots blink in sequence, and the text cycles through the placeholder lines every 1.5 s. When `interpretation` arrives the real `thought` replaces the text and the pulse stops.
2. **Path preview.** On `plan`, a ghost pen (a small black dot with a yellow rim) traces every polyline in order at a constant 60 mm/s, drawing a light tint of the stroke behind it with a `stroke-dashoffset` animation; the full path is then left dashed. Real `progress` messages fill strokes solid as the arm completes them, independent of the ghost.
3. **Vector view.** Section 6, "Ink only".
4. **Pen down.** The "Go, robot!" button on the stage and "Pass turn" in the panel both send `{type: "pass"}`. Shown only when `state.handoff` is `held` and the state is `human_turn`. The backend still refuses while a hand is over the board; the page shows its `error` text in the panel.
5. **Sound and voice.** Off by default. A small speaker pill top-right beside the counter toggles it (the panel's Sound button mirrors it), and the first click also unlocks audio for the browser's autoplay policy. Voice: `speechSynthesis`, one utterance for `thought` when it arrives and one for `quip` at `plan`, rate 0.95, a warm English system voice chosen by a preference list (`Samantha`, `Karen`, `Moira`, else the default). Tones: WebAudio oscillators only, no files: a soft two-note chime on `human_turn` and on `robot_draw`, a short click per `progress`, a quiet slow pulse while thinking. The choice persists in `localStorage`.
6. **Light chooser.** In the panel, a dial from 0 to 359 degrees drawn as a small sun that the operator drags around a miniature board; sends `{type: "set", direction: n}` on release and shows the value the server echoes in `state.direction`. The server validates the value, refuses bad ones with an `error` message, and echoes `direction` (default 0) and `energy` (default 0.5) in every `state`. An `energy` slider (0 to 1) sits beside the dial and works the same way.
7. **Clean board.** Section 6. The filter constants are tuned once on the real frame at the look pose and kept in `duet.css`; the mask needs no tuning.
8. **Bubbles in context.** Each bubble anchors to a point in board millimeters: the thought cloud to the centroid of `human.new` (this turn's ink), the speech bubble to the centroid of `plan.polylines`, the start line to the board center. The anchor goes through the same homography and crop transform as the strokes to a stage point. The bubble sits on the side of the board nearer to that point, its outer edge 3.6 % of the frame width from the board's bounding box, vertically centered on the point and clamped between the chips and the panel. Right-side bubbles mirror their tail and dots. Position changes ease over 0.35 s.

## 8. The operator panel

Opened by the corner button, `C`, or `/?view=console`. Rows, all in frame units:

- **Image**: Live · ◀ position ▶ · Play loop / Stop · Full view | Crop to board · Video (when available) · Hide controls at the far right.
- **Layers**: Plan · Ink · Bubble · Chips · Board · Clean board · Ink only · ink color · stroke color · Sound.
- **Session**: Short | Medium | Long · exchanges − n + · Held | Dock · artist buttons (greyed unless `state.artists` lists them; `["haring"]` until the other grammars land) · Pause / Resume · Pass turn · Clear arm error (red) · light dial · energy slider.
- **Status line 1** (monospace): `state` · `turn n of N` · `length` · `handoff` · `hand guard` · `error` · `ws connected | reconnecting`.
- **Status line 2**: `claude <latency> s` · `sees …` · `adds …`, or `fallback grammar · <error>`.
- **Status line 3**: dock slots and any reseat request (dock mode only).

Settings buttons send `set` and then wait for the echoed `state` to light up; the page never assumes a change took. A refused setting comes back as an `error` message and shows in red on status line 1 for five seconds.

Keys: arrows step photos, space plays or stops, `L` live, `C` controls, `Z` crop, `D` developer mode. Keys are ignored while an input has focus.

## 9. Protocol used

Transport: one WebSocket at `/ws`. On connect the server sends the latest message of each type, then live messages. On close the page reconnects after one second and shows "reconnecting" on the status line and a small red dot on the Duet badge.

Server to page: `state` (`state`, `turn`, `exchanges`, `length`, `artist`, `mode`, `handoff`, `coverage`, `error`, `at_look`, `hand_guard`, `session`, and if wired `direction`, `energy`, `artists`), `calib`, `human` (`polylines`, `new`, `found`), `interpretation` (`sees`, `adds`, `source`, `latency_s`, `error`, `thought`, `quip`), `plan` (`polylines`, `color`, `budget_mm`), `progress` (`stroke`, `drawn_mm`), `shot` (`url`, `frame_url`, `turn`, `who`), `video` (`url`), `dock` (`slots`, `reseat`), `error` (`message`).

Page to server: `set` (`length`, `exchanges`, `handoff`, `artist`, `direction`, `energy`), `pause`, `resume`, `pass`, `clear_error`.

Other URLs: `/` (the page), `/static/…` if the backend mounts it, `/stream.mjpg?overlay=0`, `/sessions/<id>/…`, `/calibration.json`, `/health`.

`state.turn` counts completed exchanges. `human`, `interpretation`, `plan`, and `progress` carry `turn`, the exchange in progress (`state.turn + 1` during capture and interpret), so a page that connects mid-session files the snapshot's messages under the right turn; without it the page falls back to `state.turn`.

Unknown message types are ignored. Every incoming field is checked for type before use; a malformed message is logged to the console and dropped, never thrown.

## 10. Files

`static/index.html` (markup only, plus the strings the backend's `test_web.py` asserts on: `<title>Duet`, `data-el="`, `dev-badge`, `/stream.mjpg`, `/ws`), `static/duet.css`, and `static/duet.js`, served from the `/static` mount the backend is adding tonight. If the mount is missing at swap-in time, the CSS and JS are inlined into `index.html` by hand and the split is kept in the working tree for later.

`duet.js` is organized as small modules in one file with clear seams: `geometry` (board order, homography, displayed rect), `viewer` (sources, loop, crop), `layers`, `story` (state table, bubbles, thinking animation, path preview), `audio`, `panel`, `socket`. Each is a plain object with functions; no framework, no build step, no external scripts.

Every meaningful element carries a specific `data-el` name and the page includes the D-key developer-mode snippet.

## 11. Testing

- **Against the fakes**: `python -m duet.run --fake` (backend, tonight) serves the real protocol with a fake camera, arm, and canned proposals. The acceptance walk: open `/?view=console`; watch a full exchange; confirm each row of the state table in section 3, the ghost preview then solid fill, the loop after `finished`, Go sending `pass`, a refused setting showing in red, and reconnect after killing and restarting the server.
- **Registration**: with the fake camera, turn on Board and confirm the outline sits on the four corner marks; step to a robot photo and confirm the green strokes sit on the green ink; toggle crop and confirm nothing slides. With Clean board on, the white mask's hole must coincide with the dashed inset of the Board layer.
- **Bubble placement**: on a turn whose plan sits in the board's left half the speech bubble is on the left with its tail pointing right, and the reverse on the right half; opening the panel moves a low bubble up above it.
- **Self-test**: `/?selftest=1` runs the geometry functions in the console: the calibration's four corners must map to the SVG corners within 0.5 px, `boardOrder` must agree with `vision.board_quad` on the shipped `calibration.json`, and the contain-rect math must be exact for 16:9 and 4:3 stages. Failures print in red; nothing else changes on the page.
- **Backend tests** that touch the page keep passing: `tests/test_web.py` checks the served page for the strings listed in section 10.
- **Sound**: with the mute off nothing plays and no `AudioContext` is created; with it on, the first click unlocks audio and the chime plays on the next state change.

## 12. Mockup reference

The approved interactive mockup is reproducible from `docs/duet/mockups/stage-viewer.template.html` and `docs/duet/mockups/build.py`, which inline tonight's session `20260918-190258` (photos, plan SVGs, history) and `duet/data/calibration.json`. Run `build.py` from the repo root with a source template and an output name; it writes into the brainstorm screen directory it is pointed at. The session files are gitignored, so the mockup rebuilds only on this machine.

## 13. Open items for the backend (asked, awaiting or landed)

| Item | Status |
| --- | --- |
| `calib` message and `/calibration.json` | landed |
| `/stream.mjpg?overlay=0` | landed |
| `shot.frame_url` raw landscape frame; landscape `session.mp4` | landing tonight |
| `interpretation.quip` and `interpretation.thought` with fixed fallback lines | landing tonight |
| `set direction` and `set energy`, validated and echoed in `state` | landing tonight |
| `state.artists` list | landing tonight, `["haring"]` at first |
| Mondrian and Van Gogh grammars | optional, last task of the night |
| `/static` mount | landing tonight |
