"""Vincent van Gogh's grammar: short curved dashes laid along a flow that streams around the
stroke. `energy` sets dash length and density; `direction` bends the current. Line art only.
Same signature as `styles.haring`."""
from __future__ import annotations

import math

from shapely.geometry import LineString

from duet.strokes import Polyline

COLOR = "green"
DASH_MIN_MM = 8.0
DASH_MAX_MM = 18.0
ROWS = (4.0, 9.0, 14.0)         # offsets of the dash rows on each side of the stroke, mm
CURL = 0.35                     # radians of bend along each dash


def _dash(p: tuple[float, float], angle: float, size: float) -> Polyline:
    """A gently curved dash centered on p, heading `angle`."""
    pts: Polyline = []
    for k in range(5):
        t = k / 4 - 0.5
        a = angle + CURL * t
        pts.append((p[0] + math.cos(a) * size * t, p[1] + math.sin(a) * size * t))
    return pts


def style(strokes: list[Polyline], energy: float = 0.5, direction_deg: float = 0.0) -> tuple[list[Polyline], str]:
    e = max(0.0, min(1.0, energy))
    size = DASH_MIN_MM + (DASH_MAX_MM - DASH_MIN_MM) * e
    spacing = size * (1.6 - 0.6 * e)
    bend = math.radians(direction_deg)
    out: list[Polyline] = []
    for pl in strokes:
        if len(pl) < 2:
            continue
        line = LineString(pl)
        for side in (1.0, -1.0):
            for row, offset in enumerate(ROWS):
                curve = line.offset_curve(side * offset)
                if curve.is_empty:
                    continue
                if curve.geom_type != "LineString":
                    curve = max(curve.geoms, key=lambda g: g.length)
                s = spacing / 2 + row * spacing / 3
                while s < curve.length:
                    p, q = curve.interpolate(s), curve.interpolate(min(s + 1.0, curve.length))
                    angle = math.atan2(q.y - p.y, q.x - p.x) + bend * 0.5 + side * CURL * (row + 1) / 3
                    out.append(_dash((p.x, p.y), angle, size))
                    s += spacing
    return out, COLOR


def fallback(human_ink: list[Polyline]) -> tuple[list[Polyline], str]:
    """The current streams around the mark: the same dashes at half energy."""
    return style(human_ink, energy=0.5)
