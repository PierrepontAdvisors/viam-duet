"""SVG preview of a turn: human ink, drawn strokes, queued strokes. Board millimeters map 1:1."""
from __future__ import annotations

from pathlib import Path

from duet import config as cfg
from duet.strokes import Polyline


def _path(pl: Polyline) -> str:
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pl)


def render(human: list[Polyline], drawn: list[Polyline], queued: list[Polyline], color: str = "green") -> str:
    w, h = cfg.BOARD_W_MM, cfg.BOARD_H_MM
    i = cfg.INSET_MM
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}mm" height="{h}mm">',
             f'<rect x="0" y="0" width="{w}" height="{h}" fill="white" stroke="#999" stroke-width="0.5"/>',
             f'<rect x="{i}" y="{i}" width="{w - 2 * i}" height="{h - 2 * i}" fill="none" stroke="#ddd" stroke-width="0.3"/>']
    parts += [f'<path d="{_path(pl)}" fill="none" stroke="#222" stroke-width="1.2"/>' for pl in human if len(pl) >= 2]
    parts += [f'<path d="{_path(pl)}" fill="none" stroke="{color}" stroke-width="1.2"/>' for pl in drawn if len(pl) >= 2]
    parts += [f'<path d="{_path(pl)}" fill="none" stroke="{color}" stroke-width="1.2" stroke-dasharray="2 1.5"/>'
              for pl in queued if len(pl) >= 2]
    parts.append("</svg>")
    return "\n".join(parts)


def write(path: Path, human: list[Polyline], drawn: list[Polyline], queued: list[Polyline], color: str = "green") -> None:
    path.write_text(render(human, drawn, queued, color))
