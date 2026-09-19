# Duet App Design System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put the live Duet page on the deck's design system before the 3:30 demo: tokens file, embedded font, mat and frame, logo, pills, squared bubbles, paper panel, pops.

**Architecture:** `tokens.css` holds the system; `duet.css` is restyled to use it; `index.html` gains the mat wrapper, the logo symbol and the font link; `ui.js` gains a five-line `popIt` helper called where the state pill, count pill and bubble text are set. Geometry, viewer, app and backend are untouched.

**Spec:** `docs/superpowers/specs/2026-09-19-duet-app-design-system.md`.

### Task 1: tokens.css, fredoka.css, structural test
- [ ] Copy `docs/duet/pitch/fredoka.css` to `code/hackathon/duet/static/fredoka.css`.
- [ ] Write `code/hackathon/duet/static/tokens.css` with the `:root` tokens from the spec and the `pop` keyframe with its reduced-motion guard.
- [ ] Write `code/hackathon/pagetests/style.test.mjs`: index.html links `/static/tokens.css`, `/static/fredoka.css` and no `fonts.googleapis.com`; contains `<symbol id="logo"`, `class="mat"`, and a `.logo` use inside `#badge`; tokens.css defines `--yellow`, `--headline`, `--paper-radius`, `--frame-stroke`, `@keyframes pop` and the reduced-motion guard; duet.css imports nothing from the network and has no `rotate(` on `.chip` or `.bubble`.
- [ ] Run the page suite (the new test fails), commit the files that exist.

### Task 2: index.html
- [ ] Replace the Google Fonts links with `<link rel="stylesheet" href="/static/fredoka.css">` and add `<link rel="stylesheet" href="/static/tokens.css">` before `duet.css`.
- [ ] Wrap `<div class="stage" ...>` in `<div class="mat" id="mat" data-el="mat — plate around the stage">` … `</div>`.
- [ ] Add the deck's `#logo` symbol to the page's `<svg class="defs">` and replace `<span class="chip yellow name" id="badge" data-el="chip — Duet">Duet</span>` with `<span class="logo-wrap" id="badge" data-el="logo — Duet"><svg class="logo" viewBox="0 0 320 130" role="img" aria-label="Duet"><use href="#logo"/></svg></span>`.
- [ ] Run the suites; commit.

### Task 3: duet.css on the system
- [ ] `:root` keeps only page-specific variables (`--stroke`, `--panel`, `--mono`, `--sat`); colours and type come from tokens.
- [ ] Body: plate and pattern; `.mat` 16:9 letterboxed, `container-type: inline-size`; `.stage` absolute, `width: 93cqw`, centred, `border-radius: var(--paper-radius)`, `box-shadow: 0 0 0 var(--frame-stroke) var(--ink)`.
- [ ] Chips as pills, logo sizes, bubbles squared with tails recomputed, Go button, gear and panel on paper, pops (`.pop` class with the keyframe, staggered by nothing; one element at a time).
- [ ] Run the suites, look at the replay on 8001 (idle, human turn, thinking, robot turn, panel open), commit.

### Task 4: ui.js pops
- [ ] Add `function popIt(el) { el.classList.remove('pop'); void el.offsetWidth; el.classList.add('pop'); }` and call it when `$('state').textContent`, `$('count')`'s number, or `$('words').textContent` actually change, and when the Go button becomes visible.
- [ ] Run the suites, check in the browser, commit.

### Task 5: reference doc and memory
- [ ] Write `docs/duet/design-system.md` (tokens, master page, components, motion, ownership: tokens.css is the source of truth, deck.css mirrors it until the deck imports it).
- [ ] Commit; update the memory note.
