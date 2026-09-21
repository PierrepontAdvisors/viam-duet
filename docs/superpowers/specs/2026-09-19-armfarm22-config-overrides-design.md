# armfarm22 config overrides and board obstacle: design

Date: 2026-09-19 (demo day). Machine: `armfarm22` in the Viam org "hackathons" (Fine Motor Skills location). Executed by Claude in the user's logged-in Chrome session, on the user's go, after the backend session is finished; every save is confirmed in chat first.

## 1. Why

The app config was reviewed against the Duet code on the morning of 2026-09-19. Names (`arm`, `gripper`, `cam`, motion `builtin`), the 1280x720 color stream, big-endian depth, the gripper frame (105 mm down the arm, th 180) and the obstacles fragment (table, wall-front, wall-side, ceiling) already match. Three values do not:

| Setting | App today | Needed | Why |
|---|---|---|---|
| cam `align_color_depth` | absent (false) | `true` | `duet/vision.py` draws the board mask on the color image and reads depth under it. Unaligned depth has the same 1280x720 shape, so `duet/camera.py`'s shape check cannot catch the mismatch and the hand check would silently read the wrong pixels. |
| arm `speed_degs_per_sec` | 60 | 30 | Design spec section 2. The code sets 30/15/10 at run time through `set_speed`, so this fixes the startup default and the app's own jog and move panels. |
| arm `collision_sensitivity` | 0 (off) | 3 | Collision detection on. The design spec asked for 5; 3 (the module default) was chosen on 2026-09-19 because day 1 ran with detection off and pen contact at 5 is untested. If 3 trips while drawing, the page's Clear arm error and Resume recover. |

All three live in the fragment `xarm-realsense-gripper2` (`859f2598-60f1-43a2-8df2-13ffbee949cc`), so on this machine they become fragment overrides, like the cam frame `z: 25` override that is already there.

A fourth item was added on 2026-09-19: the 3D scene shows only the four obstacle boxes (a 3 m table slab with its top 23 mm below the arm base, a front wall at x 740, a side wall at y 500, a ceiling at 1050). Nicholas asked for the drawing board in the scene, generated from data rather than measured, so section 2b adds a `board` obstacle computed from the taught corners. The dock tub is left out because its footprint and height are unknown.

## 2a. The three overrides

One edit to the machine JSON (Configure tab, JSON view). The existing `$set` for that fragment under `fragment_mods` grows from one key to four:

```json
"fragment_mods": [
  {
    "fragment_id": "859f2598-60f1-43a2-8df2-13ffbee949cc",
    "mods": [
      {
        "$set": {
          "components.cam.frame.translation.z": 25,
          "components.cam.attributes.align_color_depth": true,
          "components.arm.attributes.speed_degs_per_sec": 30,
          "components.arm.attributes.collision_sensitivity": 3
        }
      }
    ]
  }
]
```

Nothing else in the fragment overrides changes. The gripper, the obstacles fragment (`01ca42e4-78b9-425c-ae75-1101b9a7f3e8`), the `motion` service, the four `arm-position-saver` switches, and the modules list stay as they are. The motion service's `input_range_override` (joint 5, from the cheatsheet) is deliberately left out: it is not in the spec and could make taught poses unreachable before the demo.

## 2b. The board obstacle

One new component appended to the machine's `components` list, in the same edit and save as 2a:

```json
{
  "name": "board",
  "api": "rdk:component:gripper",
  "model": "erh:vmodutils:obstacle",
  "attributes": {
    "geometries": [
      { "type": "box", "label": "board", "x": 240, "y": 176, "z": 20 }
    ]
  },
  "frame": {
    "parent": "world",
    "translation": { "x": 392.5, "y": -260.5, "z": -13 },
    "orientation": { "type": "ov_degrees", "value": { "x": 0, "y": 0, "z": 1, "th": 0 } }
  },
  "ui_folder": { "name": "obstacles" }
}
```

Where the numbers come from:

- **Position** from the three taught corners in `duet/data/poses.json` (`corner.bl`, `corner.tl`, `corner.tr`: gripper-origin poses with the pen tip on the inner corner marks, which sit `INSET_MM` 15 mm inside the board edges). Center is the midpoint of `bl` and `tr`; rotation is the direction of the `bl` to `tl` edge. With the poses on disk at 12:00 on 2026-09-19 (the backend session is re-teaching them, so the file is ahead of git): center x 392.5, y -260.6, edge 208 by 144 mm at -0.14°, so the box is axis-aligned, rotation 0. The committed poses gave x 389, y -261.5 and edges 239 by 176 (taught at the physical corners on day 1); the center barely moves, which is the point of using the midpoint.
- **Size** is the nominal board, `BOARD_H_MM` 240 along world x by `BOARD_W_MM` 176 along y, not the measured edges: the marks are inset symmetrically, so the center is right either way and the nominal size draws the whole board. The script checks the measured edges against both 240 by 176 and 210 by 146 (nominal minus twice the inset) and warns when neither matches within 10 mm; it still prints the JSON.
- **Height** is an assumption, not a measurement: the box sits on the configured table top (z -23, the table obstacle's -123 plus half its 200 mm thickness) and is 20 mm thick, so it spans z -23 to -3 and its center is z -13. The two saved depth frames could not confirm this (`captures/depth.dep` was taken at another pose; `captures/look.dep` reads 720 mm through glare on the whiteboard). A centimeter of error changes the picture, not planning.
- **Planner safety**: the gripper reports two boxes (`case-gripper` 50x100x100 centered 50 mm behind the origin, `claws` 40x170x105 centered 2.5 mm behind it), so the lowest gripper geometry is 50 mm past the gripper origin. At pen contact the origin is at z about 125, which leaves at least 75 mm above world zero and about 78 mm above the board's top. The pen is not modelled, so drawing moves are unaffected. Obstacles do not collide with each other, so the board resting on the table slab is fine.
- **Module**: `erh:vmodutils` is already on the machine through the obstacles fragment; a machine-level component may use it.

The JSON is produced by a script, not typed: `python -m duet.board_obstacle` reads `duet/data/poses.json` and prints the component above. `duet/config.py` gains two constants, `TABLE_TOP_Z_MM = -23.0` and `BOARD_THICKNESS_MM = 20.0`, next to the board size. The script rounds the translation to 0.5 mm, uses the nominal box, and takes the box's rotation from the `bl` to `tl` edge only when it exceeds 1°, otherwise 0. One unit test in `tests/test_board_obstacle.py` feeds it three synthetic corners and checks center, dims, rotation, the edge warning and the JSON shape. The script runs at execution time, against whatever poses are on disk then; the numbers above are illustrative. If the board is re-taught later, rerun it and paste again.

## 3. Pre-flight

Checked and stated in chat before the save; the user confirms:

- The machine reads ONLINE in the app.
- No Duet process is running on the Mac: `pgrep -fl "duet|explore"` prints nothing.
- The marker is not in the gripper and the workspace is clear. The save restarts the arm module (it reconnects to the control box; the arm holds position) and restarts the camera at the new alignment setting.
- The E-stop is within reach of whoever is at the station.

## 4. Procedure

1. Open `https://app.viam.com/machine/<machine-id>/configure/json?org=<org-id>` in Chrome.
2. Apply the edit from section 2a to the `$set` block and append the `board` component from section 2b (as printed by the script) to `components`. Read the editor text back and check it matches sections 2a and 2b exactly (the three new keys, the fragment id, the one new component, no other diff). Show the diff in chat.
3. On the user's confirmation, click Save.
4. Wait until `arm`, `cam` and `board` read READY in the builder. Open the arm card: attributes show `speed_degs_per_sec: 30` and `collision_sensitivity: 3`. Open the cam card: attributes include `align_color_depth: true`. Both now carry the MODIFIED badge. Open the 3D SCENE tab: a 240 by 176 slab sits on the table in front of and to the right of the arm base (world +x, -y), under the parked arm's wrist.

If Save is refused (permissions) or a resource stays in error for more than about a minute, stop, report the app's error text, and do not retry the save without the user.

## 5. Verification (read only, no arm motion)

From `code/hackathon` with `.venv` active:

- `python explore.py`: connects, lists resources including `arm`, `gripper`, `cam`, saves `captures/depth.dep`, and the E-stop is not latched.
- Depth shape check: `python -c "from pathlib import Path; from duet.camera import decode_depth; print(decode_depth(Path('captures/depth.dep').read_bytes()).shape)"` prints `(720, 1280)`.
- `python -m duet.controller` prints the arm status without moving.
- `python explore.py`'s resource list now includes `board` among the grippers (obstacles present as grippers). `Gripper.from_robot(machine, "gripper")` is by name, so the code is unaffected.
- `python -m pytest -q tests/test_board_obstacle.py` passes (the corner math), run before the app edit, not after.

The plane fit at the look pose (`calibrate --plane`) is the real test of alignment and stays where it is, in the morning checklist.

## 6. Rollback

Remove the three new keys from the `$set` block (leave `components.cam.frame.translation.z: 25`), delete the `board` component, and save. The machine returns to the fragment values: speed 60, collision detection off, unaligned depth, four obstacles.

## 7. Docs

- `docs/superpowers/specs/2026-09-18-duet-design.md` section 2: the line asking for `collision_sensitivity` 5 gains a note that 3 was applied on 2026-09-19 and why.
- `notes/hackathon/05-morning-checklist.md`, last bullet of "Rest of the morning": "collision sensitivity 5 on the arm" becomes a pointer to this plan (applied at 3).
- `notes/hackathon/01-machine-config-cheatsheet.md` is unchanged.
