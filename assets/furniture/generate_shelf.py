import sys
from pathlib import Path
ASSET_OUTPUT_DIR = Path(r'C:\\Users\\dasha\\Projects\\trench_builder\\assets')

import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
# Back
bpy.ops.mesh.primitive_cube_add(scale=(0.6, 0.02, 0.5), location=(0, 0.51, 0))
# Shelf
bpy.ops.mesh.primitive_cube_add(scale=(0.6, 0.01, 0.24), location=(0, 0.26, 0))
# Sides
bpy.ops.mesh.primitive_cube_add(scale=(0.01, 0.52, 0.5), location=(-0.305, 0.51, 0))
bpy.ops.mesh.primitive_cube_add(scale=(0.01, 0.52, 0.5), location=(0.305, 0.51, 0))
bpy.ops.export_scene.gltf(filepath=str(ASSET_OUTPUT_DIR / "shelf.glb"), export_draco=False, export_apply=True)
print(f"Exported: shelf.glb")
