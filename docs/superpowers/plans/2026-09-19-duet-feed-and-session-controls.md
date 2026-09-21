# Duet held still, calmer feed, End / New session: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The page holds the capture still while the robot draws, never shows the gray card, streams only new frames at 4 fps, and gets End session and New session buttons that work without restarting the process.

**Architecture:** The session keeps a `held_frame` (its last capture) and an `ending` flag; `web.py` picks what the stream shows from `at_look` and `held_frame` with one pure function shared by the stream generator and a feed watcher that emits a `feed` event; a new `SessionRunner` owns the current session so `restart` can build a fresh one on a fresh recorder. The page parses `feed`, `ending`, and two new commands, and adds a Run row to the panel plus a stage-level New session button.

**Tech Stack:** Python 3.12, asyncio, FastAPI + Starlette TestClient, OpenCV, pytest; page in ES modules tested with Node's built-in runner.

**Spec:** `docs/superpowers/specs/2026-09-19-duet-feed-and-session-controls-design.md`

> Executed in full on the old base (`feat/duet-feed` at 4d00024, seven tasks, every review round closed, walked in the browser), then ported onto `feat/duet-design` at 5cd9d87 without the `SessionRunner` (Task 2) and without the stage New session button of Task 6, because the demo branch had grown its own in-place restart and welcome page in the meantime; see the design's section 9. The task texts below are the record of the first execution.

**Where:** the worktree `.claude/worktrees/duet-feed` (branch `feat/duet-feed`). All paths below are relative to `code/hackathon/` inside it. Run Python through the main checkout's virtualenv, from `code/hackathon`:

```bash
<repo>/code/hackathon/.venv/bin/python -m pytest -q -p no:cacheprovider
```

and the page tests with `node --test 'pagetests/*.test.mjs'`. The worktree guard refuses shell variables and heredocs: write plain commands with absolute paths, and use the Write/Edit tools for file contents.

**Conventions:** commit messages `type: description` (feat, fix, test, docs), ending with the line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Stage named files only (`git add path path`); never `git add -A`. Match the existing style: docstrings that say why, one-line comments after code, no type-only refactors.

---

### Task 1: Session: held frame, End, restartable, bus clear

> Executed as commits 4ff0573, 25ce59c and 2cac15f. The review rounds went past this text: `RESTARTABLE` has no `plan`, the still is set through `_hold()` with a process-unique `held_id` and only when the capture shows no hand, `marker_out` is claimed before the pick, `emit_state` carries `restartable`, and `Session.stopped` reports a pending pause. The design (section 4.1) is the record; re-executing from this text would reintroduce what the reviews removed.

**Files:**
- Modify: `duet/session.py`
- Test: `tests/test_session.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_session.py`:

```python
def test_the_bus_forgets_cleared_types_and_snapshots_feed_after_state():
    bus = EventBus()
    bus.emit("state", state="idle", turn=0)
    bus.emit("feed", source="live")
    bus.emit("plan", polylines=[])
    assert [m["type"] for m in bus.snapshot()] == ["state", "feed", "plan"]
    bus.clear("plan", "video")
    assert [m["type"] for m in bus.snapshot()] == ["state", "feed"]


def test_the_first_move_is_held_on_the_latest_live_frame(tmp_path, look_frame, exchange_start, calibration):
    s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=1)
    seen = []

    async def go_look():
        seen.append(s.held_frame is not None)
    ctl.go_look = go_look
    asyncio.run(s._state_start())
    assert seen == [True] and s.held_frame is not None


def test_end_during_the_human_turn_signs_and_finishes(tmp_path, look_frame, exchange_start, calibration):
    async def scenario():
        s, frames, ctl, rec, q = build(tmp_path, look_frame, exchange_start, calibration, exchanges=3, handoff="held")
        task = asyncio.create_task(s.run())
        await until_state(s, "human_turn")
        assert s.restartable and s.held_frame is not None
        s.end()
        await asyncio.wait_for(task, 60)
        return s, ctl, drain(q)
    s, ctl, events = asyncio.run(scenario())
    assert s.states_seen == ["start", "human_turn", "finish", "finished"]
    assert [c[0] for c in ctl.calls].count("draw") == 1            # the signature only
    assert any(e["type"] == "state" and e["ending"] for e in events)
    assert not any(e["type"] == "state" and e["ending"] for e in events[:2])   # the flag is off until End
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
        assert not s.restartable
        s.end()
        await asyncio.wait_for(task, 60)
        return s, ctl, drain(q)
    s, ctl, events = asyncio.run(scenario())
    assert s.states_seen == ["start", "human_turn", "capture", "interpret", "plan", "robot_draw", "look", "finish", "finished"]
    assert [c[0] for c in ctl.calls].count("draw") == 2            # the plan, then the signature
    assert s.turn == 1
```

- [ ] **Step 2: Run them to see them fail**

Run: `<repo>/code/hackathon/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_session.py -k "bus_forgets or first_move or end_during"`
Expected: 4 failed (`AttributeError: 'EventBus' object has no attribute 'clear'`, `'Session' object has no attribute 'held_frame'`, `'end'`).

- [ ] **Step 3: Implement**

In `duet/session.py`:

(a) After the `RETRY_AFTER_FAULT` block, add:

```python
# States in which the arm is at the look pose and not in a sequence, or has been stopped: the page's
# New session may cancel the loop here. Everywhere else the arm is moving or about to.
RESTARTABLE = ("finished", "human_turn", "capture", "interpret", "plan", "paused")
```

(b) In `EventBus`, change `SNAPSHOT` to:

```python
    SNAPSHOT = ("calib", "state", "feed", "dock", "human", "interpretation", "plan", "progress", "shot", "video", "error")
```

and add after `emit`:

```python
    def clear(self, *types: str) -> None:
        """Forget the last message of these types, so a later snapshot has nothing from an old piece."""
        for t in types:
            self.last.pop(t, None)
```

(c) In `Session.__init__`, after `self.at_look = False`:

```python
        self.held_frame: np.ndarray | None = None   # the raw look-pose frame the stream shows while the arm is away
        self.ending = False                        # End was pressed: sign at the next safe point
```

(d) In the controls section, after `pass_turn`:

```python
    def end(self) -> None:
        """Finish the piece at the next safe point: now if it is the visitor's turn, after the look
        photo if the robot is drawing. The arm is never interrupted here; Pause does that."""
        self.ending = True
        self.emit_state()

    @property
    def restartable(self) -> bool:
        return self.state in RESTARTABLE
```

(e) In `emit_state`, add `ending=self.ending,` to the `bus.emit("state", ...)` call (after `error=self.last_error,`).

(f) In `_state_start`, before `await self.ctl.go_look()`:

```python
        live = self.frames.latest()
        if live is not None:
            self.held_frame = live.color         # the first move is held on this, not shown live
```

(g) In `_capture_board`, right after `frame = await self.frames.capture_median()`:

```python
        self.held_frame = frame
```

(h) In `_state_human_turn`, inside the loop, between the `_running` check and the `_pass` check:

```python
            if self.ending:
                return "finish"
```

(i) In `_state_look`, change the end condition to:

```python
        if self.ending or self.turn >= self.settings.exchanges or self.coverage >= cfg.COVERAGE_END:
            return "finish"
```

- [ ] **Step 4: Run the tests**

Run: `<repo>/code/hackathon/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_session.py`
Expected: all pass (the existing 11 plus 4 new).

- [ ] **Step 5: Commit**

```bash
git add duet/session.py tests/test_session.py
git commit -m "feat(session): held frame for the stream, End at the next safe point, restartable states, bus clear"
```

---

### Task 2: SessionRunner

**Files:**
- Create: `duet/runner.py`
- Test: `tests/test_runner.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_runner.py`:

```python
import asyncio
import json

import pytest

from duet.fakes import FakeBrain, FakeController, FakeFrames
from duet.recorder import Recorder
from duet.runner import SessionRunner, watch
from duet.session import EventBus, HandGuard, Session, Settings


def make_runner(tmp_path, look_frame, exchange_start, calibration, **settings):
    frames = FakeFrames(look_frame, calibration)
    frames.show_board(exchange_start)
    ctl = FakeController(frames)
    bus = EventBus()
    guard = HandGuard(frames, calibration)
    ids = iter(("first", "second", "third"))

    def make_session(st: Settings) -> Session:
        rec = Recorder(next(ids), root=tmp_path, settings=st.record())
        return Session(st, frames, ctl, FakeBrain(), rec, bus, calibration, guard=guard, poll_s=0.01)
    return SessionRunner(make_session, Settings(**settings), bus, ctl), frames, ctl, bus


async def until(runner, state, timeout=10):
    async with asyncio.timeout(timeout):
        while runner.session.state != state:
            await asyncio.sleep(0.01)


def test_restart_from_finished_starts_a_fresh_piece_with_the_settings_kept(tmp_path, look_frame, exchange_start, calibration):
    async def scenario():
        runner, frames, ctl, bus = make_runner(tmp_path, look_frame, exchange_start, calibration, exchanges=2, length="medium")
        runner.start()
        await until(runner, "human_turn")
        runner.session.update_settings(length="long")
        runner.session.end()
        await asyncio.wait_for(runner.task, 60)
        assert runner.session.state == "finished" and "video" in bus.last and "plan" in bus.last
        first = runner.session
        second = await runner.restart()
        await until(runner, "human_turn")
        await runner.close()
        return first, second, bus, ctl
    first, second, bus, ctl = asyncio.run(scenario())
    assert second is not first and second.rec.id == "second" and (second.rec.dir / "turn-00-start.jpg").exists()
    assert second.settings.length == "long" and second.settings.exchanges == 2
    assert "video" not in bus.last and "plan" not in bus.last and bus.last["state"]["session"] == "second"
    assert json.loads((tmp_path / "current.json").read_text())["id"] == "second"
    assert ("recover",) not in ctl.calls


def test_restart_is_refused_while_the_robot_draws(tmp_path, look_frame, exchange_start, exchange_human, calibration):
    async def scenario():
        runner, frames, ctl, bus = make_runner(tmp_path, look_frame, exchange_start, calibration, exchanges=1, artist="haring")
        ctl.stroke_s = 0.15
        runner.start()
        await until(runner, "human_turn")
        frames.show_board(exchange_human)
        runner.session.pass_turn()
        await until(runner, "robot_draw")
        first = runner.session
        with pytest.raises(ValueError, match="moving"):
            await runner.restart()
        assert runner.session is first and not runner.task.done()
        await asyncio.wait_for(runner.task, 60)
        return runner
    runner = asyncio.run(scenario())
    assert runner.session.state == "finished"


def test_restart_from_paused_recovers_the_arm_before_the_new_piece_moves(tmp_path, look_frame, exchange_start, exchange_human, calibration):
    async def scenario():
        runner, frames, ctl, bus = make_runner(tmp_path, look_frame, exchange_start, calibration, exchanges=1, artist="haring")
        ctl.stroke_s = 0.15
        runner.start()
        await until(runner, "human_turn")
        frames.show_board(exchange_human)
        runner.session.pass_turn()
        await until(runner, "robot_draw")
        await asyncio.sleep(0.3)
        await runner.session.pause()
        await until(runner, "paused")
        n = len(ctl.calls)
        await runner.restart()
        await until(runner, "human_turn")
        await runner.close()
        return ctl.calls[n:], runner
    calls, runner = asyncio.run(scenario())
    kinds = [c[0] for c in calls]
    assert kinds.index("recover") < kinds.index("go_look")
    assert "return" not in kinds                                   # held mode: the marker stays in the gripper
    assert runner.session.rec.id == "second" and runner.session.turn == 0


def test_restart_from_a_paused_dock_draw_returns_the_marker_after_recovering(tmp_path, look_frame, exchange_start, exchange_human, calibration):
    async def scenario():
        runner, frames, ctl, bus = make_runner(tmp_path, look_frame, exchange_start, calibration, exchanges=1, artist="haring", handoff="dock")
        ctl.stroke_s = 0.15
        runner.start()
        await until(runner, "human_turn")
        frames.show_board(exchange_human)
        runner.session.pass_turn()
        await until(runner, "robot_draw")
        await asyncio.sleep(0.3)
        await runner.session.pause()
        await until(runner, "paused")
        assert runner.session.marker_out
        n = len(ctl.calls)
        await runner.restart()
        await until(runner, "human_turn")
        await runner.close()
        return ctl.calls[n:]
    calls = asyncio.run(scenario())
    assert calls[:3] == [("recover",), ("return", "green"), ("go_look",)]


def test_watch_reports_a_task_that_died(capsys):
    async def boom():
        raise RuntimeError("no")

    async def scenario():
        t = watch(asyncio.create_task(boom(), name="boom"))
        await asyncio.gather(t, return_exceptions=True)
        await asyncio.sleep(0)
    asyncio.run(scenario())
    assert "[task died] boom" in capsys.readouterr().out
```

- [ ] **Step 2: Run them to see them fail**

Run: `<repo>/code/hackathon/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_runner.py`
Expected: collection error, `ModuleNotFoundError: No module named 'duet.runner'`.

- [ ] **Step 3: Implement**

Create `duet/runner.py`:

```python
"""One piece after another: the runner owns the current session and the task running it, so the
page's New session starts a fresh piece (new recorder, new folder, the operator's settings kept)
without restarting the process or reconnecting to the machine."""
from __future__ import annotations

import asyncio
from typing import Callable

from duet.session import EventBus, Session, Settings

# What a late joiner must not see from the previous piece; `calib` and `feed` describe the rig, not the piece.
PIECE_EVENTS = ("state", "dock", "human", "interpretation", "plan", "progress", "shot", "video", "error")
MOVING = "the robot is moving; pause first or wait for it to finish"


def watch(task: asyncio.Task) -> asyncio.Task:
    """A background loop that dies silently is worse than one that dies loudly."""
    def died(t: asyncio.Task) -> None:
        if not t.cancelled() and t.exception() is not None:
            print(f"[task died] {t.get_name()}: {t.exception()!r}", flush=True)
    task.add_done_callback(died)
    return task


class SessionRunner:
    def __init__(self, make_session: Callable[[Settings], Session], settings: Settings, bus: EventBus, ctl):
        self.make_session = make_session
        self.bus = bus
        self.ctl = ctl
        self.session: Session = make_session(settings)
        self.task: asyncio.Task | None = None

    def start(self) -> asyncio.Task:
        self.task = watch(asyncio.create_task(self.session.run(), name="session"))
        return self.task

    async def restart(self) -> Session:
        """A fresh piece. Refused while the arm is moving; after a pause the arm is recovered first,
        so a low tool is lifted and the abort flag is cleared before the new piece's first move."""
        old = self.session
        if not old.restartable:
            raise ValueError(MOVING)
        paused = old.state == "paused"
        await self.close()
        if paused:
            await self.ctl.recover()
            if old.marker_out:                 # dock mode, stopped mid-draw: the marker goes home before anything else
                await self.ctl.return_marker(old.color)
        self.bus.clear(*PIECE_EVENTS)
        self.session = self.make_session(old.settings)
        self.start()
        return self.session

    async def close(self) -> None:
        """Cancel the current piece; its recorder writes session.json on the way out."""
        if self.task is not None:
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)
            self.task = None
```

- [ ] **Step 4: Run the tests**

Run: `<repo>/code/hackathon/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_runner.py`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add duet/runner.py tests/test_runner.py
git commit -m "feat: SessionRunner starts a fresh piece on New session, recovering the arm after a pause"
```

---

### Task 3: The stream: held still, new frames only, no gray card, feed event, End / restart commands

> Amended during execution: the feed watcher emits its first `feed` on its first tick, before any page connects, so a fresh bus's snapshot already carries `feed` after `state`. The three tests below that read "the next message" use a `receive(ws)` helper that skips `feed`, a test pins the late joiner's `feed`-after-`state`, and the watcher task is wrapped with `runner.watch` so a death prints `[task died] feed`.

**Files:**
- Modify: `duet/web.py`
- Test: `tests/test_web.py`

- [ ] **Step 1: Rewrite the test module's stubs and add the tests**

In `tests/test_web.py`, replace the imports and the two stub classes at the top with:

```python
import asyncio

import numpy as np
import pytest
from starlette.testclient import TestClient

from duet import vision, web
from duet.camera import Frame
from duet.runner import Refused
from duet.session import EventBus


class StubSession:
    state, turn, plan, at_look, color, held_frame, held_id, ending = "human_turn", 1, [], True, "green", None, 0, False

    def __init__(self):
        self.changes, self.actions = [], []
        self.raise_on_clear = False

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

    async def clear_error(self):
        if self.raise_on_clear:
            raise RuntimeError("arm offline")
        self.actions.append("clear_error")


class StubRunner:
    def __init__(self, session=None, refuse=False):
        self.session = session or StubSession()
        self.refuse = refuse
        self.restarts = 0

    async def restart(self):
        if self.refuse:
            raise Refused("the robot is moving; pause first or wait for it to finish")
        self.restarts += 1
        return self.session


class StubFrames:
    def __init__(self):
        self.t = 0.0
        self.gone = False

    def latest(self):
        return None if self.gone else Frame(np.full((60, 80, 3), 128, np.uint8), None, self.t)
```

Then update every existing `web.make_app(StubSession(), ...)` to `web.make_app(StubRunner(), ...)`, and in the tests that keep a `stub = StubSession()` reference, build `runner = StubRunner(stub)` and pass `runner`. In `test_ws_sends_the_snapshot_then_takes_commands`, after `ws.send_json({"type": "clear_error"})` add:

```python
            ws.send_json({"type": "end"})
            ws.send_json({"type": "restart"})
```

and change the final assertions to:

```python
    assert stub.actions == ["pass", "pause", "resume", "clear_error", "end"]
    assert runner.restarts == 1
```

Append these tests:

```python
def test_a_refused_restart_answers_with_an_error_and_the_socket_lives(tmp_path):
    runner = StubRunner(refuse=True)
    app = web.make_app(runner, StubFrames(), EventBus(), sessions_dir=tmp_path)
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_json({"type": "restart"})
            err = ws.receive_json()
            assert err["type"] == "error" and "moving" in err["message"]
            ws.send_json({"type": "nonsense"})
            assert ws.receive_json()["type"] == "error"
    assert runner.restarts == 0


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
    runner = StubRunner(s)
    seen, parts = [], []
    gen = web.mjpeg(runner, frames, lambda img, source: seen.append(source) or img, period_s=0.005)

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


def test_stream_size_scales_to_960_wide_and_leaves_smaller_frames_alone():
    big = web.stream_size(np.zeros((720, 1280, 3), np.uint8))
    assert big.shape == (540, 960, 3)
    small = np.zeros((360, 640, 3), np.uint8)
    assert web.stream_size(small) is small


def test_the_feed_watcher_emits_on_change_only():
    s, frames, bus = StubSession(), StubFrames(), EventBus()
    q = bus.subscribe()

    async def scenario():
        task = asyncio.create_task(web.watch_feed(StubRunner(s), frames, bus, period_s=0.005))
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


def test_health_follows_the_runner_current_session(tmp_path):
    runner = StubRunner()
    app = web.make_app(runner, StubFrames(), EventBus(), sessions_dir=tmp_path)
    with TestClient(app) as client:
        assert client.get("/health").json() == {"state": "human_turn", "turn": 1}
        other = StubSession()
        other.state, other.turn = "finished", 3
        runner.session = other
        assert client.get("/health").json() == {"state": "finished", "turn": 3}
```

- [ ] **Step 2: Run them to see them fail**

Run: `<repo>/code/hackathon/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_web.py`
Expected: the new tests fail (`AttributeError: module 'duet.web' has no attribute 'feed_pick'`, `'mjpeg'`, `'stream_size'`, `'watch_feed'`) and the command tests fail because `end` is an unknown command.

- [ ] **Step 3: Rewrite `duet/web.py`**

Replace the whole file with:

```python
"""The page's server: the static page, one WebSocket carrying every session event and the page's
commands, an MJPEG stream of the camera that holds the last capture still while the arm is away from
the look pose, and the session files. Local screen only; the public tunnel is P1."""
from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from duet import config as cfg
from duet import vision
from duet.runner import Refused

STATIC = cfg.PACKAGE_DIR / "static"
ALLOWED_SETTINGS = ("artist", "length", "exchanges", "mode", "handoff", "energy", "direction")
STREAM_FPS = 4                 # new frames only; the camera itself delivers one to three a second
STREAM_PERIOD_S = 1 / STREAM_FPS
STREAM_WIDTH = 960             # the page registers on the 16:9 aspect, not the pixel size
STREAM_QUALITY = 65
IMAGE_SIZE = (1280, 720)       # the RealSense color stream the calibration was made on


def hex_to_bgr(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return int(c[4:6], 16), int(c[2:4], 16), int(c[0:2], 16)


def mjpeg_part(bgr: np.ndarray, quality: int = STREAM_QUALITY) -> bytes:
    ok, jpg = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("could not encode a stream frame")
    data = jpg.tobytes()
    return (b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(data)).encode()
            + b"\r\n\r\n" + data + b"\r\n")


def stream_size(bgr: np.ndarray) -> np.ndarray:
    """Scale a frame down to STREAM_WIDTH, keeping the aspect; smaller frames pass through."""
    h, w = bgr.shape[:2]
    if w <= STREAM_WIDTH:
        return bgr
    return cv2.resize(bgr, (STREAM_WIDTH, round(h * STREAM_WIDTH / w)), interpolation=cv2.INTER_AREA)


def feed_pick(session, frames) -> tuple[str, np.ndarray | None, object]:
    """What the stream shows now. "held": the session's last capture while the arm is away from the
    look pose (the wrist camera is swinging over the board and the page's overlay would slide off it);
    "live": the latest fresh camera frame; "stale": nothing to send, so the browser keeps its last
    image instead of a gray card. The key changes when the picture should be resent."""
    still = getattr(session, "held_frame", None)
    if not session.at_look and still is not None:
        return "held", still, ("held", session.held_id)          # the id is unique for the process, unlike id(still)
    f = frames.latest()
    if f is not None:
        return "live", f.color, ("live", f.t)
    return "stale", None, None


def overlay(img: np.ndarray, plan, h_inv: np.ndarray | None, color_bgr: tuple[int, int, int],
            cam_to_robot: dict | None = None) -> np.ndarray:
    """Draw a plan onto a camera frame, leaving `img` untouched.

    `plan` is in robot-board millimeters but the homography maps camera-board pixels, so the
    calibrated per-axis fit (robot = a * cam + b) is inverted first; without one the two frames are
    taken to be the same."""
    if h_inv is None or not plan:
        return img
    ax, bx, ay, by = 1.0, 0.0, 1.0, 0.0
    if cam_to_robot and cam_to_robot.get("ax") and cam_to_robot.get("ay"):
        ax, bx = float(cam_to_robot["ax"]), float(cam_to_robot["bx"])
        ay, by = float(cam_to_robot["ay"]), float(cam_to_robot["by"])
    out = img.copy()
    for pl in plan:
        if len(pl) < 2:
            continue
        pts = np.array([[[(x - bx) / ax * vision.PX_PER_MM, (y - by) / ay * vision.PX_PER_MM]
                         for x, y in pl]], np.float32)
        cv2.polylines(out, [cv2.perspectiveTransform(pts, h_inv)[0].astype(np.int32)], False,
                      color_bgr, 2, cv2.LINE_AA)
    return out


async def mjpeg(runner, frames, render, period_s: float = STREAM_PERIOD_S):
    """Multipart JPEG chunks, one per new picture; nothing while the picture is stale or unchanged.
    `render(img, source)` may draw on the picture before it is scaled and encoded."""
    key = None
    while True:
        source, img, k = feed_pick(runner.session, frames)
        if k is not None and k != key:
            key = k
            yield mjpeg_part(stream_size(render(img, source)))
        await asyncio.sleep(period_s)


async def watch_feed(runner, frames, bus, period_s: float = STREAM_PERIOD_S) -> None:
    """One task per app: tells the page which picture the stream is showing, on change only."""
    source = None
    while True:
        now = feed_pick(runner.session, frames)[0]
        if now != source:
            source = now
            bus.emit("feed", source=source)
        await asyncio.sleep(period_s)


def make_app(runner, frames, bus, sessions_dir: Path = cfg.SESSIONS_DIR, calibration: dict | None = None) -> FastAPI:
    """`runner.session` is read at call time: New session swaps the session underneath a running app."""
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        task = asyncio.create_task(watch_feed(runner, frames, bus), name="feed")
        try:
            yield
        finally:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await task

    app = FastAPI(title="Duet", lifespan=lifespan)
    sessions_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/sessions", StaticFiles(directory=str(sessions_dir)), name="sessions")
    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")   # the page's css and js, once it splits them out
    h_inv = None
    cam_to_robot: dict | None = None
    calib: dict = {}
    if calibration and "marks_image" in calibration:
        quad = vision.board_quad(np.array(calibration["marks_image"], np.float32), calibration["board_tl_index"])
        h_inv = np.linalg.inv(vision.board_homography(quad))
        cam_to_robot = calibration.get("cam_to_robot")
        # The page registers its own layers onto the camera image with this; see the mockup session's protocol.
        calib = {"marks_image": calibration["marks_image"], "board_tl_index": calibration["board_tl_index"],
                 "board_mm": [cfg.BOARD_W_MM, cfg.BOARD_H_MM], "image_size": list(IMAGE_SIZE),
                 "cam_to_robot": cam_to_robot}
        bus.emit("calib", **calib)

    @app.get("/")
    async def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/health")
    async def health():
        s = runner.session
        return {"state": s.state, "turn": s.turn}

    @app.get("/calibration.json")
    async def calibration_json():
        return calib

    async def handle(cmd: dict) -> dict | None:
        session = runner.session
        kind = cmd.get("type")
        if kind == "set":
            changes = {k: v for k, v in cmd.items() if k in ALLOWED_SETTINGS}
            try:
                if "exchanges" in changes:
                    changes["exchanges"] = int(changes["exchanges"])
                for key in ("energy", "direction"):
                    if key in changes:
                        changes[key] = float(changes[key])
                session.update_settings(**changes)
            except (ValueError, TypeError) as exc:
                return {"type": "error", "message": f"setting refused: {exc}"}
            return None
        if kind == "pause":
            await session.pause()
        elif kind == "resume":
            session.resume()
        elif kind == "pass":
            session.pass_turn()
        elif kind == "end":
            session.end()
        elif kind == "restart":
            try:
                await runner.restart()
            except Refused as exc:
                return {"type": "error", "message": f"restart refused: {exc}"}
        elif kind == "clear_error":
            await session.clear_error()
        else:
            return {"type": "error", "message": f"unknown command {kind!r}"}
        return None

    @app.websocket("/ws")
    async def ws(sock: WebSocket):
        await sock.accept()
        q = bus.subscribe()
        pump: asyncio.Task | None = None
        try:
            for msg in bus.snapshot():
                await sock.send_json(msg)

            async def forward():
                try:
                    while True:
                        await sock.send_json(await q.get())
                except Exception:
                    # A payload that will not serialize would otherwise leave the page holding a live
                    # socket that never updates again; close it so its reconnect loop takes over.
                    with contextlib.suppress(Exception):
                        await sock.close(code=1011)
                    raise
            pump = asyncio.create_task(forward())
            while True:
                cmd = await sock.receive_json()
                try:
                    reply = (await handle(cmd) if isinstance(cmd, dict)
                             else {"type": "error", "message": "command must be an object"})
                except Exception as exc:   # a command that fails (the arm is offline, say) must not close the page
                    reply = {"type": "error", "message": f"command failed: {exc}"}
                if reply is not None:
                    await sock.send_json(reply)
        except (WebSocketDisconnect, ValueError):  # ValueError: a frame that is not JSON
            pass
        finally:
            if pump is not None:
                pump.cancel()
                with contextlib.suppress(asyncio.CancelledError, Exception):
                    await pump
            bus.unsubscribe(q)

    def shown(img: np.ndarray, source: str, with_overlay: bool) -> np.ndarray:
        """The server-side plan overlay, for `?overlay=1` clients: on any look-pose picture, live or held."""
        s = runner.session
        if not with_overlay or not s.plan or not (s.at_look or source == "held"):
            return img
        color = hex_to_bgr(cfg.COLOR_HEX.get(getattr(s, "color", "green"), "#222222"))
        return overlay(img, s.plan, h_inv, color, cam_to_robot)

    @app.get("/stream.mjpg")
    async def stream(overlay_on: int = Query(1, alias="overlay")):
        """`?overlay=0` skips the server-side stroke overlay, for a page that draws its own layers."""
        parts = mjpeg(runner, frames, lambda img, source: shown(img, source, bool(overlay_on)))
        return StreamingResponse(parts, media_type="multipart/x-mixed-replace; boundary=frame")

    return app
```

- [ ] **Step 4: Run the tests**

Run: `<repo>/code/hackathon/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_web.py`
Expected: all pass (8 existing, updated, plus 6 new).

- [ ] **Step 5: Commit**

```bash
git add duet/web.py tests/test_web.py
git commit -m "feat(web): the stream holds the capture still while the arm is away, sends new frames only at 4 fps, never a gray card; feed event; end and restart commands"
```

---

### Task 4: run.py wires the runner and the fake visitor replays on New session

**Files:**
- Modify: `duet/run.py`
- Test: `tests/test_run.py`

- [ ] **Step 1: Write the failing test**

In `tests/test_run.py`, add `from pathlib import Path` to the imports and append:

```python
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

    class Runner:
        session = Sess()

    async def scenario():
        bus = run.EventBus()
        frames, runner = Frames(), Runner()
        task = asyncio.create_task(run.fake_visitor(bus, frames, Path("s/turn-00-start.jpg"), [Path("s/turn-01-human.jpg")],
                                                    [Path("s/turn-01-robot.jpg")], runner))
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
        return frames, runner
    frames, runner = asyncio.run(scenario())
    assert frames.shown == ["turn-00-start.jpg", "turn-01-human.jpg", "turn-00-start.jpg", "turn-01-human.jpg"]
    assert runner.session.passes == 2 and frames.robot_boards == ["turn-01-robot.jpg"]
```

- [ ] **Step 2: Run it to see it fail**

Run: `<repo>/code/hackathon/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_run.py -k reloads`
Expected: FAIL, `AttributeError: module 'duet.run' has no attribute 'VISITOR_WAITS'`.

- [ ] **Step 3: Implement**

In `duet/run.py`:

(a) Change the imports: add `from duet.runner import SessionRunner, watch` after the `recorder` import, and delete the local `def watch(...)` function (lines from `def watch(task` through `return task`).

(b) After the `build_parser`/`replay_paths` section add, near the other module constants (right above `class ClaudeBrain`):

```python
VISITOR_WAITS = (2.0, 0.6, 1.0)   # the fake visitor: settle, hand over the board, look at the mark, then Go
```

(c) In `log_events`, change the last branch to include `feed`:

```python
            elif t in ("error", "dock", "video", "human", "feed"):
```

(d) Replace `fake_visitor` with:

```python
async def fake_visitor(bus: EventBus, frames, start: Path, humans: list[Path], robots: list[Path], runner) -> None:
    """Each human turn: wait a moment, move a hand over the board for a second, show the next real
    human-turn board, then press Go (the pass command), as a visitor would. A new session id (New
    session on the page) puts the recorded piece back: the blank board and every turn again."""
    q = bus.subscribe()
    boards: list[Path] = []
    session_id = None
    settle, hand, look = VISITOR_WAITS
    try:
        while True:
            m = await q.get()
            if m["type"] != "state":
                continue
            if m.get("session") != session_id:
                session_id = m.get("session")
                boards = list(humans)
                frames.show_board(cv2.imread(str(start)))
                frames.robot_boards = [cv2.imread(str(p)) for p in robots]
            if m["state"] == "human_turn":
                await asyncio.sleep(settle)
                if not boards:
                    print("[visitor] out of recorded turns; the board is yours", flush=True)
                    continue
                frames.jitter(1.2)
                await asyncio.sleep(hand)
                frames.show_board(cv2.imread(str(boards.pop(0))))
                print("[visitor] drew a mark", flush=True)
                await asyncio.sleep(look)
                runner.session.pass_turn()
                print("[visitor] pressed Go", flush=True)
    finally:
        bus.unsubscribe(q)
```

(e) In `main`, delete the line `rec = Recorder(settings=settings.record())` near the top, and replace everything from `guard = HandGuard(frames, cal)` to the end of the function with:

```python
    guard = HandGuard(frames, cal)

    def make_session(st: Settings) -> Session:
        rec = Recorder(settings=st.record())
        return Session(st, frames, ctl, brain, rec, bus, cal, guard=guard)
    runner = SessionRunner(make_session, settings, bus, ctl)
    if args.fake:
        tasks.append(watch(asyncio.create_task(fake_visitor(bus, frames, start, humans, robots, runner), name="visitor")))
    app = make_app(runner, frames, bus, calibration=cal)
    # the MJPEG stream never ends by itself, so an open page would hold a graceful shutdown forever
    server = uvicorn.Server(uvicorn.Config(app, host=args.host, port=args.port, log_level="warning",
                                           timeout_graceful_shutdown=1))
    logging.getLogger("uvicorn.error").addFilter(QuietShutdownCancels())
    print(f"Duet on http://localhost:{args.port}  source={'fake replay of ' + args.replay if args.fake else 'armfarm22'} "
          f"brain={type(brain).__name__} hand_check={guard.mode} session={runner.session.rec.dir}", flush=True)
    # the logger first: it subscribes before the loop's first emit, so `start` is printed too
    tasks.append(watch(asyncio.create_task(log_events(bus), name="log")))
    runner.start()
    try:
        await server.serve()
    finally:
        with contextlib.suppress(Exception):
            await ctl.stop()                   # the arm halts before the loop is torn down
        with contextlib.suppress(Exception, asyncio.TimeoutError):
            await asyncio.wait_for(runner.close(), 5)   # close() waits for a restart that may be recovering the arm
        for t in tasks:
            t.cancel()
            with contextlib.suppress(Exception, asyncio.CancelledError):
                await t                        # one task that already died must not abort the rest
        if machine is not None:
            with contextlib.suppress(Exception):
                await frames.stop()
            with contextlib.suppress(Exception):
                await machine.close()
```

In the `--fake` branch of `main`, the line `frames.show_board(cv2.imread(str(start)))` stays (the first piece's board is set before the visitor's first event too).

(f) Update the module docstring's last line to: `Stop with Ctrl-C. Every event is also printed to the terminal, so the loop can be watched without the page. New session on the page starts a fresh piece without a restart.`

- [ ] **Step 4: Run the tests**

Run: `<repo>/code/hackathon/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_run.py`
Expected: 4 passed (the fake main test still shuts down cleanly on SIGINT).

Then the whole suite: `<repo>/code/hackathon/.venv/bin/python -m pytest -q -p no:cacheprovider`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add duet/run.py tests/test_run.py
git commit -m "feat(run): the runner owns the piece; the fake visitor replays the recorded boards after New session"
```

---

### Task 5: Page protocol and story words

**Files:**
- Modify: `duet/static/js/protocol.js`
- Modify: `duet/static/js/story.js`
- Test: `pagetests/protocol.test.mjs`, `pagetests/story.test.mjs`

- [ ] **Step 1: Write the failing tests**

Append to `pagetests/protocol.test.mjs`:

```js
test('feed carries a known source and state carries ending', () => {
  assert.equal(parseMessage(JSON.stringify({ type: 'feed', source: 'held' })).source, 'held');
  assert.equal(parseMessage(JSON.stringify({ type: 'feed', source: 'stale' })).source, 'stale');
  assert.equal(parseMessage(JSON.stringify({ type: 'feed', source: 'frozen' })).source, 'live');
  assert.equal(parseMessage(JSON.stringify({ type: 'state', state: 'human_turn', turn: 0, ending: true, restartable: true })).ending, true);
  assert.equal(parseMessage(JSON.stringify({ type: 'state', state: 'human_turn', turn: 0, restartable: true })).restartable, true);
  const bare = parseMessage(JSON.stringify({ type: 'state', state: 'human_turn', turn: 0 }));
  assert.equal(bare.ending, false); assert.equal(bare.restartable, false);
});

test('end and restart are commands', () => {
  assert.deepEqual(command('end'), { type: 'end' });
  assert.deepEqual(command('restart'), { type: 'restart' });
});
```

Append to `pagetests/story.test.mjs` (and add `feedLabel` to its import from `../duet/static/js/story.js`):

```js
test('feedLabel names the picture source', () => {
  assert.equal(feedLabel('live'), 'live · wrist camera');
  assert.equal(feedLabel('held'), 'still · the robot is drawing');
  assert.equal(feedLabel('stale'), 'camera reconnecting…');
  assert.equal(feedLabel(undefined), 'live · wrist camera');
});
```

- [ ] **Step 2: Run them to see them fail**

Run: `node --test 'pagetests/*.test.mjs'`
Expected: 3 failing (feed parses to null; `unknown command end`; `feedLabel` is not exported).

- [ ] **Step 3: Implement**

In `duet/static/js/protocol.js`:

(a) In `PARSERS.state`, add `ending: bool(m.ending), restartable: bool(m.restartable),` after `direction: num(m.direction, 0), energy: num(m.energy, 0.5),`.

(b) After the `video:` parser add:

```js
  feed: (m) => ({ source: oneOf(m.source, ['live', 'held', 'stale'], 'live') }),
```

(c) Change `COMMANDS` to `['pause', 'resume', 'pass', 'clear_error', 'end', 'restart']`.

In `duet/static/js/story.js`, after `PLACEHOLDER_MS`:

```js
/** What the stream is showing, from the `feed` event; the panel's position line reads it. */
export const FEED_LABELS = { live: 'live · wrist camera', held: 'still · the robot is drawing', stale: 'camera reconnecting…' };
export function feedLabel(source) { return FEED_LABELS[source] || FEED_LABELS.live; }
```

- [ ] **Step 4: Run the tests**

Run: `node --test 'pagetests/*.test.mjs'`
Expected: 58 pass, 0 fail (55 before, plus 3).

- [ ] **Step 5: Commit**

```bash
git add duet/static/js/protocol.js duet/static/js/story.js pagetests/protocol.test.mjs pagetests/story.test.mjs
git commit -m "feat(page): feed, ending and restartable in the protocol, end and restart commands, feed labels"
```

---

### Task 6: Page UI: Run row, New session on the stage, picture label, camera chip

**Files:**
- Modify: `duet/static/index.html`
- Modify: `duet/static/js/app.js`
- Modify: `duet/static/js/ui.js`

No unit tests cover the DOM; Task 7 checks it in the browser. Keep the `data-el` names on every new element (developer mode).

- [ ] **Step 1: index.html**

(a) In the top-right chips `div.tr`, insert before the `#count` chip:

```html
    <span class="chip red hidden" id="cam" data-el="chip — camera reconnecting">camera reconnecting…</span>
```

(b) After the `#go` button add:

```html
  <button class="go hidden" id="again" data-el="new session button">New session</button>
```

(c) In the panel, replace the Session row's last group `<div class="g s2"><button id="pause" ...>Pause</button><button id="pass" ...>Pass turn</button></div>` with nothing (delete that div), and insert a new row between the Session row and the `Light` label:

```html
    <span class="lbl">Run</span>
    <div class="g s2"><button id="pause" data-el="pause / resume button">Pause</button><button id="pass" data-el="pass turn button">Pass turn</button></div>
    <div class="g s2"><button id="end" data-el="end session button">End session</button><button id="restart" data-el="new session button (panel)">New session</button></div>
    <div class="g s6"></div>
    <div class="g s2"><button class="danger" id="clear" data-el="clear arm error button">Clear arm error</button></div>
```

(d) In the Light row, delete `<div class="g s4"></div>` and the `<div class="g s2"><button class="danger" id="clear" ...></div>` group (they moved to the Run row).

- [ ] **Step 2: app.js**

(a) In the `app` object, add `feed: null,` after `video: null,`.

(b) In `startSession()`, add after the first line:

```js
  app.video = null; app.human = { polylines: [], new: [] }; app.interpretation = null;   // feed stays: it is about the rig, not the piece
  app.viewer.setInk([]);
```

(c) In `handle`, add `case 'feed': app.feed = msg; break;` before `case 'dock'`.

- [ ] **Step 3: ui.js**

(a) Change the story import to `import { chipFor, bubbleForState, bubbleForShot, anchorFor, PLACEHOLDER_MS, feedLabel } from './story.js';`.

(b) In `renderChips`, after `$('badge').classList.toggle('off', !app.connected);` add:

```js
    $('cam').classList.toggle('hidden', !(app.feed && app.feed.source === 'stale'));
```

and after `$('go').classList.toggle('hidden', st.state !== 'human_turn');` add:

```js
    $('again').classList.toggle('hidden', st.state !== 'finished');
```

(c) Next to `$('clear').onclick = ...` add:

```js
  $('end').onclick = () => sendCommand('end');
  $('restart').onclick = $('again').onclick = () => sendCommand('restart');
```

(d) In `renderPanel`, change the position line to:

```js
    $('pos').textContent = shot ? (shot.who === 'start' ? 'start · blank board' : `turn ${String(shot.turn).padStart(2, '0')} · ${shot.who}`) : feedLabel(app.feed ? app.feed.source : 'live');
```

and inside `if (st) {`, after the Pause line, add:

```js
      $('restart').disabled = !st.restartable;
      $('end').disabled = st.state === 'finished' || st.ending;
      $('end').textContent = st.ending && st.state !== 'finished' ? 'Ending…' : 'End session';
```

- [ ] **Step 4: Serve the page once and check the console**

Run from `code/hackathon`: `<repo>/code/hackathon/.venv/bin/python -m duet.run --fake --port 8010` in the background, open http://localhost:8010/?view=console, confirm no console errors and that the Run row shows Pause, Pass turn, End session, New session, Clear arm error. Stop the server.

- [ ] **Step 5: Commit**

```bash
git add duet/static/index.html duet/static/js/app.js duet/static/js/ui.js
git commit -m "feat(page): Run row with End session and New session, New session on the stage when finished, picture label and camera chip from the feed event"
```

---

### Task 7: Walk it in the browser, then the docs

**Files:**
- Modify: `README.md` (code/hackathon), `pagetests/README.md`

- [ ] **Step 1: The walk**

Start `python -m duet.run --fake --port 8010 --exchanges 2` (the venv python, from `code/hackathon`; the replay session folder `sessions/20260918-190258` must exist in the worktree; copy it from the main checkout if not). Open http://localhost:8010/?view=console in the built-in browser and check, reading the panel's status and position lines:

1. During `human_turn` the position line says `live · wrist camera`.
2. From `robot_draw` until the state returns to `human_turn`, the position line says `still · the robot is drawing`, the picture does not move, and the plan strokes fill in solid over the still.
3. Press End session during a human turn: the state goes to `finish` then `finished`, the video link appears, the stage shows New session, and the End button reads disabled.
4. Press New session: the status line shows a new session id, exchange 0 of 2, `human_turn`, the fake visitor draws again, and the old plan strokes are gone from the picture.
5. Press New session while the robot draws (use the panel button): the status line shows `restart refused: the robot is moving…` for five seconds and the piece continues.

Fix anything that fails before moving on; commit the fix as `fix(page): ...` or `fix(web): ...`.

- [ ] **Step 2: Docs**

In `code/hackathon/README.md`, in the file table, add after the `duet/run.py` row:

```
| `duet/runner.py`, `duet/web.py` | The runner owns the current piece (New session on the page starts a fresh one; End finishes the piece at the next safe point). The stream holds the last capture still while the arm is away from the look pose, sends new frames only at 4 fps, and freezes instead of showing a gray card when the camera stalls; the `feed` event tells the page which picture it is seeing |
```

In `pagetests/README.md`, after the keys line add:

```
Panel, Run row: Pause, Pass turn, End session (sign and finish at the next safe point), New session (a fresh piece, refused while the arm moves), Clear arm error. The position line names the picture: live, the held still, or camera reconnecting.
```

- [ ] **Step 3: Full suites, then commit**

Run both suites once more; expected all green. Then:

```bash
git add README.md pagetests/README.md
git commit -m "docs: runner, held still, feed event, and the Run row in the READMEs"
```
