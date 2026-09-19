"""Abstract mode: the robot answers the person's marks with a few clean abstract shapes, each drawn
once as a single line, kept apart from each other. Claude proposes the shapes (circles, arcs, spirals,
zigzags, lozenges); this styler keeps them as given and never adds passes or ticks; the planner's open-
strokes rules handle size and spacing. Same signature as the other stylers."""
from __future__ import annotations

import math

from duet import config as cfg
from duet.strokes import Polyline

COLOR = "green"
FALLBACK_RADIUS_MM = 12.0
INSET = cfg.INSET_MM if hasattr(cfg, "INSET_MM") else 15.0


def style(strokes: list[Polyline], energy: float = 0.5, direction_deg: float = 0.0) -> tuple[list[Polyline], str]:
    """Single clean lines, exactly as proposed; spacing and size are the planner's job now."""
    return [[(float(x), float(y)) for x, y in pl] for pl in strokes if len(pl) >= 2], COLOR


def fallback(human_ink: list[Polyline]) -> tuple[list[Polyline], str]:
    """When Claude is unavailable: one calm three-quarter arc beside the new mark, on whichever side has
    room, far enough away that the clearance rule leaves it whole."""
    pts = [p for pl in human_ink for p in pl]
    w, h = cfg.BOARD_W_MM, cfg.BOARD_H_MM
    if not pts:
        cx, cy = w / 2, h / 2
    else:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        gap = cfg.CLEARANCE_MM + FALLBACK_RADIUS_MM + 4.0
        cy = min(max((min(ys) + max(ys)) / 2, INSET + FALLBACK_RADIUS_MM), h - INSET - FALLBACK_RADIUS_MM)
        right, left = max(xs) + gap, min(xs) - gap
        cx = right if right + FALLBACK_RADIUS_MM <= w - INSET else left
        cx = min(max(cx, INSET + FALLBACK_RADIUS_MM), w - INSET - FALLBACK_RADIUS_MM)
    arc = [(cx + FALLBACK_RADIUS_MM * math.cos(t), cy + FALLBACK_RADIUS_MM * math.sin(t))
           for t in (0.25 * math.pi + i * (1.5 * math.pi / 24) for i in range(25))]
    return [arc], COLOR
