# Page tests and harness

Pure modules under `duet/static/js/` are tested with Node's runner, no install:

    node --test 'pagetests/*.test.mjs'

The replay harness serves the page with tonight's session over the real protocol:

    PY=/Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/code/hackathon/.venv/bin/python
    $PY pagetests/replay_server.py            # http://localhost:8765/?view=console

Keys on the page: arrows step photos, space plays the loop, L live, C controls, Z crop, D developer mode.

## Acceptance

`?view=console` opens with the panel, `?selftest=1` prints the geometry checks in the console.
The full walk is Task 11 of `docs/superpowers/plans/2026-09-18-duet-5-page.md`.
