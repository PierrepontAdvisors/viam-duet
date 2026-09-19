from duet import run


def test_parser_defaults_and_fake_flags():
    a = run.build_parser().parse_args([])
    assert (a.fake, a.claude, a.port, a.length, a.exchanges, a.handoff, a.replay) == (False, False, 8000, "short", 5, "held", "20260918-190258")
    b = run.build_parser().parse_args(["--fake", "--claude", "--port", "8765", "--length", "long", "--exchanges", "3",
                                       "--handoff", "dock", "--replay", "20260918-185927"])
    assert (b.fake, b.claude, b.port, b.length, b.exchanges, b.handoff, b.replay) == (True, True, 8765, "long", 3, "dock", "20260918-185927")


def test_replay_boards_come_in_turn_order(tmp_path):
    for name in ("turn-00-start.jpg", "turn-02-human.jpg", "turn-01-human.jpg", "turn-01-robot.jpg", "turn-02-robot.jpg"):
        (tmp_path / name).write_bytes(b"")
    start, humans, robots = run.replay_paths(tmp_path)
    assert start.name == "turn-00-start.jpg"
    assert [p.name for p in humans] == ["turn-01-human.jpg", "turn-02-human.jpg"]
    assert [p.name for p in robots] == ["turn-01-robot.jpg", "turn-02-robot.jpg"]
