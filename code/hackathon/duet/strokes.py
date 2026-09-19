"""Pure geometry for polylines in board millimeters. No I/O, no robot."""
from __future__ import annotations

import math

Point = tuple[float, float]
Polyline = list[Point]


def length(points: Polyline) -> float:
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def resample(points: Polyline, spacing: float) -> Polyline:
    """Points along the same path no more than `spacing` apart. Every original vertex is kept."""
    if len(points) < 2:
        return list(points)
    out: Polyline = [points[0]]
    for a, b in zip(points, points[1:]):
        n = max(1, math.ceil(math.dist(a, b) / spacing))
        for k in range(1, n + 1):
            t = k / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def cut_to_budget(polylines: list[Polyline], budget_mm: float) -> list[Polyline]:
    """Keep whole polylines, in order, while they fit; cut the first one that does not; drop the rest."""
    kept: list[Polyline] = []
    remaining = budget_mm
    for pl in polylines:
        if remaining <= 0:
            break
        if length(pl) <= remaining:
            kept.append(list(pl))
            remaining -= length(pl)
            continue
        partial: Polyline = [pl[0]]
        for a, b in zip(pl, pl[1:]):
            if remaining <= 0:
                break
            d = math.dist(a, b)
            if d <= remaining:
                partial.append(b)
                remaining -= d
            else:
                t = remaining / d
                partial.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
                remaining = 0
                break
        if len(partial) > 1:
            kept.append(partial)
        break
    return kept
