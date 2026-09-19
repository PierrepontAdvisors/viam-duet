import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const DIR = fileURLToPath(new URL('../duet/static/', import.meta.url));
const read = (name) => readFileSync(DIR + name, 'utf8');

test('the welcome page sits inside the stage with the logo, the description and a disabled Start', () => {
  const h = read('index.html');
  const w = h.slice(h.indexOf('<section class="welcome"'), h.indexOf('</section>', h.indexOf('<section class="welcome"')));
  assert.ok(w.length > 0, 'welcome section');
  assert.ok(h.indexOf('<section class="welcome"') > h.indexOf('<div class="stage"') && h.indexOf('<section class="welcome"') < h.indexOf('<div class="dev-badge">'), 'inside the stage');
  assert.ok(w.includes('id="welcome"') && w.includes('href="#logo"'), 'id and logo');
  for (const line of ['A robot arm that draws', 'Draw one mark. Duet looks, understands, and answers in the hand of an artist.', 'Six exchanges. One of a kind. Yours to keep.']) assert.ok(w.includes(line), line);
  assert.match(w, /<button class="welcome-start" id="start"[^>]*disabled[^>]*>Getting ready…<\/button>/, 'Start starts disabled');
});

test('welcome styles: overlay under the panel, staggered pops, keyline word', () => {
  const css = read('duet.css');
  assert.match(css, /\.welcome \{[^}]*z-index: 4/);
  assert.match(css, /\.gear \{[^}]*z-index: 6/);
  assert.match(css, /\.welcome-inner > :nth-child\(3\) \{ animation-delay: 240ms; \}/);
  assert.ok(css.includes('.key {'), 'keyline word style');
});

test('ui.js wires the welcome: renderWelcome in renderAll, Start sends restart on a finished session', () => {
  const js = read('js/ui.js');
  assert.match(js, /const renderAll = \(\) => \{ renderChips\(\); renderBubble\(\); renderPanel\(\); renderWelcome\(\); \}/);
  assert.ok(js.includes("sendCommand('restart')"), 'restart command');
  assert.ok(js.includes('welcomeButton(') && js.includes('welcomeReturns(') && js.includes("$('home')"), 'uses the pure rules');
});
