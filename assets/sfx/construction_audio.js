/**
 * PROCEDURAL CONSTRUCTION AUDIO — Generates construction sound effects
 * using Web Audio API. No external audio files needed.
 * 
 * Each sound is synthesized from oscillators + noise:
 *   hammer_hit:   Impulse + metallic resonance
 *   footstep:     Short noise burst + low thump
 *   power_tool:   Continuous sawtooth + noise (toggleable)
 *   gear_grind:   Granular metallic scraping
 *   concrete_pour: Filtered noise with slow LFO
 * 
 * Usage:
 *   const sfx = new ConstructionAudio();
 *   sfx.hammerHit();        // One-shot
 *   sfx.startSaw(); ... sfx.stopSaw();  // Continuous
 */

export class ConstructionAudio {
  constructor() {
    this.ctx = null;
    this._activeOscillators = new Map();
    this._initialized = false;
  }

  _ensureContext() {
    if (!this.ctx) {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
    this._initialized = true;
    return this.ctx;
  }

  /**
   * Hammer hit — impulse bandpassed through resonant body
   * attack: 0.01s, decay: 0.3s
   */
  hammerHit(intensity = 1.0) {
    const ctx = this._ensureContext();
    const now = ctx.currentTime;

    // Noise burst for impact
    const bufferSize = ctx.sampleRate * 0.05; // 50ms noise
    const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.1));
    }
    const noise = ctx.createBufferSource();
    noise.buffer = noiseBuffer;

    // Bandpass for body resonance
    const bp = ctx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = 1800 + Math.random() * 600;
    bp.Q.value = 2.0;

    // Metallic ringing tail
    const osc = ctx.createOscillator();
    osc.type = 'sine';
    osc.frequency.value = 3200 + Math.random() * 800;
    const oscGain = ctx.createGain();
    oscGain.gain.setValueAtTime(0.12 * intensity, now);
    oscGain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);

    const master = ctx.createGain();
    master.gain.setValueAtTime(0.25 * intensity, now);
    master.gain.exponentialRampToValueAtTime(0.001, now + 0.4);

    noise.connect(bp).connect(master).connect(ctx.destination);
    osc.connect(oscGain).connect(master);
    noise.start(now);
    osc.start(now);
    osc.stop(now + 0.3);
  }

  /**
   * Footstep on gravel — short filtered noise burst
   * attack: 0.005s, decay: 0.15s, two layers (high crunch + low thump)
   */
  footstep(material = 'gravel') {
    const ctx = this._ensureContext();
    const now = ctx.currentTime;

    // Layer 1: Crunch (high-pass noise)
    const bufSize = ctx.sampleRate * 0.12;
    const noiseBuf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
    const d = noiseBuf.getChannelData(0);
    let freqRange = material === 'gravel' ? [2000, 8000] : [500, 3000];
    for (let i = 0; i < bufSize; i++) {
      d[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufSize * 0.15));
    }
    const crunch = ctx.createBufferSource();
    crunch.buffer = noiseBuf;
    const hp = ctx.createBiquadFilter();
    hp.type = 'highpass';
    hp.frequency.value = freqRange[0];

    // Layer 2: Low thump
    const thump = ctx.createOscillator();
    thump.type = 'sine';
    thump.frequency.value = 80 + Math.random() * 40;
    const thumpGain = ctx.createGain();
    thumpGain.gain.setValueAtTime(0.3, now);
    thumpGain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);

    const master = ctx.createGain();
    master.gain.setValueAtTime(0.2, now);
    master.gain.exponentialRampToValueAtTime(0.001, now + 0.2);

    crunch.connect(hp).connect(master).connect(ctx.destination);
    thump.connect(thumpGain).connect(ctx.destination);
    crunch.start(now);
    thump.start(now);
    thump.stop(now + 0.15);
  }

  /**
   * Power tool / saw — starts continuous sawtooth with wobble
   * Call .stopSaw('saw') to stop
   */
  startTool(name = 'saw') {
    if (this._activeOscillators.has(name)) return;
    const ctx = this._ensureContext();
    const now = ctx.currentTime;

    const osc = ctx.createOscillator();
    osc.type = 'sawtooth';
    osc.frequency.value = 120;

    // Wobble LFO
    const lfo = ctx.createOscillator();
    lfo.frequency.value = 5 + Math.random() * 3;
    const lfoGain = ctx.createGain();
    lfoGain.gain.value = 30;
    lfo.connect(lfoGain).connect(osc.frequency);

    const noiseBuf = ctx.createBuffer(1, ctx.sampleRate * 0.5, ctx.sampleRate);
    const nd = noiseBuf.getChannelData(0);
    for (let i = 0; i < noiseBuf.length; i++) nd[i] = Math.random() * 2 - 1;
    const noiseSrc = ctx.createBufferSource();
    noiseSrc.buffer = noiseBuf;
    noiseSrc.loop = true;

    const bp = ctx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = 3000;
    bp.Q.value = 0.5;

    const master = ctx.createGain();
    master.gain.value = 0.08;
    master.gain.setValueAtTime(0.08, now);
    master.gain.linearRampToValueAtTime(0.04, now + 0.5);

    osc.connect(master).connect(ctx.destination);
    noiseSrc.connect(bp).connect(master);
    osc.start(now);
    lfo.start(now);
    noiseSrc.start(now);

    this._activeOscillators.set(name, { osc, lfo, noise: noiseSrc, master });
  }

  stopTool(name = 'saw') {
    const group = this._activeOscillators.get(name);
    if (!group) return;
    const now = this.ctx?.currentTime ?? 0;
    group.master.gain.linearRampToValueAtTime(0, now + 0.3);
    setTimeout(() => {
      try { group.osc.stop(); } catch(e) {}
      try { group.lfo.stop(); } catch(e) {}
      try { group.noise.stop(); } catch(e) {}
    }, 350);
    this._activeOscillators.delete(name);
  }

  /**
   * Gear grinding — low metallic scraping loop
   */
  gearGrind(intensity = 0.5) {
    const ctx = this._ensureContext();
    const now = ctx.currentTime;
    const duration = 0.4 + Math.random() * 0.3;

    const bufSize = ctx.sampleRate * duration;
    const buf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < bufSize; i++) {
      const t = i / ctx.sampleRate;
      // Granular metallic: amplitude-modulated noise with ring modulation
      const carrier = Math.sin(2 * Math.PI * (60 + Math.random() * 40) * t);
      const modulator = Math.sin(2 * Math.PI * (15 + Math.random() * 5) * t);
      d[i] = (Math.random() * 2 - 1) * (0.5 + 0.5 * carrier) * (0.5 + 0.5 * modulator);
    }

    const src = ctx.createBufferSource();
    src.buffer = buf;
    const bp = ctx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = 400 + Math.random() * 800;
    bp.Q.value = 1.5;

    const master = ctx.createGain();
    master.gain.setValueAtTime(0.12 * intensity, now);
    master.gain.exponentialRampToValueAtTime(0.001, now + duration);

    src.connect(bp).connect(master).connect(ctx.destination);
    src.start(now);
  }

  /**
   * Concrete pour — low-frequency filtered noise with slow LFO
   */
  concretePour(duration = 2.0) {
    const ctx = this._ensureContext();
    const now = ctx.currentTime;

    const bufSize = ctx.sampleRate * duration;
    const buf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < bufSize; i++) {
      const t = i / ctx.sampleRate;
      const rumble = Math.sin(2 * Math.PI * (2 + Math.sin(t * 0.5) * 1.5) * t);
      d[i] = (Math.random() * 2 - 1) * (0.3 + 0.7 * (0.5 + 0.5 * rumble));
    }

    const src = ctx.createBufferSource();
    src.buffer = buf;
    const lp = ctx.createBiquadFilter();
    lp.type = 'lowpass';
    lp.frequency.value = 300;

    const master = ctx.createGain();
    master.gain.setValueAtTime(0.15, now);
    master.gain.linearRampToValueAtTime(0.08, now + duration * 0.5);
    master.gain.linearRampToValueAtTime(0.001, now + duration);

    src.connect(lp).connect(master).connect(ctx.destination);
    src.start(now);
  }

  /** Cleanup all active sounds */
  stopAll() {
    for (const [name, group] of this._activeOscillators) {
      this.stopTool(name);
    }
  }
}
