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

Names default to the hackathon deck's `arm`, `gripper`, `cam`. Override in `.env` if the machine uses `arm-1` style names.

Never commit `.env`. It's in the repo's `.gitignore`.
