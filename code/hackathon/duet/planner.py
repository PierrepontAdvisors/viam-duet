"""Turn a Claude proposal into safe polylines: convert shapes, clip to the drawable area, keep clear
of existing ink unless the stroke is attached to it, then cut to the budget. Pure."""
from __future__ import annotations

import math

from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

from duet import config as cfg
from duet.strokes import Polyline, cut_to_budget, length

MIN_PIECE_MM = 2.0


def drawable_area() -> Polygon:
    i = cfg.INSET_MM
    return box(i, i, cfg.BOARD_W_MM - i, cfg.BOARD_H_MM - i)


def circle_polyline(cx: float, cy: float, r: float) -> Polyline:
    n = max(12, int(2 * math.pi * r / 4))
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]


def arc_polyline(cx: float, cy: float, r: float, start_deg: float, end_deg: float) -> Polyline:
    sweep = end_deg - start_deg
    n = max(4, int(abs(sweep) / 360 * max(12, 2 * math.pi * r / 4)))
    return [(cx + r * math.cos(math.radians(start_deg + sweep * k / n)),
             cy + r * math.sin(math.radians(start_deg + sweep * k / n))) for k in range(n + 1)]


def _lines(geom) -> list[Polyline]:
    if geom.is_empty:
        return []
    if geom.geom_type == "LineString":
        return [[(float(x), float(y)) for x, y in geom.coords]] if len(geom.coords) >= 2 else []
    if hasattr(geom, "geoms"):
        out: list[Polyline] = []
        for g in geom.geoms:
            out.extend(_lines(g))
        return out
    return []


def clip_to(polyline: Polyline, area: Polygon) -> list[Polyline]:
    if len(polyline) < 2:
        return []
    return _lines(LineString(polyline).intersection(area))


def keep_clear(polylines: list[Polyline], existing_ink: list[Polyline], clearance_mm: float) -> list[Polyline]:
    """Cut away the parts of strokes that come within `clearance_mm` of existing ink."""
    ink = [LineString(pl) for pl in existing_ink if len(pl) >= 2]
    if not ink:
        return polylines
    buffer = unary_union([line.buffer(clearance_mm) for line in ink])
    out: list[Polyline] = []
    for pl in polylines:
        if len(pl) >= 2:
            out.extend(_lines(LineString(pl).difference(buffer)))
    return out


def stroke_to_polyline(stroke: dict) -> Polyline:
    kind = stroke.get("kind", "polyline")
    if kind == "circle":
        return circle_polyline(stroke["cx"], stroke["cy"], stroke["r"])
    if kind == "arc":
        return arc_polyline(stroke["cx"], stroke["cy"], stroke["r"], stroke["start_deg"], stroke["end_deg"])
    return [(float(p["x"]), float(p["y"])) for p in stroke.get("points", [])]


def validate(strokes: list[dict], existing_ink: list[Polyline], budget_mm: float,
             clearance_mm: float = 3.0) -> list[Polyline]:
    """Proposal strokes (dicts with kind, points or cx/cy/r, attached) to safe polylines, in order."""
    area = drawable_area()
    result: list[Polyline] = []
    for s in strokes:
        parts = clip_to(stroke_to_polyline(s), area)
        if not s.get("attached", False):
            parts = keep_clear(parts, existing_ink, clearance_mm)
        result.extend(p for p in parts if length(p) >= MIN_PIECE_MM)
    return cut_to_budget(result, budget_mm)
