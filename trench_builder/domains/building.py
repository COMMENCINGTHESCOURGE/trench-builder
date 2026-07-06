"""Trench-Builder: Building Domain — Architectural Archetypes."""
from ..core import AssemblySpec, ComponentSpec, Vinculum, JointType


ARCHETYPES = ["bungalow", "row_house", "apartment", "commercial", "school", "hospital", "warehouse", "pagoda"]


def generate_building(model_id: str = "building_v1", archetype: str = "row_house") -> AssemblySpec:
    """Generate a constraint-validated building from architectural vinculum ratios.
    
    Archetypes from domain-constraint-library:
      bungalow (6×8m), row_house (5×12m), apartment (15×30m),
      commercial (6×15m), school (20×40m), hospital (25×40m),
      warehouse (15×25m), pagoda (8×20m)
    """
    if archetype not in ARCHETYPES:
        raise ValueError(f"Unknown archetype: {archetype}. Choose from {ARCHETYPES}")

    spec = AssemblySpec(
        model_id=model_id,
        domain="building",
        global_vinculum=Vinculum("building", {
            "window_wall_ratio": 0.25,
            "roof_pitch_snow_load_ratio": 1.2,
            "stair_rise_run_ratio": 0.58,
            "basement_depth_groundwater_ratio": 0.5,
        }),
        metadata={"archetype": archetype, "material": "PLA", "tolerance_mm": 0.30},
    )

    # Foundation → Walls → Roof load path
    spec.add(ComponentSpec("FOUNDATION", JointType.FIXED, parent=None,
        vinculum=Vinculum("building", {"floor_count_lot_depth_ratio": 2.5}),
        parameters={"footprint_mm": "60×120", "depth_mm": 5}))

    spec.add(ComponentSpec("WALL_FRONT", JointType.FIXED, parent="FOUNDATION",
        vinculum=Vinculum("building", {"window_wall_ratio": 0.25})))

    spec.add(ComponentSpec("WALL_REAR", JointType.FIXED, parent="FOUNDATION"))

    spec.add(ComponentSpec("WALL_LEFT", JointType.FIXED, parent="FOUNDATION"))

    spec.add(ComponentSpec("WALL_RIGHT", JointType.FIXED, parent="FOUNDATION"))

    spec.add(ComponentSpec("ROOF_TRUSS", JointType.FIXED, parent="WALL_FRONT",
        vinculum=Vinculum("building", {"roof_pitch_snow_load_ratio": 1.2}),
        parameters={"rafter_spacing_mm": 40}))

    # Operable elements
    spec.add(ComponentSpec("DOOR_FRONT", JointType.REVOLUTE, joint_axis="Z", joint_limits=(0, 90),
        parent="WALL_FRONT",
        vinculum=Vinculum("building", {"door_width_wall_thickness_ratio": 3.0}),
        parameters={"clearance_mm": 0.3}))

    spec.add(ComponentSpec("WINDOW_LEFT", JointType.SLIDER, joint_axis="Y", joint_limits=(0, 30),
        parent="WALL_LEFT",
        vinculum=Vinculum("building", {"window_area_wall_area_ratio": 0.25, "operable": True})))

    spec.add(ComponentSpec("WINDOW_RIGHT", JointType.SLIDER, joint_axis="Y", joint_limits=(0, 30),
        parent="WALL_RIGHT"))

    # Basement + staircase
    spec.add(ComponentSpec("BASEMENT", JointType.FIXED, parent="FOUNDATION",
        vinculum=Vinculum("building", {"basement_depth_groundwater_table_ratio": 0.5}),
        parameters={"waterproofing": True}))

    spec.add(ComponentSpec("STAIRCASE", JointType.FIXED, parent="FOUNDATION",
        vinculum=Vinculum("building", {"rise_run_ratio": 0.58}),
        parameters={"tread_depth_mm": 10, "riser_height_mm": 5.8}))

    spec.metadata["component_count"] = len(spec.components)
    return spec
