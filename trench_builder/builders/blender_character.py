"""
CONVEYOR BELT — Character Spec → Blender → GLB

Consumes a CharacterAssembly JSON file and generates a fully-rigged,
skin-lofted 3D character with embedded specs for reverse engineering.

Usage:
  blender --background --python builders/blender_character.py -- \
      --spec specs/kael_vos.json \
      --out exports/kael_vos.glb

Blender 5.1.1 compatible. No .add() on bpy_prop_collection.
"""

import bpy
import bmesh
import json
import sys
import math
import argparse
from pathlib import Path
from mathutils import Vector, Matrix


# ═══════════════════════════════════════════════════════
# Skeleton layout from ComponentSpec tree
# ═══════════════════════════════════════════════════════

# Maps component names to bone chain positions.
# Each character body follows: torso root → 4 limbs + head
BONE_LAYOUT = {
    "torso":      [(0, 0,  0.0), (0, 0,  1.8), 0.30, None],           # root
    "left_arm":   [(0, 0,  1.5), (-0.8, 0, 1.0), 0.18, "torso"],     # shoulder→forearm
    "right_arm":  [(0, 0,  1.5), ( 0.8, 0, 1.0), 0.18, "torso"],
    "left_leg":   [(0, 0,  0.0), (-0.3, 0,-1.5), 0.22, "torso"],     # hip→foot
    "right_leg":  [(0, 0,  0.0), ( 0.3, 0,-1.5), 0.22, "torso"],
    "head":       [(0, 0,  1.8), (0, 0,  2.4), 0.20, "torso"],
}

# For mecha/corrupted variants, add sub-bones for multi-segment limbs
LIMB_SEGMENTS = {
    "humanoid":  [1.0],                        # single bone
    "mecha":     [0.5, 0.5],                   # upper + forearm
    "organic":   [0.33, 0.33, 0.34],          # three segments
    "corrupted": [0.4, 0.3, 0.3],             # three asymmetric segments
    "reinforced": [0.45, 0.55],                # thick upper + forearm
}


def get_limb_type(components, limb_name):
    """Extract limb_type from component parameters."""
    for c in components:
        if c["name"] == limb_name:
            return c.get("parameters", {}).get("limb_type", "humanoid")
    return "humanoid"


def get_joint_limits(components, limb_name):
    """Extract joint limits from component spec."""
    for c in components:
        if c["name"] == limb_name:
            limits = c.get("joint_limits")
            if limits:
                return tuple(limits)
    return (-90, 90)


def build_skeleton(spec):
    """Convert ComponentSpec tree to bone chain definitions."""
    components = spec.get("components", [])
    bones = []

    # Torso is always root
    torso_scale = 1.0
    for c in components:
        if c["name"] == "torso":
            torso_scale = c.get("parameters", {}).get("scale", 1.0)

    tx, ty, tz = BONE_LAYOUT["torso"][0]
    thx, thy, thz = BONE_LAYOUT["torso"][1]
    torso_h = (thz - tz) * torso_scale

    bones.append(("torso_root", (tx, ty, tz), (tx, ty, tz + torso_h), 0.30 * torso_scale, None))

    # Head
    head_type = "standard"
    head_scale = 1.0
    for c in components:
        if c["name"] == "head":
            head_type = c.get("parameters", {}).get("head_type", "standard")
            head_scale = c.get("parameters", {}).get("scale", 1.0)

    head_y = tz + torso_h
    head_r = 0.20 * head_scale
    hx, hy, hz = BONE_LAYOUT["head"][0]
    hhx, hhy, hhz = BONE_LAYOUT["head"][1]
    bones.append(("head", (hx, hy, head_y), (hhx, hhy, head_y + (hhz - hz) * head_scale), head_r, "torso_root"))

    # Limbs
    for limb in ["left_arm", "right_arm", "left_leg", "right_leg"]:
        limb_type = get_limb_type(components, limb)
        segments = LIMB_SEGMENTS.get(limb_type, [1.0])
        joint_limits = get_joint_limits(components, limb)
        layout = BONE_LAYOUT.get(limb, BONE_LAYOUT["left_arm"])

        start = Vector(layout[0])
        end = Vector(layout[1])

        # Adjust start Y to match torso top (arms) or bottom (legs)
        if "arm" in limb:
            start.z = tz + torso_h * 0.85
        else:
            start.z = tz + 0.05

        direction = end - start
        length = direction.length * torso_scale
        direction.normalize()

        prev_name = "torso_root"
        cumulative = start.copy()
        for si, seg_frac in enumerate(segments):
            seg_len = length * seg_frac
            seg_end = cumulative + direction * seg_len
            name = f"{limb}_{si}" if len(segments) > 1 else limb
            radius = 0.14 * torso_scale if "leg" in limb else 0.10 * torso_scale
            if limb_type == "mecha":
                radius *= 1.2
            elif limb_type == "corrupted":
                radius *= 0.9

            bones.append((
                name,
                (cumulative.x, cumulative.y, cumulative.z),
                (seg_end.x, seg_end.y, seg_end.z),
                radius,
                prev_name,
            ))
            prev_name = name
            cumulative = seg_end

    return bones


# ═══════════════════════════════════════════════════════
# Scene helpers
# ═══════════════════════════════════════════════════════

def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.armatures, bpy.data.materials):
        for item in list(block):
            block.remove(item)


def create_skin_material(name, base_color, subsurface=0.3, roughness=0.4):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nd = mat.node_tree.nodes
    nd.clear()
    out = nd.new('ShaderNodeOutputMaterial')
    bsdf = nd.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (-300, 0)
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Subsurface Weight'].default_value = subsurface
    bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.4, 0.1)
    bsdf.inputs['Roughness'].default_value = roughness
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


# ═══════════════════════════════════════════════════════
# Variant material presets
# ═══════════════════════════════════════════════════════

VARIANT_MATERIALS = {
    "corrupted":   (0.35, 0.42, 0.45, 1.0),  # cold steel blue
    "stealth":     (0.15, 0.15, 0.18, 1.0),  # near-black
    "reinforced":  (0.55, 0.40, 0.20, 1.0),  # brass/gold
    "overcharge":  (0.70, 0.20, 0.60, 1.0),  # hot magenta
    "dual":        (0.50, 0.50, 0.50, 1.0),  # split grey
    "standard":    (0.80, 0.50, 0.40, 1.0),  # warm terracotta/clay
}


def get_variant_color(spec):
    variant = spec.get("sprite_params", {}).get("variant", "standard")
    return VARIANT_MATERIALS.get(variant, VARIANT_MATERIALS["standard"])


# ═══════════════════════════════════════════════════════
# Main build
# ═══════════════════════════════════════════════════════

def build_character(spec):
    """Build a full character from a CharacterAssembly dict."""
    character_name = spec.get("character_name", spec.get("model_id", "unknown"))
    print(f"\n{'='*60}")
    print(f"BUILDING: {character_name}")
    print(f"  Role: {spec.get('role', '')}")
    print(f"  Variant: {spec.get('sprite_params', {}).get('variant', 'standard')}")

    reset_scene()
    bones = build_skeleton(spec)

    # Build mesh from bone endpoints (skin modifier loft)
    verts_data = []
    edges = []
    vmap = {}
    bone_names = []

    for name, h, t, r, parent in bones:
        hi = vmap.setdefault(
            (round(h[0], 4), round(h[1], 4), round(h[2], 4)),
            len(verts_data)
        )
        if hi == len(verts_data):
            verts_data.append((Vector(h), r))

        ti = vmap.setdefault(
            (round(t[0], 4), round(t[1], 4), round(t[2], 4)),
            len(verts_data)
        )
        if ti == len(verts_data):
            verts_data.append((Vector(t), r * 0.85))

        edges.append((hi, ti))
        bone_names.append((name, hi, ti, parent))

    mesh = bpy.data.meshes.new(f"{character_name}_mesh")
    mesh.from_pydata([v[0] for v in verts_data], edges, [])
    mesh.update()

    obj = bpy.data.objects.new(character_name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Skin modifier
    obj.modifiers.new(name="SkinLoft", type='SKIN')
    subsurf = obj.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    # Initialize skin data
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    if len(mesh.skin_vertices) == 0:
        bpy.ops.mesh.customdata_skin_add()
    bpy.ops.object.mode_set(mode='OBJECT')

    mesh.update()
    skin_layer = mesh.skin_vertices[0]
    for i, (co, radius) in enumerate(verts_data):
        if i < len(skin_layer.data):
            skin_layer.data[i].radius = (radius, radius)

    # Mark root
    for name, hi, ti, parent in bone_names:
        if parent is None and hi < len(skin_layer.data):
            skin_layer.data[hi].use_root = True

    # Shading (Blender 5.x: use_auto_smooth removed, use modifier instead)
    bpy.ops.object.shade_smooth()
    obj.modifiers.new(name="WeightedNormals", type='WEIGHTED_NORMAL')

    # UV unwrap (may fail in headless — skip gracefully)
    try:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    except RuntimeError:
        pass  # Headless Blender sometimes can't run UV ops
    finally:
        bpy.ops.object.mode_set(mode='OBJECT')

    # Armature
    bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
    arm = bpy.context.active_object
    arm.name = f"{character_name}_rig"
    arm.data.name = f"{character_name}_armature"
    bpy.ops.armature.select_all(action='SELECT')
    bpy.ops.armature.delete()

    eb = arm.data.edit_bones
    for name, h, t, r, parent in bones:
        b = eb.new(name)
        b.head, b.tail = Vector(h), Vector(t)
        b.roll = 0
        if parent and parent in eb:
            b.parent = eb[parent]
    bpy.ops.object.mode_set(mode='OBJECT')

    # Parent mesh to armature
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    # Material
    color = get_variant_color(spec)
    mat = create_skin_material(f"{character_name}_mat", color,
                               subsurface=0.3, roughness=0.4)
    obj.data.materials.append(mat)

    # EMBED SPEC FOR REVERSE ENGINEERING
    obj["trench_builder_spec"] = json.dumps(spec)
    obj["trench_builder_version"] = "1.0"
    obj["domain"] = "character"

    print(f"  Bones: {len(bones)}")
    print(f"  Vertices: {len(verts_data)}")
    print(f"  Material: {color}")
    print(f"  Spec embedded: {len(obj['trench_builder_spec'])} bytes")

    return obj, arm


# ═══════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════

def export_glb(spec, output_path):
    """Build and export to GLB."""
    obj, arm = build_character(spec)

    # Select everything for export
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    arm.select_set(True)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.export_scene.gltf(
        filepath=output_path,
        use_selection=True,
        export_format='GLB',
        export_apply=True,
        export_animations=False,
    )

    size_mb = Path(output_path).stat().st_size / (1024 * 1024)
    print(f"\n  EXPORTED: {output_path} ({size_mb:.2f} MB)")
    return output_path


# ═══════════════════════════════════════════════════════
# Batch mode — process all specs in a directory
# ═══════════════════════════════════════════════════════

def batch_process(specs_dir, output_dir):
    specs_dir = Path(specs_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for spec_file in sorted(specs_dir.glob("*.json")):
        with open(spec_file) as f:
            spec = json.load(f)
        name = spec.get("character_name", spec.get("model_id", spec_file.stem))
        out_path = output_dir / f"{name.lower().replace(' ', '_')}.glb"
        try:
            path = export_glb(spec, str(out_path))
            results.append((name, path, True))
        except Exception as e:
            print(f"  FAILED: {name} — {e}")
            results.append((name, str(out_path), False))

    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE: {len([r for r in results if r[2]])}/{len(results)} exported")
    for name, path, ok in results:
        status = "OK" if ok else "FAIL"
        print(f"  {status}: {name} -> {path}")
    return results


# ═══════════════════════════════════════════════════════
# CLI entry point
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    # Handle Blender's argument passing (-- separates Blender args from script args)
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Character Spec → GLB conveyor belt")
    parser.add_argument("--spec", help="Single character JSON spec file")
    parser.add_argument("--out", help="Output GLB path (required with --spec)")
    parser.add_argument("--batch", help="Process all JSON specs in directory")
    parser.add_argument("--outdir", default="exports", help="Output directory for batch mode")

    args = parser.parse_args(argv)

    if args.spec and args.out:
        with open(args.spec) as f:
            spec = json.load(f)
        export_glb(spec, args.out)

    elif args.batch:
        batch_process(args.batch, args.outdir)

    else:
        print("Usage:")
        print("  Single:  blender --background --python blender_character.py -- --spec char.json --out char.glb")
        print("  Batch:   blender --background --python blender_character.py -- --batch specs/ --outdir exports/")
        sys.exit(1)
