# Duet live page: welcome page (zero state)

Date: 2026-09-19, 13:10. Status: approved in chat ("continue"). Extends the app design-system spec.

- **What.** A full-stage overlay inside the frame, on the yellow plate with the squiggle texture: the block logo large, "A robot arm that draws with you." at headline size, two body lines ("Draw one mark. Duet looks, understands, and answers in the hand of an artist." and "Six exchanges. One of a kind. Yours to keep."), and a Start button. Its parts pop in 120 ms apart each time it appears.
- **When it shows.** On load; when a fresh session begins (a state in idle, look, start arriving after a state that was not fresh, which is what a restarted process or a reconnect looks like); 8 seconds after a session reaches finished. Start hides it. The operator panel (C), the corner button and developer mode stay usable over it.
- **The button.** "Getting ready…" and disabled until the state is human_turn, then "Start" (it pops). At finished it reads "Start" too; pressing it sends the `restart` command, shows "Starting soon…", and the page hides the welcome by itself once the new session reaches human_turn. Today the backend has no `restart` (it runs one session per process and the other session owns those files), so the operator restarts the process; the page's behaviour needs no change when the command lands.
- **Pure rules** live in `story.js` (`welcomeButton`, `welcomeReturns`, `WELCOME_RETURN_MS`, `FRESH_STATES`) with tests; `ui.js` only wires them. Structure test in `pagetests/welcome.test.mjs`.
- **Follow-up for the backend owners:** a `restart` command in `web.py` that lets `run.py` build a fresh Session and Recorder and run again.
