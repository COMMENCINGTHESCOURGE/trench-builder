"""
PIPELINE TO GLB — Universal template
Feed any SIMP tensor or D_mat spec → Blender mesh → GLB
Usage: blender --background --python pipeline_to_glb.py -- --config part_config.json
"""
import bpy, bmesh, json, sys, argparse
from pathlib import Path

def load_config(path):
    with open(path) as f:
        return json.load(f)

def build_from_tensor(cfg):
    """SIMP voxel tensor → merged mesh (mecha parts)."""
    with open(cfg["tensor_path"]) as f:
        data = json.load(f)
    meta = data["metadata"]
    nx, ny, nz = meta["grid_dimensions"]
    density = data["channels"]["density"]
    
    threshold = cfg.get("density_threshold", 0.3)
    active = set()
    for iz in range(nz):
        for iy in range(ny):
            for ix in range(nx):
                if density[iz][iy][ix] > threshold:
                    active.add((ix, iy, iz))
    
    print(f"  Active voxels: {len(active)} / {nx*ny*nz}")
    
    mesh = bpy.data.meshes.new(cfg["name"])
    bm = bmesh.new()
    scale = 0.5
    for (ix, iy, iz) in active:
        cx, cy, cz = ix + 0.5, iy + 0.5, iz + 0.5
        verts = [bm.verts.new((cx + dx*scale, cy + dy*scale, cz + dz*scale))
                 for dx in (-1,1) for dy in (-1,1) for dz in (-1,1)]
        bm.verts.ensure_lookup_table()
        faces = [(0,1,3,2),(4,5,7,6),(0,4,6,2),(1,5,7,3),(2,6,7,3),(0,4,5,1)]
        for f in faces:
            try: bm.faces.new([verts[i] for i in f])
            except: pass
    
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bm.to_mesh(mesh)
    bm.free()
    return bpy.data.objects.new(cfg["name"], mesh)

def apply_modifiers(obj, cfg):
    """Apply the configured modifier stack."""
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    
    for mod_cfg in cfg.get("modifiers", []):
        mod_type = mod_cfg["type"]
        mod = obj.modifiers.new(name=mod_type, type=mod_type)
        for k, v in mod_cfg.get("params", {}).items():
            if hasattr(mod, k):
                setattr(mod, k, v)
        if mod_cfg.get("apply", True):
            bpy.ops.object.modifier_apply(modifier=mod.name)
        print(f"  Applied: {mod_type}")

def apply_material(obj, cfg):
    """Create material and assign to mesh."""
    mat_cfg = cfg.get("material", {})
    mat = bpy.data.materials.new(cfg["name"] + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        color = mat_cfg.get("color", [0.5, 0.3, 0.5, 1.0])
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = mat_cfg.get("metallic", 0.5)
        bsdf.inputs["Roughness"].default_value = mat_cfg.get("roughness", 0.5)
    
    # Sprite texture if specified
    tex_path = mat_cfg.get("texture")
    if tex_path and Path(tex_path).exists():
        tex_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex_node.image = bpy.data.images.load(str(Path(tex_path).resolve()))
        mat.node_tree.links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
        print(f"  Texture applied: {tex_path}")
    
    obj.data.materials.append(mat)

def export_glb(obj, path):
    """Export selected object as GLB."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=str(path), export_format='GLB',
        use_selection=True, export_apply=True)
    print(f"  Exported: {path} ({Path(path).stat().st_size/1024:.0f} KB)")

# ═══ MAIN ═══
if __name__ == "__main__":
    # Parse --config from sys.argv (Blender eats its own args)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args(argv)
    
    cfg = load_config(args.config)
    print(f"PIPELINE → GLB: {cfg['name']}")
    print(f"  Config: {args.config}")
    
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    obj = build_from_tensor(cfg)
    apply_modifiers(obj, cfg)
    apply_material(obj, cfg)
    export_glb(obj, cfg["output"])
    
    print(f"DONE: {cfg['output']}")
