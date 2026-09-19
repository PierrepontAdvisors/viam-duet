"""Abstract mode: clean single lines, spaced apart, with a calm fallback."""
import math

from shapely.geometry import LineString

from duet import config as cfg
from duet.styles import abstract

LINE = [(30.0, 30.0), (80.0, 30.0)]
CIRCLE = [(100 + 10 * math.cos(t), 150 + 10 * math.sin(t)) for t in (i * 2 * math.pi / 24 for i in range(25))]


def test_style_keeps_strokes_as_given_with_no_extra_passes_or_ticks():
    out, color = abstract.style([LINE, CIRCLE], energy=0.9, direction_deg=45.0)
    assert color == "green"
    assert out == [[(30.0, 30.0), (80.0, 30.0)], [(float(x), float(y)) for x, y in CIRCLE]]


def test_fallback_is_one_arc_beside_the_mark_inside_the_inset_and_clear_of_the_ink():
    out, color = abstract.fallback([LINE])
    assert color == "green" and len(out) == 1 and len(out[0]) == 25
    xs, ys = [p[0] for p in out[0]], [p[1] for p in out[0]]
    assert min(xs) >= 15 and max(xs) <= cfg.BOARD_W_MM - 15 and min(ys) >= 15 and max(ys) <= cfg.BOARD_H_MM - 15
    assert LineString(out[0]).distance(LineString(LINE)) >= cfg.CLEARANCE_MM


def test_fallback_with_no_ink_sits_at_the_board_center():
    out, _ = abstract.fallback([])
    cx, cy = cfg.BOARD_W_MM / 2, cfg.BOARD_H_MM / 2
    assert all(abs(math.hypot(x - cx, y - cy) - abstract.FALLBACK_RADIUS_MM) < 1e-6 for x, y in out[0])


def test_fallback_near_the_right_edge_goes_left():
    right_mark = [(150.0, 100.0), (158.0, 100.0)]
    out, _ = abstract.fallback([right_mark])
    assert max(p[0] for p in out[0]) < 150
