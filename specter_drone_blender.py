"""
NOVA HORIZON 3D — High-Fidelity Specter Drone
Blender 5.1 Python Script
Generates a compound-mesh enemy with PBR materials, lighting rig, and renders.
"""
import bpy
import math
import os

# ============================================================
# CLEAN SCENE
# ============================================================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for col in bpy.data.collections:
    if col.name != 'Scene Collection':
        bpy.data.collections.remove(col)
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)

# ============================================================
# COLLECTION
# ============================================================
drone_col = bpy.data.collections.new("SpecterDrone")
bpy.context.scene.collection.children.link(drone_col)

def link_to_drone(obj):
    """Unlink from scene collection, link to drone collection."""
    for col in obj.users_collection:
        col.objects.unlink(obj)
    drone_col.objects.link(obj)

# ============================================================
# MATERIALS
# ============================================================

# --- Core: Emissive energy sphere ---
mat_core = bpy.data.materials.new("Drone_Core")
mat_core.use_nodes = True
nodes = mat_core.node_tree.nodes
links = mat_core.node_tree.links
nodes.clear()
emission = nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (0.0, 0.9, 0.45, 1.0)  # Teal green
emission.inputs['Strength'].default_value = 15.0
output = nodes.new('ShaderNodeOutputMaterial')
links.new(emission.outputs['Emission'], output.inputs['Surface'])

# --- Inner Shell: Translucent glass ---
mat_shell = bpy.data.materials.new("Drone_InnerShell")
mat_shell.use_nodes = True
nodes = mat_shell.node_tree.nodes
links = mat_shell.node_tree.links
bsdf = nodes.get('Principled BSDF')
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.2, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.05
    # Transmission for glass
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.85
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.85
    bsdf.inputs['IOR'].default_value = 1.45
    bsdf.inputs['Alpha'].default_value = 0.6
mat_shell.blend_method = 'BLEND' if hasattr(mat_shell, 'blend_method') else None

# --- Outer Shield: Dark metallic translucent ---
mat_outer = bpy.data.materials.new("Drone_OuterShield")
mat_outer.use_nodes = True
nodes = mat_outer.node_tree.nodes
bsdf = nodes.get('Principled BSDF')
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.12, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.15
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 1.0
        bsdf.inputs['Coat Roughness'].default_value = 0.1
    elif 'Clearcoat' in bsdf.inputs:
        bsdf.inputs['Clearcoat'].default_value = 1.0
    bsdf.inputs['Alpha'].default_value = 0.4

# --- Ring Material: Brushed alloy ---
mat_ring = bpy.data.materials.new("Drone_Ring")
mat_ring.use_nodes = True
nodes = mat_ring.node_tree.nodes
links = mat_ring.node_tree.links
bsdf = nodes.get('Principled BSDF')
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.75, 0.75, 0.8, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.2
    # Add subtle anisotropy for brushed metal look
    if 'Anisotropic' in bsdf.inputs:
        bsdf.inputs['Anisotropic'].default_value = 0.5

# --- Sensor Node Material: Glowing accent ---
mat_sensor = bpy.data.materials.new("Drone_Sensor")
mat_sensor.use_nodes = True
nodes = mat_sensor.node_tree.nodes
links = mat_sensor.node_tree.links
nodes.clear()
emission = nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (0.0, 1.0, 0.8, 1.0)
emission.inputs['Strength'].default_value = 5.0
output = nodes.new('ShaderNodeOutputMaterial')
links.new(emission.outputs['Emission'], output.inputs['Surface'])

# --- Particle Material: Faint cyan sparks ---
mat_particle = bpy.data.materials.new("Drone_Particle")
mat_particle.use_nodes = True
nodes = mat_particle.node_tree.nodes
links = mat_particle.node_tree.links
nodes.clear()
emission = nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (0.0, 0.8, 0.6, 1.0)
emission.inputs['Strength'].default_value = 3.0
output = nodes.new('ShaderNodeOutputMaterial')
transparent = nodes.new('ShaderNodeBsdfTransparent')
mix = nodes.new('ShaderNodeMixShader')
mix.inputs['Fac'].default_value = 0.7
links.new(transparent.outputs['BSDF'], mix.inputs[1])
links.new(emission.outputs['Emission'], mix.inputs[2])
links.new(mix.outputs['Shader'], output.inputs['Surface'])

# ============================================================
# GEOMETRY
# ============================================================

# --- 1. Core energy sphere (small, intensely glowing) ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, segments=32, ring_count=16, location=(0, 0, 0))
core = bpy.context.active_object
core.name = "Drone_Core"
core.data.materials.append(mat_core)
link_to_drone(core)

# --- 2. Inner shell (slightly larger, glass) ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, segments=48, ring_count=24, location=(0, 0, 0))
inner_shell = bpy.context.active_object
inner_shell.name = "Drone_InnerShell"
inner_shell.data.materials.append(mat_shell)
link_to_drone(inner_shell)

# --- 3. Outer shield (largest sphere, dark metallic translucent) ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, segments=64, ring_count=32, location=(0, 0, 0))
outer_shield = bpy.context.active_object
outer_shield.name = "Drone_OuterShield"
outer_shield.data.materials.append(mat_outer)
# Add subdivision surface for smoothness
sub = outer_shield.modifiers.new("Subsurf", 'SUBSURF')
sub.levels = 2
sub.render_levels = 3
link_to_drone(outer_shield)

# --- 4. Primary orbital ring (tilted) ---
bpy.ops.mesh.primitive_torus_add(
    major_radius=1.1, minor_radius=0.04,
    major_segments=64, minor_segments=16,
    location=(0, 0, 0)
)
ring1 = bpy.context.active_object
ring1.name = "Drone_Ring_Primary"
ring1.rotation_euler = (math.radians(25), math.radians(15), 0)
ring1.data.materials.append(mat_ring)
link_to_drone(ring1)

# --- 5. Secondary orbital ring (perpendicular, thinner) ---
bpy.ops.mesh.primitive_torus_add(
    major_radius=1.0, minor_radius=0.025,
    major_segments=64, minor_segments=12,
    location=(0, 0, 0)
)
ring2 = bpy.context.active_object
ring2.name = "Drone_Ring_Secondary"
ring2.rotation_euler = (math.radians(75), math.radians(-30), math.radians(45))
ring2.data.materials.append(mat_ring)
link_to_drone(ring2)

# --- 6. Tertiary accent ring (innermost, emissive) ---
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.65, minor_radius=0.015,
    major_segments=48, minor_segments=8,
    location=(0, 0, 0)
)
ring3 = bpy.context.active_object
ring3.name = "Drone_Ring_Accent"
ring3.rotation_euler = (math.radians(90), 0, math.radians(60))
ring3.data.materials.append(mat_sensor)
link_to_drone(ring3)

# --- 7. Sensor nodes (4 floating cylinders around equator) ---
for i in range(4):
    angle = i * (math.pi / 2)  # 90 degree spacing
    x = math.cos(angle) * 1.25
    y = math.sin(angle) * 1.25
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.06, depth=0.18,
        vertices=12,
        location=(x, y, 0)
    )
    sensor = bpy.context.active_object
    sensor.name = f"Drone_Sensor_{i}"
    # Point sensor toward center
    sensor.rotation_euler = (math.radians(90), 0, angle + math.radians(90))
    sensor.data.materials.append(mat_sensor)
    link_to_drone(sensor)

# --- 8. Antenna spines (top and bottom) ---
for z_sign, name in [(1, "Top"), (-1, "Bottom")]:
    bpy.ops.mesh.primitive_cone_add(
        radius1=0.08, radius2=0.01, depth=0.5,
        vertices=8,
        location=(0, 0, z_sign * 1.0)
    )
    spine = bpy.context.active_object
    spine.name = f"Drone_Spine_{name}"
    if z_sign == -1:
        spine.rotation_euler = (math.radians(180), 0, 0)
    spine.data.materials.append(mat_ring)
    link_to_drone(spine)

# --- 9. Surface panel detail (hexagonal plates on outer shield) ---
# Create a few hexagonal detail plates slightly above the outer shell surface
for i in range(6):
    angle = i * (math.pi / 3)
    r = 0.82  # Just above outer shield
    x = math.cos(angle) * r * 0.7
    y = math.sin(angle) * r * 0.7
    z = math.sin(angle * 0.5) * 0.3
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.12, depth=0.015,
        vertices=6,  # Hexagon
        location=(x, y, z)
    )
    plate = bpy.context.active_object
    plate.name = f"Drone_HexPlate_{i}"
    # Orient to face outward from center
    direction = math.atan2(y, x)
    plate.rotation_euler = (
        math.acos(z / max(math.sqrt(x*x + y*y + z*z), 0.001)),
        0,
        direction
    )
    plate.data.materials.append(mat_ring)
    link_to_drone(plate)

# ============================================================
# LIGHTING RIG
# ============================================================

# Key light: Cool blue-white from upper right
bpy.ops.object.light_add(type='AREA', location=(3, -2, 4))
key_light = bpy.context.active_object
key_light.name = "Key_Light"
key_light.data.energy = 200
key_light.data.color = (0.7, 0.85, 1.0)
key_light.data.size = 3
key_light.rotation_euler = (math.radians(45), math.radians(15), math.radians(-20))
link_to_drone(key_light)

# Rim light: Teal accent from behind
bpy.ops.object.light_add(type='AREA', location=(-3, 1, 2))
rim_light = bpy.context.active_object
rim_light.name = "Rim_Light"
rim_light.data.energy = 150
rim_light.data.color = (0.0, 0.9, 0.7)
rim_light.data.size = 2
rim_light.rotation_euler = (math.radians(30), math.radians(-160), 0)
link_to_drone(rim_light)

# Fill light: Very dim warm from below
bpy.ops.object.light_add(type='AREA', location=(0, 3, -1))
fill_light = bpy.context.active_object
fill_light.name = "Fill_Light"
fill_light.data.energy = 30
fill_light.data.color = (1.0, 0.85, 0.7)
fill_light.data.size = 4
fill_light.rotation_euler = (math.radians(-70), 0, 0)
link_to_drone(fill_light)

# Ground bounce: Subtle green from own emission reflecting
bpy.ops.object.light_add(type='POINT', location=(0, 0, -2))
ground_bounce = bpy.context.active_object
ground_bounce.name = "Ground_Bounce"
ground_bounce.data.energy = 20
ground_bounce.data.color = (0.0, 0.8, 0.5)
link_to_drone(ground_bounce)

# ============================================================
# GROUND PLANE (for shadow and reflection)
# ============================================================
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -2.5))
ground = bpy.context.active_object
ground.name = "Ground_Plane"
mat_ground = bpy.data.materials.new("Ground")
mat_ground.use_nodes = True
bsdf = mat_ground.node_tree.nodes.get('Principled BSDF')
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.03, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.4
    bsdf.inputs['Metallic'].default_value = 0.1
ground.data.materials.append(mat_ground)
link_to_drone(ground)

# ============================================================
# CAMERA
# ============================================================
bpy.ops.object.camera_add(location=(3.5, -3.5, 1.5))
cam = bpy.context.active_object
cam.name = "Drone_Camera"
cam.data.lens = 85  # Portrait lens for cinematic feel
cam.data.clip_end = 100
# Point at drone center
constraint = cam.constraints.new('TRACK_TO')
constraint.target = core
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'
bpy.context.scene.camera = cam
link_to_drone(cam)

# ============================================================
# WORLD / ENVIRONMENT
# ============================================================
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("DroneWorld")
    bpy.context.scene.world = world
world.use_nodes = True
wnodes = world.node_tree.nodes
wlinks = world.node_tree.links
wnodes.clear()
bg = wnodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.005, 0.005, 0.015, 1.0)  # Near-black with subtle blue
bg.inputs['Strength'].default_value = 0.3
output = wnodes.new('ShaderNodeOutputWorld')
wlinks.new(bg.outputs['Background'], output.inputs['Surface'])

# ============================================================
# RENDER SETTINGS
# ============================================================
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_depth = '16'

# Bloom via compositor
try:
    scene.use_nodes = True
    node_tree = getattr(scene, "compositing_node_group", None)
    if node_tree is None:
        if hasattr(scene, "compositing_node_group"):
            node_tree = bpy.data.node_groups.new('CompositorNodeTree', 'CompositorNodeTree')
            scene.compositing_node_group = node_tree
        else:
            node_tree = getattr(scene, "node_tree", None)
    comp_nodes = node_tree.nodes
    comp_links = node_tree.links
    comp_nodes.clear()

    rl = comp_nodes.new('CompositorNodeRLayers')
    glare = comp_nodes.new('CompositorNodeGlare')
    if 'Type' in glare.inputs:
        glare.inputs['Type'].default_value = 'Fog Glow'
        glare.inputs['Quality'].default_value = 'High'
        glare.inputs['Threshold'].default_value = 0.8
        glare.inputs['Size'].default_value = 7.0
    else:
        glare.glare_type = 'FOG_GLOW'
        glare.quality = 'HIGH'
        glare.threshold = 0.8
        glare.size = 7

    comp_type = 'CompositorNodeComposite' if 'CompositorNodeComposite' in bpy.types.__dict__ else 'NodeGroupOutput'
    composite = comp_nodes.new(comp_type)

    viewer_type = 'CompositorNodeViewer' if 'CompositorNodeViewer' in bpy.types.__dict__ else 'NodeGroupOutput'
    viewer = comp_nodes.new(viewer_type)

    comp_links.new(rl.outputs['Image'], glare.inputs['Image'])
    comp_links.new(glare.outputs['Image'], composite.inputs['Image'])
    comp_links.new(glare.outputs['Image'], viewer.inputs['Image'])
except Exception as comp_err:
    print(f"Warning: Compositor setup skipped due to: {comp_err}")

# ============================================================
# ANIMATION: Ring rotation + hover bob (60 frames)
# ============================================================
scene.frame_start = 1
scene.frame_end = 120
scene.frame_set(1)

# Animate ring rotations
for frame in range(1, 121):
    scene.frame_set(frame)
    t = frame / 120.0
    
    ring1.rotation_euler = (
        math.radians(25),
        math.radians(15) + t * math.pi * 2,
        t * math.pi * 0.5
    )
    ring1.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    ring2.rotation_euler = (
        math.radians(75) + t * math.pi * 1.5,
        math.radians(-30),
        math.radians(45) + t * math.pi * 2
    )
    ring2.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    ring3.rotation_euler = (
        math.radians(90),
        t * math.pi * 3,
        math.radians(60)
    )
    ring3.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    # Hover bob for entire drone (move core, shells track)
    bob = math.sin(t * math.pi * 4) * 0.15
    core.location.z = bob
    core.keyframe_insert(data_path="location", frame=frame)
    inner_shell.location.z = bob
    inner_shell.keyframe_insert(data_path="location", frame=frame)
    outer_shield.location.z = bob
    outer_shield.keyframe_insert(data_path="location", frame=frame)

scene.frame_set(1)

# ============================================================
# OUTPUT PATH
# ============================================================
output_dir = r"G:\My Drive\Trench_Builder\blender_renders"
os.makedirs(output_dir, exist_ok=True)
scene.render.filepath = os.path.join(output_dir, "specter_drone_render")

print("=" * 60)
print("SPECTER DRONE SCENE BUILT SUCCESSFULLY")
print(f"Objects: {len(drone_col.objects)}")
print(f"Materials: {len(bpy.data.materials)}")
print(f"Render output: {scene.render.filepath}")
print("=" * 60)
print("To render: Blender > Render > Render Image (F12)")
print("Or headless: blender --background specter_drone.blend --render-output //render_ -f 1")
