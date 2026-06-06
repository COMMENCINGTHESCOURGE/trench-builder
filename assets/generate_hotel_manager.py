"""
HOTEL MANAGER BASE MESH — Faceless athletic humanoid in T-pose.
Infinite Hotel Franchise character generator for Blender 5.1.

Mesh strategy:
  - Proportioned primitives (no external assets required)
  - T-pose: arms horizontal, palms down, feet shoulder-width
  - Athletic mesomorph: broad shoulders, narrow waist, muscular thighs
  - Faceless: smooth head with no facial features
  - Smooth shading on all geometry

Material:
  - Principled BSDF: Base Color #C58B75, Roughness 0.7, Specular 0.2
  - Subsurface Scattering: Weight 0.15, Radius (1.0, 0.2, 0.1)
  - No clearcoat; matte clay-like finish

Run in Blender:
  blender --background --python generate_hotel_manager.py
Export:
  hotel_manager.glb
"""

import bpy
import math
import os
from pathlib import Path

# ── Clean scene ─────────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ── Materials ───────────────────────────────────────────────────
def make_clay_material(name="HotelManager_Clay"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.773, 0.545, 0.459, 1.0)  # ~#C58B75
    bsdf.inputs["Roughness"].default_value = 0.7
    bsdf.inputs["Specular IOR Level"].default_value = 0.2
    bsdf.inputs["Subsurface Weight"].default_value = 0.15
    # RGB radius for SSS — warm flesh scatter
    bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.2, 0.1)
    bsdf.inputs["Metallic"].default_value = 0.0
    return mat

clay = make_clay_material()

# ── Dimensions (approx human, meters) ──────────────────────────
HEIGHT = 1.82      # Total height
SHOULDER_W = 0.48  # Shoulder width (broad)
TORSO_W = 0.30     # Waist width (narrow)
TORSO_D = 0.22
TORSO_H = 0.55
LEG_W = 0.24
LEG_D = 0.18
LEG_H = 0.85
ARM_W = 0.10
ARM_D = 0.10
ARM_H = 0.70
HEAD_R = 0.11
NECK_R = 0.05
NECK_H = 0.08

# ── Helpers ─────────────────────────────────────────────────────
def add_limb(name, location, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    bpy.ops.object.transform_apply(scale=True)
    return obj

def add_sphere(name, location, radius, material):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, segments=20, ring_count=12)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

# ── Build body ─────────────────────────────────────────────────
def build_hotel_manager():
    hip_y = LEG_H
    shoulder_y = hip_y + TORSO_H
    neck_y = shoulder_y + NECK_H
    head_y = neck_y + HEAD_R + 0.02

    # --- Legs ---
    add_limb("Leg_L", (-LEG_W/2, 0, LEG_H/2), (LEG_W/2, LEG_D/2, LEG_H/2), clay)
    add_limb("Leg_R", ( LEG_W/2, 0, LEG_H/2), (LEG_W/2, LEG_D/2, LEG_H/2), clay)

    # --- Hips / Pelvis ---
    pelvis_h = 0.12
    pelvis_y = hip_y - pelvis_h/2
    add_limb("Pelvis", (0, 0, pelvis_y), (TORSO_W/2 + 0.02, TORSO_D/2, pelvis_h/2), clay)

    # --- Torso (tapered: shoulder wide, waist narrow) ---
    # Two segments: upper chest and lower waist
    chest_y = pelvis_y + pelvis_h/2 + (TORSO_H - pelvis_h)/2
    add_limb("Chest", (0, 0, chest_y), (SHOULDER_W/2, TORSO_D/2, (TORSO_H - pelvis_h)/2), clay)

    waist_y = pelvis_y + pelvis_h/2 + (TORSO_H - pelvis_h)*0.25
    add_limb("Waist", (0, 0, waist_y), (TORSO_W/2, TORSO_D/2, (TORSO_H - pelvis_h)*0.25), clay)

    # --- Arms (T-pose: horizontal from shoulders) ---
    arm_y = shoulder_y - ARM_H/2
    # Shoulder pivot at shoulder_y, arm extends sideways in X
    add_limb("Arm_L", (-SHOULDER_W/2 - ARM_H/2, 0, shoulder_y), (ARM_H/2, ARM_D/2, ARM_W/2), clay)
    add_limb("Arm_R", ( SHOULDER_W/2 + ARM_H/2, 0, shoulder_y), (ARM_H/2, ARM_D/2, ARM_W/2), clay)

    # Hands (simple spheres at arm ends)
    hand_x = SHOULDER_W/2 + ARM_H
    add_sphere("Hand_L", (-hand_x, 0, shoulder_y), ARM_W*0.7, clay)
    add_sphere("Hand_R", ( hand_x, 0, shoulder_y), ARM_W*0.7, clay)

    # --- Neck ---
    add_limb("Neck", (0, 0, neck_y), (NECK_R, NECK_R, NECK_H/2), clay)

    # --- Head (smooth sphere, no face) ---
    add_sphere("Head", (0, 0, head_y), HEAD_R, clay)

    # --- Feet ---
    foot_h = 0.08
    foot_y = foot_h/2
    foot_x = LEG_W/2
    foot_z = LEG_H + 0.02
    add_limb("Foot_L", (-foot_x, 0, foot_y), (LEG_W/3, LEG_D/2, foot_h/2), clay)
    add_limb("Foot_R", ( foot_x, 0, foot_y), (LEG_W/3, LEG_D/2, foot_h/2), clay)

# ── Smooth shading ──────────────────────────────────────────────
def smooth_all():
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            for poly in obj.data.polygons:
                poly.use_smooth = True

# ── Build ───────────────────────────────────────────────────────
print("Building hotel manager base mesh...")
build_hotel_manager()
smooth_all()

# ── Export ──────────────────────────────────────────────────────
out_dir = Path(os.environ.get("ASSET_OUTPUT_DIR", Path(__file__).parent))
out = out_dir / "hotel_manager.glb"
bpy.ops.export_scene.gltf(
    filepath=str(out),
    export_format='GLB',
    export_apply=True,
    export_image_format='NONE'
)
print(f"Exported: {out}")
print("Hotel manager base mesh complete.")
