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
