import asyncio

import numpy as np
from starlette.testclient import TestClient

from duet import vision, web
from duet.camera import Frame
from duet.session import EventBus


class StubSession:
    state, turn, at_look, color, held_frame, held_id, ending = "human_turn", 1, True, "green", None, 0, False

    def __init__(self):
        self.changes, self.actions = [], []
        self.raise_on_clear = False
        self.plan = []

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

    def end(self):
        self.actions.append("end")

    def restart(self):
        self.actions.append("restart")

    async def reset_arm(self):
        self.actions.append("reset_arm")

    async def clear_error(self):
        if self.raise_on_clear:
            raise RuntimeError("arm offline")
        self.actions.append("clear_error")


class StubFrames:
    def __init__(self):
        self.t = 0.0
        self.gone = False

    def latest(self):
        return None if self.gone else Frame(np.full((60, 80, 3), 128, np.uint8), None, self.t)


def receive(ws) -> dict:
    """The next message that is not the feed watcher's: it emits `feed` on its first tick, before any page
    connects, so a fresh bus's snapshot already carries one."""
    while True:
        m = ws.receive_json()
        if m["type"] != "feed":
            return m


def test_page_serves_with_dev_mode_and_data_el_names(tmp_path):
    app = web.make_app(StubSession(), StubFrames(), EventBus(), sessions_dir=tmp_path)
    with TestClient(app) as client:
        r = client.get("/")
        assert r.status_code == 200 and "<title>Duet" in r.text
        assert 'data-el="' in r.text and "dev-badge" in r.text
        assert "/stream.mjpg" in r.text and "/ws" in r.text
        assert "m.handoff !== 'held'" not in r.text      # Pass is the operator's escape in both handoff modes


def test_ws_sends_the_snapshot_then_takes_commands(tmp_path):
    bus = EventBus()
    bus.emit("state", state="human_turn", turn=1)
    bus.emit("plan", polylines=[[[1, 1], [2, 2]]], color="#000")
    stub = StubSession()
    app = web.make_app(stub, StubFrames(), bus, sessions_dir=tmp_path)
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            first, second = receive(ws), receive(ws)
            assert [first["type"], second["type"]] == ["state", "plan"]
            ws.send_json({"type": "set", "length": "medium", "exchanges": "4"})
            ws.send_json({"type": "set", "direction": "45", "energy": "0.7"})
            ws.send_json({"type": "pass"})
            ws.send_json({"type": "pause"})
            ws.send_json({"type": "resume"})
            ws.send_json({"type": "clear_error"})
            ws.send_json({"type": "set", "length": "bogus"})
            err = receive(ws)
            assert err["type"] == "error" and "length" in err["message"]
            ws.send_json({"type": "set", "direction": "east"})
            assert "setting refused" in receive(ws)["message"]
            ws.send_json({"type": "end"})
            ws.send_json({"type": "restart"})
            ws.send_json({"type": "nonsense"})
            err2 = receive(ws)
            assert err2["type"] == "error" and "nonsense" in err2["message"]
    assert stub.changes == [{"length": "medium", "exchanges": 4}, {"direction": 45.0, "energy": 0.7}]
    assert stub.actions == ["pass", "pause", "resume", "clear_error", "end", "restart"]


def test_a_failing_command_answers_with_an_error_and_the_socket_lives(tmp_path):
    stub = StubSession()
    stub.raise_on_clear = True
    app = web.make_app(stub, StubFrames(), EventBus(), sessions_dir=tmp_path)
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_json({"type": "clear_error"})
            err = receive(ws)
            assert err["type"] == "error" and "arm offline" in err["message"]
            ws.send_json({"type": "pass"})                    # the socket still answers afterwards
            ws.send_json({"type": "nonsense"})
            assert receive(ws)["type"] == "error"
    assert stub.actions == ["pass"]


def test_reset_arm_command_reaches_the_session(tmp_path):
    bus = EventBus()
    bus.emit("state", state="human_turn", turn=1)
    stub = StubSession()
    app = web.make_app(stub, StubFrames(), bus, sessions_dir=tmp_path)
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            receive(ws)
            ws.send_json({"type": "reset_arm"})
            ws.send_json({"type": "pass"})
    assert stub.actions == ["reset_arm", "pass"]


def test_a_late_joiner_gets_the_feed_in_its_snapshot_after_state(tmp_path):
    bus = EventBus()
    bus.emit("state", state="human_turn", turn=1)
    app = web.make_app(StubSession(), StubFrames(), bus, sessions_dir=tmp_path)
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            first, second = ws.receive_json(), ws.receive_json()
            assert first["type"] == "state" and second == {"type": "feed", "source": "live"}


def test_two_clients_get_the_same_snapshot_and_both_unsubscribe(tmp_path):
    bus = EventBus()
    bus.emit("state", state="human_turn", turn=1)
    app = web.make_app(StubSession(), StubFrames(), bus, sessions_dir=tmp_path)
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as a, client.websocket_connect("/ws") as b:
            assert a.receive_json() == b.receive_json() == {"type": "state", "state": "human_turn", "turn": 1}
    assert len(bus.subs) == 0


def test_overlay_maps_robot_mm_back_through_the_calibration(look_frame, calibration):
    quad = vision.board_quad(np.array(calibration["marks_image"], np.float32), calibration["board_tl_index"])
    h_inv = np.linalg.inv(vision.board_homography(quad))
    plan = [[(30, 30), (150, 30)], [(88, 40), (88, 200)]]
    out = web.overlay(look_frame, plan, h_inv, (0, 0, 255), calibration.get("cam_to_robot"))
    assert out.shape == look_frame.shape and not np.array_equal(out, look_frame)
    assert np.array_equal(web.overlay(look_frame, [], h_inv, (0, 0, 255), calibration.get("cam_to_robot")), look_frame)


def test_render_plan_draws_on_the_held_still_and_on_live_at_the_look_pose(look_frame, calibration):
    quad = vision.board_quad(np.array(calibration["marks_image"], np.float32), calibration["board_tl_index"])
    h_inv = np.linalg.inv(vision.board_homography(quad))
    cam = calibration.get("cam_to_robot")
    s = StubSession()
    s.plan = [[(30, 30), (150, 30)]]
    assert not np.array_equal(web.render_plan(s, look_frame, "live", h_inv, cam), look_frame)
    s.at_look = False
    assert np.array_equal(web.render_plan(s, look_frame, "live", h_inv, cam), look_frame)
    assert not np.array_equal(web.render_plan(s, look_frame, "held", h_inv, cam), look_frame)
    s.plan = []
    assert np.array_equal(web.render_plan(s, look_frame, "live", h_inv, cam), look_frame)
    assert np.array_equal(web.render_plan(s, look_frame, "held", h_inv, cam), look_frame)


def test_mjpeg_part_is_a_multipart_jpeg_chunk():
    part = web.mjpeg_part(np.full((60, 80, 3), 128, np.uint8))
    assert part.startswith(b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ")
    assert part.endswith(b"\r\n") and b"\xff\xd8" in part


def test_feed_pick_holds_the_still_away_from_the_look_pose_and_freezes_when_stale():
    s, frames = StubSession(), StubFrames()
    still = np.zeros((60, 80, 3), np.uint8)
    assert web.feed_pick(s, frames)[0] == "live"
    s.held_frame, s.held_id = still, 7
    assert web.feed_pick(s, frames)[0] == "live"                   # a still is only shown while the arm is away
    s.at_look = False
    source, img, key = web.feed_pick(s, frames)
    assert source == "held" and img is still and key == ("held", 7)
    s.held_frame = None
    assert web.feed_pick(s, frames)[0] == "live"                   # no still yet: the first move shows what there is
    frames.gone = True
    assert web.feed_pick(s, frames) == ("stale", None, None)
    s.at_look = True
    assert web.feed_pick(s, frames) == ("stale", None, None)


def test_the_stream_sends_only_new_pictures_and_nothing_while_stale():
    s, frames = StubSession(), StubFrames()
    seen, parts = [], []
    gen = web.mjpeg(s, frames, lambda s, img, source: seen.append(source) or img, period_s=0.005)

    async def scenario():
        async def pump():
            async for part in gen:
                parts.append(part)
        task = asyncio.create_task(pump())
        await asyncio.sleep(0.05)
        n1 = len(parts)                                            # one live frame; the same frame is not resent
        frames.t = 1.0
        await asyncio.sleep(0.05)
        n2 = len(parts)
        frames.gone = True
        await asyncio.sleep(0.05)
        n3 = len(parts)                                            # stale: nothing sent, the browser keeps its last image
        s.at_look, s.held_frame, s.held_id = False, np.full((60, 80, 3), 7, np.uint8), 1
        await asyncio.sleep(0.05)
        n4 = len(parts)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        return n1, n2, n3, n4
    counts = asyncio.run(scenario())
    assert counts == (1, 2, 2, 3)
    assert parts[0].startswith(b"--frame\r\nContent-Type: image/jpeg") and parts[2] != parts[0]
    assert seen == ["live", "live", "held"]
    assert not hasattr(web, "no_frame_part")


def test_a_client_joining_while_held_gets_the_still_on_its_first_tick():
    s = StubSession()
    s.at_look = False
    s.held_frame, s.held_id = np.full((60, 80, 3), 5, np.uint8), 3
    frames = StubFrames()
    seen, parts = [], []
    gen = web.mjpeg(s, frames, lambda s, img, source: seen.append(source) or img, period_s=0.005)

    async def scenario():
        async def pump():
            async for part in gen:
                parts.append(part)
        task = asyncio.create_task(pump())
        await asyncio.sleep(0.05)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    asyncio.run(scenario())
    assert len(parts) == 1
    assert seen == ["held"]


def test_the_keepalive_resends_the_current_picture():
    s, frames = StubSession(), StubFrames()
    parts = []
    gen = web.mjpeg(s, frames, lambda s, img, source: img, period_s=0.005, keepalive_s=0.03)

    async def scenario():
        async def pump():
            async for part in gen:
                parts.append(part)
        task = asyncio.create_task(pump())
        await asyncio.sleep(0.1)
        n1 = len(parts)
        frames.gone = True                 # stale: no resend while nothing is available
        await asyncio.sleep(0.1)
        n2 = len(parts)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        return n1, n2
    n1, n2 = asyncio.run(scenario())
    assert 2 <= n1 <= 5
    assert n2 == n1


def test_stream_size_scales_to_960_wide_and_leaves_smaller_frames_alone():
    big = web.stream_size(np.zeros((720, 1280, 3), np.uint8))
    assert big.shape == (540, 960, 3)
    small = np.zeros((360, 640, 3), np.uint8)
    assert web.stream_size(small) is small


def test_the_feed_watcher_emits_on_change_only():
    s, frames, bus = StubSession(), StubFrames(), EventBus()
    q = bus.subscribe()

    async def scenario():
        task = asyncio.create_task(web.watch_feed(s, frames, bus, period_s=0.005))
        await asyncio.sleep(0.03)
        frames.gone = True
        await asyncio.sleep(0.03)
        s.at_look, s.held_frame, s.held_id = False, np.zeros((60, 80, 3), np.uint8), 1
        await asyncio.sleep(0.03)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    asyncio.run(scenario())
    out = []
    while not q.empty():
        out.append(q.get_nowait())
    assert out == [{"type": "feed", "source": "live"}, {"type": "feed", "source": "stale"}, {"type": "feed", "source": "held"}]
    assert bus.last["feed"]["source"] == "held"


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
