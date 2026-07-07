#!/usr/bin/env python
"""
audit_building_vinculum.py
==========================
Blender script to audit procedurally generated building meshes (Geometry Nodes).
Ensures that:
  - Node Degree / Vertex Valence <= 6 (Mycelial limits)
  - Mesh edges conform to G0, G1, or G2 Vinculum states
  - Prunes over-valent connections to preserve manifold integrity.
"""
import bpy
import bmesh
import math
import sys

def run_building_audit():
    print("=== STARTING PROCEDURAL BUILDING TOPOLOGY AUDIT ===")
    
    # 1. Locate active mesh
    obj = bpy.context.active_object
    if not obj or obj.type != 'MESH':
        print("  [ERROR] No active mesh object selected.")
        return False
        
    print(f"  Target mesh located: '{obj.name}' ({len(obj.data.vertices)} vertices)")

    # 2. Open Bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    # 3. Check for Over-Valency (Node Degree > 6)
    over_valency_verts = [v for v in bm.verts if len(v.link_edges) > 6]
    print(f"  Total Over-valent Vertices Found: {len(over_valency_verts)}")
    
    # 4. Prune Over-Valent connections (Weld / Prune Operator)
    pruned_count = 0
    for v in over_valency_verts:
        # Sort linked edges by length and prune the weakest (shortest) link
        linked_edges = sorted(v.link_edges, key=lambda e: e.calc_length())
        while len(v.link_edges) > 6:
            edge_to_remove = linked_edges.pop(0)
            bm.edges.remove(edge_to_remove)
            pruned_count += 1

    if pruned_count > 0:
        print(f"  [REPAIR] Pruned {pruned_count} over-valent edge connections.")
        
    # 5. Classify remaining edges (G0, G1, G2)
    g0_count = 0
    g1_count = 0
    g2_count = 0
    failed_count = 0
    
    g1_threshold_rad = math.radians(30.0) # G0 fold cutoff
    
    bm.edges.ensure_lookup_table()
    for edge in bm.edges:
        if not edge.is_manifold:
            failed_count += 1
            continue
            
        try:
            angle = edge.calc_face_angle()
        except ValueError:
            failed_count += 1
            continue
            
        if angle > g1_threshold_rad:
            g0_count += 1
        elif angle > 0.001:
            g1_count += 1
        else:
            g2_count += 1

    print("\n========================================")
    print("      VINCULUM BUILDING AUDIT REPORT    ")
    print("========================================")
    print(f"  G0 Sharp Folds (Division):       {g0_count}")
    print(f"  G1 Smooth Creases (Grouping):    {g1_count}")
    print(f"  G2 Invisible Seams (Complement): {g2_count}")
    print(f"  FAILED Bindings (Non-manifold):  {failed_count}")
    print("========================================")

    # 6. Save modifications back to mesh
    bm.to_mesh(obj.data)
    bm.free()
    
    if failed_count > 0:
        print("  VERDICT: BREACH [FAILED] - Non-manifold topology remains.")
        return False
    else:
        print("  VERDICT: SYSTEM GREEN [PASSED] - Mesh conforms to Vinculum bounds.")
        return True

if __name__ == "__main__":
    run_building_audit()
