import asyncio
import json

import pytest

from duet import config as cfg
from duet.fakes import FakeBrain, FakeController, FakeFrames
from duet.recorder import Recorder
from duet.session import ARTISTS, EventBus, HandGuard, Session, Settings


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
    assert kinds[:2] == ["lift_if_low", "go_look"] and kinds.count("draw") == 2   # lift check, look, then the plan and the signature
    for name in ("turn-00-start.jpg", "turn-00-start-frame.jpg", "turn-01-human.jpg", "turn-01-human-frame.jpg",
                 "turn-01-robot.jpg", "turn-01-final.jpg", "turn-01-final-frame.jpg", "plan-01.svg", "session.mp4"):
        assert (rec.dir / name).exists(), name
    shot = next(e for e in events if e["type"] == "shot")
    assert shot["who"] == "start" and shot["frame_url"].endswith("turn-00-start-frame.jpg")
    human_shot = next(e for e in events if e["type"] == "shot" and e["who"] == "human")
    assert human_shot["turn"] == 1
    meta = json.loads((rec.dir / "session.json").read_text())
    assert meta["turn"] == 1 and meta["exchanges"] == 1 and meta["history"][0]["source"] == "fake"
    assert meta["history"][0]["sees"].startswith("A creature")
    types = [e["type"] for e in events]
    for t in ("state", "human", "interpretation", "plan", "progress", "shot", "video"):
        assert t in types, t
    interp = next(e for e in events if e["type"] == "interpretation")
    assert interp["quip"] == "What a creature! Here comes the sun." and interp["source"] == "fake"
    assert interp["thought"] == "Is that a creature waking up?"
    assert interp["turn"] == 1
    human = next(e for e in events if e["type"] == "human")
    assert 10 <= len(human["new"]) <= 16
    assert human["turn"] == 1
    xs = [x for pl in human["new"] for x, _ in pl]
    assert 30 <= min(xs) <= 45 and 130 <= max(xs) <= 145              # robot-board mm (cam_to_robot applied)
    assert [e["turn"] for e in events if e["type"] == "progress"] == [1] * sum(e["type"] == "progress" for e in events)
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
        async def propose(self, board, human_cam, history, length, exchange, total, artist="haring"):
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
    s, frames, ctl, *_ = build(tmp_path, look_frame, exchange_start, calibration)
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
    assert state["direction"] == 45 and state["energy"] == 0.8 and state["artists"] == list(ARTISTS)
    for a in ARTISTS:
        assert s.update_settings(artist=a).artist == a
    s.update_settings(handoff="dock")                     # the arm's held flag follows the page's Marker toggle
    assert ctl.held_mode is False
    s.update_settings(handoff="held")
    assert ctl.held_mode is True
    s.state = "robot_draw"                                # a Marker click mid-draw must not reach the arm
    with pytest.raises(ValueError):
        s.update_settings(handoff="dock")
    s.state = "idle"


def test_pause_during_the_robot_turn_stops_the_arm_and_resume_finishes(tmp_path, look_frame, exchange_start, exchange_human, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held", artist="haring")
        ctl.stroke_s = 0.15                             # haring's passes and ticks make a plan long enough to pause in the middle of
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
        held_id0, held_frame0 = s.held_id, s.held_frame
        frames.show_hand(True)
        frames.show_board(exchange_human)
        await s._capture_board()
        assert s.guard.reference is ref0                # the hand frame was refused
        assert s.held_id == held_id0 and s.held_frame is held_frame0   # the held still is unchanged too
        frames.show_hand(False)
        await s._capture_board()
        assert s.guard.reference is not ref0            # a clean frame refreshes it
        assert s.held_id != held_id0                    # ...and so does the held still
        await cancel(task)
        return s, drain(q)
    s, events = asyncio.run(scenario())
    assert any(e["type"] == "error" and "reference" in e["message"] for e in events)


def test_a_hung_recover_times_out_and_stays_paused(tmp_path, look_frame, exchange_start, calibration, monkeypatch):
    from duet import session as session_mod
    monkeypatch.setattr(session_mod, "RECOVER_TIMEOUT_S", 0.2)

    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")

        async def hang():
            ctl.calls.append(("recover",))
            await asyncio.sleep(10)
        ctl.recover = hang
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        await s.pause()
        await until_state(s, "paused")
        s.resume()
        await asyncio.sleep(0.6)
        state, err = s.state, s.last_error
        await cancel(task)
        return state, err, drain(q)
    state, err, events = asyncio.run(scenario())
    assert state == "paused" and "recover timed out" in err
    assert any(e["type"] == "error" and "recover timed out" in e["message"] for e in events)


def test_restart_after_finished_begins_a_new_piece_in_place(tmp_path, look_frame, exchange_start, exchange_human, exchange_robot, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held")
        frames.robot_boards = [exchange_robot, exchange_robot]
        task = asyncio.create_task(s.run_forever())
        await until_state(s, "human_turn")
        frames.show_board(exchange_human)
        s.pass_turn()
        await until_state(s, "finished")
        first_dir = s.rec.dir
        s.restart()
        await until_seen(s, "start", count=2)
        await until_seen(s, "human_turn", count=2)
        drain(q)
        snapshot = [m["type"] for m in s.bus.snapshot()]
        await cancel(task)
        return s, first_dir, snapshot
    s, first_dir, snapshot = asyncio.run(scenario())
    assert s.rec.dir != first_dir and s.turn == 0 and s.history == [] and s.human_ink == []
    assert "plan" not in snapshot and "interpretation" not in snapshot           # the finished piece left the snapshot
    assert "state" in snapshot and "shot" in snapshot                             # the new start photo is there


def test_reset_arm_stops_recovers_returns_to_the_look_pose_and_keeps_the_turn(tmp_path, look_frame, exchange_start, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=3, handoff="held")
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        await s.reset_arm()
        async with asyncio.timeout(10):
            while [c[0] for c in ctl.calls].count("go_look") < 2 or s.state != "human_turn":
                await asyncio.sleep(0.01)
        await cancel(task)
        return s, ctl, drain(q)
    s, ctl, events = asyncio.run(scenario())
    kinds = [c[0] for c in ctl.calls]
    assert kinds.index("stop") < kinds.index("recover") < len(kinds) - 1 - kinds[::-1].index("go_look")
    assert s.turn == 0 and s.state == "human_turn" and s.at_look
    assert not any(e["type"] == "error" for e in events)


def test_reset_arm_also_works_while_paused(tmp_path, look_frame, exchange_start, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=3, handoff="held")
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        await s.pause()
        await until_state(s, "paused")
        await s.reset_arm()
        async with asyncio.timeout(10):
            while [c[0] for c in ctl.calls].count("go_look") < 2 or s.state != "human_turn":
                await asyncio.sleep(0.01)
        await cancel(task)
        return s, ctl
    s, ctl = asyncio.run(scenario())
    kinds = [c[0] for c in ctl.calls]
    assert kinds.count("go_look") == 2 and s.state == "human_turn" and s.turn == 0


def test_the_bus_snapshots_feed_right_after_state():
    bus = EventBus()
    bus.emit("state", state="idle", turn=0)
    bus.emit("feed", source="live")
    bus.emit("plan", polylines=[])
    assert [m["type"] for m in bus.snapshot()] == ["state", "feed", "plan"]


def test_the_first_move_is_held_on_the_latest_live_frame(tmp_path, look_frame, exchange_start, calibration):
    s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1)
    seen = []

    async def go_look():
        seen.append(("go_look", s.held_frame is not None))

    async def lift_if_low():
        seen.append(("lift_if_low", s.held_frame is not None))
    ctl.go_look, ctl.lift_if_low = go_look, lift_if_low
    asyncio.run(s._state_start())
    assert seen == [("lift_if_low", True), ("go_look", True)] and s.held_frame is not None   # held before the first move of all


def test_end_during_the_human_turn_signs_and_finishes(tmp_path, look_frame, exchange_start, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=3, handoff="held")
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        assert s.held_frame is not None
        before = drain(q)          # everything up to human_turn, none of it carrying the End flag yet
        s.end()
        await asyncio.wait_for(task, 60)
        return s, ctl, before, drain(q)
    s, ctl, before, events = asyncio.run(scenario())
    assert s.states_seen == ["start", "human_turn", "finish", "finished"]
    assert [c[0] for c in ctl.calls].count("draw") == 1            # the signature only
    assert any(e["type"] == "state" and e["ending"] for e in events)
    assert not any(e["type"] == "state" and e["ending"] for e in before)   # the flag is off until End
    assert (s.rec.dir / "turn-00-final.jpg").exists()


def test_end_during_the_robot_turn_finishes_after_the_look_photo(tmp_path, look_frame, exchange_start, exchange_human, exchange_robot, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=3, handoff="held", artist="haring")
        ctl.stroke_s = 0.15
        frames.robot_boards = [exchange_robot]
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        frames.show_board(exchange_human)
        s.pass_turn()
        await until_state(s, "robot_draw")
        s.end()
        await asyncio.wait_for(task, 60)
        return s, ctl, drain(q)
    s, ctl, events = asyncio.run(scenario())
    assert s.states_seen == ["start", "human_turn", "capture", "interpret", "plan", "robot_draw", "look", "finish", "finished"]
    assert [c[0] for c in ctl.calls].count("draw") == 2            # the plan, then the signature
    assert s.turn == 1


def test_end_while_paused_acts_on_resume(tmp_path, look_frame, exchange_start, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=3, handoff="held")
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        await s.pause()
        await until_state(s, "paused")
        s.end()
        s.resume()
        await asyncio.wait_for(task, 60)
        return s
    s = asyncio.run(scenario())
    # the doubled human_turn is the existing pause bookkeeping: the state returns "human_turn" when
    # the loop notices it is paused, and only then does the run loop itself set "paused".
    assert s.states_seen == ["start", "human_turn", "human_turn", "paused", "human_turn", "finish", "finished"]


def test_reset_clears_the_end_flag_so_the_next_piece_runs_its_exchanges(tmp_path, look_frame, exchange_start, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=3, handoff="held")
        task = asyncio.create_task(s.run_forever())
        await until_state(s, "human_turn")
        s.end()
        await until_state(s, "finished")
        s.bus.emit("feed", source="live")               # the rig's picture source must survive the piece reset
        s.restart()
        await until_seen(s, "human_turn", count=2)
        await asyncio.sleep(0.1)                        # the new piece stays in the human turn; it does not finish at once
        state, ending = s.state, s.ending
        await cancel(task)
        return s, state, ending
    s, state, ending = asyncio.run(scenario())
    assert ending is False and state == "human_turn"
    assert s.states_seen[-2:] == ["start", "human_turn"]
    assert "feed" in s.bus.last and "plan" not in s.bus.last


def test_the_artist_is_fixed_when_the_mark_is_captured(tmp_path, look_frame, exchange_start, exchange_human, exchange_robot, calibration):
    class WaitingBrain(FakeBrain):
        def __init__(self):
            super().__init__()
            self.go, self.artists = asyncio.Event(), []

        async def propose(self, board, human_cam, history, length, exchange, total, artist="haring"):
            self.artists.append(artist)
            await self.go.wait()
            return await super().propose(board, human_cam, history, length, exchange, total, artist)

    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held", artist="abstract")
        s.brain = WaitingBrain()
        frames.robot_boards = [exchange_robot]
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        frames.show_board(exchange_human)
        s.pass_turn()
        await until_state(s, "interpret")
        s.update_settings(artist="haring")        # picked for the next turn while this one is being thought about
        s.brain.go.set()
        await asyncio.wait_for(task, 60)
        return s, rec, drain(q)
    s, rec, events = asyncio.run(scenario())
    assert s.brain.artists == ["abstract"]
    interp = next(e for e in events if e["type"] == "interpretation")
    plan = next(e for e in events if e["type"] == "plan")
    assert interp["artist"] == "abstract" and plan["artist"] == "abstract"
    shots = {e["who"]: e for e in events if e["type"] == "shot"}
    assert shots["human"]["artist"] == "abstract" and shots["robot"]["artist"] == "abstract" and "artist" not in shots["start"]
    assert s.bus.last["state"]["artist"] == "haring"
    meta = json.loads((rec.dir / "session.json").read_text())
    assert next(t for t in meta["turns"] if t["turn"] == 1)["artist"] == "abstract"


def test_an_ink_artist_answers_without_the_brain(tmp_path, look_frame, exchange_start, exchange_human, exchange_robot, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1, handoff="held", artist="mimic")
        frames.robot_boards = [exchange_robot]
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        frames.show_board(exchange_human)
        s.pass_turn()
        await asyncio.wait_for(task, 60)
        return s, rec, drain(q)
    s, rec, events = asyncio.run(scenario())
    assert s.brain.n == 0
    interp = next(e for e in events if e["type"] == "interpretation")
    assert interp["source"] == "ink" and interp["artist"] == "mimic" and interp["quip"] == "Copycat!" and interp["latency_s"] == 0.0
    plan = next(e for e in events if e["type"] == "plan")
    assert plan["artist"] == "mimic" and plan["polylines"]
    meta = json.loads((rec.dir / "session.json").read_text())
    assert meta["history"][0]["source"] == "ink" and meta["history"][0]["adds"].endswith("shifted")
