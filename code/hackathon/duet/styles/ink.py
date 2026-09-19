"""Shared ground for the artists that work from the visitor's ink instead of a Claude proposal: the
turn's strokes and words as one record, joining traced fragments, finding closed shapes, and the
direction the light comes from. Pure functions on polylines in board millimeters."""
from __future__ import annotations

import math
from dataclasses import dataclass

from shapely.geometry import MultiPolygon, Polygon

from duet import config as cfg
from duet.strokes import Polyline


@dataclass(frozen=True)
class InkTurn:
    strokes: list[Polyline]
    color: str
    sees: str
    adds: str
    thought: str
    quip: str


def _joined(a: Polyline, b: Polyline, gap_mm: float) -> Polyline | None:
    """a then b, either reversed as needed, when an end of a lies within gap_mm of an end of b."""
    for aa in (a, a[::-1]):
        for bb in (b, b[::-1]):
            if math.dist(aa[-1], bb[0]) <= gap_mm:
                return aa + bb
    return None


def join_fragments(polylines: list[Polyline], gap_mm: float = cfg.INK_JOIN_MM) -> list[Polyline]:
    """Traced strokes come in pieces; pieces whose ends lie within gap_mm of each other become one."""
    chains = [[(float(x), float(y)) for x, y in pl] for pl in polylines if len(pl) >= 2]
    merged = True
    while merged and len(chains) > 1:
        merged = False
        for i in range(len(chains)):
            for j in range(i + 1, len(chains)):
                joined = _joined(chains[i], chains[j], gap_mm)
                if joined is not None:
                    chains = [c for k, c in enumerate(chains) if k not in (i, j)] + [joined]
                    merged = True
                    break
            if merged:
                break
    return chains


def exterior(geom) -> Polyline:
    """The outline of a polygon, or of the largest part of a multipolygon; [] for anything else."""
    if geom.is_empty:
        return []
    if isinstance(geom, MultiPolygon):
        geom = max(geom.geoms, key=lambda g: g.area)
    if not isinstance(geom, Polygon):
        return []
    return [(float(x), float(y)) for x, y in geom.exterior.coords]


def closed_shapes(polylines: list[Polyline], min_area_mm2: float = cfg.SHADER_MIN_AREA_MM2,
                  gap_mm: float = cfg.INK_JOIN_MM) -> list[Polyline]:
    """After joining: the outlines of the strokes that close on themselves (ends within gap_mm) and
    enclose at least min_area_mm2."""
    out: list[Polyline] = []
    for pl in join_fragments(polylines, gap_mm):
        if len(pl) < 3 or math.dist(pl[0], pl[-1]) > gap_mm:
            continue
        poly = Polygon(pl)
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_empty or poly.area < min_area_mm2:
            continue
        ring = exterior(poly)
        if ring:
            out.append(ring)
    return out


def light_vector(direction_deg: float) -> tuple[float, float]:
    """Unit vector pointing where the light comes from, in board mm with y down; the same angle
    convention as the Haring ticks."""
    a = math.radians(direction_deg)
    return (math.cos(a), math.sin(a))
