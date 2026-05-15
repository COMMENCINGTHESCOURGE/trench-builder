# CINEMATOGRAPHY & B-ROLL PRODUCTION FRAMEWORK
# Power Rangers Assembly Model — DaShawn / Guinea Pig Trench LLC
# May 2026

# ═══════════════════════════════════════════════════════
# THE POWER RANGERS MODEL
# ═══════════════════════════════════════════════════════
#
# Power Rangers (1993) was assembled from two sources:
#
#   SENTAI FOOTAGE (60%)           AMERICAN FOOTAGE (40%)
#   ─────────────────────           ─────────────────────
#   Kyōryū Sentai Zyuranger        New scenes with American actors
#   Fight choreography              Command center scenes
#   Zord/Megazord sequences         High school drama
#   Monster battles                 Morphing transitions
#   Japanese landscape shots        Angel Grove establishing shots
#
# The GENIUS of this model: existing spectacular footage is
# recontextualized by new framing footage. The Japanese fight
# scenes become "Zord battles" through American voice-over and
# transition wipes. The sentai footage provides production value
# that would be impossible on the show's budget.
#
# TRENCH BUILDER adapts this model:
#
#   SENTAI FOOTAGE (existing)       B-ROLL (generated)
#   ─────────────────────           ──────────────────
#   CAD models (Onshape parts)      Camera path sequences
#   3D terrain/topography           Helta close-up shots
#   Subwoofer/motor assembly        Thermal bloom captures
#   Structure placement             Build sequence montages
#   EM field visualization          Transition wipes/morphs

# ═══════════════════════════════════════════════════════
# THE HELTA — Iconic Close-Up Theory
# ═══════════════════════════════════════════════════════
#
# "Helta" derives from "helmet" — the Power Rangers helmet is the
# most iconic visual element. Every morphing sequence centers on
# the helmet close-up. The helmet shot IS the brand.
#
# In industrial/engineering cinematography, the "helta" is the
# close-up that defines the visual identity:
#
#   DOMAIN              HELTA SHOT
#   ──────              ──────────
#   Audio               Copper voice coil winding detail
#   Automotive          Anisotropic brushed motor housing
#   Architecture        Structural joint / material grain
#   Industrial          CNC tool path on machined surface
#   EM Systems          Flux line convergence at air gap
#
# The helta shot rules:
#   1. Extreme close-up — fill frame with the detail
#   2. Slow movement — dolly or subtle orbit
#   3. Backlight/rim light — separate subject from background
#   4. Shallow depth of field — isolate the detail
#   5. Material response — let the surface tell its story

# ═══════════════════════════════════════════════════════
# B-ROLL PACKAGE STRUCTURE
# ═══════════════════════════════════════════════════════
#
# A complete B-roll package follows this sequence:
#
#   1. ESTABLISHING SHOT (drone/crane)     — Where are we?
#   2. CONTEXT SHOT (orbit/dolly)          — What is this?
#   3. HELTA 1 (copper close-up)           — Material detail
#   4. HELTA 2 (thermal bloom)             — Energy/process
#   5. HELTA 3 (EM field / motion)         — Dynamic behavior
#   6. ACTION SHOT (build/assemble)        — What happens?
#   7. EXIT SHOT (dutch/crane away)        — Closure
#
# Total package: ~30-45 seconds of B-roll from 7 shots.
# Generated programmatically from the same 3D scene.

# ═══════════════════════════════════════════════════════
# SHOT TYPE CATALOG
# ═══════════════════════════════════════════════════════

SHOT_CATALOG = {
    "establishing": {
        "orbit": "360° product reveal — sentai establishing shot. Full context.",
        "crane": "Vertical boom sweep — reveals scale. Starts low, ends high.",
        "drone": "Aerial flyover — terrain + structures in context. Top-down reveal.",
    },
    "b_roll_helta": {
        "helta_copper": "Extreme close-up on copper windings. Anisotropic brushing visible. Rim-lit.",
        "helta_thermal": "Heat bloom radiating from core. Emissive color shift. Slow orbit.",
        "helta_em": "Magnetic flux lines pulsing. Particle field around air gap. Fast cut.",
    },
    "motion": {
        "dolly": "Slow push-in toward subject. Increasing tension. Hitchcock zoom feel.",
        "dutch": "Canted angle — dramatic tension. Disorientation. Action movie language.",
    },
    "action": {
        "build": "Structure assembly sequence. Camera moves with construction. Dynamic angles.",
        "explode": "Disassembly view — parts separate in space. Technical breakdown.",
    },
}

# ═══════════════════════════════════════════════════════
# TRANSITIONS — The Morphing Sequence
# ═══════════════════════════════════════════════════════
#
# Power Rangers morphing = the transition BETWEEN states.
# In cinematography, transitions are as important as shots.
#
#   WIPE:         Camera passes behind object → new scene revealed
#   MATCH CUT:    Same composition, different subject
#   DISSOLVE:     Thermal bloom dissolves into establishing shot
#   LENS FLARE:   Light source crosses frame → transition point
#   RACK FOCUS:   Pull focus from detail to context

# ═══════════════════════════════════════════════════════
# HYPERFRAMES INTEGRATION
# ═══════════════════════════════════════════════════════
#
# Hyperframes (from Video 3 research) enables rendering these
# cinematography sequences as actual video files:
#
#   1. Define shot list as JSON (already implemented)
#   2. Hyperframes renders each shot as HTML/WebGL frame sequence
#   3. FFmpeg assembles frames + transitions into final video
#   4. Output: B-roll package as .mp4
#
# This closes the loop: 3D scene → cinematography → video output.
