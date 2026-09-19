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
PEN_DOWN_OFFSET_MM = -1.5  # relative to the touched-off plane (negative: below); corners re-taught 2026-09-19 with the held marker, tuned with teach touch
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

BUDGET_MM = {"short": 400.0, "medium": 1200.0, "long": 4000.0}
BUDGET_S = {"short": 30.0, "medium": 120.0, "long": 540.0}  # long is the "big scene" setting; tripled on day 2, the drawing ran short

MOVE_TIMEOUT_S = 30.0
LINE_TOLERANCE_MM = 1.0

HAND_CHECK_TIMEOUT_S = 2.0    # a hand check slower than this counts as a hand present
GRIPPER_SETTLE_S = 0.3        # pause after grab or open before the next move
REQUIRE_GRAB_DETECT = False   # set True in stage 3 if this gripper unit reports grab() reliably

COVERAGE_END = 0.33           # end the session when this fraction of the drawable area is inked

# ---- perception: trigger readings (plan 2) --------------------------------------------------
FIXTURES_DIR = PACKAGE_DIR.parent / "tests" / "fixtures"

DOCK_SLOTS = ("green",)         # markers in the dock; single-marker rig decided 2026-09-18
COLOR_HEX = {"green": "#1b8f3a", "red": "#c62828", "blue": "#1e56c9", "black": "#222222"}

CLEARANCE_MM = 8.0              # the robot never draws within this distance of existing ink (spec section 15)
DOT_TOLERANCE_MM = 3.0          # a docked marker's dot further than this from its recorded spot is "moved"
DOT_MIN_AREA_PX = 30            # smaller color blobs are noise, not a marker's end plug

STILL_WINDOW_S = 1.5            # frames compared for the stillness reading; the poller keeps 3 s; two frames must fit even at a 1 s cadence
STILL_THRESH = 3.0              # mean absolute gray difference between frames that still counts as still
STILL_S = 1.5                   # dock rule: markers home, still, no hand for this long
HELD_QUIET_S = 2.0              # held rule: still and no hand for this long after activity
TRIGGER_GRACE_S = 0.4           # one noisy poll must not restart the quiet timer; the scene must stay unsettled this long

HAND_HEIGHT_MM = 25.0           # depth check: anything this far above the board plane, over the board or dock, is a hand
HAND_AREA_MM2 = 2000.0          # a changed or raised blob at least this big is a hand, not ink
HAND_COLOR_AREA_MM2 = 5000.0        # color backup: a filled shape up to about 70 x 70 mm is not a hand; a hand only half in view (about 4000 mm²) is missed, a full palm (about 6000) is caught
HAND_DIFF_THRESH = 40           # color backup: gray difference from the reference frame that counts as changed
HAND_OPEN_PX = 9                # color backup: opening kernel that erases marker lines but not a hand

ARTIST = "abstract"        # demo default from day 2: clean abstract shapes, no passes or ticks
# A small glyph the robot signs with, in mm relative to its own top-left; the session places it in a corner.
SIGNATURE_MM = [[(0.0, 8.0), (4.0, 0.0), (8.0, 8.0)], [(2.0, 5.0), (6.0, 5.0)]]

# Open strokes (spec 2026-09-19): every plan large, single-lined, free of overlap, whatever the artist.
MIN_SHAPE_MM = 30.0             # a proposed shape smaller than this across is enlarged...
TARGET_SHAPE_MM = 40.0          # ...to this span, about its center
SELF_GAP_MM = 5.0               # a stroke is cut where it comes back within this of its own path
PARALLEL_GAP_MM = 6.0           # a stroke running alongside an earlier one within this is dropped
STROKE_CAP = {"short": 3, "medium": 8, "long": 15}  # strokes kept per turn, dots not counted (tripled on day 2)
DOT_SPACING_MM = 9.0            # pointillist fill: grid spacing, jitter, tick length, cap per turn
DOT_JITTER_MM = 1.5
DOT_MM = 1.5
DOTS_MAX = 60
DOT_EXEMPT_MM = 3.0             # polylines shorter than this are dots and skip the rules above
