"""
mecha_knee_to_glb.py — Convert SIMP tensor output to Blender mesh, export GLB.
Uses Blender 5.1 Python API. Run:
  "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --python mecha_knee_to_glb.py
"""
import json
import bpy
import bmesh
import math
from pathlib import Path

TENSOR_PATH = Path(__file__).parent.parent / "mecha_knee_tensor.json"
OUTPUT_PATH = Path(__file__).parent.parent / "mecha_knee.glb"

def load_tensor():
    with open(TENSOR_PATH) as f:
        data = json.load(f)
    meta = data["metadata"]
    nx, ny, nz = meta["grid_dimensions"]
    density = data["channels"]["density"]
    return nx, ny, nz, density

def build_mesh(nx, ny, nz, density):
    """Build a single mesh from voxels where density > threshold."""
    threshold = 0.3
    active = set()
    
    # Identify active voxels
    for iz in range(nz):
        for iy in range(ny):
            for ix in range(nx):
                if density[iz][iy][ix] > threshold:
                    active.add((ix, iy, iz))
    
    if not active:
        print("No active voxels found — threshold too high?")
        return None
    
    print(f"Active voxels: {len(active)} / {nx * ny * nz}")
    
    # Create mesh and bmesh
    mesh = bpy.data.meshes.new("mecha_knee_mesh")
    bm = bmesh.new()
    
    # Build one cube per active voxel
    vert_offset = 0
    scale = 0.5  # half-voxel for unit spacing
    
    for (ix, iy, iz) in active:
        cx, cy, cz = ix + 0.5, iy + 0.5, iz + 0.5
        # 8 corners
        verts = [
            bm.verts.new((cx - scale, cy - scale, cz - scale)),
            bm.verts.new((cx + scale, cy - scale, cz - scale)),
            bm.verts.new((cx + scale, cy + scale, cz - scale)),
            bm.verts.new((cx - scale, cy + scale, cz - scale)),
            bm.verts.new((cx - scale, cy - scale, cz + scale)),
            bm.verts.new((cx + scale, cy - scale, cz + scale)),
            bm.verts.new((cx + scale, cy + scale, cz + scale)),
            bm.verts.new((cx - scale, cy + scale, cz + scale)),
        ]
        bm.verts.ensure_lookup_table()
        v = verts
        # 6 faces
        faces = [(0,1,2,3), (4,7,6,5), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)]
        for f in faces:
            try:
                bm.faces.new([v[i] for i in f])
            except ValueError:
                pass  # duplicate face
    
    # Remove doubles
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    
    # Write to mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # Create object
    obj = bpy.data.objects.new("mecha_knee", mesh)
    bpy.context.collection.objects.link(obj)
    
    # Add material with vertex colors based on density
    mat = bpy.data.materials.new("mecha_material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.545, 0.361, 0.455, 1.0)  # purple-brown
        bsdf.inputs["Metallic"].default_value = 0.3
        bsdf.inputs["Roughness"].default_value = 0.6
    obj.data.materials.append(mat)
    
    return obj

def export_glb(obj, path):
    """Export the mesh as GLB."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format='GLB',
        use_selection=True,
        export_apply=True,
    )
    print(f"Exported: {path} ({path.stat().st_size / 1024:.1f} KB)")

# ═══ MAIN ═══
import sys
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

nx, ny, nz, density = load_tensor()
print(f"Grid: {nx}x{ny}x{nz}, {nx*ny*nz} voxels")
obj = build_mesh(nx, ny, nz, density)

if not obj:
    print("FAILED: no mesh produced.")
    sys.exit(1)

# Set as active object for modifier operations
bpy.context.view_layer.objects.active = obj

# Subdivision surface for organic look
mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
mod.levels = 2
mod.render_levels = 3

# Smooth shading
bpy.ops.object.shade_smooth()

# Apply the modifier before export
bpy.ops.object.modifier_apply(modifier=mod.name)

export_glb(obj, OUTPUT_PATH)
print("DONE.")
