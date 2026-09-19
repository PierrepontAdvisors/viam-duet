# Duet Pitch Deck Icons and Motion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Icons and Viam lines on card 6 with simpler copy, a fourth "your own artist" module on card 5, and a staggered toy-pop entrance for everything inside the frame.

**Architecture:** Five SVG symbols join the defs; card 5 and card 6 markup is rewritten inside their `.content`; CSS adds the module head row, the step layout, the pills and one keyframe with nth-child delays. No script changes.

**Spec:** `docs/superpowers/specs/2026-09-19-duet-pitch-deck-icons-motion-design.md`.

### Task 1: Tests (Modify `code/hackathon/pagetests/pitch.test.mjs`)

- [ ] In the copy test replace `'Viam camera component.', 'Claude Opus 5.', 'Viam motion service.',` and `'viam-server owns the arm', 'app.viam.com',` with the list below; in the master-page test delete the `sections[5].includes('viam-server owns the arm')` assertion; in the logo test replace the `if (i !== 5) { ... }` block with its two inner assertions unconditionally and delete the `card 6 keeps the strip` assertion. Then append:

```js
test('card 6 steps carry icons and Viam lines, card 5 has four modules, motion is defined', () => {
  const h = read('index.html');
  for (const id of ['i-look', 'i-think', 'i-answer', 'i-draw', 'i-own']) {
    assert.ok(h.includes(`<symbol id="${id}"`), `symbol ${id}`);
    assert.ok(h.includes(`href="#${id}"`), `${id} is used`);
  }
  const sections = h.split(/<section class="card /).slice(1);
  assert.equal((sections[4].match(/class="paper mod/g) || []).length, 4, 'card 5 has four modules');
  assert.ok(sections[4].includes('Your own artist') && sections[4].includes('>Next<'), 'fourth module is marked Next');
  assert.equal((sections[5].match(/class="viam caption"/g) || []).length, 4, 'card 6 has four Viam lines');
  assert.ok(!sections[5].includes('class="paper mod num"'), 'numbers row removed');
  const css = read('deck.css');
  assert.match(css, /@keyframes pop/);
  assert.match(css, /prefers-reduced-motion: reduce\)[^}]*\{[^}]*\.card\.active \* \{ animation: none !important; \}/);
});
```

New copy entries:

```js
    'The camera on the wrist photographs the board.', 'Viam · the camera component streams colour and depth from the wrist.',
    'Claude reads the drawing and decides what to add.', 'Viam · the frame reaches Claude through the Python SDK.',
    "The artist's style turns that idea into strokes.", "Viam · board millimetres map into the machine's world frame.",
    'The arm draws them, planned safely around the table.', 'Viam · the motion service plans every move around the table and wall.',
    'Your own artist', 'Bold comic-book lines with halftone dots', 'Describe a style in one sentence. Duet answers in it.',
```

### Task 2: Symbols (Modify `docs/duet/pitch/index.html`, after `</symbol>` of `#logo`)

```html
    <!-- step icons: thick round ink strokes, one plate colour each -->
    <symbol id="i-look" viewBox="0 0 100 100"><g fill="none" stroke="#111" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><path d="M50 16 v-9 M24 26 l-6 -6 M76 26 l6 -6"/><path d="M10 56 q40 -40 80 0 q-40 40 -80 0 z" fill="#1f4fd6"/><circle cx="50" cy="56" r="13" fill="#fff"/><circle cx="50" cy="56" r="6" fill="#111" stroke="none"/></g></symbol>
    <symbol id="i-think" viewBox="0 0 100 100"><g fill="none" stroke="#111" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><path d="M32 62 q-16 0 -16 -13 q0 -12 12 -13 q2 -14 18 -14 q12 0 16 8 q14 -4 18 8 q12 2 10 13 q-2 11 -15 11 z" fill="#ffd400"/><circle cx="28" cy="76" r="5" fill="#ffd400"/><circle cx="18" cy="88" r="3" fill="#ffd400"/></g></symbol>
    <symbol id="i-answer" viewBox="0 0 100 100"><g fill="none" stroke="#111" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><path d="M34 72 l36 -36 l12 12 l-36 36 l-16 4 z" fill="#17a34a"/><path d="M62 44 l12 12"/><path d="M10 90 q8 -10 16 0 t16 0 t16 0"/></g></symbol>
    <symbol id="i-draw" viewBox="0 0 100 100"><g fill="none" stroke="#111" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><rect x="12" y="76" width="40" height="12" rx="4" fill="#e5322d"/><path d="M32 76 l10 -32 l30 -14" stroke-width="9"/><circle cx="42" cy="44" r="6" fill="#e5322d"/><circle cx="72" cy="30" r="6" fill="#e5322d"/><path d="M72 30 l14 12 l-4 6"/></g></symbol>
    <symbol id="i-own" viewBox="0 0 100 100"><g fill="none" stroke="#111" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"><path d="M22 78 l40 -40 l10 10 l-40 40 l-14 4 z" fill="#ff7a00"/><path d="M56 44 l10 10"/><path d="M76 14 v16 M68 22 h16 M88 40 v8 M84 44 h8"/></g></symbol>
```

### Task 3: Card 5 and card 6 content (Modify `docs/duet/pitch/index.html`)

Card 5: replace the `<ul class="mods three"> ... </ul>` with

```html
      <ul class="mods four">
        <li class="paper mod" data-el="card 5 lesson — Haring"><div class="mod-head"><svg class="sample" viewBox="0 0 100 60"><use href="#s-haring" width="100" height="60"/></svg><span class="caption">Haring</span></div><p class="body">One continuous outline, then motion ticks. Your blob becomes a figure.</p></li>
        <li class="paper mod" data-el="card 5 lesson — Mondrian"><div class="mod-head"><svg class="sample" viewBox="0 0 100 60"><use href="#s-mondrian" width="100" height="60"/></svg><span class="caption">Mondrian</span></div><p class="body">Your mark's edges run out to a grid. You start seeing the rectangle in everything.</p></li>
        <li class="paper mod" data-el="card 5 lesson — Van Gogh"><div class="mod-head"><svg class="sample" viewBox="0 0 100 60"><use href="#s-vangogh" width="100" height="60"/></svg><span class="caption">Van Gogh</span></div><p class="body">Dashes stream around your mark like water around a rock.</p></li>
        <li class="paper mod own" data-el="card 5 lesson — your own artist"><div class="mod-head"><svg class="icon" viewBox="0 0 100 100" aria-hidden="true"><use href="#i-own"/></svg><span class="caption">Your own artist</span><span class="pill next">Next</span></div><span class="pill prompt" data-el="card 5 prompt example">"Bold comic-book lines with halftone dots"</span><p class="body">Describe a style in one sentence. Duet answers in it.</p></li>
      </ul>
```

Card 6: replace everything from `<ol class="mods four">` through the closing `</ul>` of the numbers with

```html
      <ol class="mods four">
        <li class="step" data-el="card 6 step — Look"><div class="paper mod node"><div class="mod-head"><svg class="icon" viewBox="0 0 100 100" aria-hidden="true"><use href="#i-look"/></svg><h3 class="body">Look</h3></div><p class="body">The camera on the wrist photographs the board.</p></div><p class="viam caption" data-el="card 6 Viam line — Look">Viam · the camera component streams colour and depth from the wrist.</p></li>
        <li class="step" data-el="card 6 step — Understand"><div class="paper mod node"><div class="mod-head"><svg class="icon" viewBox="0 0 100 100" aria-hidden="true"><use href="#i-think"/></svg><h3 class="body">Understand</h3></div><p class="body">Claude reads the drawing and decides what to add.</p></div><p class="viam caption" data-el="card 6 Viam line — Understand">Viam · the frame reaches Claude through the Python SDK.</p></li>
        <li class="step" data-el="card 6 step — Answer"><div class="paper mod node"><div class="mod-head"><svg class="icon" viewBox="0 0 100 100" aria-hidden="true"><use href="#i-answer"/></svg><h3 class="body">Answer</h3></div><p class="body">The artist's style turns that idea into strokes.</p></div><p class="viam caption" data-el="card 6 Viam line — Answer">Viam · board millimetres map into the machine's world frame.</p></li>
        <li class="step" data-el="card 6 step — Draw"><div class="paper mod node"><div class="mod-head"><svg class="icon" viewBox="0 0 100 100" aria-hidden="true"><use href="#i-draw"/></svg><h3 class="body">Draw</h3></div><p class="body">The arm draws them, planned safely around the table.</p></div><p class="viam caption" data-el="card 6 Viam line — Draw">Viam · the motion service plans every move around the table and wall.</p></li>
      </ol>
```

and card 6's footer strip becomes `<span class="strip" data-el="card 6 footer">Nicholas Fjellberg Swerdlowe &middot; Viam Fine Motor Skills Hackathon &middot; 2026</span>`.

### Task 4: CSS (Modify `docs/duet/pitch/deck.css`)

Delete the `.node p`, `.num`, `.num b`, `.num span` rules. Add after `.closing`:

```css
/* module head: drawing or icon beside the name; steps on card 6 carry a Viam line under the box */
.mod-head { display: flex; align-items: center; gap: var(--s1); min-width: 0; }
.mod-head .sample { width: 6cqw; height: 3.6cqw; flex: none; }
.icon { width: 4cqw; height: 4cqw; flex: none; display: block; }
.mods.four .mod .body { line-height: 1.25; }
.pill.next { padding: .2cqw .8cqw; background: var(--yellow); margin-left: auto; }
.pill.prompt { align-self: flex-start; text-align: left; font-weight: 600; }
.step { min-width: 0; display: flex; flex-direction: column; gap: var(--s1); }
.step .node { flex: 1; }
.viam { font-weight: 600; padding: 0 .4cqw; }

/* entrance: everything inside the frame pops in, in reading order, when a card becomes active */
@keyframes pop { from { opacity: 0; transform: translateY(1cqw) scale(.92); } 70% { opacity: 1; transform: translateY(0) scale(1.02); } to { opacity: 1; transform: none; } }
.card.active :is(.kicker, .wordmark, .split .words > :not(.line), .split .figure, .triptych .module, .modules .lead, .modules .mods > *, .modules .closing, .foot > *) {
  animation: pop .45s cubic-bezier(.2, .7, .3, 1) both; animation-delay: calc(var(--i, 2) * 80ms); }
.card.active .kicker { --i: 0; }
.card.active .wordmark { --i: 1; }
.card.active :is(.split .words > :nth-child(1), .triptych .m1, .modules .lead) { --i: 2; }
.card.active :is(.split .words > :nth-child(2), .triptych .m2, .modules .mods > :nth-child(1)) { --i: 3; }
.card.active :is(.split .words > :nth-child(3), .triptych .m3, .modules .mods > :nth-child(2)) { --i: 4; }
.card.active :is(.split .words > :nth-child(4), .split .figure, .modules .mods > :nth-child(3)) { --i: 5; }
.card.active .modules .mods > :nth-child(4) { --i: 6; }
.card.active :is(.modules .closing, .foot > *) { --i: 7; }
@media (prefers-reduced-motion: reduce) { .card.active * { animation: none !important; } }
```

### Task 5: Verify

- [ ] `node --test 'pagetests/*.test.mjs'` → `fail 0`; render cards 5 and 6 (and 1, 2 for the motion's final state) with headless Chrome; check the four modules fit above the footer on card 5, the Viam lines sit under each box on card 6, icons read at size; commit.
