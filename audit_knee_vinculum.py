#!/usr/bin/env python
"""
audit_knee_vinculum.py
======================
Headless Blender script to run the Codex Vinculum Topology Suite audit against 
the rebuilt mecha knee GLB model. Checks for:
  - Non-manifold edge breaches (Failed bindings)
  - Mycelial node degree / vertex valence > 6 (Over-valency faults)
  - Edge classifications (G0, G1, G2)

Exits 0 if no failed bindings are found, and 1 otherwise.

Usage:
  blender --background --python audit_knee_vinculum.py
"""

import os
import sys
import bpy

def run_audit():
    print("=== STARTING VINCULUM TOPOLOGY AUDIT ===")

    # 1. Clear default scene
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    # 2. Import generated GLB
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    glb_path = os.path.join(workspace_dir, "mecha_knee_rebuild.glb")
    print(f"  Importing GLB model: {glb_path}")
    if not os.path.exists(glb_path):
        print(f"  [ERROR] GLB model not found at: {glb_path}")
        sys.exit(1)

    bpy.ops.import_scene.gltf(filepath=glb_path)

    # 3. Locate active imported mesh
    imported_objects = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    if not imported_objects:
        print("  [ERROR] No mesh objects were imported.")
        sys.exit(1)
        
    obj = imported_objects[0]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    print(f"  Target mesh located: '{obj.name}' ({len(obj.data.vertices)} vertices)")

    # Re-weld split vertices from GLB export before topological audit
    print("  Welding split vertices (Remove Doubles)...")
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"  Post-welding mesh: {len(obj.data.vertices)} vertices")

    # 4. Load and register codex_vinculum_addon
    addon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "codex_vinculum_addon.py")
    print(f"  Loading Vinculum Addon from: {addon_path}")
    if not os.path.exists(addon_path):
        print(f"  [ERROR] Vinculum addon not found at: {addon_path}")
        sys.exit(1)

    with open(addon_path, "r", encoding="utf-8") as f:
        exec(f.read(), globals())

    try:
        register()
    except ValueError as e:
        # Already registered is fine
        pass

    # 5. Execute analysis
    # g1_threshold is set to 30.0 degrees (G0/G1 cutoff)
    analysis = analyze_vinculum_topology(bpy.context, g1_threshold=30.0)

    # 6. Report results
    g0_count = len(analysis["G0"])
    g1_count = len(analysis["G1"])
    g2_count = len(analysis["G2"])
    failed_count = len(analysis["FAILED"])

    print()
    print("========================================")
    print("      VINCULUM AUDIT REPORT             ")
    print("========================================")
    print(f"  G0 Sharp Folds (Division):      {g0_count}")
    print(f"  G1 Smooth Creases (Grouping):   {g1_count}")
    print(f"  G2 Invisible Seams (Complement): {g2_count}")
    print(f"  FAILED Bindings (Faults):       {failed_count}")
    print("========================================")

    if failed_count > 0:
        print("  VERDICT: BREACH [FAILED]")
        print("  Reason: Non-manifold edges or vertex valence > 6 detected.")
        sys.exit(1)
    else:
        print("  VERDICT: SYSTEM GREEN [PASSED]")
        print("  Reason: All edge binds and valences conform to vinculum limits.")
        sys.exit(0)

if __name__ == "__main__":
    run_audit()
