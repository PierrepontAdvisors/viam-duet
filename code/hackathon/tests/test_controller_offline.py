"""Offline checks of the controller's safety logic with stubbed Viam clients. No hardware."""
import asyncio

import pytest
from viam.proto.common import Pose, PoseInFrame

from duet import config as cfg
from duet import controller as C
from duet.calib import BoardToRobot
from duet.strokes import resample


class FakeMotion:
    def __init__(self, move_delay_s=0.01):
        self.calls = 0
        self.move_delay_s = move_delay_s
        self.refuse_call = None        # when set, exactly that call number returns False
        self.destinations = []         # every commanded PoseInFrame, in order
        self.stop_during_call = None   # when set, call controller.stop() from inside that move
        self.controller = None

    async def move(self, **kw):
        self.calls += 1
        self.destinations.append(kw["destination"])
        if self.calls == self.stop_during_call:
            await self.controller.stop()
        await asyncio.sleep(self.move_delay_s)
        return self.calls != self.refuse_call

    async def get_pose(self, **kw):
        return PoseInFrame(reference_frame="world", pose=Pose(x=0, y=0, z=1, o_x=0, o_y=0, o_z=-1, theta=0))


class FakeArm:
    def __init__(self, stop_error=None):
        self.stopped = 0
        self.commands = []
        self.stop_error = stop_error

    async def do_command(self, cmd):
        self.commands.append(cmd)
        return {}

    async def stop(self):
        self.stopped += 1
        if self.stop_error is not None:
            raise self.stop_error


class FakeGripper:
    def __init__(self, grab_result=True):
        self.grab_result = grab_result
        self.commands = []

    async def do_command(self, cmd):
        self.commands.append(cmd)
        return {}

    async def grab(self):
        return self.grab_result


def down(x, y, z):
    return Pose(x=x, y=y, z=z, o_x=0, o_y=0, o_z=-1, theta=0)


SQUARE = [(100, 100), (160, 100), (160, 160), (100, 160), (100, 100)]
SHORT = [(100, 100), (104, 100)]   # two waypoints: travel, pen-down, one waypoint, lift


def make_controller(hand_check=None, gripper=None, arm=None):
    """Build a Controller around fakes without connecting to a machine."""
    c = C.Controller.__new__(C.Controller)
    c.arm, c.gripper, c.motion = arm or FakeArm(), gripper or FakeGripper(), FakeMotion()
    c.motion.controller = c
    c.poses = {"look": {"x": 0, "y": 0, "z": 300, "o_x": 0, "o_y": 0, "o_z": -1, "theta": 0},
               "slot": {"red": {"x": 50, "y": 50, "z": 40, "o_x": 0, "o_y": 0, "o_z": -1, "theta": 0}}}
    c.board = BoardToRobot.from_corners(down(300, -100, 5), down(300, 179, 5), down(84, -100, 5), 279, 216)
    c.held_mode = False
    c.hand_check = hand_check
    c.events = asyncio.Queue()
    c.move_times = []
    c.needs_lift = False
    c._lift_mm = cfg.LIFT_MM
    c.last_error = None
    c._abort = asyncio.Event()
    c._lock = asyncio.Lock()
    c._waiting = 0
    return c


def test_stop_aborts_a_running_draw_and_halts_the_arm():
    async def scenario():
        c = make_controller()
        task = asyncio.create_task(c.draw([SQUARE, SQUARE, SQUARE], 10_000, 600))
        await asyncio.sleep(0.05)
        await c.stop()
        with pytest.raises(C.Aborted):
            await task
        return c
    c = asyncio.run(scenario())
    assert c.arm.stopped >= 1
    assert c.motion.calls < 45   # nowhere near three full squares of planned moves
    assert c.last_error and "Aborted" in c.last_error


def test_exception_inside_a_sequence_halts_and_records_the_error():
    async def scenario():
        c = make_controller()
        c.poses = {}   # go_look fails on the missing pose
        with pytest.raises(KeyError):
            await c.go_look()
        return c
    c = asyncio.run(scenario())
    assert c.arm.stopped == 1
    assert c.last_error.startswith("KeyError")


def test_halt_failure_keeps_the_original_cause():
    async def scenario():
        c = make_controller(arm=FakeArm(stop_error=RuntimeError("arm offline")))
        c.poses = {}
        with pytest.raises(KeyError):
            await c.go_look()
        return c
    c = asyncio.run(scenario())
    assert "KeyError" in c.last_error
    assert "arm.stop failed: arm offline" in c.last_error


def test_lock_is_released_after_a_refusal_and_after_a_fault():
    state = {"hand": True}

    async def hand():
        return state["hand"]

    async def scenario():
        c = make_controller(hand_check=hand)
        with pytest.raises(C.Blocked):
            await c.go_look()
        state["hand"] = False
        await c.go_look()                     # the refusal must not have kept the lock
        good_poses, c.poses = c.poses, {}
        with pytest.raises(KeyError):
            await c.go_look()
        c.poses = good_poses
        await c.go_look()                     # nor the fault
        return c
    c = asyncio.run(scenario())
    assert c.motion.calls == 2
    assert c._lock.locked() is False


def test_busy_rejects_a_concurrent_command_instead_of_queuing_it():
    async def scenario():
        c = make_controller()
        task = asyncio.create_task(c.draw([SQUARE], 10_000, 600))
        await asyncio.sleep(0.005)
        with pytest.raises(C.Busy):
            await c.move_to(down(0, 0, 100))
        await task
        return c
    c = asyncio.run(scenario())
    assert c.arm.stopped == 0


def test_command_cannot_barge_in_front_of_a_waiting_recover():
    async def scenario():
        c = make_controller()
        c.motion.move_delay_s = 0.2
        draw = asyncio.create_task(c.draw([SQUARE], 10_000, 600))
        await asyncio.sleep(0.05)
        await c.stop()
        recovery = asyncio.create_task(c.recover())
        await asyncio.sleep(0.01)             # recover() is now waiting for the lock
        with pytest.raises(C.Busy):
            await c.move_to(down(0, 0, 100))   # must be rejected, not queued behind the recovery
        await recovery
        with pytest.raises(C.Aborted):
            await draw
        return c
    c = asyncio.run(scenario())
    assert c.needs_lift is False
    assert c.last_error is None


def test_recover_gives_up_after_the_wait_budget(monkeypatch):
    monkeypatch.setattr(cfg, "MOVE_TIMEOUT_S", 0.05)

    async def scenario():
        c = make_controller()
        c.motion.move_delay_s = 0.5
        draw = asyncio.create_task(c.draw([SHORT], 10_000, 600))
        await asyncio.sleep(0.01)
        with pytest.raises(C.Busy, match="still running"):
            await c.recover()
        await c.stop()
        with pytest.raises(C.Aborted):
            await draw
        await c.go_look()                     # the lock is usable once the sequence unwinds
        return c
    c = asyncio.run(scenario())
    assert c._lock.locked() is False


def test_hand_between_strokes_ends_the_turn_without_a_halt():
    calls = {"n": 0}

    async def hand():
        calls["n"] += 1
        return calls["n"] > 1   # clear at the start of the sequence, present before the second stroke

    async def scenario():
        c = make_controller(hand_check=hand)
        return c, await c.draw([SQUARE, SQUARE, SQUARE], 10_000, 600)
    c, result = asyncio.run(scenario())
    assert result.blocked is True
    assert result.strokes_done == 1
    assert c.arm.stopped == 0
    assert c.needs_lift is False


def test_hand_at_the_start_refuses_without_a_halt():
    async def hand():
        return True

    async def scenario():
        c = make_controller(hand_check=hand)
        with pytest.raises(C.Blocked):
            await c.go_look()
        return c
    c = asyncio.run(scenario())
    assert c.arm.stopped == 0
    assert c.motion.calls == 0


def test_hand_check_fault_counts_as_a_hand():
    async def hand():
        raise RuntimeError("camera gone")

    async def scenario():
        c = make_controller(hand_check=hand)
        with pytest.raises(C.Blocked):
            await c.go_look()
        return c
    c = asyncio.run(scenario())
    assert "camera gone" in c.last_error
    assert c.arm.stopped == 0


def test_empty_polyline_is_skipped_not_fatal():
    async def scenario():
        c = make_controller()
        return c, await c.draw([[], SQUARE], 10_000, 600)
    c, result = asyncio.run(scenario())
    assert result.strokes_done == 1
    assert c.arm.stopped == 0


def test_refused_move_mid_stroke_halts_and_recover_lifts():
    async def scenario():
        c = make_controller()
        c.motion.refuse_call = 4   # travel, pen-down, one waypoint succeed; the fourth move is refused
        with pytest.raises(C.MoveRefused):
            await c.draw([SQUARE], 10_000, 600)
        assert c.needs_lift is True
        assert c.arm.stopped == 1
        await c.recover()
        return c
    c = asyncio.run(scenario())
    assert c.needs_lift is False
    assert c.last_error is None
    assert {"clear_error": True} in c.arm.commands
    lift = c.motion.destinations[-1].pose
    assert (lift.x, lift.y, lift.z) == (0, 0, 1 + cfg.LIFT_MM)   # straight up from tip_pose by LIFT_MM


def test_stop_during_the_final_lift_keeps_needs_lift():
    async def scenario():
        c = make_controller()
        c.motion.stop_during_call = 4   # the lift move of SHORT: travel, pen-down, waypoint, lift
        await c.draw([SHORT], 10_000, 600)
        assert c.needs_lift is True     # the lift may have been truncated by the stop
        await c.recover()
        return c
    c = asyncio.run(scenario())
    assert c.needs_lift is False
    assert c.arm.stopped == 1


def test_recover_ignores_the_hand_gate():
    async def hand():
        return True

    async def scenario():
        c = make_controller(hand_check=hand)
        c.needs_lift, c._lift_mm = True, cfg.LIFT_MM
        await c.recover()
        return c
    c = asyncio.run(scenario())
    assert c.needs_lift is False
    assert c.motion.calls == 1


def test_recover_waits_for_the_aborted_move_to_unwind():
    async def scenario():
        c = make_controller()
        c.motion.move_delay_s = 0.2
        task = asyncio.create_task(c.draw([SQUARE], 10_000, 600))
        await asyncio.sleep(0.05)
        await c.stop()
        await c.recover()   # must wait for the in-flight move rather than raise Busy
        with pytest.raises(C.Aborted):
            await task
        return c
    c = asyncio.run(scenario())
    assert c.needs_lift is False
    assert c.last_error is None


def test_dock_abort_recovers_with_the_uncap_height():
    async def scenario():
        c = make_controller()
        c.motion.refuse_call = 2   # hover succeeds, the descent to grip height is refused
        with pytest.raises(C.MoveRefused):
            await c.pick_marker("red")
        assert c.needs_lift is True and c._lift_mm == cfg.UNCAP_LIFT_MM
        await c.recover()
        return c
    c = asyncio.run(scenario())
    assert c.needs_lift is False
    lift = c.motion.destinations[-1].pose
    assert (lift.x, lift.y, lift.z) == (0, 0, 1 + cfg.UNCAP_LIFT_MM)


def test_move_to_low_marks_needs_lift_for_recover():
    async def scenario():
        c = make_controller()
        await c.move_to(down(50, 50, 40), low=True)
        assert c.needs_lift is True and c._lift_mm == cfg.UNCAP_LIFT_MM
        await c.move_to(down(0, 0, 300))
        return c
    c = asyncio.run(scenario())
    assert c.needs_lift is False


def test_pick_marker_checks_grab_only_when_configured(monkeypatch):
    async def lenient():
        monkeypatch.setattr(cfg, "REQUIRE_GRAB_DETECT", False)
        c = make_controller(gripper=FakeGripper(grab_result=False))
        await c.pick_marker("red")
        return c
    c = asyncio.run(lenient())
    assert c.needs_lift is False
    assert c.arm.stopped == 0

    async def strict():
        monkeypatch.setattr(cfg, "REQUIRE_GRAB_DETECT", True)
        c = make_controller(gripper=FakeGripper(grab_result=False))
        with pytest.raises(RuntimeError, match="closed on nothing"):
            await c.pick_marker("red")
        return c
    c = asyncio.run(strict())
    assert c.arm.stopped == 1
    assert c.needs_lift is True


def test_command_cannot_barge_in_the_lock_handoff_window():
    async def scenario():
        c = make_controller()
        await c._lock.acquire()                # stand in for a running sequence
        rec = asyncio.create_task(c.recover())
        for _ in range(3):
            await asyncio.sleep(0)             # rec is now parked on the lock
        assert c._waiting == 1
        c._lock.release()                      # waiter woken, has not resumed yet
        assert c._lock.locked() is False       # the exact window the guard must cover
        with pytest.raises(C.Busy):
            await c.move_to(down(0, 0, 100))   # rejected, not queued behind the recovery
        await rec
        return c
    c = asyncio.run(scenario())
    assert c._waiting == 0


def test_cancelling_a_sequence_halts_the_arm_and_propagates():
    async def scenario():
        c = make_controller()
        c.motion.move_delay_s = 0.05
        task = asyncio.create_task(c.draw([SQUARE], 10_000, 600))
        await asyncio.sleep(0.02)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        return c
    c = asyncio.run(scenario())
    assert c.arm.stopped == 1
    assert c._lock.locked() is False
    assert "CancelledError" in c.last_error


def test_short_stroke_fixture_matches_the_waypoint_spacing():
    # test_stop_during_the_final_lift_keeps_needs_lift assumes SHORT resamples to exactly two points
    assert len(resample(SHORT, cfg.WAYPOINT_MM)) == 2
