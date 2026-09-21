# Duet: a robot arm that draws with you

You draw one mark on a whiteboard. Duet looks at it, works out what the drawing is becoming, and answers in the hand of an artist. You take turns until the piece is done, then it signs, and the photos of every turn become a short film.

Built in a day at Viam's Fine Motor Skills hackathon, New York, September 18 to 19, 2026, on a UFACTORY xArm 6 with a gripper and a wrist camera, running on [Viam](https://www.viam.com). Honorable mention.

## See it

The showcase site has three pages: a homepage, the pitch deck, and a demo that replays the longest piece of the day, with a cartoon hand doing the visitor's part.

```
python3 -m http.server 8090 -d site
```

Then open http://localhost:8090/ (the homepage), `/presentation/` (the deck), and `/demo/`. On the demo: Start begins the piece; the arrow keys move it by half an exchange; a click on the turn clock pauses and resumes; C opens the controls, G the diagnostics, D the developer mode. `?speed=2` runs it twice as fast.

The deck on its own: `open docs/duet/pitch/index.html`. Right or space advances, 1 to 7 jump, F is fullscreen, P plays it on a loop, N shows the speaker's notes.

## How it works

Every exchange is the same loop, on a real machine or in replay:

1. **Look.** The arm parks at a look pose above the board and the wrist camera watches. The page says "Your turn!".
2. **Capture.** You draw one mark and press Go (or put the marker back in its cap, with the dock handoff). The camera takes a photo, and the new ink is what got darker since the last look, traced into strokes and mapped onto the board in millimetres.
3. **Interpret.** The artist decides what to add. Six artists ask Claude: it is told what the board looks like so far and answers with one sentence about what it sees, one about what it will add, and the strokes. Two ink artists work locally: Mimic copies your mark beside itself, Shader fills your shapes with dots.
4. **Plan and draw.** The strokes are checked against the board and the arm's reach, budgeted by the piece's length setting, and drawn through Viam's motion service while a ghost pen previews them on the page.
5. **Sign.** After the last exchange the arm signs, the recorder stitches the turn photos into `session.mp4`, and the page offers the piece to watch.

The page is a small FastAPI app with a WebSocket. It shows the camera, the chips and the speech bubble of the story, the artist picker, a controls panel (layers, picture levels, session settings, arm resets), and a diagnostics drawer that logs every frame. In replay mode the same page is driven by a recorded session instead of a socket; that is what the showcase demo is.

## Run it

Python 3.12. From `code/hackathon`:

```
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env        # machine address and API key from the Viam app's CONNECT tab; Anthropic key for the Claude artists
.venv/bin/python -m duet.run                   # the machine, page at http://localhost:8000
./demo.sh                                      # the same, relaunched if the connection drops
```

Without a machine, the fake run replays a recorded session through a fake camera and arm. The showcase session ships with the repo:

```
.venv/bin/python -m duet.run --fake --replay ../../../site/demo/sessions/20260919-151119
.venv/bin/python -m duet.run --fake --claude --replay ../../../site/demo/sessions/20260919-151119   # the real Claude call on the real boards
```

Tests: `.venv/bin/python -m pytest -q` for the Python side and `node --test 'pagetests/*.test.mjs'` for the page, both from `code/hackathon`. Rebuild the showcase site after changing the page, the deck, or the recording with `python3 site/build.py` (see `site/README.md`).

## Map

| Path | What it is |
| --- | --- |
| `code/hackathon/duet/` | The app: camera and vision, the session loop, the artists (`styles/`), the planner and stroke geometry, the controller, the recorder, the web page (`static/`) and its replay mode |
| `code/hackathon/tests/`, `pagetests/` | pytest for the Python side, Node's test runner for the page's modules |
| `docs/duet/` | The product brief, the design system, mockups, and the pitch deck (`pitch/`) |
| `docs/superpowers/` | The working record: a design spec and an implementation plan for each piece of the build, in the order they were made |
| `site/` | The showcase site: homepage, the deck as the presentation, the demo in replay mode with one recorded session; deploys as a static folder |
| `notes/` | Where the repo began: notes from Viam's 101 workshop (a palletizing robot in simulation) and the hackathon prep |
| `docs/viam/` | A Markdown mirror of Viam's documentation, kept for offline search; Viam's, under CC BY-SA 4.0 |
| `resources.md` | Links |

Secrets live only in `code/hackathon/.env`, which is gitignored; `.env.example` lists every key. Recorded sessions, camera captures, and the third-party reference clone are gitignored too.

## Credits

Made by Nicholas Fjellberg Swerdlowe. The robot, the machine platform, and the hackathon are Viam's. The Claude artists are Anthropic's Claude; the code was written with Claude Code; the deck's illustrations were generated with Nano Banana 2. The Haring, Mondrian, and Van Gogh artists are homages in the style of those painters, drawn by rules and prompts, not from their works.

## Rights

This repository is published to be read. No open-source license is granted: the code, the deck, the site, and the notes are copyright 2026 Nicholas Fjellberg Swerdlowe, all rights reserved. The exception is `docs/viam`, which is Viam's documentation redistributed unchanged under CC BY-SA 4.0. If you would like to use something here, ask.
