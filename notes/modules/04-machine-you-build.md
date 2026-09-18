# 04 — The machine you're going to build

Source: page 4 of the course print view (lesson, ~5 min)
Date:

## What this page is about
A preview of the finished machine's configuration and where each piece of it comes from.

## Key concepts
- **Config is the machine** — one document stored with the machine in the app. viam-server downloads it and builds whatever it describes.
- **Modules provide implementations** — every resource in the config needs code behind it. A few modules ship inside viam-server; most are downloaded from the registry.
- **Same API regardless of hardware** — code written against the simulated arm works unchanged on a real arm because every arm module implements the same arm API.
- Four words used constantly: **component** (hardware: arm, gripper, camera), **service** (capability on top of components: motion, vision, data), **resource** (either), **module** (the code implementing one or more resources).

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
