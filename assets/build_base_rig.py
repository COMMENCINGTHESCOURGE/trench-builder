import bpy
import math
from pathlib import Path

# ==========================================
# 1. TECHNICAL STANDARDS
# ==========================================
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0

if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# ==========================================
# 2. CLEAN + BUILD BODY (same as generate_hotel_manager.py)
# ==========================================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Clay material (terracotta + SSS)
def make_clay_material(name="HotelManager_Clay"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.773, 0.545, 0.459, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7
    bsdf.inputs["Specular IOR Level"].default_value = 0.2
    bsdf.inputs["Subsurface Weight"].default_value = 0.15
    bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.2, 0.1)
    bsdf.inputs["Metallic"].default_value = 0.0
    return mat

clay = make_clay_material()

# Dimensions
HEIGHT = 1.82
SHOULDER_W = 0.48
TORSO_W = 0.30
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

hip_y = LEG_H
shoulder_y = hip_y + TORSO_H
neck_y = shoulder_y + NECK_H
head_y = neck_y + HEAD_R + 0.02

add_limb("Leg_L", (-LEG_W/2, 0, LEG_H/2), (LEG_W/2, LEG_D/2, LEG_H/2), clay)
add_limb("Leg_R", ( LEG_W/2, 0, LEG_H/2), (LEG_W/2, LEG_D/2, LEG_H/2), clay)

pelvis_h = 0.12
pelvis_y = hip_y - pelvis_h/2
add_limb("Pelvis", (0, 0, pelvis_y), (TORSO_W/2 + 0.02, TORSO_D/2, pelvis_h/2), clay)

chest_y = pelvis_y + pelvis_h/2 + (TORSO_H - pelvis_h)/2
add_limb("Chest", (0, 0, chest_y), (SHOULDER_W/2, TORSO_D/2, (TORSO_H - pelvis_h)/2), clay)

waist_y = pelvis_y + pelvis_h/2 + (TORSO_H - pelvis_h)*0.25
add_limb("Waist", (0, 0, waist_y), (TORSO_W/2, TORSO_D/2, (TORSO_H - pelvis_h)*0.25), clay)

arm_y = shoulder_y - ARM_H/2
add_limb("Arm_L", (-SHOULDER_W/2 - ARM_H/2, 0, shoulder_y), (ARM_H/2, ARM_D/2, ARM_W/2), clay)
add_limb("Arm_R", ( SHOULDER_W/2 + ARM_H/2, 0, shoulder_y), (ARM_H/2, ARM_D/2, ARM_W/2), clay)

hand_x = SHOULDER_W/2 + ARM_H
add_sphere("Hand_L", (-hand_x, 0, shoulder_y), ARM_W*0.7, clay)
add_sphere("Hand_R", ( hand_x, 0, shoulder_y), ARM_W*0.7, clay)

add_limb("Neck", (0, 0, neck_y), (NECK_R, NECK_R, NECK_H/2), clay)
add_sphere("Head", (0, 0, head_y), HEAD_R, clay)

foot_h = 0.08
foot_x = LEG_W/2
foot_z = LEG_H + 0.02
add_limb("Foot_L", (-foot_x, 0, foot_h/2), (LEG_W/3, LEG_D/2, foot_h/2), clay)
add_limb("Foot_R", ( foot_x, 0, foot_h/2), (LEG_W/3, LEG_D/2, foot_h/2), clay)

# Smooth shading
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth = True

# Join all body parts into one mesh
body_parts = [obj.name for obj in bpy.context.scene.objects if obj.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')
for name in body_parts:
    bpy.data.objects[name].select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects[body_parts[0]]
bpy.ops.object.join()
joined = bpy.context.active_object
joined.name = "BaseMesh_Flesh"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# ==========================================
# 3. METARIG + BINDING
# ==========================================
# Ensure we are in Object Mode
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Add human metarig (built-in)
bpy.ops.object.armature_basic_human_metarig_add()
rig = bpy.context.active_object
rig.name = "Avatar_Armature_GOVERNOR"

# Origin at feet
bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
rig.location = (0, 0, 0)

# Enforce metric scale
rig.scale = (1.0, 1.0, 1.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Bind mesh to armature with automatic weights
bpy.ops.object.select_all(action='DESELECT')
joined.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig

bpy.ops.object.parent_set(type='ARMATURE_AUTO')

print(f"[Chronos] Mesh '{joined.name}' bound to '{rig.name}' successfully.")

# ==========================================
# 4. EXPORT PIPELINE (.GLTF)
# ==========================================
out_dir = Path(r"C:\Users\dasha\Projects\trench_builder\assets")
out_path = out_dir / "Avatar_BaseMesh_V1.gltf"

bpy.ops.export_scene.gltf(
    filepath=str(out_path),
    export_format='GLTF_SEPARATE',
    use_selection=True,
    export_yup=True,
    export_texcoords=True,
    export_normals=True,
    export_tangents=True,
    export_materials='EXPORT',
    export_skins=True,
    export_animations=False,
)

print(f"[Flux-Chamber] Rigged base exported to: {out_path}")
