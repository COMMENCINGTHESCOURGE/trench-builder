import pytest
from trench_builder.domains.typography import TypographyAssembly, MATERIAL_PRESETS
from trench_builder.core.component_spec import AssemblySpec

def test_typography_assembly_build():
    """Verify that TypographyAssembly.build generates a valid AssemblySpec."""
    spec = TypographyAssembly.build(
        text="TEST",
        font="Eurostile Bold",
        glyph_material="brushed_chrome",
        substrate_material="sandblasted_aluminum"
    )
    
    assert isinstance(spec, AssemblySpec)
    assert spec.model_id == "typo_test_brushed_chrome"
    assert spec.domain == "typography"
    
    # Check components
    components = spec.components
    has_emission = any(l.channel == "emission" for l in MATERIAL_PRESETS["brushed_chrome"].layers)
    expected_len = 1 + len("TEST") * (2 if has_emission else 1)
    assert len(components) == expected_len
    
    # Verify substrate is root
    substrate = components[0]
    assert substrate.name == "substrate"
    assert substrate.parent is None
    
    # Verify glyphs are parented to substrate
    glyph_components = [c for c in components if c.name.startswith("glyph_")]
    assert len(glyph_components) == len("TEST")
    for glyph in glyph_components:
        assert glyph.parent == "substrate"
        assert glyph.parameters["glyph"]["character"] in "TEST"


def test_presets():
    """Verify that all default use-case presets are valid."""
    for name, config in TypographyAssembly.PRESETS.items():
        spec = TypographyAssembly.build(
            text="PRESET",
            font=config["font"],
            glyph_material=config["glyph_material"],
            substrate_material=config["substrate_material"],
            cap_height=config["cap_height"],
            extrusion_depth=config["extrusion_depth"],
            bevel_profile=config["bevel_profile"],
            substrate_depth=config["substrate_depth"],
        )
        assert isinstance(spec, AssemblySpec)
        has_emission = any(l.channel == "emission" for l in MATERIAL_PRESETS[config["glyph_material"]].layers)
        expected_len = 1 + len("PRESET") * (2 if has_emission else 1)
        assert len(spec.components) == expected_len


def test_patch_v_compliance():
    """Verify that each layer in MATERIAL_PRESETS targets a different channel (Patch v)."""
    for preset_name, stack in MATERIAL_PRESETS.items():
        channels = [layer.channel for layer in stack.layers]
        # No duplicate channels
        assert len(channels) == len(set(channels)), f"Duplicate PBR channel detected in preset {preset_name}"
