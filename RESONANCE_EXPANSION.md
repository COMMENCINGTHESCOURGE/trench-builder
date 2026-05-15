# RESONANCE EXPANSION — Living Backrooms
# From static MEP → dynamic systemic simulation
# DaShawn / Guinea Pig Trench LLC — May 2026

# ═══════════════════════════════════════════════════════
# PHASE 2: TRANSFER FUNCTIONS — Oscillation + Damping
# ═══════════════════════════════════════════════════════

# The BACKROOMS_MEP is static infrastructure.
# This expansion makes it ALIVE through transfer functions
# that connect simulation nodes with real physics response.

# ═══════════════════════════════════════════════════════
# 1. LIGHT_SYSTEM — Voltage-driven flicker
# ═══════════════════════════════════════════════════════

LIGHT_TRANSFER = """
  Input: grid load (0-1), time (t)
  Output: emissive intensity, color temperature shift

  Base luminance:     L₀ = 0.4  (fluorescent baseline)
  Grid flicker:       G(t) = 1 + 0.03·sin(2π·60·t)  (60Hz mains hum)
  Load sag:           S(load) = 1 - 0.2·load²  (dim when grid is taxed)
  Random instability: R = 1 + 0.01·Perlin(t·0.1)  (temporal noise)

  Final emissive:     L = L₀ · G(t) · S(load) · R

  Color shift:        Temp = 4200K + 800·sin(2π·0.25·t)  (warm→cool cycling)
                      RGB = KelvinToRGB(Temp)
"""

# ═══════════════════════════════════════════════════════
# 2. TRANSFORMER_ACOUSTICS — Harmonic hum
# ═══════════════════════════════════════════════════════

ACOUSTIC_TRANSFER = """
  Input: grid load, distance from listener
  Output: hum amplitude, frequency, harmonics

  Fundamental:        f₀ = 60Hz  (mains frequency)
  2nd harmonic:       f₁ = 120Hz · (1 + 0.05·load)
  3rd harmonic:       f₂ = 180Hz · (1 + 0.02·sin(2π·0.1·t))
  Sub-harmonic:       f_sub = 30Hz · (1 + 0.1·load²)  (transformer core saturation)

  Amplitude falloff:  A = A₀ / (1 + distance²)  (inverse square)
  Damping envelope:   D(t) = 1 - exp(-t/τ)  (startup ramp)
                      τ = 0.3 + 0.5·load  (heavier load = slower stabilization)
"""

# ═══════════════════════════════════════════════════════
# 3. CONDUIT_THERMAL — I²R heating along conduit runs
# ═══════════════════════════════════════════════════════

CONDUIT_THERMAL = """
  Input: current (I), conduit length, ambient temp
  Output: surface temperature gradient

  Joule heating:      P = I²R  per meter
  Thermal resistance: R_thermal = length / (k·A)
  Temperature rise:   ΔT = P · R_thermal

  Material response:
    Copper conduit:   emissivity = 0.03 + 0.15·(ΔT/100)  (copper darkens with heat)
    Steel conduit:    emissivity = 0.25 + 0.05·(ΔT/100)

  Visualization:      Emissive color shifts from dark → orange → red
                      Smoothstep falloff from hottest point (junction box)
                      along conduit length
"""

# ═══════════════════════════════════════════════════════
# 4. VENT_AIRFLOW — Pressure-driven HVAC simulation
# ═══════════════════════════════════════════════════════

VENT_TRANSFER = """
  Input: HVAC fan speed, duct pressure
  Output: particle velocity, turbidity, temperature gradient

  Flow velocity:      v = √(2·ΔP/ρ)  (Bernoulli through orifice)
  Particle drift:     dx/dt = v · sin(2π·t + phase_offset)
  Turbidity:          T = 0.05 + 0.15·Re^(-0.5)  (Reynolds-dependent)
  
  Temperature mixing: T_out = T_supply · (1 - e^(-t/τ_mix)) + T_ambient · e^(-t/τ_mix)
                      τ_mix = 2.0 / fan_speed  (faster fan = faster mixing)
"""

# ═══════════════════════════════════════════════════════
# 5. SYSTEMIC INTERCONNECTIVITY GRAPH
# ═══════════════════════════════════════════════════════

DEPENDENCY_GRAPH = """
  Power_Grid ──→ Junction_Box ──→ Outlet ──→ Switch ──→ Light_Fixture
      │              │                │
      │              ├──→ Conduit ──→ Ceiling (thermal path)
      │              │
      └──→ Transformer ──→ Acoustic_Hum (120Hz + harmonics)
      
  HVAC_System ──→ Duct_Network ──→ Supply_Vent ──→ Air_Particles
      │                                              │
      └──→ Return_Vent ←── Air_Particles ←──────────┘

  Thermostat ──→ Temperature_Sensor ──→ HVAC_Controller
      │                                      │
      └──→ Target_Temp ←── Grid_Load ←──────┘
"""

# ═══════════════════════════════════════════════════════
# MANIFESTATION BRIDGE — Abstract graph → Visual output
# ═══════════════════════════════════════════════════════

MANIFESTATION = """
  When WorldStateKernel updates a node property:

  1. Traverse dependency graph to find ALL affected visual components
  2. For each component's THREE.Group:
     - Update emissive (light → thermal → heat maps)
     - Update opacity (flow → particle density → conduit glow)
     - Update position (vibration → micro-jitter → resonance)
     - Spawn/destroy particle systems (HVAC → airflow → dust motes)
  3. Apply transfer functions with correct easing curves
  4. Animate over multiple frames (no instantaneous jumps)

  Example: Grid load increases 0→0.8
    → Lights dim (emissive -16%) with smoothstep over 0.3s
    → Transformer hum amplitude rises with exponential ramp
    → Junction box temperature rises, conduit glows warm orange
    → HVAC compensates (fan speed +20% after 2s thermostat delay)
"""
