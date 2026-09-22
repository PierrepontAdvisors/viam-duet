# Class deck, round two — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fold what the teacher actually recorded from the 2026-09-22 talk back into the deck and the script, so tomorrow's run teaches the course's own vocabulary instead of improvising it in Q&A.

**Architecture:** Six small, independent edits to three files that already exist (`index.html`, `script.md`, `talk.md`) plus one rebuilt card. Nothing structural: no new cards in the 14-card count, no CSS template changes, no new assets. Each task stands alone, so any of them can be dropped if the evening runs out.

**Tech Stack:** Static HTML/CSS deck (no build), Node's test runner for the page contract, Markdown for the spoken words.

**Source of truth for these changes:** `Nicholas_Guest_Speaker_Student_Notes_1.docx.pdf` at the repo root — the teacher's write-up of the 2026-09-22 talk, with her section headings, the questions students asked, and the reflection questions they are graded on.

**Working directory:** the worktree `.worktrees/class-deck` (branch `feat/class-script-narrative`, tracking `origin/main`). Run Node tests from `code/hackathon`. After the last task, refresh `~/Desktop/Duet class talk` — that Desktop copy is what gets presented, and it does not update itself.

---

## Why these six

Every theme the teacher chose to write up was checked against the deck. Six of her eight sections are nowhere in it:

| Her section | In the deck today |
|---|---|
| "The Tracy Connection" (her title: *From Tracy to Real-World Robotics*) | the word "Tracy" appears 0 times |
| PLAN → CODE → TEST → DEBUG → REVISE (printed as a banner) | the loop appears nowhere |
| "Think Before You Execute" (two-hour sprints) | 0 mentions |
| "never been a professional programmer" | 0 mentions |
| "Why Comments and Communication Matter" | the word "comment" appears 0 times |
| Brief → user stories → tasks | 0 mentions |

The story carried the room; the curriculum came out of Q&A. These tasks move the curriculum onto the slides.

---

## File structure

| File | What changes |
|---|---|
| `docs/duet/class/index.html` | card 7's left label and headline (Tracy); card 12 rebuilt as the five-step loop; card 7's robot panel gains a real comment |
| `docs/duet/class/script.md` | the Tracy sentences, the "not a professional programmer" line, the loop words on card 12, a comment sentence on card 7 |
| `docs/duet/class/talk.md` | the Q&A section rebuilt around the six questions students actually asked; the communication answer names comments |
| `code/hackathon/pagetests/class.test.mjs` | copy assertions follow the new card 7 and card 12 |
| `~/Desktop/Duet class talk/` | refreshed copy (last task) |

---

### Task 1: Name Tracy on card 7

The teacher titled the entire packet *From Tracy to Real-World Robotics*, and one of the graded reflection questions is "What connection did you notice between Tracy and Nicholas's robot?" The deck never says the name.

**Files:**
- Modify: `docs/duet/class/index.html` (card 7 headline and left code label)
- Modify: `docs/duet/class/script.md` (card 7 spoken words)
- Modify: `code/hackathon/pagetests/class.test.mjs` (copy list)

- [ ] **Step 1: Update the copy assertions first**

In `code/hackathon/pagetests/class.test.mjs`, in the `Act 2` test's copy list, replace:

```js
    'Your turtle and my robot follow the same thing: a list of points.', 'Your turtle', 'My robot (simplified)',
```

with:

```js
    'Tracy and my robot follow the same thing: a list of points.', 'Tracy (your turtle)', 'My robot (simplified)',
```

- [ ] **Step 2: Run the tests to watch them fail**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: 1 failing test, `copy missing: Tracy and my robot follow the same thing: a list of points.`

- [ ] **Step 3: Change the two strings on card 7**

In `docs/duet/class/index.html`, replace:

```html
<h2 class="headline" data-el="card 7 headline">Your turtle and my robot follow the same thing: a list of points.</h2>
```

with:

```html
<h2 class="headline" data-el="card 7 headline">Tracy and my robot follow the same thing: a list of points.</h2>
```

and replace:

```html
<span class="caption" data-el="card 7 code label — your turtle">Your turtle</span>
```

with:

```html
<span class="caption" data-el="card 7 code label — your turtle">Tracy (your turtle)</span>
```

- [ ] **Step 4: Run the tests to watch them pass**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: `# pass 22`, `# fail 0` for this file; then `node --test 'pagetests/*.test.mjs'` → 159 pass.

- [ ] **Step 5: Say her name in the script**

In `docs/duet/class/script.md`, under `## 7 · It's just points (1:30)`, replace:

```
On the left is turtle, and you've written something like this already. Pen up, go to the starting point, pen down, walk through a list of points, pen up again.
```

with:

```
On the left is Tracy, and you've written something like this already. Pen up, go to the starting point, pen down, walk through a list of points, pen up again.
```

and replace:

```
It's the same program. Mine has a motor attached to it.
```

with:

```
It's the same program. Tracy draws on a screen; mine has a motor and a marker. That's the only difference that matters.
```

- [ ] **Step 6: Commit**

```bash
git add docs/duet/class/index.html docs/duet/class/script.md code/hackathon/pagetests/class.test.mjs
git commit -m "feat(class): card 7 names Tracy, the turtle the class actually uses

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Put the course's loop on card 12

The teacher printed **PLAN → CODE → TEST → DEBUG → REVISE** as a banner and closed the packet with *START SMALL. THINK. BUILD. TEST. LEARN. REVISE.* Card 12 currently shows the four stuck-log fields with no loop around them. This rebuilds it as the loop, with the log as what DEBUG actually looks like.

**Files:**
- Modify: `docs/duet/class/index.html` (card 12 `.under` block)
- Modify: `docs/duet/class/class.css` (a `.loop` row beside the existing `.fields`)
- Modify: `docs/duet/class/script.md` (card 12 words)
- Modify: `code/hackathon/pagetests/class.test.mjs` (copy list and the card-12 block budget)

- [ ] **Step 1: Update the tests first**

In `code/hackathon/pagetests/class.test.mjs`, in the `Act 3` copy list, replace:

```js
    'I wrote down every problem.', '>Symptom<', '>What I tried<', '>Fix<', '>Why it worked<', 'This is what debugging actually is.',
```

with:

```js
    'I wrote down every problem.', '>PLAN<', '>CODE<', '>TEST<', '>DEBUG<', '>REVISE<',
    '>What I saw<', '>What I tried<', '>What fixed it<', '>Why it worked<', 'This is what debugging actually is.',
```

and in the same file, in the story-card block budget, replace:

```js
  for (const [i, allowed] of [[8, 2], [10, 2], [11, 6]]) {   // cards 9, 11, 12: a headline and a takeaway under the pictures (12 adds its four fields)
```

with:

```js
  for (const [i, allowed] of [[8, 2], [10, 2], [11, 12]]) {   // cards 9, 11, 12: a headline and a takeaway under the pictures (12 adds the loop and the four log fields)
```

- [ ] **Step 2: Run the tests to watch them fail**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: 1 failing test, `copy missing: >PLAN<`.

- [ ] **Step 3: Rebuild card 12's `.under` block**

In `docs/duet/class/index.html`, replace the whole `<div class="under">` … `</div>` of card 12 with:

```html
      <div class="under">
        <ol class="loop" data-el="card 12 loop">
          <li class="pill" data-el="card 12 loop — plan">PLAN</li>
          <li class="pill" data-el="card 12 loop — code">CODE</li>
          <li class="pill" data-el="card 12 loop — test">TEST</li>
          <li class="pill on" data-el="card 12 loop — debug">DEBUG</li>
          <li class="pill" data-el="card 12 loop — revise">REVISE</li>
        </ol>
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

(The four field names now match the teacher's own wording: she wrote "describe exactly what you observe", "record what you tried", "determine what fixed the problem", "understand why the solution worked".)

- [ ] **Step 4: Add the loop row to the stylesheet**

In `docs/duet/class/class.css`, immediately after the `.fields .body { --body: 2.1cqw; }` line, add:

```css
.loop { display: flex; justify-content: center; align-items: center; gap: 2.2cqw; }
.loop .pill { position: relative; --body: 1.9cqw; font-size: var(--body); letter-spacing: .08em; padding: .4cqw 1.1cqw; }
.loop .pill.on { background: var(--yellow); }   /* the step this card is about */
.loop .pill + .pill::before { content: "→"; position: absolute; left: -1.55cqw; top: 50%; transform: translateY(-50%);
                              font-size: var(--body); color: var(--ink); }   /* the arrow sits in the gap, not in the pill */
```

- [ ] **Step 5: Run the tests to watch them pass**

Run (from `code/hackathon`): `node --test 'pagetests/*.test.mjs'`
Expected: 159 pass, 0 fail.

- [ ] **Step 6: Check card 12 in the browser**

A server runs at `http://localhost:8792/` serving the worktree's `docs/duet` (if not: `python3 -m http.server 8792 --directory docs/duet` from the worktree, in the background). Open `http://localhost:8792/class/index.html?v=200#12`.

Then measure it, with animations frozen so the reading is the settled layout:

```js
(() => { let s = document.getElementById('freeze') || document.head.appendChild(Object.assign(document.createElement('style'), { id: 'freeze' })); s.textContent = '*{animation:none !important;transition:none !important}'; const c = document.querySelector('.card.active'); const content = c.querySelector('.content').getBoundingClientRect(); const q = document.querySelector('.stage').getBoundingClientRect().width / 100; let max = -1e9, min = 1e9; c.querySelectorAll('.content *').forEach(e => { const r = e.getBoundingClientRect(); if (r.height) { max = Math.max(max, r.bottom); min = Math.min(min, r.top); } }); const loop = [...c.querySelectorAll('.loop .pill')].map(p => Math.round(p.getBoundingClientRect().top)); return { slack_cqw: +(((content.bottom - max) + (min - content.top)) / q).toFixed(2), loopOnOneLine: new Set(loop).size === 1 }; })()
```

Expected: `slack_cqw` ≥ 1 and `loopOnOneLine: true`. If the loop wraps, step `.loop .pill { --body: 1.9cqw }` down to `1.7cqw` and re-measure. If slack drops below 1, step `.fields .body` from `2.1cqw` to `1.9cqw`.

- [ ] **Step 7: Rewrite card 12's words**

In `docs/duet/class/script.md`, replace the whole body under `## 12 · The log (0:45) — not in the ten-minute version` (keep the heading and the italic stage direction) with:

```
You know this loop: plan, code, test, debug, revise. I spent that whole weekend going round it, and the step nobody teaches you is debug.

So here's what I did every time something broke. I wrote down what I saw, what I tried, what fixed it, and why that worked. Eight entries by Friday night, and that indentation error is one of them.

More than once, writing down exactly what I was seeing turned out to be most of the fix, because it forced me to look at it properly. Debugging isn't about being clever. It's about being organized while you're wrong.
```

- [ ] **Step 8: Commit**

```bash
git add docs/duet/class/index.html docs/duet/class/class.css docs/duet/class/script.md code/hackathon/pagetests/class.test.mjs
git commit -m "feat(class): card 12 shows the class's own loop, with the log as what debug looks like

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: Say the line that makes the advice credible

The teacher's section *You Already Know Enough to Start* opens with: "Nicholas has worked in software for many years as a product manager, but he has never been a professional programmer." That is the sentence that makes card 14 land, and it is not in the script.

**Files:**
- Modify: `docs/duet/class/script.md` (cards 1 and 14)
- Modify: `code/hackathon/pagetests/class.test.mjs` (script phrase list)

- [ ] **Step 1: Add the phrase to the script test**

In `code/hackathon/pagetests/class.test.mjs`, in the `script.md` test, replace:

```js
    'You already know enough to start', 'Eight entries by Friday night', '[click]', 'product manager']
```

with:

```js
    'You already know enough to start', 'Eight entries by Friday night', '[click]', 'product manager',
    'never been a professional programmer']
```

- [ ] **Step 2: Run it to watch it fail**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: 1 failing test, `script missing: never been a professional programmer`.

- [ ] **Step 3: Add the sentence to card 1**

In `docs/duet/class/script.md`, under `## 1 · Duet (1:00)`, replace:

```
I work as a product manager, which means I figure out what a piece of software should do, and then work with engineers and designers until it does it. For the last twelve years I've done that for fashion companies, the ones behind brands like Louis Vuitton and Uniqlo. I build the systems that produce the pictures you see when you shop online. For a long time that meant 3D, and lately it means AI.
```

with:

```
I work as a product manager, which means I figure out what a piece of software should do, and then work with engineers and designers until it does it. For the last twelve years I've done that for fashion companies, the ones behind brands like Louis Vuitton and Uniqlo. I build the systems that produce the pictures you see when you shop online. For a long time that meant 3D, and lately it means AI.

One thing to say up front, because it matters for the end of this talk. I have never been a professional programmer. I've worked alongside them for twelve years, and I've only started writing real code myself recently.
```

- [ ] **Step 4: Call back to it on card 14**

In `docs/duet/class/script.md`, under `## 14 · One piece of advice (0:45)`, replace:

```
[click] You already know enough to start. Turtle is a robot with the motor taken out.
```

with:

```
[click] You already know enough to start. Remember, I'm not a professional programmer either. Tracy is a robot with the motor taken out.
```

- [ ] **Step 5: Run the tests to watch them pass**

Run (from `code/hackathon`): `node --test 'pagetests/*.test.mjs'`
Expected: 159 pass, 0 fail.

- [ ] **Step 6: Commit**

```bash
git add docs/duet/class/script.md code/hackathon/pagetests/class.test.mjs
git commit -m "docs(class): the script says he has never been a professional programmer, and card 14 calls back to it

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: Say "comments", the word the class is practising

The teacher's section is *Why Comments and Communication Matter*, and two of her Key Takeaways name comments. The prepared answer covers naming, plans, tests and describing — but never uses the word, and the deck has no comment on screen except an inert `# e.g.` line.

**Files:**
- Modify: `docs/duet/class/index.html` (card 7's robot panel comment)
- Modify: `docs/duet/class/talk.md` (the communication answer)
- Modify: `docs/duet/class/script.md` (one sentence on card 7)
- Modify: `code/hackathon/pagetests/class.test.mjs` (card 7 verbatim panel)

- [ ] **Step 1: Update the robot panel's expected text**

In `code/hackathon/pagetests/class.test.mjs`, in the `Act 2` test, replace:

```js
  const robot = [
    'stroke = points_from_claude()', '# e.g. [(0, 0), (40, 0), (40, 40)]', 'x, y = stroke[0]',
```

with:

```js
  const robot = [
    'stroke = points_from_claude()', '# Claude picks the shape; we just walk it', 'x, y = stroke[0]',
```

- [ ] **Step 2: Run it to watch it fail**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: 1 failing test, `robot panel verbatim`.

- [ ] **Step 3: Make the comment say *why*, not *what***

In `docs/duet/class/index.html`, in card 7's robot panel, replace:

```
# e.g. [(0, 0), (40, 0), (40, 40)]
```

with:

```
# Claude picks the shape; we just walk it
```

- [ ] **Step 4: Run the tests to watch them pass**

Run (from `code/hackathon`): `node --test 'pagetests/*.test.mjs'`
Expected: 159 pass, 0 fail.

- [ ] **Step 5: Point at it in the script**

In `docs/duet/class/script.md`, under `## 7 · It's just points (1:30)`, after the paragraph ending "That's the only difference that matters.", add:

```
And see that line with the hash in front of it? That's a comment. The computer skips it. It's there for a person. Notice it doesn't repeat what the code says; it says why the code is like that.
```

- [ ] **Step 6: Name comments in the prepared answer**

In `docs/duet/class/talk.md`, in the section `## Carolina's question: why communication matters when people build together`, replace:

```
You also say what something should do before you build it. I wrote a plan for these slides before I made a single one, so when I disagreed with myself later, the plan was there to argue with. And my tests are really just sentences: this card shows four pictures, this button says Go. If somebody breaks one of those sentences, the computer says so immediately.
```

with:

```
Then there are comments, which you're writing right now. Here's the rule I'd give you: the code already says what it does, so a comment should say why it's like that. "Add 5 to the height" is a useless comment. "Add 5 so the pen clears the marker tray" is the one that saves somebody an hour.

You also say what something should do before you build it. I wrote a plan for these slides before I made a single one, so when I disagreed with myself later, the plan was there to argue with. And my tests are really just sentences: this card shows four pictures, this button says Go. If somebody breaks one of those sentences, the computer says so immediately.
```

- [ ] **Step 7: Commit**

```bash
git add docs/duet/class/index.html docs/duet/class/script.md docs/duet/class/talk.md code/hackathon/pagetests/class.test.mjs
git commit -m "docs(class): the deck carries a real comment, and the answer says what a comment is for

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Rebuild the Q&A around the questions they actually asked

The prepared list was guesswork and it missed. The teacher recorded six questions; only one ("did you write all the code") was prepped. This replaces the speculative list with the real one, answered.

**Files:**
- Modify: `docs/duet/class/talk.md` (the `## Likely questions` section)
- Modify: `code/hackathon/pagetests/class.test.mjs` (the talk.md assertions)

- [ ] **Step 1: Update the talk.md test**

In `code/hackathon/pagetests/class.test.mjs`, in the `talk.md is the run-of-show` test, replace:

```js
  for (const line of ['Did you write all the code?', 'Could I build this?', 'Did it ever hit anything?']) assert.ok(t.includes(line), `Q&A missing: ${line}`);
```

with:

```js
  for (const line of ['Did you write all the code?', 'How did Claude and the robot communicate?',
    'Did you use an AI agent, APIs, or something else?', 'How do you manage your time and stay organized?',
    'What is different about working alone versus with a team?', 'How long have you been coding?']) {
    assert.ok(t.includes(line), `Q&A missing: ${line}`);
  }
```

- [ ] **Step 2: Run it to watch it fail**

Run (from `code/hackathon`): `node --test pagetests/class.test.mjs`
Expected: 1 failing test, `Q&A missing: How did Claude and the robot communicate?`.

- [ ] **Step 3: Replace the Likely questions section**

In `docs/duet/class/talk.md`, replace everything from the line `## Likely questions` to the end of the file with:

```markdown
## Likely questions

The first six are the ones students actually asked on 2026-09-22, in the order the teacher recorded them. Answer them in your own words; these are the facts to hit.

- **How do you manage your time and stay organized when a problem is hard?** I split the two days into two-hour sprints, and I deliberately spent the first one not building. I wrote down what the arm could do, what I actually wanted to make, and what would be finished by Saturday. The thinking time is the part people skip.
- **What is different about working alone versus with a team?** Alone you're never blocked waiting for anybody, and you can change your mind in a second. But nobody catches your bad idea, and nobody knows what you meant at two in the morning. That's why I wrote things down: I was my own teammate.
- **How long have you been coding?** I've worked in software for twelve years, but as a product manager, not a programmer. I've only been writing real code myself for about a year, and I still look things up constantly.
- **How did Claude and the robot communicate?** They never talked to each other. My Python program is the go-between. It sends the photo to Claude over the internet and gets back two sentences and a list of points; then it sends those points to the arm, also over the internet, using Viam's library.
- **Did you use an AI agent, APIs, or something else?** Both, in different places. During the talk, each turn is one plain API call: photo goes out, answer comes back, nothing autonomous. While I was building it, I used Claude as an agent that could read my files and write code with me, which is how one person got it done in two days.
- **How do comments and communication help when several people work on the same project?** See the written answer above. The short version: the code says what, a comment says why, and everything else — names, plans, tests — exists so the next person doesn't have to guess.
- **Did you write all the code?** I designed it and decided everything. Claude wrote a lot of it with me. I still had to understand every piece to fix it when it broke, and it broke a lot. That's the job now: knowing what to build, and knowing when it's wrong.
- **How much did it cost?** The arm was lent for the weekend. The AI part cost less than lunch. The Claude I write code with is a monthly subscription.
- **Could I build this?** The drawing part, yes, this month, with Tracy. The robot part is the same code with a motor.
- **Did it ever hit anything?** Never a person or the table. It did crush the pen on the board once; that's the story on card 9. The software knows where the table and wall are and plans around them, and there's a big red emergency-stop button.
- **Can it draw me?** No. It doesn't copy what it sees; it adds one thing to what you drew, with one green marker, in simple shapes.
- **Is it going to take artists' jobs?** It can't start a drawing. It can only answer one. Every piece needs a person's first mark.
- **What would you do next?** Let you teach it your own drawing style from a stack of your sketches.
```

- [ ] **Step 4: Run the tests to watch them pass**

Run (from `code/hackathon`): `node --test 'pagetests/*.test.mjs'`
Expected: 159 pass, 0 fail.

- [ ] **Step 5: Commit**

```bash
git add docs/duet/class/talk.md code/hackathon/pagetests/class.test.mjs
git commit -m "docs(class): the Q&A prep is the six questions students actually asked, answered

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: Ship it to the Desktop and rehearse

**Files:**
- Modify: `~/Desktop/Duet class talk/` (the presenting copy)

- [ ] **Step 1: Full suite**

Run (from `code/hackathon`): `node --test 'pagetests/*.test.mjs'` → 159 pass. Then `/Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/code/hackathon/.venv/bin/python -m pytest -q` → 186 passed.

- [ ] **Step 2: Walk all fourteen cards**

Open `http://localhost:8792/class/index.html?v=201#1` and step through with the right arrow, including every reveal. Confirm: card 7 says Tracy in the headline and on the left label; card 12 shows the five-step loop with DEBUG highlighted; no card's content crosses its frame; the only console error is the `img/medal.jpg` 404 if the photo is absent from the worktree copy.

- [ ] **Step 3: Refresh the Desktop copy**

```bash
SRC="/Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/.worktrees/class-deck/docs/duet/class"
DEST="$HOME/Desktop/Duet class talk"
cp "$SRC/index.html" "$SRC/class.css" "$SRC/class.js" "$DEST/deck/class/"
cp "$SRC/script.md" "$DEST/Script.md"
cp "$SRC/talk.md" "$DEST/Run of show.md"
```

- [ ] **Step 4: Confirm the Desktop copy is the new one**

```bash
grep -c "Tracy" "$HOME/Desktop/Duet class talk/deck/class/index.html"
grep -c "PLAN" "$HOME/Desktop/Duet class talk/deck/class/index.html"
```
Expected: `2` and `1`.

- [ ] **Step 5: Decide the card 3 captions, or drop the card**

The four clip captions under card 3 have been blank since the deck was built, and `script.md` still has four `_(your line about clip N)_` placeholders. Either write the four lines now (one short phrase each: what that team's arm did), or open the deck with `?cut=10` tomorrow, which removes card 3 entirely. Do not present card 3 with empty captions and improvise a third time.

- [ ] **Step 6: Open it the way it will be presented**

```bash
open "$HOME/Desktop/Duet class talk/1 — Open the presentation.html"
```
Press **F**, then walk it once with a timer running, reading from `Script.md`. Note the elapsed time at card 8 — that is the halfway marker. If card 8 lands past 8 minutes, use the paragraphs marked *(skip if you're running long)*.

- [ ] **Step 7: Commit and push**

```bash
git push
```
Then open a PR against `main` and squash-merge it, the same way as PRs #15, #17 and #19.

---

## What is deliberately not in this plan

- **A new "think before you execute" card.** The two-hour-sprint material earned a full section in the teacher's notes and a graded reflection question, so it belongs on a slide eventually. But adding a fifteenth card the night before means renumbering every counter, the cut list, the SPECS model in the tests and the script's timings. It is now the first prepared Q&A answer instead, which is where it came from. Do it properly after tomorrow.
- **A "how professional teams communicate" card** (brief → user stories → tasks). Same reasoning; it is a strong slide and a weak thing to build tonight.
- **Cutting the medal, the clips or the trigger story.** They did not appear in her write-up, but absence from a study aid is not evidence they failed in the room. Keep them for tomorrow and decide with a second data point.

## Assumption worth checking before you start

This plan assumes tomorrow is **a different class or section**. If it is the same students who saw the talk on 2026-09-22, the right move is not a tightened repeat — it is a different session built on their reflection questions, and this plan is the wrong shape. Confirm before Task 1.
