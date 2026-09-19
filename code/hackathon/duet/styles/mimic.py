"""Mimic: the robot copies the strokes the visitor just drew and sets the copy beside them. No Claude
call. `energy` scales the copy, the light dial says which side it goes to, and the exchange number
picks shift, mirror, or a quarter turn. The planner's rules (clip, clearance, cap) still apply."""
from __future__ import annotations

from duet import config as cfg
from duet.strokes import Polyline, length
from duet.styles import abstract
from duet.styles.ink import InkTurn, light_vector

FROM_INK = True
COLOR = "green"
VARIANTS = ("shifted", "mirrored", "turned")
THOUGHTS = ("Let me try that…", "Watch this…", "One more, my way…")
QUIPS = ("Copycat!", "Like this?", "Two of a kind!", "Your move, again.")
SEES = "Your new mark, ready to echo."
INSET = cfg.INSET_MM


def _bbox(pls: list[Polyline]) -> tuple[float, float, float, float]:
    xs = [x for pl in pls for x, _ in pl]
    ys = [y for pl in pls for _, y in pl]
    return min(xs), min(ys), max(xs), max(ys)


def _copy(new: list[Polyline], scale: float, variant: str) -> list[Polyline]:
    """The strokes scaled, and mirrored or turned, about their bounding-box centre."""
    x0, y0, x1, y1 = _bbox(new)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    out: list[Polyline] = []
    for pl in new:
        pts: Polyline = []
        for x, y in pl:
            dx, dy = x - cx, y - cy
            if variant == "mirrored":
                dx = -dx
            elif variant == "turned":
                dx, dy = -dy, dx
            pts.append((cx + scale * dx, cy + scale * dy))
        out.append(pts)
    return out


def _half_extent(pls: list[Polyline], u: tuple[float, float]) -> float:
    x0, y0, x1, y1 = _bbox(pls)
    return (abs(u[0]) * (x1 - x0) + abs(u[1]) * (y1 - y0)) / 2


def _shift(pls: list[Polyline], dx: float, dy: float) -> list[Polyline]:
    return [[(x + dx, y + dy) for x, y in pl] for pl in pls]


def _fits(pls: list[Polyline]) -> bool:
    x0, y0, x1, y1 = _bbox(pls)
    return x0 >= INSET and y0 >= INSET and x1 <= cfg.BOARD_W_MM - INSET and y1 <= cfg.BOARD_H_MM - INSET


def _inside_area(pls: list[Polyline]) -> float:
    x0, y0, x1, y1 = _bbox(pls)
    w = min(x1, cfg.BOARD_W_MM - INSET) - max(x0, INSET)
    h = min(y1, cfg.BOARD_H_MM - INSET) - max(y0, INSET)
    return max(0.0, w) * max(0.0, h)


def place(copy: list[Polyline], original: list[Polyline], direction_deg: float) -> tuple[list[Polyline], bool]:
    """The copy moved beside the original along the dial's direction, clear of it; the opposite side and
    the two perpendiculars are tried when it would leave the drawable area. Returns the placement and
    whether it fits; when nothing fits, the candidate with the most area inside."""
    ux, uy = light_vector(direction_deg)
    best: list[Polyline] | None = None
    for u in ((ux, uy), (-ux, -uy), (-uy, ux), (uy, -ux)):
        d = _half_extent(original, u) + _half_extent(copy, u) + cfg.CLEARANCE_MM + cfg.MIMIC_GAP_MM
        cand = _shift(copy, d * u[0], d * u[1])
        if _fits(cand):
            return cand, True
        if best is None or _inside_area(cand) > _inside_area(best):
            best = cand
    return best or copy, False


def respond(new: list[Polyline], energy: float, direction_deg: float, exchange: int, length_setting: str) -> InkTurn:
    v = (exchange - 1) % len(VARIANTS)
    words = dict(sees=SEES, adds=f"a copy beside it, {VARIANTS[v]}", thought=THOUGHTS[v],
                 quip=QUIPS[(exchange - 1) % len(QUIPS)])
    strokes = [[(float(x), float(y)) for x, y in pl] for pl in new if len(pl) >= 2]
    if not strokes:
        return InkTurn([], COLOR, **words)
    lo, hi = cfg.MIMIC_SCALE
    scale = lo + (hi - lo) * max(0.0, min(1.0, energy))
    placed: list[Polyline] = []
    for s in sorted({scale, lo}, reverse=True):
        placed, fits = place(_copy(strokes, s, VARIANTS[v]), strokes, direction_deg)
        if fits:
            break
    return InkTurn(sorted(placed, key=length, reverse=True), COLOR, **words)


fallback = abstract.fallback
