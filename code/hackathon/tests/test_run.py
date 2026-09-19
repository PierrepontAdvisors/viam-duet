import asyncio
import os
import signal

from duet import recorder, run


def test_parser_defaults_and_fake_flags():
    a = run.build_parser().parse_args([])
    assert (a.fake, a.claude, a.port, a.artist, a.length, a.exchanges, a.handoff, a.replay) == (False, False, 8000, "haring", "short", 5, "held", "20260918-190258")
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
