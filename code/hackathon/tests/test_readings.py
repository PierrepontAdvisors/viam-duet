import math

import cv2
import numpy as np

from duet import config as cfg
from duet import vision


def quad_in(frame, calibration):
    return vision.find_corner_marks(frame, expected=calibration["marks_image"])


def homography_for(quad, calibration):
    return vision.board_homography(vision.board_quad(quad, calibration["board_tl_index"]))


def test_real_exchange_diffs_to_the_visitors_strokes(exchange_start, exchange_human):
    mask, coverage = vision.new_ink(exchange_human, exchange_start)
    polylines = vision.trace(mask)
    assert 10 <= len(polylines) <= 16 and 0.015 < coverage < 0.03
    xs = [x for pl in polylines for x, _ in pl]
    ys = [y for pl in polylines for _, y in pl]
    assert 30 <= min(xs) <= 40 and 130 <= max(xs) <= 140
    assert 78 <= min(ys) <= 88 and 180 <= max(ys) <= 190
    assert int(vision.new_ink(exchange_start, exchange_human)[0].sum()) == 0   # nothing got darker the other way


def test_mm_per_px_at_the_look_pose_is_about_half_a_millimeter(look_frame, calibration):
    quad = quad_in(look_frame, calibration)
    assert 0.45 <= vision.mm_per_px(quad) <= 0.56


def test_to_board_mm_maps_the_marks_to_the_board_corners(look_frame, calibration):
    quad = quad_in(look_frame, calibration)
    board = vision.board_quad(quad, calibration["board_tl_index"])
    pts = vision.to_board_mm(homography_for(quad, calibration), [tuple(p) for p in board])
    expected = [(0, 0), (cfg.BOARD_W_MM, 0), (cfg.BOARD_W_MM, cfg.BOARD_H_MM), (0, cfg.BOARD_H_MM)]
    assert all(abs(a - b) < 0.01 for p, ref in zip(pts, expected) for a, b in zip(p, ref))


def test_plane_fit_on_a_synthetic_tilted_plane():
    h, w = 120, 160
    ys, xs = np.mgrid[0:h, 0:w]
    depth = (600 + 0.5 * xs - 0.25 * ys).astype(np.uint16)
    depth[5:10, 5:10] = 0                       # holes are ignored
    depth[50:60, 50:60] = 3000                   # glare on the board reflects the ceiling: far readings must not skew the fit
    a, b, c = vision.fit_plane(depth, np.ones((h, w), np.uint8))
    assert abs(a - 0.5) < 0.02 and abs(b + 0.25) < 0.02 and abs(c - 600) < 2


def test_reference_depth_lowers_the_expected_surface_inside_the_dock():
    dock = [[10, 10], [30, 10], [30, 30], [10, 30]]
    ref = vision.reference_depth((40, 40), (0.0, 0.0, 700.0), [(dock, 30.0)])
    assert ref[5, 5] == 700 and ref[20, 20] == 670


def test_hand_present_depth_on_synthetic_frames():
    h, w = 120, 160
    expected = vision.plane_depth((h, w), (0.0, 0.0, 700.0))
    depth = np.full((h, w), 700, np.uint16)
    region = np.ones((h, w), np.uint8)
    assert vision.hand_present_depth(depth, region, expected, mm2_per_px=1.0) is False
    depth[40:80, 40:100] = 640                   # 60 mm above the plane, 2400 px = 2400 mm²
    assert vision.hand_present_depth(depth, region, expected, mm2_per_px=1.0) is True
    assert vision.hand_present_depth(depth, region, expected, mm2_per_px=0.5) is False   # too small at half the scale
    depth[:] = 700
    depth[40:80, 40:100] = 690                   # only 10 mm up: a sheet of paper, not a hand
    assert vision.hand_present_depth(depth, region, expected, mm2_per_px=1.0) is False


def test_hand_present_color_on_the_real_look_frame(look_frame, calibration):
    quad = quad_in(look_frame, calibration)
    region = vision.polygon_mask(look_frame.shape, [quad.tolist()])
    mm2 = vision.mm_per_px(quad) ** 2
    cx, cy = int(quad[:, 0].mean()), int(quad[:, 1].mean())
    assert vision.hand_present_color(look_frame, look_frame, region, mm2) is False
    inked = look_frame.copy()                                       # a visitor's marker lines: thin, must not count
    for k in range(6):
        cv2.line(inked, (cx - 100, cy - 60 + 20 * k), (cx + 100, cy - 40 + 20 * k), (30, 30, 170), 3)
    assert vision.hand_present_color(inked, look_frame, region, mm2) is False
    hand = inked.copy()                                             # a hand: about 65 x 45 mm of skin over the board
    cv2.ellipse(hand, (cx, cy), (65, 45), 20, 0, 360, (150, 180, 230), -1)
    assert vision.hand_present_color(hand, look_frame, region, mm2) is True
    fingertip = look_frame.copy()                                   # a 9 mm dot: too small
    cv2.circle(fingertip, (cx, cy), 9, (90, 120, 170), -1)
    assert vision.hand_present_color(fingertip, look_frame, region, mm2) is False


def green_frame(cx, cy, r=6):
    f = np.full((200, 300, 3), 235, np.uint8)
    cv2.circle(f, (cx, cy), r, (60, 170, 60), -1)   # a green end plug
    return f


def test_dock_dots_home_moved_missing(look_frame, calibration):
    h = homography_for(quad_in(look_frame, calibration), calibration)
    slots = {"green": {"xy": [150, 100], "hsv_lo": [40, 60, 60], "hsv_hi": [85, 255, 255]}}
    home = vision.dock_dots(green_frame(150, 100), slots, h)["green"]
    assert home.status == "home" and math.hypot(*home.displacement_mm) < 1.0
    moved = vision.dock_dots(green_frame(150 + 16, 100), slots, h)["green"]     # 16 px is about 8 mm here
    assert moved.status == "moved" and 4 < math.hypot(*moved.displacement_mm) < 14
    missing = vision.dock_dots(np.full((200, 300, 3), 235, np.uint8), slots, h)["green"]
    assert missing.status == "missing"


def test_still_needs_two_frames_and_a_quiet_scene():
    a = np.full((90, 160, 3), 128, np.uint8)
    b = a.copy()
    b[20:40, 20:60] = 200
    assert vision.still([a]) is False
    assert vision.still([a, a.copy(), a.copy()]) is True
    assert vision.still([a, b]) is False
