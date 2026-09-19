# Machine config cheatsheet (from the crash-course deck)

The team machine should arrive with all of this configured. This is here so I can recognize it, repair it, or rebuild it.

## Components
| Name | Model | Attributes |
|------|-------|------------|
| `arm` | `viam:ufactory:xArm6` (or the 850 model) | `{"host": "<control box IP>", "speed_degs_per_sec": 30}` |
| `gripper` | `viam:ufactory:gripper` | `{"arm": "arm"}` — the gripper names the arm it hangs off |
| `cam` | `viam:camera:realsense` | `{"serial_number": "<from discovery>", "sensors": ["color", "depth"], "align_color_depth": true}` |

- Camera discovery: add `viam:realsense:discovery` (or `viam:orbbec:discovery`) as a service, refresh it to get the serial number, add the camera it found, then delete the discovery service.
- Testing from the app: the arm card in CONFIGURE has joint sliders, jog buttons, and an end-position editor. Each maps to an arm API call. Gripper card has Open / Grab and shows IsHoldingSomething. Camera control panel shows live color/depth and a 3D point cloud.

## Frames (RealSense on xArm6; other hardware needs its own measurements)
| Frame | Parent | Translation (mm) | Orientation (ov_degrees) |
|-------|--------|------------------|--------------------------|
| `arm` | `world` | 0, 0, 0 | z=1, th=0 |
| `gripper` | `arm` | 0, 0, **105** | z=1, th=0 |
| `cam` | `arm` | **73, -40, 18** | z=1, **th=90** |

For a precise camera frame, the deck points at the `viam:camera-calibration:handeye` service.

Heads-up: the companion repo's reference config uses `arm-1` / `gripper-1` / `cam-1` and a camera frame of translation (-73, 40, 18) with th=270, while the deck says `arm` / `gripper` / `cam` and (73, -40, 18) with th=90. Those two camera frames are not the same placement. Trust whatever is on the team machine, and check it in the 3D scene: the camera should sit where it physically is on the wrist.

## Obstacles
- On `armfarm22` (checked 2026-09-18): `table`, `wall-front`, `wall-side`, `ceiling`. Resource names match the deck: `arm`, `gripper`, `cam`.
- `table` and `wall` are `erh:vmodutils:obstacle` resources. The motion service plans around them. Direct arm moves do not.
- Each obstacle is a `geometries` list (box dimensions, centered on the component's origin) plus a `frame` parented to `world`. They present on the API as grippers, so they appear among the grippers in `resource_names`. Reference shapes from the companion repo: table 1200 × 800 × 30 at z = -15; safety walls 20 × 1200 × 600 at z = 300.

## Motion service joint limits
The built-in motion service accepts `input_range_override` to narrow joint ranges below the kinematic limits. Keys are the arm name, then joint index (from 0) or joint name. Values are **radians** (1.5708 = 90°, 0.7854 = 45°). Optional `max_velocity` and `max_acceleration` alongside `min`/`max`. Deck recommendation: limit joint 5 so the camera cable can't wind around the wrist. This shapes planned motion only.

```json
{
  "input_range_override": {
    "arm": {
      "0": { "min": -1.5708, "max": 1.5708 },
      "5": { "min": -1.5708, "max": 1.5708 }
    }
  }
}
```

## Vision options the deck recommends
| Need | Module |
|------|--------|
| Find simple shapes, then segment them in 3D | `devrel:shape-finder:detector` + `viam:vision:detections-to-segments` |
| General object detection / classification | `viam-labs:vision:yolov8` (model_location = stock model name, local file, or Hugging Face repo id) |
| Pre-trained COCO detector | built-in `rdk:builtin:mlmodel` vision service over `viam:mlmodel-tflite:tflite_cpu` running `viam-labs/EfficientDet-COCO` |
| Hand gestures (7 classes) | `viam:hand-gesture-recognition:gestures` |
| Fiducial pose tracking | `viam:apriltag:pose_tracker` |

## Helpers worth knowing
- **Manual mode** on the arm's Configure panel: move the arm by hand to find a pose.
- `erh:vmodutils:arm-position-saver`: records the current pose and can return the arm to it later.
- Quick test tray: pin a control so it stays visible while navigating the app.
- Picture-in-picture: keep the camera feed visible while moving the arm.
- Data manager service: capture images and joint positions, sync to the app, review failed grasps, or train a model.
- CONTROL tab Sandbox: run SDK code in the browser without installing anything.
- CONNECT tab: pick a language, toggle "Include API key", copy the snippet. Never commit the key.
