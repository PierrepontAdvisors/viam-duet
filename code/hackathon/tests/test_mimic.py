"""Mimic: a copy of the visitor's new strokes lands beside them, sized by energy, varied by exchange."""
from shapely.geometry import LineString

from duet import config as cfg
from duet.styles import mimic

SQUARE = [(60.0, 100.0), (90.0, 100.0), (90.0, 130.0), (60.0, 130.0), (60.0, 100.0)]   # 30 mm, centre (75,115)
TAIL = [(75.0, 130.0), (75.0, 140.0)]


def bbox(pls):
    xs = [x for pl in pls for x, _ in pl]
    ys = [y for pl in pls for _, y in pl]
    return min(xs), min(ys), max(xs), max(ys)


def test_the_copy_sits_beside_the_original_clear_of_it_and_inside_the_inset():
    t = mimic.respond([SQUARE], energy=0.5, direction_deg=0.0, exchange=1, length_setting="medium")
    assert t.color == "green" and len(t.strokes) == 1
    assert LineString(t.strokes[0]).distance(LineString(SQUARE)) >= cfg.CLEARANCE_MM
    x0, y0, x1, y1 = bbox(t.strokes)
    assert x0 >= cfg.INSET_MM and x1 <= cfg.BOARD_W_MM - cfg.INSET_MM
    assert y0 >= cfg.INSET_MM and y1 <= cfg.BOARD_H_MM - cfg.INSET_MM
    assert x0 > 90.0                                       # the dial at 0 degrees sends it to the right
    assert abs((x1 - x0) - 36.0) < 0.01                    # energy 0.5 scales by 1.2


def test_energy_one_makes_the_copy_1_6_times_the_size():
    t = mimic.respond([SQUARE], energy=1.0, direction_deg=90.0, exchange=1, length_setting="long")
    x0, y0, x1, y1 = bbox(t.strokes)
    assert abs((x1 - x0) - 48.0) < 0.01 and abs((y1 - y0) - 48.0) < 0.01
    assert y0 > 130.0                                      # 90 degrees sends it below


def test_exchange_two_mirrors_and_exchange_three_turns_the_copy():
    flag = [(60.0, 100.0), (100.0, 100.0), (60.0, 120.0), (60.0, 100.0)]   # a right-pointing triangle, 40 by 20
    shifted = mimic.respond([flag], 0.0, 90.0, exchange=1, length_setting="long").strokes[0]
    mirrored = mimic.respond([flag], 0.0, 90.0, exchange=2, length_setting="long").strokes[0]
    turned = mimic.respond([flag], 0.0, 90.0, exchange=3, length_setting="long").strokes[0]
    assert shifted[1][0] == max(p[0] for p in shifted)    # the tip still points right
    assert mirrored[1][0] == min(p[0] for p in mirrored)  # the tip points left
    x0, y0, x1, y1 = bbox([turned])
    assert abs((x1 - x0) - 16.0) < 0.01 and abs((y1 - y0) - 32.0) < 0.01     # width and height swap (scale 0.8)


def test_a_mark_by_the_right_edge_sends_the_copy_left():
    right = [(130.0, 100.0), (155.0, 100.0), (155.0, 125.0), (130.0, 125.0), (130.0, 100.0)]
    t = mimic.respond([right], 0.5, 0.0, exchange=1, length_setting="long")
    x0, _, x1, _ = bbox(t.strokes)
    assert x1 < 130.0 and x0 >= cfg.INSET_MM


def test_strokes_come_longest_first_and_the_words_cycle():
    t1 = mimic.respond([TAIL, SQUARE], 0.5, 180.0, exchange=1, length_setting="long")
    assert len(t1.strokes) == 2 and len(t1.strokes[0]) == 5 and len(t1.strokes[1]) == 2
    t2 = mimic.respond([SQUARE], 0.5, 180.0, exchange=2, length_setting="long")
    assert t1.quip != t2.quip and t1.thought != t2.thought
    assert t1.adds.endswith("shifted") and t2.adds.endswith("mirrored")
    assert mimic.respond([], 0.5, 0.0, exchange=1, length_setting="short").strokes == []
    assert mimic.FROM_INK is True
