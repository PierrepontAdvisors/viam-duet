from duet.trigger import Event, Reading, Trigger


def r(t, hand=False, still=True, **dots):
    return Reading(t=t, hand=hand, still=still, dots=dots)


def run(trigger, readings):
    return [(x.t, trigger.update(x)) for x in readings]


def test_dock_fires_after_a_marker_leaves_and_returns_and_the_scene_settles():
    tr = Trigger("dock", quiet_s=1.5)
    events = run(tr, [r(0, green="home"), r(1, green="missing", still=False), r(2, green="missing"),
                      r(3, green="home"), r(4, green="home"), r(4.6, green="home")])
    assert [e for _, e in events if e] == [Event("fire")]
    assert events[-1][0] == 4.6


def test_dock_does_not_fire_if_no_marker_ever_left():
    tr = Trigger("dock", quiet_s=1.5)
    assert all(e is None for _, e in run(tr, [r(t, green="home") for t in range(10)]))


def test_dock_hand_or_motion_restarts_the_quiet_timer():
    tr = Trigger("dock", quiet_s=1.5)
    events = run(tr, [r(0, green="missing"), r(1, green="home"), r(2, green="home", hand=True),
                      r(3, green="home"), r(4, green="home"), r(4.4, green="home"), r(4.6, green="home")])
    assert [t for t, e in events if e == Event("fire")] == [4.6]


def test_dock_moved_marker_asks_for_a_reseat_then_fires_once_home():
    tr = Trigger("dock", quiet_s=1.0)
    events = run(tr, [r(0, green="missing"), r(1, green="moved"), r(2, green="moved"), r(3, green="missing"),
                      r(4, green="home"), r(5, green="home"), r(6, green="home")])
    assert [e for _, e in events if e] == [Event("reseat", ("green",)), Event("reseat_ok"), Event("fire")]


def test_dock_with_no_calibrated_dots_never_fires():
    tr = Trigger("dock", quiet_s=0.5)
    assert all(e is None for _, e in run(tr, [r(t) for t in range(6)]))


def test_held_fires_after_activity_then_quiet():
    tr = Trigger("held", quiet_s=2.0)
    events = run(tr, [r(0), r(1, still=False), r(2, hand=True), r(3), r(4), r(5), r(5.5)])
    assert [t for t, e in events if e == Event("fire")] == [5]


def test_held_never_fires_on_an_untouched_board():
    tr = Trigger("held", quiet_s=2.0)
    assert all(e is None for _, e in run(tr, [r(t) for t in range(10)]))


def test_reset_after_fire_requires_new_activity():
    tr = Trigger("held", quiet_s=1.0)
    events = run(tr, [r(0, still=False), r(1), r(2), r(3), r(4), r(5)])
    assert [t for t, e in events if e == Event("fire")] == [2]
