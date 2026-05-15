# ELECTROMAGNETIC POWERTRAIN DOMAIN — New Research Frontier
# Discovered: May 15, 2026 — from DaShawn's technical conversation
#
# This domain sits at the intersection of:
# - Physically Based Rendering (Cook-Torrance, multi-scatter GGX)
# - Electromagnetic simulation (Maxwell stress tensors)
# - Real-time vehicle dynamics (NVH analysis, torque ripple)
# - Automotive-grade CAD (SiC inverter, hairpin windings, oil cooling)
#
# The Onshape engine assembly (crank/piston/connecting rod) is the ICE side.
# This domain covers the EV/hybrid side — electric motors and power electronics.

# ═══════════════════════════════════════════════════════
# KEY TECHNOLOGIES IDENTIFIED
# ═══════════════════════════════════════════════════════

ELECTROMAGNETIC_DOMAIN = {
    "copper_anisotropy": {
        "description": "Brushed copper hairpin windings with directional micro-facet roughness",
        "technique": "Anisotropic GGX BRDF — roughness varies with tangent direction",
        "status": "not_implemented",
        "priority": 1,
    },
    "polymer_caustics": {
        "description": "Caustic light patterns through molded polymer housings",
        "technique": "Screen-space photon splatting or baked caustic maps",
        "status": "not_implemented",
        "priority": 1,
    },
    "subsurface_polymers": {
        "description": "Light diffusion through semi-transparent plastic components",
        "technique": "Transmission + thickness in MeshPhysicalMaterial (already in skin mat)",
        "status": "started",
        "priority": 2,
    },
    "thermal_mapping": {
        "description": "Material-specific emissive temperature gradients",
        "technique": "Per-component emissiveIntensity driven by heat simulation",
        "status": "planned",
        "priority": 1,
    },
    "oil_flow_visualization": {
        "description": "Semi-transparent manifold volumes for cooling channel fluid particles",
        "technique": "GPU particle system clipped to manifold geometry",
        "status": "not_implemented",
        "priority": 2,
    },
    "magnetic_field_overlay": {
        "description": "Maxwell stress tensor visualization over rotor-stator air gap",
        "technique": "Vector field rendering with non-manifold surface integration",
        "status": "not_implemented",
        "priority": 3,
    },
    "shader_lod_cascade": {
        "description": "Full Cook-Torrance at <50cm, cubemap fallbacks at distance",
        "technique": "Distance-based material LOD switching",
        "status": "not_implemented",
        "priority": 2,
    },
    "baked_radiance_transfer": {
        "description": "Static lighting baked into lightmaps + real-time metalness/roughness",
        "technique": "PMREMGenerator for environment maps + dynamic material params",
        "status": "not_implemented",
        "priority": 2,
    },
    "configurable_dashboard": {
        "description": "Toggle between thermal/EM/structural visualization modes",
        "technique": "Multi-pass rendering with post-process mode switching",
        "status": "not_implemented",
        "priority": 1,
    },
}

# ═══════════════════════════════════════════════════════
# INTEGRATION WITH TRENCH BUILDER v5
# ═══════════════════════════════════════════════════════
#
# The Onshape CAD imports (CRANKSHAFT, PISTON, CONNECTING_ROD, ENG_BLOCK)
# provide the mechanical foundation. The electromagnetic domain extends this
# into EV/hybrid territory.
#
# Priority order for v5:
# 1. Engine animation (crankshaft rotation → piston oscillation)
# 2. Configurable dashboard (thermal/EM/structural toggles)
# 3. Copper anisotropy + polymer caustics
# 4. Thermal mapping via emissive gradients
#
# These are all achievable in single-file HTML with Three.js + shader passes.
# The Shader LOD cascade and baked radiance transfer are optimizations for
# production deployment — not needed for the MVP dashboard.
