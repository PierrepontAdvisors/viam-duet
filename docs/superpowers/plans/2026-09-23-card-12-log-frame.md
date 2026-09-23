# Card 12: the log in one frame — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop card 12 reading as six loose boxes. The headline, the numbered list and the takeaway become one bordered frame — a log page — beside the notebook picture, with the PLAN → REVISE loop untouched at the top.

**Architecture:** Markup only inside card 12's right-hand column, plus one CSS block. No change to the deck's card count, the loop, the grid, the script's spoken words, or any other card.

**Tech Stack:** Static HTML/CSS (no build), Node's test runner for the page contract.

**Decisions taken with Nicholas before writing this:**
- "Its own card" means **one frame inside slide 12**, not a new slide. The deck stays at fourteen.
- The **notebook picture stays**, to the left of the frame.
- The loop row at the top is **unchanged**.

---

## Why it looks messy now

Card 12's right column is four separate rounded pills, a headline and a yellow pill, each with its own border, stacked with gaps. Counting the loop, the card draws **ten** outlined boxes. Nothing groups the log's three parts, so the eye has no order to follow.

The fix is one frame with internal structure: a title, four ruled rows, and a yellow footer band — the shape of an actual log page, which is what the card is about.

---

## File structure

| File | What changes |
|---|---|
| `docs/duet/class/index.html` | card 12's right column becomes a single `.logcard` frame |
| `docs/duet/class/class.css` | the `.logcard` block replaces the `.fields` pill rules |
| `code/hackathon/pagetests/class.test.mjs` | the card-12 assertions follow the new structure |
| `docs/duet/class/script.md` | one stage direction reworded |

---

### Task 1: The frame

**Files:**
- Modify: `docs/duet/class/index.html` (card 12)
- Modify: `docs/duet/class/class.css`
- Modify: `code/hackathon/pagetests/class.test.mjs`

- [ ] **Step 1: Update the tests first**

In `code/hackathon/pagetests/class.test.mjs`, in the `Act 3` test, replace this line:

```js
  for (const [i, allowed] of [[8, 2], [10, 2], [11, 12]]) {   // cards 9, 11, 12: a headline and a takeaway under the pictures (12 adds the loop and the four log fields)
```

with:

```js
  for (const [i, allowed] of [[8, 2], [10, 2]]) {   // cards 9 and 11: a headline and a takeaway under the pictures
```

and immediately after that loop's closing `}`, add:

```js
  // card 12: the log's three parts live in one frame, not as loose boxes
  const logcard = s[11].slice(s[11].indexOf('<div class="paper logcard"'), s[11].indexOf('</div>', s[11].indexOf('<p class="body foot"')));
  assert.ok(logcard.includes('I wrote down every problem.'), 'the frame carries the title');
  assert.equal((logcard.match(/<li\b/g) || []).length, 4, 'the frame carries the four rows');
  assert.ok(logcard.includes('This is what debugging actually is.'), 'the frame carries the takeaway');
  assert.ok(!s[11].includes('class="fields"'), 'the loose pill row is gone');
  assert.ok(!/<p class="paper body takeaway"[^>]*data-el="card 12/.test(s[11]), 'the takeaway is inside the frame, not a pill beside it');
```

- [ ] **Step 2: Run the tests to watch them fail**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: 1 failing test, `the frame carries the title` (the slice is empty because `.logcard` does not exist yet).

- [ ] **Step 3: Replace card 12's right column**

In `docs/duet/class/index.html`, replace:

```html
        <div class="under">
          <h2 class="headline" data-el="card 12 headline">I wrote down every problem.</h2>
          <ol class="fields">
            <li class="pill" data-el="card 12 field — what I saw"><span class="num">1</span><span class="body">What I saw</span></li>
            <li class="pill" data-el="card 12 field — what I tried"><span class="num">2</span><span class="body">What I tried</span></li>
            <li class="pill" data-el="card 12 field — what fixed it"><span class="num">3</span><span class="body">What fixed it</span></li>
            <li class="pill" data-el="card 12 field — why it worked"><span class="num">4</span><span class="body">Why it worked</span></li>
          </ol>
          <p class="paper body takeaway" data-el="card 12 takeaway">This is what debugging actually is.</p>
        </div>
```

with:

```html
        <div class="paper logcard" data-el="card 12 log card">
          <h2 class="headline" data-el="card 12 headline">I wrote down every problem.</h2>
          <ol class="rows">
            <li data-el="card 12 field — what I saw"><span class="num">1</span><span class="body">What I saw</span></li>
            <li data-el="card 12 field — what I tried"><span class="num">2</span><span class="body">What I tried</span></li>
            <li data-el="card 12 field — what fixed it"><span class="num">3</span><span class="body">What fixed it</span></li>
            <li data-el="card 12 field — why it worked"><span class="num">4</span><span class="body">Why it worked</span></li>
          </ol>
          <p class="body foot" data-el="card 12 takeaway">This is what debugging actually is.</p>
        </div>
```

- [ ] **Step 4: Replace the CSS**

In `docs/duet/class/class.css`, replace these six lines:

```css
.log .twocol > .under { grid-column: 8 / span 5; gap: .6cqw; }
.log .twocol .headline { --headline: 3.4cqw; }
.log .twocol .takeaway { --body: 2cqw; padding-top: .7cqw; padding-bottom: .7cqw; }
.log .panel img { max-height: 26cqw; }   /* the big column earns a taller picture than the 21cqw default */
.fields { display: flex; flex-direction: column; gap: .45cqw; align-self: stretch; }   /* the four fields in order, one per line */
.fields .pill { display: flex; justify-content: flex-start; align-items: baseline; gap: .7cqw; padding: .45cqw 1cqw; }
.fields .num { color: var(--blue); font-weight: 700; }
.fields .body { --body: 1.9cqw; }
```

with:

```css
.log .twocol > .panel { grid-column: 1 / span 6; }
.log .twocol > .logcard { grid-column: 7 / span 6; }
.log .panel img { max-height: 26cqw; }   /* the big column earns a taller picture than the 21cqw default */

/* the log page: a title, four ruled rows and a stamped conclusion, all inside one frame */
.logcard { display: flex; flex-direction: column; padding: 1.2cqw 0 0; overflow: hidden; text-align: left; }
.logcard .headline { --headline: 2.9cqw; padding: 0 var(--paper-pad) 1cqw; }
.logcard .rows { display: flex; flex-direction: column; }
.logcard .rows li { display: flex; align-items: baseline; gap: .9cqw; padding: .7cqw var(--paper-pad);
                    border-top: var(--paper-border) solid rgba(17, 17, 17, .18); --body: 2.1cqw; font-size: var(--body); font-weight: 600; }
.logcard .num { color: var(--blue); font-weight: 700; min-width: 1.5cqw; }
.logcard .foot { --body: 2.1cqw; font-size: var(--body); font-weight: 700; text-align: center;
                 padding: .9cqw var(--paper-pad); background: var(--yellow); border-top: var(--paper-border) solid var(--ink); }
```

Two notes on that block. `.logcard` keeps `.paper`'s border and radius from `deck.css` and only adds the inside; `overflow: hidden` is what lets the yellow footer run to the frame's edges without poking past its rounded corners. The first row's `border-top` doubles as the rule under the title, so no separate divider rule is needed.

- [ ] **Step 5: Run the tests to watch them pass**

Run (from `code/hackathon`): `node --test 'pagetests/*.test.mjs'`
Expected: 159 pass, 0 fail.

- [ ] **Step 6: Commit**

```bash
git add docs/duet/class/index.html docs/duet/class/class.css code/hackathon/pagetests/class.test.mjs
git commit -m "feat(class): card 12's log is one frame, not six loose boxes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Check it and tune the fit

**Files:**
- Possibly modify: `docs/duet/class/class.css` (token steps only)

- [ ] **Step 1: Open card 12**

The deck is served at `http://localhost:8795/` from the worktree's `docs/duet` (if it is not, run `python3 -m http.server 8795 --directory docs/duet` in the background from the worktree). Open `http://localhost:8795/class/index.html?v=400#12`.

The stylesheet caches across navigations, so force a fresh one and freeze the animations before measuring:

```js
(async () => { [...document.querySelectorAll('link[rel=stylesheet]')].forEach(x => { const u = new URL(x.href); u.searchParams.set('bust', Date.now()); x.href = u.toString(); }); await new Promise(r => setTimeout(r, 1500)); let s = document.getElementById('freeze') || document.head.appendChild(Object.assign(document.createElement('style'), { id: 'freeze' })); s.textContent = '*{animation:none !important;transition:none !important}'; const c = document.querySelector('.card.active'); const q = document.querySelector('.stage').getBoundingClientRect().width / 100; const content = c.querySelector('.content').getBoundingClientRect(); let max = -1e9, min = 1e9; c.querySelectorAll('.content *').forEach(e => { const r = e.getBoundingClientRect(); if (r.height) { max = Math.max(max, r.bottom); min = Math.min(min, r.top); } }); const card = c.querySelector('.logcard').getBoundingClientRect(); const img = c.querySelector('.panel img').getBoundingClientRect(); const rows = [...c.querySelectorAll('.logcard .rows li')].map(li => Math.round(li.getBoundingClientRect().height)); return { slack_cqw: +(((content.bottom - max) + (min - content.top)) / q).toFixed(2), frame_cqw: [+(card.width / q).toFixed(1), +(card.height / q).toFixed(1)], picture_cqw: [+(img.width / q).toFixed(1), +(img.height / q).toFixed(1)], rowsEqual: new Set(rows).size === 1 }; })()
```

Expected: `slack_cqw` ≥ 1, `rowsEqual: true`, and the frame within a few cqw of the picture's height so the two columns look level.

- [ ] **Step 2: Look at it**

Take a screenshot. Check: one frame, not six boxes; the four rows separated by hairlines, numbers aligned in a blue column; the yellow band flush to the frame's left and right edges with the rounded bottom corners intact; the title on one line if it fits.

- [ ] **Step 3: Tune only if a measurement says so**

If `slack_cqw` is under 1, step `.logcard .rows li { --body: 2.1cqw }` to `1.95cqw`, then `.logcard .headline { --headline: 2.9cqw }` to `2.6cqw`. If the frame is much shorter than the picture, raise the row padding from `.7cqw` to `.9cqw` rather than growing the type. Never touch `--pad-y`: deck.css's 4cqw against the 3cqw frame inset is what keeps the header and footer bands inside the frame.

- [ ] **Step 4: Commit any tuning**

```bash
git add docs/duet/class/class.css
git commit -m "fix(class): card 12's frame sits level with its picture

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: The stage direction, and ship it

**Files:**
- Modify: `docs/duet/class/script.md`
- Modify: `~/Desktop/Duet class talk/` (the presenting copy)

- [ ] **Step 1: Reword the one stale line**

In `docs/duet/class/script.md`, under `## 12 · The log (0:45) — not in the ten-minute version`, replace:

```
*The loop across the top, the notebook on the left, the four fields listed on the right.*
```

with:

```
*The loop across the top, the notebook on the left, and the log itself on the right.*
```

The spoken words do not change: they already walk the loop and then the four things he wrote down.

- [ ] **Step 2: Run both suites**

Run (from `code/hackathon`): `node --test 'pagetests/*.test.mjs'` → 159 pass. Then `/Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/code/hackathon/.venv/bin/python -m pytest -q` → 186 passed.

- [ ] **Step 3: Walk the deck once**

Step from card 1 to card 14 with the right arrow, including every reveal. Card 12 is the only one that changed, but confirm nothing else shifted: no card's content crosses its frame, and the console shows no errors.

- [ ] **Step 4: Refresh the Desktop copy**

```bash
SRC="/Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/.worktrees/class-deck/docs/duet/class"
DEST="$HOME/Desktop/Duet class talk"
cp "$SRC/index.html" "$SRC/class.css" "$DEST/deck/class/"
cp "$SRC/script.md" "$DEST/Script.md"
```

- [ ] **Step 5: Commit and push**

```bash
git add docs/duet/class/script.md
git commit -m "docs(class): card 12's stage direction describes the log frame

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
git push
```

---

## Out of scope

- **The loop row.** Unchanged, as agreed.
- **The spoken words.** The script is at 1,690 of its 1,700-word budget; this change adds none.
- **The other thirteen cards.** Nothing else is touched.
