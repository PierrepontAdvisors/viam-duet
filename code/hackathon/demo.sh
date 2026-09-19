#!/bin/zsh
# Keep the live demo up. The Viam client exits the process when it cannot reconnect after a network
# drop; this relaunches duet.run five seconds later. Ctrl-C twice within five seconds stops the loop.
#     ./demo.sh                 the machine, page at http://localhost:8000
#     ./demo.sh --length long   any duet.run flags pass through
cd "$(dirname "$0")" || exit 1
while true; do
  .venv/bin/python -m duet.run "$@"
  echo "duet.run exited at $(date +%H:%M:%S); relaunching in 5 s (Ctrl-C now to stop)"
  sleep 5 || break
done
