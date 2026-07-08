"""
Trench-Builder: Typography Builder — Spec → Blender → GLB
Consumes Typography spec JSON files and generates extruded 3D text/decals 
with procedural PBR material node networks (Voronoi cast iron pitting, brushed swirls).

Usage:
  blender --background --python builders/blender_typography.py -- \
      --spec specs/conveyor_badge.json \
      --out exports/conveyor_badge.glb
"""

import bpy
import bmesh
import json
import sys
import math
import argparse
from pathlib import Path
from mathutils import Vector


def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves):
        for item in list(block):
            block.remove(item)


def create_pitted_cast_iron_material(name, color_val, layers_spec):
    """Creates a Principled PBR material with Voronoi-driven surface pitting."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Create Core Shader Nodes
    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

    # Base attributes
    bsdf.inputs["Base Color"].default_value = (color_val["r"], color_val["g"], color_val["b"], 1.0)
    bsdf.inputs["Metallic"].default_value = 0.85

    # Procedural Pitting (Voronoi Noise)
    tex_coord = nodes.new("ShaderNodeTextureCoordinate")
    voronoi = nodes.new("ShaderNodeTexVoronoi")
    voronoi.inputs["Scale"].default_value = 150.0  # Dense micro-pitting

    val_to_bump = nodes.new("ShaderNodeBump")
    val_to_bump.inputs["Strength"].default_value = 0.3
    val_to_bump.inputs["Distance"].default_value = 0.05

    links.new(tex_coord.outputs["Generated"], voronoi.inputs["Vector"])
    links.new(voronoi.outputs["Distance"], val_to_bump.inputs["Height"])
    links.new(val_to_bump.outputs["Normal"], bsdf.inputs["Normal"])

    # Roughness modulation (Patch v compliance: roughness channel)
    math_node = nodes.new("ShaderNodeMath")
    math_node.operation = 'MULTIPLY'
    math_node.inputs[1].default_value = 0.6  # Scaled roughness range
    links.new(voronoi.outputs["Distance"], math_node.inputs[0])
    links.new(math_node.outputs["Value"], bsdf.inputs["Roughness"])

    return mat


def create_brushed_chrome_material(name, color_val, layers_spec):
    """Creates an anisotropic brushed metal material with directional swirls."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

    # Base attributes
    bsdf.inputs["Base Color"].default_value = (color_val["r"], color_val["g"], color_val["b"], 1.0)
    bsdf.inputs["Metallic"].default_value = 0.95
    bsdf.inputs["Roughness"].default_value = 0.25

    # Brushed texture coordinate stretching
    tex_coord = nodes.new("ShaderNodeTextureCoordinate")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (100.0, 1.0, 1.0)  # Stretched in X for brushed look

    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 5.0
    noise.inputs["Detail"].default_value = 8.0

    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.15
    bump.inputs["Distance"].default_value = 0.02

    links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    return mat


def create_neon_backlit_material(name, color_val, layers_spec):
    """Creates a backlit emission shader for neon effects."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (200, 0)
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

    # Frosted acrylic base
    bsdf.inputs["Base Color"].default_value = (0.95, 0.95, 0.97, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.4

    # Neon tube emission inside
    bsdf.inputs["Emission Color"].default_value = (color_val["r"], color_val["g"], color_val["b"], 1.0)
    bsdf.inputs["Emission Strength"].default_value = 8.0

    return mat


def create_constant_material(name, color_val):
    """Creates a basic matte/solid PBR material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (color_val["r"], color_val["g"], color_val["b"], 1.0)
    bsdf.inputs["Metallic"].default_value = 0.2
    bsdf.inputs["Roughness"].default_value = 0.5
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

    return mat


def apply_procedural_material(obj, material_spec):
    """Parses material layer specifications and binds procedural node shaders."""
    if not material_spec:
        return
    
    mat_name = material_spec.get("name", "material_spec")
    layers = material_spec.get("layers", [])
    
    # Extract color
    color_val = {"r": 0.5, "g": 0.5, "b": 0.5}
    for layer in layers:
        if layer.get("channel") == "albedo" and isinstance(layer.get("value"), dict):
            color_val = layer["value"]
            break

    # Identify material preset type based on numerator/denominator
    frac_str = material_spec.get("fractype", "")
    if "Cast Iron" in frac_str:
        mat = create_pitted_cast_iron_material(mat_name, color_val, layers)
    elif "Chrome" in frac_str or "Aluminum" in frac_str:
        mat = create_brushed_chrome_material(mat_name, color_val, layers)
    elif "Neon" in frac_str:
        # Check for emission color
        for layer in layers:
            if layer.get("channel") == "emission" and isinstance(layer.get("value"), dict):
                color_val = layer["value"].get("color", color_val)
                # Map array [r,g,b] to dict if needed
                if isinstance(color_val, list) and len(color_val) >= 3:
                    color_val = {"r": color_val[0], "g": color_val[1], "b": color_val[2]}
        mat = create_neon_backlit_material(mat_name, color_val, layers)
    else:
        mat = create_constant_material(mat_name, color_val)
        
    obj.data.materials.append(mat)


def build_typography(spec_path, output_path):
    print(f"Loading Typography spec: {spec_path}")
    with open(spec_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)

    reset_scene()

    components = spec.get("components", [])
    substrate_comp = None
    glyph_comps = []
    
    for c in components:
        if c["name"] == "substrate":
            substrate_comp = c
        elif c["name"].startswith("glyph_"):
            glyph_comps.append(c)

    # 1. Build Substrate Plate
    if substrate_comp:
        params = substrate_comp.get("parameters", {})
        w = params.get("width", 8.0)
        h = params.get("height", 1.5)
        d = params.get("depth", 0.1)
        
        # Create substrate bevel box via BMesh
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -d/2))
        sub_obj = bpy.context.active_object
        sub_obj.name = "substrate"
        sub_obj.scale = (w, h, d)
        bpy.ops.object.transform_apply(scale=True)
        
        # Bind material
        apply_procedural_material(sub_obj, params.get("material"))
    else:
        # Fallback root
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        sub_obj = bpy.context.active_object
        sub_obj.name = "substrate"

    # 2. Build Glyphs
    for comp in glyph_comps:
        params = comp.get("parameters", {})
        char = params.get("character", "")
        if not char:
            continue
            
        offset_x = params.get("offset_x", 0.0)
        extrude_val = params.get("extrusion_depth", 0.15)
        bevel_val = params.get("bevel_depth", 0.02)
        
        print(f"Generating 3D Glyph: '{char}' at X={offset_x:.2f}")
        
        # Create text curve
        bpy.ops.object.text_add(location=(offset_x, 0, 0))
        text_obj = bpy.context.active_object
        text_obj.name = comp["name"]
        
        # Configure geometry
        text_obj.data.body = char
        text_obj.data.extrude = extrude_val
        text_obj.data.bevel_depth = bevel_val
        text_obj.data.align_x = 'CENTER'
        text_obj.data.align_y = 'CENTER'
        
        # Convert to mesh to apply materials and export cleanly
        bpy.ops.object.convert(target='MESH')
        
        # Parent to substrate
        text_obj.parent = sub_obj
        
        # Bind material
        apply_procedural_material(text_obj, params.get("material"))
        
        # Ensure smooth lighting calculations
        text_obj.data.polygons.foreach_set("use_smooth", [True] * len(text_obj.data.polygons))

    # Embed original specifications into root object custom properties
    sub_obj["trench_builder_spec"] = json.dumps(spec)
    sub_obj["trench_builder_version"] = "3.1_typography"

    # Export to GLB
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    bpy.ops.object.select_all(action='DESELECT')
    sub_obj.select_set(True)
    for child in sub_obj.children:
        child.select_set(True)
        
    print(f"Exporting compiled typography assembly to: {output_path}")
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format='GLB',
        use_selection=True
    )
    print("Compilation and export completed successfully.")


if __name__ == "__main__":
    # Handle command line args passed to blender --python
    argv = sys.argv
    if "--" in argv:
        args_idx = argv.index("--") + 1
        args_list = argv[args_idx:]
    else:
        args_list = []

    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, help="Input spec JSON path")
    parser.add_argument("--out", required=True, help="Output GLB path")
    args = parser.parse_args(args_list)

    build_typography(args.spec, args.out)
