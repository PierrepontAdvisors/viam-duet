/** Speech and tones. Nothing is created until the person turns sound on, so the page is silent by default
 *  and the browser's autoplay rule is satisfied by that first click. */
const VOICE_PREFS = ['Samantha', 'Karen', 'Moira', 'Google UK English Female'];

export class Sound {
  constructor() { this.on = false; this.ctx = null; this.humNode = null; }

  enable(onOff) {
    this.on = onOff;
    if (onOff) {
      if (!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)();
      if (this.ctx.state === 'suspended') this.ctx.resume();
    } else {
      this.hum(false);
      if ('speechSynthesis' in window) speechSynthesis.cancel();
    }
  }

  voice() {
    if (!('speechSynthesis' in window)) return null;
    const voices = speechSynthesis.getVoices();
    return VOICE_PREFS.map(n => voices.find(v => v.name === n)).find(Boolean) || voices.find(v => v.lang && v.lang.startsWith('en')) || null;
  }

  speak(text) {
    if (!this.on || !text || !('speechSynthesis' in window)) return;
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.95; u.pitch = 1.1;
    const v = this.voice(); if (v) u.voice = v;
    speechSynthesis.speak(u);
  }

  tone(freq, dur, { type = 'sine', gain = 0.08, at = 0 } = {}) {
    if (!this.on || !this.ctx) return;
    const o = this.ctx.createOscillator(), g = this.ctx.createGain(), t = this.ctx.currentTime + at;
    o.type = type; o.frequency.value = freq;
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(gain, t + 0.01); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g).connect(this.ctx.destination);
    o.start(t); o.stop(t + dur + 0.02);
  }

  /** Two notes: rising for "your turn", falling-then-rising for "my turn". */
  chime(kind) {
    if (kind === 'yours') { this.tone(523, 0.18); this.tone(784, 0.3, { at: 0.16 }); }
    else { this.tone(392, 0.18); this.tone(523, 0.3, { at: 0.16 }); }
  }

  click() { this.tone(1400, 0.04, { type: 'square', gain: 0.03 }); }

  /** A quiet slow pulse while Claude is looking. */
  hum(onOff) {
    if (onOff && this.on && this.ctx && !this.humNode) {
      const o = this.ctx.createOscillator(), g = this.ctx.createGain(), lfo = this.ctx.createOscillator(), lg = this.ctx.createGain();
      o.frequency.value = 110; g.gain.value = 0.02; lfo.frequency.value = 0.6; lg.gain.value = 0.015;
      lfo.connect(lg).connect(g.gain); o.connect(g).connect(this.ctx.destination);
      o.start(); lfo.start();
      this.humNode = { o, lfo, g };
    }
    if (!onOff && this.humNode) {
      const { o, lfo, g } = this.humNode, t = this.ctx.currentTime;
      g.gain.linearRampToValueAtTime(0, t + 0.3); o.stop(t + 0.35); lfo.stop(t + 0.35);
      this.humNode = null;
    }
  }
}
