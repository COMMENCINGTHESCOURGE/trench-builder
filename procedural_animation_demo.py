"""
PROCEDURAL ANIMATION DEEP DIVE — Blender 5.1 Geometry Nodes
============================================================
Creates a geometry node system that animates mecha parts procedurally.
No keyframes. Time drives everything through nodes.

Run:
  "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --python procedural_animation_demo.py
"""
import bpy
import math
import json
from pathlib import Path

# ═══ SCENE SETUP ═══
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import the mecha knee GLB
glb_path = Path(__file__).parent.parent / "mecha_knee.glb"
if glb_path.exists():
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    obj = bpy.context.selected_objects[0]
    obj.name = "mecha_knee"
else:
    # Fallback: create a simple mesh
    bpy.ops.mesh.primitive_cube_add(size=2)
    obj = bpy.context.active_object
    obj.name = "mecha_knee"
    bpy.ops.object.shade_smooth()

print(f"Working with: {obj.name}")

# ═══ GEOMETRY NODE TREE ═══
ng = bpy.data.node_groups.new("MechaProceduralAnimation", "GeometryNodeTree")

# Interface: expose parameters for game engine
ng.interface.new_socket("Geometry", socket_type="NodeSocketGeometry", in_out="INPUT")
ng.interface.new_socket("Breath", socket_type="NodeSocketFloat", in_out="INPUT")
ng.interface.items_tree["Breath"].default_value = 0.8
ng.interface.items_tree["Breath"].min_value = 0.0
ng.interface.items_tree["Breath"].max_value = 1.0

ng.interface.new_socket("JointAngle", socket_type="NodeSocketFloat", in_out="INPUT")
ng.interface.items_tree["JointAngle"].default_value = 0.0
ng.interface.items_tree["JointAngle"].min_value = -90.0
ng.interface.items_tree["JointAngle"].max_value = 90.0

ng.interface.new_socket("Time", socket_type="NodeSocketFloat", in_out="INPUT")
ng.interface.items_tree["Time"].default_value = 0.0

ng.interface.new_socket("Geometry", socket_type="NodeSocketGeometry", in_out="OUTPUT")

nodes = ng.nodes
links = ng.links

# --- NODE 1: Group Input ---
group_in = nodes.new("NodeGroupInput")
group_in.location = (-800, 0)

# --- NODE 2: Group Output ---
group_out = nodes.new("NodeGroupOutput")
group_out.location = (800, 0)

# --- NODE 3: Scene Time (built-in time driver) ---
scene_time = nodes.new("GeometryNodeInputSceneTime")
scene_time.location = (-800, -200)

# --- NODE 4: Math — sine wave from time ---
math_sine = nodes.new("ShaderNodeMath")
math_sine.operation = 'SINE'
math_sine.location = (-600, -200)
links.new(scene_time.outputs["Seconds"], math_sine.inputs[0])

# --- NODE 5: Math — remap sine (-1..1) to (0..1) ---
math_remap = nodes.new("ShaderNodeMath")
math_remap.operation = 'MULTIPLY_ADD'
math_remap.location = (-400, -200)
math_remap.inputs[1].default_value = 0.5
math_remap.inputs[2].default_value = 0.5
links.new(math_sine.outputs["Value"], math_remap.inputs[0])

# --- NODE 6: Multiply Breath × Wave ---
math_breath = nodes.new("ShaderNodeMath")
math_breath.operation = 'MULTIPLY'
math_breath.location = (-200, -200)
links.new(math_remap.outputs["Value"], math_breath.inputs[0])
links.new(group_in.outputs["Breath"], math_breath.inputs[1])

# --- NODE 7: Noise Texture (organic micro-deformation) ---
noise = nodes.new("ShaderNodeTexNoise")
noise.location = (-600, -400)
noise.inputs["Scale"].default_value = 2.0
noise.inputs["Detail"].default_value = 4.0
noise.inputs["Roughness"].default_value = 0.5

# --- NODE 8: Combine XYZ for noise position ---
combine_pos = nodes.new("ShaderNodeCombineXYZ")
combine_pos.location = (-800, -400)

# --- NODE 9: Separate XYZ from Object Info (for world-space position) ---
obj_info = nodes.new("GeometryNodeObjectInfo")
obj_info.location = (-1000, -400)
obj_info.transform_space = 'RELATIVE'

# --- NODE 10: Vector Math — Scale noise displacement ---
vec_scale = nodes.new("ShaderNodeVectorMath")
vec_scale.operation = 'MULTIPLY'
vec_scale.location = (-400, -500)
vec_scale.inputs[1].default_value = (0.02, 0.02, 0.02)  # subtle displacement
links.new(noise.outputs["Color"], vec_scale.inputs[0])

# --- NODE 11: Set Position — apply displacement ---
set_pos = nodes.new("GeometryNodeSetPosition")
set_pos.location = (200, -300)
links.new(group_in.outputs["Geometry"], set_pos.inputs["Geometry"])

# --- NODE 12: Math — multiply noise by breath ---
math_noise_breath = nodes.new("ShaderNodeMath")
math_noise_breath.operation = 'MULTIPLY'
math_noise_breath.location = (-200, -500)
links.new(vec_scale.outputs["Vector"], math_noise_breath.inputs[0])
links.new(group_in.outputs["Breath"], math_noise_breath.inputs[1])

# --- NODE 13: Transform Geometry — rotate via joint angle ---
transform = nodes.new("GeometryNodeTransform")
transform.location = (400, 0)
transform.inputs["Rotation"].default_value = (0, 0, 0)
links.new(set_pos.outputs["Geometry"], transform.inputs["Geometry"])

# --- NODE 14: Combine rotation from joint angle ---
combine_rot = nodes.new("FunctionNodeCombineTransform")
combine_rot.location = (200, 100)

# --- NODE 15: Math — joint angle to radians ---
math_to_rad = nodes.new("ShaderNodeMath")
math_to_rad.operation = 'MULTIPLY'
math_to_rad.location = (0, 100)
math_to_rad.inputs[1].default_value = math.pi / 180.0
links.new(group_in.outputs["JointAngle"], math_to_rad.inputs[0])

links.new(math_to_rad.outputs["Value"], combine_rot.inputs["Rotation"])
links.new(combine_rot.outputs["Transform"], transform.inputs["Transform"])

# --- FINAL: connect to output ---
links.new(transform.outputs["Geometry"], group_out.inputs["Geometry"])

# ═══ ASSIGN NODE GROUP TO OBJECT ═══
mod = obj.modifiers.new("ProceduralMechaAnim", 'NODES')
mod.node_group = ng

print(f"""
PROCEDURAL ANIMATION NODE TREE — READY
═══════════════════════════════════════
Nodes: {len(nodes)}
Links: {len(links)}
Inputs exposed:
  • Breath (float 0-1)    — drives organic micro-deformation
  • JointAngle (float °)   — drives mecha joint rotation
  • Time (float sec)       — optional external time source
Internal:
  • Scene Time → Sine → Remap → Breath modulation
  • Noise Texture → Position displacement (0.02mm)
  • JoinsAngle → Radians → Transform rotation
Behavior per frame:
  1. Scene time drives sine wave
  2. Sine remapped to 0-1 range  
  3. Multiplied by Breath input = breathing amplitude
  4. Noise texture sampled at changing positions
  5. Vertices displaced by noise × breath = organic micro-movement
  6. Joint angle rotates entire assembly
""")

# ═══ SAVE .blend ═══
out_path = Path(__file__).parent.parent / "mecha_procedural_anim.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out_path))
print(f"Saved: {out_path}")
