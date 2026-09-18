# 08 — Connect from code

Source: page 8 of the course print view (exercise, ~4 min)
Date:

## What this page is about
Get Python talking to the machine: a virtual environment with the SDK, an API key, and the machine's cloud address.

## Steps in my words
1. In a second terminal (viam-server keeps the first), create a venv and install `viam-sdk`; confirm `import viam` works.
2. In the app's CONNECT tab, copy the machine default API key's ID and Key into `api-key.json` (placeholders for `key_id` and `key`). It's a credential; never commit it.
3. In `helpers.py`, set `MACHINE_ADDRESS` to the remote address copied from the ONLINE dropdown. It's a single hostname ending in `.viam.cloud`.
4. Run `python helpers.py`. Success prints "connected to" plus the address; failure names which of the three things to fix.

## Working locally instead of the course IDE
`helpers.py` and `api-key.json` are provided by the course IDE. To work in this repo instead, copy `helpers.py` into `code/palletizer/` and create `api-key.json` there. Both `api-key.json` and `.venv/` are gitignored. My address: `palletizer-101-main.b18ipyo3lz.viam.cloud`.

## Checkpoint
`python helpers.py` prints connected to my machine's address.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
