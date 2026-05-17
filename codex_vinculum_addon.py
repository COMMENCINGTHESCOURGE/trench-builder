#!/usr/bin/env python
"""
CODEX VINCULUM TOPOLOGY SUITE — Blender Add-on
═══════════════════════════════════════════════════════
Implements the vinculum theory as a 3D topology analyzer.
Every mesh edge is a vinculum. Every fold angle is a mode.

MODE MAPPING:
  G0 (Sharp Fold)     → DIVISION vinculum    → Champagne Gold accent
  G1 (Smooth Crease)  → GROUPING vinculum    → moderate bevel weight
  G2 (Invisible Seam) → COMPLEMENT vinculum  → no visual mark
  FAILED              → Non-manifold or high-valence → correction needed

MYCELIAL NODE DEGREE:
  vert_valence > 6 = too many hyphae at one junction = topology risk

Codex Session: May 16, 2026
"""
import bpy
import bmesh
import math
from bpy.types import Operator, Panel
from bpy.props import FloatProperty

# -------------------------------------------------------------------
# THE CORE CODEX VINCULUM ENGINE (BMESH TOPOLOGY ANALYSIS)
# -------------------------------------------------------------------

def analyze_vinculum_topology(context, g1_threshold):
    """
    Analyzes mesh edges based on dihedral fold angles and valence,
    assigning them to the corresponding Vinculum Continuity Mode.
    """
    obj = context.active_object
    if not obj or obj.type != 'MESH':
        return {"G0": [], "G1": [], "G2": [], "FAILED": []}

    # Ensure we are working with up-to-date mesh data
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)

    bm.edges.ensure_lookup_table()
    
    modes = {"G0": [], "G1": [], "G2": [], "FAILED": []}
    rad_threshold = math.radians(g1_threshold)

    for edge in bm.edges:
        # Non-manifold or boundary edges = FAILED BINDING
        if not edge.is_manifold:
            modes["FAILED"].append(edge.index)
            continue
        
        # Check Mycelial Node Degree (Valence) at the edge vertices
        # Over-valency poses a severe topology risk (unbound vinculum)
        if len(edge.verts[0].link_edges) > 6 or len(edge.verts[1].link_edges) > 6:
            modes["FAILED"].append(edge.index)
            continue

        # Calculate the Dihedral Fold Angle (The Vinculum)
        try:
            angle = edge.calc_face_angle()
        except ValueError:
            # Fallback if face normals are deeply corrupted
            modes["FAILED"].append(edge.index)
            continue

        if angle > rad_threshold:
            # G0: SHARP FOLD -> DIVISION vinculum
            modes["G0"].append(edge.index)
        elif angle > 0.001:
            # G1: SMOOTH CREASE -> GROUPING vinculum
            modes["G1"].append(edge.index)
        else:
            # G2: INVISIBLE SEAM -> COMPLEMENT vinculum
            modes["G2"].append(edge.index)

    if obj.mode != 'EDIT':
        bm.free()

    return modes

# -------------------------------------------------------------------
# OPERATOR: APPLY GOLD CHAMPAGNE ACCENTS & CORRECTIONS
# -------------------------------------------------------------------

class MESH_OT_codex_vinculum_bind(Operator):
    """Codex Topology Drone Execution: Mark Creases and Isolate Faults"""
    bl_idname = "mesh.codex_vinculum_bind"
    bl_label = "Execute Vinculum Bind"
    bl_options = {'REGISTER', 'UNDO'}

    g1_threshold: FloatProperty(
        name="G0/G1 Threshold (Degrees)",
        description="Angle above which an edge becomes a G0 Sharp Fold",
        default=30.0,
        min=0.0,
        max=180.0
    )

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object must be a mesh.")
            return {'CANCELLED'}

        # Toggle to edit mode to manipulate bmesh safely
        original_mode = obj.mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        bm = bmesh.from_edit_mesh(obj.data)
        
        # Request data layers for edge weights (Champagne Gold Accents)
        bevel_layer = bm.edges.layers.bevel_weight.verify()
        crease_layer = bm.edges.layers.crease.verify()

        # Run Drone Analysis
        analysis = analyze_vinculum_topology(context, self.g1_threshold)

        # Clear previous selection to highlight operations
        for edge in bm.edges:
            edge.select = False

        # Apply Physical Creasing based on Vinculum Mode
        # G0 (Sharp Folds) receive the sharpest physical definitions
        for idx in analysis["G0"]:
            edge = bm.edges[idx]
            edge[bevel_layer] = 1.0  # Champagne Gold Edge Accent
            edge[crease_layer] = 1.0

        # G1 (Smooth Creases) receive a moderated binding structural weight
        for idx in analysis["G1"]:
            edge = bm.edges[idx]
            edge[bevel_layer] = 0.5
            edge[crease_layer] = 0.3

        # Select Failed Bindings automatically for user/drone intervention
        for idx in analysis["FAILED"]:
            bm.edges[idx].select = True

        # Refresh viewport overlay updates
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode=original_mode)

        summary = f"G0: {len(analysis['G0'])} | G1: {len(analysis['G1'])} | G2: {len(analysis['G2'])} | FAILED: {len(analysis['FAILED'])}"
        self.report({'INFO'}, f"Codex Bind Complete -> {summary}")
        return {'FINISHED'}

# -------------------------------------------------------------------
# INTERFACE: THE TOPOLOGY DRONE PANEL
# -------------------------------------------------------------------

class VIEW3D_PT_codex_topology_suite(Panel):
    """The Drone Command Console for viewing the Vinculum Overlay Matrix"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Codex'
    bl_label = "Vinculum Topology Suite"

    def draw(self, layout):
        layout.label(text="Codex Session: May 16, 2026", icon='COLOR')
        
        col = layout.column(align=True)
        col.label(text="Vinculum Mode Guide:")
        col.row().label(text="G0: Sharp Fold (Division)", icon='DOT')
        col.row().label(text="G1: Smooth Crease (Grouping)", icon='DOT')
        col.row().label(text="G2: Invisible Seam (Complement)", icon='DOT')
        col.row().label(text="Non-Manifold / High Valence (Fault)", icon='ERROR')
        
        layout.separator()
        
        # Trigger Operator Button
        layout.operator("mesh.codex_vinculum_bind", text="Run Drone Alignment", icon='AUTOMATIC')

# -------------------------------------------------------------------
# REGISTRATION SYSTEM
# -------------------------------------------------------------------

classes = (
    MESH_OT_codex_vinculum_bind,
    VIEW3D_PT_codex_topology_suite,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
