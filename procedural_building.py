#!/usr/bin/env python
"""
procedural_building.py
======================
Constraint-Driven Vehicle & Shop Configuration Engine for Blender 4.0+.
Implements:
  1. Declarative VehicleConfig system.
  2. BMesh-based concrete speaker shop/tuning bay envelope and vehicle hoist.
  3. Kirigami folded sheet-metal speaker enclosure.
  4. Complete, multi-layered speaker driver assembly:
     - Voice Coil Former (inner tabbed cylinder).
     - Folding Spider (concentric ripple bellows suspension).
     - Main Speaker Cone (faceted sector panels).
     - Outer Surround (flexible boundary roll).
  5. GLB and .blend exports.
"""

import bpy
import bmesh
import math
import os
from pathlib import Path
from mathutils import Vector

class VehicleConfig:
    def __init__(self):
        # Packaging bounds (m)
        self.wheelbase = 3.8
        self.track_width = 1.8
        self.ride_height = 0.4
        self.panel_gap = 0.005
        
        # Structural parameters
        self.chassis_height = 1.8
        self.speaker_volume_litres = 120.0
        self.lug_nut_count = 5

def setup_materials():
    print("Setting up materials...")
    
    # --- Glass Material ---
    glass = bpy.data.materials.new(name="Glass")
    glass.use_nodes = True
    g_nodes = glass.node_tree.nodes
    g_nodes.clear()
    
    out_node = g_nodes.new('ShaderNodeOutputMaterial')
    bsdf_node = g_nodes.new('ShaderNodeBsdfPrincipled')
    bsdf_node.location = (-200, 0)
    glass.node_tree.links.new(bsdf_node.outputs['BSDF'], out_node.inputs['Surface'])
    
    inputs = bsdf_node.inputs
    if 'Base Color' in inputs:
        inputs['Base Color'].default_value = (0.8, 0.9, 1.0, 1.0)
    if 'Transmission Weight' in inputs:
        inputs['Transmission Weight'].default_value = 1.0
    elif 'Transmission' in inputs:
        inputs['Transmission'].default_value = 1.0
    if 'Roughness' in inputs:
        inputs['Roughness'].default_value = 0.05
        
    # --- Concrete/Metal Shop Material ---
    metal = bpy.data.materials.new(name="Concrete")
    metal.use_nodes = True
    m_nodes = metal.node_tree.nodes
    m_nodes.clear()
    
    out_node_m = m_nodes.new('ShaderNodeOutputMaterial')
    bsdf_node_m = m_nodes.new('ShaderNodeBsdfPrincipled')
    bsdf_node_m.location = (-200, 0)
    metal.node_tree.links.new(bsdf_node_m.outputs['BSDF'], out_node_m.inputs['Surface'])
    
    inputs_m = bsdf_node_m.inputs
    if 'Base Color' in inputs_m:
        inputs_m['Base Color'].default_value = (0.35, 0.36, 0.38, 1.0)
    if 'Roughness' in inputs_m:
        inputs_m['Roughness'].default_value = 0.4
    if 'Metallic' in inputs_m:
        inputs_m['Metallic'].default_value = 0.8
        
    return glass, metal

def purge_scene():
    print("Purging scene data blocks...")
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)

def rodrigues_rotation(v_pos, u_axis, theta):
    v = Vector(v_pos)
    u = Vector(u_axis).normalized()
    term1 = v * math.cos(theta)
    term2 = u.cross(v) * math.sin(theta)
    term3 = u * u.dot(v) * (1.0 - math.cos(theta))
    return term1 + term2 + term3

def generate_speaker_shop():
    cfg = VehicleConfig()
    print(f"Generating Configurable Vehicle Shop: Wheelbase={cfg.wheelbase}m, Track={cfg.track_width}m")
    
    # 1. Purge
    purge_scene()
    
    # 2. Materials
    glass_mat, metal_mat = setup_materials()
    
    # Shop Structure
    width, depth, height = 16, 20, 7.0
    shop_mesh = bpy.data.meshes.new("TuningBayMesh")
    bm_shop = bmesh.new()
    bmesh.ops.create_cube(bm_shop, size=1.0)
    bmesh.ops.scale(bm_shop, vec=(width, depth, height), verts=bm_shop.verts)
    bmesh.ops.translate(bm_shop, vec=(0.0, 0.0, height / 2.0), verts=bm_shop.verts)
    bm_shop.to_mesh(shop_mesh)
    bm_shop.free()
    
    shop_obj = bpy.data.objects.new("TuningBay", shop_mesh)
    bpy.context.collection.objects.link(shop_obj)
    shop_obj.data.materials.append(metal_mat)
    
    # 3. Dynamic Hoist
    hoist_mesh = bpy.data.meshes.new("VehicleHoistMesh")
    bm_hoist = bmesh.new()
    offset_x = cfg.track_width / 2.0 + 0.7
    
    # Posts
    bmesh.ops.create_cube(bm_hoist, size=1.0)
    bmesh.ops.scale(bm_hoist, vec=(0.4, 0.4, 4.5), verts=bm_hoist.verts[-8:])
    bmesh.ops.translate(bm_hoist, vec=(-offset_x, 0.0, 2.25), verts=bm_hoist.verts[-8:])
    
    bmesh.ops.create_cube(bm_hoist, size=1.0)
    bmesh.ops.scale(bm_hoist, vec=(0.4, 0.4, 4.5), verts=bm_hoist.verts[-8:])
    bmesh.ops.translate(bm_hoist, vec=(offset_x, 0.0, 2.25), verts=bm_hoist.verts[-8:])
    
    # Arms
    bmesh.ops.create_cube(bm_hoist, size=1.0)
    bmesh.ops.scale(bm_hoist, vec=(offset_x * 2.0, 1.8, 0.15), verts=bm_hoist.verts[-8:])
    bmesh.ops.translate(bm_hoist, vec=(0.0, 0.0, cfg.chassis_height), verts=bm_hoist.verts[-8:])
    
    bm_hoist.to_mesh(hoist_mesh)
    bm_hoist.free()
    
    hoist_obj = bpy.data.objects.new("VehicleHoist", hoist_mesh)
    bpy.context.collection.objects.link(hoist_obj)
    hoist_obj.data.materials.append(metal_mat)
    
    # 4. Vehicle Chassis Frame
    car_mesh = bpy.data.meshes.new("VehicleMesh")
    bm_car = bmesh.new()
    
    bmesh.ops.create_cube(bm_car, size=1.0)
    bmesh.ops.scale(bm_car, vec=(0.15, cfg.wheelbase, 0.15), verts=bm_car.verts)
    bmesh.ops.translate(bm_car, vec=(-cfg.track_width/2.0 + 0.2, 0.0, cfg.chassis_height + 0.15), verts=bm_car.verts[-8:])
    
    bmesh.ops.create_cube(bm_car, size=1.0)
    bmesh.ops.scale(bm_car, vec=(0.15, cfg.wheelbase, 0.15), verts=bm_car.verts[-8:])
    bmesh.ops.translate(bm_car, vec=(cfg.track_width/2.0 - 0.2, 0.0, cfg.chassis_height + 0.15), verts=bm_car.verts[-8:])
    
    bmesh.ops.create_cube(bm_car, size=1.0)
    bmesh.ops.scale(bm_car, vec=(cfg.track_width - 0.4, 0.15, 0.15), verts=bm_car.verts[-8:])
    bmesh.ops.translate(bm_car, vec=(0.0, -cfg.wheelbase/2.0, cfg.chassis_height + 0.15), verts=bm_car.verts[-8:])
    
    bmesh.ops.create_cube(bm_car, size=1.0)
    bmesh.ops.scale(bm_car, vec=(cfg.track_width - 0.4, 0.15, 0.15), verts=bm_car.verts[-8:])
    bmesh.ops.translate(bm_car, vec=(0.0, cfg.wheelbase/2.0, cfg.chassis_height + 0.15), verts=bm_car.verts[-8:])
    
    bm_car.to_mesh(car_mesh)
    bm_car.free()
    
    car_obj = bpy.data.objects.new("VehicleChassis", car_mesh)
    bpy.context.collection.objects.link(car_obj)
    car_obj.data.materials.append(metal_mat)
    
    # 5. Respectful Kirigami Folded Sheet-Metal Enclosure
    print("  Generating folded Kirigami sheet-metal speaker enclosure via Rodrigues' rotation...")
    kirigami_mesh = bpy.data.meshes.new("KirigamiEnclosureMesh")
    bm_k = bmesh.new()
    
    box_w = cfg.track_width - 0.6
    box_d = 1.0
    box_h = 0.9
    
    # Flat 2D layout sheet
    sheet_w = box_w + 2 * box_h
    sheet_d = box_d + 2 * box_h
    bmesh.ops.create_grid(bm_k, x_segments=1, y_segments=1, size=0.5)
    bmesh.ops.scale(bm_k, vec=(sheet_w, sheet_d, 0.0), verts=bm_k.verts)
    
    # Relief cuts
    bmesh.ops.subdivide_edges(bm_k, edges=bm_k.edges, cuts=2, use_grid_fill=True)
    
    # Bending/Folding Flaps via Rodrigues' Rotation
    theta = math.pi / 2.0
    
    flaps_x = [v for v in bm_k.verts if v.co.x > box_w / 2.0]
    for v in flaps_x:
        local_co = v.co - Vector((box_w/2.0, 0.0, 0.0))
        rot_co = rodrigues_rotation(local_co, (0.0, 1.0, 0.0), theta)
        v.co = rot_co + Vector((box_w/2.0, 0.0, 0.0))
        
    flaps_nx = [v for v in bm_k.verts if v.co.x < -box_w / 2.0]
    for v in flaps_nx:
        local_co = v.co - Vector((-box_w/2.0, 0.0, 0.0))
        rot_co = rodrigues_rotation(local_co, (0.0, -1.0, 0.0), theta)
        v.co = rot_co + Vector((-box_w/2.0, 0.0, 0.0))
        
    flaps_y = [v for v in bm_k.verts if v.co.y > box_d / 2.0]
    for v in flaps_y:
        local_co = v.co - Vector((0.0, box_d/2.0, 0.0))
        rot_co = rodrigues_rotation(local_co, (-1.0, 0.0, 0.0), theta)
        v.co = rot_co + Vector((0.0, box_d/2.0, 0.0))
        
    flaps_ny = [v for v in bm_k.verts if v.co.y < -box_d / 2.0]
    for v in flaps_ny:
        local_co = v.co - Vector((0.0, -box_d/2.0, 0.0))
        rot_co = rodrigues_rotation(local_co, (1.0, 0.0, 0.0), theta)
        v.co = rot_co + Vector((0.0, -box_d/2.0, 0.0))
        
    bmesh.ops.translate(bm_k, vec=(0.0, -cfg.wheelbase/2.0 + 0.6, cfg.chassis_height + 0.2), verts=bm_k.verts)
    
    bm_k.to_mesh(kirigami_mesh)
    bm_k.free()
    
    kirigami_obj = bpy.data.objects.new("KirigamiEnclosure", kirigami_mesh)
    bpy.context.collection.objects.link(kirigami_obj)
    kirigami_obj.data.materials.append(metal_mat)
    
    # 6. Complete Symmetrical Speaker Driver Stack
    print("  Generating complete folded speaker driver stacks (Former + Spider + Cone + Surround)...")
    sub_mesh = bpy.data.meshes.new("SubwooferBoxMesh")
    bm_sub = bmesh.new()
    
    # Define concentric diameters
    r_coil = 0.08
    r_spider_outer = 0.15
    r_cone_outer = 0.25
    r_surround_outer = 0.28
    
    # Generate left and right driver stacks
    centers = [-box_w/4.0, box_w/4.0]
    for cx in centers:
        # Base translation vector for this driver center
        base_loc = Vector((cx, -cfg.wheelbase/2.0 + 0.6 + cfg.panel_gap, cfg.chassis_height + 0.65))
        
        # A. Voice Coil Former (Cylinder)
        bmesh.ops.create_cone(bm_sub, cap_ends=True, cap_tris=True, segments=16, radius1=r_coil, radius2=r_coil, depth=0.2)
        bmesh.ops.translate(bm_sub, vec=base_loc - Vector((0.0, 0.1, 0.0)), verts=bm_sub.verts[-18:])
        
        # B. Folding Spider Suspension (Concentric ripple rings - folded alternating +/- 15 degrees)
        for ring in range(3):
            r_inner = r_coil + ring * 0.02
            r_outer = r_inner + 0.02
            # Alternating direction fold angle (0.25 radians ~ 15 degrees)
            f_angle = 0.25 if ring % 2 == 0 else -0.25
            
            bmesh.ops.create_cone(bm_sub, cap_ends=True, cap_tris=True, segments=16, radius1=r_inner, radius2=r_outer, depth=0.04)
            # Apply fold rotation to upper vertex rim
            for v in bm_sub.verts[-18:]:
                if v.co.z > 0.0:
                    rot = rodrigues_rotation(v.co, (1.0, 0.0, 0.0), f_angle)
                    v.co = rot
            bmesh.ops.translate(bm_sub, vec=base_loc - Vector((0.0, 0.02, 0.0)), verts=bm_sub.verts[-18:])
            
        # C. Main Speaker Cone (Faceted sector panels)
        bmesh.ops.create_cone(bm_sub, cap_ends=True, cap_tris=True, segments=16, radius1=r_spider_outer, radius2=r_cone_outer, depth=0.2)
        bmesh.ops.translate(bm_sub, vec=base_loc, verts=bm_sub.verts[-18:])
        
        # D. Outer Surround (Flexible boundary roll)
        bmesh.ops.create_cone(bm_sub, cap_ends=True, cap_tris=True, segments=16, radius1=r_cone_outer, radius2=r_surround_outer, depth=0.03)
        bmesh.ops.translate(bm_sub, vec=base_loc + Vector((0.0, 0.1, 0.0)), verts=bm_sub.verts[-18:])
        
    bm_sub.to_mesh(sub_mesh)
    bm_sub.free()
    
    sub_obj = bpy.data.objects.new("VehicleSubwoofers", sub_mesh)
    bpy.context.collection.objects.link(sub_obj)
    sub_obj.data.materials.append(glass_mat)
    
    print("Structural constraint assembly complete.")

def export_outputs():
    output_dir = Path(__file__).parent / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    blend_path = output_dir / "procedural_building.blend"
    glb_path = output_dir / "procedural_building.glb"
    
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    print(f"Saved Blender file: {blend_path}")
    
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format='GLB',
        use_selection=False,
        export_apply=True
    )
    print(f"Exported GLB to: {glb_path}")

if __name__ == "__main__":
    generate_speaker_shop()
    export_outputs()
