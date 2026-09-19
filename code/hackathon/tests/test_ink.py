"""Shared helpers for the artists that work from the visitor's ink: joining traced fragments, finding
closed shapes, and the direction the light comes from."""
import math

from duet import config as cfg
from duet.styles import ink


def circle(cx, cy, r, n=48, start=0.0, end=2 * math.pi):
    return [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in (start + (end - start) * i / n for i in range(n + 1))]


def test_join_fragments_merges_pieces_whose_ends_meet_and_leaves_others_alone():
    half_a = circle(80, 100, 20, n=24, start=0.0, end=math.pi)                          # (100,100) round to (60,100)
    half_b = circle(80, 100, 20, n=24, start=math.pi + 0.2, end=2 * math.pi - 0.1)      # gaps of about 4 and 2 mm
    far = [(20.0, 20.0), (40.0, 20.0)]
    out = ink.join_fragments([half_a, far, half_b])
    assert len(out) == 2
    joined = max(out, key=len)
    assert len(joined) == len(half_a) + len(half_b)
    assert math.dist(joined[0], joined[-1]) < cfg.INK_JOIN_MM        # a ring now
    assert far in out


def test_closed_shapes_returns_rings_with_area_and_skips_lines_and_tiny_loops():
    ring = circle(60, 60, 20, n=32)                                     # about 1250 mm2
    tiny = circle(120, 120, 5, n=16)                                    # about 80 mm2
    line = [(20.0, 200.0), (150.0, 200.0)]
    shapes = ink.closed_shapes([ring, tiny, line])
    assert len(shapes) == 1
    assert all(abs(math.hypot(x - 60, y - 60) - 20) < 0.5 for x, y in shapes[0])


def test_light_vector_points_where_the_light_comes_from():
    assert ink.light_vector(0) == (1.0, 0.0)
    x, y = ink.light_vector(90)
    assert abs(x) < 1e-9 and abs(y - 1) < 1e-9
