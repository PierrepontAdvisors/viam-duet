"""Shader: fills the shapes the visitor just drew with dots, denser away from the light; a line with
no interior gets a band of dots along its shadow side. No Claude call. `energy` sets the spacing, the
light dial sets the gradient, and the exchange number seeds the jitter so a replay draws the same dots.
Its dots keep 4 mm from ink instead of the usual 8 (the session passes CLEARANCE_MM to the planner)."""
from __future__ import annotations

import random

from shapely.geometry import LineString, Polygon

from duet import config as cfg
from duet import open as op
from duet.strokes import Polyline
from duet.styles import abstract
from duet.styles.ink import InkTurn, closed_shapes, exterior, join_fragments, light_vector

FROM_INK = True
COLOR = "green"
CLEARANCE_MM = cfg.SHADER_CLEARANCE_MM
THOUGHTS = ("Where does the light fall?", "A little shadow…")
QUIPS = ("Let me shade that in.", "Darker here, lighter there.", "Dots, dots, dots!")


def spacing_for(energy: float) -> float:
    lo, hi = cfg.SHADER_SPACING_MM
    return lo + (hi - lo) * max(0.0, min(1.0, energy))


def _lit_fraction(p: tuple[float, float], bounds: tuple[float, float, float, float], light: tuple[float, float]) -> float:
    """0 on the shape's shadow edge, 1 on its lit edge, along the light's direction."""
    x0, y0, x1, y1 = bounds
    half = (abs(light[0]) * (x1 - x0) + abs(light[1]) * (y1 - y0)) / 2 or 1.0
    t = ((p[0] - (x0 + x1) / 2) * light[0] + (p[1] - (y0 + y1) / 2) * light[1]) / half
    return (max(-1.0, min(1.0, t)) + 1) / 2


def shade(polygon: Polyline, light: tuple[float, float], spacing: float, max_dots: int, seed: int,
          rng: random.Random) -> list[Polyline]:
    """The polygon stippled, then thinned toward the light."""
    bounds = Polygon(polygon).bounds
    kept: list[Polyline] = []
    for dot in op.stipple(polygon, spacing=spacing, max_dots=max_dots, seed=seed):
        keep = 1.0 - (1.0 - cfg.SHADER_LIT_KEEP) * _lit_fraction(dot[0], bounds, light)
        if rng.random() < keep:
            kept.append(dot)
    return kept


def shadow_band(line: Polyline, light: tuple[float, float], width: float = cfg.SHADER_BAND_MM) -> Polyline:
    """A band beside the line on the side away from the light."""
    ls = LineString(line)
    if ls.length == 0:
        return []
    bands = [ls.buffer(width * side, single_sided=True) for side in (1.0, -1.0)]
    away = min(bands, key=lambda b: b.centroid.x * light[0] + b.centroid.y * light[1])
    return exterior(away)


def respond(new: list[Polyline], energy: float, direction_deg: float, exchange: int, length_setting: str) -> InkTurn:
    light, spacing = light_vector(direction_deg), spacing_for(energy)
    cap = cfg.SHADER_DOTS_MAX[length_setting]
    rng = random.Random(exchange)
    dots: list[Polyline] = []
    shapes = closed_shapes(new)
    if shapes:
        areas = [Polygon(s).area for s in shapes]
        total = sum(areas) or 1.0
        for shape, area in zip(shapes, areas):
            dots += shade(shape, light, spacing, max(1, round(cap * area / total)), exchange, rng)
        sees, adds = "A shape with an inside.", "dots inside it, thicker away from the light"
    else:
        lines = join_fragments(new)
        share = max(1, cap // max(1, len(lines)))
        for line in lines:
            band = shadow_band(line, light)
            if band:
                dots += shade(band, light, spacing, share, exchange, rng)
        sees, adds = "A line with a shadow side.", "a band of dots along its shadow side"
    return InkTurn(dots, COLOR, sees, adds, THOUGHTS[(exchange - 1) % len(THOUGHTS)], QUIPS[(exchange - 1) % len(QUIPS)])


fallback = abstract.fallback
