from duet import config as cfg
from duet import planner
from duet.styles import haring
from duet.strokes import length
from duet import svg


def test_validate_clips_to_the_drawable_area():
    out = planner.validate([{"kind": "polyline", "points": [{"x": 0, "y": 50}, {"x": 100, "y": 50}]}], [], 1000)
    assert len(out) == 1
    assert min(x for x, _ in out[0]) >= cfg.INSET_MM - 1e-6


def test_validate_keeps_unattached_strokes_clear_of_ink():
    ink = [[(60, 20), (60, 120)]]
    out = planner.validate([{"kind": "polyline", "points": [{"x": 30, "y": 70}, {"x": 90, "y": 70}]}], ink, 1000)
    assert len(out) == 2                      # cut into two pieces around the ink
    for pl in out:
        assert all(abs(x - 60) >= cfg.CLEARANCE_MM - 1e-6 for x, _ in pl)


def test_validate_ignores_the_attached_flag_and_still_keeps_clear():
    ink = [[(60, 20), (60, 120)]]
    out = planner.validate([{"kind": "polyline", "attached": True,
                             "points": [{"x": 30, "y": 70}, {"x": 90, "y": 70}]}], ink, 1000)
    assert len(out) == 2
    for pl in out:
        assert all(abs(x - 60) >= cfg.CLEARANCE_MM - 1e-6 for x, _ in pl)


def test_finalize_keeps_styled_passes_and_ticks_off_the_ink():
    from shapely.geometry import LineString
    ink = [[(80, 40), (80, 160)]]                       # a vertical human stroke
    styled, _ = haring.style([[(30, 100), (74, 100)]], energy=1.0)   # ends 6 mm from it, ticks radiate
    final = planner.finalize(styled, ink, 10_000)
    ink_line = LineString(ink[0])
    assert final, "something must survive"
    for pl in final:
        assert LineString(pl).distance(ink_line) >= cfg.CLEARANCE_MM - 1e-6


def test_finalize_clips_styled_strokes_to_the_drawable_area():
    # hugs the top inset edge, drawn right to left, so the ticks radiate off the board
    styled = haring.style([[(150.0, 15.0), (20.0, 15.0)]], energy=1.0)[0]
    assert min(y for pl in styled for _, y in pl) < cfg.INSET_MM, "the styled input must escape, or this proves nothing"
    final = planner.finalize(styled, [], 10_000)
    assert final, "something must survive"
    for pl in final:
        for x, y in pl:
            assert cfg.INSET_MM - 1e-6 <= x <= cfg.BOARD_W_MM - cfg.INSET_MM + 1e-6
            assert cfg.INSET_MM - 1e-6 <= y <= cfg.BOARD_H_MM - cfg.INSET_MM + 1e-6


def test_validate_converts_circles_and_respects_budget():
    out = planner.validate([{"kind": "circle", "cx": 88, "cy": 120, "r": 20}], [], 50)
    assert 1 <= len(out) <= 2
    assert sum(length(pl) for pl in out) <= 50 + 1e-6


def test_haring_bolds_and_ticks():
    strokes = [[(30, 100), (130, 100)]]
    out, color = haring.style(strokes, energy=1.0)
    assert color == "green"
    assert out[0] == strokes[0]
    passes = len(haring.PASS_OFFSETS_MM)
    assert all(len(p) >= 2 for p in out[1:1 + passes])   # the extra passes
    tick_count = len(out) - 1 - passes
    assert tick_count == int(99.9 // haring.TICK_SPACING_MM)   # 100 mm line, one tick per spacing
    assert all(abs(length(t) - (haring.TICK_BASE_MM + haring.TICK_EXTRA_MM)) < 1e-6 for t in out[1 + passes:])


def test_haring_fallback_outlines_the_human_mark():
    out, _ = haring.fallback([[(50, 50), (120, 50)]])
    assert len(out) >= 2
    assert any(abs(pl[0][1] - 56) < 1e-6 for pl in out) and any(abs(pl[0][1] - 44) < 1e-6 for pl in out)


def test_svg_renders_paths():
    text = svg.render([[(10, 10), (20, 20)]], [[(30, 30), (40, 40)]], [[(50, 50), (60, 60)]])
    assert text.count("<path") == 3 and 'stroke-dasharray' in text


def test_finalize_thins_the_haring_passes_to_one_line_and_caps_by_length():
    from duet import config as cfg
    line = [(30.0, 60.0), (120.0, 60.0)]
    styled, _ = haring.style([line])                    # the stroke, two passes beside it, and ticks
    out = planner.finalize(styled, [], 4000, length_setting="long")
    long_lines = [p for p in out if planner.length(p) > 40]
    assert len(long_lines) == 1                         # one pass survives; the ticks are short and spaced
    short = planner.finalize(styled, [], 4000, length_setting="short")
    assert len([p for p in short if planner.length(p) >= cfg.DOT_EXEMPT_MM]) <= cfg.STROKE_CAP["short"]


def test_validate_enlarges_small_shapes_and_stipples_dots():
    from duet import config as cfg
    small = {"kind": "circle", "cx": 88.0, "cy": 120.0, "r": 10.0}
    out = planner.validate([small], [], 4000)
    xs = [x for pl in out for x, _ in pl]
    assert max(xs) - min(xs) > 38                       # a 20 mm circle grew to about 40
    dots = {"kind": "dots", "points": [{"x": 40, "y": 40}, {"x": 80, "y": 40}, {"x": 80, "y": 80}, {"x": 40, "y": 80}]}
    ink = [[(40.0, 40.0), (80.0, 40.0)]]                # a mark along the polygon's top edge
    out = planner.validate([dots], ink, 4000)
    assert 8 <= len(out) <= 25 and all(abs(planner.length(d) - cfg.DOT_MM) < 1e-6 for d in out)
    assert all(d[0][1] > 40 + cfg.CLEARANCE_MM - 1 for d in out)        # none within clearance of the ink
    final = planner.finalize(out, ink, 4000, length_setting="short")
    assert len(final) == len(out)                       # dots are not counted by the cap and are not crumbs
