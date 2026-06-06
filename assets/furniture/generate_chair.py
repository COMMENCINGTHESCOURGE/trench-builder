import sys
from pathlib import Path
ASSET_OUTPUT_DIR = Path(r'C:\\Users\\dasha\\Projects\\trench_builder\\assets')

import bpy, math
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
# Seat
bpy.ops.mesh.primitive_cube_add(size=0.45, location=(0, 0, 0.45))
seat = bpy.context.active_object
seat.name = "Seat"
# Legs
for x in (-0.2, 0.2):
    for z in (-0.2, 0.2):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.45, location=(x, 0.225, z))
# Back
bpy.ops.mesh.primitive_cube_add(scale=(0.45, 0.03, 0.4), location=(0, -0.24, 0.65))
# Export
bpy.ops.export_scene.gltf(filepath=str(ASSET_OUTPUT_DIR / "chair.glb"), export_draco=False, export_apply=True)
print(f"Exported: chair.glb")
