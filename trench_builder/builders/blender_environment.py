"""
CONVEYOR BELT — Environment Spec → Blender → GLB

Generates trees (trunk + canopy), rocks (displaced icosphere),
and bushes (clustered spheres) from EnvironmentAssembly JSON specs.

Usage:
  blender --background --python builders/blender_environment.py -- --spec specs/tree_pine.json --out exports/tree_pine.glb
  blender --background --python builders/blender_environment.py -- --batch specs/ --outdir exports/
"""

import bpy
import bmesh
import json
import sys
import math
import random
import argparse
from pathlib import Path
from mathutils import Vector


def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials):
        for item in list(block):
            block.remove(item)


def make_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nd = mat.node_tree.nodes
    nd.clear()
    out = nd.new('ShaderNodeOutputMaterial')
    bsdf = nd.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (-200, 0)
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.75
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


# ═══════════════════════════════════════════════════════
# Tree builder — trunk cylinder + canopy cone/sphere
# ═══════════════════════════════════════════════════════

def build_tree(spec):
    components = spec.get("components", [])
    trunk_params = {}
    canopy_params = {}
    for c in components:
        if c["component_type"] == "trunk":
            trunk_params = c.get("parameters", {})
        elif c["component_type"] == "foliage":
            canopy_params = c.get("parameters", {})

    trunk_h = trunk_params.get("height", 2.0)
    trunk_r = trunk_params.get("radius", 0.25)
    trunk_color = trunk_params.get("color", (0.3, 0.2, 0.1, 1.0))
    canopy_r = canopy_params.get("radius", 1.5)
    canopy_h = canopy_params.get("height", 1.5)
    canopy_color = canopy_params.get("color", (0.1, 0.4, 0.1, 1.0))
    shape = canopy_params.get("shape", "sphere")

    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=trunk_r, depth=trunk_h, location=(0, 0, trunk_h/2))
    trunk = bpy.context.active_object
    trunk.name = "trunk"
    bpy.ops.object.shade_smooth()

    # Canopy
    if shape == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=canopy_r, radius2=0.0, depth=canopy_h,
                                         location=(0, 0, trunk_h + canopy_h/2))
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=canopy_r,
                                              location=(0, 0, trunk_h + canopy_h * 0.7))
        bpy.context.active_object.scale = (1.0, 1.0, canopy_h / canopy_r)

    canopy = bpy.context.active_object
    canopy.name = "canopy"
    bpy.ops.object.shade_smooth()

    # Parent canopy to trunk
    canopy.parent = trunk

    # Materials
    trunk_mat = make_material("trunk_mat", trunk_color)
    canopy_mat = make_material("canopy_mat", canopy_color)
    trunk.data.materials.append(trunk_mat)
    canopy.data.materials.append(canopy_mat)

    # EMBED SPEC
    trunk["trench_builder_spec"] = json.dumps(spec)
    trunk["trench_builder_version"] = "1.0"

    return trunk


# ═══════════════════════════════════════════════════════
# Rock builder — displaced icosphere
# ═══════════════════════════════════════════════════════

def build_rock(spec):
    params = spec["components"][0].get("parameters", {})
    size = params.get("size", 1.5)
    subdivisions = params.get("subdivisions", 3)
    displacement = params.get("displacement", 0.3)
    color = params.get("color", (0.3, 0.3, 0.3, 1.0))
    shape = params.get("shape", "boulder")

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=size, location=(0, 0, 0))
    rock = bpy.context.active_object
    rock.name = "rock"

    # Displacement modifier for organic shape
    disp = rock.modifiers.new(name="RockDisplace", type='DISPLACE')
    disp.strength = displacement
    tex = bpy.data.textures.new(name="RockNoise", type='CLOUDS')
    disp.texture = tex

    # Shape-specific tweaks
    if shape == "crystal":
        rock.scale = (1.0, 2.0, 1.0)  # Tall
    elif shape == "slab":
        rock.scale = (2.0, 0.6, 1.0)  # Flat
    elif shape == "cluster":
        # Add 2-3 smaller child rocks
        for i in range(3):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=size * 0.4,
                                                   location=(random.uniform(-0.5, 0.5) * size,
                                                            random.uniform(-0.3, 0.3) * size,
                                                            random.uniform(-0.5, 0.5) * size))
            child = bpy.context.active_object
            child.parent = rock
            child_mat = make_material(f"rock_cluster_mat_{i}", color)
            child.data.materials.append(child_mat)

    # Decimate for low-poly look
    dec = rock.modifiers.new(name="Decimate", type='DECIMATE')
    dec.ratio = 0.4 if shape == "crystal" else 0.6

    bpy.ops.object.shade_smooth()

    mat = make_material("rock_mat", color)
    rock.data.materials.append(mat)

    rock["trench_builder_spec"] = json.dumps(spec)
    rock["trench_builder_version"] = "1.0"

    return rock


# ═══════════════════════════════════════════════════════
# Bush builder — clustered spheres
# ═══════════════════════════════════════════════════════

def build_bush(spec):
    params = spec["components"][0].get("parameters", {})
    size = params.get("size", 1.0)
    cluster_count = params.get("cluster_count", 5)
    color = params.get("color", (0.1, 0.4, 0.1, 1.0))
    shape = params.get("shape", "round")

    # Center sphere
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=size * 0.5, location=(0, 0, size * 0.3))
    bush = bpy.context.active_object
    bush.name = "bush_center"

    # Cluster children
    for i in range(cluster_count):
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(0.3, 0.7) * size
        x = math.cos(angle) * dist
        y = random.uniform(-0.1, 0.3) * size
        z = math.sin(angle) * dist
        child_r = random.uniform(0.2, 0.4) * size

        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=child_r, location=(x, y, z))
        child = bpy.context.active_object
        child.parent = bush

        child_mat = make_material(f"bush_mat_{i}", (
            color[0] + random.uniform(-0.05, 0.05),
            color[1] + random.uniform(-0.08, 0.08),
            color[2] + random.uniform(-0.05, 0.05),
            1.0,
        ))
        child.data.materials.append(child_mat)

    # If spiky, add angular protrusions
    if shape == "spiky":
        for i in range(cluster_count):
            angle = random.uniform(0, math.pi * 2)
            phi = random.uniform(0.3, 0.9) * math.pi
            dist = size * 0.8
            x = math.cos(angle) * math.sin(phi) * dist
            y = math.cos(phi) * dist
            z = math.sin(angle) * math.sin(phi) * dist
            bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=0.05, radius2=0.0, depth=size*0.4,
                                             location=(x, y, z))
            spike = bpy.context.active_object
            spike.parent = bush

    bpy.ops.object.shade_smooth()

    mat = make_material("bush_mat", color)
    bush.data.materials.append(mat)

    bush["trench_builder_spec"] = json.dumps(spec)
    bush["trench_builder_version"] = "1.0"

    return bush


# ═══════════════════════════════════════════════════════
# Dispatch + export
# ═══════════════════════════════════════════════════════

BUILDERS = {
    "tree": build_tree,
    "rock": build_rock,
    "bush": build_bush,
    "plant": build_bush,  # same geometry as bush for now
}


def build_and_export(spec, output_path):
    reset_scene()
    asset_type = spec.get("asset_type", "tree")
    builder = BUILDERS.get(asset_type, build_tree)

    obj = builder(spec)

    # Select everything for export
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    for child in obj.children_recursive:
        child.select_set(True)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=output_path, use_selection=True,
        export_format='GLB', export_apply=True,
    )

    size_kb = Path(output_path).stat().st_size / 1024
    name = spec.get("model_id", "unknown")
    print(f"  EXPORTED: {name} -> {output_path} ({size_kb:.0f} KB)")
    return output_path


def batch_process(specs_dir, output_dir):
    specs_dir = Path(specs_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for spec_file in sorted(specs_dir.glob("*.json")):
        with open(spec_file) as f:
            spec = json.load(f)
        name = spec.get("model_id", spec_file.stem)
        out_path = output_dir / f"{name}.glb"
        try:
            build_and_export(spec, str(out_path))
            results.append((name, str(out_path), True))
        except Exception as e:
            print(f"  FAILED: {name} — {e}")
            results.append((name, str(out_path), False))

    print(f"\nBATCH COMPLETE: {len([r for r in results if r[2]])}/{len(results)} exported")
    for name, path, ok in results:
        status = "OK" if ok else "FAIL"
        print(f"  {status}: {name} -> {path}")


if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser()
    parser.add_argument("--spec")
    parser.add_argument("--out")
    parser.add_argument("--batch")
    parser.add_argument("--outdir", default="exports")
    args = parser.parse_args(argv)

    if args.spec and args.out:
        with open(args.spec) as f:
            spec = json.load(f)
        build_and_export(spec, args.out)
    elif args.batch:
        batch_process(args.batch, args.outdir)
    else:
        print("Usage: blender --background --python blender_environment.py -- --batch specs/ --outdir exports/")
        sys.exit(1)
