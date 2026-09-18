import math

from duet.strokes import cut_to_budget, length, resample


def test_length_of_closed_square():
    square = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
    assert length(square) == 40


def test_length_of_single_point_is_zero():
    assert length([(3, 3)]) == 0


def test_resample_keeps_endpoints_and_respects_spacing():
    pts = resample([(0, 0), (30, 0)], 8)
    assert pts[0] == (0, 0)
    assert pts[-1] == (30, 0)
    assert len(pts) == 5  # 0, 7.5, 15, 22.5, 30
    assert all(math.dist(a, b) <= 8 + 1e-9 for a, b in zip(pts, pts[1:]))


def test_resample_keeps_every_original_vertex():
    pts = resample([(0, 0), (10, 0), (10, 10)], 4)
    assert (10, 0) in pts
    assert (10, 10) in pts


def test_cut_to_budget_keeps_whole_strokes_then_cuts_one():
    strokes = [[(0, 0), (10, 0)], [(0, 0), (0, 10)], [(0, 0), (50, 0)]]
    out = cut_to_budget(strokes, 25)
    assert out[:2] == strokes[:2]
    assert out[2] == [(0, 0), (5.0, 0.0)]
    assert len(out) == 3


def test_cut_to_budget_with_nothing_left():
    assert cut_to_budget([[(0, 0), (1, 0)]], 0) == []
