import sys
from pathlib import Path
ASSET_OUTPUT_DIR = Path(r'C:\\Users\\dasha\\Projects\\trench_builder\\assets')

import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
# Mattress
bpy.ops.mesh.primitive_cube_add(scale=(1.0, 0.12, 0.6), location=(0, 0.06, 0))
# Headboard
bpy.ops.mesh.primitive_cube_add(scale=(0.03, 0.5, 0.6), location=(0.515, 0.31, 0))
bpy.ops.export_scene.gltf(filepath=str(ASSET_OUTPUT_DIR / "bed.glb"), export_draco=False, export_apply=True)
print(f"Exported: bed.glb")
