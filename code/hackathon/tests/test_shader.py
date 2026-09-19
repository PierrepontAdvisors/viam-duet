"""Shader: dots inside the visitor's closed shapes, denser away from the light; a band beside bare lines."""
import math

from shapely.geometry import LineString, Point, Polygon

from duet import config as cfg
from duet import planner
from duet.styles import shader


def circle(cx, cy, r, n=48):
    return [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in (2 * math.pi * i / n for i in range(n + 1))]


RING = circle(88, 120, 30)


def test_a_closed_shape_gets_dots_inside_it_that_survive_the_4_mm_clearance():
    t = shader.respond([RING], energy=0.5, direction_deg=0.0, exchange=1, length_setting="medium")
    assert t.color == "green" and 15 <= len(t.strokes) <= 60
    inside = Polygon(RING).buffer(cfg.DOT_JITTER_MM + 0.1)
    assert all(inside.contains(Point(d[0])) for d in t.strokes)
    plan = planner.finalize(t.strokes, [RING], cfg.BUDGET_MM["medium"], clearance_mm=shader.CLEARANCE_MM, length_setting="medium")
    assert len(plan) >= 10
    ring = LineString(RING)
    assert all(ring.distance(LineString(d)) >= shader.CLEARANCE_MM for d in plan)
    assert all(abs(math.dist(*d) - cfg.DOT_MM) < 1e-9 for d in plan)
    assert shader.CLEARANCE_MM == 4.0 and shader.FROM_INK is True


def test_dots_thin_toward_the_light():
    lit_right = shader.respond([RING], 0.5, 0.0, exchange=1, length_setting="long")       # light from the right
    left = sum(1 for d in lit_right.strokes if d[0][0] < 88)
    assert left > len(lit_right.strokes) - left
    lit_left = shader.respond([RING], 0.5, 180.0, exchange=1, length_setting="long")      # light from the left
    left2 = sum(1 for d in lit_left.strokes if d[0][0] < 88)
    assert left2 < len(lit_left.strokes) - left2


def test_a_bare_line_gets_a_band_of_dots_on_its_shadow_side_only():
    line = [(40.0, 120.0), (140.0, 120.0)]
    t = shader.respond([line], 0.5, 270.0, exchange=2, length_setting="medium")          # light from above
    assert t.strokes and all(d[0][1] > 120.0 for d in t.strokes)
    assert all(d[0][1] <= 120.0 + cfg.SHADER_BAND_MM + cfg.DOT_JITTER_MM for d in t.strokes)
    assert t.sees.startswith("A line")


def test_fragments_of_one_square_are_joined_and_shaded_and_the_cap_follows_the_length():
    a = [(50.0, 50.0), (110.0, 50.0), (110.0, 110.0)]
    b = [(108.0, 112.0), (50.0, 110.0), (50.0, 53.0)]                # ends about 3 mm from a's
    t = shader.respond([a, b], 0.5, 0.0, exchange=3, length_setting="short")
    assert t.sees.startswith("A shape") and 1 <= len(t.strokes) <= cfg.SHADER_DOTS_MAX["short"]
    dense = shader.respond([a, b], 1.0, 0.0, exchange=3, length_setting="long")
    assert len(dense.strokes) > len(t.strokes)
    assert shader.respond([a, b], 0.5, 0.0, exchange=3, length_setting="short").strokes == t.strokes
