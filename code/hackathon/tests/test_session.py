import asyncio
import json

import pytest

from duet import config as cfg
from duet.fakes import FakeBrain, FakeController, FakeFrames
from duet.recorder import Recorder
from duet.session import EventBus, HandGuard, Session, Settings


def drain(q):
    out = []
    while not q.empty():
        out.append(q.get_nowait())
    return out


def build(tmp_path, look_frame, exchange_start, calibration, **settings):
    frames = FakeFrames(look_frame, calibration)
    frames.show_board(exchange_start)
    ctl = FakeController(frames)
    st = Settings(**settings)
    rec = Recorder("t", root=tmp_path, settings=st.record())
    bus = EventBus()
    q = bus.subscribe()
    s = Session(st, frames, ctl, FakeBrain(), rec, bus, calibration, guard=HandGuard(frames, calibration), poll_s=0.01)
    return s, frames, ctl, rec, q


async def until_state(session, state, timeout=10):
    """Wait until the session is in `state` now (only for states that yield while in them)."""
    async with asyncio.timeout(timeout):
        while session.state != state:
            await asyncio.sleep(0.01)


async def until_seen(session, state, count=1, timeout=10):
    """Wait until `state` has been entered `count` times (capture runs the fake camera and vision without yielding)."""
    async with asyncio.timeout(timeout):
        while session.states_seen.count(state) < count:
            await asyncio.sleep(0.01)


async def cancel(task):
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


def test_one_full_exchange_on_the_real_day_1_boards(tmp_path, look_frame, exchange_start, exchange_human, exchange_robot, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")
        frames.robot_boards = [exchange_robot]          # what the fake arm "draws": the real robot photo
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        frames.show_board(exchange_human)               # the visitor drew the real creature
        s.pass_turn()
        await asyncio.wait_for(task, 60)
        return s, ctl, rec, drain(q)
    s, ctl, rec, events = asyncio.run(scenario())
    assert s.states_seen == ["start", "human_turn", "capture", "interpret", "plan", "robot_draw", "look", "finish", "finished"]
    kinds = [c[0] for c in ctl.calls]
    assert kinds[0] == "go_look" and kinds.count("draw") == 2       # the plan, then the signature
    for name in ("turn-00-start.jpg", "turn-00-start-frame.jpg", "turn-01-human.jpg", "turn-01-human-frame.jpg",
                 "turn-01-robot.jpg", "turn-01-final.jpg", "turn-01-final-frame.jpg", "plan-01.svg", "session.mp4"):
        assert (rec.dir / name).exists(), name
    shot = next(e for e in events if e["type"] == "shot")
    assert shot["who"] == "start" and shot["frame_url"].endswith("turn-00-start-frame.jpg")
    human_shot = next(e for e in events if e["type"] == "shot" and e["who"] == "human")
    assert human_shot["turn"] == 1
    meta = json.loads((rec.dir / "session.json").read_text())
    assert meta["turn"] == 1 and meta["exchanges"] == 1 and meta["history"][0]["source"] == "claude"
    assert meta["history"][0]["sees"].startswith("A creature")
    types = [e["type"] for e in events]
    for t in ("state", "human", "interpretation", "plan", "progress", "shot", "video"):
        assert t in types, t
    interp = next(e for e in events if e["type"] == "interpretation")
    assert interp["quip"] == "What a creature! Here comes the sun." and interp["source"] == "claude"
    assert interp["thought"] == "Is that a creature waking up?"
    assert interp["turn"] == 1
    human = next(e for e in events if e["type"] == "human")
    assert 10 <= len(human["new"]) <= 16
    assert human["turn"] == 1
    xs = [x for pl in human["new"] for x, _ in pl]
    assert 30 <= min(xs) <= 45 and 130 <= max(xs) <= 145              # robot-board mm (cam_to_robot applied)
    plan = next(e for e in events if e["type"] == "plan")
    assert plan["polylines"] and plan["color"] == cfg.COLOR_HEX["green"]
    assert plan["turn"] == 1
    assert ctl.drawn[0] == plan["polylines"][:len(ctl.drawn[0])]


def test_no_new_ink_returns_to_the_human_turn(tmp_path, look_frame, exchange_start, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        s.pass_turn()                                   # nothing was drawn
        await until_seen(s, "human_turn", count=2)
        await cancel(task)
        return s, ctl, drain(q)
    s, ctl, events = asyncio.run(scenario())
    assert s.states_seen[-3:] == ["human_turn", "capture", "human_turn"]
    assert not any(c[0] == "draw" for c in ctl.calls)
    assert any(e["type"] == "human" and e.get("found") is False for e in events)


def test_held_trigger_fires_from_the_frames_alone(tmp_path, look_frame, exchange_start, exchange_human, calibration, monkeypatch):
    monkeypatch.setattr(cfg, "HELD_QUIET_S", 0.3)
    monkeypatch.setattr(cfg, "TRIGGER_GRACE_S", 0.1)   # Trigger refuses a grace window as long as the quiet one
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        frames.jitter(0.2)                              # a hand moving over the board
        await asyncio.sleep(0.1)
        frames.show_board(exchange_human)
        await until_seen(s, "capture", timeout=5)       # fires 0.3 s after the scene settles, no pass needed
        await cancel(task)
        return s
    s = asyncio.run(scenario())
    assert "capture" in s.states_seen


def test_a_hand_over_the_board_blocks_the_capture_until_it_leaves(tmp_path, look_frame, exchange_start, exchange_human, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        frames.show_board(exchange_human)
        frames.show_hand(True)
        s.pass_turn()                                   # the operator passes while a hand is still over the board
        await until_seen(s, "human_turn", count=2)      # capture refused, back to the human turn
        assert not any(c[0] == "draw" for c in ctl.calls)
        frames.show_hand(False)
        s.pass_turn()
        await until_seen(s, "interpret")                # now the capture went through
        await cancel(task)
        return s, drain(q)
    s, events = asyncio.run(scenario())
    assert any(e["type"] == "error" and "hand" in e["message"] for e in events)
    assert s.states_seen.count("capture") == 2


def test_pause_and_resume_recover_the_arm(tmp_path, look_frame, exchange_start, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        await s.pause()
        await until_state(s, "paused")
        s.resume()
        await until_state(s, "human_turn")
        await cancel(task)
        return s, ctl
    s, ctl = asyncio.run(scenario())
    kinds = [c[0] for c in ctl.calls]
    assert "stop" in kinds and "recover" in kinds and kinds.index("stop") < kinds.index("recover")


def test_a_fault_in_the_brain_pauses_with_the_error_on_the_bus(tmp_path, look_frame, exchange_start, exchange_human, calibration):
    class BrokenBrain:
        async def propose(self, board, human_cam, history, length, exchange, total):
            raise RuntimeError("no network")

    async def scenario():
        frames = FakeFrames(look_frame, calibration)
        frames.show_board(exchange_start)
        bus = EventBus()
        q = bus.subscribe()
        st = Settings(exchanges=1, handoff="held")
        s = Session(st, frames, FakeController(frames), BrokenBrain(), Recorder("f", root=tmp_path, settings=st.record()),
                    bus, calibration, poll_s=0.01)
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        frames.show_board(exchange_human)
        s.pass_turn()
        await until_state(s, "paused")
        await cancel(task)
        return s, drain(q)
    s, events = asyncio.run(scenario())
    assert "no network" in s.last_error
    assert any(e["type"] == "error" and "no network" in e["message"] for e in events)


def test_settings_are_validated_at_the_boundary(tmp_path, look_frame, exchange_start, calibration):
    s, *_ = build(tmp_path, look_frame, exchange_start, calibration)
    with pytest.raises(ValueError):
        s.update_settings(length="huge")
    with pytest.raises(ValueError):
        s.update_settings(exchanges=21)
    with pytest.raises(ValueError):
        s.update_settings(direction=400)
    with pytest.raises(ValueError):
        s.update_settings(energy=1.5)
    new = s.update_settings(length="medium", exchanges=4, energy=0.8, direction=45)
    assert (new.exchanges, new.energy, new.direction) == (4, 0.8, 45)
    state = s.bus.last["state"]
    assert state["direction"] == 45 and state["energy"] == 0.8 and state["artists"] == ["haring"]


def test_pause_during_the_robot_turn_stops_the_arm_and_resume_finishes(tmp_path, look_frame, exchange_start, exchange_human, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")
        ctl.stroke_s = 0.15                             # slow enough to pause in the middle of the plan
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        frames.show_board(exchange_human)
        s.pass_turn()
        await until_state(s, "robot_draw")
        await asyncio.sleep(0.4)
        await s.pause()
        await until_state(s, "paused")
        s.resume()
        await asyncio.wait_for(task, 60)
        return s, ctl, drain(q)
    s, ctl, events = asyncio.run(scenario())
    assert ctl.calls.index(("stop",)) < ctl.calls.index(("recover",))
    assert "paused" in s.states_seen and s.states_seen[-1] == "finished"
    assert not any(e["type"] == "error" and "Aborted" in e["message"] for e in events)


def test_a_startup_fault_pauses_and_resume_retries(tmp_path, look_frame, exchange_start, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")
        ctl.fail_go_look_once = True                    # a latched arm error on the very first move
        task = asyncio.create_task(s.run())
        await until_state(s, "paused")
        assert "Emergency Stop" in s.last_error
        s.resume()
        await until_state(s, "human_turn")
        await cancel(task)
        return s, drain(q)
    s, events = asyncio.run(scenario())
    assert any(e["type"] == "error" and "Emergency Stop" in e["message"] for e in events)
    assert s.states_seen[:3] == ["start", "paused", "start"]


def test_a_hand_in_the_capture_does_not_become_the_reference(tmp_path, look_frame, exchange_start, exchange_human, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        ref0 = s.guard.reference
        frames.show_hand(True)
        frames.show_board(exchange_human)
        await s._capture_board()
        assert s.guard.reference is ref0                # the hand frame was refused
        frames.show_hand(False)
        await s._capture_board()
        assert s.guard.reference is not ref0            # a clean frame refreshes it
        await cancel(task)
        return s, drain(q)
    s, events = asyncio.run(scenario())
    assert any(e["type"] == "error" and "reference" in e["message"] for e in events)
