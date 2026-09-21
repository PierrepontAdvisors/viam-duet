# Prep checklist

## Done on this Mac (2026-09-18)
- [x] Viam 101 completed (notes in `../modules/`)
- [x] Viam CLI installed via Homebrew: `viam version` → 1.8.0
- [x] Python 3.12 venv at `code/hackathon/.venv` with `viam-sdk`
- [x] Local docs mirror in `docs/viam/` (`grep -ril <term> docs/viam`), including the xArm6 pick-and-place tutorial under `docs/viam/tutorials/pick-and-place/`
- [x] Companion repo cloned to `code/hackathon/reference/pick-and-place/` (gitignored) (starter script, reference solution, config fragment, obstacle template, frame worksheet)
- [x] Starter scripts: `code/hackathon/explore.py` (read-only) and `moves.py` (planned test moves)
- [x] viam-server installed locally (only needed for the 101 machine; the hackathon machine runs its own)

## Do before hacking starts
- [ ] `viam login` in a terminal (opens a browser; sign in with the same account as app.viam.com)
- [ ] Join the hackathon Discord (invite on the Luma event page)
- [ ] Optionally add Viam's MCP server (https://app.viam.com/mcp) as a connector in Claude so it can read the machine directly
- [ ] Decide the challenge with the team. Note the pick in `04-plan.md`

## First 20 minutes with the hardware
1. Find the machine: Hackathons org → Fine Motor Skills location. Confirm it's ONLINE.
2. Locate the physical E-stop. Everyone on the team touches it once.
3. CONFIGURE tab: confirm `arm`, `gripper`, `cam`, `table`, `wall` are all READY. Read the LOGS tab if anything is red.
4. Move the arm a few degrees from the arm card (jog), then Open / Grab the gripper, then look at the camera's color, depth, and point cloud.
5. 3D SCENE: check the gripper and camera ride the arm, and the table and wall obstacles are where the real ones are.
6. CONNECT tab → Python → Include API key → copy. Put the key id, key, and address into `code/hackathon/.env` (gitignored). Run `explore.py` from `code/hackathon/` to prove the laptop can reach the machine.
7. Add the joint-5 limit to the motion service before any planned moves.

## Things to keep in mind
- Direct arm calls ignore obstacles. Use the motion service for anything near the table.
- Start slow: `speed_degs_per_sec` is 30 in the reference config. Leave it.
- Log every wrong turn in `../stuck-log.md`; the stuck log from Viam 101 already has the common Python mistakes.
