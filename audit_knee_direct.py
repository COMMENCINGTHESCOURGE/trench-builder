#!/usr/bin/env python
"""
audit_knee_direct.py
====================
Runs the Codex Vinculum Topology Suite audit directly on the reconstructed 
quad mesh in Blender memory before GLB export. This avoids triangulation 
valence inflation.

Usage:
  blender --background --python audit_knee_direct.py
"""

import os
import sys
import bpy

def run_direct_audit():
    print("=== STARTING DIRECT VINCULUM QUAD MESH AUDIT ===")

    # 1. Clear default scene
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    # 2. Register addon
    addon_dir = os.path.dirname(os.path.abspath(__file__))
    addon_path = os.path.join(addon_dir, "codex_topology_suite.py")
    with open(addon_path, "r", encoding="utf-8") as f:
        exec(f.read(), globals())
    try:
        register()
    except ValueError:
        pass

    # 3. Import Voxel JSON
    props = bpy.context.scene.ets_props
    props.voxel_path = os.path.join(os.path.dirname(addon_dir), "mecha_knee_tensor.json")
    print(f"  Importing voxel JSON: {props.voxel_path}")
    if not os.path.exists(props.voxel_path):
        print(f"  [ERROR] JSON not found at: {props.voxel_path}")
        sys.exit(1)

    bpy.ops.ets.import_voxel_manifest()
    obj = bpy.context.view_layer.objects.active
    print(f"  Raw Voxel Mesh: {len(obj.data.vertices)} vertices, {len(obj.data.polygons)} faces")

    # 4. Clean to base (Welds duplicates and marks creases)
    props.crease_angle = 0.61  # ~35 degrees in radians
    props.bevel_weight = 1.0
    props.preserve_hard_edges = True
    props.preserve_creases = True
    props.rebuild_quad_topology = True
    props.rebuild_edge_flow = True
    props.rebuild_bevel_weights = True
    props.use_quadriflow = False
    
    bpy.ops.ets.cleanup_to_base()
    print(f"  Cleaned Quad Mesh: {len(obj.data.vertices)} vertices, {len(obj.data.polygons)} faces")



    # 5. Load and register codex_vinculum_addon
    vinculum_path = os.path.join(addon_dir, "codex_vinculum_addon.py")
    with open(vinculum_path, "r", encoding="utf-8") as f:
        exec(f.read(), globals())
    try:
        register()
    except ValueError:
        pass

    # 6. Execute direct topology analysis
    analysis = analyze_vinculum_topology(bpy.context, g1_threshold=30.0)

    g0_count = len(analysis["G0"])
    g1_count = len(analysis["G1"])
    g2_count = len(analysis["G2"])
    failed_count = len(analysis["FAILED"])

    print()
    print("========================================")
    print("      DIRECT VINCULUM AUDIT REPORT      ")
    print("========================================")
    print(f"  G0 Sharp Folds (Division):      {g0_count}")
    print(f"  G1 Smooth Creases (Grouping):   {g1_count}")
    print(f"  G2 Invisible Seams (Complement): {g2_count}")
    print(f"  FAILED Bindings (Faults):       {failed_count}")
    print("========================================")

    if failed_count > 0:
        print("  VERDICT: BREACH [FAILED]")
        print("  Reason: Non-manifold edges or vertex valence > 6 detected.")
        
        # Let's inspect a few failed edge indices to see why they failed
        print("  Failed Edge Diagnostics:")
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.edges.ensure_lookup_table()
        
        failed_reasons = []
        for idx in analysis["FAILED"][:10]:
            edge = bm.edges[idx]
            if not edge.is_manifold:
                failed_reasons.append(f"    Edge {idx}: Non-manifold (linked faces: {len(edge.link_faces)})")
            else:
                v1_val = len(edge.verts[0].link_edges)
                v2_val = len(edge.verts[1].link_edges)
                failed_reasons.append(f"    Edge {idx}: Valence breach (v1: {v1_val}, v2: {v2_val})")
        bm.free()
        for reason in failed_reasons:
            print(reason)
            
        sys.exit(1)
    else:
        print("  VERDICT: SYSTEM GREEN [PASSED]")
        print("  Reason: All edge binds and valences conform to vinculum limits.")
        sys.exit(0)

if __name__ == "__main__":
    run_direct_audit()
