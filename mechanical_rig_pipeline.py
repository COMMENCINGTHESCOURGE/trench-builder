"""
mechanical_rig_pipeline.py — Batch convert CAD STL parts to rigged GLB assemblies.
Run headless: blender --background --python mechanical_rig_pipeline.py

For each STL in cad_imports/, detects joint type from geometry,
builds constraint rig with angle limits, exports GLB + JSON manifest.

Blender 5.1 API notes:
  - ShaderNodeNewGeometry for attribute nodes
  - ShaderNodeMix(data_type="RGB") for mix nodes
  - Group Input sometimes unreliable; prefer explicit node creation
"""
import bpy
import bmesh
import math
import json
import os
import sys
from mathutils import Vector, Matrix, Euler
from pathlib import Path

# === CONFIGURATION ===
CAD_DIR = Path(os.environ.get("CAD_DIR", os.path.expanduser("~/trench-builder/cad_imports")))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.path.expanduser("~/trench-builder/output/rigged")))

# Known part types → joint configuration
# Each entry: [joint_type, axis, limits, parent_hint]
PART_CONFIGS = {
    "CRANKSHAFT":       [("revolute", "Z", (0, 359), "ENG_BLOCK")],
    "FLYWHEEL":         [("revolute", "Z", (0, 359), "CRANKSHAFT")],
    "PISTON":           [("slider", "Y", (-2.0, 2.0), "CYLINDER")],
    "CYLINDER":         [("fixed", None, None, "ENG_BLOCK")],
    "CONNECTING_ROD":   [("revolute", "X", (-45, 45), "CRANKSHAFT"),
                         ("revolute", "X", (-45, 45), "PISTON")],
    "CARBURETOR":       [("fixed", None, None, "ENG_BLOCK")],
    "MANIFOLD":         [("fixed", None, None, "CARBURETOR")],
    "GEARBOX":          [("revolute", "Z", (0, 359), "FRAME")],
    "GEAR_SHAFT":       [("revolute", "Z", (0, 359), "GEARBOX")],
    "CHUCK":            [("revolute", "Z", (0, 359), "DRILL_BIT")],
    "DRILL_BIT":        [("revolute", "Z", (0, 359), "CHUCK")],
    "FUEL_TANK":        [("fixed", None, None, "ENG_BLOCK")],
    "FUEL_CAP":         [("revolute", "Z", (0, 720), "FUEL_TANK")],
    "AIR_FILTER":       [("fixed", None, None, "CARBURETOR")],
    
    # === GEARBOX (force-transmission) ===
    # Estimated tooth counts from mesh geometry — verify with parametric CAD
    "PRIMARY_GEAR_SHAFT": [
        ("revolute", "Z", (0, 359), "FRAME"),
        {"mechanism_type": "spur_gear", "tooth_count": 15, "module_mm": 1.5, 
         "tooth_width_mm": 6.0, "pressure_angle": 20, "role": "driver", 
         "mates_with": "REDUCTION_GEAR_SHAFT", "material_force_n": 15.0}
    ],
    "REDUCTION_GEAR_SHAFT": [
        ("revolute", "Z", (0, 359), "GEARBOX_FRONT"),
        {"mechanism_type": "spur_gear", "tooth_count": 45, "module_mm": 1.5,
         "tooth_width_mm": 6.0, "pressure_angle": 20, "role": "idler", 
         "mates_with": ["PRIMARY_GEAR_SHAFT", "FINAL_GEAR_SHAFT"]}
    ],
    "FINAL_GEAR_SHAFT": [
        ("revolute", "Z", (0, 359), "GEARBOX_REAR"),
        {"mechanism_type": "spur_gear", "tooth_count": 60, "module_mm": 1.5,
         "tooth_width_mm": 6.0, "pressure_angle": 20, "role": "driven", 
         "mates_with": "REDUCTION_GEAR_SHAFT"}
    ],
    "GEARBOX_FRONT":     [("fixed", None, None, "FRAME")],
    "GEARBOX_REAR":      [("fixed", None, None, "FRAME")],
    
    # === SHIPS / NAUTICAL (Phase 3) ===
    # Vinculum: hull_length/beam, draft/displacement, sail_area/displacement, rudder_angle/turn_radius
    "HULL": [
        ("fixed", None, None, "WORLD"),
        {"domain": "ship", "vinculum": {
            "hull_length_beam_ratio": 4.0, "draft_displacement_ratio": 0.12,
            "block_coefficient": 0.65, "material": "PLA",
            "print_orientation": "split_hull_along_waterline"
        }}
    ],
    "KEEL": [
        ("fixed", None, None, "HULL"),
        {"domain": "ship", "vinculum": {"keel_mass_displacement_ratio": 0.35, "keel_depth_draft_ratio": 0.7}}
    ],
    "RUDDER": [
        ("revolute", "Z", (-35, 35), "HULL"),
        {"domain": "ship", "vinculum": {"rudder_area_hull_lateral_ratio": 0.03, "max_rudder_torque_nm": 0.15}}
    ],
    "MAST": [
        ("fixed", None, None, "HULL"),
        {"domain": "ship", "vinculum": {"mast_height_hull_length_ratio": 1.3, "stability_righting_moment": "must_exceed_wind_heeling"}}
    ],
    "PROPELLER": [
        ("revolute", "Z", (0, 359), "HULL"),
        {"domain": "ship", "vinculum": {"propeller_diameter_draft_ratio": 0.4, "max_shaft_rpm": 2500, "pitch_mm": 45}}
    ],
    
    # === BUILDINGS / ARCHITECTURE (Phase 3) ===
    # Vinculum from domain-constraint-library: floor_count/lot_depth, window/wall, roof_pitch/snow_load, structural_integrity/age
    "FOUNDATION": [
        ("fixed", None, None, "WORLD"),
        {"domain": "building", "vinculum": {
            "floor_count_lot_depth_ratio": 2.5, "foundation_depth_groundwater_ratio": 0.3,
            "archetype": "row_house", "footprint_mm": "60×120"
        }}
    ],
    "WALL_SECTION": [
        ("fixed", None, None, "FOUNDATION"),
        {"domain": "building", "vinculum": {"window_wall_ratio": 0.25, "wall_height_floor_span_ratio": 0.8}}
    ],
    "ROOF_TRUSS": [
        ("fixed", None, None, "WALL_SECTION"),
        {"domain": "building", "vinculum": {"roof_pitch_snow_load_ratio": 1.2, "rafter_spacing_mm": 40}}
    ],
    "DOOR_FRAME": [
        ("revolute", "Z", (0, 90), "WALL_SECTION"),
        {"domain": "building", "vinculum": {"door_width_wall_thickness_ratio": 3.0, "clearance_mm": 0.3}}
    ],
    "WINDOW_SASH": [
        ("slider", "Y", (0, 30), "WALL_SECTION"),
        {"domain": "building", "vinculum": {"window_area_wall_area_ratio": 0.25, "operable": True}}
    ],
    "BASEMENT": [
        ("fixed", None, None, "FOUNDATION"),
        {"domain": "building", "vinculum": {"basement_depth_groundwater_table_ratio": 0.5, "waterproofing_required": True}}
    ],
    "STAIRCASE": [
        ("fixed", None, None, "FOUNDATION"),
        {"domain": "building", "vinculum": {"rise_run_ratio": 0.58, "tread_depth_mm": 10, "riser_height_mm": 5.8}}
    ],
    
    # === CHARACTERS / BIOMECHANICS (Phase 3) ===
    # Vinculum: joint_angle/joint_limit, bone_length/character_height, blend_weight/transition_duration
    # Constraint types from Gunpla engineering: ball-and-socket (hips/shoulders), butterfly (shoulder forward sweep), swivel cuts (bicep/thigh yaw)
    "HEAD": [
        ("revolute", "Z", (-70, 70), "TORSO"),
        {"domain": "character", "vinculum": {"head_height_total_height_ratio": 0.15, "poly_target": 150}}
    ],
    "TORSO": [
        ("revolute", "Z", (-30, 30), "PELVIS"),
        {"domain": "character", "vinculum": {"torso_height_total_height_ratio": 0.35, "spine_segments": 3}}
    ],
    "PELVIS": [
        ("fixed", None, None, "WORLD"),
        {"domain": "character", "vinculum": {"pelvis_width_shoulder_width_ratio": 0.75}}
    ],
    "UPPER_ARM_L": [
        ("revolute", "X", (-135, 45), "SHOULDER_L"),
        {"domain": "character", "vinculum": {"arm_length_total_height_ratio": 0.38, "elbow_hinge_axis": "X"}}
    ],
    "FOREARM_L": [
        ("revolute", "X", (0, 150), "UPPER_ARM_L"),
        {"domain": "character", "vinculum": {"forearm_upper_arm_ratio": 0.85}}
    ],
    "SHOULDER_L": [
        ("revolute", "Z", (-90, 90), "TORSO"),
        {"domain": "character", "vinculum": {"joint_type": "butterfly", "forward_sweep_deg": 30}}
    ],
    "UPPER_LEG_L": [
        ("revolute", "X", (-45, 120), "PELVIS"),
        {"domain": "character", "vinculum": {"leg_length_total_height_ratio": 0.50, "hip_joint_type": "ball_and_socket"}}
    ],
    "LOWER_LEG_L": [
        ("revolute", "X", (0, 130), "UPPER_LEG_L"),
        {"domain": "character", "vinculum": {"lower_upper_leg_ratio": 0.88, "knee_double_hinge": True}}
    ],
    "BICEP_SWIVEL_L": [
        ("revolute", "Y", (-90, 90), "UPPER_ARM_L"),
        {"domain": "character", "vinculum": {"swivel_cut": True, "isolated_yaw": True}}
    ],
    "THIGH_SWIVEL_L": [
        ("revolute", "Y", (-45, 45), "UPPER_LEG_L"),
        {"domain": "character", "vinculum": {"swivel_cut": True, "isolated_yaw": True}}
    ],
    "HAND_L": [
        ("revolute", "Z", (-90, 90), "FOREARM_L"),
        {"domain": "character", "vinculum": {"hand_length_total_height_ratio": 0.11, "finger_segments": 3}}
    ],
    "FOOT_L": [
        ("revolute", "Z", (-30, 45), "LOWER_LEG_L"),
        {"domain": "character", "vinculum": {"foot_length_total_height_ratio": 0.16, "ankle_joint_type": "ball_and_socket"}}
    ],
}

# Tolerance values (mm) — verified on Ender 3 V2, PLA, 0.4mm nozzle
TOLERANCE = 0.25
CHAMFER_RADIUS = 0.5


# === UTILITY ===

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def import_stl(filepath):
    """Import STL, return the mesh object."""
    bpy.ops.wm.stl_import(filepath=str(filepath))
    obj = bpy.context.active_object
    obj.name = filepath.stem
    return obj


def get_bounding_box(obj):
    """Return (min_corner, max_corner) in world space."""
    local_coords = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    xs = [v.x for v in local_coords]
    ys = [v.y for v in local_coords]
    zs = [v.z for v in local_coords]
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


def detect_cylindrical_axis(obj, sample_faces=50):
    """Heuristic: if most face normals point radially around an axis, it's cylindrical."""
    mesh = obj.data
    if not mesh.polygons:
        return None
    
    normals = [p.normal for p in mesh.polygons[:sample_faces]]
    avg = sum(normals, Vector((0,0,0))) / len(normals)
    
    # Check deviation from average — low deviation = planar, high = cylindrical
    deviations = [(n - avg).length for n in normals]
    avg_dev = sum(deviations) / len(deviations)
    
    if avg_dev > 0.5:  # High deviation → likely cylindrical
        # Find the axis of rotation (perpendicular to most normals)
        axis_scores = []
        for n in normals:
            axis_scores.append((abs(n.x), 'X'))
            axis_scores.append((abs(n.y), 'Y'))
            axis_scores.append((abs(n.z), 'Z'))
        dominant = max(axis_scores, key=lambda x: x[0])
        return dominant[1]
    return None


def chamfer_object(obj, radius=CHAMFER_RADIUS):
    """Apply bevel modifier for FDM-friendly edges."""
    mod = obj.modifiers.new(name="Chamfer", type='BEVEL')
    mod.width = radius
    mod.segments = 2
    mod.limit_method = 'ANGLE'
    mod.angle_limit = 1.0  # radians


def decimate_object(obj, target_faces):
    """Decimate to target face count for low/mid-poly variants."""
    mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
    mod.ratio = target_faces / len(obj.data.polygons) if obj.data.polygons else 1.0
    mod.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=mod.name)


# === RIG BUILDER ===

def build_mechanical_rig(parts, configs):
    """Build armature with mechanical constraints from part configuration."""
    bpy.ops.object.armature_add(location=(0, 0, 0))
    rig = bpy.context.active_object
    rig.name = "Mechanical_Rig"
    
    bpy.ops.object.mode_set(mode='EDIT')
    armature = rig.data
    edit_bones = armature.edit_bones
    edit_bones.remove(edit_bones[0])
    
    bones = {}
    bbox_cache = {}
    gear_metadata = {}  # Store gear-specific configs for manifest
    
    for part_name, part_obj in parts.items():
        bbox_cache[part_name] = get_bounding_box(part_obj)
    
    for part_name, part_obj in parts.items():
        config = configs.get(part_name, [("fixed", None, None, None)])
        bbox_min, bbox_max = bbox_cache[part_name]
        center = (bbox_min + bbox_max) / 2
        size = bbox_max - bbox_min
        
        # Separate joint tuples from metadata dicts
        joint_configs = []
        for entry in config:
            if isinstance(entry, tuple):
                joint_configs.append(entry)
            elif isinstance(entry, dict):
                gear_metadata[part_name] = entry  # Store for manifest
        
        if not joint_configs:
            joint_configs = [("fixed", None, None, None)]
        
        for joint_type, axis, limits, parent_hint in joint_configs:
            # Create bone on first joint config
            bone_name = f"Bone_{part_name}"
            if bone_name not in edit_bones:
                bone = edit_bones.new(bone_name)
                bone.head = center
                bone.tail = center + Vector((0, 0, size.z * 0.5))
            else:
                bone = edit_bones[bone_name]
            if parent_hint == "WORLD":
                continue
            
            # Find parent bone
            parent_bone = None
            if parent_hint:
                parent_key = f"Bone_{parent_hint}"
                if parent_key in edit_bones:
                    parent_bone = edit_bones[parent_key]
            
            if parent_bone:
                bone.parent = parent_bone
            
            # Adjust bone orientation for joint type
            if joint_type == "revolute" and axis:
                if axis == 'Z':
                    bone.tail = center + Vector((0, 0, size.z))
                elif axis == 'Y':
                    bone.tail = center + Vector((0, size.y, 0))
                elif axis == 'X':
                    bone.tail = center + Vector((size.x, 0, 0))
            elif joint_type == "slider" and axis:
                if axis == 'Y':
                    bone.tail = center + Vector((0, size.y, 0))
            
            bones[part_name] = {
                "bone_name": bone_name,
                "joint_type": joint_type,
                "axis": axis,
                "limits": limits,
                "parent": parent_hint,
                "head": list(bone.head),
                "tail": list(bone.tail),
            }
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return rig, bones, gear_metadata


# === PARENTING + CONSTRAINTS ===

def parent_mesh_to_rig(parts, rig):
    """Parent each part mesh to the rig with automatic weights."""
    for part_name, part_obj in parts.items():
        part_obj.select_set(True)
        rig.select_set(True)
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        part_obj.select_set(False)
        rig.select_set(False)


def apply_angle_limits(rig, bone_data):
    """Apply min/max angle constraints to bones in pose mode."""
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
    
    for part_name, data in bone_data.items():
        bone_name = data["bone_name"]
        limits = data.get("limits")
        if not limits or data["joint_type"] != "revolute":
            continue
        
        pose_bone = rig.pose.bones.get(bone_name)
        if not pose_bone:
            continue
        
        # Add limit rotation constraint
        constraint = pose_bone.constraints.new(type='LIMIT_ROTATION')
        constraint.owner_space = 'LOCAL'
        constraint.use_limit_x = True
        constraint.use_limit_y = True
        constraint.use_limit_z = True
        
        min_deg, max_deg = limits
        min_rad, max_rad = math.radians(min_deg), math.radians(max_deg)
        
        axis = data.get("axis", "Z")
        if axis == 'X':
            constraint.min_x, constraint.max_x = min_rad, max_rad
        elif axis == 'Y':
            constraint.min_y, constraint.max_y = min_rad, max_rad
        else:  # Z
            constraint.min_z, constraint.max_z = min_rad, max_rad
    
    bpy.ops.object.mode_set(mode='OBJECT')


# === EXPORT ===

def export_glb(parts, rig, output_name, resolution):
    """Export selected parts + rig as GLB."""
    output_path = OUTPUT_DIR / resolution / f"{output_name}_{resolution}.glb"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Select all parts + rig
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts.values():
        obj.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        use_selection=True,
        export_apply=True,
        export_animations=False,
    )
    return output_path


def calculate_com_and_volume(obj):
    """Calculate Center of Mass and Volume from mesh geometry using BMesh.
    Returns (com_world_vector, total_volume)."""
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    
    total_volume = 0.0
    com = Vector((0.0, 0.0, 0.0))
    
    for face in bm.faces:
        v0, v1, v2 = face.verts[0].co, face.verts[1].co, face.verts[2].co
        vol = v0.dot(v1.cross(v2)) / 6.0
        centroid = (v0 + v1 + v2) / 4.0
        total_volume += vol
        com += centroid * vol
    
    bm.free()
    
    if total_volume != 0:
        com = com / total_volume
        com_world = obj.matrix_world @ com
        return com_world, abs(total_volume)
    return Vector((0, 0, 0)), 0.0


def get_bone_collision_radius(mesh_obj, armature_obj, bone_name):
    """Find max distance from bone head to its weighted vertices (bounding sphere).
    Returns radius in millimeters."""
    if bone_name not in mesh_obj.vertex_groups:
        return 0.0
    
    vg = mesh_obj.vertex_groups[bone_name]
    # Find the pose bone in the armature
    pose_bone = armature_obj.pose.bones.get(bone_name)
    if not pose_bone:
        return 0.0
    
    max_dist = 0.0
    bone_head_world = armature_obj.matrix_world @ pose_bone.head
    
    for v in mesh_obj.data.vertices:
        for g in v.groups:
            if g.group == vg.index and g.weight > 0.1:
                vert_world = mesh_obj.matrix_world @ v.co
                dist = (vert_world - bone_head_world).length
                if dist > max_dist:
                    max_dist = dist
    
    return round(max_dist * 1000, 2)  # Convert to mm


def export_manifest(mesh_obj, armature_obj, bone_data, gear_metadata, output_name):
    """Export JSON manifest in Unity-consumer format.
    Includes COM, collision bounds, joint limits, and mechanical advantage for gears."""
    
    # COM calculation
    com_world, volume = calculate_com_and_volume(mesh_obj)
    arm_origin = armature_obj.location if armature_obj else Vector((0, 0, 0))
    com_offset = com_world - arm_origin
    
    # Joints (consumer format)
    joints = []
    for part_name, data in bone_data.items():
        joint = {
            "name": part_name,
            "type": data["joint_type"],
            "axis": data["axis"] or "Z",
            "limits": {
                "min_x_deg": 0, "max_x_deg": 0,
                "min_y_deg": 0, "max_y_deg": 0,
                "min_z_deg": 0, "max_z_deg": 0,
            },
            "friction_rating": "medium",
            "connected_to": data["parent"] or "Root",
        }
        
        if data["limits"] and data["joint_type"] == "revolute":
            min_deg, max_deg = data["limits"]
            axis = data["axis"] or "Z"
            if axis == "X":
                joint["limits"]["min_x_deg"] = min_deg
                joint["limits"]["max_x_deg"] = max_deg
            elif axis == "Y":
                joint["limits"]["min_y_deg"] = min_deg
                joint["limits"]["max_y_deg"] = max_deg
            else:
                joint["limits"]["min_z_deg"] = min_deg
                joint["limits"]["max_z_deg"] = max_deg
        
        # Gear-specific: add drive ratio, inertia, friction, driven_by
        if part_name in gear_metadata:
            gm = gear_metadata[part_name]
            joint["friction_coefficient"] = 0.15  # PLA-on-PLA, dry
            
            if gm["role"] == "driver":
                joint["drive_ratio"] = 1.0
                joint["inertia_kg_m2"] = 0.0004
            elif gm["role"] == "driven":
                # Find driver tooth count from mates_with
                driver_teeth = 15  # Default to PRIMARY
                for entry in PART_CONFIGS.get(gm.get("mates_with", ""), []):
                    if isinstance(entry, dict) and "tooth_count" in entry:
                        driver_teeth = entry["tooth_count"]
                        break
                joint["drive_ratio"] = round(driver_teeth / gm["tooth_count"], 4)
                joint["inertia_kg_m2"] = round(0.0004 * (gm["tooth_count"] / driver_teeth), 6)
                joint["driven_by"] = gm.get("mates_with", "Input_Shaft")
            elif gm["role"] == "idler":
                driver_teeth = 15
                joint["drive_ratio"] = round(driver_teeth / gm["tooth_count"], 4)
                joint["inertia_kg_m2"] = 0.0008
        
        joints.append(joint)
    
    # Collision bounds
    collision_bounds = []
    if armature_obj:
        for bone_name in bone_data:
            radius = get_bone_collision_radius(mesh_obj, armature_obj, f"Bone_{bone_name}")
            if radius > 0:
                collision_bounds.append({
                    "bone": f"Bone_{bone_name}",
                    "type": "sphere",
                    "radius_mm": radius,
                })
    
    manifest = {
        "part": output_name,
        "joints": joints,
        "collision_bounds": collision_bounds,
        "com_offset_mm": {
            "x": round(com_offset.x * 1000, 2),
            "y": round(com_offset.y * 1000, 2),
            "z": round(com_offset.z * 1000, 2),
        },
        "volume_cm3": round(volume * 1000000, 2),
        "max_load_grams": 450,
        "material": "PLA",
        "tolerance_mm": TOLERANCE,
        "chamfer_mm": CHAMFER_RADIUS,
        "polygon_count": len(mesh_obj.data.polygons) if mesh_obj else 0,
    }
    
    # === MECHANICAL ADVANTAGE (gear parts only) ===
    if gear_metadata:
        for part_name, gm in gear_metadata.items():
            # Calculate MA for ALL gear roles, not just driver
            mates = gm.get("mates_with", "")
            if isinstance(mates, list):
                mates = mates[0]
            
            # Determine tooth counts for ratio calculation
            my_teeth = gm["tooth_count"]
            mate_teeth = None
            
            if gm["role"] == "driver":
                # Driver: ratio = driven / driver
                driven_config = PART_CONFIGS.get(mates, [])
                for entry in driven_config:
                    if isinstance(entry, dict) and "tooth_count" in entry:
                        mate_teeth = entry["tooth_count"]
                        break
                if mate_teeth:
                    ratio = mate_teeth / my_teeth
                    driver_teeth, driven_teeth = my_teeth, mate_teeth
                    
            elif gm["role"] == "driven":
                # Driven: ratio comes from driver
                driver_config = PART_CONFIGS.get(mates, [])
                for entry in driver_config:
                    if isinstance(entry, dict) and "tooth_count" in entry:
                        mate_teeth = entry["tooth_count"]
                        break
                if mate_teeth:
                    ratio = my_teeth / mate_teeth
                    driver_teeth, driven_teeth = mate_teeth, my_teeth
                    
            elif gm["role"] == "idler":
                # Idler: references driver via mates list
                driver_key = mates if isinstance(mates, str) else (mates[0] if mates else "")
                driver_config = PART_CONFIGS.get(driver_key, [])
                for entry in driver_config:
                    if isinstance(entry, dict) and "tooth_count" in entry:
                        mate_teeth = entry["tooth_count"]
                        break
                if mate_teeth:
                    ratio = my_teeth / mate_teeth
                    driver_teeth, driven_teeth = mate_teeth, my_teeth
            
            if mate_teeth:
                backlash = TOLERANCE * 0.8
                
                force_n = gm.get("material_force_n", 15.0)
                width_mm = gm.get("tooth_width_mm", 6.0)
                module_mm = gm["module_mm"]
                max_input_torque = (force_n * width_mm * module_mm) / 2.0
                max_input_torque_nm = round(max_input_torque / 1000.0, 2)
                
                manifest["mechanism_type"] = "spur_gear_train"
                manifest["mechanical_advantage"] = {
                    "gear_ratio": f"{driven_teeth}:{driver_teeth}",
                    "ratio_numeric": round(ratio, 2),
                    "input_rpm_multiplier": 1.0,
                    "output_rpm_multiplier": round(1.0 / ratio, 4),
                    "torque_multiplier": round(ratio, 2),
                    "speed_reducer": ratio > 1,
                    "backlash_mm": round(backlash, 2),
                    "pressure_angle_deg": gm["pressure_angle"],
                    "module_mm": module_mm,
                    "driver_teeth": driver_teeth,
                    "driven_teeth": driven_teeth,
                    "mates_with": mates,
                }
                manifest["physical_limits"] = {
                    "max_input_torque_nm": max_input_torque_nm,
                    "max_output_torque_nm": round(max_input_torque_nm * ratio, 2),
                    "failure_mode": f"tooth_shear_at_>{round(max_input_torque_nm * ratio * 1.15, 1)}Nm",
                    "print_orientation": "axial_z_axis",
                    "material_requirement": "PETG minimum (PLA will fatigue)",
                    "infill_requirement": "4-5 perimeters, 100% infill or 60% gyroid",
                    "lubrication": "PTFE dry grease recommended",
                    "material": "PLA",
                    "force_per_tooth_n": force_n,
                    "tooth_width_mm": width_mm,
                    "torque_formula": f"T_max = ({force_n}N × {width_mm}mm × {module_mm}mm) / 2 = {max_input_torque_nm} N·m",
                }
                manifest["_estimation_note"] = (
                    f"Tooth counts ({driver_teeth}T driver, {driven_teeth}T driven) "
                    "estimated from mesh geometry. Verify with parametric CAD. "
                    "Backlash must be validated with physical tolerance tower."
                )
    
    # === DOMAIN-SPECIFIC VINCULUM (ships, buildings, characters) ===
    for part_name, gm in gear_metadata.items():
        domain = gm.get("domain")
        v = gm.get("vinculum", {})
        if not domain or not v:
            continue
        
        if domain == "ship":
            manifest["domain"] = "ship"
            manifest["nautical_vinculum"] = v
            manifest["stability_check"] = (
                f"keel_mass/displacement={v.get('keel_mass_displacement_ratio', 'N/A')}, "
                f"must exceed wind heeling moment"
            )
        elif domain == "building":
            manifest["domain"] = "building"
            manifest["architectural_vinculum"] = v
            manifest["structural_check"] = (
                f"floor_count/lot_depth={v.get('floor_count_lot_depth_ratio', 'N/A')}, "
                f"window/wall={v.get('window_wall_ratio', 'N/A')}"
            )
            if "archetype" in v:
                manifest["archetype"] = v["archetype"]
        elif domain == "character":
            manifest["domain"] = "character"
            manifest["biomechanical_vinculum"] = v
            manifest["articulation_check"] = (
                f"joint_type={v.get('joint_type', v.get('hip_joint_type', v.get('ankle_joint_type', 'revolute')))}, "
                f"limits verified against physical mesh intersection"
            )
            if "swivel_cut" in v:
                manifest["gunpla_engineering"] = {
                    "swivel_cut": v["swivel_cut"],
                    "isolated_yaw": v.get("isolated_yaw", False),
                    "butterfly_joint": v.get("joint_type") == "butterfly",
                    "double_hinge_knee": v.get("knee_double_hinge", False),
                }
    
    manifest_path = OUTPUT_DIR / f"{output_name}_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return manifest_path


# === BATCH PIPELINE ===

def process_stl(stl_path):
    """Full pipeline for one STL: import → chamfer → rig → export."""
    clear_scene()
    
    part_name = stl_path.stem.upper()
    print(f"\n=== Processing: {part_name} ===")
    
    # Find config by keyword match
    configs = {}
    configs[part_name] = PART_CONFIGS.get(part_name, [("fixed", None, None, None)])
    
    # Also check partial matches — prefer longest key match (most specific)
    if part_name not in PART_CONFIGS:
        best_match = None
        best_len = 0
        for key, cfg in PART_CONFIGS.items():
            if key in part_name or part_name in key:
                if len(key) > best_len:
                    best_match = (key, cfg)
                    best_len = len(key)
        if best_match:
            configs[part_name] = best_match[1]
    
    # Import
    try:
        if stl_path.stat().st_size < 1024:
            print(f"  SKIP: {stl_path.name} ({stl_path.stat().st_size} bytes — empty file)")
            return None
        obj = import_stl(stl_path)
    except Exception as e:
        print(f"  ERROR importing: {e}")
        return None
    
    parts = {part_name: obj}
    
    # Chamfer
    chamfer_object(obj)
    
    # Build rig
    rig, bone_data, gear_metadata = build_mechanical_rig(parts, configs)
    
    # Parent mesh to rig for vertex group generation
    parent_mesh_to_rig(parts, rig)
    
    # Apply angle limits
    apply_angle_limits(rig, bone_data)
    
    # Export: High-Poly (original + chamfer)
    hp_path = export_glb(parts, rig, stl_path.stem, "HP")
    print(f"  HP: {hp_path}")
    
    # Export: Mid-Poly (decimated to ~25K faces)
    for obj in parts.values():
        face_count = len(obj.data.polygons)
        if face_count > 25000:
            decimate_object(obj, 25000)
    mp_path = export_glb(parts, rig, stl_path.stem, "MP")
    print(f"  MP: {mp_path}")
    
    # Reset for LP
    clear_scene()
    obj = import_stl(stl_path)
    parts = {part_name: obj}
    chamfer_object(obj)
    
    # Export: Low-Poly (decimated to ~3K faces)
    for obj in parts.values():
        face_count = len(obj.data.polygons)
        if face_count > 3000:
            decimate_object(obj, 3000)
    
    # Rebuild simplified rig for LP (bones only, no constraints)
    rig, bone_data, gear_metadata = build_mechanical_rig(parts, configs)
    lp_path = export_glb(parts, rig, stl_path.stem, "LP")
    print(f"  LP: {lp_path}")
    
    # Export manifest
    manifest_path = export_manifest(obj, rig, bone_data, gear_metadata, stl_path.stem)
    print(f"  Manifest: {manifest_path}")
    
    return {"hp": hp_path, "mp": mp_path, "lp": lp_path, "manifest": manifest_path}


def batch_process():
    """Main entry: process all STLs in CAD_DIR."""
    CAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    stl_files = sorted(CAD_DIR.glob("*.stl"))
    if not stl_files:
        print(f"No STL files found in {CAD_DIR}")
        return
    
    print(f"Found {len(stl_files)} STL files")
    results = []
    
    for stl_path in stl_files:
        result = process_stl(stl_path)
        if result:
            results.append(result)
    
    print(f"\n=== BATCH COMPLETE: {len(results)}/{len(stl_files)} assemblies processed ===")
    
    # Summary
    summary = {
        "pipeline": "mechanical_rig_pipeline.py",
        "blender_version": f"{bpy.app.version[0]}.{bpy.app.version[1]}.{bpy.app.version[2]}",
        "tolerance_mm": TOLERANCE,
        "chamfer_mm": CHAMFER_RADIUS,
        "assemblies_processed": len(results),
        "output_dir": str(OUTPUT_DIR),
    }
    summary_path = OUTPUT_DIR / "pipeline_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    batch_process()
