"""
MATERIAL LIBRARY — Comprehensive PBR material definitions for construction/industrial assets.
Run inside Blender: loads materials into the current file for use by any generator script.

Categories:
  - Ferrous metals (raw, brushed, polished, cast, wrought, oiled gear steel)
  - Non-ferrous (copper, brass, aluminum, bronze)
  - Wood (oak, pine, mahogany, plywood, weathered, ash)
  - Concrete / stone (rough, smooth, granite, gravel, asphalt)
  - Industrial (rubber, glass, plastic, cable grease, hydraulic fluid)
  - Surface treatments (galvanized, painted red, anodized, rusted)

Usage:
  from material_library import get_material, list_materials
  mat = get_material("gear_steel_oiled")
"""
import bpy
import math

# ── Node-based PBR material factory ─────────────────────────────

def _make_material(name, base_color, metallic, roughness,
                   specular=0.5, clearcoat=0.0, clearcoat_roughness=0.0,
                   ior=1.45, transmission=0.0, alpha=1.0):
    """Create a Principled BSDF material with the given parameters."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Specular IOR Level"].default_value = specular
    bsdf.inputs["Coat Weight"].default_value = clearcoat
    bsdf.inputs["Coat Roughness"].default_value = clearcoat_roughness
    bsdf.inputs["IOR"].default_value = ior
    bsdf.inputs["Transmission Weight"].default_value = transmission
    bsdf.inputs["Alpha"].default_value = alpha
    return mat


# ── Material catalog ────────────────────────────────────────────

MATERIAL_SPECS = {
    # --- Ferrous Metals ---
    "gear_steel_oiled": {
        "base_color": (0.18, 0.17, 0.15), "metallic": 0.95, "roughness": 0.35,
        "specular": 0.6, "clearcoat": 0.05,
    },
    "gear_steel_worn": {
        "base_color": (0.22, 0.21, 0.19), "metallic": 0.9, "roughness": 0.55,
        "specular": 0.4,
    },
    "raw_steel": {
        "base_color": (0.25, 0.24, 0.22), "metallic": 0.92, "roughness": 0.6,
        "specular": 0.4,
    },
    "brushed_steel": {
        "base_color": (0.38, 0.37, 0.35), "metallic": 0.88, "roughness": 0.3,
        "specular": 0.5,
    },
    "polished_steel": {
        "base_color": (0.55, 0.53, 0.50), "metallic": 0.95, "roughness": 0.12,
        "specular": 0.8, "clearcoat": 0.1,
    },
    "cast_iron": {
        "base_color": (0.12, 0.11, 0.10), "metallic": 0.85, "roughness": 0.75,
        "specular": 0.2,
    },
    "wrought_iron": {
        "base_color": (0.10, 0.09, 0.08), "metallic": 0.8, "roughness": 0.7,
        "specular": 0.15,
    },
    "tool_steel": {
        "base_color": (0.15, 0.14, 0.13), "metallic": 0.98, "roughness": 0.22,
        "specular": 0.7, "clearcoat": 0.03,
    },
    "galvanized_steel": {
        "base_color": (0.55, 0.54, 0.52), "metallic": 0.9, "roughness": 0.4,
        "specular": 0.45,
    },
    "rusted_steel": {
        "base_color": (0.45, 0.22, 0.08), "metallic": 0.3, "roughness": 0.9,
        "specular": 0.05,
    },

    # --- Non-Ferrous ---
    "copper": {
        "base_color": (0.85, 0.38, 0.18), "metallic": 1.0, "roughness": 0.25,
        "specular": 0.7,
    },
    "brass": {
        "base_color": (0.78, 0.65, 0.22), "metallic": 1.0, "roughness": 0.2,
        "specular": 0.65,
    },
    "bronze": {
        "base_color": (0.65, 0.42, 0.18), "metallic": 1.0, "roughness": 0.3,
        "specular": 0.5,
    },
    "aluminum_raw": {
        "base_color": (0.45, 0.44, 0.43), "metallic": 0.85, "roughness": 0.5,
        "specular": 0.4,
    },
    "aluminum_brushed": {
        "base_color": (0.62, 0.61, 0.60), "metallic": 0.82, "roughness": 0.28,
        "specular": 0.5,
    },
    "aluminum_polished": {
        "base_color": (0.78, 0.77, 0.75), "metallic": 0.85, "roughness": 0.08,
        "specular": 0.9,
    },
    "anodized_red": {
        "base_color": (0.75, 0.08, 0.05), "metallic": 0.6, "roughness": 0.2,
        "specular": 0.5, "clearcoat": 0.15,
    },
    "anodized_black": {
        "base_color": (0.04, 0.04, 0.04), "metallic": 0.6, "roughness": 0.18,
        "specular": 0.5, "clearcoat": 0.1,
    },

    # --- Wood ---
    "oak": {
        "base_color": (0.42, 0.28, 0.15), "metallic": 0.0, "roughness": 0.55,
        "specular": 0.3, "clearcoat": 0.05,
    },
    "oak_varnished": {
        "base_color": (0.48, 0.32, 0.18), "metallic": 0.0, "roughness": 0.2,
        "specular": 0.4, "clearcoat": 0.5,
    },
    "pine": {
        "base_color": (0.72, 0.58, 0.35), "metallic": 0.0, "roughness": 0.6,
        "specular": 0.2,
    },
    "plywood": {
        "base_color": (0.58, 0.45, 0.28), "metallic": 0.0, "roughness": 0.5,
        "specular": 0.25,
    },
    "mahogany": {
        "base_color": (0.35, 0.15, 0.08), "metallic": 0.0, "roughness": 0.3,
        "specular": 0.35, "clearcoat": 0.2,
    },
    "weathered_timber": {
        "base_color": (0.38, 0.35, 0.30), "metallic": 0.0, "roughness": 0.85,
        "specular": 0.05,
    },
    "ash": {
        "base_color": (0.65, 0.58, 0.45), "metallic": 0.0, "roughness": 0.45,
        "specular": 0.3,
    },
    "bamboo": {
        "base_color": (0.55, 0.48, 0.25), "metallic": 0.0, "roughness": 0.4,
        "specular": 0.3, "clearcoat": 0.08,
    },

    # --- Concrete / Stone ---
    "concrete_rough": {
        "base_color": (0.35, 0.33, 0.30), "metallic": 0.0, "roughness": 0.85,
        "specular": 0.05,
    },
    "concrete_smooth": {
        "base_color": (0.42, 0.40, 0.37), "metallic": 0.0, "roughness": 0.4,
        "specular": 0.15,
    },
    "concrete_polished": {
        "base_color": (0.48, 0.46, 0.43), "metallic": 0.0, "roughness": 0.15,
        "specular": 0.3, "clearcoat": 0.1,
    },
    "granite": {
        "base_color": (0.38, 0.36, 0.34), "metallic": 0.02, "roughness": 0.35,
        "specular": 0.2,
    },
    "gravel": {
        "base_color": (0.32, 0.30, 0.28), "metallic": 0.0, "roughness": 0.95,
        "specular": 0.02,
    },
    "asphalt": {
        "base_color": (0.12, 0.11, 0.10), "metallic": 0.0, "roughness": 0.8,
        "specular": 0.05,
    },
    "brick": {
        "base_color": (0.52, 0.22, 0.12), "metallic": 0.0, "roughness": 0.7,
        "specular": 0.08,
    },

    # --- Industrial / Misc ---
    "rubber_black": {
        "base_color": (0.05, 0.05, 0.05), "metallic": 0.0, "roughness": 0.7,
        "specular": 0.1,
    },
    "rubber_conveyor": {
        "base_color": (0.08, 0.07, 0.07), "metallic": 0.0, "roughness": 0.65,
        "specular": 0.08,
    },
    "glass_clear": {
        "base_color": (0.95, 0.96, 0.98), "metallic": 0.0, "roughness": 0.02,
        "specular": 1.0, "ior": 1.52, "transmission": 0.95,
    },
    "glass_frosted": {
        "base_color": (0.90, 0.91, 0.93), "metallic": 0.0, "roughness": 0.35,
        "specular": 0.8, "ior": 1.52, "transmission": 0.6,
    },
    "plastic_pvc": {
        "base_color": (0.75, 0.74, 0.72), "metallic": 0.0, "roughness": 0.4,
        "specular": 0.3,
    },
    "plastic_abs_black": {
        "base_color": (0.06, 0.06, 0.06), "metallic": 0.0, "roughness": 0.35,
        "specular": 0.35,
    },
    "cable_grease": {
        "base_color": (0.08, 0.07, 0.05), "metallic": 0.1, "roughness": 0.25,
        "specular": 0.6, "clearcoat": 0.3,
    },
    "hydraulic_oil": {
        "base_color": (0.65, 0.35, 0.08), "metallic": 0.05, "roughness": 0.05,
        "specular": 0.9, "ior": 1.47, "transmission": 0.4,
    },
    "carbon_fiber": {
        "base_color": (0.08, 0.08, 0.09), "metallic": 0.3, "roughness": 0.3,
        "specular": 0.4, "clearcoat": 0.4,
    },

    # --- Painted / Coated ---
    "paint_red_industrial": {
        "base_color": (0.65, 0.06, 0.04), "metallic": 0.05, "roughness": 0.4,
        "specular": 0.3, "clearcoat": 0.08,
    },
    "paint_yellow_safety": {
        "base_color": (0.92, 0.72, 0.05), "metallic": 0.05, "roughness": 0.35,
        "specular": 0.25,
    },
    "paint_green_machine": {
        "base_color": (0.15, 0.35, 0.18), "metallic": 0.08, "roughness": 0.4,
        "specular": 0.3,
    },
    "paint_white_enamel": {
        "base_color": (0.92, 0.91, 0.88), "metallic": 0.02, "roughness": 0.18,
        "specular": 0.4, "clearcoat": 0.15,
    },
    "powder_coat_black": {
        "base_color": (0.04, 0.04, 0.04), "metallic": 0.03, "roughness": 0.25,
        "specular": 0.3, "clearcoat": 0.05,
    },
}

# ── Public API ──────────────────────────────────────────────────

def load_all():
    """Create all materials in the current Blender session. Idempotent."""
    count = 0
    for name, spec in MATERIAL_SPECS.items():
        if name not in bpy.data.materials:
            _make_material(name, **spec)
            count += 1
    return count

def get_material(name):
    """Get a material by name, loading it if needed."""
    if name not in bpy.data.materials:
        if name in MATERIAL_SPECS:
            _make_material(name, **MATERIAL_SPECS[name])
        else:
            raise KeyError(f"Unknown material: {name}. Available: {list(MATERIAL_SPECS.keys())}")
    return bpy.data.materials[name]

def list_materials():
    """Return sorted list of all material names."""
    return sorted(MATERIAL_SPECS.keys())

def list_by_category():
    """Return materials grouped by category."""
    return {
        "Ferrous Metals": [k for k in MATERIAL_SPECS if k.endswith("steel") or
                           k in ("cast_iron", "wrought_iron", "tool_steel", "galvanized_steel", "rusted_steel")],
        "Non-Ferrous": ["copper", "brass", "bronze", "aluminum_raw", "aluminum_brushed",
                        "aluminum_polished", "anodized_red", "anodized_black"],
        "Wood": ["oak", "oak_varnished", "pine", "plywood", "mahogany", "weathered_timber", "ash", "bamboo"],
        "Concrete / Stone": ["concrete_rough", "concrete_smooth", "concrete_polished",
                            "granite", "gravel", "asphalt", "brick"],
        "Industrial": ["rubber_black", "rubber_conveyor", "glass_clear", "glass_frosted",
                       "plastic_pvc", "plastic_abs_black", "cable_grease", "hydraulic_oil", "carbon_fiber"],
        "Painted / Coated": ["paint_red_industrial", "paint_yellow_safety", "paint_green_machine",
                            "paint_white_enamel", "powder_coat_black"],
    }


# ── CLI (when run standalone) ───────────────────────────────────

if __name__ == "__main__":
    count = load_all()
    print(f"Material library: {count} materials loaded "
          f"({len(MATERIAL_SPECS)} defined, {count} new)")
    cats = list_by_category()
    for cat, names in cats.items():
        print(f"  {cat}: {len(names)}")
