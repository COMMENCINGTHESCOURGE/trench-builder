# GAMESHARK — The 7th Domain: Creative Memory Manipulation
# DaShawn / Guinea Pig Trench LLC — May 2026

# ═══════════════════════════════════════════════════════
# THE GAMESHARK PRINCIPLE
# ═══════════════════════════════════════════════════════

# GameShark was not just a cheat device.
# It was a MEMORY INTERCEPTOR — sitting between the console and cartridge,
# modifying values in transit before they reached the game.

#   Console → [GameShark intercepts RAM reads/writes] → Game
#   Scene   → [Shader passes intercept rendered frames]  → Display
#   Physics → [Debug overlay intercepts simulation state] → Output

# THE INSIGHT: Every post-processing system in TRENCH BUILDER
# is a GameShark for reality simulation.

# ═══════════════════════════════════════════════════════
# GAMESHARK → TRENCH BUILDER PARALLELS
# ═══════════════════════════════════════════════════════

GAMESHARK_MAP = {
    "infinite_health": {
        "gameshark": "Freeze HP value at max — intercept memory write to health address",
        "tr_builder": "Freeze thermal state — override emissive values to hold a specific temperature visualization",
    },
    "moon_jump": {
        "gameshark": "Modify gravity constant or velocity cap in memory",
        "tr_builder": "Physics toggle — override damping/inertia for cinematic slow-motion or zero-G shots",
    },
    "walk_through_walls": {
        "gameshark": "Disable collision detection flag",
        "tr_builder": "Clip plane toggle — camera passes through structures for interior inspection shots",
    },
    "debug_mode": {
        "gameshark": "Enable hidden developer menu with level select, item spawn, stat viewer",
        "tr_builder": "Developer overlay — wireframe toggle, material inspector, FPS counter, physics debug vectors",
    },
    "code_finder": {
        "gameshark": "Search RAM for changing values to isolate the address controlling a behavior",
        "tr_builder": "Shader parameter isolation — tweak one uniform at a time to find the visual 'address' controlling an effect",
    },
    "master_code": {
        "gameshark": "Required code that enables the cheat device to hook into the game's memory",
        "tr_builder": "EffectComposer — the 'master code' that enables all post-processing passes to hook into the render pipeline",
    },
}

# ═══════════════════════════════════════════════════════
# CREATIVE MODE — From Stroboscopic Chrono-Break
# ═══════════════════════════════════════════════════════

# From the sprite sheet design document (earlier session):
# "GameShark / Creative Mode — glitched memory-address block,
#  debug overlay with 999 health display, a corrupter orb that
#  locks enemy animations on-twos, and a 'RetroShark' cartridge
#  outline beside a holographic hyperrealistic hand reaching
#  into the pixel grid."

# This IS the TRENCH BUILDER Creative Mode spec:
#   - Glitched memory-address block → Debug HUD with shader parameter values
#   - 999 health display → Simulation state readout (physics, thermal, EM)
#   - Corrupter orb → Parameter randomization for glitch-art B-roll
#   - RetroShark cartridge → The physical GameShark as visual motif
#   - Hand reaching into pixel grid → The engineer manipulating simulation directly

# ═══════════════════════════════════════════════════════
# UPDATED CONVERGENCE — 7 Domains
# ═══════════════════════════════════════════════════════

# 1. RENDERING        — Emulates light transport
# 2. EM SYSTEMS       — Emulates electromagnetic behavior
# 3. INDUSTRIAL        — Emulates mechanical systems
# 4. ARCHITECTURAL     — Emulates buildings as organisms
# 5. CINEMATOGRAPHY    — Emulates camera/film production
# 6. EMULATION         — Emulates hardware/software systems
# 7. GAMESHARK         — Creative memory manipulation / debug mode
#
# GameShark is the meta-domain: it's the tool that lets you
# intercept and modify ANY of the other domains in real-time.
# It's the developer console for reality simulation.
