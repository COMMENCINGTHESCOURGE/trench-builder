# DISTANCE FIELD RENDERING — Foundational Technique
# Proximity-Based Falloff in the TRENCH BUILDER Pipeline
# May 2026

# The core equation: d = √((x_obj - x_target)² + (y_obj - y_target)²)
# Opacity = 1 - (distance / maxRadius)  → with easing curve

# ═══════════════════════════════════════════════════════
# ALREADY IMPLEMENTED — Distance fields in existing systems
# ═══════════════════════════════════════════════════════

EXISTING_DF = {
    "fog": {
        "system": "TRENCH BUILDER v3/v4/v5",
        "technique": "FogExp2(0x000010, 0.003) — exponential distance fog",
        "equation": "opacity = exp(-distance² × density)",
        "visual": "Distant objects lose contrast, saturation, sharpness",
    },
    "god_rays": {
        "system": "TRENCH BUILDER v4",
        "technique": "Screen-space distance from sun position → radial light shafts",
        "equation": "ray_intensity = exp(-distance × 3.5) × intensity",
        "visual": "Volumetric light beams from sun direction",
    },
    "ssao": {
        "system": "TRENCH BUILDER v4",
        "technique": "Sample neighboring pixel brightness → darken crevices",
        "equation": "ao = 1.0 - Σ(length(color_diff)) × 0.015 × intensity",
        "visual": "Contact shadows in corners and crevices",
    },
    "film_grain": {
        "system": "TRENCH BUILDER v4",
        "technique": "Distance-independent noise (the exception — grain is uniform)",
        "visual": "Perceptual realism through imperfection",
    },
}

# ═══════════════════════════════════════════════════════
# PLANNED — Distance fields to add next
# ═══════════════════════════════════════════════════════

PLANNED_DF = {
    "thermal_bloom": {
        "system": "TRENCH BUILDER v5+",
        "technique": "Distance from voice coil → emissive intensity falloff",
        "curve": "Smoothstep — organic heat diffusion feel",
        "visual": "Copper glows red at center, fades to dark at magnet edge",
    },
    "caustic_projection": {
        "system": "TRENCH BUILDER v5+",
        "technique": "Distance from acrylic dome → caustic pattern intensity",
        "curve": "Exponential — light scatters exponentially through medium",
        "visual": "Bright interference patterns near dome, fading outward",
    },
    "em_field_decay": {
        "system": "v5 EM visualization",
        "technique": "Distance from coil gap → flux line opacity and particle density",
        "curve": "Inverse square — 1/d² decay (physical accuracy)",
        "visual": "Dense bright flux lines at gap, sparse dim lines at distance",
    },
}

# ═══════════════════════════════════════════════════════
# EASING CURVES — The "Feel" of Distance
# ═══════════════════════════════════════════════════════

EASING = {
    "linear":      "t = 1 - d/R                 → Uniform fade. Mechanical feel.",
    "exponential": "t = exp(-d × k)             → Fast initial drop, long tail. Glow feel.",
    "smoothstep":  "t = 3t² - 2t³ where t=1-d/R → Ease in/out. Organic, natural feel.",
    "inverse_sq":  "t = 1/(1 + d²)             → Physical accuracy (light, gravity, EM).",
    "gaussian":    "t = exp(-d²/(2σ²))          → Smooth bell curve. Heat diffusion feel.",
}

# ═══════════════════════════════════════════════════════
# DEPLOYMENT PATHS — Per environment
# ═══════════════════════════════════════════════════════

# 2D Canvas / DOM:   Loop objects, update CSS opacity per frame
# Three.js shaders:  Pass target pos as uniform → Fragment Shader computes per-pixel
# WebGPU compute:    Parallel distance calc for millions of particles
# Terminal (ANSI):   Distance → Unicode block density (░▒▓█) — labyrinth explorer uses this

# The labyrinth_explorer.py already implements distance-field rendering
# in the terminal: distance from camera → luminance → dither → Unicode block character.
# This is the same technique operating in a completely different output medium.
