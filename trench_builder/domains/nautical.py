"""Trench-Builder: Nautical Domain — Ships, Sailboats, Hulls."""
from ..core import AssemblySpec, ComponentSpec, Vinculum, JointType


def generate_sailboat(model_id: str = "sailboat_v1") -> AssemblySpec:
    """Generate a constraint-validated sailboat hull assembly."""
    spec = AssemblySpec(
        model_id=model_id,
        domain="ship",
        global_vinculum=Vinculum("ship", {
            "hull_length_beam_ratio": 4.0,
            "draft_displacement_ratio": 0.12,
        }),
        metadata={"material": "PLA", "tolerance_mm": 0.25, "print_orientation": "split_hull"},
    )

    spec.add(ComponentSpec("HULL", JointType.FIXED, parent=None,
        vinculum=Vinculum("ship", {"block_coefficient": 0.65}),
        parameters={"length_mm": 120, "beam_mm": 30, "draft_mm": 15}))

    spec.add(ComponentSpec("KEEL", JointType.FIXED, parent="HULL",
        vinculum=Vinculum("ship", {"keel_mass_displacement_ratio": 0.35, "keel_depth_draft_ratio": 0.7}),
        parameters={"depth_mm": 10, "mass_grams": 500}))

    spec.add(ComponentSpec("RUDDER", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-35, 35),
        parent="HULL",
        vinculum=Vinculum("ship", {"rudder_area_hull_lateral_ratio": 0.03, "max_rudder_torque_nm": 0.15}),
        parameters={"chord_mm": 5, "span_mm": 12}))

    spec.add(ComponentSpec("MAST", JointType.FIXED, parent="HULL",
        vinculum=Vinculum("ship", {"mast_height_hull_length_ratio": 1.3}),
        parameters={"height_mm": 156, "radius_mm": 2}))

    spec.add(ComponentSpec("PROPELLER", JointType.REVOLUTE, joint_axis="Z", joint_limits=(0, 359),
        parent="HULL",
        vinculum=Vinculum("ship", {"propeller_diameter_draft_ratio": 0.4}),
        parameters={"diameter_mm": 6, "pitch_mm": 45, "max_rpm": 2500}))

    return spec


def generate_cargo_ship(model_id: str = "cargo_v1") -> AssemblySpec:
    """Generate a cargo ship with larger hull, twin propellers."""
    spec = AssemblySpec(
        model_id=model_id,
        domain="ship",
        global_vinculum=Vinculum("ship", {
            "hull_length_beam_ratio": 6.0,
            "draft_displacement_ratio": 0.15,
            "block_coefficient": 0.80,
        }),
        metadata={"material": "PETG", "tolerance_mm": 0.30},
    )

    spec.add(ComponentSpec("HULL", JointType.FIXED,
        parameters={"length_mm": 300, "beam_mm": 50, "draft_mm": 45}))

    spec.add(ComponentSpec("RUDDER", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-40, 40),
        parent="HULL"))

    spec.add(ComponentSpec("PROPELLER_PORT", JointType.REVOLUTE, joint_axis="Z", joint_limits=(0, 359),
        parent="HULL"))

    spec.add(ComponentSpec("PROPELLER_STARBOARD", JointType.REVOLUTE, joint_axis="Z", joint_limits=(0, 359),
        parent="HULL"))

    spec.add(ComponentSpec("CARGO_HATCH", JointType.SLIDER, joint_axis="Y", joint_limits=(0, 80),
        parent="HULL"))

    return spec
