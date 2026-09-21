# Environment setup

Record what was installed, the exact commands, and anything that went wrong.

## Machine
- OS:
- The course runs in simulation, so no hardware is required. Note anything used anyway:

## Viam app account
- Org: Nicholas's Org
- Location: First Location
- Machine: `palletizer-101`, part `palletizer-101-main`
- Status on 2026-09-17: viam-server installed and started from the Terminal panel
- Machine page: https://app.viam.com/machine/<machine-id>/configure?org=<org-id>
- Tabs on the machine page: configure, control, logs, connect, 3D scene, motion
- Credentials file: `~/Downloads/viam-palletizer-101-main.json`, downloaded from the app. It authenticates this Mac to the cloud. Never copy it into this repo.

## viam-server
- Install method: Homebrew, from the app's setup page
```bash
brew trust viamrobotics/brews && brew tap viamrobotics/brews && brew install viam-server
```
- Version (`viam-server --version`): v1.8.0, installed 2026-09-17 via Homebrew 6.0.13
- Start in the foreground (stops when the terminal closes):
```bash
viam-server -config ~/Downloads/viam-palletizer-101-main.json
```
- Or run as a background service that restarts at login:
```bash
cp ~/Downloads/viam-palletizer-101-main.json $(brew --prefix)/etc/viam.json
brew services start viam-server
```
- Stop the service: `brew services stop viam-server`
- The machine should show as online in the app within about 30 seconds of starting.
- First successful start: 2026-09-17. Startup log showed: config fetched from cloud, builtin motion service constructed, WebRTC connection to app.viam.com established.
- Cloud hostname for this part: `palletizer-101-main.xxxxxxxxxx.viam.cloud`
- Local endpoint while running: `https://0.0.0.0:8080` (gRPC/WebRTC, self-signed cert)
- Local state directory: `~/.viam` (packages, cache). Warning at first start: disk 94.6% used, 26.85 GB free. Modules and ML models download here, so keep an eye on space.
- Log lines to look for on a healthy start: `startup ... complete`, `Config watcher started`, `serving`.

## Viam CLI
- Install method:
- Version (`viam version`):
- Logged in via (`viam login`):

## SDK
- Language: Python (the course examples use the Python SDK with `asyncio`)
- System Python on this Mac is 3.9.6. Use a virtual environment so the SDK does not touch the system install:
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install viam-sdk
```
- Install command:
- Version (`pip show viam-sdk`):

## Course IDE vs. this Mac
The course assumes a Linux browser IDE beside the content, with `viam.json`, `api-key.json`, and `helpers.py` in its file tree and viam-server running in its terminal. I run viam-server on the Mac instead. Two ways to do the Python from page 8 on:
1. Use the course IDE for the code. The Mac's viam-server is the robot; the IDE connects through the cloud address. Simplest.
2. Work locally in `code/palletizer/`: copy `helpers.py` from the IDE, create `api-key.json` (gitignored), use the venv command above. Notes stay next to the code.

## Problems during setup
See `stuck-log.md`.
