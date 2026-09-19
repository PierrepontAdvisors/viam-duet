"""When does the human's turn end? A pure state machine over readings from `vision`.

Dock rule: at least one docked marker went missing since the last turn; now every marker is home,
the scene is still and no hand is visible, and that has held for STILL_S. A marker that is home but
out of position asks for a reseat instead.

Held rule: something happened since the last turn (motion or a hand); now the scene is still with
no hand, and that has held for HELD_QUIET_S. The session then diffs the board and goes back to
waiting if no new ink is found.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from duet import config as cfg


@dataclass(frozen=True)
class Reading:
    t: float
    hand: bool
    still: bool
    dots: dict[str, str] = field(default_factory=dict)   # slot -> "home" | "moved" | "missing"; empty in held mode


@dataclass(frozen=True)
class Event:
    kind: str                        # "fire" | "reseat" | "reseat_ok"
    slots: tuple[str, ...] = ()


class Trigger:
    def __init__(self, handoff: str, quiet_s: float | None = None):
        if handoff not in ("dock", "held"):
            raise ValueError(f"handoff must be 'dock' or 'held', not {handoff!r}")
        self.handoff = handoff
        self.quiet_s = quiet_s if quiet_s is not None else (cfg.STILL_S if handoff == "dock" else cfg.HELD_QUIET_S)
        self.reset()

    def reset(self) -> None:
        self.armed = False               # something happened since the last turn
        self.quiet_since: float | None = None
        self.reseat = False

    def update(self, r: Reading) -> Event | None:
        settled, event = self._dock(r) if self.handoff == "dock" else self._held(r)
        if event is not None:
            return event
        if not settled:
            self.quiet_since = None
            return None
        if self.quiet_since is None:
            self.quiet_since = r.t
            return None
        if r.t - self.quiet_since >= self.quiet_s:
            self.reset()
            return Event("fire")
        return None

    def _dock(self, r: Reading) -> tuple[bool, Event | None]:
        if any(s == "missing" for s in r.dots.values()):
            self.armed = True
        moved = tuple(sorted(name for name, s in r.dots.items() if s == "moved"))
        if moved:
            self.quiet_since = None
            if self.reseat:
                return False, None
            self.reseat = True
            return False, Event("reseat", moved)
        if self.reseat:
            self.reseat = False
            self.quiet_since = None
            return False, Event("reseat_ok")
        all_home = bool(r.dots) and all(s == "home" for s in r.dots.values())
        return self.armed and all_home and r.still and not r.hand, None

    def _held(self, r: Reading) -> tuple[bool, Event | None]:
        if r.hand or not r.still:
            self.armed = True
        return self.armed and r.still and not r.hand, None
