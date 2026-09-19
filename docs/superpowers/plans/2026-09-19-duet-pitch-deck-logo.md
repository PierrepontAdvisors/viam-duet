# Duet Pitch Deck Frame Wash and Toy Logo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lighten the ground inside every card's frame and replace the "Duet" word (header, footer line, card 2) with a vector alphabet-block logo.

**Architecture:** One `<symbol id="logo">` in the deck's SVG defs, referenced with `<use>` at three CSS sizes; ink parts use `currentColor` so a single rule turns the logo white on the black card. A `.wash` layer sits between the plate texture and the frame. No script changes.

**Tech Stack:** HTML, CSS, inline SVG, Node test runner, headless Chrome.

**Spec:** `docs/superpowers/specs/2026-09-19-duet-pitch-deck-logo-design.md`.

---

### Task 1: Failing test

**Files:** Modify `code/hackathon/pagetests/pitch.test.mjs` (append)

- [ ] **Step 1: Append**

```js
test('the toy logo replaces the Duet word, and every frame has a wash', () => {
  const h = read('index.html');
  const sym = h.slice(h.indexOf('<symbol id="logo"'), h.indexOf('</symbol>', h.indexOf('<symbol id="logo"')));
  assert.ok(sym.length > 0, 'symbol #logo exists');
  assert.equal((sym.match(/<rect /g) || []).length, 4, 'four blocks');
  for (const ch of ['>D<', '>U<', '>E<', '>T<']) assert.ok(sym.includes(ch), `block letter ${ch}`);
  assert.ok(sym.includes('currentColor'), 'ink parts use currentColor');
  const sections = h.split(/<section class="card /).slice(1);
  sections.forEach((s, i) => {
    assert.ok(/class="wordmark"[^>]*>\s*<svg class="logo/.test(s), `card ${i + 1} header logo`);
    assert.ok(s.includes('class="wash"'), `card ${i + 1} wash`);
    if (i !== 5) {
      assert.ok(/class="band foot">\s*<svg class="logo foot-logo/.test(s), `card ${i + 1} footer logo`);
      assert.ok(!s.includes('Viam Fine Motor Skills · 2026'), `card ${i + 1} footer line replaced`);
    }
  });
  assert.ok(sections[5].includes('viam-server owns the arm'), 'card 6 keeps the strip');
  assert.ok(/class="name"[^>]*>\s*<svg class="logo/.test(sections[1]), 'card 2 large logo');
  const css = read('deck.css');
  assert.ok(css.includes('.wash {') && css.includes('.plate-black .wash'), 'wash rules');
  assert.ok(css.includes('.plate-black .logo'), 'logo turns white on black');
});
```

- [ ] **Step 2: Run** `cd code/hackathon && node --test pagetests/pitch.test.mjs` → 16 pass, 1 fail (`symbol #logo exists`).

---

### Task 2: CSS

**Files:** Modify `docs/duet/pitch/deck.css`

- [ ] **Step 1: After the `.plate-black .frame` rule, add**

```css
/* wash: the inside of the frame is calmer than the margin */
.wash { position: absolute; inset: var(--frame-inset); border-radius: var(--paper-radius); background: rgba(255, 255, 255, .22); pointer-events: none; }
.plate-cream .wash { background: rgba(255, 255, 255, .12); }
.plate-black .wash { background: rgba(0, 0, 0, .35); }

/* logo: four toy blocks, ink parts in currentColor */
.logo { display: block; color: var(--ink); }
.plate-black .logo { color: #fff; }
.wordmark .logo { height: 3.2cqw; width: auto; }
.foot-logo { height: 2.4cqw; width: auto; }
.name .logo { width: 22cqw; height: auto; }
```

- [ ] **Step 2: Run the tests** → still 1 fail (markup pending). Commit `feat(pitch): frame wash and logo sizes`.

---

### Task 3: Markup

**Files:** Modify `docs/duet/pitch/index.html`

- [ ] **Step 1: Add the symbol inside `<defs>`, after the `s-haring` symbol**

```html
    <!-- the Duet logo: four toy alphabet blocks and a marker squiggle; ink parts in currentColor -->
    <symbol id="logo" viewBox="0 0 320 130">
      <g transform="rotate(-6 52 64)"><rect x="20" y="32" width="64" height="64" rx="12" fill="#ffd400" stroke="currentColor" stroke-width="5"/><text x="52" y="66" font-family="Fredoka, 'Chalkboard SE', sans-serif" font-weight="700" font-size="46" text-anchor="middle" dominant-baseline="central" fill="currentColor">D</text></g>
      <g transform="rotate(4 124 64)"><rect x="92" y="32" width="64" height="64" rx="12" fill="#e5322d" stroke="currentColor" stroke-width="5"/><text x="124" y="66" font-family="Fredoka, 'Chalkboard SE', sans-serif" font-weight="700" font-size="46" text-anchor="middle" dominant-baseline="central" fill="currentColor">U</text></g>
      <g transform="rotate(-3 196 64)"><rect x="164" y="32" width="64" height="64" rx="12" fill="#1f4fd6" stroke="currentColor" stroke-width="5"/><text x="196" y="66" font-family="Fredoka, 'Chalkboard SE', sans-serif" font-weight="700" font-size="46" text-anchor="middle" dominant-baseline="central" fill="currentColor">E</text></g>
      <g transform="rotate(5 268 64)"><rect x="236" y="32" width="64" height="64" rx="12" fill="#17a34a" stroke="currentColor" stroke-width="5"/><text x="268" y="66" font-family="Fredoka, 'Chalkboard SE', sans-serif" font-weight="700" font-size="46" text-anchor="middle" dominant-baseline="central" fill="currentColor">T</text></g>
      <path d="M40 118 q10 -10 20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0 t20 0" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round"/>
    </symbol>
```

- [ ] **Step 2: In every card**, after the `<img class="plate-img" ...>` line insert `<div class="wash" aria-hidden="true"></div>`; replace `<span class="wordmark" data-el="card N wordmark">Duet</span>` with `<span class="wordmark" data-el="card N wordmark"><svg class="logo" role="img" aria-label="Duet"><use href="#logo"/></svg></span>`; on cards 1 to 5 and 7 replace `<span class="strip" data-el="card N footer">Viam Fine Motor Skills · 2026</span>` (card 5's is `data-el="card 5 footer line"`) with `<svg class="logo foot-logo" role="img" aria-label="Duet" data-el="card N footer logo"><use href="#logo"/></svg>`; on card 2 replace `<h1 class="name display" data-el="card 2 wordmark large">Duet</h1>` with `<h1 class="name" data-el="card 2 wordmark large"><svg class="logo" role="img" aria-label="Duet"><use href="#logo"/></svg></h1>`. These are mechanical; a Python script with exact string replacements does them in one pass.

- [ ] **Step 3: Run the full suite** `node --test 'pagetests/*.test.mjs'` → `fail 0`. Commit `feat(pitch): toy-block Duet logo in header, footer and card 2; wash inside the frame`.

---

### Task 4: Renders

- [ ] Render cards 1, 2, 6, 7 with headless Chrome at 1280 by 720 over file:// into `code/hackathon/captures/pitch-N.png` (same command as the grid plan) and check: the wash lightens the inside of the frame while the margin keeps full colour; the logo reads at header and footer size; card 7's logo has white keylines; card 2's column fits above the footer. Lower the card 2 logo width one step (20cqw) if it does not. Commit any CSS tuning with `fix(pitch): ...`.
