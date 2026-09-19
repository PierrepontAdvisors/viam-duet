"""Designer: sharp corners are rounded; straight runs and gentle bends pass untouched."""
import math

from duet import config as cfg
from duet.styles import designer


def turn_angles(pl):
    out = []
    for p, q, r in zip(pl, pl[1:], pl[2:]):
        a1, a2 = math.atan2(q[1] - p[1], q[0] - p[0]), math.atan2(r[1] - q[1], r[0] - q[0])
        out.append(abs(math.degrees((a2 - a1 + math.pi) % (2 * math.pi) - math.pi)))
    return out


def test_a_square_gets_rounded_corners_including_the_closing_one():
    square = [(40.0, 40.0), (80.0, 40.0), (80.0, 80.0), (40.0, 80.0), (40.0, 40.0)]
    (out,), color = designer.style([square], energy=0.5, direction_deg=0.0)
    assert color == "green" and len(out) > 12
    assert max(turn_angles(out)) < cfg.FILLET_MIN_DEG
    assert math.dist(out[0], out[-1]) < 1e-9                                       # still closed
    assert all(40.0 - 1e-6 <= x <= 80.0 + 1e-6 and 40.0 - 1e-6 <= y <= 80.0 + 1e-6 for x, y in out)
    assert (40.0, 40.0) not in out                                                  # the closing corner is rounded too


def test_straight_lines_and_gentle_bends_are_unchanged():
    line = [(20.0, 20.0), (120.0, 20.0)]
    gentle = [(20.0, 20.0), (60.0, 22.0), (100.0, 30.0)]
    out, _ = designer.style([line, gentle])
    assert out == [line, gentle]


def test_a_short_side_limits_the_fillet():
    el = [(0.0, 0.0), (10.0, 0.0), (10.0, 60.0)]
    (out,), _ = designer.style([el])
    assert abs(out[1][0] - 5.5) < 1e-6 and abs(out[1][1]) < 1e-6              # rounding starts 4.5 mm before the corner
    assert abs(out[-2][0] - 10.0) < 1e-6 and abs(out[-2][1] - 4.5) < 1e-6     # and ends 4.5 mm after it
    assert designer.fallback([el])[1] == "green"
