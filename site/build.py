#!/usr/bin/env python3
"""Assemble the showcase site from the sources: the pitch deck as the presentation, the live page in
replay mode as the demo, and the recorded session with the most turns as the recording it replays.

    python3 site/build.py                          # site/, longest session under code/hackathon/sessions (gitignored recordings)
    python3 site/build.py --sessions site/demo/sessions --session 20260919-151119    # a fresh clone: from the shipped session

Standard library only for the assembly; run it with the hackathon venv's python to trace the visitor's marks
from the photos as the live page did (plain python3 falls back to the plan SVGs' traced ink).
The generated folders are committed so Vercel serves site/ as is."""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATIC = REPO / "code" / "hackathon" / "duet" / "static"
PITCH = REPO / "docs" / "duet" / "pitch"
CALIBRATION = REPO / "code" / "hackathon" / "duet" / "data" / "calibration.json"
SESSIONS = REPO / "code" / "hackathon" / "sessions"
IMAGE_SIZE = [1280, 720]
ARTISTS = ["abstract", "mimic", "haring", "mondrian", "vangogh", "architect", "designer", "shader"]
COLOR_HEX = {"green": "#1b8f3a", "red": "#c62828", "blue": "#1f4fd6", "black": "#222222"}
INK_NEAR_MM = 3.0        # a traced path this close to last turn's traced ink is the same mark seen again
ROBOT_NEAR_MM = 4.0      # a traced path this close to the robot's own strokes is the robot's mark, not the visitor's
DECK_SKIP = {"gen_images.py", "README.md", "__pycache__", ".DS_Store"}
# Thoughts and quips for Claude turns, which the recorder did not keep; ink artists speak from their banks.
WORDS = {
    "20260919-151119": {7: ("A crowded world of creatures!", "A dancer for the lower corner!"),
                        10: ("A whole garden, dancing…", "Swirling skies to finish it off!")},
}

PATH_RE = re.compile(r'<path d="([^"]+)"([^>]*)/>')
STROKE_RE = re.compile(r'stroke="([^"]+)"')
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")

Point = tuple[float, float]
Polyline = list[Point]


def parse_plan_svg(text: str) -> tuple[list[Polyline], list[Polyline], list[Polyline]]:
    """A plan-NN.svg's three kinds of path: all traced ink, the robot's strokes so far, this turn's plan."""
    ink, done, plan = [], [], []
    for d, attrs in PATH_RE.findall(text):
        nums = [float(v) for v in NUM_RE.findall(d)]
        pl = [(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]
        if len(pl) < 2:
            continue
        m = STROKE_RE.search(attrs)
        stroke = m.group(1) if m else ""
        robot = stroke in ("green", "#1b8f3a")
        (plan if robot and "stroke-dasharray" in attrs else done if robot else ink).append(pl)
    return ink, done, plan


def _seg_dist2(p: Point, a: Point, b: Point) -> float:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return (p[0] - ax) ** 2 + (p[1] - ay) ** 2
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return (p[0] - (ax + t * dx)) ** 2 + (p[1] - (ay + t * dy)) ** 2


def prepare(paths: list[Polyline], mm: float) -> list[tuple[float, float, float, float, Polyline]]:
    """Paths with their bounding boxes grown by mm, so most points are dismissed without segment math."""
    out = []
    for pl in paths:
        xs, ys = [p[0] for p in pl], [p[1] for p in pl]
        out.append((min(xs) - mm, min(ys) - mm, max(xs) + mm, max(ys) + mm, pl))
    return out


def near(path: Polyline, prepared: list, mm: float, samples: int = 12) -> bool:
    """True when more than half of the path's sample points lie within mm of some prepared path."""
    if not prepared or not path:
        return False
    pts = path if len(path) <= samples else [path[round(i * (len(path) - 1) / (samples - 1))] for i in range(samples)]
    limit = mm * mm
    hits = 0
    for p in pts:
        for x0, y0, x1, y1, pl in prepared:
            if not (x0 <= p[0] <= x1 and y0 <= p[1] <= y1):
                continue
            if any(_seg_dist2(p, a, b) <= limit for a, b in zip(pl, pl[1:])):
                hits += 1
                break
    return hits * 2 > len(pts)


def new_ink(ink: list[Polyline], previous_ink: list[Polyline], robot: list[Polyline]) -> list[Polyline]:
    """The visitor's new marks this turn: traced paths not seen last turn and not the robot's own strokes."""
    prev, own = prepare(previous_ink, INK_NEAR_MM), prepare(robot, ROBOT_NEAR_MM)
    return [pl for pl in ink if not near(pl, prev, INK_NEAR_MM) and not near(pl, own, ROBOT_NEAR_MM)]


def _vision():
    """The live pipeline's tracing, when the hackathon venv is running this script; None under plain python3."""
    try:
        import sys
        sys.path.insert(0, str(REPO / "code" / "hackathon"))
        import cv2
        from duet import vision
        return vision, cv2
    except Exception:            # noqa: BLE001 - any missing wheel means "no tracing", not a failure
        return None, None


def traced_new_ink(session_dir: Path, n: int, calibration: dict, vision, cv2) -> list[Polyline] | None:
    """The visitor's marks of turn n as the live page saw them: what got darker between the last look
    and this turn's photo, skeletonised and mapped to robot millimetres. None when a photo is unreadable."""
    cur = cv2.imread(str(session_dir / f"turn-{n:02d}-human.jpg"))
    prev = cv2.imread(str(session_dir / (f"turn-{n - 1:02d}-robot.jpg" if n > 1 else "turn-00-start.jpg")))
    if cur is None or prev is None or cur.shape != prev.shape:
        return None
    mask, _ = vision.new_ink(cur, prev)
    return [[(float(x), float(y)) for x, y in pl] for pl in vision.cam_to_robot(vision.trace(mask), calibration)]


def longest_session(sessions: Path) -> Path:
    """The session folder whose record counts the most completed turns (ties: the latest)."""
    best, best_key = None, (-1, "")
    for folder in sorted(sessions.iterdir()) if sessions.is_dir() else []:
        meta = folder / "session.json"
        if not meta.is_file():
            continue
        try:
            turns = int(json.loads(meta.read_text()).get("turn", 0))
        except (ValueError, json.JSONDecodeError):
            continue
        if (turns, folder.name) > best_key:
            best, best_key = folder, (turns, folder.name)
    if best is None:
        raise SystemExit(f"no session with a session.json under {sessions}")
    return best


def rounded(pl: Polyline) -> list[list[float]]:
    return [[round(x, 1), round(y, 1)] for x, y in pl]


def replay_data(session_dir: Path, calibration: dict, words: dict[int, tuple[str, str]] | None = None) -> dict:
    """replay.json: the session's turns with their words, new ink, plan strokes, and the calibration."""
    meta = json.loads((session_dir / "session.json").read_text())
    sid = session_dir.name
    base = f"sessions/{sid}"
    words = words or {}
    vision, cv2 = _vision()
    turns, previous_ink = [], []
    for t in sorted(meta.get("turns", []), key=lambda t: t["turn"]):
        n = int(t["turn"])
        svg = session_dir / f"plan-{n:02d}.svg"
        ink, done, plan = parse_plan_svg(svg.read_text()) if svg.is_file() else ([], [], [])
        traced = traced_new_ink(session_dir, n, calibration, vision, cv2) if vision else None
        new = traced if traced is not None else new_ink(ink, previous_ink, done)
        entry = {
            "turn": n, "artist": t.get("artist") or meta.get("artist") or "haring", "source": t.get("source") or "claude",
            "latency_s": t.get("latency_s"), "coverage": t.get("coverage", 0.0), "planned_mm": t.get("planned_mm"),
            "sees": t.get("sees", ""), "adds": t.get("adds", ""), "color": COLOR_HEX.get(t.get("color") or "green", "#1b8f3a"),
            "new": [rounded(pl) for pl in new], "plan": [rounded(pl) for pl in plan],
            "frames": {"human": (session_dir / f"turn-{n:02d}-human-frame.jpg").is_file(),
                       "robot": (session_dir / f"turn-{n:02d}-robot-frame.jpg").is_file()},
        }
        if n in words:
            entry["thought"], entry["quip"] = words[n]
        turns.append(entry)
        previous_ink = ink
    last = turns[-1]["turn"] if turns else 0
    return {
        "session": sid, "base": base, "exchanges": int(meta.get("exchanges") or len(turns) or 1),
        "length": meta.get("length") or "long", "artists": ARTISTS,
        "calib": {"marks_image": calibration["marks_image"], "board_tl_index": calibration["board_tl_index"],
                  "board_mm": calibration.get("board_mm", [176.0, 240.0]), "image_size": IMAGE_SIZE,
                  "cam_to_robot": calibration.get("cam_to_robot") or {"ax": 1, "bx": 0, "ay": 1, "by": 0}},
        "frames": {"start": (session_dir / "turn-00-start-frame.jpg").is_file(),
                   "final": (session_dir / f"turn-{last:02d}-final.jpg").is_file()},
        "video": f"{base}/session.mp4" if (session_dir / "session.mp4").is_file() else None,
        "turns": turns,
    }


SITE = "https://viam-duet.vercel.app"
PREVIEW_DESCRIPTION = ("You draw one mark. Duet looks, understands, and answers in the hand of an artist. "
                       "Built at Viam's Fine Motor Skills hackathon, New York, September 2026. Honorable mention.")
PREVIEW_ALT = "A visitor with a red marker and a robot arm with a green marker drawing loops together on a whiteboard."


def preview_tags(url: str, title: str) -> str:
    """Open Graph and Twitter card tags, so a shared link unfurls with the illustration (site/img/og-card.jpg)."""
    return "\n".join([
        '<meta property="og:type" content="website">', '<meta property="og:site_name" content="Duet">',
        f'<meta property="og:title" content="{title}">', f'<meta property="og:description" content="{PREVIEW_DESCRIPTION}">',
        f'<meta property="og:url" content="{url}">', f'<meta property="og:image" content="{SITE}/img/og-card.jpg">',
        '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{PREVIEW_ALT}">', '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">', f'<meta name="twitter:description" content="{PREVIEW_DESCRIPTION}">',
        f'<meta name="twitter:image" content="{SITE}/img/og-card.jpg">', f'<meta name="twitter:image:alt" content="{PREVIEW_ALT}">',
    ])


def rewrite_index(html: str, replay_url: str = "replay.json") -> str:
    """The page's index for the site: assets relative to demo/, the replay meta tag, a title, the link preview tags."""
    out = html.replace('href="/static/', 'href="static/').replace('src="/static/', 'src="static/')
    marker = '<meta name="viewport" content="width=device-width, initial-scale=1">'
    assert marker in out, "the page's viewport meta moved"
    out = out.replace(marker, f'{marker}\n<meta name="duet-replay" content="{replay_url}">', 1)
    out = out.replace("<title>Duet</title>", "<title>Duet · demo</title>\n" + preview_tags(f"{SITE}/demo/", "Duet: the demo"), 1)
    return out


def copy_tree(src: Path, dst: Path, skip: set[str] = frozenset()) -> None:
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst, ignore=lambda d, names: [n for n in names if n in skip])


def build(out: Path, session_dir: Path, calibration: dict, static: Path = STATIC, pitch: Path = PITCH) -> dict:
    """Write assets/, presentation/, and demo/ under out. Returns the replay data written."""
    out.mkdir(parents=True, exist_ok=True)
    assets = out / "assets"
    assets.mkdir(exist_ok=True)
    for name in ("tokens.css", "fredoka.css"):
        shutil.copy2(static / name, assets / name)
    copy_tree(pitch, out / "presentation", DECK_SKIP)
    demo = out / "demo"
    copy_tree(static, demo / "static", {"__pycache__", ".DS_Store"})
    dst = demo / "sessions" / session_dir.name
    if session_dir.resolve() == dst.resolve():          # rebuilding from the shipped session: leave it where it is
        for other in (demo / "sessions").glob("*"):
            if other.is_dir() and other.resolve() != dst.resolve(): shutil.rmtree(other)
    else:
        shutil.rmtree(demo / "sessions", ignore_errors=True)
        copy_tree(session_dir, dst, {".DS_Store"})
    (demo / "index.html").write_text(rewrite_index((static / "index.html").read_text()))
    data = replay_data(session_dir, calibration, WORDS.get(session_dir.name))
    (demo / "replay.json").write_text(json.dumps(data, separators=(",", ":")) + "\n")
    return data


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--session", help="session folder name; default: the one with the most turns")
    p.add_argument("--sessions", type=Path, default=SESSIONS, help="where the recorded sessions live")
    p.add_argument("--out", type=Path, default=REPO / "site", help="the site folder to write into")
    args = p.parse_args(argv)
    session_dir = args.sessions / args.session if args.session else longest_session(args.sessions)
    if not (session_dir / "session.json").is_file():
        raise SystemExit(f"no session.json in {session_dir}")
    data = build(args.out, session_dir, json.loads(CALIBRATION.read_text()))
    strokes = sum(len(t["plan"]) for t in data["turns"])
    marks = sum(len(t["new"]) for t in data["turns"])
    size = sum(f.stat().st_size for f in (args.out / "demo" / "sessions").rglob("*") if f.is_file()) / 1e6
    print(f"site written to {args.out}: session {data['session']}, {len(data['turns'])} turns, "
          f"{marks} visitor marks, {strokes} robot strokes, {size:.1f} MB of session files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
