/** Everything drawn over the picture: chips, the bubble and its placement, the panel, layers, keys. */
import { chipFor, bubbleForState, bubbleForShot, anchorFor, PLACEHOLDER_MS } from './story.js';
import { bubblePosition } from './geometry.js';

const $ = (id) => document.getElementById(id);
const store = {
  get(k, d) { try { const v = localStorage.getItem(`duet.${k}`); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(`duet.${k}`, JSON.stringify(v)); } catch { /* private window: fine */ } },
};
const LAYER_DEFAULTS = { robot: true, ink: true, caption: true, chips: true, board: false, clean: true, vector: false };
const LAYER_NODES = { robot: 'l-robot', ink: 'l-ink', board: 'l-board' };
const esc = (s) => String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

export function initUI(app, { sendSet, sendCommand, on }) {
  const view = { source: 'live', index: -1, playing: false, timer: null, thinkingSince: 0, strokeLocked: false, lastError: null, autoplayed: null };
  const stage = $('stage'), viewer = app.viewer;

  // ---- layers and colors ----
  function applyLayer(name, onOff) {
    if (name === 'caption') $('caption').classList.toggle('hidden', !onOff);
    else if (name === 'chips') { $('chips').classList.toggle('hidden', !onOff); $('count').parentElement.classList.toggle('hidden', !onOff); }
    else if (name === 'clean') { stage.classList.toggle('clean', onOff); $('mask').classList.toggle('hidden', !onOff); }
    else if (name === 'vector') stage.classList.toggle('vector', onOff);
    else $(LAYER_NODES[name]).classList.toggle('hidden', !onOff);
    document.querySelector(`[data-layer="${name}"]`).classList.toggle('on', onOff);
    store.set(`layer.${name}`, onOff);
  }
  for (const b of document.querySelectorAll('[data-layer]')) {
    const name = b.dataset.layer;
    applyLayer(name, store.get(`layer.${name}`, LAYER_DEFAULTS[name]));
    b.onclick = () => applyLayer(name, !b.classList.contains('on'));
  }
  const inkColor = $('ink-color'), strokeColor = $('stroke-color');
  inkColor.value = store.get('color.ink', '#111111'); stage.style.setProperty('--ink', inkColor.value);
  inkColor.oninput = () => { stage.style.setProperty('--ink', inkColor.value); store.set('color.ink', inkColor.value); };
  const lockedStroke = store.get('color.stroke', null);
  if (lockedStroke) { view.strokeLocked = true; strokeColor.value = lockedStroke; stage.style.setProperty('--stroke', lockedStroke); }
  strokeColor.oninput = () => { view.strokeLocked = true; stage.style.setProperty('--stroke', strokeColor.value); store.set('color.stroke', strokeColor.value); };

  // ---- chips ----
  function renderChips() {
    $('badge').classList.toggle('off', !app.connected);
    const st = app.state;
    if (!st) { $('state').textContent = app.connected ? 'Getting ready…' : 'Connecting…'; $('state').className = 'chip white'; return; }
    const c = chipFor(st.state);
    $('state').textContent = c.text; $('state').className = `chip ${c.tone}`;
    $('count').innerHTML = `Exchange <b>${st.turn}</b> of ${st.exchanges}`;
    $('go').classList.toggle('hidden', !(st.handoff === 'held' && st.state === 'human_turn'));
  }

  // ---- bubble ----
  function currentBubble() {
    const shot = view.source === 'shot' ? app.book.shots[view.index] : null;
    if (shot) return { ...bubbleForShot(shot.who, app.book.get(shot.turn)), record: app.book.get(shot.turn), who: shot.who, thinking: false };
    const st = app.state;
    if (!st) return { kind: 'speech', text: 'One moment…', record: null, who: 'start', thinking: false };
    const rec = app.book.get(st.turn), reseat = !!(app.dock && app.dock.reseat.length);
    const b = bubbleForState(st.state, rec, { reseat, elapsedMs: Date.now() - view.thinkingSince });
    const who = st.state === 'human_turn' || st.state === 'idle' || st.state === 'look' ? 'start' : (b.kind === 'thought' ? 'human' : 'robot');
    return { ...b, record: rec, who, thinking: b.kind === 'thought' && !(rec && rec.thought) };
  }
  function placeBubble(b) {
    if (!viewer.h) return;
    const anchor = viewer.boardToStage(anchorFor(b.who === 'start' ? 'start' : b.kind, b.record));
    const sub = $('caption'), cq = viewer.W / 100;
    const floor = document.body.classList.contains('controls') ? viewer.H - $('panel').offsetHeight - cq : viewer.H - 1.6 * cq;
    const pos = bubblePosition(anchor, viewer.quadStage, { W: viewer.W, H: viewer.H, bw: sub.offsetWidth, bh: sub.offsetHeight, topMin: 7 * cq, floor });
    sub.style.left = `${pos.x}px`; sub.style.top = `${pos.y}px`;
    $('bubble').classList.toggle('right', pos.onRight);
  }
  function renderBubble() {
    const b = currentBubble();
    $('bubble').classList.remove('speech', 'thought', 'thinking');
    $('bubble').classList.add(b.kind); if (b.thinking) $('bubble').classList.add('thinking');
    $('words').textContent = b.text;
    placeBubble(b);
  }
  setInterval(() => { if (view.source === 'live' && currentBubble().thinking) renderBubble(); }, PLACEHOLDER_MS);
  viewer.onRegister = () => placeBubble(currentBubble());

  // ---- sources and the loop ----
  function showLive() { stopLoop(); view.source = 'live'; viewer.showLive(); renderAll(); }
  function showShot(i) {
    const n = app.book.shots.length; if (!n) return;
    view.source = 'shot'; view.index = ((i % n) + n) % n; viewer.showShot(app.book.shots[view.index]); renderAll();
  }
  function step(i) {
    showShot(i);
    const wait = app.book.loopSchedule()[view.index] || 1000;
    view.timer = setTimeout(() => step(view.index + 1), wait);
  }
  function play() { if (view.playing || !app.book.shots.length) return; view.playing = true; step(0); }
  function stopLoop() { if (!view.playing) return; view.playing = false; clearTimeout(view.timer); }
  function togglePlay() { if (view.playing) { stopLoop(); renderPanel(); } else play(); }

  // ---- panel ----
  function toggleControls(force) {
    const onOff = document.body.classList.toggle('controls', force);
    $('gear').title = onOff ? '' : 'Show controls (C)';
    placeBubble(currentBubble());
  }
  $('gear').onclick = () => toggleControls(true); $('hide').onclick = () => toggleControls(false);
  $('b-live').onclick = showLive;
  $('b-prev').onclick = () => { stopLoop(); showShot(view.source === 'live' ? app.book.shots.length - 1 : view.index - 1); };
  $('b-next').onclick = () => { stopLoop(); showShot(view.source === 'live' ? 0 : view.index + 1); };
  $('b-play').onclick = togglePlay;
  const seg = (id, fn) => { $(id).onclick = (e) => { const v = e.target.dataset.v; if (v && !e.target.disabled) fn(v); }; };
  seg('crop-seg', v => viewer.setCrop(v === 'board'));
  seg('length-seg', v => sendSet({ length: v }));
  seg('handoff-seg', v => sendSet({ handoff: v }));
  seg('artist-seg', v => sendSet({ artist: v }));
  $('ex-minus').onclick = () => app.state && sendSet({ exchanges: Math.max(1, app.state.exchanges - 1) });
  $('ex-plus').onclick = () => app.state && sendSet({ exchanges: Math.min(10, app.state.exchanges + 1) });
  $('pause').onclick = () => sendCommand(app.state && app.state.state === 'paused' ? 'resume' : 'pause');
  $('pass').onclick = () => sendCommand('pass'); $('go').onclick = () => sendCommand('pass');
  $('clear').onclick = () => sendCommand('clear_error');
  const dir = $('direction'), energy = $('energy');
  const showDir = () => { $('direction-val').textContent = `${dir.value}°`; $('sun').style.setProperty('--dir', `${dir.value}deg`); };
  const showEnergy = () => { $('energy-val').textContent = (energy.value / 100).toFixed(2); };
  dir.oninput = showDir; dir.onchange = () => sendSet({ direction: +dir.value });
  energy.oninput = showEnergy; energy.onchange = () => sendSet({ energy: energy.value / 100 });

  function markSeg(id, value) { for (const b of $(id).children) b.classList.toggle('on', b.dataset.v === value); }
  function renderPanel() {
    const st = app.state;
    $('crop-seg').children[0].classList.toggle('on', !viewer.crop); $('crop-seg').children[1].classList.toggle('on', viewer.crop);
    $('b-live').classList.toggle('on', view.source === 'live');
    const shot = view.source === 'shot' ? app.book.shots[view.index] : null;
    $('pos').textContent = shot ? (shot.who === 'start' ? 'start · blank board' : `turn ${String(shot.turn).padStart(2, '0')} · ${shot.who}`) : 'live · wrist camera';
    $('b-prev').disabled = $('b-next').disabled = !app.book.shots.length;
    $('b-play').textContent = view.playing ? '■ Stop' : '▶ Play loop'; $('b-play').classList.toggle('on', view.playing);
    $('b-video').classList.toggle('hidden', !app.video); if (app.video) $('b-video').href = app.video.url;
    if (st) {
      markSeg('length-seg', st.length); markSeg('handoff-seg', st.handoff); markSeg('artist-seg', st.artist);
      for (const b of $('artist-seg').children) b.disabled = !st.artists.includes(b.dataset.v);
      $('ex').textContent = st.exchanges;
      $('pause').textContent = st.state === 'paused' ? 'Resume' : 'Pause'; $('pause').classList.toggle('on', st.state === 'paused');
      $('pass').classList.toggle('hidden', st.handoff !== 'held');
      if (document.activeElement !== dir) { dir.value = Math.round(st.direction); showDir(); }
      if (document.activeElement !== energy) { energy.value = Math.round(st.energy * 100); showEnergy(); }
    }
    renderStatus();
  }
  function renderStatus() {
    const st = app.state, ws = app.connected ? 'connected' : '<span class="err">reconnecting</span>';
    $('status1').innerHTML = st
      ? `state <b>${esc(st.state)}</b> · turn <b>${st.turn}</b> of <b>${st.exchanges}</b> · length <b>${esc(st.length)}</b> · handoff <b>${esc(st.handoff)}</b> · hand guard <b>${esc(st.hand_guard || '?')}</b> · error ${st.error ? `<span class="err">${esc(st.error)}</span>` : '<b>none</b>'} · ws ${ws}`
      : `waiting for the first state message · ws ${ws}`;
    const i = app.interpretation;
    $('status2').innerHTML = !i ? 'claude <b>idle</b>'
      : i.source === 'fallback' ? `claude <span class="err">fallback grammar</span> · ${esc(i.error || 'outline and ticks around the new mark')}`
      : `claude <b>${i.latency_s == null ? '?' : i.latency_s.toFixed(1)} s</b> · sees <b>${esc(i.sees)}</b> · adds <b>${esc(i.adds)}</b>`;
    const parts = [];
    if (app.dock) parts.push(`dock ${esc(Object.entries(app.dock.slots).map(([k, v]) => `${k}:${v}`).join(' ') || 'none')}` + (app.dock.reseat.length ? ` · <span class="err">reseat ${esc(app.dock.reseat.join(', '))}</span>` : ''));
    if (view.lastError && Date.now() - view.lastError.t < 5000) parts.push(`<span class="err">${esc(view.lastError.message)}</span>`);
    $('status3').innerHTML = parts.join(' · ');
  }
  const renderAll = () => { renderChips(); renderBubble(); renderPanel(); };

  // ---- keys and developer mode ----
  document.addEventListener('keydown', (e) => {
    if (e.target instanceof Element && e.target.matches('input, textarea, select')) return;
    if (e.key === 'ArrowLeft') { stopLoop(); showShot(view.source === 'live' ? app.book.shots.length - 1 : view.index - 1); }
    else if (e.key === 'ArrowRight') { stopLoop(); showShot(view.source === 'live' ? 0 : view.index + 1); }
    else if (e.key === ' ') { e.preventDefault(); togglePlay(); }
    else if (e.key === 'l' || e.key === 'L') showLive();
    else if (e.key === 'c' || e.key === 'C') toggleControls();
    else if (e.key === 'z' || e.key === 'Z') viewer.setCrop(!viewer.crop);
    else if (e.key === 'd' || e.key === 'D') { document.body.classList.toggle('dev'); if (!document.body.classList.contains('dev')) $('devLabel').style.display = 'none'; }
  });
  const label = $('devLabel'), toast = $('devToast'); let toastTimer = null;
  document.addEventListener('mousemove', (e) => {
    if (!document.body.classList.contains('dev')) { label.style.display = 'none'; return; }
    const t = e.target.closest ? e.target.closest('[data-el]') : null;
    if (!t) { label.style.display = 'none'; return; }
    label.textContent = t.getAttribute('data-el'); label.style.display = 'block';
    label.style.left = `${Math.min(e.clientX + 12, window.innerWidth - label.offsetWidth - 8)}px`; label.style.top = `${e.clientY + 14}px`;
  });
  document.addEventListener('click', (e) => {
    if (!document.body.classList.contains('dev')) return;
    const t = e.target.closest ? e.target.closest('[data-el]') : null; if (!t) return;
    e.preventDefault(); e.stopPropagation();
    const name = t.getAttribute('data-el');
    (navigator.clipboard ? navigator.clipboard.writeText(name) : Promise.reject()).catch(() => {});
    toast.textContent = `Copied: ${name}`; toast.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => toast.classList.remove('show'), 1400);
  }, true);

  // ---- messages ----
  on((msg) => {
    if (msg.type === 'state') {
      if (msg.state === 'capture' && !(app.book.get(msg.turn) || {}).thought) view.thinkingSince = Date.now();
      if (msg.state === 'finished' && view.autoplayed !== msg.session) { view.autoplayed = msg.session; setTimeout(() => { if (view.source === 'live') play(); }, 3000); }
      if (msg.state === 'human_turn' && msg.turn === 0 && view.source !== 'live') showLive();
    }
    if (msg.type === 'error') view.lastError = { message: msg.message, t: Date.now() };
    renderAll();
  });
  if (new URLSearchParams(location.search).get('view') === 'console') toggleControls(true);
  renderAll();
  return { showLive, showShot, play, stopLoop, toggleControls, renderAll };
}
