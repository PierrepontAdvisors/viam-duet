import { test } from 'node:test';
import assert from 'node:assert/strict';
import { formatSeconds, fraction, Clock } from '../duet/static/js/clock.js';

const el = () => { const classes = new Set(['hidden']), vars = {}, dataset = {}; return { dataset, vars, textContent: '',
  classList: { add: (c) => classes.add(c), remove: (c) => classes.delete(c), contains: (c) => classes.has(c) }, style: { setProperty: (k, v) => { vars[k] = v; } } }; };

test('formatSeconds and fraction', () => {
  assert.equal(formatSeconds(0), '0.0 s'); assert.equal(formatSeconds(8432), '8.4 s'); assert.equal(formatSeconds(-5), '0.0 s');
  assert.equal(fraction(0, 1000), 0); assert.equal(fraction(250, 1000), 0.25); assert.equal(fraction(2000, 1000), 1); assert.equal(fraction(5, 0), 1);
});

test('Clock: start shows and counts, past the total the bar stays full, pause freezes and relabels, resume continues, stop hides', () => {
  let clock = 0;
  const timers = { set: (fn) => ({ fn }), clear: () => {} };
  const chip = el(), who = el(), time = el();
  const c = new Clock(chip, { who, time, now: () => clock, timers });
  c.start({ who: 'visitor', ms: 2000 });
  assert.ok(!chip.classList.contains('hidden')); assert.equal(chip.dataset.who, 'visitor'); assert.equal(who.textContent, 'Human'); assert.equal(time.textContent, '0.0 s');
  clock = 500; c.render(); assert.equal(chip.vars['--fill'], 0.25); assert.equal(time.textContent, '0.5 s');
  clock = 3000; c.render(); assert.equal(chip.vars['--fill'], 1); assert.equal(time.textContent, '3.0 s');
  c.pause(); assert.equal(chip.dataset.who, 'paused'); assert.equal(who.textContent, 'Paused');
  clock = 9000; c.render(); assert.equal(time.textContent, '3.0 s', 'frozen');
  c.resume(); assert.equal(chip.dataset.who, 'visitor'); assert.equal(who.textContent, 'Human');
  clock = 9500; c.render(); assert.equal(time.textContent, '3.5 s');
  c.start({ who: 'robot', ms: 1000 });
  assert.equal(chip.dataset.who, 'robot'); assert.equal(who.textContent, 'Robot'); assert.equal(time.textContent, '0.0 s');
  c.stop(); assert.ok(chip.classList.contains('hidden'));
  c.pause(); c.resume(); c.render(); assert.ok(chip.classList.contains('hidden'), 'idle calls do nothing');
});
