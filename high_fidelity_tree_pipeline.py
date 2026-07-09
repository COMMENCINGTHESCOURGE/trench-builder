import bpy
import json
import sys
import argparse
import random
import math
from mathutils import Vector, Euler

def load_config(path):
    with open(path) as f:
        return json.load(f)

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def generate_branch(curve_data, start_loc, direction, length, radius, depth, max_depth, density, leaves_list):
    if depth > max_depth: return
    
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(1)
    
    p0 = spline.bezier_points[0]
    p1 = spline.bezier_points[1]
    
    end_loc = start_loc + direction * length
    
    p0.co = start_loc
    p0.handle_left_type = 'VECTOR'
    p0.handle_right_type = 'VECTOR'
    p0.radius = radius
    
    p1.co = end_loc
    p1.handle_left_type = 'VECTOR'
    p1.handle_right_type = 'VECTOR'
    p1.radius = radius * 0.6
    
    # Branches
    if depth < max_depth:
        # Number of branches increases with density spec
        num_branches = max(2, int(density))
        for _ in range(num_branches):
            angle_y = random.uniform(0.3, 1.2) # Lean outward
            angle_z = random.uniform(0, math.pi*2)
            rot = Euler((0, angle_y, angle_z), 'XYZ')
            
            # Base it mostly on UP vector to simulate phototropism
            up_vector = Vector((0,0,1))
            new_dir = direction.lerp(up_vector, 0.3)
            new_dir.rotate(rot)
            new_dir.normalize()
            
            branch_length = length * random.uniform(0.6, 0.85)
            branch_radius = radius * 0.65
            
            branch_start = start_loc + direction * (length * random.uniform(0.4, 0.9))
            generate_branch(curve_data, branch_start, new_dir, branch_length, branch_radius, depth+1, max_depth, density, leaves_list)
    else:
        # At terminal branches, record positions for foliage
        leaves_list.append(end_loc)

def build_and_export_tree(cfg, output_path):
    tree_name = cfg.get("model_id", "Tree")
    
    height = 5.0
    radius = 0.5
    density = 3
    trunk_color = [0.3, 0.2, 0.1, 1.0]
    foliage_color = [0.1, 0.5, 0.2, 1.0]
    
    for comp in cfg.get("components", []):
        if comp["component_type"] == "trunk":
            height = comp["parameters"].get("height", height)
            radius = comp["parameters"].get("radius", radius)
            trunk_color = comp["parameters"].get("color", trunk_color)
        elif comp["component_type"] == "foliage":
            density = comp["parameters"].get("density", density)
            foliage_color = comp["parameters"].get("color", foliage_color)
            
    random.seed(hash(tree_name)) # Deterministic per tree

    # 1. Generate Custom Curve Tree
    curve_data = bpy.data.curves.new(tree_name+"_curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.fill_mode = 'FULL'
    curve_data.bevel_depth = 1.0 # Multiplier for point radius
    curve_data.bevel_resolution = 4

    tree_obj = bpy.data.objects.new(tree_name+"_Trunk", curve_data)
    bpy.context.collection.objects.link(tree_obj)
    
    leaves_positions = []
    # Kick off recursion
    max_depth = 4
    initial_length = height * 0.4
    generate_branch(curve_data, Vector((0,0,0)), Vector((0,0,1)), initial_length, radius, 0, max_depth, density, leaves_positions)
    
    # Convert tree to mesh
    bpy.ops.object.select_all(action='DESELECT')
    tree_obj.select_set(True)
    bpy.context.view_layer.objects.active = tree_obj
    bpy.ops.object.convert(target='MESH')
    
    # 2. Generate Foliage Clusters
    bpy.ops.object.select_all(action='DESELECT')
    leaf_objects = []
    leaf_radius = (height / max_depth) * 0.8
    for pos in leaves_positions:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=leaf_radius, location=pos)
        leaf = bpy.context.active_object
        
        # Add some random distortion to leaves
        for v in leaf.data.vertices:
            v.co += Vector((random.uniform(-0.2,0.2), random.uniform(-0.2,0.2), random.uniform(-0.2,0.2)))
            
        leaf_objects.append(leaf)
        bpy.ops.object.select_all(action='DESELECT')
        
    # Join all leaves into one object
    if leaf_objects:
        for leaf in leaf_objects:
            leaf.select_set(True)
        bpy.context.view_layer.objects.active = leaf_objects[0]
        bpy.ops.object.join()
        leaves_obj = bpy.context.active_object
        leaves_obj.name = tree_name + "_Foliage"
    else:
        leaves_obj = None

    # 3. Materials
    mat_t = bpy.data.materials.new("Bark")
    mat_t.use_nodes = True
    mat_t.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = trunk_color
    tree_obj.data.materials.append(mat_t)
    
    if leaves_obj:
        mat_f = bpy.data.materials.new("Foliage")
        mat_f.use_nodes = True
        mat_f.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = foliage_color
        leaves_obj.data.materials.append(mat_f)
    
    # 4. Join Trunk and Foliage
    bpy.ops.object.select_all(action='DESELECT')
    tree_obj.select_set(True)
    if leaves_obj:
        leaves_obj.select_set(True)
    
    bpy.context.view_layer.objects.active = tree_obj
    bpy.ops.object.join()
    
    final_obj = bpy.context.active_object
    final_obj.name = tree_name
    
    # 5. Export
    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format='GLB',
        use_selection=True,
        export_apply=True
    )
    print(f"Exported to {output_path}")

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    
    clear_scene()
    cfg = load_config(args.config)
    build_and_export_tree(cfg, args.out)
