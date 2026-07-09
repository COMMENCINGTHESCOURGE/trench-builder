#!/usr/bin/env python
"""
verify_knee_mesh.py
===================
Blender automation script that runs headlessly to import the mecha knee voxel 
manifest, perform quad-based topology cleanup, crease beveling, and export 
the finished 3D bracket model as mecha_knee_rebuild.glb.

Usage:
  blender --background --python verify_knee_mesh.py
"""

import os
import sys
import json
import bpy

def run_rebuild():
    print("=== STARTING BLENDER VOXEL MESH RECONSTRUCTION ===")

    # 1. Register codex_topology_suite dynamically
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    addon_path = os.path.join(addon_dir, "codex_topology_suite.py")
    
    print(f"  Loading addon from: {addon_path}")
    if not os.path.exists(addon_path):
        print(f"  [ERROR] Addon not found at: {addon_path}")
        sys.exit(1)
        
    # Execute the addon script directly to register its classes
    with open(addon_path, "r", encoding="utf-8") as f:
        exec(f.read(), globals())

    # Call register() which registers properties and operators
    try:
        register()
    except ValueError as e:
        print(f"  Addon already registered: {e}")
    print("  Addon registered successfully.")

    # 2. Clear default scene objects (cubes, lights, cameras)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    print("  Cleaned default scene.")

    # 3. Configure import paths and properties
    props = bpy.context.scene.ets_props
    props.voxel_path = os.path.join(os.path.dirname(addon_dir), "mecha_knee_tensor.json")
    print(f"  Voxel manifest source path: {props.voxel_path}")

    # Set parameters for the cleanup
    props.crease_angle = 0.61  # ~35 degrees in radians
    props.bevel_weight = 1.0
    props.preserve_hard_edges = True
    props.preserve_creases = True
    props.rebuild_quad_topology = True
    props.rebuild_edge_flow = True
    props.rebuild_bevel_weights = True
    props.use_quadriflow = False  # Disabled by default as voxel checkerboards violate manifold constraints

    # 4. Import the voxel mesh
    print("  Running ets.import_voxel_manifest operator...")
    res = bpy.ops.ets.import_voxel_manifest()
    if res != {"FINISHED"}:
        print("  [ERROR] Voxel import operator failed.")
        sys.exit(1)

    # Make sure we have the active imported mesh object
    obj = bpy.context.view_layer.objects.active
    if not obj or obj.name != "Voxelized_SIMP_Mesh":
        print("  [ERROR] Failed to locate imported voxel mesh object.")
        sys.exit(1)
    print(f"  Imported mesh '{obj.name}' with {len(obj.data.vertices)} vertices, {len(obj.data.polygons)} faces.")

    # 5. Run cleanup and rebuild operators
    print("  Running ets.cleanup_to_base operator...")
    res = bpy.ops.ets.cleanup_to_base()
    if res != {"FINISHED"}:
        print("  [ERROR] Cleanup to base operator failed.")
        sys.exit(1)
        
    cleanup_result = json.loads(obj["ets_cleanup_result"])
    print(f"  Reconstructed mesh: {cleanup_result['vertices']} vertices, {cleanup_result['faces']} faces, {cleanup_result['crease_edges']} crease edges.")

    # 6. Export the mesh to GLB format
    output_glb_path = os.path.join(os.path.dirname(addon_dir), "mecha_knee_rebuild.glb")
    print(f"  Exporting rebuilt model to GLB: {output_glb_path}")
    
    # Select our object
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Export only selected object
    bpy.ops.export_scene.gltf(
        filepath=output_glb_path,
        export_format="GLB",
        use_selection=True,
        export_apply=True
    )
    print(f"  Export complete! GLB size: {os.path.getsize(output_glb_path)} bytes.")
    print("=== BLENDER VOXEL MESH RECONSTRUCTION DONE ===")


if __name__ == "__main__":
    run_rebuild()
