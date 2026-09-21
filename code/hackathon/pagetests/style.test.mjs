import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const DIR = fileURLToPath(new URL('../duet/static/', import.meta.url));
const read = (name) => readFileSync(DIR + name, 'utf8');

test('the page loads the design system and the embedded font, not Google Fonts', () => {
  const h = read('index.html');
  assert.match(h, /href="\/static\/tokens\.css(\?v=\w+)?"/, 'tokens.css linked');
  assert.match(h, /href="\/static\/fredoka\.css(\?v=\w+)?"/, 'fredoka.css linked');
  assert.match(h, /href="\/static\/duet\.css\?v=\w+"/, 'duet.css carries a cache-busting version');
  assert.ok(!h.includes('fonts.googleapis.com'), 'no network font');
  assert.ok(h.indexOf('tokens.css') < h.indexOf('duet.css'), 'tokens load before the page styles');
  assert.ok(!/\?v=ds8/.test(h), 'the page moved to v=ds9 with the drawing hand');
});

test('the page carries the mat, the logo symbol and the logo in the badge', () => {
  const h = read('index.html');
  assert.ok(h.includes('class="mat"'), 'mat wrapper');
  assert.ok(h.includes('<symbol id="logo"'), 'logo symbol');
  assert.match(h, /id="badge"[^>]*>\s*<svg class="logo" viewBox="0 0 320 130"/, 'logo inside #badge');
});

test('tokens.css defines the system and the pop; duet.css leans on it', () => {
  const t = read('tokens.css');
  for (const v of ['--yellow:', '--headline:', '--paper-radius:', '--frame-stroke:', '--story:']) assert.ok(t.includes(v), v);
  assert.match(t, /@keyframes pop/);
  assert.match(t, /\.pop \{ animation: pop [^;]*backwards; \}/, 'a finished pop releases the element for hover');
  assert.match(t, /prefers-reduced-motion: reduce\)\s*\{\s*\.pop \{ animation: none; \}/);
  const css = read('duet.css');
  assert.ok(!/@import/.test(css), 'no imports');
  assert.ok(!/\.chip \{[^}]*rotate\(/.test(css) && !/\.bubble(\.speech|\.thought)? \{[^}]*rotate\(/.test(css), 'chips and bubbles sit square at rest (hover may tilt)');
  assert.ok(css.includes('var(--paper-radius)') && css.includes('var(--frame-stroke)'), 'page uses the tokens');
});

test('buttons are toy presses: shadow at rest, lift on hover, squash on press, wiggle once when Start and Go arrive', () => {
  const css = read('duet.css');
  assert.match(css, /\.panel button, \.panel a \{ box-shadow: \.18cqw \.18cqw 0 var\(--ink\); \}/);
  assert.match(css, /\.panel button:not\(:disabled\):hover[^{]*\{[^}]*translate\(-\.12cqw, -\.12cqw\) rotate\(-1deg\)/);
  assert.match(css, /\.go:hover, \.go\.hover, \.welcome-start:not\(:disabled\):hover \{[^}]*box-shadow: \.7cqw \.7cqw 0 var\(--ink\)/);
  assert.match(css, /@keyframes wiggle/);
  assert.match(css, /\.go\.pop, \.welcome-start\.pop \{ animation: pop .*?, wiggle/);
  assert.match(css, /prefers-reduced-motion: reduce\) \{\s*button\.chip, \.gear, \.go, \.welcome-start, \.panel button, \.panel a \{ transition: none; \}/);
});

test('the demo hand: an element in the stage with the pointing-hand SVG, above the menu, out of the way of a real pointer, still under reduced motion', () => {
  const h = read('index.html');
  assert.match(h, /<div class="hand hidden" id="hand" data-el="demo hand">\s*<svg class="finger" viewBox="0 0 60 72" aria-hidden="true">/);
  assert.ok(h.includes('class="skin"') && h.includes('class="cuff"'), 'the hand has skin and a cuff');
  assert.ok(h.indexOf('id="hand"') > h.indexOf('id="artist-menu"') && h.indexOf('id="hand"') < h.indexOf('id="caption"'), 'after the CTA row, before the bubble');
  const css = read('duet.css');
  assert.match(css, /\.hand \{[^}]*z-index: 5;[^}]*pointer-events: none;/);
  assert.match(css, /\.hand\.press \{ transform: [^}]*scale\(\.88\)/);
  assert.match(css, /prefers-reduced-motion: reduce\) \{ \.hand \{ transition: none; \} \.hand\.press \{ transform: translate\(-1\.17cqw, -\.17cqw\); \} \}/);
  assert.ok(!css.includes('#artist-btn { pointer-events: none; }'), 'the picker takes clicks in replay mode');
});

test('the hand draws and is named: a marker in its SVG, a Visitor tag, a red pen layer; the robot dot has a Robot tag; the clock chip sits after the state chip', () => {
  const h = read('index.html');
  assert.match(h, /<svg class="finger" viewBox="0 0 60 72" aria-hidden="true">/, 'the finger is its own SVG');
  assert.match(h, /<svg class="marker" viewBox="0 0 60 72" aria-hidden="true">\s*<g transform="rotate\(-35 14 2\)">\s*<path d="M14 2[^"]*" fill="#111"\/>/, 'the marker: its own SVG, leaning from the tip at the hotspot');
  assert.ok(h.indexOf('class="marker"') > h.indexOf('class="finger"') && h.indexOf('class="marker"') < h.indexOf('class="tag">Visitor'), 'finger, then marker, then the tag');
  assert.match(h, /<span class="tag">Visitor<\/span>\s*<\/div>/, 'the Visitor tag ends the hand element');
  assert.match(h, /<span class="tag hidden" id="pen-tag" data-el="tag — robot pen">Robot<\/span>/);
  assert.match(h, /<g class="hand-ink" id="l-hand" data-el="layer — the hand's red trace"><path id="handpath"\/><circle id="handpen" r="2\.2"\/><\/g>/);
  assert.ok(h.indexOf('id="l-hand"') > h.indexOf('id="l-ghost"') && h.indexOf('id="l-hand"') < h.indexOf('</g>\n    </svg>'), 'inside the board fit, after the ghost');
  assert.match(h, /id="state"[^\n]*<\/span>\n\s*<button class="chip white clock hidden" id="clock" title="Pause or resume the piece" data-el="chip — turn clock">\s*<i class="fill"><\/i><b id="clock-who">Visitor<\/b> <span id="clock-time">0\.0 s<\/span>\s*<\/button>/);
  const css = read('duet.css');
  assert.match(css, /button\.chip:hover, button\.chip\.hover \{/); assert.match(css, /button\.chip:active, button\.chip\.active \{/);
  assert.match(css, /\.go:hover, \.go\.hover, \.welcome-start:not\(:disabled\):hover \{/); assert.match(css, /\.go:active, \.go\.active, \.welcome-start:not\(:disabled\):active \{/);
  assert.match(css, /\.hand \.marker \{ display: none; \} \.hand\.draw \.marker \{ display: block; \} \.hand\.draw \.finger \{ display: none; \}/, 'only the pen draws');
  assert.match(css, /\.hand \{[^}]*transition: left \.625s ease, top \.625s ease, transform \.15s ease/, 'the glide is a quarter slower');
  assert.match(css, /\.tag \{[^}]*pointer-events: none;[^}]*white-space: nowrap;/);
  assert.match(css, /\.hand \.tag \{ left: 3\.4cqw; top: 5\.4cqw; \}/); assert.match(css, /#pen-tag \{ z-index: 4; transform: translate\(1cqw, 1cqw\); \}/);
  assert.match(css, /\.clock \{ position: relative; overflow: hidden; \}/);
  assert.match(css, /\.clock \.fill \{[^}]*width: calc\(var\(--fill, 0\) \* 100%\);[^}]*background: var\(--human\);/);
  assert.match(css, /\.clock\[data-who="robot"\] \.fill \{ background: var\(--robot\); \}/);
  assert.match(css, /\.clock\[data-who="paused"\] \.fill \{ animation: blink 1s ease-in-out infinite; \}/);
  assert.match(css, /\.ov \.hand-ink path \{ stroke: var\(--human\); stroke-width: 1\.2; opacity: \.9; \} \.ov \.hand-ink circle \{ display: none; \}/);
});
