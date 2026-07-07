import sys
from pathlib import Path
ASSET_OUTPUT_DIR = Path(r'C:\\Users\\dasha\\Projects\\trench_builder\\assets')

import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
# Top
bpy.ops.mesh.primitive_cube_add(scale=(0.6, 0.02, 0.4), location=(0, 0.7, 0))
# Legs
for x in (-0.55, 0.55):
    for z in (-0.35, 0.35):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.7, location=(x, 0.35, z))
bpy.ops.export_scene.gltf(filepath=str(ASSET_OUTPUT_DIR / "table.glb"), export_draco=False, export_apply=True)
print(f"Exported: table.glb")
