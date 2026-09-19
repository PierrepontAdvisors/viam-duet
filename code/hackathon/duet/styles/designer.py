"""Product Designer: object sketches. Claude proposes housings, controls, and parts; this styler rounds
every sharp corner with a small fillet (a quadratic curve between the two sides, limited by their
length) and leaves straight runs and gentle bends alone. `energy` and `direction` are accepted and
ignored, as in Abstract."""
from __future__ import annotations

import math

from duet import config as cfg
from duet.strokes import Polyline
from duet.styles import abstract

COLOR = "green"
SAMPLES = 6


def _turn_deg(p, q, r) -> float:
    a1, a2 = math.atan2(q[1] - p[1], q[0] - p[0]), math.atan2(r[1] - q[1], r[0] - q[0])
    return abs(math.degrees((a2 - a1 + math.pi) % (2 * math.pi) - math.pi))


def _rounded(p, q, r, radius: float) -> Polyline:
    """Points from a spot on side pq, round the corner q, to a spot on side qr."""
    l1, l2 = math.dist(p, q), math.dist(q, r)
    t = min(radius, 0.45 * l1, 0.45 * l2)
    a = (q[0] + (p[0] - q[0]) * t / l1, q[1] + (p[1] - q[1]) * t / l1)
    b = (q[0] + (r[0] - q[0]) * t / l2, q[1] + (r[1] - q[1]) * t / l2)
    out: Polyline = []
    for k in range(SAMPLES + 1):
        s = k / SAMPLES
        w0, w1, w2 = (1 - s) ** 2, 2 * (1 - s) * s, s ** 2
        out.append((w0 * a[0] + w1 * q[0] + w2 * b[0], w0 * a[1] + w1 * q[1] + w2 * b[1]))
    return out


def fillet(pl: Polyline, radius: float = cfg.DESIGNER_FILLET_MM, min_turn_deg: float = cfg.FILLET_MIN_DEG) -> Polyline:
    pts = [(float(x), float(y)) for x, y in pl]
    pts = [p for i, p in enumerate(pts) if i == 0 or p != pts[i - 1]]
    if len(pts) < 3:
        return pts
    closed = math.dist(pts[0], pts[-1]) < 1e-9
    ring = pts[:-1] if closed else pts
    n = len(ring)
    out: Polyline = [] if closed else [ring[0]]
    for i in (range(n) if closed else range(1, n - 1)):
        p, q, r = ring[i - 1], ring[i], ring[(i + 1) % n]
        if _turn_deg(p, q, r) < min_turn_deg:
            out.append(q)
        else:
            out.extend(_rounded(p, q, r, radius))
    out.append(out[0] if closed else ring[-1])
    return out


def style(strokes: list[Polyline], energy: float = 0.5, direction_deg: float = 0.0) -> tuple[list[Polyline], str]:
    return [fillet(pl) for pl in strokes if len(pl) >= 2], COLOR


fallback = abstract.fallback
