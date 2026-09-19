import { test } from 'node:test';
import assert from 'node:assert/strict';
import { welcomeButton, welcomeReturns, welcomePrompt, WELCOME_RETURN_MS, chipFor, bubbleForState, bubbleForShot, placeholderAt, PLACEHOLDERS, FIXED, TurnBook, anchorFor, feedLabel, ARTIST_INFO, artistName, pickerText } from '../duet/static/js/story.js';

test('chipFor gives the storybook words and tone per state, and a readable fallback', () => {
  assert.deepEqual(chipFor('human_turn'), { text: 'Your turn!', tone: 'green' });
  assert.deepEqual(chipFor('robot_draw'), { text: 'My turn! Hands off, please', tone: 'red' });
  assert.deepEqual(chipFor('paused'), { text: 'Paused', tone: 'red' });
  assert.deepEqual(chipFor('reseat_marker'), { text: 'reseat marker', tone: 'white' });
});

test('placeholders cycle every 1.5 seconds', () => {
  assert.equal(placeholderAt(0), PLACEHOLDERS[0]);
  assert.equal(placeholderAt(1600), PLACEHOLDERS[1]);
  assert.equal(placeholderAt(1500 * PLACEHOLDERS.length + 10), PLACEHOLDERS[0]);
});

test('bubbleForState: thinking shows a placeholder until the thought lands, then speaks the quip', () => {
  assert.deepEqual(bubbleForState('capture', null, { elapsedMs: 0 }), { kind: 'thought', text: PLACEHOLDERS[0] });
  assert.deepEqual(bubbleForState('interpret', { thought: 'Is that a cat?' }, {}), { kind: 'thought', text: 'Is that a cat?' });
  assert.deepEqual(bubbleForState('plan', { quip: 'A hat for the cat!' }, {}), { kind: 'speech', text: 'A hat for the cat!' });
  assert.deepEqual(bubbleForState('robot_draw', null, {}), { kind: 'speech', text: FIXED.noQuip });
  assert.deepEqual(bubbleForState('human_turn', null, {}), { kind: 'speech', text: FIXED.start });
  assert.deepEqual(bubbleForState('human_turn', null, { reseat: true }), { kind: 'speech', text: FIXED.reseat });
  assert.deepEqual(bubbleForState('finished', null, {}), { kind: 'speech', text: 'The end! Wipe the board for the next artist.' });
});

test('bubbleForShot follows the photo: thought on the human, speech on the robot', () => {
  assert.deepEqual(bubbleForShot('start', null), { kind: 'speech', text: FIXED.start });
  assert.deepEqual(bubbleForShot('human', { thought: 'Loops!' }), { kind: 'thought', text: 'Loops!' });
  assert.deepEqual(bubbleForShot('human', null), { kind: 'thought', text: FIXED.oldThought });
  assert.deepEqual(bubbleForShot('robot', { quip: 'Dance!' }), { kind: 'speech', text: 'Dance!' });
  assert.deepEqual(bubbleForShot('final', null), { kind: 'speech', text: FIXED.oldQuip });
});

test('TurnBook merges notes per turn and keeps shots in story order', () => {
  const b = new TurnBook();
  b.note(1, { thought: 'Hmm' }); b.note(1, { quip: 'Yes!' });
  assert.deepEqual(b.get(1), { thought: 'Hmm', quip: 'Yes!' }); assert.equal(b.get(2), null);
  b.addShot({ url: '/sessions/s/turn-01-robot.jpg', frame_url: null, turn: 1, who: 'robot', session: 's' });
  b.addShot({ url: '/sessions/s/turn-00-start.jpg', frame_url: null, turn: 0, who: 'start', session: 's' });
  const i = b.addShot({ url: '/sessions/s/turn-01-human.jpg', frame_url: null, turn: 1, who: 'human', session: 's' });
  assert.equal(i, 1);
  assert.deepEqual(b.shots.map(s => `${s.turn}-${s.who}`), ['0-start', '1-human', '1-robot']);
  b.addShot({ url: '/sessions/s/turn-01-robot.jpg', frame_url: '/sessions/s/turn-01-robot-frame.jpg', turn: 1, who: 'robot', session: 's' });
  assert.equal(b.shots.length, 3); assert.equal(b.shots[2].frame_url, '/sessions/s/turn-01-robot-frame.jpg');
  assert.equal(b.indexOf(1, 'human'), 1);
});

test('backfill lists every shot that should precede the latest one, with frame urls when the latest has one', () => {
  const b = new TurnBook();
  const latest = { url: '/sessions/s/turn-02-human.jpg', frame_url: '/sessions/s/turn-02-human-frame.jpg', turn: 2, who: 'human', session: 's' };
  const list = b.backfill(latest);
  assert.deepEqual(list.map(s => `${s.turn}-${s.who}`), ['0-start', '1-human', '1-robot']);
  assert.equal(list[1].url, '/sessions/s/turn-01-human.jpg'); assert.equal(list[1].frame_url, '/sessions/s/turn-01-human-frame.jpg');
  assert.equal(b.backfill({ ...latest, frame_url: null })[1].frame_url, null);
  assert.deepEqual(b.backfill({ ...latest, turn: 0, who: 'start' }), []);
});

test('loopSchedule is one second per shot with the last held two seconds', () => {
  const b = new TurnBook();
  for (const [t, w] of [[0, 'start'], [1, 'human'], [1, 'robot']]) b.addShot({ url: `/sessions/s/turn-0${t}-${w}.jpg`, frame_url: null, turn: t, who: w, session: 's' });
  assert.deepEqual(b.loopSchedule(), [1000, 1000, 2000]);
  assert.deepEqual(new TurnBook().loopSchedule(), []);
});

test('anchorFor points a thought at the new ink and a speech at the plan', () => {
  const rec = { new: [[[10, 10], [30, 10]]], plan: [[[100, 200]]] };
  assert.deepEqual(anchorFor('thought', rec), [20, 10]);
  assert.deepEqual(anchorFor('speech', rec), [100, 200]);
  assert.deepEqual(anchorFor('speech', null), [88, 120]);
  assert.deepEqual(anchorFor('start', rec), [88, 120]);
});

test('welcomeButton: ready only at your turn or after the end; waiting after Start on a finished session', () => {
  assert.deepEqual(welcomeButton(null), { label: 'Getting ready…', enabled: false });
  assert.deepEqual(welcomeButton('look'), { label: 'Getting ready…', enabled: false });
  assert.deepEqual(welcomeButton('human_turn'), { label: 'Start', enabled: true });
  assert.deepEqual(welcomeButton('finished'), { label: 'Start', enabled: true });
  assert.deepEqual(welcomeButton('finished', true), { label: 'Starting soon…', enabled: false });
  assert.deepEqual(welcomeButton('robot_draw'), { label: 'Getting ready…', enabled: false });
});

test('welcomeReturns: a fresh state after a finished or running session, never at first load or between fresh states', () => {
  assert.equal(welcomeReturns('finished', 'idle'), true);
  assert.equal(welcomeReturns('human_turn', 'look'), false);      // look follows every robot turn, it is not a new session
  assert.equal(welcomeReturns(null, 'idle'), false);
  assert.equal(welcomeReturns('idle', 'look'), false);
  assert.equal(welcomeReturns('finished', 'human_turn'), false);
  assert.equal(WELCOME_RETURN_MS, 8000);
});

test('welcomeReturns: look after a robot turn is not a fresh session', () => {
  assert.equal(welcomeReturns('robot_draw', 'look'), false);
  assert.equal(welcomeReturns('finished', 'start'), true);
  assert.equal(welcomeReturns('finished', 'idle'), true);
});

test('feedLabel names the picture source', () => {
  assert.equal(feedLabel('live'), 'live · wrist camera');
  assert.equal(feedLabel('held'), 'still · the robot is drawing');
  assert.equal(feedLabel('stale'), 'camera reconnecting…');
  assert.equal(feedLabel(undefined), 'live · wrist camera');
});

test('every artist has a name and a one-line description; unknown ids read as a capitalised id', () => {
  assert.deepEqual(Object.keys(ARTIST_INFO), ['abstract', 'mimic', 'haring', 'mondrian', 'vangogh', 'architect', 'designer', 'shader']);
  for (const [name, blurb] of Object.values(ARTIST_INFO)) { assert.ok(name.length >= 5); assert.ok(blurb.split(' ').length <= 6, blurb); }
  assert.equal(artistName('vangogh'), 'Van Gogh'); assert.equal(artistName('zorn'), 'Zorn'); assert.equal(artistName(''), '');
});

test('pickerText: opens on the human turn, labels the robot states with the turn artist, hides otherwise', () => {
  assert.deepEqual(pickerText('human_turn', 'abstract', null, null), { text: 'as Abstract ▾', open: true });
  assert.deepEqual(pickerText('human_turn', 'shader', 'mimic', null), { text: 'as Shader ▾', open: true });   // the setting, not the last turn
  assert.deepEqual(pickerText('capture', 'abstract', 'mimic', null), { text: 'Mimic is looking…', open: false });
  assert.deepEqual(pickerText('interpret', 'abstract', null, null), { text: 'Abstract is looking…', open: false });  // not known yet: the setting
  assert.deepEqual(pickerText('plan', 'abstract', 'shader', null), { text: 'Shader is drawing', open: false });
  assert.deepEqual(pickerText('robot_draw', 'abstract', 'architect', null), { text: 'Architect is drawing', open: false });
  for (const s of ['idle', 'start', 'look', 'finish', 'finished', 'paused']) assert.equal(pickerText(s, 'abstract', 'mimic', null), null, s);
});

test('pickerText while browsing: a robot photo names who drew it, anything else hides the picker', () => {
  assert.deepEqual(pickerText('human_turn', 'abstract', null, { who: 'robot', artist: 'designer' }), { text: 'Designer drew this', open: false });
  assert.equal(pickerText('human_turn', 'abstract', null, { who: 'robot', artist: null }), null);
  assert.equal(pickerText('human_turn', 'abstract', null, { who: 'human', artist: 'designer' }), null);
  assert.equal(pickerText('robot_draw', 'abstract', 'mimic', { who: 'start', artist: null }), null);
});

test('a full board at start: the wipe state instructs, the welcome prompts, and Start stays live', () => {
  assert.deepEqual(chipFor('wipe'), { text: 'Wipe the board', tone: 'red' });
  assert.deepEqual(bubbleForState('wipe', null, {}), { kind: 'speech', text: FIXED.wipe });
  assert.match(FIXED.wipe, /wipe/i); assert.match(FIXED.wipe, /Start/);
  assert.deepEqual(welcomeButton('wipe'), { label: 'Start', enabled: true });
  assert.equal(welcomePrompt('wipe', 0.348), 'The board is still 35% full. Wipe it clean, then press Start.');
  assert.equal(welcomePrompt('finished', 0.4), 'Wipe the board clean for the next artist, then press Start.');
  for (const s of ['idle', 'start', 'human_turn', 'robot_draw', 'paused', null]) assert.equal(welcomePrompt(s, 0.4), null, String(s));
  assert.match(bubbleForState('finished', null, {}).text, /wipe/i);
  assert.equal(welcomeReturns('start', 'wipe'), false);
});
