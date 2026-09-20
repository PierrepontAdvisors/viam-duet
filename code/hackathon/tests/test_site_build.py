"""The showcase site assembler: plan SVG parsing, the visitor's new ink, the longest session, the build."""
import importlib.util
import json
from pathlib import Path

import pytest

BUILD = Path(__file__).resolve().parents[3] / "site" / "build.py"
spec = importlib.util.spec_from_file_location("site_build", BUILD)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 176.0 240.0" width="176.0mm" height="240.0mm">\n'


def path(pl, stroke, dashed=False):
    d = " ".join(("M" if i == 0 else "L") + f" {x:.1f} {y:.1f}" for i, (x, y) in enumerate(pl))
    dash = ' stroke-dasharray="2 1.5"' if dashed else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="1.2"{dash}/>\n'


SQUARE = [(40.0, 40.0), (80.0, 40.0), (80.0, 80.0), (40.0, 80.0), (40.0, 40.0)]
LINE = [(100.0, 100.0), (140.0, 100.0)]
COPY = [(100.0, 40.0), (140.0, 40.0), (140.0, 80.0), (100.0, 80.0), (100.0, 40.0)]     # the robot's echo of the square
CALIB = {"marks_image": [[1, 2], [3, 4], [5, 6], [7, 8]], "board_tl_index": 3, "board_mm": [176.0, 240.0],
         "cam_to_robot": {"ax": 0.97, "bx": 8.5, "ay": 0.99, "by": 8.3}}


def test_parse_plan_svg_splits_traced_ink_robot_strokes_and_the_plan():
    svg = HEAD + path(SQUARE, "#222") + path(COPY, "green") + path(LINE, "green", dashed=True) + "</svg>"
    ink, done, plan = build.parse_plan_svg(svg)
    assert ink == [SQUARE] and done == [COPY] and plan == [LINE]


def test_new_ink_keeps_fresh_marks_and_drops_last_turns_ink_and_the_robots_marks():
    seen_again = [(x + 0.4, y - 0.3) for x, y in SQUARE]                    # the same square, traced a little differently
    robot_seen = [(x + 1.5, y + 1.0) for x, y in COPY]                       # the robot's copy as the camera traced it
    fresh = LINE
    out = build.new_ink([seen_again, robot_seen, fresh], previous_ink=[SQUARE], robot=[COPY])
    assert out == [fresh]
    assert build.new_ink([SQUARE], previous_ink=[], robot=[]) == [SQUARE]


def write_session(root: Path, name: str, turns: int) -> Path:
    d = root / name
    d.mkdir(parents=True)
    meta = {"turn": turns, "exchanges": turns, "length": "medium", "turns": [], "history": []}
    (d / "turn-00-start.jpg").write_bytes(b"jpg"); (d / "turn-00-start-frame.jpg").write_bytes(b"jpg")
    prev_ink = []
    for n in range(1, turns + 1):
        mark = [(20.0 + 10 * n, 100.0 + 10 * n), (60.0 + 10 * n, 100.0 + 10 * n)]     # each turn's mark on its own row
        plan = [(20.0 + 10 * n, 120.0 + 5 * n), (60.0 + 10 * n, 120.0 + 5 * n)]
        ink = prev_ink + [mark]
        (d / f"plan-{n:02d}.svg").write_text(HEAD + "".join(path(pl, "#222") for pl in ink) + path(plan, "green", dashed=True) + "</svg>")
        for who in ("human", "robot"):
            (d / f"turn-{n:02d}-{who}.jpg").write_bytes(b"jpg"); (d / f"turn-{n:02d}-{who}-frame.jpg").write_bytes(b"jpg")
        meta["turns"].append({"turn": n, "artist": "mimic" if n % 2 else "haring", "source": "ink" if n % 2 else "claude",
                              "latency_s": 0.0 if n % 2 else 7.1, "coverage": 0.05 * n, "planned_mm": 40, "color": "green",
                              "sees": f"Seen {n}.", "adds": f"Added {n}."})
        prev_ink = ink
    (d / "session.json").write_text(json.dumps(meta))
    return d


def test_longest_session_picks_the_most_turns_and_skips_folders_without_a_record(tmp_path):
    write_session(tmp_path, "20260919-100000", 3)
    write_session(tmp_path, "20260919-120000", 7)
    write_session(tmp_path, "20260919-140000", 7)
    (tmp_path / "current.json").write_text("{}")
    (tmp_path / "20260919-150000").mkdir()
    assert build.longest_session(tmp_path).name == "20260919-140000"
    with pytest.raises(SystemExit):
        build.longest_session(tmp_path / "nowhere")


def test_replay_data_carries_turns_words_new_ink_plans_frames_and_the_calibration(tmp_path):
    d = write_session(tmp_path, "20260919-120000", 2)
    data = build.replay_data(d, CALIB, words={2: ("A thought.", "A quip!")})
    assert data["session"] == "20260919-120000" and data["base"] == "sessions/20260919-120000"
    assert data["exchanges"] == 2 and data["length"] == "medium" and data["video"] is None
    assert data["calib"]["image_size"] == [1280, 720] and data["calib"]["cam_to_robot"]["ax"] == 0.97
    assert data["frames"] == {"start": True, "final": False}
    t1, t2 = data["turns"]
    assert t1["artist"] == "mimic" and t1["source"] == "ink" and "thought" not in t1
    assert t2["thought"] == "A thought." and t2["quip"] == "A quip!" and t2["latency_s"] == 7.1
    assert t1["new"] == [[[30.0, 110.0], [70.0, 110.0]]] and t2["new"] == [[[40.0, 120.0], [80.0, 120.0]]]   # only this turn's mark
    assert t1["plan"] == [[[30.0, 125.0], [70.0, 125.0]]] and t1["color"] == "#1b8f3a"
    assert t2["frames"] == {"human": True, "robot": True}


def test_rewrite_index_makes_assets_relative_and_adds_the_replay_meta():
    html = build.rewrite_index((build.STATIC / "index.html").read_text())
    assert '="/static/' not in html and 'href="static/duet.css' in html and 'src="static/js/app.js' in html
    assert '<meta name="duet-replay" content="replay.json">' in html and "<title>Duet · demo</title>" in html


def test_build_assembles_assets_presentation_and_a_demo_that_replays_the_session(tmp_path):
    d = write_session(tmp_path / "sessions", "20260919-120000", 2)
    out = tmp_path / "site"
    data = build.build(out, d, CALIB)
    assert (out / "assets" / "tokens.css").is_file() and (out / "assets" / "fredoka.css").is_file()
    assert (out / "presentation" / "index.html").is_file() and (out / "presentation" / "deck.js").is_file()
    assert not (out / "presentation" / "gen_images.py").exists()
    assert 'class="homelink pill" href="../"' in (out / "presentation" / "index.html").read_text()
    assert (out / "demo" / "static" / "js" / "replay.js").is_file()
    index = (out / "demo" / "index.html").read_text()
    assert 'content="replay.json"' in index and 'id="site-home" href="../"' in index
    assert (out / "demo" / "sessions" / "20260919-120000" / "plan-02.svg").is_file()
    written = json.loads((out / "demo" / "replay.json").read_text())
    assert written == data and len(written["turns"]) == 2
