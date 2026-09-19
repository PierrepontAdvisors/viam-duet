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
  assert.match(t, /prefers-reduced-motion: reduce\)\s*\{\s*\.pop \{ animation: none; \}/);
  const css = read('duet.css');
  assert.ok(!/@import/.test(css), 'no imports');
  assert.ok(!/\.chip[^{]*\{[^}]*rotate\(/.test(css) && !/\.bubble[^{]*\{[^}]*rotate\(/.test(css), 'chips and bubbles sit square');
  assert.ok(css.includes('var(--paper-radius)') && css.includes('var(--frame-stroke)'), 'page uses the tokens');
});
