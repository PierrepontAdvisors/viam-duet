import json
import os

import numpy as np
import pytest

import duet.recorder as recorder
from duet.recorder import Recorder, video_duration_s, video_size


def frame(shade):
    """A portrait board photo, like the warped 704 x 960 boards."""
    return np.full((128, 96, 3), shade, np.uint8)


def raw(shade):
    """A landscape camera frame, like the 1280 x 720 look-pose frames."""
    return np.full((96, 128, 3), shade, np.uint8)


def test_photos_svgs_and_json_land_in_the_session_folder(tmp_path):
    rec = Recorder("abc", root=tmp_path, settings={"length": "short", "exchanges": 3})
    p0 = rec.save_photo(0, "start", frame(240))
    p1 = rec.save_photo(1, "human", frame(200))
    rec.save_svg(1, "<svg/>")
    rec.record_turn(1, sees="A line.", adds="A sun.", source="claude")
    rec.record_turn(1, coverage=0.02)
    rec.set_turn(1)
    rec.write()
    assert p0.name == "turn-00-start.jpg" and p1.name == "turn-01-human.jpg"
    assert rec.latest_photo == p1
    assert (tmp_path / "abc" / "plan-01.svg").read_text() == "<svg/>"
    meta = json.loads((tmp_path / "abc" / "session.json").read_text())
    assert meta["id"] == "abc" and meta["length"] == "short" and meta["exchanges"] == 3
    assert meta["turn"] == 1 and meta["last_photo"] == "turn-01-human.jpg" and meta["started"] == "abc"
    assert meta["history"] == [{"sees": "A line.", "adds": "A sun.", "source": "claude"}]
    assert meta["turns"] == [{"turn": 1, "sees": "A line.", "adds": "A sun.", "source": "claude", "coverage": 0.02}]
    assert json.loads((tmp_path / "current.json").read_text())["id"] == "abc"


def test_stitch_makes_a_video_one_second_per_turn_with_the_last_held(tmp_path):
    rec = Recorder("vid", root=tmp_path)
    for i, shade in enumerate((240, 200, 160)):
        rec.save_photo(i, "robot", frame(shade))
    out = rec.stitch()
    assert out is not None and out.exists() and out.stat().st_size > 1000
    assert abs(video_duration_s(out) - 4.0) < 0.35     # 1 + 1 + 2 s hold on the last frame


def test_stitch_with_no_photos_is_none(tmp_path):
    assert Recorder("empty", root=tmp_path).stitch() is None


def test_camera_frames_are_saved_beside_the_photos_and_make_a_landscape_video(tmp_path):
    rec = Recorder("fr", root=tmp_path)
    for i, shade in enumerate((240, 200, 160)):
        rec.save_photo(i, "robot", frame(shade), frame=raw(shade))
    assert (tmp_path / "fr" / "turn-01-robot-frame.jpg").exists()
    assert rec.latest_frame.name == "turn-02-robot-frame.jpg" and rec.latest_photo.name == "turn-02-robot.jpg"
    out = rec.stitch()
    assert video_size(out) == (128, 96)                    # the landscape frames, not the portrait photos
    assert abs(video_duration_s(out) - 4.0) < 0.35
    rec.save_photo(3, "final", frame(120))                  # a turn without a frame: the stitch falls back to photos
    assert rec.latest_frame is None and video_size(rec.stitch()) == (96, 128)


def test_stitch_with_a_single_photo_holds_for_the_full_duration(tmp_path):
    rec = Recorder("one", root=tmp_path)
    rec.save_photo(0, "start", frame(240))
    out = rec.stitch()
    assert abs(video_duration_s(out) - 2.0) < 0.35


def test_stitch_honors_custom_frame_and_hold_durations(tmp_path):
    rec = Recorder("custom", root=tmp_path)
    for i, shade in enumerate((240, 220, 200, 180)):
        rec.save_photo(i, "robot", frame(shade))
    out = rec.stitch(per_frame_s=0.5, hold_last_s=1.0)
    assert abs(video_duration_s(out) - 2.5) < 0.15


def test_stitch_failure_is_swallowed(tmp_path, monkeypatch):
    rec = Recorder("boom", root=tmp_path)
    rec.save_photo(0, "start", frame(240))
    monkeypatch.setattr(recorder, "FFMPEG", "/nonexistent/ffmpeg")
    assert rec.stitch() is None


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores the mode")
def test_save_photo_into_a_read_only_dir_raises(tmp_path):
    ro = Recorder("ro", root=tmp_path)
    ro.dir.chmod(0o500)
    try:
        with pytest.raises(OSError):
            ro.save_photo(0, "start", frame(240))
    finally:
        ro.dir.chmod(0o700)


def test_current_json_follows_the_newest_session(tmp_path):
    a = Recorder("a", root=tmp_path)
    a.write()
    b = Recorder("b", root=tmp_path)
    b.write()
    a.write()  # a's finally, after b has taken over
    assert json.loads((tmp_path / "current.json").read_text())["id"] == "b"
