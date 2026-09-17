# Environment setup

Record what was installed, the exact commands, and anything that went wrong.

## Machine
- OS:
- The course runs in simulation, so no hardware is required. Note anything used anyway:

## Viam app account
- Org / location / machine names:
- Where the machine credentials live (never in this repo):

## viam-server
- Install method:
- Version (`viam-server --version`):
- How to start / stop:

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

## Problems during setup
See `stuck-log.md`.
