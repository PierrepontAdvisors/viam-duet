# Duet page: a held still while the robot draws, a calmer feed, and End / New session: design

Date: 2026-09-19 (demo day), afternoon. First built on branch `feat/duet-feed` (worktree `.claude/worktrees/duet-feed`, based on `feat/duet-design` at f33ba9b) and verified there; then, because the demo branch had moved on (welcome page, design system, an in-place restart, Reset arm), ported onto `feat/duet-design` at 5cd9d87 as `feat/duet-feed-v2`, later renamed `feat/duet-feed`. Section 9 records the reconciliation. The demo keeps running from the main checkout; this branch merges when Nicholas says so.

## 1. Why

Nicholas asked, after the morning's runs on the machine:

1. A stop or end-session button on the page, or a restart button.
2. While the arm is in motion, do not show the live camera feed.
3. Take a still before the arm commits and hold that.
4. When the arm is done, show the live feed again.
5. Reduce the live feed to a frame rate that does not lag.
6. Never show the camera feed when it is gray and disconnected.

What the page does today: the wrist camera's MJPEG stream (`/stream.mjpg?overlay=0`) is the picture at all times. While the arm draws, the camera swings over the board, the plan overlay (registered to the look pose) slides off the picture, and when the Viam relay stalls for two seconds the stream switches to a dark gray "no camera frame" card and back. The server resends every frame five times a second at 1280x720 even though the camera delivers about one to three frames a second, so the browser queues frames and the picture runs behind. A finished session sits in `finished` until the process is restarted, which reconnects to the machine.

## 2. Decisions taken without asking

Nicholas is at the hackathon and not watching this session, so the design picks defaults and states them:

- **The still is the capture frame.** The session already takes a clean median photo at the look pose right before every robot turn (`_capture_board`). That raw landscape frame is the still: it has no hand in it, it is what the `shot` thumbnail shows, and the page's plan overlay registers on it exactly. No extra capture.
- **The server decides what the stream shows; the page only labels it.** One rule in `web.py` serves every client (the page, a second screen, the replay harness) and the page keeps no state-to-picture mapping. The page learns the source from a new `feed` event.
- **A stale camera freezes the picture; it never goes gray.** When no fresh frame exists the stream simply stops sending, so the browser keeps the last image, and the page shows a small "camera reconnecting" chip. The dark placeholder card is removed.
- **Both End and New session.** Nicholas offered "stop or end session, or restart". End finishes the piece properly (signature, final photo, video) at the next safe point; New session starts a fresh piece with a new session folder without restarting the process. Pause remains the way to halt the arm now.
- **Frame rate 4 per second, only new frames, 960 pixels wide.** New frames only removes the queueing; 960x540 at JPEG quality 65 is about a third of today's bytes and keeps the 16:9 aspect the page's registration assumes.

## 3. The picture feed (server)

### 3.1 Sources

`web.py` gains one pure function that both the stream and the feed watcher use:

```python
def feed_pick(session, frames) -> tuple[str, np.ndarray | None, object]:
    """What the stream shows now: ("live", frame, key), ("held", still, key) or ("stale", None, None).
    `key` changes when the picture should be resent; None means send nothing and let the browser keep
    the last image."""
```

Rule, in order:

| Condition | Source | Image | Key |
|---|---|---|---|
| `not session.at_look` and `session.held_frame is not None` | `held` | the held still | `("held", session.held_id)` |
| `frames.latest()` returned a frame | `live` | the frame's color | `("live", frame.t)` |
| otherwise | `stale` | none | `None` |

`at_look` is already maintained by the session: it goes False in `_wait_hands_clear`, right before the arm leaves for a draw, and True after every `go_look`. So the still is shown from the moment the arm is cleared to move until it is back at the look pose, which covers the plan draw, the signature, and the return move. The rare case of "not at look and no still yet" is a session's very first move to the look pose; the session sets `held_frame` from the latest live frame before that move (section 4.1), so the wrist swing is never shown when a frame exists.

### 3.2 The stream generator

```python
STREAM_FPS = 4
STREAM_PERIOD_S = 1 / STREAM_FPS
STREAM_WIDTH = 960          # the page registers on the 16:9 aspect, not the pixel size
STREAM_QUALITY = 65

async def mjpeg(with_overlay):
    key = None
    while True:
        source, img, k = feed_pick(runner.session, frames)
        if k is not None and k != key:
            key = k
            yield mjpeg_part(stream_size(shown(img, with_overlay)), STREAM_QUALITY)
        await asyncio.sleep(STREAM_PERIOD_S)
```

`stream_size` scales the frame to `STREAM_WIDTH` with `cv2.INTER_AREA` when it is wider, keeping the aspect; smaller frames pass through. The server overlay (`render_plan`, for `?overlay=1` clients only) draws the current plan on any look-pose picture, live or held; the session sets `plan` to the signature while it signs so the overlay never shows a finished turn's strokes. While nothing changes, the current picture is resent every `STREAM_KEEPALIVE_S` (10 s) so a proxy on the future public tunnel does not cut an idle response. `no_frame_part`, `NO_FRAME_AFTER_S`, and `PLACEHOLDER_SIZE` go away. The fake camera stamps a frame time only when its picture changes, so `run.py --fake` shows the same new-frames-only behavior as the real camera.

A client that connects while the picture is held or stale gets the still on its first tick (held) or nothing until the camera returns (stale). Nothing sent means the `<img>` stays blank on the black stage, which is the case the page's chip explains.

### 3.3 The feed event

A watcher task, started by the app's lifespan, polls `feed_pick` at the stream period and emits on change:

```json
{"type": "feed", "source": "live" | "held" | "stale"}
```

`feed` joins `EventBus.SNAPSHOT` (after `state`) so a page that joins mid-turn gets it. The watcher is one per app, not per stream client.

## 4. End and New session

### 4.1 Session changes (`session.py`)

- `held_frame: np.ndarray | None` with a `held_id` that is unique for the process (an `itertools.count`), set through `_hold(frame)` in `_capture_board` for every capture that shows no hand (a capture with a hand keeps the previous still, as it keeps the previous reference), and in `_state_start` from the latest live frame's color (if any) before `go_look`, so the session's first move is held too. The stream keys on `held_id` rather than `id(array)`, which Python can reuse after a restart frees the old still.
- `end()`: sets `ending`. The human-turn loop returns `"finish"` when `ending` is set (checked before Go), and `_state_look` returns `"finish"` instead of `"human_turn"`. So End during the human turn signs within a poll (the still shown while it signs is the last capture, which may predate the visitor's final marks; the final photo has them); End during interpret, plan, or robot_draw lets the robot finish its stroke set and sign after the look photo. In `finish`, `finished`, or `paused`, the flag is stored and acts when the loop reaches the next decision point (Resume from a paused robot_draw goes to `look`, which ends). `end()` emits state; the state message gains an `ending: bool` field so the panel can show it. End cannot be undone; a mis-press finishes the piece.
- `restartable` property: `self.state in ("finished", "human_turn", "capture", "interpret", "paused")`, also sent in every state message so the page needs no copy of the list. Those are the states in which the arm is at the look pose and not in a sequence, or has been stopped (`plan` is not listed because `_state_plan` never awaits, so the loop is never observed there). `idle`, `start`, `look`, `robot_draw`, and `finish` are refused: the arm is moving or about to.
- `marker_out`: True from `pick_marker` to `return_marker` in dock mode (held mode never sets it), so the runner knows a marker must go home before a new piece moves.

### 4.2 `SessionRunner` (new module `duet/runner.py`)

Owns the current session and the task running it, so the page can start a new piece without restarting the process.

```python
class Refused(ValueError): ...          # a restart the operator must not have right now; the page shows the message

class SessionRunner:
    def __init__(self, make_session: Callable[[Settings], Session], settings: Settings, bus: EventBus, ctl): ...
                                        # builds the first session here, so web.py can read it before start()
    session: Session                    # the current one; web.py reads it at call time
    task: asyncio.Task | None
    def start(self) -> asyncio.Task     # runs the current session; refuses if a piece is already running
    async def restart(self) -> Session  # see below
    async def close(self) -> None       # cancels the current task and marks the runner closed; run.py's shutdown
```

`restart()` runs under a lock shared with `close()`, so two clients pressing New session at once (the panel button and the stage button, or a second screen) start one piece: the second caller re-evaluates against the new session and is refused.
1. Refuse with `Refused("the robot is moving; pause first or wait for it to finish")` unless `session.restartable`; refuse too once `close()` has run.
2. Cancel the task and await it (`gather(return_exceptions=True)`); a cancel in `_draw` already stops the arm, and the old recorder writes its `session.json` on the way out.
3. If the old session was paused, or a pause is pending (`session.stopped`: Pause clears the running flag and halts the arm at once, but the state label only changes when the current state coroutine returns, seconds later during a Claude call), `await ctl.recover()` so a low tool is lifted and the abort flag is cleared before the new session's first move; then, if the old session's `marker_out` is set (dock mode, stopped mid-draw), `await ctl.return_marker(old.color)` so the marker goes home instead of being dropped by the next piece's `pick_marker`. If either raises, the runner emits `error` ("restart failed: ...") on the bus, keeps the old session in place so a retry works, and re-raises.
4. `bus.clear(...)` for every snapshot type except `calib` and `feed`, so a late joiner's snapshot has nothing from the old piece.
5. Build the next session with `make_session(self.session.settings)` (the operator's settings carry over; the recorder inside `make_session` gets a fresh id and folder) and run it.

Known limits, accepted for the demo: commands sent during the two seconds of recovery reach the old session (a Pause there re-arms the abort flag, and the new piece then pauses on its first move; Resume recovers it). A cancel landing inside `restart()` between the old piece's cancel and the new piece's start (uvicorn's one-second graceful shutdown cancelling the websocket task) leaves no piece running, which at shutdown is what is wanted. `run.py` bounds its shutdown call to `runner.close()` with a five-second timeout, since `close()` waits for a restart that may be recovering the real arm. The `HandGuard` is shared across pieces, so its reference frame is the old piece's board until the new piece's first capture refreshes it; the board still holds the old ink at that moment, so the check is right.

`watch()` (the done-callback that prints a task that died) moves from `run.py` into `runner.py`; `run.py` imports it from there.

`EventBus.clear(*types)` removes those keys from `last`.

### 4.3 Wiring (`run.py`, `web.py`)

- `run.main` builds `make_session(settings)` as a closure over `frames`, `ctl`, `brain`, `bus`, `cal`, `guard` that makes a new `Recorder(settings=settings.record())` and `Session`, hands it to `SessionRunner`, and passes the runner to `make_app`. Shutdown calls `runner.close()` in place of cancelling the session task.
- `make_app(runner, frames, bus, ...)`: everything that read `session` reads `runner.session` at call time (`/health`, `shown`, `handle`, the feed watcher). Tests pass a stub runner with a `.session` attribute.
- `handle` gains `end` (calls `runner.session.end()`) and `restart` (awaits `runner.restart()`; a `Refused` becomes an `error` reply like a refused setting; anything else is a command failure, as today).
- `fake_visitor` takes the runner; when a `state` message carries a new session id it reloads its boards (the start board and the human turns) and `frames.robot_boards`, so `python -m duet.run --fake` replays the recorded piece again after New session.

## 5. Protocol additions

| Direction | Message | Fields |
|---|---|---|
| server to page | `feed` | `source`: `live`, `held`, `stale` |
| server to page | `state` | gains `ending: bool` and `restartable: bool` |
| page to server | `end` | none |
| page to server | `restart` | none |

`protocol.js` parses `feed` (unknown source falls back to `live`), `ending` and `restartable` (default false), and `command()` accepts `end` and `restart`.

## 6. Page changes

- **Panel.** Pause and Pass move out of the Session row into a new `Run` row with End session and New session, then the Clear arm error button: `Run | Pause | Pass | End | New session | (empty) | Clear arm error`. The Session row keeps length, exchanges, handoff, artist; the Light row loses the Clear arm error button. New session is disabled unless the state message says `restartable`; End is disabled in `finished` and while `ending` is set (its label then reads "Ending…").
- **Stage button.** In `finished`, the Go button's slot shows "New session" (same `.go` style, id `again`), so the next visitor can start without opening the panel. It sends `restart`.
- **Picture label.** The panel's position line reads `live · wrist camera`, `still · the robot is drawing`, or `camera reconnecting…` from `app.feed.source` (`story.js` `feedLabel(source)`).
- **Camera chip.** A small chip in the top-right, `camera reconnecting…` (red tone), visible only while `feed.source === 'stale'`.
- **Restart on the page.** `startSession()` (already run when `state.session` changes) also clears `app.video`, `app.human`, `app.interpretation`, and the ink layer, so nothing of the old piece lingers; the view returns to live and the photo loop stops (a finished piece autoplays its loop, and New session is pressed from exactly there). A second press of New session is refused: "a new piece just started" when the two presses were in flight together, "the robot is moving" when the second lands after the first completed and the new piece is still in `idle` or `start`. Either message clears itself after five seconds; accepted.
- **Viewer.** No change: the `<img>` keeps its last frame when the stream sends nothing, which is the intended freeze.

## 7. Testing

Python (`tests/`):
- `test_web.py`: `feed_pick` returns held when not at look with a still, live when fresh, stale otherwise; the generator yields once per new key and nothing while stale; `stream_size` scales 1280x720 to 960x540 and leaves 640x360 alone; `no_frame_part` is gone; `end` and `restart` are routed and a refused restart answers with an `error` and keeps the socket; the feed watcher emits `feed` on change and it follows `state` in the snapshot; `/health` follows the runner's current session.
- `test_session.py`: `end()` in the human turn goes straight to `finish` then `finished` with the signature drawn; `end()` during `robot_draw` completes the draw, takes the look photo, and signs without another human turn; `end()` while paused acts on Resume; `held_frame` is set at start and at every clean capture and kept through a capture with a hand; `restartable` is true in `human_turn`, `paused` and `finished`, false in `robot_draw`; `marker_out` is set during a dock-mode draw only.
- `test_runner.py` (new): restart from `finished` yields a new session id and folder and a cleared snapshot; restart from `paused` calls `recover` before the new session's `go_look`, and returns the marker first when the pause interrupted a dock-mode draw; restart during `robot_draw` raises and leaves the session running; settings carry over.
- `test_run.py`: the fake visitor reloads its boards on a new session id.

Page (`pagetests/`, Node): `protocol.test.mjs` for `feed`, `ending`, `restartable`, `end`, `restart`; `story.test.mjs` for `feedLabel`.

Manual, at the end: `python -m duet.run --fake` from the worktree (with the replay session folder copied in), the page in the built-in browser: the picture holds the capture still through the robot's turn and returns to live at the look pose; End during a human turn signs and finishes; New session starts a fresh piece with a new id and the visitor replays.

## 8. Out of scope

- The camera poller's own cadence (`FrameSource`, 5 polls a second, each grab 0.3 to 0.9 s over Viam's relay). The stream can only be as fresh as the poller.
- A second camera for the hand check while the arm draws (still the checklist's "if time allows").
- The replay harness `pagetests/replay_server.py` emits `feed` (held around its scripted robot turn, live otherwise), `ending` and `restartable`, and accepts `end` and `restart` so the page's buttons work against it; it is still a script, not the real server.
- A feed watcher that dies (its failure prints `[task died] feed`) stays dead for the process; the page's label and chip freeze at their last value. Restarting the process is the recovery.

## 9. Reconciliation with the demo branch (afternoon)

While this was being built, `feat/duet-design` gained its own New session: `Session.restart()` sets an event, `run_forever()` runs a piece, waits for the restart, and `reset()` starts the next one in place with a fresh recorder (the welcome page's Start sends `restart`), plus `reset_arm` (stop, recover, look pose, human turn). Nicholas chose to keep that and drop the `SessionRunner` of section 4.2, so the port keeps from this design: the held still (`held_frame`, `held_id`, `_hold`), `feed` in the snapshot, `end()` and `ending` (with `reset()` clearing `ending`), the signature as the plan while signing, the stream of section 3 with its keep-alive, the fake camera stamping only on change, the visitor replaying on a new piece, the harness protocol, and on the page the feed label, the camera chip and End session in a Run row. Not ported: `SessionRunner`, `Refused`, `restartable` (in the state message and on the page), `marker_out`, `stopped`, `EventBus.clear`, the stage-level New session button (the welcome Start is that button). `watch()` moved to `duet/tasks.py` so the server can wrap its feed watcher without importing the runner module. The known limits of section 4.2 that concerned the runner no longer apply; the shared hand-guard reference and the one-way End still do.
