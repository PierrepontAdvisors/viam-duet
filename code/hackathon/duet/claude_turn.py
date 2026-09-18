"""One Claude turn: the gridded board photo and the traced human strokes go in, a structured
proposal (what it sees, what it adds, strokes in board millimeters) comes out.

    python -m duet.claude_turn captures/calib_board.jpg                      first turn, nothing to diff
    python -m duet.claude_turn current.jpg previous.jpg --length medium --exchange 2/5

Writes captures/plan.svg with the validated, styled strokes. Needs ANTHROPIC_API_KEY in .env.
"""
from __future__ import annotations

import base64
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import anthropic
import cv2
import numpy as np
from pydantic import BaseModel

import viam_conn
from duet import config as cfg
from duet import planner, svg, vision
from duet.strokes import Polyline, cut_to_budget, length
from duet.styles import haring

MODEL = "claude-opus-5"
TIMEOUT_S = {"short": 12.0, "medium": 25.0, "long": 45.0}   # a long scene is thousands of output tokens; 12 s timed out
GRID_MM = 20


class Pt(BaseModel):
    x: float
    y: float


class Stroke(BaseModel):
    kind: Literal["polyline", "circle", "arc"]
    points: list[Pt]          # polyline only; empty otherwise
    cx: float                 # circle and arc center; 0 otherwise
    cy: float
    r: float                  # circle and arc radius; 0 otherwise
    start_deg: float          # arc only; 0 otherwise
    end_deg: float
    attached: bool            # true only if the stroke deliberately touches existing ink


class Proposal(BaseModel):
    sees: str
    adds: str
    color: str
    strokes: list[Stroke]


SYSTEM = f"""You are Duet, a robot arm that draws together with a person on a small dry-erase board.
The person draws a mark, you look at the board and add to it, and you take turns until the piece is done.

The board is {cfg.BOARD_W_MM:.0f} mm wide and {cfg.BOARD_H_MM:.0f} mm tall. Coordinates are millimeters with the
origin at the top-left corner, x increasing to the right and y increasing downward. The photo you receive
is a flat top-down view with a grid every {GRID_MM} mm labelled along the edges, so you can read positions
off it. Only the area at least {cfg.INSET_MM:.0f} mm inside every edge is drawable.

Your job each turn: say in one sentence what the drawing is becoming, say in one sentence what you will add
and why, then give the strokes as data. Strokes are polylines, circles, or arcs in board millimeters.
Keep every stroke inside the drawable area and at least 3 mm away from existing ink, unless a stroke is
meant to touch or continue existing ink, in which case mark it attached. The total length of all strokes
must stay within the budget you are given. The artist mode is Keith Haring: thick, simple, continuous outlines; simplified figures and creatures
with rounded limbs in energetic poses; clear silhouettes; playful symbols; everything reads from across a
room. Motion ticks radiating from your strokes are added for you, so do not draw them. Be generous:
use the budget.
Draw like a marker on a whiteboard: line art only, no fills, no shading. Use the pacing you are given:
early exchanges add one clear element; the last exchange should complete the piece.
Respond only through the structured output."""


def grid_overlay(board_bgr: np.ndarray) -> np.ndarray:
    """The board photo with a labelled millimeter grid so positions can be read off it."""
    out = board_bgr.copy()
    h, w = out.shape[:2]
    px = vision.PX_PER_MM
    for mm in range(0, int(cfg.BOARD_W_MM) + 1, GRID_MM):
        x = int(mm * px)
        cv2.line(out, (x, 0), (x, h - 1), (200, 200, 200), 1)
        cv2.putText(out, str(mm), (x + 2, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 200), 1)
    for mm in range(0, int(cfg.BOARD_H_MM) + 1, GRID_MM):
        y = int(mm * px)
        cv2.line(out, (0, y), (w - 1, y), (200, 200, 200), 1)
        cv2.putText(out, str(mm), (2, y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 200), 1)
    return out


def encode_jpeg_b64(bgr: np.ndarray) -> str:
    ok, buf = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ok:
        raise RuntimeError("could not encode the board photo")
    return base64.standard_b64encode(buf.tobytes()).decode("ascii")


def fmt_polylines(polylines: list[Polyline]) -> str:
    if not polylines:
        return "(none)"
    return "\n".join("  " + " ".join(f"({x:.0f},{y:.0f})" for x, y in pl) for pl in polylines)


@dataclass(frozen=True)
class TurnResult:
    proposal: Proposal | None
    source: str            # "claude" or "fallback"
    latency_s: float
    error: str | None


def make_client() -> anthropic.Anthropic:
    if not viam_conn.ANTHROPIC_API_KEY:
        raise SystemExit("ANTHROPIC_API_KEY is missing from code/hackathon/.env")
    return anthropic.Anthropic(api_key=viam_conn.ANTHROPIC_API_KEY, timeout=TIMEOUT_S["long"], max_retries=0)


def propose(client: anthropic.Anthropic, board_bgr: np.ndarray, human: list[Polyline], history: list[dict],
            length_setting: str, exchange: int, exchange_total: int) -> TurnResult:
    budget = cfg.BUDGET_MM[length_setting]
    asks = {"short": "one small addition: a detail or an accent",
            "medium": "one full element that extends the drawing",
            "long": "a full scene: six to twelve bold elements, such as figures, creatures, a setting and "
                    "symbols, each a simple continuous outline, spread across the free space"}[length_setting]
    hist = "\n".join(f"  exchange {i + 1}: saw \"{h['sees']}\"; added \"{h['adds']}\"" for i, h in enumerate(history)) or "  (this is the first exchange)"
    text = (f"Exchange {exchange} of {exchange_total}. Length setting: {length_setting}, so add {asks}. "
            f"Stroke budget: {budget:.0f} mm total. Allowed color: green.\n"
            f"New strokes the person just drew, as polylines in board millimeters:\n{fmt_polylines(human)}\n"
            f"Earlier exchanges:\n{hist}")
    t0 = time.monotonic()
    try:
        response = client.with_options(timeout=TIMEOUT_S[length_setting]).messages.parse(
            model=MODEL,
            max_tokens=8000,
            system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                             "data": encode_jpeg_b64(grid_overlay(board_bgr))}},
                {"type": "text", "text": text},
            ]}],
            output_format=Proposal,
            output_config={"effort": "low"},
        )
        return TurnResult(response.parsed_output, "claude", time.monotonic() - t0, None)
    except Exception as exc:   # timeout, network, refusal, schema: the fallback grammar answers
        return TurnResult(None, "fallback", time.monotonic() - t0, f"{type(exc).__name__}: {str(exc)[:200]}")


def plan_turn(result: TurnResult, human: list[Polyline], existing_ink: list[Polyline],
              length_setting: str) -> tuple[list[Polyline], str]:
    """Validated and styled polylines for the arm, from a proposal or the fallback."""
    budget = cfg.BUDGET_MM[length_setting]
    if result.proposal is None:
        styled, color = haring.fallback(human)
        return cut_to_budget(styled, budget), color
    strokes = [s.model_dump() for s in result.proposal.strokes]
    safe = planner.validate(strokes, existing_ink, budget)
    styled, color = haring.style(safe)
    return cut_to_budget(styled, budget), color     # styling adds passes and ticks; the budget is for the arm


def main(argv: list[str]) -> None:
    if not argv:
        raise SystemExit(__doc__)
    length_setting = argv[argv.index("--length") + 1] if "--length" in argv else "short"
    ex = argv[argv.index("--exchange") + 1] if "--exchange" in argv else "1/5"
    exchange, total = (int(v) for v in ex.split("/"))
    paths = [a for a in argv if not a.startswith("--") and a not in (length_setting, ex)]
    current = cv2.imread(paths[0])
    if current is None:
        raise SystemExit(f"cannot read {paths[0]}")
    if len(paths) > 1:
        previous = cv2.imread(paths[1])
        mask, coverage = vision.new_ink(current, previous)
        human = vision.trace(mask)
    else:
        human, coverage = [], 0.0
    ink_now = vision.trace(vision.new_ink(current, np.full_like(current, 235))[0])
    print(f"human strokes traced: {len(human)}; all ink on the board: {len(ink_now)} paths; coverage {coverage:.3f}")
    result = propose(make_client(), current, human, [], length_setting, exchange, total)
    print(f"source: {result.source}  latency: {result.latency_s:.1f} s" + (f"  error: {result.error}" if result.error else ""))
    if result.proposal:
        p = result.proposal
        print(f"sees: {p.sees}\nadds: {p.adds}\ncolor: {p.color}\nstrokes proposed: {len(p.strokes)}")
    planned, color = plan_turn(result, human, ink_now, length_setting)
    total_mm = sum(length(pl) for pl in planned)
    out = Path("captures/plan.svg")
    svg.write(out, ink_now, [], planned, color)
    print(f"planned {len(planned)} polylines, {total_mm:.0f} mm (budget {cfg.BUDGET_MM[length_setting]:.0f}); preview {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
