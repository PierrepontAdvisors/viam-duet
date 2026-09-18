"""Keith Haring grammar: every stroke drawn bold as two passes, with short motion ticks radiating
from it. Pure functions on polylines in board millimeters."""
from __future__ import annotations

import math

from shapely.geometry import LineString

from duet.strokes import Polyline

COLOR = "green"
SECOND_PASS_MM = 1.5
TICK_SPACING_MM = 25.0
TICK_GAP_MM = 3.0
TICK_BASE_MM = 8.0
TICK_EXTRA_MM = 7.0


def offset_polyline(pl: Polyline, d_mm: float) -> Polyline:
    if len(pl) < 2:
        return []
    geom = LineString(pl).offset_curve(d_mm)
    if geom.is_empty:
        return []
    if geom.geom_type != "LineString":
        geom = max(geom.geoms, key=lambda g: g.length)
    return [(float(x), float(y)) for x, y in geom.coords]


def ticks(pl: Polyline, energy: float = 0.5, direction_deg: float = 0.0) -> list[Polyline]:
    """Short strokes leaving the line every TICK_SPACING_MM, on its left side, tilted by `direction`."""
    if len(pl) < 2:
        return []
    line = LineString(pl)
    total = line.length
    tick_len = TICK_BASE_MM + TICK_EXTRA_MM * max(0.0, min(1.0, energy))
    ang = math.radians(direction_deg)
    out: list[Polyline] = []
    k = 1
    while k * TICK_SPACING_MM < total:
        s = k * TICK_SPACING_MM
        p, q = line.interpolate(s), line.interpolate(min(s + 1.0, total))
        tx, ty = q.x - p.x, q.y - p.y
        norm = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / norm, tx / norm
        dx, dy = nx * math.cos(ang) - ny * math.sin(ang), nx * math.sin(ang) + ny * math.cos(ang)
        out.append([(p.x + dx * TICK_GAP_MM, p.y + dy * TICK_GAP_MM),
                    (p.x + dx * (TICK_GAP_MM + tick_len), p.y + dy * (TICK_GAP_MM + tick_len))])
        k += 1
    return out


def style(strokes: list[Polyline], energy: float = 0.5, direction_deg: float = 0.0) -> tuple[list[Polyline], str]:
    """Bold every validated stroke and add ticks. Returns polylines and the marker color."""
    out: list[Polyline] = []
    for pl in strokes:
        if len(pl) < 2:
            continue
        out.append(pl)
        second = offset_polyline(pl, SECOND_PASS_MM)
        if len(second) >= 2:
            out.append(second)
        out.extend(ticks(pl, energy, direction_deg))
    return out, COLOR


def fallback(human_ink: list[Polyline]) -> tuple[list[Polyline], str]:
    """When Claude is unavailable: an offset outline on both sides of the new mark, plus ticks."""
    out: list[Polyline] = []
    for pl in human_ink:
        for d in (6.0, -6.0):
            off = offset_polyline(pl, d)
            if len(off) >= 2:
                out.append(off)
        out.extend(ticks(pl))
    return out, COLOR
