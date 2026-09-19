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
  assert.match(css, /body\.controls \.corner, body\.diagnostics \.corner \{ display: none; \}/);
  assert.ok(!css.includes('body.controls .gear { display: none; }'), 'the old per-button hide is gone');
  assert.match(css, /\.diag \{[^}]*z-index: 5/);
  assert.match(css, /body\.diagnostics \.diag \{ display: flex; \}/);
  assert.ok(!/body\.diag[ .]/.test(css), 'the body class must not be the drawer class: body.diag would match .diag { display: none }');
  assert.match(css, /\.light \{[^}]*background: var\(--red\)/);
  assert.match(css, /\.light\.on \{ background: var\(--green\); \}/);
  assert.match(css, /\.light\.blink \{ background: var\(--yellow\); \}/);
  assert.match(css, /prefers-reduced-motion: reduce\) \{ \.light\.on\.blink \{ background: var\(--green\); \} \}/);
  assert.match(css, /\.diag-timeline \{[^}]*aspect-ratio: 1000 \/ 92/);
});

test('assets are versioned ds7 so open pages fetch the new scripts', () => {
  const h = read('index.html');
  assert.ok(!h.includes('?v=ds5') && !h.includes('?v=ds6'), 'no older version left');
  assert.match(h, /src="\/static\/js\/app\.js\?v=ds7"/);
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

test('app.js records every frame before dispatch, both socket events, and every sent command', () => {
  const js = read('js/app.js');
  assert.match(js, /import \{ append, frameEntry, sentEntry, socketEntry \} from '\.\/diag\.js\?v=ds7';/);
  assert.match(js, /import \{ initDiagView \} from '\.\/diagview\.js\?v=ds7';/);
  assert.match(js, /import \{ initUI \} from '\.\/ui\.js\?v=ds7';/);
  const onmessage = js.slice(js.indexOf('ws.onmessage'), js.indexOf('\n}', js.indexOf('ws.onmessage')));
  assert.ok(onmessage.indexOf('frameEntry(e.data, m, t, seq)') < onmessage.indexOf('if (m) handle(m)'), 'recorded before dispatch');
  assert.match(onmessage, /app\.diagView\.blink\(\)/);
  assert.match(js, /ws\.onopen = \(\) => \{[^\n]*socketEntry\('open', null, t, seq\)[^\n]*setConnected\(true\)/);
  assert.match(js, /ws\.onclose = \(e\) => \{[^\n]*socketEntry\('close', e\.code, t, seq\)[^\n]*setConnected\(false\)/);
  assert.match(js, /app\.ws\.send\(JSON\.stringify\(msg\)\);\n\s*record\(\(t, seq\) => sentEntry\(msg, t, seq\)\);/);
  assert.ok(js.indexOf('app.diagView = initDiagView(') < js.indexOf('app.ui = initUI('), 'the view exists before the UI needs it');
});

test('ui.js opens one drawer at a time, binds G and ?view=diag, and floors the bubble on whichever is open', () => {
  const js = read('js/ui.js');
  assert.match(js, /function toggleDiag\(force\) \{\n\s*const onOff = document\.body\.classList\.toggle\('diagnostics', force\);\n\s*if \(onOff\) document\.body\.classList\.remove\('controls'\);\n\s*app\.diagView\.setOpen\(onOff\);/);
  assert.match(js, /function toggleControls\(force\) \{\n\s*const onOff = document\.body\.classList\.toggle\('controls', force\);\n\s*if \(onOff\) closeDiag\(\);/);
  assert.match(js, /\$\('diag-gear'\)\.onclick = \(\) => toggleDiag\(true\); \$\('diag-hide'\)\.onclick = \(\) => toggleDiag\(false\);/);
  assert.match(js, /e\.key === 'g' \|\| e\.key === 'G'\) toggleDiag\(\)/);
  assert.match(js, /if \(view0 === 'diag'\) toggleDiag\(true\);/);
  assert.match(js, /const open = document\.body\.classList\.contains\('controls'\) \? \$\('panel'\) : document\.body\.classList\.contains\('diagnostics'\) \? \$\('diag'\) : null;/);
});
