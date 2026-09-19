# Duet design system and the live page

Date: 2026-09-19, 12:55. Status: Nicholas chose the full restyle before the 3:30 demo (option C) over the recommended after-demo plan; this document records the design and the safety rules. Source of the look: the pitch deck specs of the same day (grid, logo, icons and motion).

## 1. The design system as an artifact

- `code/hackathon/duet/static/tokens.css` is the source of truth: colours (yellow `#ffd400`, red `#e5322d`, blue `#1f4fd6`, green `#17a34a`, orange `#ff7a00`, cream `#fff4d6`, ink `#111`, paper `#fff`, robot ink `#1b8f3a`, visitor ink `#c62828`), the Fredoka stack, four type sizes (display 6.4, headline 4, body 2.1, caption 1.3 cqw), space 1 to 4 cqw, paper (radius 1.2, border .35, padding 1.6 cqw), frame (inset 3, stroke .45 cqw), gutter 1.2 cqw, and the `pop` keyframe with its reduced-motion guard. The live page imports it. The deck keeps an identical `:root` for now because it must stay a self-contained folder; the reference doc says so.
- `code/hackathon/duet/static/fredoka.css` is a copy of the deck's embedded font, so the page no longer depends on Google Fonts at the venue.
- `docs/duet/design-system.md` is the one-page reference: tokens, the master page, components (frame and mat, kicker pill, paper card, pill, speech and thought bubble, chip, logo, step icons), motion, and which file owns what.

## 2. The live page on the system

- **Mat and frame.** The body is a yellow plate with the squiggle pattern (an inline-SVG data URI background at 12 percent, drifting slowly). A `.mat` box, 16:9 and letterboxed like before, holds the camera `.stage` at 93 percent of its width, centred, with the ink keyline drawn as a box shadow so the stage's own coordinate system is untouched. The page measures everything from the stage's own width, so the calibration overlay, bubble placement and crop stay exactly as they are.
- **Logo.** The deck's `#logo` symbol replaces the rotated "Duet" chip top-left; it greys out when the socket is down (the existing `off` class).
- **Chips become pills.** Paper white, ink border, Fredoka 700, no rotation; the tones keep their names (`green`, `red`, `yellow`, `white`, `black`) and take the system colours. The state pill is the page's kicker.
- **Bubbles squared.** Speech is yellow paper, thought is white paper, both with the paper radius and border, no rotation; the left and right tails and the thought dots stay; the thinking pulse stays.
- **Go button** keeps its shape in the system green with the ink border and hard shadow.
- **Panel** becomes paper: white at 94 percent over the picture, an ink top rule, Fredoka labels in ink, pill buttons (white with ink border; `on` yellow; `danger` red with white text; `hide` transparent), sliders with the yellow accent, the status line in ink on paper.
- **Motion.** The state pill, the count pill and the bubble pop (the system keyframe) whenever their text changes; the Go button pops when it appears. `prefers-reduced-motion` turns it off.

## 3. Safety rules for demo day

- CSS and markup only, plus the smallest JavaScript in `ui.js` to restart the pop on text change. Nothing in `geometry.js`, `viewer.js`, `app.js`, or the backend.
- Every step is tested with `node --test 'pagetests/*.test.mjs'` and `pytest tests/test_web.py`, checked in the browser against `python -m duet.run --fake --port 8001`, and committed on its own, so any step can be reverted with `git revert` before 3:30.
- If the real machine is running the page at the same time, the served files change live; each commit leaves the page usable.
