# Page tests and harness

Pure modules under `duet/static/js/` are tested with Node's runner, no install:

    node --test 'pagetests/*.test.mjs'

The replay harness serves the page with a recorded session over the real protocol. A fresh clone has only the showcase session, so point it there:

    DUET_SESSIONS=../../site/demo/sessions DUET_SESSION=20260919-151119 DUET_FRAME=tests/fixtures/look_frame.jpg \
      .venv/bin/python pagetests/replay_server.py     # http://localhost:8765/?view=console (or ?view=diag for the diagnostics drawer)
    DUET_SPEED=3 ...                                   # faster turns; without the variables it looks for a recording under sessions/ and a capture under captures/

Keys on the page: arrows step photos, space plays the loop, L live, C controls, G diagnostics, Z crop, D developer mode.

Panel, Run row: Pause, Pass turn, End session (sign and finish at the next safe point), Relaunch run (the run exits with the arm stopped and `demo.sh` starts it again with the code on disk; the page reloads itself when the new run answers; refused while the arm moves), Reset arm, Clear arm error. The position line names the picture: live, the held still while the robot draws, or camera reconnecting. The harness reproduces the labels but its stream still moves; the freeze is only visible against the real server.

## Acceptance

`?view=console` opens with the panel, `?selftest=1` prints the geometry checks in the console.
The full walk is Task 11 of `docs/superpowers/plans/2026-09-18-duet-5-page.md`.
