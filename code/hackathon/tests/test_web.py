import numpy as np
from starlette.testclient import TestClient

from duet import web
from duet.camera import Frame
from duet.session import EventBus


class StubSession:
    state, turn, plan, at_look, color = "human_turn", 1, [], False, "green"

    def __init__(self):
        self.changes, self.actions = [], []

    def update_settings(self, **changes):
        if changes.get("length") == "bogus":
            raise ValueError("length must be short, medium or long")
        self.changes.append(changes)

    async def pause(self):
        self.actions.append("pause")

    def resume(self):
        self.actions.append("resume")

    def pass_turn(self):
        self.actions.append("pass")

    async def clear_error(self):
        self.actions.append("clear_error")


class StubFrames:
    def latest(self):
        return Frame(np.full((60, 80, 3), 128, np.uint8), None, 0.0)


def test_page_serves_with_dev_mode_and_data_el_names(tmp_path):
    app = web.make_app(StubSession(), StubFrames(), EventBus(), sessions_dir=tmp_path)
    with TestClient(app) as client:
        r = client.get("/")
        assert r.status_code == 200 and "<title>Duet" in r.text
        assert 'data-el="' in r.text and "dev-badge" in r.text
        assert "/stream.mjpg" in r.text and "/ws" in r.text


def test_ws_sends_the_snapshot_then_takes_commands(tmp_path):
    bus = EventBus()
    bus.emit("state", state="human_turn", turn=1)
    bus.emit("plan", polylines=[[[1, 1], [2, 2]]], color="#000")
    stub = StubSession()
    app = web.make_app(stub, StubFrames(), bus, sessions_dir=tmp_path)
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            first, second = ws.receive_json(), ws.receive_json()
            assert [first["type"], second["type"]] == ["state", "plan"]
            ws.send_json({"type": "set", "length": "medium", "exchanges": "4"})
            ws.send_json({"type": "set", "direction": "45", "energy": "0.7"})
            ws.send_json({"type": "pass"})
            ws.send_json({"type": "set", "length": "bogus"})
            err = ws.receive_json()
            assert err["type"] == "error" and "length" in err["message"]
            ws.send_json({"type": "set", "direction": "east"})
            assert "setting refused" in ws.receive_json()["message"]
            ws.send_json({"type": "nonsense"})
            assert ws.receive_json()["type"] == "error"
    assert stub.changes == [{"length": "medium", "exchanges": 4}, {"direction": 45.0, "energy": 0.7}]
    assert stub.actions == ["pass"]


def test_mjpeg_part_is_a_multipart_jpeg_chunk():
    part = web.mjpeg_part(np.full((60, 80, 3), 128, np.uint8))
    assert part.startswith(b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ")
    assert part.endswith(b"\r\n") and b"\xff\xd8" in part


def test_session_files_and_health_are_served(tmp_path):
    (tmp_path / "s1").mkdir()
    (tmp_path / "s1" / "turn-01-human.jpg").write_bytes(b"\xff\xd8\xff")
    app = web.make_app(StubSession(), StubFrames(), EventBus(), sessions_dir=tmp_path)
    with TestClient(app) as client:
        assert client.get("/sessions/s1/turn-01-human.jpg").status_code == 200
        assert client.get("/health").json()["state"] == "human_turn"
        assert client.get("/static/index.html").status_code == 200      # the static mount serves the page's own files


def test_calibration_is_served_and_leads_the_snapshot(tmp_path, calibration):
    bus = EventBus()
    bus.emit("state", state="idle", turn=0)
    app = web.make_app(StubSession(), StubFrames(), bus, sessions_dir=tmp_path, calibration=calibration)
    with TestClient(app) as client:
        cal = client.get("/calibration.json").json()
        assert cal["marks_image"] == calibration["marks_image"] and cal["board_mm"] == [176.0, 240.0]
        assert cal["image_size"] == [1280, 720] and cal["cam_to_robot"] == calibration["cam_to_robot"]
        with client.websocket_connect("/ws") as ws:
            assert [ws.receive_json()["type"], ws.receive_json()["type"]] == ["calib", "state"]
