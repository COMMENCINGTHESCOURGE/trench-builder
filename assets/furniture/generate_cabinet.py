import sys
from pathlib import Path
ASSET_OUTPUT_DIR = Path(r'C:\\Users\\dasha\\Projects\\trench_builder\\assets')

import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
# Body
bpy.ops.mesh.primitive_cube_add(scale=(0.5, 0.55, 0.4), location=(0, 0.275, 0))
# Door (front panel)
bpy.ops.mesh.primitive_cube_add(scale=(0.44, 0.01, 0.36), location=(0, 0.555, 0.02))
# Handle
bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.08, location=(0.15, 0.56, 0.18), rotation=(0, 0, 0))
bpy.ops.export_scene.gltf(filepath=str(ASSET_OUTPUT_DIR / "cabinet.glb"), export_draco=False, export_apply=True)
print(f"Exported: cabinet.glb")
