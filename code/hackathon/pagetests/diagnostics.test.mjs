import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const DIR = fileURLToPath(new URL('../duet/static/', import.meta.url));
const read = (name) => readFileSync(DIR + name, 'utf8');

test('the corner row holds the light, the gear and Controls, inside the stage', () => {
  const h = read('index.html');
  const i = h.indexOf('<div class="corner"');
  assert.ok(i > h.indexOf('<div class="stage"') && i < h.indexOf('<div class="panel"'), 'corner row before the panel, inside the stage');
  const row = h.slice(i, h.indexOf('</div>', i));
  assert.match(row, /<span class="light" id="light"/);
  assert.match(row, /<button class="gear icon" id="diag-gear" title="Diagnostics \(G\)" aria-label="Diagnostics"[^>]*>\s*<svg viewBox="0 0 24 24" aria-hidden="true">/);
  assert.match(row, /<button class="gear" id="gear" title="Show controls \(C\)"/);
  assert.ok(row.indexOf('id="light"') < row.indexOf('id="diag-gear"') && row.indexOf('id="diag-gear"') < row.indexOf('id="gear"'), 'light, gear, Controls in that order');
});

test('the drawer follows the panel with a header, the fixed-viewBox timeline and a six-column table', () => {
  const h = read('index.html');
  const i = h.indexOf('<section class="diag" id="diag"');
  assert.ok(i > h.indexOf('id="status3"') && i < h.indexOf('<div class="dev-badge">'), 'after the panel, before the dev badge');
  const d = h.slice(i, h.indexOf('</section>', i));
  assert.match(d, /<span class="lbl">Diagnostics<\/span>/);
  assert.match(d, /<span class="diag-summary" id="diag-summary"/);
  assert.match(d, /<button id="diag-hide"[^>]*>Hide<\/button>/);
  assert.match(d, /<svg class="diag-timeline" id="diag-timeline" viewBox="0 0 1000 92"/);
  assert.match(d, /<table class="log">\s*<thead><tr><th>time<\/th><th>dir<\/th><th>type<\/th><th>turn<\/th><th>size<\/th><th>summary<\/th><\/tr><\/thead><tbody id="diag-rows">/);
});

test('every data-el name in the page is unique', () => {
  const names = [...read('index.html').matchAll(/data-el="([^"]+)"/g)].map(m => m[1]);
  const dupes = names.filter((n, i) => names.indexOf(n) !== i);
  assert.deepEqual(dupes, []);
  for (const n of ['corner buttons', 'status light — socket', 'diagnostics toggle button', 'diagnostics drawer', 'diagnostics — summary', 'diagnostics — timeline', 'diagnostics — log', 'hide diagnostics button']) assert.ok(names.includes(n), n);
});

test('styles: the corner row hides under both drawers, the drawer shares the panel layer, the light has three looks', () => {
  const css = read('duet.css');
  assert.match(css, /\.corner \{[^}]*z-index: 6/);
  assert.match(css, /body\.controls \.corner, body\.diag \.corner \{ display: none; \}/);
  assert.ok(!css.includes('body.controls .gear { display: none; }'), 'the old per-button hide is gone');
  assert.match(css, /\.diag \{[^}]*z-index: 5/);
  assert.match(css, /body\.diag \.diag \{ display: flex; \}/);
  assert.match(css, /\.light \{[^}]*background: var\(--red\)/);
  assert.match(css, /\.light\.on \{ background: var\(--green\); \}/);
  assert.match(css, /\.light\.blink \{ background: var\(--yellow\); \}/);
  assert.match(css, /prefers-reduced-motion: reduce\) \{ \.light\.on\.blink \{ background: var\(--green\); \} \}/);
  assert.match(css, /\.diag-timeline \{[^}]*aspect-ratio: 1000 \/ 92/);
});

test('assets are versioned ds6 so open pages fetch the new scripts', () => {
  const h = read('index.html');
  assert.ok(!h.includes('?v=ds5'), 'no ds5 left');
  assert.match(h, /src="\/static\/js\/app\.js\?v=ds6"/);
});

test('diagview redraws the table only on entries, ticks once a second only while open, and escapes every cell', () => {
  const js = read('js/diagview.js');
  assert.match(js, /export function initDiagView\(\{ light, summary, svg, tbody \}\)/);
  assert.match(js, /return \{ setOpen, setConnected, blink, onEntry \};/);
  assert.match(js, /setInterval\(tick, 1000\)/);
  assert.ok(!/setInterval\(renderTable/.test(js), 'the table is not on the clock');
  assert.match(js, /light\.classList\.toggle\('on', onOff\)/);
  assert.match(js, /light\.classList\.add\('blink'\)/);
  assert.match(js, /esc\(summarize\(e\)\)/);
  assert.match(js, /esc\(JSON\.stringify\(fold\(e\.raw\), null, 2\)\)/);
});
