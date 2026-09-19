"""Piet Mondrian's grammar: straight horizontal and vertical lines. Each stroke's bounding box is
snapped to a grid and drawn as a rectangle; `energy` adds subdivisions; `direction` picks which
side the extra lines grow from. Line art only. Same signature as `styles.haring`."""
from __future__ import annotations

import math

from duet import config as cfg
from duet.strokes import Polyline

COLOR = "green"
GRID_MM = 10.0


def _snap(v: float) -> float:
    return round(v / GRID_MM) * GRID_MM


def _box(pl: Polyline) -> tuple[float, float, float, float]:
    xs, ys = [x for x, _ in pl], [y for _, y in pl]
    x0, y0, x1, y1 = _snap(min(xs)), _snap(min(ys)), _snap(max(xs)), _snap(max(ys))
    if x1 - x0 < GRID_MM:
        x1 = x0 + GRID_MM
    if y1 - y0 < GRID_MM:
        y1 = y0 + GRID_MM
    return x0, y0, x1, y1


def _rect(x0: float, y0: float, x1: float, y1: float) -> Polyline:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]


def style(strokes: list[Polyline], energy: float = 0.5, direction_deg: float = 0.0) -> tuple[list[Polyline], str]:
    out: list[Polyline] = []
    splits = int(round(max(0.0, min(1.0, energy)) * 3))          # 0 to 3 subdivisions per stroke
    grow_right = math.cos(math.radians(direction_deg)) >= 0
    for pl in strokes:
        if len(pl) < 2:
            continue
        x0, y0, x1, y1 = _box(pl)
        out.append(_rect(x0, y0, x1, y1))
        for k in range(1, splits + 1):
            t = k / (splits + 1)
            xs = x0 + (x1 - x0) * (t if grow_right else 1 - t)
            out.append([(xs, y0), (xs, y1)])                     # vertical subdivision
            if k % 2 == 0:
                ys = y0 + (y1 - y0) * t
                out.append([(x0, ys), (x1, ys)])                 # every second one also horizontal
    return out, COLOR


def fallback(human_ink: list[Polyline]) -> tuple[list[Polyline], str]:
    """Extend the mark's bounding box edges to the drawable edges: the human's mark becomes a cell."""
    out: list[Polyline] = []
    lo, hi_x, hi_y = cfg.INSET_MM, cfg.BOARD_W_MM - cfg.INSET_MM, cfg.BOARD_H_MM - cfg.INSET_MM
    for pl in human_ink:
        if len(pl) < 2:
            continue
        x0, y0, x1, y1 = _box(pl)
        out += [[(lo, y0), (hi_x, y0)], [(lo, y1), (hi_x, y1)], [(x0, lo), (x0, hi_y)], [(x1, lo), (x1, hi_y)]]
    return out, COLOR
