"""Architect: plan and elevation drafting. Claude proposes walls, doorways, stairs, and rooflines; this
styler squares up any polyline that runs close to the axes everywhere, and leaves arcs and diagonals
as they are. `energy` and `direction` are accepted and ignored, as in Abstract."""
from __future__ import annotations

import math

from shapely.geometry import LineString

from duet import config as cfg
from duet.strokes import Polyline
from duet.styles import abstract

COLOR = "green"
SIMPLIFY_MM = 2.0


def _off_axis_deg(a: tuple[float, float], b: tuple[float, float]) -> float:
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 90.0
    return min(ang, 90.0 - ang)


def square_up(pl: Polyline, snap_deg: float = cfg.ARCH_SNAP_DEG) -> Polyline:
    """Straight runs within snap_deg of horizontal or vertical become exactly so, each keeping its
    length along its axis; a polyline with any steeper segment is returned unchanged."""
    pts = [(float(x), float(y)) for x, y in pl]
    if len(pts) < 2:
        return pts
    simple = [(float(x), float(y)) for x, y in LineString(pts).simplify(SIMPLIFY_MM).coords]
    segs = [(a, b) for a, b in zip(simple, simple[1:]) if a != b]
    if not segs or any(_off_axis_deg(a, b) > snap_deg for a, b in segs):
        return pts
    out: Polyline = [simple[0]]
    for a, b in segs:
        dx, dy = b[0] - a[0], b[1] - a[1]
        px, py = out[-1]
        out.append((px + dx, py) if abs(dx) >= abs(dy) else (px, py + dy))
    return out


def style(strokes: list[Polyline], energy: float = 0.5, direction_deg: float = 0.0) -> tuple[list[Polyline], str]:
    return [square_up(pl) for pl in strokes if len(pl) >= 2], COLOR


fallback = abstract.fallback
