import math

from duet.strokes import length
from duet.styles import haring, mondrian, vangogh

LINE = [[(40.0, 60.0), (120.0, 100.0)]]


def test_every_styler_has_the_same_signature_and_returns_polylines_and_a_color():
    for mod in (haring, mondrian, vangogh):
        out, color = mod.style(LINE, energy=0.5, direction_deg=0.0)
        assert color == "green" and out and all(len(pl) >= 2 for pl in out)
        fb, color = mod.fallback(LINE)
        assert color == "green" and fb and all(len(pl) >= 2 for pl in fb)


def test_mondrian_snaps_to_horizontal_and_vertical_lines():
    out, _ = mondrian.style(LINE, energy=0.5)
    for pl in out:
        for a, b in zip(pl, pl[1:]):
            assert abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6      # every segment is axis-aligned
    assert len(mondrian.style(LINE, energy=1.0)[0]) > len(mondrian.style(LINE, energy=0.0)[0])


def test_vangogh_draws_short_curved_dashes_along_the_flow():
    out, _ = vangogh.style(LINE, energy=0.5, direction_deg=0.0)
    assert len(out) >= 6
    assert all(5.0 <= length(pl) <= 30.0 for pl in out)                    # dashes, not long lines
    tilted, _ = vangogh.style(LINE, energy=0.5, direction_deg=90.0)
    a, b = out[0], tilted[0]
    da = math.atan2(a[-1][1] - a[0][1], a[-1][0] - a[0][0])
    db = math.atan2(b[-1][1] - b[0][1], b[-1][0] - b[0][0])
    assert abs((da - db + math.pi) % (2 * math.pi) - math.pi) > 0.5        # direction bends the current
