# VEO INTERPOLATION PROMPT — Transition Scene Between Two Endpoints
# DaShawn / Guinea Pig Trench LLC — May 2026

# ═══════════════════════════════════════════════════════
# ENDPOINT A: demo_clip.mp4 (7.7MB)
# ───────────────────────────────────
# Dark blue opening → cuts → bright product reveal
# Energy: Fast, dynamic, demo-style
# Palette: Blue tech → gray mood → blue return → bright neutral
# Role: HOOK — grabs attention, sets the problem
#
# ENDPOINT B: demo_clip2.mp4 (12MB)
# ────────────────────────────────────
# Warm neutral, smooth continuous shot
# Energy: Calm, product-focused, ambient
# Palette: Warm green-gray, bright, sustained
# Role: RESOLUTION — product in use, calm confidence
#
# THE GAP BETWEEN: 60% more robust scene
# Neither endpoint alone tells the full story.
# The transition IS the story — from problem to solution.
# ═══════════════════════════════════════════════════════

VEO_INTERPOLATION_PROMPT = """
GENERATE A TRANSITION SCENE between these two keyframes.

START FRAME (clip 1, end): Bright neutral product reveal — the TRENCH BUILDER 
interface is visible. Dark blue background transitioning to bright.

END FRAME (clip 2, beginning): Warm ambient product shot — smooth, calm, 
the builder is running, Gemma 4 panel visible.

THE TRANSITION (the 60% more robust scene):
─────────────────────────────────────────────
Camera moves from the product interface INTO the product. We descend through 
the 3D scene — past the copper voice coil windings glowing with thermal bloom, 
through the electromagnetic field particles swirling in the magnetic gap, 
past the caustic patterns rippling on the floor from the acrylic dome.

The visual narrative: "This isn't just software. This is physics rendered live."

SHOT SEQUENCE:
0:00-0:02  Push into the TRENCH BUILDER interface — it dissolves into the 3D scene
0:02-0:04  Camera orbits the copper windings — orange thermal bloom pulses
0:04-0:06  Camera tracks through EM field — pink particles swirl, flux lines glow
0:06-0:08  Camera pulls back to reveal the full subwoofer assembly
0:08-0:10  Gemma 4 chat panel slides in from right — text: "Voice coil within spec"
0:10-0:12  Camera settles on the warm ambient product shot (clip 2's endpoint)

VISUAL STYLE:
- Dark blue background transitions to warm neutral
- Copper (#dd8844) with anisotropic brushing
- Orange thermal glow (#ff8844) radiating from windings
- Pink EM particles (#ff6688) with additive blending
- Blue caustic patterns (#cceeff) on dark floor
- Clean tech UI elements with orange accent (#ffaa44)

AUDIO:
- Ambient electronic pulse fades in (Lyria 3 track)
- Subtle bass throb synchronized with thermal bloom pulses
- Clean, professional, cinematic

MOOD: The moment of revelation. "Oh — this is REAL."

OUTPUT: 12-second video, 1280×720, 24fps, h264
"""

# ═══════════════════════════════════════════════════════
# ALTERNATE: Pure mathematical interpolation prompt
# ═══════════════════════════════════════════════════════

VEO_MATH_INTERPOLATION = """
Generate 12 seconds of video that smoothly interpolates between two visual states.

START STATE:
  Avg RGB: (115, 120, 105) — bright warm gray
  Brightness: 113 | Contrast: 65
  Energy: High contrast, cut-driven, dynamic
  Mood: Attention-grabbing, problem statement

END STATE:
  Avg RGB: (129, 138, 134) — brighter warm green-gray
  Brightness: 134 | Contrast: 69
  Energy: Smooth, continuous, calm
  Mood: Confident, product-in-use, resolution

INTERPOLATION PATH:
  Frame 1-3:   Hold start state, slight darkening
  Frame 4-6:   Drop into deep 3D scene — copper + thermal + EM visible
  Frame 7-9:   Rise back up — brightness increases, contrast softens
  Frame 10-12: Settle at end state — warm, bright, calm

The interpolation is NOT a linear crossfade.
It's a JOURNEY — descending into the physics, then rising into the solution.
"""

# ═══════════════════════════════════════════════════════
# FINAL ASSEMBLY — 3 clips into 3 minutes
# ═══════════════════════════════════════════════════════

ASSEMBLY = {
    "clip_1": {"file": "demo_clip.mp4", "duration": "8s", "role": "HOOK — problem & attention"},
    "transition": {"file": "TO GENERATE", "duration": "12s", "role": "JOURNEY — into the physics"},
    "clip_2": {"file": "demo_clip2.mp4", "duration": "8s", "role": "RESOLUTION — product confidence"},
    "remaining": {"file": "Screen record", "duration": "152s", "role": "Full demo + Gemma 4 + equity message"},
}
