"""Open strokes: every plan large, single-lined, and free of overlap, whatever the artist."""
import math

from shapely.geometry import LineString, Point, Polygon

from duet import config as cfg
from duet import open as op
from duet.strokes import length


def circle(cx, cy, r, n=48, turns=1.0):
    return [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in (i * 2 * math.pi * turns / n for i in range(n + 1))]


def span(pl):
    xs, ys = [p[0] for p in pl], [p[1] for p in pl]
    return max(max(xs) - min(xs), max(ys) - min(ys))


def test_enlarge_scales_small_shapes_to_the_target_about_their_center():
    small = circle(80, 100, 12)                       # 24 mm across
    (out,) = op.enlarge([small])
    assert abs(span(out) - cfg.TARGET_SHAPE_MM) < 0.5
    cx = sum(p[0] for p in out) / len(out); cy = sum(p[1] for p in out) / len(out)
    assert abs(cx - 80) < 0.5 and abs(cy - 100) < 0.5


def test_enlarge_leaves_big_shapes_and_dots_alone():
    big = circle(80, 100, 25)                         # 50 mm across
    dot = [(10.0, 10.0), (11.5, 10.0)]
    assert op.enlarge([big, dot]) == [big, dot]


def test_uncross_cuts_a_spiral_after_its_first_turn():
    spiral = [(88 + (5 + 8 * t / (4 * math.pi)) * math.cos(t), 120 + (5 + 8 * t / (4 * math.pi)) * math.sin(t))
              for t in (i * 4 * math.pi / 120 for i in range(121))]        # two turns, radius 5 -> 13 mm, 4 mm between turns
    out = op.uncross(spiral)
    assert 0.3 * length(spiral) < length(out) < 0.75 * length(spiral)
    line = LineString(out)
    assert line.is_simple


def test_uncross_keeps_a_closing_circle_and_a_straight_line():
    ring = circle(88, 120, 15)
    out = op.uncross(ring)
    assert abs(length(out) - length(ring)) < 3.0
    assert Point(out[-1]).distance(Point(out[0])) < cfg.SELF_GAP_MM
    straight = [(20.0, 20.0), (120.0, 20.0)]
    out = op.uncross(straight)
    assert out[0] == (20.0, 20.0) and abs(out[-1][0] - 120.0) < 0.01 and abs(length(out) - 100.0) < 0.01


def test_uncross_drops_the_second_tooth_of_a_tight_zigzag():
    zig = [(20.0, 100.0), (60.0, 100.0), (20.0, 103.0), (60.0, 106.0), (20.0, 109.0)]   # teeth 3 mm apart
    out = op.uncross(zig)
    assert length(out) < 90.0                          # the first stroke and part of the return, no more


def test_thin_drops_parallels_but_keeps_crossings():
    a = [(20.0, 50.0), (60.0, 50.0)]
    parallel = [(20.0, 53.0), (60.0, 53.0)]
    crossing = [(40.0, 30.0), (40.0, 70.0)]
    assert op.thin([a, parallel, crossing]) == [a, crossing]


def test_thin_reduces_a_haring_triple_pass_to_one():
    base = [(30.0, 30.0), (80.0, 30.0)]
    passes = [base, [(30.0, 31.5), (80.0, 31.5)], [(30.0, 33.0), (80.0, 33.0)]]
    assert op.thin(passes) == [base]


def test_cap_keeps_the_first_strokes_and_never_counts_dots():
    strokes = [[(0.0, float(i)), (40.0, float(i))] for i in range(6)]
    dots = [[(5.0, 5.0), (6.5, 5.0)], [(15.0, 5.0), (16.5, 5.0)]]
    out = op.cap(dots + strokes, "short")
    assert out == dots + strokes[:2]
    assert len(op.cap(strokes, "long")) == 5


def test_stipple_fills_a_square_with_sparse_dots_inside_it_repeatably():
    square = [(40.0, 40.0), (80.0, 40.0), (80.0, 80.0), (40.0, 80.0)]
    dots = op.stipple(square, seed=7)
    assert 12 <= len(dots) <= 25
    poly = Polygon(square).buffer(cfg.DOT_JITTER_MM + 0.1)
    assert all(poly.contains(Point(d[0])) for d in dots)
    assert all(abs(length(d) - cfg.DOT_MM) < 1e-9 for d in dots)
    centers = [d[0] for d in dots]
    assert min(math.dist(p, q) for i, p in enumerate(centers) for q in centers[i + 1:]) >= 5.9
    assert dots == op.stipple(square, seed=7)


def test_stipple_widens_the_grid_to_respect_the_dot_cap():
    board = [(0.0, 0.0), (176.0, 0.0), (176.0, 240.0), (0.0, 240.0)]
    dots = op.stipple(board, seed=1)
    assert 30 <= len(dots) <= cfg.DOTS_MAX


def test_is_dot_recognizes_stipple_dots_only():
    assert op.is_dot([(5.0, 5.0), (6.5, 5.0)])
    assert not op.is_dot([(5.0, 5.0), (6.0, 5.0)])           # a clipped leftover
    assert not op.is_dot([(5.0, 5.0), (6.5, 5.0), (7.0, 5.0)])
