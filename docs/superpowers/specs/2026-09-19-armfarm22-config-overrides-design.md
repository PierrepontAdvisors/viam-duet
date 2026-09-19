# armfarm22 config overrides: design

Date: 2026-09-19 (demo day). Machine: `armfarm22` in the Viam org "hackathons" (Fine Motor Skills location). Executed by Claude in the user's logged-in Chrome session, on the user's go, after the backend session is finished; every save is confirmed in chat first.

## 1. Why

The app config was reviewed against the Duet code on the morning of 2026-09-19. Names (`arm`, `gripper`, `cam`, motion `builtin`), the 1280x720 color stream, big-endian depth, the gripper frame (105 mm down the arm, th 180) and the obstacles fragment (table, wall-front, wall-side, ceiling) already match. Three values do not:

| Setting | App today | Needed | Why |
|---|---|---|---|
| cam `align_color_depth` | absent (false) | `true` | `duet/vision.py` draws the board mask on the color image and reads depth under it. Unaligned depth has the same 1280x720 shape, so `duet/camera.py`'s shape check cannot catch the mismatch and the hand check would silently read the wrong pixels. |
| arm `speed_degs_per_sec` | 60 | 30 | Design spec section 2. The code sets 30/15/10 at run time through `set_speed`, so this fixes the startup default and the app's own jog and move panels. |
| arm `collision_sensitivity` | 0 (off) | 3 | Collision detection on. The design spec asked for 5; 3 (the module default) was chosen on 2026-09-19 because day 1 ran with detection off and pen contact at 5 is untested. If 3 trips while drawing, the page's Clear arm error and Resume recover. |

All three live in the fragment `xarm-realsense-gripper2` (`859f2598-60f1-43a2-8df2-13ffbee949cc`), so on this machine they become fragment overrides, like the cam frame `z: 25` override that is already there.

## 2. The change

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

Nothing else in the config changes: not the gripper, the obstacles fragment (`01ca42e4-78b9-425c-ae75-1101b9a7f3e8`), the `motion` service, the four `arm-position-saver` switches, or the modules list. The motion service's `input_range_override` (joint 5, from the cheatsheet) is deliberately left out: it is not in the spec and could make taught poses unreachable before the demo.

## 3. Pre-flight

Checked and stated in chat before the save; the user confirms:

- The machine reads ONLINE in the app.
- No Duet process is running on the Mac: `pgrep -fl "duet|explore"` prints nothing.
- The marker is not in the gripper and the workspace is clear. The save restarts the arm module (it reconnects to the control box; the arm holds position) and restarts the camera at the new alignment setting.
- The E-stop is within reach of whoever is at the station.

## 4. Procedure

1. Open `https://app.viam.com/machine/7d49b15e-a2a7-47b8-beec-f66ff062a979/configure/json?org=6d6c7293-bc67-43e4-9c8b-31c76aac27d3` in Chrome.
2. Apply the edit from section 2 to the `$set` block. Read the editor text back and check it matches section 2 exactly (the three new keys, the fragment id, no other diff). Show the diff in chat.
3. On the user's confirmation, click Save.
4. Wait until `arm` and `cam` read READY in the builder. Open the arm card: attributes show `speed_degs_per_sec: 30` and `collision_sensitivity: 3`. Open the cam card: attributes include `align_color_depth: true`. Both now carry the MODIFIED badge.

If Save is refused (permissions) or a resource stays in error for more than about a minute, stop, report the app's error text, and do not retry the save without the user.

## 5. Verification (read only, no arm motion)

From `code/hackathon` with `.venv` active:

- `python explore.py`: connects, lists resources including `arm`, `gripper`, `cam`, saves `captures/depth.dep`, and the E-stop is not latched.
- Depth shape check: `python -c "from pathlib import Path; from duet.camera import decode_depth; print(decode_depth(Path('captures/depth.dep').read_bytes()).shape)"` prints `(720, 1280)`.
- `python -m duet.controller` prints the arm status without moving.

The plane fit at the look pose (`calibrate --plane`) is the real test of alignment and stays where it is, in the morning checklist.

## 6. Rollback

Remove the three new keys from the `$set` block (leave `components.cam.frame.translation.z: 25`) and save. The machine returns to the fragment values: speed 60, collision detection off, unaligned depth.

## 7. Docs

- `docs/superpowers/specs/2026-09-18-duet-design.md` section 2: the line asking for `collision_sensitivity` 5 gains a note that 3 was applied on 2026-09-19 and why.
- `notes/hackathon/05-morning-checklist.md`, last bullet of "Rest of the morning": "collision sensitivity 5 on the arm" becomes a pointer to this plan (applied at 3).
- `notes/hackathon/01-machine-config-cheatsheet.md` is unchanged.
