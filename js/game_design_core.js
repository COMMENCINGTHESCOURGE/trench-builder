// =============================================================================
// GHOST BRAID SYSTEM: GAME DESIGN CORE (game_design_core.js)
// Zero-renderer dependency shared module.
// Extracts Factions, Economy, Progression, Dual Modes, Events, Clock, Audio Synth
// =============================================================================

window.GameDesignCore = {
  // ─── 1. FACTIONS / CLASSES ───
  CHARACTERS: [
    { id: 'defender', name: 'Defender Faction', bonus: '+$500 starting credits, default shield boost', sprite: 'defender' },
    { id: 'dimmak', name: 'Dim Mak Syndicate', bonus: '+30 starting cargo storage capacity', sprite: 'dimmak' },
    { id: 'mecha', name: 'Mecha Union', bonus: '-50% police raid risk via secure frequency', sprite: 'mecha' },
    { id: 'kraken', name: 'Kraken Vanguard', bonus: '10% market purchasing discount', sprite: 'kraken' },
    { id: 'akuaku', name: 'Aku Sanctum', bonus: 'Predictive price trend telemetry visualizer', sprite: 'akuaku' },
    { id: 'grief', name: 'Grief Marauders', bonus: '+$2000 credits but starts carrying loan debt', sprite: 'grief' }
  ],

  // ─── 1.5. FACTION STATS NORMALIZATION (T5) ───
  FACTION_STATS: {
    defender: {
      space_shield_mult: 1.25,
      space_energy_mult: 1.0,
      ground_hull_mult: 1.25,
      ground_recharge_mult: 1.0,
      description: "Priority capacitor routing for hull and shield plates."
    },
    dimmak: {
      space_shield_mult: 1.0,
      space_energy_mult: 1.30,
      ground_hull_mult: 1.0,
      ground_recharge_mult: 1.30,
      description: "Syndicate grade auxiliary reactor generators."
    },
    mecha: {
      space_shield_mult: 1.0,
      space_energy_mult: 1.10,
      ground_hull_mult: 1.15,
      ground_recharge_mult: 1.10,
      description: "Industrial union standardized alloy reinforcements."
    },
    kraken: {
      space_shield_mult: 1.10,
      space_energy_mult: 1.0,
      ground_hull_mult: 1.10,
      ground_recharge_mult: 1.10,
      description: "Vanguard tactical defensive plating."
    },
    akuaku: {
      space_shield_mult: 1.05,
      space_energy_mult: 1.15,
      ground_hull_mult: 1.05,
      ground_recharge_mult: 1.15,
      description: "Sanctum spiritual telemetry enhancements."
    },
    grief: {
      space_shield_mult: 0.90,
      space_energy_mult: 1.20,
      ground_hull_mult: 0.90,
      ground_recharge_mult: 1.20,
      description: "High-risk marauder overloaded thruster systems."
    }
  },

  // ─── 2. ECONOMY ───
  SUBSTANCES: [
    { name: 'Void Dust', color: '#88aacc', minPrice: 15, maxPrice: 40, icon: 'circle' },
    { name: 'Nebula Crystals', color: '#aa66ff', minPrice: 50, maxPrice: 120, icon: 'diamond' },
    { name: 'Plasma Vials', color: '#ff6644', minPrice: 200, maxPrice: 500, icon: 'circle' },
    { name: 'Dark Matter', color: '#334466', minPrice: 1000, maxPrice: 3000, icon: 'diamond' },
    { name: 'Quantum Tears', color: '#00eeff', minPrice: 5000, maxPrice: 12000, icon: 'circle' },
    { name: 'Onion Extract', color: '#ffd700', minPrice: 10000, maxPrice: 50000, icon: 'diamond' }
  ],

  LOCATIONS: [
    { name: 'Trench Hub', char: 'defender', desc: 'Balanced prices, safe haven', color: '#00d2ff',
      priceMod: [1, 1, 1, 1, 1, 1], policeRate: 0.08, volatility: 0.2 },
    { name: 'Kraken Depths', char: 'kraken', desc: 'Cheap dust, pricey tears', color: '#2244aa',
      priceMod: [0.5, 0.8, 1, 1.2, 1.8, 1.3], policeRate: 0.12, volatility: 0.3 },
    { name: 'Dim Mak District', char: 'dimmak', desc: 'Volatile markets, frequent events', color: '#ff60a0',
      priceMod: [1.2, 1.1, 0.9, 0.8, 1, 1.2], policeRate: 0.15, volatility: 0.6 },
    { name: 'Mecha Station', char: 'mecha', desc: 'Stable prices, high security', color: '#ff8c00',
      priceMod: [1.1, 1, 1.1, 1, 0.9, 0.8], policeRate: 0.22, volatility: 0.1 },
    { name: 'Grief Wastes', char: 'grief', desc: 'Everything cheap but dangerous', color: '#aa2233',
      priceMod: [0.6, 0.6, 0.7, 0.7, 0.8, 0.9], policeRate: 0.25, volatility: 0.4 },
    { name: 'Aku Aku Sanctum', char: 'akuaku', desc: 'Rare goods, mysterious shifts', color: '#b060ff',
      priceMod: [1.3, 1.2, 1, 0.9, 0.7, 0.5], policeRate: 0.1, volatility: 0.5 }
  ],

  generatePrices(locIdx) {
    const loc = this.LOCATIONS[locIdx];
    const prices = [];
    const trends = [];
    for (let i = 0; i < 6; i++) {
      const sub = this.SUBSTANCES[i];
      const base = sub.minPrice + Math.random() * (sub.maxPrice - sub.minPrice);
      const vol = 1 + (Math.random() * 2 - 1) * loc.volatility;
      let price = Math.round(base * loc.priceMod[i] * vol);
      price = Math.max(1, price);
      prices.push(price);
      trends.push(Math.random() < 0.33 ? -1 : Math.random() < 0.5 ? 1 : 0);
    }
    return { prices, trends };
  },

  // ─── 3. PROGRESSION ───
  RANKS: [
    { name: 'Petty Smuggler', min: 0 },
    { name: 'Street Hustler', min: 5000 },
    { name: 'Void Dealer', min: 20000 },
    { name: 'Cartel Boss', min: 80000 },
    { name: 'Galactic Overlord', min: 250000 }
  ],

  USER_RANKS: [
    { name: 'Casual User', min: 0 },
    { name: 'Weekend Warrior', min: 5 },
    { name: 'Trench Fiend', min: 10 },
    { name: 'Substrate Junkie', min: 16 },
    { name: 'Ascended Spacer', min: 23 },
    { name: 'Transcendent Entity', min: 30 }
  ],

  getRank(worth, role, daysAlive) {
    if (role === 'user') {
      let r = this.USER_RANKS[0];
      for (const rank of this.USER_RANKS) {
        if (daysAlive >= rank.min) r = rank;
      }
      return r.name;
    }
    let r = this.RANKS[0];
    for (const rank of this.RANKS) {
      if (worth >= rank.min) r = rank;
    }
    return r.name;
  },

  // ─── 4. DUAL MODES ───
  SUBSTANCE_EFFECTS: [
    { potency: 10, duration: 1, addictive: false },
    { potency: 25, duration: 2, addictive: false },
    { potency: 40, duration: 2, addictive: false },
    { potency: 60, duration: 3, addictive: false },
    { potency: 80, duration: 3, addictive: false },
    { potency: 100, duration: 4, addictive: true }
  ],

  processUserDayEffects(highMeter, totalUses, day) {
    const drain = 12 + Math.floor(day / 5) * 3;
    const newHigh = Math.max(0, highMeter - drain);
    let hpLoss = 0;
    let withdrawal = false;
    if (newHigh <= 0) {
      withdrawal = true;
      hpLoss = 8 + Math.floor(totalUses / 3) * 2;
    }
    return { highMeter: newHigh, hpLoss, withdrawal, drain };
  },

  // ─── 5. DYNAMIC EVENTS ───
  EVENTS: {
    MARKET_CRASH: 'market_crash',
    PRICE_SURGE: 'price_surge',
    POLICE_RAID: 'police_raid',
    BLACK_MARKET: 'black_market',
    WORMHOLE: 'wormhole',
    PIRATE_AMBUSH: 'pirate_ambush',
    LUCKY_FIND: 'lucky_find'
  },

  rollEvent(locIdx, policeFactor = 1.0) {
    const loc = this.LOCATIONS[locIdx];
    const roll = Math.random();
    if (roll < 0.08) {
      const si = Math.floor(Math.random() * 6);
      return { type: this.EVENTS.MARKET_CRASH, si, factor: 0.2 + Math.random() * 0.3 };
    } else if (roll < 0.16) {
      const si = Math.floor(Math.random() * 6);
      return { type: this.EVENTS.PRICE_SURGE, si, factor: 2.0 + Math.random() * 3.0 };
    } else if (roll < 0.24) {
      if (Math.random() < loc.policeRate * policeFactor) {
        return { type: this.EVENTS.POLICE_RAID };
      }
    } else if (roll < 0.30) {
      const si = Math.floor(Math.random() * 5);
      return { type: this.EVENTS.BLACK_MARKET, si, discount: 0.3 + Math.random() * 0.3 };
    } else if (roll < 0.35) {
      return { type: this.EVENTS.WORMHOLE };
    } else if (roll < 0.40) {
      return { type: this.EVENTS.PIRATE_AMBUSH, damage: Math.floor(Math.random() * 15) + 5 };
    } else if (roll < 0.45) {
      return { type: this.EVENTS.LUCKY_FIND, cash: Math.round(150 + Math.random() * 700) };
    }
    return null;
  },

  // ─── 6. CLOCK ───
  DEFAULT_MAX_DAYS: 30,

  // ─── 7. AUDIO IDENTITY (SYNTHESIZER) ───
  SYNTH_MELODY: {
    BPM: 126,
    bassNotes: [
      {note: 65.41, time: 0, dur: 0.8},
      {note: 65.41, time: 1.0, dur: 0.4},
      {note: 77.78, time: 1.5, dur: 0.4},
      {note: 65.41, time: 2.0, dur: 0.8},
      {note: 82.41, time: 3.0, dur: 0.6},
      {note: 87.31, time: 4.0, dur: 0.8},
      {note: 87.31, time: 5.0, dur: 0.4},
      {note: 98.00, time: 5.5, dur: 0.4},
      {note: 87.31, time: 6.0, dur: 0.8},
      {note: 65.41, time: 7.0, dur: 0.8}
    ],
    melodyNotes: [
      {note: 523.25, time: 0, dur: 0.3},
      {note: 466.16, time: 0.33, dur: 0.3},
      {note: 392.00, time: 0.66, dur: 0.5},
      {note: 349.23, time: 1.25, dur: 0.25},
      {note: 392.00, time: 1.5, dur: 0.5},
      {note: 523.25, time: 2.0, dur: 0.4},
      {note: 587.33, time: 2.5, dur: 0.3},
      {note: 523.25, time: 3.0, dur: 0.5},
      {note: 466.16, time: 4.0, dur: 0.3},
      {note: 440.00, time: 4.33, dur: 0.15},
      {note: 415.30, time: 4.5, dur: 0.15},
      {note: 392.00, time: 4.66, dur: 0.5},
      {note: 311.13, time: 5.25, dur: 0.4},
      {note: 349.23, time: 6.0, dur: 0.3},
      {note: 392.00, time: 6.5, dur: 0.4},
      {note: 311.13, time: 7.0, dur: 0.8}
    ]
  },

  playProceduralLaser(audioCtx, time) {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(1100, time);
    osc.frequency.exponentialRampToValueAtTime(160, time + 0.14);
    gain.gain.setValueAtTime(0.06, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.14);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(time);
    osc.stop(time + 0.14);
  },

  playProceduralExplosion(audioCtx, time) {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(170, time);
    osc.frequency.linearRampToValueAtTime(25, time + 0.48);
    gain.gain.setValueAtTime(0.18, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.55);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(time);
    osc.stop(time + 0.55);
  },

  // ─── 8. ECONOMIC ARBITRAGE & DEGRADATION (T6) ───
  calculateArbitrage(basePrice, segments, quantity) {
    // 5% price multiplier compound per segment
    const multiplier = Math.pow(1.05, segments);
    // 5% cargo degradation per 10 segments
    const degradationRate = 0.05 * Math.floor(segments / 10);
    const effectiveQuantity = Math.max(0, quantity * (1.0 - Math.min(1.0, degradationRate)));
    const finalPrice = Math.round(basePrice * multiplier);
    return {
      pricePerUnit: finalPrice,
      effectiveQuantity: effectiveQuantity,
      totalValue: Math.round(finalPrice * effectiveQuantity)
    };
  }
};

// Export to window object or node module system
if (typeof window !== 'undefined') {
  window.GameDesignCore = GameDesignCore;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GameDesignCore;
}
