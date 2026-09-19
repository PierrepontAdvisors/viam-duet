# Hackathon starter code

Python 3.12 virtual environment with the Viam SDK, plus three small scripts.

```bash
cd code/hackathon
source .venv/bin/activate
cp .env.example .env      # then paste address, key id, key from the machine's CONNECT tab
python explore.py         # read-only: resources, arm pose, gripper state, camera frames
python moves.py where     # gripper tip pose in world
python moves.py up 50     # planned 50 mm lift, obstacles honored
```

| File | Purpose |
|------|---------|
| `viam_conn.py` | Reads `.env`, exposes `connect()` and the resource names |
| `explore.py` | Connection proof. Prints everything, moves nothing, saves camera frames to `captures/` |
| `moves.py` | Verb-per-command test moves through the motion service: `where`, `open`, `grab`, `up`, `down`, `goto`, `stop` |
| `reference/pick-and-place/` | Clone of viam-devrel/pick-and-place (gitignored). `scripts/reference-solution.py` is a complete detect-pick-place loop on this exact hardware |
| `duet/` | The Duet drawing robot. `python -m duet.<module>`; each module's docstring has its usage. Day 1: `teach`, `stroke_bench`, `dock_test`, `aim`, `calibrate`, `claude_turn`, `turn` (terminal loop). Night 1: `trigger`, `session`, `recorder`, `web`, `run`, `fakes` |
| `duet/run.py` | `python -m duet.run` starts everything against the machine with the page on http://localhost:8000; `--fake` replays the real day-1 boards through a fake camera and arm; `--fake --claude` adds the real Claude call |
| `duet/web.py` | The stream holds the last capture still while the arm is away from the look pose, sends new frames only at 4 fps (a keep-alive every 10 s), and freezes instead of showing a gray card when the camera stalls; the `feed` event tells the page which picture it is seeing. End session (`end`) finishes the piece at the next safe point; Start on the welcome (`restart`) begins the next piece in place; Relaunch run (`relaunch`) exits the run cleanly so `demo.sh` starts it again with the code on disk |
| `tests/fixtures/` | A real look-pose frame and the boards of the first hardware exchange, used by the tests and by `run.py --fake` |
| `sessions/` | One folder per session (gitignored): turn photos, plan SVGs, `session.json`, `session.mp4` |

Names default to the hackathon deck's `arm`, `gripper`, `cam`. Override in `.env` if the machine uses `arm-1` style names.

Never commit `.env`. It's in the repo's `.gitignore`.
