# 03 — Run viam-server

Source: page 3 of the course print view (exercise, ~3 min)
Date:

## What this page is about
Install viam-server where the robot's compute lives and start it with the machine's cloud credentials so the machine goes online.

## How the course does it vs. how I did it
- Course: a Linux browser IDE stands in for the robot's computer. You paste the credentials into a `viam.json` file there, download the viam-server binary with curl, and run it in the IDE terminal.
- Me: installed viam-server on the Mac with Homebrew and ran it against `~/Downloads/viam-palletizer-101-main.json`. Same result: the machine shows ONLINE. Commands and log notes in `../01-setup.md`.
- Consequence: my viam-server runs on the Mac, so it must stay running while I work through the exercises. The Python code can run either in the course IDE or locally; both reach the machine through the cloud address.

## Checkpoint
viam-server running, machine ONLINE in the app.

## Things that tripped me up
Short version here; full write-up in `../stuck-log.md`.

## Questions
-

## One-sentence takeaway
