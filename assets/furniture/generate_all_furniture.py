# Generate procedural furniture GLBs for trench-builder interiors
# Run: blender --background --python generate_furniture.py

import bpy, sys, os
from pathlib import Path

output_dir = Path(os.environ.get("ASSET_OUTPUT_DIR", "."))

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def make_material(name, color=(0.7, 0.6, 0.4), roughness=0.5, metalness=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metalness
    return mat

# ── Chair ──
clear_scene()
mat = make_material("chair_mat", (0.55, 0.35, 0.15))

bpy.ops.mesh.primitive_cube_add(size=0.45, location=(0, 0, 0.45))
bpy.context.active_object.data.materials.append(mat)

for x in (-0.2, 0.2):
    for z in (-0.2, 0.2):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.45, location=(x, 0.225, z))
        bpy.context.active_object.data.materials.append(mat)

bpy.ops.mesh.primitive_cube_add(scale=(0.45, 0.03, 0.4), location=(0, -0.24, 0.65))
bpy.context.active_object.data.materials.append(mat)

bpy.ops.export_scene.gltf(filepath=str(output_dir / "chair.glb"), use_selection=False)
print(f"Exported: {output_dir / 'chair.glb'}")

# ── Table ──
clear_scene()
mat = make_material("table_mat", (0.6, 0.4, 0.2))

bpy.ops.mesh.primitive_cube_add(scale=(0.6, 0.02, 0.4), location=(0, 0.7, 0))
bpy.context.active_object.data.materials.append(mat)

for x in (-0.55, 0.55):
    for z in (-0.35, 0.35):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.7, location=(x, 0.35, z))
        bpy.context.active_object.data.materials.append(mat)

bpy.ops.export_scene.gltf(filepath=str(output_dir / "table.glb"), use_selection=False)
print(f"Exported: {output_dir / 'table.glb'}")

# ── Shelf ──
clear_scene()
mat = make_material("shelf_mat", (0.5, 0.3, 0.1))

bpy.ops.mesh.primitive_cube_add(scale=(0.6, 0.02, 0.5), location=(0, 0.51, 0))
bpy.context.active_object.data.materials.append(mat)

bpy.ops.mesh.primitive_cube_add(scale=(0.6, 0.01, 0.24), location=(0, 0.26, 0))
bpy.context.active_object.data.materials.append(mat)

for x in (-0.305, 0.305):
    bpy.ops.mesh.primitive_cube_add(scale=(0.01, 0.52, 0.5), location=(x, 0.51, 0))
    bpy.context.active_object.data.materials.append(mat)

bpy.ops.export_scene.gltf(filepath=str(output_dir / "shelf.glb"), use_selection=False)
print(f"Exported: {output_dir / 'shelf.glb'}")

# ── Bed ──
clear_scene()
mat_bed = make_material("bed_mat", (0.8, 0.75, 0.7))
mat_frame = make_material("bed_frame_mat", (0.3, 0.25, 0.2))

bpy.ops.mesh.primitive_cube_add(scale=(1.0, 0.12, 0.6), location=(0, 0.06, 0))
bpy.context.active_object.data.materials.append(mat_bed)

bpy.ops.mesh.primitive_cube_add(scale=(0.03, 0.5, 0.6), location=(0.515, 0.31, 0))
bpy.context.active_object.data.materials.append(mat_frame)

bpy.ops.export_scene.gltf(filepath=str(output_dir / "bed.glb"), use_selection=False)
print(f"Exported: {output_dir / 'bed.glb'}")

# ── Cabinet ──
clear_scene()
mat_cab = make_material("cabinet_mat", (0.6, 0.5, 0.35))
mat_handle = make_material("handle_mat", (0.8, 0.7, 0.5), metalness=0.6)

bpy.ops.mesh.primitive_cube_add(scale=(0.5, 0.55, 0.4), location=(0, 0.275, 0))
bpy.context.active_object.data.materials.append(mat_cab)

bpy.ops.mesh.primitive_cube_add(scale=(0.44, 0.01, 0.36), location=(0, 0.555, 0.02))
bpy.context.active_object.data.materials.append(mat_cab)

bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.08, location=(0.15, 0.56, 0.18))
bpy.context.active_object.data.materials.append(mat_handle)

bpy.ops.export_scene.gltf(filepath=str(output_dir / "cabinet.glb"), use_selection=False)
print(f"Exported: {output_dir / 'cabinet.glb'}")
