"""Constants for Duet. Geometry is in board millimeters. Speeds are xArm joint speeds in degrees per second."""
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_DIR / "data"                 # poses.json and calibration.json, committed
SESSIONS_DIR = PACKAGE_DIR.parent / "sessions"  # per-session photos and video, gitignored

POSES_PATH = DATA_DIR / "poses.json"
CALIBRATION_PATH = DATA_DIR / "calibration.json"

# Writing surface inside the raised frame, measured from the taught corners on 2026-09-18: the edge
# touched off as top-left -> top-right is the short one. Board x runs along it, board y down the long edge.
BOARD_W_MM = 176.0
BOARD_H_MM = 240.0
INSET_MM = 15.0        # drawable area starts this far inside the corners
LIFT_MM = 20.0         # pen-up travel height above the board
PEN_DOWN_OFFSET_MM = 1.0  # above the touched-off plane; re-teach corners with the held marker, then tune with stroke_bench --pen
WAYPOINT_MM = 8.0      # spacing of planned moves along a stroke; set from the stage 2 measurement

SPEED_TRAVEL = 30.0    # deg/s, matches the machine's configured speed
SPEED_DRAW = 15.0
SPEED_DOCK = 10.0

MARKER = "green"             # the dock slot name, used only when HELD_MODE is False
HELD_MODE = True             # demo decision 2026-09-18: the robot keeps its marker; dock pick and return are skipped
GRIPPER_OPEN_FOR_PICK = 500   # 0 closed .. 850 open; set to barrel width + 15 mm in stage 3
UNCAP_LIFT_MM = 40.0          # straight-up pull that uncaps the marker
DOCK_HOVER_MM = 60.0          # safe height above a slot
DOCK_ENTRY_MM = 60.0          # free planned moves end this far above the approach pose; the rest is vertical
RELEASE_DROP_MM = 5.0         # on return, open this far above the seat pose so the marker drops into its cap

BUDGET_MM = {"short": 400.0, "medium": 1200.0, "long": 3000.0}
BUDGET_S = {"short": 15.0, "medium": 40.0, "long": 90.0}

MOVE_TIMEOUT_S = 30.0
LINE_TOLERANCE_MM = 1.0

HAND_CHECK_TIMEOUT_S = 2.0    # a hand check slower than this counts as a hand present
GRIPPER_SETTLE_S = 0.3        # pause after grab or open before the next move
REQUIRE_GRAB_DETECT = False   # set True in stage 3 if this gripper unit reports grab() reliably
