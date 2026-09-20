# Duet showcase site: homepage, presentation, and a replayed demo on Vercel

Date: 2026-09-20, the morning after the hackathon. Status: built from Nicholas's goal without a brainstorm round (the goal was set as a directive). Branch `feat/showcase-site`, worktree `.worktrees/showcase-site`. Parent specs: `2026-09-18-duet-page-design.md` (the page), `2026-09-19-duet-pitch-deck-design.md` (the deck), `2026-09-19-duet-artists-design.md` (the artists the replayed session used).

## 1. What it is

A static site in `site/` at the repository root, deployable to Vercel with no build step. Three parts, one look:

- **Homepage** `site/index.html`: the Duet logo, the one-line thesis, the hackathon and the honorable mention, and two toy-press buttons: "Watch the presentation" and "Play the demo".
- **Presentation** `site/presentation/`: a copy of the pitch deck in `docs/duet/pitch/`, with a Home link in its bottom-left corner mirroring the playbar.
- **Demo** `site/demo/`: a copy of the live page in `code/hackathon/duet/static/` running in **replay mode**: no WebSocket and no camera stream; a scripted stream of the same protocol messages, built from the recorded session with the most turns (`20260919-151119`, ten exchanges: Mimic, Shader, Haring, Van Gogh), with the turn photos as the picture and a Home chip in the top-right row and on the welcome page.

The look is shared because all three use the same tokens (`tokens.css`), the same embedded Fredoka, the same logo symbol, the yellow squiggle mat, paper cards, pill chips, and the toy-press button. Nothing in the live page's look changes; replay mode only hides what has no meaning without a robot.

## 2. Layout of `site/`

```
site/
  index.html, home.css        hand-written homepage
  vercel.json                 clean URLs; long cache for the session photos
  README.md                   how to rebuild and deploy
  build.py                    assembles assets/, presentation/, demo/ from the sources (stdlib only)
  assets/tokens.css, fredoka.css          copied from duet/static
  presentation/               copied from docs/duet/pitch (index, deck.css, deck.js, dev.js, fredoka.css, img/)
  demo/index.html             duet/static/index.html with /static/ made relative and a replay meta tag
  demo/static/                copied from duet/static
  demo/replay.json            the session as data: turns, words, strokes, calibration
  demo/sessions/<id>/         the session's photos, frames, plan SVGs, session.json, session.mp4
```

The generated parts are committed, so Vercel serves `site/` as is (Root Directory `site`, no build command). Identical images in `docs/duet/pitch/img` and `site/presentation/img` are one blob in git. Rebuild after changing the page, the deck, or the session:

```
python3 site/build.py                       # picks the session with the most turns under code/hackathon/sessions
python3 site/build.py --session 20260919-151119
```

## 3. Replay mode in the page

`duet/static/js/replay.js`, new. Two parts:

- **`schedule(replay, speed)`**, pure: `replay.json` in, a list of steps out. A step is `{ emit: msg }` or `{ wait: ms, on?: 'pass' }`. The piece runs: state `look` and the start shot; then per exchange: `human_turn` (a 4 s wait that Go, the `pass` command, cuts short), `capture` with the human shot and the `human` message (the visitor's ink so far, and this turn's new strokes), `interpret` with the `interpretation` (1.2 s for an ink artist, 3.5 s for a Claude turn), `plan` with the plan strokes, `robot_draw` with a `progress` per stroke paced so a turn's drawing takes 3 to 12 s, the robot shot, `look` with the exchange counted, and `feed` live/held around the arm's move; then `finish`, `finished`, and the `video`. Waits divide by `speed` (`?speed=2` on the URL).
- **`Player`**: runs the steps with `setTimeout`, feeds each message to the page exactly as a socket frame would arrive (through `parseMessage`, recorded in the diagnostics drawer), and takes the page's commands: `pass` ends the scripted human turn, `pause`/`resume` hold the clock, `restart` begins the piece again under a new session id suffix so the page forgets the last strokes, `end` jumps to the finish. Settings and arm commands are ignored.

Words: the ink artists' thoughts and quips are the stylers' own banks, indexed by exchange as the backend does, so the replay says what the live page said. Claude turns carry `thought`/`quip` from `replay.json` when the build has them (a per-session table in `build.py`), else a line derived from `sees` and `adds`.

`app.js` reads `<meta name="duet-replay" content="replay.json">`. When present it does not open a socket: it loads the replay, marks the body `replay`, shows the Home links, treats the page as connected, routes `send()` to the player, points the "live" picture at the latest camera frame from each shot, and skips the plan back-fill. The welcome's Start begins the piece; on a finished piece it restarts it, as on the live page.

Hidden in replay mode (`.live-only`): the Session, Artist, Run, and Light rows of the controls panel. Kept: Image, Layers, Picture, the status lines (which say `replay` instead of `ws connected`), the diagnostics drawer, the artist picker as a read-only label, Go (it skips the wait), the sound.

## 4. Ink and strokes from the recording

Each `plan-NN.svg` holds three kinds of path: all traced ink on the board (`#222`), the robot's own strokes so far (solid green), and this turn's plan (dashed green). The build derives:

- `plan` = the dashed paths.
- `new` = the traced paths of this turn that are not near (within 3 mm for most of their points) the traced paths of the previous turn, and not near the robot's own strokes (4 mm), so the visitor's new marks come out and the robot's marks, which the camera also sees as ink, stay out.
- The `human` message's `polylines` = the union of `new` over the turns so far.

## 5. The homepage

A 16:9 mat like the page and the deck, the yellow squiggle behind a paper card: logo, "A robot arm that draws **with** you.", one paragraph (Viam's Fine Motor Skills hackathon, New York, September 18 to 19, 2026, honorable mention), the two buttons, a caption saying what the demo replays, and the deck's footer strip. D-key developer mode as everywhere else.

## 6. Tests

- `pagetests/replay.test.mjs`: words per artist and turn; the step sequence for a two-turn fixture (types, order, relative URLs, accumulating ink, progress per stroke, speed halving waits); the Player runs a fixture through a stubbed sleep and honours pass and restart.
- `tests/test_site_build.py`: plan SVG parsing; new-ink derivation on synthetic paths; the longest-session pick; a build into a temporary folder from a synthetic session yields the expected files, a relative `demo/index.html` with the meta tag, and a `replay.json` with the turns.
- `pagetests/pitch.test.mjs` and `welcome.test.mjs` keep passing with the Home links added.
- Manual: `python3 -m http.server 8090 -d site`, then the three pages in a browser.

## 7. Deploy

`cd site && vercel --prod` (the CLI is logged in as nswerdlowe-1729), or import the repository in the Vercel dashboard with Root Directory `site` and no build command.
