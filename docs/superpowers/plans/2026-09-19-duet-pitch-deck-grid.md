# Duet Pitch Deck Grid and Design System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put the seven existing cards of `docs/duet/pitch/` on one poster-frame master page and one 12-column grid, driven by design tokens (four type sizes, one spacing scale, one paper style), without changing copy, images, controls or developer mode.

**Architecture:** `deck.css` is rewritten around custom-property tokens and three template classes (`.split`, `.triptych`, `.modules`); per-card rules only place things on the grid. Each `<section class="card">` becomes a three-row grid (header band, content on 12 columns, footer band) with the frame, pattern and plate image as absolutely positioned layers behind. `deck.js` changes one line: the counter is written into every card's footer instead of one stage-level element. The Node tests gain a master-page check and a token check that fails on any font size outside the four tokens.

**Tech Stack:** Same as the deck: HTML, CSS with container units, classic JavaScript, Node 24 test runner, headless Chrome for screenshots.

**Spec:** `docs/superpowers/specs/2026-09-19-duet-pitch-deck-grid-design.md`. Grid arithmetic at any window size (everything is in cqw, so it is the same at every size): column width 5.9cqw, cols 1–7 span 48.5cqw, cols 9–12 span 27.2cqw, content area about 39cqw tall between the bands. Three spec values do not fit and are amended by this plan (Task 4 writes the amendment): the header wordmark is body size (headline size would steal 2cqw of height on every card); card 1's lines and card 7's headline are headline size, because display size wraps them past the content area (display is used once, for card 2's wordmark); the artist chips are horizontal pills (drawing beside the name) so three fit in the text column; the number cards use 1cqw vertical padding so card 6 fits with a two-line footer strip.

---

## File structure

```
docs/duet/pitch/
  deck.css     rewritten: tokens, master page, templates, per-card placement, developer-mode styles (Task 2)
  index.html   rewritten markup: same copy, images and data-el names, plus frame, header band, footer band per card (Task 3)
  deck.js      render() writes every .counter (Task 3)
code/hackathon/pagetests/pitch.test.mjs   two new tests (Task 1)
docs/superpowers/specs/2026-09-19-duet-pitch-deck-grid-design.md   amendment paragraph (Task 4)
```

Paths are relative to the repository root `/Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam`. Tests run from `code/hackathon`. Commits go on `feat/duet-design`; nothing under `code/hackathon/duet/` is staged.

---

### Task 1: The failing tests

**Files:**
- Modify: `code/hackathon/pagetests/pitch.test.mjs` (append)

- [ ] **Step 1: Append the master-page and token tests**

```js
test('every card carries the master page: frame, kicker, wordmark, footer with a counter', () => {
  const h = read('index.html');
  const kickers = ['01 · Thesis', '02 · What Duet is', '03 · One turn', '04 · Co-creation', '05 · Learning', '06 · How it works', '07 · The build'];
  const sections = h.split(/<section class="card /).slice(1);
  assert.equal(sections.length, 7);
  sections.forEach((s, i) => {
    assert.ok(s.includes('class="kicker"') && s.includes(kickers[i]), `card ${i + 1} kicker "${kickers[i]}"`);
    assert.equal((s.match(/class="wordmark"/g) || []).length, 1, `card ${i + 1} has one wordmark`);
    assert.ok(/class="band foot"/.test(s) && /class="counter"/.test(s), `card ${i + 1} footer with counter`);
    assert.ok(/class="frame"/.test(s), `card ${i + 1} frame`);
    assert.ok(/class="card (split|triptych|modules) /.test('class="card ' + s.slice(0, 40)), `card ${i + 1} uses a template class`);
  });
  assert.ok(sections[5].includes('viam-server owns the arm'), 'card 6 footer carries the Viam strip');
  assert.ok(!/id="counter"/.test(h), 'the stage-level counter is gone');
});

test('deck.css is built on the tokens: four type sizes, three templates, no stray font sizes', () => {
  const css = read('deck.css');
  for (const t of ['--display', '--headline', '--body', '--caption', '--s1', '--s4', '--paper-radius', '--paper-border', '--paper-pad', '--gutter', '--frame-inset']) {
    assert.ok(css.includes(t + ':'), `token ${t} is defined`);
  }
  for (const c of ['.split', '.triptych', '.modules', '.frame', '.kicker', '.wordmark', '.band']) assert.ok(css.includes(c), `rule ${c}`);
  const sizes = [...css.matchAll(/font-size:\s*([^;}]+)/g)].map((m) => m[1].trim());
  assert.ok(sizes.length >= 8, 'font sizes are set through the tokens');
  for (const v of sizes) assert.match(v, /^var\(--(display|headline|body|caption)\)$/, `font-size "${v}" is not a token`);
});
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd /Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/code/hackathon && node --test pagetests/pitch.test.mjs 2>&1 | grep -E "^(✖|ℹ (tests|pass|fail))" | grep -v "^✖ failing"
```

Expected: 14 pass, the 2 new tests fail (no kicker; `font-size "5.2cqw" is not a token`).

- [ ] **Step 3: Commit the tests**

```bash
cd /Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam && git add code/hackathon/pagetests/pitch.test.mjs && git commit -m "test(pitch): master page per card and token-only font sizes"
```

---

### Task 2: deck.css on tokens

**Files:**
- Rewrite: `docs/duet/pitch/deck.css`

- [ ] **Step 1: Replace deck.css with the token-based stylesheet**

```css
:root {
  /* colour */
  --yellow: #ffd400; --red: #e5322d; --blue: #1f4fd6; --green: #17a34a; --orange: #ff7a00; --cream: #fff4d6;
  --ink: #111; --paper: #fff; --robot: #1b8f3a; --human: #c62828;
  --story: "Fredoka", "Chalkboard SE", "Comic Sans MS", "Segoe Print", sans-serif;
  /* type: the only four sizes in the deck */
  --display: 6.4cqw; --headline: 4cqw; --body: 2.1cqw; --caption: 1.3cqw;
  /* space */
  --s1: 1cqw; --s2: 2cqw; --s3: 3cqw; --s4: 4cqw;
  /* paper */
  --paper-radius: 1.2cqw; --paper-border: .35cqw; --paper-pad: 1.6cqw;
  /* grid and master page */
  --gutter: 1.2cqw; --pad-x: 8cqw; --pad-y: 4.5cqw; --frame-inset: 3cqw; --frame-stroke: .45cqw;
  --tile: 160px;
}
html, body { margin: 0; height: 100%; background: #000; overflow: hidden; }
body { display: flex; align-items: center; justify-content: center; font-family: var(--story); color: var(--ink); }
.defs { position: absolute; width: 0; height: 0; overflow: hidden; }
h1, h2, h3, p, ul, ol, figure, figcaption { margin: 0; }
ul, ol { padding: 0; list-style: none; }

/* stage: a 16:9 box letterboxed in the viewport */
.stage { position: relative; width: min(100vw, 177.78vh); aspect-ratio: 16 / 9; overflow: hidden; background: #000;
         container-type: inline-size; user-select: none; cursor: default; }

/* card: plate behind, then the master page as three rows (header band, content, footer band) */
.card { position: absolute; inset: 0; box-sizing: border-box; background: var(--plate, #000); opacity: 0; pointer-events: none;
        transition: opacity .35s ease; display: grid; grid-template-rows: auto minmax(0, 1fr) auto; row-gap: var(--s2);
        padding: var(--pad-y) var(--pad-x); }
.card.active { opacity: 1; pointer-events: auto; }
.plate-yellow { --plate: var(--yellow); }
.plate-red    { --plate: var(--red); }
.plate-blue   { --plate: var(--blue); }
.plate-green  { --plate: var(--green); }
.plate-orange { --plate: var(--orange); }
.plate-cream  { --plate: var(--cream); }
.plate-black  { --plate: #000; color: #fff; }

/* plate layers: SVG squiggle tile (fallback) under the generated texture */
.pattern { position: absolute; left: 0; top: 0; width: calc(100% + var(--tile)); height: calc(100% + var(--tile));
           color: #000; opacity: .12; pointer-events: none; animation: drift 27s linear infinite; }
.plate-cream .pattern { opacity: .08; }
.plate-black .pattern { opacity: .35; }
.plate-img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; mix-blend-mode: multiply; opacity: .12;
             pointer-events: none; animation: breathe 30s ease-in-out infinite alternate; }
.plate-cream .plate-img { opacity: .08; }
.plate-black .plate-img { mix-blend-mode: normal; opacity: .35; }
.card.plated .pattern { display: none; }
@keyframes drift { to { transform: translate(calc(-1 * var(--tile)), calc(-1 * var(--tile))); } }
@keyframes breathe { to { transform: scale(1.04); } }
@media (prefers-reduced-motion: reduce) { .pattern, .plate-img { animation: none; } .card { transition: none; } }

/* frame */
.frame { position: absolute; inset: var(--frame-inset); border: var(--frame-stroke) solid var(--ink); border-radius: var(--paper-radius); pointer-events: none; }
.plate-black .frame { border-color: #fff; }

/* bands */
.band { position: relative; display: flex; justify-content: space-between; align-items: center; gap: var(--s2); min-width: 0; }
.kicker { font-size: var(--caption); font-weight: 700; line-height: 1; letter-spacing: .12em; text-transform: uppercase;
          padding: .6cqw 1.2cqw; background: var(--paper); color: var(--ink); border: var(--paper-border) solid var(--ink); border-radius: 999px; }
.wordmark { font-size: var(--body); font-weight: 700; line-height: 1; }
.foot { font-size: var(--caption); font-weight: 600; line-height: 1.2; }
.foot .strip { flex: 1; min-width: 0; }
.foot .counter { flex: none; }
.plate-black .wordmark, .plate-black .foot { color: #fff; }

/* content on the 12-column grid */
.content { position: relative; display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); column-gap: var(--gutter);
           align-items: center; min-height: 0; }

/* type roles */
.display  { font-size: var(--display);  font-weight: 700; line-height: 1.05; }
.headline { font-size: var(--headline); font-weight: 700; line-height: 1.1; }
.body     { font-size: var(--body);     font-weight: 600; line-height: 1.3; }
.caption  { font-size: var(--caption);  font-weight: 700; line-height: 1.2; }
.key { color: #fff; -webkit-text-stroke: .05em var(--ink); paint-order: stroke fill; }
.plate-black .key { color: var(--yellow); -webkit-text-stroke: 0; }

/* paper: one style for every card-like thing */
.paper { box-sizing: border-box; background: var(--paper); color: var(--ink); border: var(--paper-border) solid var(--ink);
         border-radius: var(--paper-radius); padding: var(--paper-pad); }
.pill { display: inline-block; padding: .5cqw 1.2cqw; border: var(--paper-border) solid var(--ink); border-radius: 999px;
        background: var(--paper); color: var(--ink); font-size: var(--caption); font-weight: 700; line-height: 1.2; text-align: center; }

/* template: split (words in cols 1-7, figure in cols 9-12) */
.split .words { grid-column: 1 / 8; min-width: 0; display: flex; flex-direction: column; gap: var(--s2); }
.split .figure { grid-column: 9 / 13; min-width: 0; }
.hero img { display: block; width: 100%; height: auto; aspect-ratio: 1; object-fit: cover; border-radius: calc(var(--paper-radius) - .4cqw); }
.thesis .words { gap: var(--s3); }
.thesis .line { opacity: 0; transform: translateY(1cqw); transition: opacity .4s ease, transform .4s ease; }
.card[data-build="1"] .line:nth-child(-n+1),
.card[data-build="2"] .line:nth-child(-n+2),
.card[data-build="3"] .line:nth-child(-n+3) { opacity: 1; transform: none; }
.beats { display: flex; flex-direction: column; gap: .4cqw; }
.chips { display: flex; gap: var(--gutter); }
.chip { flex: 1; min-width: 0; display: flex; align-items: center; gap: var(--s1); padding: var(--s1) var(--s1); }
.chip .sample { width: 5cqw; height: 3cqw; flex: none; }
.flipwrap { display: flex; flex-direction: column; align-items: center; gap: var(--s1); }
.flip img { display: block; height: 30cqw; width: auto; max-width: 100%; object-fit: contain; border-radius: calc(var(--paper-radius) - .4cqw); }
.credit { opacity: .85; }
.cta { color: var(--yellow); margin-top: var(--s1); }

/* template: triptych (three modules of four columns) */
.triptych .m1 { grid-column: 1 / 5; }
.triptych .m2 { grid-column: 5 / 9; }
.triptych .m3 { grid-column: 9 / 13; }
.module { min-width: 0; display: flex; flex-direction: column; align-items: center; gap: .6cqw; }
.photo img { display: block; height: 30cqw; width: auto; max-width: 100%; object-fit: contain; border-radius: calc(var(--paper-radius) - .4cqw); }
.cap { color: #fff; text-align: center; }
.bubble { position: relative; width: 100%; background: var(--yellow); padding: var(--s2); display: flex; flex-direction: column; gap: var(--s1); text-align: center; }
.bubble .adds { color: var(--robot); }
.bubble .pill { align-self: center; }
.bubble::before { content: ""; position: absolute; top: 50%; right: calc(-1 * var(--s2) - var(--paper-border)); transform: translateY(-50%);
                  border: 1.4cqw solid transparent; border-right: 0; border-left: var(--s2) solid var(--ink); }
.bubble::after  { content: ""; position: absolute; top: 50%; right: calc(-1 * var(--s2) + .55cqw); transform: translateY(-50%);
                  border: 1cqw solid transparent; border-right: 0; border-left: 1.5cqw solid var(--yellow); }

/* template: modules (headline across the top, equal paper modules under it, a closing line) */
.modules .content { display: flex; flex-direction: column; justify-content: center; gap: var(--s2); }
.modules .head { display: flex; flex-direction: column; gap: var(--s1); }
.mods { display: grid; column-gap: var(--gutter); row-gap: var(--gutter); }
.mods.three { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.mods.four  { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.mod { min-width: 0; display: flex; flex-direction: column; gap: .6cqw; }
.mod .sample { width: 9cqw; height: 5.4cqw; }
.node p { font-size: var(--caption); font-weight: 600; line-height: 1.25; }
.num { align-items: center; padding-top: var(--s1); padding-bottom: var(--s1); }
.num b { font-size: var(--headline); font-weight: 700; line-height: 1.1; }
.num span { font-size: var(--caption); font-weight: 600; line-height: 1.2; }
.closing { font-weight: 700; }

/* developer mode (press D), from ~/.claude/rules/common/preview-dev-mode.md */
body.dev [data-el]{outline:1px dashed rgba(39,67,227,.4);outline-offset:-1px;}
body.dev [data-el]:hover{outline:2px solid #2743E3;background:rgba(39,67,227,.07);cursor:crosshair;}
.dev-badge{position:fixed;top:12px;left:50%;transform:translateX(-50%);z-index:2147483000;display:none;
  padding:7px 14px;font:600 11px/1 system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;
  color:#fff;background:#2743E3;border-radius:999px;box-shadow:0 6px 20px rgba(39,67,227,.35);}
body.dev .dev-badge{display:block;}
.dev-label{position:fixed;z-index:2147483001;display:none;pointer-events:none;padding:4px 8px;
  font:600 11px/1 system-ui,sans-serif;color:#fff;background:#1B221D;border-radius:6px;white-space:nowrap;}
.dev-toast{position:fixed;bottom:70px;left:50%;transform:translateX(-50%) translateY(10px);z-index:2147483002;
  opacity:0;padding:9px 16px;font:600 12px/1 system-ui,sans-serif;color:#fff;background:#1B2FA8;border-radius:999px;
  transition:opacity .2s,transform .2s;pointer-events:none;}
.dev-toast.show{opacity:1;transform:translateX(-50%) translateY(0);}
```

- [ ] **Step 2: Run the tests**

```bash
cd /Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/code/hackathon && node --test pagetests/pitch.test.mjs 2>&1 | grep -E "^(✖|ℹ (tests|pass|fail))" | grep -v "^✖ failing"
```

Expected: the token test passes; only the master-page test still fails (index.html is unchanged so far). The earlier CSS test still passes because `.plate-img`, `.card.plated .pattern`, `@keyframes drift`, the reduced-motion rule, `--yellow`, `--blue` and `.dev-badge` are all present.

- [ ] **Step 3: Commit**

```bash
cd /Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam && git add docs/duet/pitch/deck.css && git commit -m "feat(pitch): deck.css on design tokens, poster-frame master page, three templates"
```

---

### Task 3: index.html on the master page, deck.js counters

**Files:**
- Rewrite: `docs/duet/pitch/index.html` (the `<svg class="defs">` block is unchanged and kept verbatim)
- Modify: `docs/duet/pitch/deck.js` (render and the DOMContentLoaded lookup)

- [ ] **Step 1: Replace everything from `<div class="stage"` to the closing `</div>` of the stage with the new cards**

The `<head>` (favicon, both stylesheets), the `<svg class="defs">` block, the developer-mode elements and the two script tags stay exactly as they are. Copy, image paths and existing `data-el` names are unchanged; the new elements add "card N kicker", "card N wordmark", "card N footer".

```html
<div class="stage" data-el="stage">

  <section class="card split thesis plate-yellow" data-card="1" data-el="card 1 — thesis">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="img/plate-1.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 1 kicker">01 · Thesis</span><span class="wordmark" data-el="card 1 wordmark">Duet</span></header>
    <div class="content">
      <div class="words">
        <p class="line headline" data-el="card 1 line 1">Anyone can now study with the greatest minds in history.</p>
        <p class="line headline" data-el="card 1 line 2">Nobody could make art with them.</p>
        <p class="line headline" data-el="card 1 line 3">Until <span class="key">today</span>.</p>
      </div>
      <figure class="paper hero figure" data-el="card 1 hero — figure with a book and a marker"><img src="img/hero-thesis.jpg" alt=""></figure>
    </div>
    <footer class="band foot"><span class="strip" data-el="card 1 footer">Viam Fine Motor Skills · 2026</span><span class="counter">1 / 7</span></footer>
  </section>

  <section class="card split what plate-red" data-card="2" data-el="card 2 — what Duet is">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="img/plate-2.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 2 kicker">02 · What Duet is</span><span class="wordmark" data-el="card 2 wordmark">Duet</span></header>
    <div class="content">
      <div class="words">
        <h1 class="name display" data-el="card 2 wordmark large">Duet</h1>
        <p class="sub headline" data-el="card 2 subtitle">A robot arm that draws <span class="key">with</span> you.</p>
        <ul class="beats body">
          <li data-el="card 2 beat 1">You make a mark.</li>
          <li data-el="card 2 beat 2">It looks, understands, and answers.</li>
          <li data-el="card 2 beat 3">In the hand of an artist you choose.</li>
        </ul>
        <div class="chips">
          <figure class="paper chip" data-el="card 2 chip — Van Gogh"><svg class="sample" viewBox="0 0 100 60"><use href="#s-vangogh" width="100" height="60"/></svg><figcaption class="caption">Van Gogh</figcaption></figure>
          <figure class="paper chip" data-el="card 2 chip — Mondrian"><svg class="sample" viewBox="0 0 100 60"><use href="#s-mondrian" width="100" height="60"/></svg><figcaption class="caption">Mondrian</figcaption></figure>
          <figure class="paper chip" data-el="card 2 chip — Keith Haring"><svg class="sample" viewBox="0 0 100 60"><use href="#s-haring" width="100" height="60"/></svg><figcaption class="caption">Keith Haring</figcaption></figure>
        </div>
      </div>
      <figure class="paper hero figure" data-el="card 2 hero — person and robot arm drawing together"><img src="img/hero-duet.jpg" alt=""></figure>
    </div>
    <footer class="band foot"><span class="strip" data-el="card 2 footer">Viam Fine Motor Skills · 2026</span><span class="counter">2 / 7</span></footer>
  </section>

  <section class="card triptych turn plate-blue" data-card="3" data-el="card 3 — one turn">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="img/plate-3.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 3 kicker">03 · One turn</span><span class="wordmark" data-el="card 3 wordmark">Duet</span></header>
    <div class="content">
      <div class="module m1" data-el="card 3 photo — your mark">
        <figure class="paper photo"><img src="img/turn-01-human.jpg" alt="The visitor's red mark on the board"></figure>
        <p class="cap caption">Your mark</p>
      </div>
      <div class="module m2">
        <div class="paper bubble body" data-el="card 3 speech bubble">
          <p class="sees" data-el="card 3 speech bubble — sees">A big bold amoeba-like creature with loops and eye-holes sprawls across the board.</p>
          <p class="adds" data-el="card 3 speech bubble — adds">I'll add a small green spiral accent inside the lower loop body to give the creature a pulsing core.</p>
          <span class="pill" data-el="card 3 badge — latency">8 s to look and decide</span>
        </div>
      </div>
      <div class="module m3" data-el="card 3 photo — the answer">
        <figure class="paper photo"><img src="img/turn-01-robot.jpg" alt="The board after the robot's green spiral"></figure>
        <p class="cap caption">Duet answers</p>
      </div>
    </div>
    <footer class="band foot"><span class="strip" data-el="card 3 footer">Viam Fine Motor Skills · 2026</span><span class="counter">3 / 7</span></footer>
  </section>

  <section class="card split cocreate plate-green" data-card="4" data-el="card 4 — co-creation">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="img/plate-4.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 4 kicker">04 · Co-creation</span><span class="wordmark" data-el="card 4 wordmark">Duet</span></header>
    <div class="content">
      <div class="words">
        <h2 class="headline" data-el="card 4 headline">Everyone leaves with a one-of-a-kind piece, made with a <span class="key">partner</span>.</h2>
        <p class="under body" data-el="card 4 line">Six exchanges. Two artists. One of them was a robot.</p>
      </div>
      <div class="figure flipwrap">
        <figure class="paper photo flip" data-el="card 4 flipbook image"><img id="flip" src="img/turn-00-start.jpg" alt="The board, turn by turn"></figure>
        <span class="pill" id="flipLabel" data-el="card 4 flipbook counter">start</span>
      </div>
    </div>
    <footer class="band foot"><span class="strip" data-el="card 4 footer">Viam Fine Motor Skills · 2026</span><span class="counter">4 / 7</span></footer>
  </section>

  <section class="card modules learn plate-orange" data-card="5" data-el="card 5 — learning">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="img/plate-5.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 5 kicker">05 · Learning</span><span class="wordmark" data-el="card 5 wordmark">Duet</span></header>
    <div class="content">
      <div class="head"><h2 class="headline" data-el="card 5 headline">And you learn their language by <span class="key">answering back</span>.</h2></div>
      <ul class="mods three">
        <li class="paper mod" data-el="card 5 lesson — Haring">
          <svg class="sample" viewBox="0 0 100 60"><use href="#s-haring" width="100" height="60"/></svg>
          <span class="caption">Haring</span>
          <p class="body">One continuous outline, then motion ticks. Your blob becomes a figure.</p>
        </li>
        <li class="paper mod" data-el="card 5 lesson — Mondrian">
          <svg class="sample" viewBox="0 0 100 60"><use href="#s-mondrian" width="100" height="60"/></svg>
          <span class="caption">Mondrian</span>
          <p class="body">Your mark's edges run out to a grid. You start seeing the rectangle in everything.</p>
        </li>
        <li class="paper mod" data-el="card 5 lesson — Van Gogh">
          <svg class="sample" viewBox="0 0 100 60"><use href="#s-vangogh" width="100" height="60"/></svg>
          <span class="caption">Van Gogh</span>
          <p class="body">Dashes stream around your mark like water around a rock.</p>
        </li>
      </ul>
      <p class="closing body" data-el="card 5 footer">You don't study the technique. You have a conversation in it.</p>
    </div>
    <footer class="band foot"><span class="strip" data-el="card 5 footer line">Viam Fine Motor Skills · 2026</span><span class="counter">5 / 7</span></footer>
  </section>

  <section class="card modules how plate-cream" data-card="6" data-el="card 6 — how it works">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle)"/></svg>
    <img class="plate-img" src="img/plate-6.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 6 kicker">06 · How it works</span><span class="wordmark" data-el="card 6 wordmark">Duet</span></header>
    <div class="content">
      <div class="head">
        <h2 class="headline" data-el="card 6 title">Look. Understand. Answer. Draw.</h2>
        <p class="sub body" data-el="card 6 subtitle"><span class="key">Viam</span> under every step.</p>
      </div>
      <ol class="mods four">
        <li class="paper mod node" data-el="card 6 node — Look"><h3 class="body">Look</h3><p>Viam camera component. RealSense colour and depth, aligned, from the wrist. The board is found again every turn.</p></li>
        <li class="paper mod node" data-el="card 6 node — Understand"><h3 class="body">Understand</h3><p>Claude Opus 5. One photo in, two sentences and strokes out.</p></li>
        <li class="paper mod node" data-el="card 6 node — Answer"><h3 class="body">Answer</h3><p>The artist's grammar styles the strokes. The planner clips and budgets them, in board millimetres mapped into Viam's world frame.</p></li>
        <li class="paper mod node" data-el="card 6 node — Draw"><h3 class="body">Draw</h3><p>Viam motion service. Every move planned around the table and wall obstacles, linear constraints on pen-down, arm and gripper components over the Python SDK.</p></li>
      </ol>
      <ul class="mods four">
        <li class="paper mod num" data-el="card 6 number — 8 s"><b>8 s</b><span>to look and decide</span></li>
        <li class="paper mod num" data-el="card 6 number — 2 mm"><b>2 mm</b><span>calibration</span></li>
        <li class="paper mod num" data-el="card 6 number — tests"><b>120</b><span>tests</span></li>
        <li class="paper mod num" data-el="card 6 number — direct moves"><b>0</b><span>direct arm moves</span></li>
      </ul>
    </div>
    <footer class="band foot"><span class="strip" data-el="card 6 Viam strip">viam-server owns the arm's control box &middot; machine configured in app.viam.com &middot; Python SDK from a laptop &middot; motion service with obstacles &middot; camera, arm, gripper components</span><span class="counter">6 / 7</span></footer>
  </section>

  <section class="card split build plate-black" data-card="7" data-el="card 7 — the build">
    <svg class="pattern" aria-hidden="true"><rect width="100%" height="100%" fill="url(#squiggle-bright)"/></svg>
    <img class="plate-img" src="img/plate-7.jpg" alt="" aria-hidden="true" onload="this.closest('.card').classList.add('plated')">
    <div class="frame" aria-hidden="true"></div>
    <header class="band head"><span class="kicker" data-el="card 7 kicker">07 · The build</span><span class="wordmark" data-el="card 7 wordmark">Duet</span></header>
    <div class="content">
      <div class="words">
        <h2 class="headline" data-el="card 7 headline"><span class="key">One person.</span> Two days. Claude and Viam.</h2>
        <p class="credit body" data-el="card 7 credit">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; September 2026</p>
        <p class="cta headline" data-el="card 7 footer — rig instruction">Draw one mark. Duet answers.</p>
      </div>
      <figure class="paper hero figure" data-el="card 7 hero — dancing figure beside the arm"><img src="img/hero-build.jpg" alt=""></figure>
    </div>
    <footer class="band foot"><span class="strip" data-el="card 7 footer">Viam Fine Motor Skills · 2026</span><span class="counter">7 / 7</span></footer>
  </section>

</div>
```

- [ ] **Step 2: Make deck.js write every counter**

In `docs/duet/pitch/deck.js`, change the variable line and `render`:

```js
  var state = { card: 1, build: 0 };
  var stage, counters, flipImg, flipLabelEl, cards;

  function render() {
    cards.forEach(function (el) {
      var n = parseInt(el.getAttribute('data-card'), 10);
      var active = n === state.card;
      el.classList.toggle('active', active);
      if (active) el.setAttribute('data-build', String(state.build));
    });
    counters.forEach(function (el) { el.textContent = state.card + ' / ' + CARDS; });
    if (parseHash(location.hash) !== state.card) history.replaceState(null, '', '#' + state.card);
  }
```

and in the `DOMContentLoaded` handler replace `counter = document.getElementById('counter');` with:

```js
    counters = Array.prototype.slice.call(document.querySelectorAll('.counter'));
```

- [ ] **Step 3: Run the whole page suite**

```bash
cd /Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/code/hackathon && node --test 'pagetests/*.test.mjs' 2>&1 | grep -E "^(✖|ℹ (tests|pass|fail))" | grep -v "^✖ failing"
```

Expected: `fail 0` (16 deck tests plus the page tests).

- [ ] **Step 4: Commit**

```bash
cd /Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam && git add docs/duet/pitch/index.html docs/duet/pitch/deck.js && git commit -m "feat(pitch): every card on the poster-frame master page and the 12-column grid"
```

---

### Task 4: Screenshots, alignment review, spec amendment

**Files:**
- Modify: `docs/superpowers/specs/2026-09-19-duet-pitch-deck-grid-design.md` (append)
- Possibly modify: `docs/duet/pitch/deck.css` (sizes only)

- [ ] **Step 1: Render all seven cards over file:// with headless Chrome**

```bash
cd /Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam && CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" && for n in 1 2 3 4 5 6 7; do "$CHROME" --headless=new --disable-gpu --hide-scrollbars --window-size=1280,720 --virtual-time-budget=3000 --screenshot="code/hackathon/captures/pitch-$n.png" "file:///Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/docs/duet/pitch/index.html#$n" >/dev/null 2>&1; done; ls -l code/hackathon/captures/pitch-*.png | awk '{print $5, $9}'
```

Expected: seven PNGs. Card 1 shows the frame, kicker, wordmark and hero with no lines yet (they reveal on advance).

- [ ] **Step 2: Review each screenshot against the grid**

Open each PNG (the Read tool shows it) and check:
- The frame is complete on every card, white on card 7, and nothing touches it.
- Kicker top-left and wordmark top-right sit on one line; footer text left and counter right on one line; the card 6 strip wraps to at most two lines.
- Split cards: the hero's top edge is level with the top of the text block; the chips on card 2 end exactly where the text column ends; nothing overflows into the footer.
- Card 3: the three modules are equal, the bubble tail points at "Duet answers", captions are under the photos.
- Cards 5 and 6: the modules are equal in width and align with the numbers below (card 6); node text is legible at 1280 wide.
- Card 7: white type readable over the 35 percent plate with no panel.

If text overflows the content area on a card, lower that card's largest text one token step (display to headline, headline to body) or reduce a gap from `--s3` to `--s2`; never introduce a new size. If the plate competes with the type, lower `.plate-img` opacity. Re-render and re-check after any change.

- [ ] **Step 3: Interactive check in the served copy**

```bash
cd /Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam/docs/duet/pitch && python3 -m http.server 8010 --bind 127.0.0.1
```

Open `http://127.0.0.1:8010/#1` in the built-in browser at 1280 by 720: Right three times reveals the lines; the counter in the footer reads `1 / 7` and follows the cards; `5`, `Home`, `End` jump; the flipbook cycles with its pill; `D` shows the badge and a click copies "card 3 kicker" without advancing. Stop the server afterwards.

- [ ] **Step 4: Amend the spec**

Append to `docs/superpowers/specs/2026-09-19-duet-pitch-deck-grid-design.md`:

```markdown
## 7. Amendments while building (2026-09-19 afternoon)

Measured on the grid (column 5.9cqw, content area about 39cqw tall between the bands), four values in sections 2 to 4 did not fit and were changed:

- The header wordmark is body size, not headline size; the header band is then as tall as the kicker pill and every card keeps 2cqw more content height.
- Card 1's three lines and card 7's headline and closing line are headline size. At display size they wrap past the content area in a seven-column words block. Display size is used once, for card 2's wordmark.
- The artist chips are horizontal pills (drawing 5 by 3cqw beside the name) so three fit in cols 1–7; "Keith Haring" wraps to two lines inside its chip.
- The number cards on card 6 use 1cqw vertical padding (the paper token's 1.6cqw elsewhere) so the nodes, numbers and a two-line footer strip fit together.
```

- [ ] **Step 5: Commit**

```bash
cd /Users/nicholasfjellbergswerdlowe/Dropbox/2026/PA/Viam && git add docs/duet/pitch/deck.css docs/superpowers/specs/2026-09-19-duet-pitch-deck-grid-design.md && git commit -m "docs(pitch): grid spec amended with the measured sizes; deck tuned after the screenshot pass"
```

If `deck.css` did not change in Step 2, commit only the spec with the same message.

---

## Self-review

**Spec coverage.** Section 2 master page: frame, header band with kicker texts and wordmark, footer band with event text and counter, card 6 strip in the footer, per-card counters written by `deck.js` (Tasks 2 and 3). Section 3 tokens: all defined in `:root` and used through `.display/.headline/.body/.caption`, `--s1..--s4`, the paper trio, plate opacities 12/8/35, key word unchanged (Task 2); the font-size test enforces "no other sizes" (Task 1). Section 4 templates: `.split` for cards 1, 2, 4, 7 with words in 1–7 and figure in 9–12; `.triptych` modules at 1–4, 5–8, 9–12 with the squared bubble and tail; `.modules` for 5 and 6 with equal modules and the numbers in the same four columns, arrows dropped (Tasks 2 and 3). Section 5 files and tests: the two new tests (Task 1), CSS rewrite (Task 2), markup and `deck.js` (Task 3), screenshots and review (Task 4). Section 6 out of scope respected: no copy or image changes, nothing under `duet/`.

**Placeholders.** None; both rewritten files are complete in the plan.

**Consistency.** Class names used in the markup (`band head`, `band foot`, `strip`, `counter`, `kicker`, `wordmark`, `frame`, `content`, `words`, `figure`, `hero`, `module m1..m3`, `photo`, `cap`, `bubble`, `pill`, `flipwrap`, `flip`, `head`, `mods three|four`, `mod`, `node`, `num`, `closing`, `beats`, `chips`, `chip`, `sample`, `line`, `credit`, `cta`, type roles `display|headline|body|caption`) all have rules in the Task 2 stylesheet. The Task 1 tests look for `class="kicker"`, `class="wordmark"`, `class="band foot"`, `class="counter"`, `class="frame"`, the template class right after `class="card `, the kicker texts, and `.split/.triptych/.modules/.frame/.kicker/.wordmark/.band` in the CSS, all of which Tasks 2 and 3 produce. `deck.js` uses `counters` consistently in the variable line, `render` and the lookup. The `#flip` and `#flipLabel` ids that `deck.js` reads are kept.
