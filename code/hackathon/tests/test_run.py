import asyncio
import os
import signal
from pathlib import Path

from duet import recorder, run
from duet.session import ARTISTS


def test_parser_defaults_and_fake_flags():
    a = run.build_parser().parse_args([])
    assert (a.fake, a.claude, a.port, a.artist, a.length, a.exchanges, a.handoff, a.replay) == (False, False, 8000, "abstract", "short", 5, "held", "20260918-190258")
    b = run.build_parser().parse_args(["--fake", "--claude", "--port", "8765", "--artist", "vangogh", "--length", "long",
                                       "--exchanges", "3", "--handoff", "dock", "--replay", "20260918-185927"])
    assert (b.fake, b.claude, b.port, b.artist, b.length, b.exchanges, b.handoff, b.replay) == (True, True, 8765, "vangogh", "long", 3, "dock", "20260918-185927")


def test_replay_boards_come_in_turn_order(tmp_path):
    for name in ("turn-00-start.jpg", "turn-02-human.jpg", "turn-01-human.jpg", "turn-01-robot.jpg", "turn-02-robot.jpg"):
        (tmp_path / name).write_bytes(b"")
    start, humans, robots = run.replay_paths(tmp_path)
    assert start.name == "turn-00-start.jpg"
    assert [p.name for p in humans] == ["turn-01-human.jpg", "turn-02-human.jpg"]
    assert [p.name for p in robots] == ["turn-01-robot.jpg", "turn-02-robot.jpg"]


def test_main_fake_wires_the_loop_and_shuts_down(tmp_path, monkeypatch):
    monkeypatch.setattr(run, "Recorder", lambda **kw: recorder.Recorder(root=tmp_path, **kw))
    seen: list[str] = []

    class SpyBus(run.EventBus):
        def emit(self, type, **data):
            if type == "state":
                seen.append(data["state"])
            return super().emit(type, **data)

    monkeypatch.setattr(run, "EventBus", SpyBus)
    args = run.build_parser().parse_args(["--fake", "--port", "0", "--exchanges", "1"])

    async def scenario():
        task = asyncio.create_task(run.main(args))
        async with asyncio.timeout(30):
            while "capture" not in seen:
                await asyncio.sleep(0.05)
        os.kill(os.getpid(), signal.SIGINT)      # what Ctrl-C does under uvicorn
        async with asyncio.timeout(15):
            await task

    asyncio.run(scenario())
    assert seen[:3] == ["start", "human_turn", "capture"], seen


def test_fake_visitor_reloads_the_recorded_piece_on_a_new_session(monkeypatch):
    monkeypatch.setattr(run.cv2, "imread", lambda p: Path(p).name)
    monkeypatch.setattr(run, "VISITOR_WAITS", (0.0, 0.0, 0.0))

    class Frames:
        def __init__(self):
            self.shown, self.robot_boards = [], []

        def show_board(self, board):
            self.shown.append(board)

        def jitter(self, seconds):
            pass

    class Sess:
        passes = 0

        def pass_turn(self):
            self.passes += 1

    async def scenario():
        bus = run.EventBus()
        frames, session = Frames(), Sess()
        task = asyncio.create_task(run.fake_visitor(bus, frames, Path("s/turn-00-start.jpg"), [Path("s/turn-01-human.jpg")],
                                                    [Path("s/turn-01-robot.jpg")], session))
        await asyncio.sleep(0)
        bus.emit("state", state="start", session="a")
        bus.emit("state", state="human_turn", session="a")
        await asyncio.sleep(0.05)
        bus.emit("state", state="human_turn", session="a")        # out of recorded turns: no Go
        await asyncio.sleep(0.05)
        bus.emit("state", state="start", session="b")
        bus.emit("state", state="human_turn", session="b")
        await asyncio.sleep(0.05)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        return frames, session
    frames, session = asyncio.run(scenario())
    assert frames.shown == ["turn-00-start.jpg", "turn-01-human.jpg", "turn-00-start.jpg", "turn-01-human.jpg"]
    assert session.passes == 2 and frames.robot_boards == ["turn-01-robot.jpg"]


def test_every_artist_is_a_choice_on_the_command_line():
    for a in ARTISTS:
        assert run.build_parser().parse_args(["--artist", a]).artist == a


def test_no_guard_runs_the_loop_with_the_hand_guard_off(tmp_path, monkeypatch):
    monkeypatch.setattr(run, "Recorder", lambda **kw: recorder.Recorder(root=tmp_path, **kw))
    guards: list[str] = []

    class SpyBus(run.EventBus):
        def emit(self, type, **data):
            if type == "state":
                guards.append(data["hand_guard"])
            return super().emit(type, **data)

    monkeypatch.setattr(run, "EventBus", SpyBus)
    assert run.build_parser().parse_args([]).no_guard is False
    args = run.build_parser().parse_args(["--fake", "--port", "0", "--exchanges", "1", "--no-guard"])

    async def scenario():
        task = asyncio.create_task(run.main(args))
        async with asyncio.timeout(30):
            while not guards:
                await asyncio.sleep(0.05)
        os.kill(os.getpid(), signal.SIGINT)
        async with asyncio.timeout(15):
            await task

    asyncio.run(scenario())
    assert set(guards) == {"off"}, guards
