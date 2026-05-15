# GEMINI 3.1 PRO — Hackathon Asset Generation Prompts
# Veo video + Lyria 3 music + Nano Banana 2 cover image
# DaShawn / Guinea Pig Trench LLC — May 2026

# ═══════════════════════════════════════════════════════
# 1. VEO — Cinematic Demo Video (3:00)
# ═══════════════════════════════════════════════════════

VEO_VIDEO_PROMPT = """
Create a 3-minute cinematic product demo video with the following scenes.
Use screen-recorded reference footage as visual guidance where noted.

SCENE 1 (0:00-0:15) — THE PROBLEM:
Dark background. Text fades in: "$2,545/year. $10,000/lifetime."
A cursor hovers over "Buy Now" — then hesitates. Pulls away.
Text: "The tools that design our world are locked behind paywalls."

SCENE 2 (0:15-0:45) — THE SOLUTION:
TRENCH BUILDER interface opens. Bright, clean, engineering aesthetic.
Quick cuts: 3D building rising from terrain, walls snapping into place,
plumbing pipes routing through walls, electrical conduits glowing yellow.
Text overlay: "Single HTML file. Any browser. Zero cost."

SCENE 3 (0:45-1:15) — GEMMA 4:
Split screen: left side shows 3D subwoofer scene, right side shows
Gemma 4 chat panel. User types: "Is the voice coil properly sized?"
Gemma 4 responds with technical analysis. Text fades: "Local AI.
No cloud. No API keys. Complete privacy."

SCENE 4 (1:15-1:45) — PERCEPTUAL PHYSICS:
Bass frequency slider moves. Subwoofer cone pulses. Orange thermal bloom
radiates from copper windings. Pink EM particles swirl in magnetic field.
Blue caustic patterns ripple on floor. All responding to one frequency input.
Text: "Physics drives the visualization. Not canned animation."

SCENE 5 (1:45-2:15) — DIGITAL EQUITY:
Split screen. Left: architect in glass office tower. Right: builder with
laptop under a tree. Same TRENCH BUILDER interface on both screens.
Same Gemma 4 assistant answering questions. Same HTML file.
Text: "One file. Every device. Every community."

SCENE 6 (2:15-2:45) — ARCHITECTURE:
Clean tech diagram. Browser → Three.js → Ollama → Gemma 4 2B.
Arrows connect the layers. Labels appear: "WebGL PBR Rendering,"
"Local Inference," "Zero API Cost," "Offline Capable."

SCENE 7 (2:45-3:00) — CALL TO ACTION:
GitHub repository page. README scrolls. Badge: "MIT Licensed."
Text: "The tools to design our world should belong to everyone."
Final frame: github.com/COMMENCINGTHESCOURGE/trench-builder
Fade to black.

STYLE: Clean engineering aesthetic. Dark blue/gray backgrounds with
orange accent color (#ffaa44). Code-like typography. Professional but
warm. Inspired by Stripe and Linear design languages.

AUDIO: Professional voiceover narration (provided separately).
Background: ambient electronic with subtle bass pulse.
"""

# ═══════════════════════════════════════════════════════
# 2. LYRIA 3 — Background Music (30 seconds, loops)
# ═══════════════════════════════════════════════════════

LYRIA3_MUSIC_PROMPT = """
Generate a 30-second instrumental track for a tech product demo video.

GENRE: Ambient electronic / cinematic tech
TEMPO: 80 BPM
KEY: D minor
MOOD: Inspiring, warm, determined — not aggressive or salesy

STRUCTURE:
0-5s:   Soft ambient pad fade-in, subtle sub-bass drone
5-15s:  Clean electronic pulse enters (kick on 1 and 3, hi-hat shimmer)
15-25s: Arpeggiated synth melody enters, warm major-to-minor progression
25-30s: Melody resolves, pad sustains, clean fade-out

INSTRUMENTS: Deep sub-bass, warm analog pads, clean electronic drums,
            arpeggiated synth lead, subtle noise texture

REFERENCE ARTISTS: Jon Hopkins, Max Cooper, Rival Consoles
USE CASE: Background for 3-minute hackathon product demo video
          Should loop cleanly for repeated playback

VOCALS: None — instrumental only
"""

# ═══════════════════════════════════════════════════════
# 3. NANO BANANA 2 — Cover Image
# ═══════════════════════════════════════════════════════

NANO_BANANA_COVER_PROMPT = """
Create a cover image / thumbnail for a hackathon project called
"TRENCH BUILDER — Democratizing Architectural Engineering with Gemma 4."

COMPOSITION:
Center: A 3D subwoofer/motor assembly rendered in copper and steel,
with orange thermal bloom radiating from the copper windings and
pink electromagnetic field lines swirling around it. The assembly
floats above a dark terrain grid.

Top-left: "TRENCH BUILDER" in bold orange (#ffaa44) technical typography
Top-right: "🤖 Gemma 4" badge in blue (#4466aa)
Bottom: A subtle browser window frame suggesting it runs in-browser

BACKGROUND: Deep navy/black (#050b1a) with subtle circuit-board pattern
or wireframe grid fading into the distance.

STYLE: Clean, technical, professional. Think Linear.app or Stripe
documentation aesthetic crossed with industrial engineering photography.
No cartoon elements. Photorealistic materials on the 3D assembly.

ASPECT RATIO: 16:9
RESOLUTION: 1920x1080

REFERENCE: The aesthetic of the TRENCH BUILDER v5 subwoofer scene —
copper PBR, dark background, glowing thermal/EM effects.
"""

# ═══════════════════════════════════════════════════════
# 4. NANO BANANA 2 — Gallery Images (optional)
# ═══════════════════════════════════════════════════════

GALLERY_PROMPTS = [
    "3D construction scene: walls, foundations, and roof trusses on surveyed terrain with topography contour lines. Dark blue background. Engineering aesthetic.",
    "Split screen showing the same TRENCH BUILDER interface on a high-end workstation and a budget Chromebook. Text: 'One file. Any device.'",
    "Close-up of copper voice coil windings with orange thermal bloom. Anisotropic brushed metal visible. Studio lighting. Industrial photography style.",
    "Gemma 4 chat panel overlay on 3D scene. User asks 'Is this foundation deep enough?' and AI responds with technical guidance. Clean UI design.",
]
