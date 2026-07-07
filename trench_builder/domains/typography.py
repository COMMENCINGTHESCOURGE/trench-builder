"""
Trench-Builder Domain: Typography — Procedural 3D Signage & Badging

Generates AssemblySpec objects for extruded 3D text, vehicle badges,
storefront signs, mecha decals, and arcade cabinet lettering.

Architecture:
  core/vinculum.py   → Vinculum.typography() constraints (G2, kerning, coverage)
  domains/typography.py → THIS FILE — assembly generator
  builders/blender_typography.py → Blender backend (mesh + materials + GLB)

Vinculum Four Roles (VINCULUM_FOUR_ROLES.md):
  Role 1 (Division):   glyph_area / substrate_area = coverage_ratio
  Role 2 (Grouping):   {word_block} = kerned unit, alignment computed as one
  Role 3 (Multiply):   base_metal × surface_noise × edge_emission = appearance
  Role 4 (Sequence):   variant̄ = iterate sweep until converged

Fractype Integration:
  Material stacks encoded as FracType fractions:
    (Raw Cast Iron / Frosted Glass Edge-glow) = final_surface

Patch v compliance:
  Each material variant routes to a DIFFERENT channel:
    variant_A → roughness    variant_B → metallic
    variant_C → emission     variant_D → clearcoat
  Not four waves on one channel.

Patch vii compliance:
  Noise across glyphs is phase-offset by glyph_index × 0.3
  No synchronized modulation.

Patch ix compliance:
  All procedural noise takes uTime as input — materials animate.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import math
import json

from ..core.vinculum import Vinculum, Constraint, ConstraintKind, JointType
from ..core.component_spec import ComponentSpec, AssemblySpec


# ═══════════════════════════════════════════════════════
# Material Presets — Fractype-encoded material stacks
# ═══════════════════════════════════════════════════════

@dataclass
class MaterialLayer:
    """A single layer in the Fractype material stack.

    Each layer targets a DIFFERENT PBR channel (Patch v):
      - base → albedo/metallic
      - noise → roughness (procedural, never static texture)
      - emission → emissive rim / edge glow
      - clearcoat → surface lacquer / glass
    """
    channel: str                          # "albedo" | "roughness" | "metallic" | "emission" | "clearcoat"
    source: str                           # "procedural" | "constant" | "texture_path"
    value: Any = None                     # float for constant, dict for procedural params
    noise_type: Optional[str] = None      # "voronoi" | "perlin" | "anisotropic" | "gradient"
    phase_offset: float = 0.0            # Patch vii: per-glyph phase offset
    animate: bool = True                  # Patch ix: uTime drives this layer

    def to_dict(self) -> dict:
        return {
            "channel": self.channel,
            "source": self.source,
            "value": self.value,
            "noise_type": self.noise_type,
            "phase_offset": self.phase_offset,
            "animate": self.animate,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MaterialLayer":
        return cls(**data)


@dataclass
class MaterialStack:
    """Full PBR material as a Fractype fraction.

    Encoded as: (numerator / denominator) = realized appearance
      numerator   = primary surface identity (e.g., "Raw Cast Iron")
      denominator = modifiers & effects (e.g., "Frosted Glass Edge-glow")
    """
    name: str
    numerator: str                        # Primary identity
    denominator: str                      # Modifiers
    layers: List[MaterialLayer] = field(default_factory=list)

    def fractype_encode(self) -> str:
        """Encode as Fractype fraction string."""
        return f"({self.numerator}/{self.denominator})"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "numerator": self.numerator,
            "denominator": self.denominator,
            "fractype": self.fractype_encode(),
            "layers": [l.to_dict() for l in self.layers],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MaterialStack":
        layers = [MaterialLayer.from_dict(l) for l in data.get("layers", [])]
        return cls(
            name=data["name"],
            numerator=data["numerator"],
            denominator=data["denominator"],
            layers=layers,
        )


# ═══════════════════════════════════════════════════════
# Material Preset Library
# ═══════════════════════════════════════════════════════

MATERIAL_PRESETS: Dict[str, MaterialStack] = {
    "raw_cast_iron": MaterialStack(
        name="Raw Cast Iron",
        numerator="Raw Cast Iron",
        denominator="Frosted Glass Edge-glow",
        layers=[
            MaterialLayer("albedo", "constant", {"r": 0.15, "g": 0.13, "b": 0.12}),
            MaterialLayer("metallic", "constant", 0.85),
            MaterialLayer("roughness", "procedural", {"scale": 12.0, "detail": 4},
                          noise_type="voronoi", phase_offset=0.0, animate=True),
            MaterialLayer("emission", "procedural", {"color": [0.3, 0.8, 1.0], "intensity": 2.5,
                                                      "falloff": "fresnel", "edge_width": 0.02},
                          noise_type="gradient", phase_offset=0.0, animate=True),
            MaterialLayer("clearcoat", "constant", 0.0),
        ]
    ),
    "brushed_chrome": MaterialStack(
        name="Brushed Chrome",
        numerator="Brushed Chrome",
        denominator="Mirror Polish Edge-catch",
        layers=[
            MaterialLayer("albedo", "constant", {"r": 0.75, "g": 0.76, "b": 0.78}),
            MaterialLayer("metallic", "constant", 0.95),
            MaterialLayer("roughness", "procedural", {"scale": 40.0, "stretch": [1.0, 0.05, 1.0]},
                          noise_type="anisotropic", phase_offset=0.0, animate=True),
            MaterialLayer("emission", "procedural", {"color": [1.0, 1.0, 1.0], "intensity": 0.8,
                                                      "falloff": "fresnel", "edge_width": 0.01},
                          noise_type="gradient", phase_offset=0.0, animate=True),
            MaterialLayer("clearcoat", "constant", 0.7),
        ]
    ),
    "sandblasted_aluminum": MaterialStack(
        name="Sandblasted Aluminum",
        numerator="Sandblasted Aluminum",
        denominator="Machined Swirl Substrate",
        layers=[
            MaterialLayer("albedo", "constant", {"r": 0.65, "g": 0.66, "b": 0.68}),
            MaterialLayer("metallic", "constant", 0.7),
            MaterialLayer("roughness", "procedural", {"scale": 8.0, "swirl_frequency": 3.0},
                          noise_type="anisotropic", phase_offset=0.0, animate=False),
            MaterialLayer("emission", "constant", 0.0),
            MaterialLayer("clearcoat", "constant", 0.3),
        ]
    ),
    "bismuth_crystal": MaterialStack(
        name="Bismuth Crystal",
        numerator="Bismuth Iridescence",
        denominator="Thermal Stress Crystallization",
        layers=[
            MaterialLayer("albedo", "procedural", {"palette": "rainbow", "scale": 6.0},
                          noise_type="voronoi", phase_offset=0.0, animate=True),
            MaterialLayer("metallic", "constant", 0.9),
            MaterialLayer("roughness", "procedural", {"scale": 3.0, "step_edges": True},
                          noise_type="voronoi", phase_offset=0.5, animate=True),
            MaterialLayer("emission", "procedural", {"color": [0.6, 0.2, 1.0], "intensity": 1.2,
                                                      "falloff": "edge_detect", "edge_width": 0.03},
                          noise_type="gradient", phase_offset=0.25, animate=True),
            MaterialLayer("clearcoat", "constant", 0.6),
        ]
    ),
    "neon_backlit": MaterialStack(
        name="Neon Backlit",
        numerator="Frosted Acrylic",
        denominator="Neon Tube Emission",
        layers=[
            MaterialLayer("albedo", "constant", {"r": 0.95, "g": 0.95, "b": 0.97}),
            MaterialLayer("metallic", "constant", 0.0),
            MaterialLayer("roughness", "constant", 0.4),
            MaterialLayer("emission", "procedural", {"color": [1.0, 0.1, 0.4], "intensity": 8.0,
                                                      "falloff": "volume", "edge_width": 0.0},
                          noise_type="perlin", phase_offset=0.0, animate=True),
            MaterialLayer("clearcoat", "constant", 0.9),
        ]
    ),
}


# ═══════════════════════════════════════════════════════
# Glyph Geometry Parameters
# ═══════════════════════════════════════════════════════

@dataclass
class GlyphParams:
    """Per-glyph geometric parameters."""
    character: str
    cap_height: float = 1.0               # Normalized cap height
    extrusion_depth: float = 0.15         # Depth as ratio of cap height
    bevel_depth: float = 0.02             # Bevel depth
    bevel_segments: int = 12              # Segments for G2 bevel curve
    bevel_profile: str = "g2_catmull"     # "g2_catmull" | "g2_bezier" | "chamfer" | "round"
    offset_x: float = 0.0                # Position offset from kerning
    noise_seed: int = 0                   # Per-glyph noise seed (Patch vii)

    def to_dict(self) -> dict:
        return {
            "character": self.character,
            "cap_height": self.cap_height,
            "extrusion_depth": self.extrusion_depth,
            "bevel_depth": self.bevel_depth,
            "bevel_segments": self.bevel_segments,
            "bevel_profile": self.bevel_profile,
            "offset_x": self.offset_x,
            "noise_seed": self.noise_seed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GlyphParams":
        return cls(**data)


# ═══════════════════════════════════════════════════════
# Typography Assembly Generator
# ═══════════════════════════════════════════════════════

class TypographyAssembly:
    """Domain generator: text string → AssemblySpec.

    Consumes font/material/geometry parameters and produces a fully
    constrained, serializable AssemblySpec following the same pattern
    as character.py and environment.py.

    Usage:
        assembly = TypographyAssembly.build(
            text="CONVEYOR",
            font="Eurostile Bold",
            glyph_material="raw_cast_iron",
            substrate_material="sandblasted_aluminum",
        )
        assembly.save_json("specs/conveyor_badge.json")
    """

    # Default substrate dimensions (normalized)
    DEFAULT_SUBSTRATE = {
        "width": 8.0,
        "height": 1.5,
        "depth": 0.1,
        "corner_radius": 0.05,
        "material": "sandblasted_aluminum",
        "finish": "machined_swirls",
    }

    # Use-case presets
    PRESETS: Dict[str, Dict[str, Any]] = {
        "vehicle_badge": {
            "font": "Eurostile Bold",
            "glyph_material": "brushed_chrome",
            "substrate_material": "sandblasted_aluminum",
            "cap_height": 0.8,
            "extrusion_depth": 0.12,
            "bevel_profile": "g2_catmull",
            "substrate_depth": 0.05,
            "projection_mode": "shrinkwrap",
            "tags": ["automotive", "chrome", "badge"],
        },
        "storefront_sign": {
            "font": "Eurostile Bold",
            "glyph_material": "raw_cast_iron",
            "substrate_material": "sandblasted_aluminum",
            "cap_height": 1.2,
            "extrusion_depth": 0.18,
            "bevel_profile": "g2_bezier",
            "substrate_depth": 0.15,
            "projection_mode": "planar",
            "tags": ["signage", "storefront", "cast_iron"],
        },
        "mecha_decal": {
            "font": "Eurostile Bold",
            "glyph_material": "brushed_chrome",
            "substrate_material": "sandblasted_aluminum",
            "cap_height": 0.4,
            "extrusion_depth": 0.05,
            "bevel_profile": "chamfer",
            "substrate_depth": 0.02,
            "projection_mode": "uv_decal",
            "surface_conformity": 0.8,
            "tags": ["tactical", "mecha", "decal"],
        },
        "arcade_cabinet": {
            "font": "Press Start 2P",
            "glyph_material": "neon_backlit",
            "substrate_material": "sandblasted_aluminum",
            "cap_height": 1.0,
            "extrusion_depth": 0.1,
            "bevel_profile": "round",
            "substrate_depth": 0.2,
            "projection_mode": "planar",
            "tags": ["retro", "arcade", "neon"],
        },
        "conveyor_badge": {
            "font": "Eurostile Bold",
            "glyph_material": "raw_cast_iron",
            "substrate_material": "sandblasted_aluminum",
            "cap_height": 1.0,
            "extrusion_depth": 0.15,
            "bevel_profile": "g2_catmull",
            "substrate_depth": 0.1,
            "projection_mode": "planar",
            "tags": ["badge", "industrial", "conveyor"],
        },
    }

    @classmethod
    def build(
        cls,
        text: str,
        font: str = "Eurostile Bold",
        glyph_material: str = "raw_cast_iron",
        substrate_material: str = "sandblasted_aluminum",
        cap_height: float = 1.0,
        extrusion_depth: float = 0.15,
        bevel_profile: str = "g2_catmull",
        bevel_segments: int = 12,
        substrate_depth: float = 0.1,
        projection_mode: str = "planar",
        surface_conformity: float = 0.0,
        model_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> AssemblySpec:
        """Build a typography AssemblySpec from parameters.

        Returns a fully constrained AssemblySpec with:
          - substrate plate (root)
          - per-glyph letter components
          - edge_glow emission components per glyph
          - global typography vinculum
        """
        if model_id is None:
            model_id = f"typo_{text.lower().replace(' ', '_')}_{glyph_material}"

        # ── Global vinculum: typography constraints ──
        global_vinc = Vinculum.typography()

        # ── Substrate: root component ──
        substrate_width = len(text) * cap_height * 0.75 + cap_height * 0.5
        substrate_height = cap_height * 1.5

        glyph_mat = MATERIAL_PRESETS.get(glyph_material)
        substrate_mat = MATERIAL_PRESETS.get(substrate_material)

        substrate = ComponentSpec(
            name="substrate",
            component_type="plate",
            parent=None,
            joint_type=JointType.FIXED,
            parameters={
                "width": substrate_width,
                "height": substrate_height,
                "depth": substrate_depth,
                "corner_radius": 0.05,
                "material": substrate_mat.to_dict() if substrate_mat else substrate_material,
                "finish": "machined_swirls",
            },
            tags=["substrate", "root"],
        )

        components: List[ComponentSpec] = [substrate]

        # ── Per-glyph components ──
        # Kerning: simple monospace for now, font-metric kerning in builder
        glyph_width = cap_height * 0.65
        total_text_width = len(text) * glyph_width
        start_x = -total_text_width / 2 + glyph_width / 2

        for i, char in enumerate(text):
            glyph = GlyphParams(
                character=char,
                cap_height=cap_height,
                extrusion_depth=extrusion_depth,
                bevel_depth=cap_height * 0.02,
                bevel_segments=bevel_segments,
                bevel_profile=bevel_profile,
                offset_x=start_x + i * glyph_width,
                noise_seed=i * 7 + 42,  # Deterministic per-glyph seed
            )

            # Phase-offset per glyph (Patch vii)
            glyph_phase = i * 0.3

            # Build material layers with per-glyph phase offset
            glyph_layers = []
            if glyph_mat:
                for layer in glyph_mat.layers:
                    offset_layer = MaterialLayer(
                        channel=layer.channel,
                        source=layer.source,
                        value=layer.value,
                        noise_type=layer.noise_type,
                        phase_offset=layer.phase_offset + glyph_phase,
                        animate=layer.animate,
                    )
                    glyph_layers.append(offset_layer)

            letter_comp = ComponentSpec(
                name=f"glyph_{i}_{char}",
                component_type="letter",
                parent="substrate",
                joint_type=JointType.FIXED,
                parameters={
                    "glyph": glyph.to_dict(),
                    "font": font,
                    "material": {
                        "stack": [l.to_dict() for l in glyph_layers],
                        "fractype": glyph_mat.fractype_encode() if glyph_mat else f"({glyph_material}/_)",
                    },
                },
                tags=["glyph", f"char_{char}"],
                surface_normal=[0.0, 0.0, 1.0],
                projection_mode=projection_mode,
                surface_conformity=surface_conformity,
            )
            components.append(letter_comp)

            # Edge glow emission as separate component (routes to emission channel — Patch v)
            if glyph_mat and any(l.channel == "emission" for l in glyph_mat.layers):
                emission_layer = next(l for l in glyph_mat.layers if l.channel == "emission")
                edge_glow = ComponentSpec(
                    name=f"edge_glow_{i}_{char}",
                    component_type="emissive_rim",
                    parent=f"glyph_{i}_{char}",
                    joint_type=JointType.FIXED,
                    parameters={
                        "color": emission_layer.value.get("color", [1, 1, 1]) if isinstance(emission_layer.value, dict) else [1, 1, 1],
                        "intensity": emission_layer.value.get("intensity", 1.0) if isinstance(emission_layer.value, dict) else 1.0,
                        "falloff": emission_layer.value.get("falloff", "fresnel") if isinstance(emission_layer.value, dict) else "fresnel",
                        "edge_width": emission_layer.value.get("edge_width", 0.02) if isinstance(emission_layer.value, dict) else 0.02,
                        "phase_offset": glyph_phase,
                        "animate": True,
                    },
                    tags=["emission", "edge_glow"],
                )
                components.append(edge_glow)

        # ── Assemble ──
        assembly = AssemblySpec(
            model_id=model_id,
            domain="typography",
            components=components,
            global_vinculum=global_vinc,
            metadata={
                "text": text,
                "font": font,
                "glyph_material_id": glyph_material,
                "substrate_material_id": substrate_material,
                "bevel_profile": bevel_profile,
                "fractype_surface": glyph_mat.fractype_encode() if glyph_mat else "",
                "fractype_substrate": substrate_mat.fractype_encode() if substrate_mat else "",
                "generator": "TypographyAssembly",
                "generator_version": "1.0",
            },
            version="1.0",
        )

        # ── Tags from caller ──
        if tags:
            assembly.metadata["tags"] = tags

        return assembly

    @classmethod
    def from_preset(cls, preset_name: str, text: Optional[str] = None) -> AssemblySpec:
        """Build from a named preset configuration.

        Available presets:
          - vehicle_badge
          - storefront_sign
          - mecha_decal
          - arcade_cabinet
          - conveyor_badge
        """
        if preset_name not in cls.PRESETS:
            available = ", ".join(cls.PRESETS.keys())
            raise ValueError(f"Unknown preset '{preset_name}'. Available: {available}")

        preset = cls.PRESETS[preset_name].copy()
        preset_tags = preset.pop("tags", [])

        if text is None:
            # Default text from preset name
            text = preset_name.upper().replace("_", " ")

        return cls.build(text=text, tags=preset_tags, **preset)

    @classmethod
    def sweep(
        cls,
        text: str,
        iterations: int = 20,
        fonts: Optional[List[str]] = None,
        materials: Optional[List[str]] = None,
        bevel_profiles: Optional[List[str]] = None,
    ) -> List[AssemblySpec]:
        """Generate N parameter-sweep variants for evaluation.

        Vinculum Role 4 (Sequence): variant̄ = iterate until converged.
        Each variant routes material differences to DIFFERENT channels (Patch v).
        """
        if fonts is None:
            fonts = ["Eurostile Bold", "DIN Condensed", "Futura Heavy", "Bebas Neue", "Orbitron"]
        if materials is None:
            materials = list(MATERIAL_PRESETS.keys())
        if bevel_profiles is None:
            bevel_profiles = ["g2_catmull", "g2_bezier", "chamfer", "round"]

        variants = []
        for i in range(iterations):
            font = fonts[i % len(fonts)]
            mat = materials[i % len(materials)]
            bevel = bevel_profiles[i % len(bevel_profiles)]
            # Vary extrusion depth across sweep
            depth = 0.10 + (i / iterations) * 0.10  # 0.10 → 0.20
            segments = 8 + (i % 4) * 4              # 8, 12, 16, 20

            variant = cls.build(
                text=text,
                font=font,
                glyph_material=mat,
                extrusion_depth=depth,
                bevel_profile=bevel,
                bevel_segments=segments,
                model_id=f"sweep_{text.lower()}_{i:03d}",
                tags=["sweep", f"variant_{i}"],
            )
            variant.metadata["sweep_index"] = i
            variant.metadata["sweep_font"] = font
            variant.metadata["sweep_material"] = mat
            variant.metadata["sweep_bevel"] = bevel
            variant.metadata["sweep_extrusion_depth"] = depth
            variants.append(variant)

        return variants

    @classmethod
    def validate_measurements(cls, assembly: AssemblySpec) -> List[str]:
        """Validate a typography assembly against its vinculum constraints.

        Computes measurements from the assembly's own parameters and checks
        them against the global vinculum.
        """
        measurements = {}

        # Extract measurements from components
        glyphs = [c for c in assembly.components if c.component_type == "letter"]
        substrate = assembly.get_component("substrate")

        if glyphs and substrate:
            # Coverage ratio (Role 1: glyph_area / substrate_area)
            glyph_area = sum(
                g.parameters.get("glyph", {}).get("cap_height", 1.0) *
                g.parameters.get("glyph", {}).get("cap_height", 1.0) * 0.65
                for g in glyphs
            )
            sub_area = (substrate.parameters.get("width", 1.0) *
                        substrate.parameters.get("height", 1.0))
            if sub_area > 0:
                measurements["coverage_ratio"] = glyph_area / sub_area

        if glyphs:
            # Bevel continuity
            first_glyph = glyphs[0].parameters.get("glyph", {})
            profile = first_glyph.get("bevel_profile", "chamfer")
            if profile.startswith("g2"):
                measurements["bevel_continuity"] = 2.0
            elif profile.startswith("g1") or profile == "round":
                measurements["bevel_continuity"] = 1.0
            else:
                measurements["bevel_continuity"] = 0.0

            # Extrusion depth ratio
            cap_h = first_glyph.get("cap_height", 1.0)
            ext_d = first_glyph.get("extrusion_depth", 0.15)
            if cap_h > 0:
                measurements["extrusion_depth_ratio"] = ext_d / cap_h

            # Chamfer segments
            measurements["chamfer_segments"] = float(first_glyph.get("bevel_segments", 12))

            # Kerning tolerance (assume 0.0 for generator-built specs)
            measurements["kerning_tolerance"] = 0.0

        return assembly.validate_all(measurements)
