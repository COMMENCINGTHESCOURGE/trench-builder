#!/usr/bin/env python
"""
HYPERPOLY LOFT CHARACTER — Skin Modifier Version
Blender 5.1.1 compatible. No .add() on bpy_prop_collection.
"""
import bpy
import math
from mathutils import Vector

def reset_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.armatures, bpy.data.materials):
        for item in list(block):
            if item.users == 0:
                block.remove(item)

def build_lofted_character():
    reset_scene()
    
    skeleton = [
        ("Root",       (0, 0, -3.8), (0, 0, -0.5),  0.25, None),
        ("Spine_Low",  (0, 0, -0.5), (0, 0,  0.8),  0.28, "Root"),
        ("Spine_Mid",  (0, 0,  0.8), (0, 0,  2.2),  0.32, "Spine_Low"),
        ("Spine_High", (0, 0,  2.2), (0, 0,  3.7),  0.30, "Spine_Mid"),
        ("Neck",       (0, 0,  3.7), (0, 0,  4.3),  0.12, "Spine_High"),
        ("Head",       (0, 0,  4.3), (0, 0,  5.4),  0.22, "Neck"),
        ("Shoulder_L", (0, 0,  3.0), (-2.2, 0, 3.0), 0.12, "Spine_High"),
        ("UpperArm_L", (-2.2, 0, 3.0), (-2.6, 0, 2.0), 0.09, "Shoulder_L"),
        ("Forearm_L",  (-2.6, 0, 2.0), (-3.0, 0, 0.6), 0.08, "UpperArm_L"),
        ("Hand_L",     (-3.0, 0, 0.6), (-3.2, 0,-0.2), 0.07, "Forearm_L"),
        ("Shoulder_R", (0, 0,  3.0), ( 2.2, 0, 3.0), 0.12, "Spine_High"),
        ("UpperArm_R", ( 2.2, 0, 3.0), ( 2.6, 0, 2.0), 0.09, "Shoulder_R"),
        ("Forearm_R",  ( 2.6, 0, 2.0), ( 3.0, 0, 0.6), 0.08, "UpperArm_R"),
        ("Hand_R",     ( 3.0, 0, 0.6), ( 3.2, 0,-0.2), 0.07, "Forearm_R"),
        ("Thigh_L",    (0, 0, -0.5), (-0.8, 0,-0.6), 0.14, "Root"),
        ("Shin_L",     (-0.8, 0,-0.6), (-0.8, 0,-2.4), 0.10, "Thigh_L"),
        ("Foot_L",     (-0.8, 0,-2.4), (-0.8, 0.4,-3.8),0.08, "Shin_L"),
        ("Thigh_R",    (0, 0, -0.5), ( 0.8, 0,-0.6), 0.14, "Root"),
        ("Shin_R",     ( 0.8, 0,-0.6), ( 0.8, 0,-2.4), 0.10, "Thigh_R"),
        ("Foot_R",     ( 0.8, 0,-2.4), ( 0.8, 0.4,-3.8),0.08, "Shin_R"),
    ]
    
    verts, edges = [], []
    vmap = {}
    head_idx, tail_idx = {}, {}
    
    for name, h, t, r, parent in skeleton:
        hi = vmap.setdefault(
            (round(h[0],4), round(h[1],4), round(h[2],4)),
            len(verts)
        )
        if hi == len(verts):
            verts.append((Vector(h), r))
        
        ti = vmap.setdefault(
            (round(t[0],4), round(t[1],4), round(t[2],4)),
            len(verts)
        )
        if ti == len(verts):
            verts.append((Vector(t), r * 0.85))
        
        head_idx[name], tail_idx[name] = hi, ti
        edges.append((hi, ti))
    
    mesh = bpy.data.meshes.new("LoftSkeleton")
    mesh.from_pydata([v[0] for v in verts], edges, [])
    mesh.update()
    
    obj = bpy.data.objects.new("HyperPoly_Loft", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Skin modifier
    obj.modifiers.new(name="SkinLoft", type='SKIN')
    subsurf = obj.modifiers.new(name="HyperSubsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 4
    
    # Initialize skin data
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    if len(mesh.skin_vertices) == 0:
        bpy.ops.mesh.customdata_skin_add()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Set radii — access skin_vertices directly, no .data intermediary
    mesh.update()
    skin_layer = mesh.skin_vertices[0]  # the layer itself
    for i, (co, radius) in enumerate(verts):
        if i < len(skin_layer.data):
            skin_layer.data[i].radius = (radius, radius)
    
    # Mark root vertices
    for name, h, t, r, parent in skeleton:
        if parent is None and head_idx[name] < len(skin_layer.data):
            skin_layer.data[head_idx[name]].use_root = True
    
    # Shading
    bpy.ops.object.shade_smooth()
    mesh.use_auto_smooth = True
    mesh.auto_smooth_angle = math.radians(30)
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Vertex groups — add indices one at a time (Blender 5.x compatible)
    zones = {
        "Head": ["Head","Neck"], "Chest": ["Spine_High","Spine_Mid"],
        "Abdomen": ["Spine_Low","Spine_Mid"], "Pelvis": ["Root"],
        "Arm_L": ["Shoulder_L","UpperArm_L","Forearm_L","Hand_L"],
        "Arm_R": ["Shoulder_R","UpperArm_R","Forearm_R","Hand_R"],
        "Leg_L": ["Thigh_L","Shin_L","Foot_L"],
        "Leg_R": ["Thigh_R","Shin_R","Foot_R"],
    }
    for gname, bones in zones.items():
        grp = obj.vertex_groups.new(name=gname)
        for b in bones:
            if b in head_idx:
                grp.add([head_idx[b]], 1.0, 'ADD')
            if b in tail_idx and tail_idx[b] != head_idx.get(b, -1):
                grp.add([tail_idx[b]], 1.0, 'ADD')
    
    # Armature
    bpy.ops.object.armature_add(enter_editmode=True, location=(0,0,0))
    arm = bpy.context.active_object
    arm.name = "HyperPoly_Rig"
    arm.data.name = "HyperPoly_Armature"
    bpy.ops.armature.select_all(action='SELECT')
    bpy.ops.armature.delete()
    
    eb = arm.data.edit_bones
    for name, h, t, r, parent in skeleton:
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
    
    # Final modifiers
    obj.modifiers.new(name="VolumePreserve", type='CORRECTIVE_SMOOTH').factor = 0.5
    
    disp = obj.modifiers.new(name="SkinMicroDetail", type='DISPLACE')
    disp.strength = 0.012
    tex = bpy.data.textures.new(name="SkinNoise", type='NOISE')
    tex.noise_type = 'MUSGRAVE'
    tex.noise_scale = 0.025
    tex.musgrave_dimension_max = 0.8
    disp.texture = tex
    
    obj.modifiers.new(name="WeightedNormals", type='WEIGHTED_NORMAL')
    
    # Material
    mat = bpy.data.materials.new(name="HyperPoly_Skin")
    mat.use_nodes = True
    nd = mat.node_tree.nodes
    nd.clear()
    out = nd.new('ShaderNodeOutputMaterial')
    bsdf = nd.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (-300, 0)
    bsdf.inputs['Base Color'].default_value = (0.8, 0.5, 0.4, 1.0)
    bsdf.inputs['Subsurface Weight'].default_value = 0.3
    bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.4, 0.1)
    bsdf.inputs['Roughness'].default_value = 0.4
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    obj.data.materials.append(mat)
    
    print("✓ Skin-lofted character complete.")
    return obj

if __name__ == "__main__":
    build_lofted_character()
