/** The diagnostics drawer's DOM: the status light, the header numbers, the timeline SVG, and the log table.
 *  Redraws once a second while open; the table only when an entry arrives, so it never flickers while read. */
import { WINDOW_MS, summarize, fold, clock, header, timeline } from './diag.js?v=ds6';

const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const VB_W = 1000, VB_H = 92, LABEL_W = 92, BAND_H = 8, TICK_H = 10;   // viewBox units
const BLINK_MS = 120;
const f1 = (n) => n.toFixed(1);
const toggled = (set, v) => { const out = new Set(set); if (out.has(v)) out.delete(v); else out.add(v); return out; };

export function initDiagView({ light, summary, svg, tbody }) {
  const view = { open: false, connected: false, entries: [], expanded: new Set(), timer: null, blinkTimer: null };

  function renderHeader() {
    const h = header(view.entries, Date.now(), view.connected);
    const since = h.sinceLastMs === null ? 'no message yet' : `${(h.sinceLastMs / 1000).toFixed(1)} s since last message`;
    summary.innerHTML = `socket <b class="${h.connected ? 'ok' : 'err'}">${h.connected ? 'connected' : 'reconnecting'}</b> · ${since}`
      + ` · <b>${h.received}</b> received · <b>${h.sent}</b> sent · <b>${h.reconnects}</b> reconnects · <b class="${h.dropped ? 'err' : ''}">${h.dropped}</b> dropped`;
  }

  function renderTimeline() {
    const { lanes, bands, ticks } = timeline(view.entries, Date.now(), WINDOW_MS, view.connected);
    const plotW = VB_W - LABEL_W, laneH = (VB_H - BAND_H - TICK_H) / lanes.length, bandY = VB_H - TICK_H - BAND_H;
    const px = (x) => LABEL_W + x * plotW;
    const parts = [];
    for (const tk of ticks) {
      parts.push(`<line class="tick" x1="${f1(px(tk.x))}" y1="0" x2="${f1(px(tk.x))}" y2="${bandY + BAND_H}"/>`);
      parts.push(`<text class="tick" x="${f1(px(tk.x))}" y="${VB_H - 2}" text-anchor="${tk.x >= 1 ? 'end' : 'middle'}">${esc(tk.label)}</text>`);
    }
    lanes.forEach((lane, i) => {
      const y = i * laneH, base = f1(y + laneH * 0.78);
      parts.push(`<text class="lane" x="0" y="${base}">${esc(lane.type)}</text>`);
      parts.push(`<line class="lane" x1="${LABEL_W}" y1="${f1(y + laneH / 2)}" x2="${VB_W}" y2="${f1(y + laneH / 2)}"/>`);
      for (const m of lane.marks) {
        parts.push(`<rect class="mark${lane.type === 'error' ? ' err' : ''}" x="${f1(px(m.x) - 1)}" y="${f1(y + 1)}" width="2" height="${f1(laneH - 2)}"/>`);
        if (m.label) parts.push(`<text class="mark" x="${f1(px(m.x) + 2.5)}" y="${base}">${esc(m.label)}</text>`);
      }
    });
    for (const b of bands) parts.push(`<rect class="band ${b.connected ? 'ok' : 'err'}" x="${f1(px(b.x0))}" y="${bandY}" width="${f1((b.x1 - b.x0) * plotW)}" height="${BAND_H}"/>`);
    svg.innerHTML = parts.join('');
  }

  function rowHtml(e) {
    const cls = ['row', e.dir === 'in' && (e.type === 'error' || !e.ok) ? 'err' : '', e.dir === 'out' ? 'out' : '', e.dir === 'ws' ? 'ws' : ''].filter(Boolean).join(' ');
    const row = `<tr class="${cls}" data-seq="${e.seq}"><td>${clock(e.t)}</td><td>${e.dir}</td><td>${esc(e.type)}</td><td>${e.turn ?? ''}</td><td>${e.size}</td><td title="${esc(summarize(e))}">${esc(summarize(e))}</td></tr>`;
    const detail = view.expanded.has(e.seq) && e.dir !== 'ws'
      ? `<tr class="detail" data-seq="${e.seq}"><td colspan="6"><pre>${esc(JSON.stringify(fold(e.raw), null, 2))}</pre></td></tr>` : '';
    return row + detail;
  }
  function renderTable() { tbody.innerHTML = [...view.entries].reverse().map(rowHtml).join(''); }
  tbody.addEventListener('click', (ev) => {
    const tr = ev.target.closest('tr.row'); if (!tr) return;
    const seq = +tr.dataset.seq, entry = view.entries.find(x => x.seq === seq);
    if (!entry || entry.dir === 'ws') return;
    view.expanded = toggled(view.expanded, seq);
    renderTable();
  });

  function tick() { renderHeader(); renderTimeline(); }
  function setOpen(onOff) {
    view.open = onOff;
    clearInterval(view.timer); view.timer = null;
    if (!onOff) return;
    tick(); renderTable();
    view.timer = setInterval(tick, 1000);
  }
  function setConnected(onOff) {
    view.connected = onOff;
    light.classList.toggle('on', onOff); light.title = onOff ? 'Socket connected' : 'Socket reconnecting';
    if (view.open) tick();
  }
  function blink() {
    light.classList.add('blink'); clearTimeout(view.blinkTimer);
    view.blinkTimer = setTimeout(() => light.classList.remove('blink'), BLINK_MS);
  }
  function onEntry(entries) { view.entries = entries; if (view.open) { renderTable(); tick(); } }
  return { setOpen, setConnected, blink, onEntry };
}
