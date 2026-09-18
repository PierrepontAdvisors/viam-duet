# 15 — Run

Source: page 15 of the course print view (exercise, ~12 min)
Date:

## What this page is about
Turn one cycle into a packed pallet: a real placement pattern, a loop of eight, and make `run` the default verb.

## Values I need
- Pattern: two layers of a 2 × 2 grid. Layer = i // 4, slot = i % 4, column = slot % 2, row = slot // 2. x offsets by half a box width per column, y by half a box length per row, z tip = pallet top + (layer + 1) × box height.
- `run` clears the drawn boxes, resets `placed`, calls `place` eight times, prints the count.
- Entry point: no argument means `run`.

## Checkpoint
`python palletizer.py` packs eight boxes. Watch closely: something in the second layer is physically impossible. That's page 16.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
