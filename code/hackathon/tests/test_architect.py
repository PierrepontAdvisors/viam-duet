"""Architect: nearly straight-ruled lines are squared up; curves and diagonals pass untouched."""
import math

from duet.styles import architect


def test_a_polyline_within_15_degrees_of_the_axes_comes_out_orthogonal():
    wall = [(20.0, 20.0), (80.0, 23.0), (82.0, 70.0)]
    (out,), color = architect.style([wall], energy=0.5, direction_deg=0.0)
    assert color == "green" and out[0] == (20.0, 20.0)
    for a, b in zip(out, out[1:]):
        assert abs(a[0] - b[0]) < 1e-9 or abs(a[1] - b[1]) < 1e-9
    assert abs(out[1][0] - 80.0) < 1e-9 and abs(out[2][1] - 67.0) < 1e-9      # runs keep their length along the axis


def test_diagonals_and_arcs_pass_untouched():
    diagonal = [(20.0, 20.0), (80.0, 80.0)]
    arc = [(88 + 30 * math.cos(t), 120 + 30 * math.sin(t)) for t in (math.pi * i / 24 for i in range(25))]
    out, _ = architect.style([diagonal, arc])
    assert out == [diagonal, [(float(x), float(y)) for x, y in arc]]


def test_fallback_is_the_calm_arc():
    out, color = architect.fallback([[(30.0, 30.0), (80.0, 30.0)]])
    assert color == "green" and len(out) == 1 and len(out[0]) == 25
