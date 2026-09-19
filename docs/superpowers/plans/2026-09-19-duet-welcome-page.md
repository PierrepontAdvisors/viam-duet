# Duet Welcome Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A welcome overlay on the live page that shows at start and after a session ends, with the logo, a description and a Start button whose state follows the session.

**Spec:** `docs/superpowers/specs/2026-09-19-duet-welcome-page-design.md`.

- [ ] Task 1: `story.js` gains `FRESH_STATES`, `WELCOME_RETURN_MS = 8000`, `welcomeButton(state, waiting)` and `welcomeReturns(prev, next)`; `story.test.mjs` covers them (red first).
- [ ] Task 2: `pagetests/welcome.test.mjs` asserts the overlay markup (ids `welcome`, `start`, the copy, the disabled initial button), the CSS (`.welcome`, staggered delays, `.key`) and that `ui.js` sends `restart` (red first).
- [ ] Task 3: markup in `index.html` inside the stage, CSS in `duet.css` (welcome at z-index 4, gear raised to 6), wiring in `ui.js` (`renderWelcome` in `renderAll`, the Start handler); if `protocol.js` restricts command kinds, add `restart`.
- [ ] Task 4: suites green; browser check on the replay: overlay on load, "Getting ready…" then "Start" pop, Start hides, finished brings it back after 8 s, Start at finished shows "Starting soon…" and the status line reports the unknown command; commit.
