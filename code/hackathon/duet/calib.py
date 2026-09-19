"""Board-to-robot calibration and pose storage.

Three touch-off corners, recorded as gripper poses in `world` while the marker tip rests on the
writing surface, define the board plane. Commanding the gripper to a pose from `to_world` puts the
tip on the board, so the marker length never needs measuring.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from viam.proto.common import Pose

from duet import config as cfg


def pose_to_dict(p: Pose) -> dict:
    return {"x": p.x, "y": p.y, "z": p.z, "o_x": p.o_x, "o_y": p.o_y, "o_z": p.o_z, "theta": p.theta}


def dict_to_pose(d: dict) -> Pose:
    return Pose(x=d["x"], y=d["y"], z=d["z"], o_x=d["o_x"], o_y=d["o_y"], o_z=d["o_z"], theta=d["theta"])


def load_poses(path: Path = cfg.POSES_PATH) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_pose(name: str, pose: Pose, path: Path = cfg.POSES_PATH) -> dict:
    """Store `pose` under a dotted name such as 'slot.red'; rewrite the file atomically; return the new dict."""
    poses = load_poses(path)
    node = poses
    *parents, leaf = name.split(".")
    for key in parents:
        node = node.setdefault(key, {})
    node[leaf] = pose_to_dict(pose)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(poses, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)   # atomic on POSIX: a crash mid-write cannot truncate the taught poses
    return poses


@dataclass(frozen=True)
class BoardToRobot:
    origin: tuple[float, float, float]        # top-left corner in world mm
    ex: tuple[float, float, float]            # vector top-left -> top-right
    ey: tuple[float, float, float]            # vector top-left -> bottom-left
    width_mm: float
    height_mm: float
    orientation: tuple[float, float, float, float]  # o_x, o_y, o_z, theta of the touch-off
    warp: tuple[float, float, float] = (0.0, 0.0, 0.0)  # measured bottom-right minus tl + ex + ey: a bowed board bends the surface

    @classmethod
    def from_corners(cls, tl: Pose, tr: Pose, bl: Pose, width_mm: float, height_mm: float,
                     br: Pose | None = None) -> "BoardToRobot":
        """Three corners define the plane; a fourth, when touched off, records how far the real
        bottom-right sits from the parallelogram's, so a bowed board is followed bilinearly."""
        o = np.array([tl.x, tl.y, tl.z])
        ex = np.array([tr.x, tr.y, tr.z]) - o
        ey = np.array([bl.x, bl.y, bl.z]) - o
        warp = (np.array([br.x, br.y, br.z]) - (o + ex + ey)) if br is not None else np.zeros(3)
        return cls(tuple(map(float, o)), tuple(map(float, ex)), tuple(map(float, ey)),
                   width_mm, height_mm, (tl.o_x, tl.o_y, tl.o_z, tl.theta), tuple(map(float, warp)))

    @classmethod
    def from_poses(cls, poses: dict) -> "BoardToRobot":
        corners = poses.get("corner", {})
        missing = [name for name in ("tl", "tr", "bl") if name not in corners]
        if missing:
            raise ValueError(f"missing corner touch-offs: {', '.join(missing)}; "
                             "run `python -m duet.teach corner <name>` for each")
        return cls.from_corners(dict_to_pose(corners["tl"]), dict_to_pose(corners["tr"]),
                                dict_to_pose(corners["bl"]), cfg.BOARD_W_MM, cfg.BOARD_H_MM,
                                br=dict_to_pose(corners["br"]) if "br" in corners else None)

    def to_world(self, u: float, v: float, lift: float = 0.0) -> Pose:
        """Gripper pose that puts the marker tip at board point (u, v), raised by `lift` mm.
        `lift` is along world z, not the board normal; the board is assumed to be close to level."""
        o, ex, ey, warp = (np.array(t) for t in (self.origin, self.ex, self.ey, self.warp))
        s, t = u / self.width_mm, v / self.height_mm
        p = o + ex * s + ey * t + warp * s * t
        ox, oy, oz, th = self.orientation
        return Pose(x=float(p[0]), y=float(p[1]), z=float(p[2] + lift), o_x=ox, o_y=oy, o_z=oz, theta=th)
