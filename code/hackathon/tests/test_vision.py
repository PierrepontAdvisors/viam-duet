import cv2
import numpy as np

from duet import config as cfg
from duet import vision


def white_board():
    w, h = vision.BOARD_PX
    return np.full((h, w, 3), 235, dtype=np.uint8)


def mm(x, y):
    return int(x * vision.PX_PER_MM), int(y * vision.PX_PER_MM)


def test_new_ink_finds_only_the_added_line_inside_the_drawable_area():
    prev = white_board()
    cur = prev.copy()
    cv2.line(cur, mm(40, 60), mm(120, 60), (30, 30, 30), 3)          # new, inside
    cv2.line(cur, mm(2, 2), mm(2, 100), (30, 30, 30), 3)             # new, but in the inset margin
    mask, coverage = vision.new_ink(cur, prev)
    ys, xs = np.nonzero(mask)
    assert xs.min() >= mm(40, 0)[0] - 4 and xs.max() <= mm(120, 0)[0] + 4
    assert abs(ys.mean() / vision.PX_PER_MM - 60) < 1.0
    assert 0 < coverage < 0.01


def test_new_ink_ignores_ink_that_was_already_there():
    prev = white_board()
    cv2.line(prev, mm(40, 60), mm(120, 60), (30, 30, 30), 3)
    cur = prev.copy()
    mask, _ = vision.new_ink(cur, prev)
    assert mask.sum() == 0


def test_trace_recovers_a_line_as_one_polyline_in_millimeters():
    prev = white_board()
    cur = prev.copy()
    cv2.line(cur, mm(40, 60), mm(120, 100), (30, 30, 30), 3)
    mask, _ = vision.new_ink(cur, prev)
    polylines = vision.trace(mask)
    assert len(polylines) == 1
    pl = polylines[0]
    ends = sorted([pl[0], pl[-1]])
    assert abs(ends[0][0] - 40) < 2 and abs(ends[0][1] - 60) < 2
    assert abs(ends[1][0] - 120) < 2 and abs(ends[1][1] - 100) < 2
    assert len(pl) <= 4   # a straight line simplifies to very few points


def test_trace_of_empty_mask_is_empty():
    assert vision.trace(np.zeros(vision.BOARD_PX[::-1], dtype=np.uint8)) == []


def test_corner_marks_and_warp_on_a_synthetic_frame():
    frame = np.full((720, 1280, 3), 200, dtype=np.uint8)
    quad = [(300, 150), (700, 160), (720, 620), (280, 610)]          # a slightly rotated board
    for x, y in quad:
        cv2.rectangle(frame, (x - 10, y - 10), (x + 10, y + 10), (20, 20, 20), -1)
    found = vision.find_corner_marks(frame)
    for (fx, fy), (x, y) in zip(found, quad):
        assert abs(fx - x) < 2 and abs(fy - y) < 2
    board = vision.warp_to_board(frame, vision.board_quad(found, 0))
    assert board.shape[:2] == (vision.BOARD_PX[1], vision.BOARD_PX[0])
