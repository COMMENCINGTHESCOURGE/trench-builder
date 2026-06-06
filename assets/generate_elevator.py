"""
ELEVATOR ASSET GENERATOR — Industrial construction elevator for Trench Builder.
Run inside Blender: Scripting workspace → Open → Run Script.
Exports: elevator.glb to the same directory.

Design: Steel cage frame, sliding double doors, overhead pulley/cable drum,
interior platform with guardrails, wall-mounted control panel.
Construction-site aesthetic — exposed bolts, cross-bracing, raw steel.
"""
import bpy
import math
import os
from pathlib import Path

# ── Clean scene ─────────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ── Materials ───────────────────────────────────────────────────
def steel_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.55
    bsdf.inputs["Metallic"].default_value = 0.9
    return mat

def concrete_material(name="Concrete"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.35, 0.33, 0.30, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.85
    bsdf.inputs["Metallic"].default_value = 0.0
    return mat

steel_dark = steel_material("Steel_Dark", (0.15, 0.14, 0.13, 1.0))
steel_med  = steel_material("Steel_Med",  (0.28, 0.27, 0.25, 1.0))
steel_light = steel_material("Steel_Light", (0.42, 0.40, 0.37, 1.0))
cable_mat  = steel_material("Cable",        (0.10, 0.10, 0.10, 1.0))
panel_mat  = steel_material("Panel",        (0.22, 0.20, 0.15, 1.0))
concrete   = concrete_material()

# ── Dimensions (meters) ─────────────────────────────────────────
CAGE_W = 2.0    # Width
CAGE_D = 2.0    # Depth
CAGE_H = 3.0    # Height
SHAFT_H = 4.5   # Total shaft height (cage + headroom)
PLATFORM_H = 0.15
RAIL_H = 1.1    # Guardrail height
FRAME_THICK = 0.08  # Steel beam thickness
FLOOR_Y = 0.15      # Floor base offset

# ── Helper: add mesh object ─────────────────────────────────────
def add_mesh(name, verts, faces, material):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(material)
    bpy.context.collection.objects.link(obj)
    return obj

def add_cube(name, location, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    bpy.ops.object.transform_apply(scale=True)
    return obj

def add_cylinder(name, location, radius, depth, rotation, material):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, location=location,
        rotation=rotation, vertices=16
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

# ── 1. Shaft Frame ──────────────────────────────────────────────
def build_shaft_frame():
    """Four corner posts + cross-bracing on X and Y faces."""
    # Corner posts
    for x in (-CAGE_W/2, CAGE_W/2):
        for y in (-CAGE_D/2, CAGE_D/2):
            add_cube(f"Post_{x:.1f}_{y:.1f}",
                     (x, y, SHAFT_H/2 + FLOOR_Y),
                     (FRAME_THICK, FRAME_THICK, SHAFT_H/2),
                     steel_dark)

    # Top frame ring
    h = SHAFT_H + FLOOR_Y
    for x_sign in (-1, 1):
        add_cube(f"TopBeam_X{x_sign}",
                 (x_sign * CAGE_W/2, 0, h),
                 (FRAME_THICK, CAGE_D/2, FRAME_THICK), steel_med)
    for y_sign in (-1, 1):
        add_cube(f"TopBeam_Y{y_sign}",
                 (0, y_sign * CAGE_D/2, h),
                 (CAGE_W/2, FRAME_THICK, FRAME_THICK), steel_med)

    # Cross-bracing — X face (front and back)
    for y_sign in (-1, 1):
        y = y_sign * CAGE_D/2
        # Diagonal beams
        for i in range(3):
            z0 = FLOOR_Y + i * (CAGE_H / 3)
            z1 = z0 + CAGE_H / 3
            for x_dir in (-1, 1):
                x0 = -x_dir * CAGE_W/2
                x1 = x_dir * CAGE_W/2
                cx = (x0 + x1) / 2
                cz = (z0 + z1) / 2
                dx = abs(x1 - x0)
                dz = abs(z1 - z0)
                length = math.sqrt(dx**2 + dz**2)
                angle = math.atan2(dx, dz)
                bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, y, cz))
                obj = bpy.context.active_object
                obj.name = f"Brace_X_{y_sign}_{i}_{x_dir}"
                obj.scale = (FRAME_THICK * 0.6, FRAME_THICK * 0.6, length / 2)
                obj.rotation_euler = (0, angle, 0)
                obj.data.materials.append(steel_dark)
                bpy.ops.object.transform_apply(scale=True)

    # Cross-bracing — Y face (sides)
    for x_sign in (-1, 1):
        x = x_sign * CAGE_W/2
        for i in range(3):
            z0 = FLOOR_Y + i * (CAGE_H / 3)
            z1 = z0 + CAGE_H / 3
            for y_dir in (-1, 1):
                y0 = -y_dir * CAGE_D/2
                y1 = y_dir * CAGE_D/2
                cy = (y0 + y1) / 2
                cz = (z0 + z1) / 2
                dy = abs(y1 - y0)
                dz = abs(z1 - z0)
                length = math.sqrt(dy**2 + dz**2)
                angle = math.atan2(dy, dz)
                bpy.ops.mesh.primitive_cube_add(size=1, location=(x, cy, cz))
                obj = bpy.context.active_object
                obj.name = f"Brace_Y_{x_sign}_{i}_{y_dir}"
                obj.scale = (FRAME_THICK * 0.6, FRAME_THICK * 0.6, length / 2)
                obj.rotation_euler = (angle, 0, 0)
                obj.data.materials.append(steel_dark)
                bpy.ops.object.transform_apply(scale=True)


# ── 2. Interior Platform ────────────────────────────────────────
def build_platform():
    """Floor platform with checkered tread plate."""
    add_cube("Platform", (0, 0, FLOOR_Y),
             (CAGE_W/2 - FRAME_THICK, CAGE_D/2 - FRAME_THICK, PLATFORM_H / 2),
             steel_light)

    # Guardrails around perimeter
    rail_top = FLOOR_Y + RAIL_H
    rail_z = (FLOOR_Y + rail_top) / 2
    rail_half = RAIL_H / 2

    # Top rails
    for x in (-CAGE_W/2 + FRAME_THICK, CAGE_W/2 - FRAME_THICK):
        add_cube(f"RailTop_X{x:.1f}",
                 (x, 0, rail_top),
                 (FRAME_THICK * 0.5, CAGE_D/2 - FRAME_THICK, FRAME_THICK * 0.5),
                 steel_light)
    for y in (-CAGE_D/2 + FRAME_THICK, CAGE_D/2 - FRAME_THICK):
        add_cube(f"RailTop_Y{y:.1f}",
                 (0, y, rail_top),
                 (CAGE_W/2 - FRAME_THICK, FRAME_THICK * 0.5, FRAME_THICK * 0.5),
                 steel_light)

    # Mid rails
    for x in (-CAGE_W/2 + FRAME_THICK, CAGE_W/2 - FRAME_THICK):
        add_cube(f"RailMid_X{x:.1f}",
                 (x, 0, FLOOR_Y + RAIL_H * 0.55),
                 (FRAME_THICK * 0.4, CAGE_D/2 - FRAME_THICK, FRAME_THICK * 0.4),
                 steel_med)
    for y in (-CAGE_D/2 + FRAME_THICK, CAGE_D/2 - FRAME_THICK):
        add_cube(f"RailMid_Y{y:.1f}",
                 (0, y, FLOOR_Y + RAIL_H * 0.55),
                 (CAGE_W/2 - FRAME_THICK, FRAME_THICK * 0.4, FRAME_THICK * 0.4),
                 steel_med)


# ── 3. Sliding Doors ────────────────────────────────────────────
def build_doors():
    """Double sliding doors on front face (Y+) with track mechanism."""
    door_w = CAGE_W / 2 - FRAME_THICK
    door_h = CAGE_H
    door_t = 0.03
    door_y = CAGE_D/2 + 0.02

    # Left door
    add_cube("Door_Left", (-CAGE_W/4, door_y, CAGE_H/2 + FLOOR_Y),
             (door_w/2, door_t, door_h/2), steel_med)

    # Right door
    add_cube("Door_Right", (CAGE_W/4, door_y, CAGE_H/2 + FLOOR_Y),
             (door_w/2, door_t, door_h/2), steel_med)

    # Track above doors
    add_cube("Door_Track", (0, door_y, CAGE_H + FLOOR_Y + 0.05),
             (CAGE_W/2 + 0.1, 0.04, 0.02), steel_dark)

    # Track beam support
    add_cube("Track_Bracket", (0, door_y, CAGE_H + FLOOR_Y + 0.12),
             (0.04, 0.06, 0.06), steel_dark)


# ── 4. Cable Drum & Pulley Assembly ─────────────────────────────
def build_cable_system():
    """Overhead drum, pulley wheels, cables descending to cage."""
    drum_y = CAGE_D/2 + 0.3
    drum_z = SHAFT_H + FLOOR_Y - 0.4

    # Main drum
    add_cylinder("Cable_Drum", (0, drum_y, drum_z),
                 0.15, CAGE_W * 0.8, (0, math.pi/2, 0), cable_mat)

    # Drum axle supports
    for x_sign in (-1, 1):
        add_cube(f"Drum_Bearing_{x_sign}",
                 (x_sign * CAGE_W * 0.35, drum_y, drum_z),
                 (0.06, 0.06, 0.2), steel_dark)

    # Support beam connecting drum to shaft
    add_cube("Drum_Beam", (0, CAGE_D/2 + 0.05, drum_z),
             (CAGE_W/2 + 0.1, 0.06, 0.06), steel_dark)

    # Pulley wheels at cage top corners
    for x_sign in (-1, 1):
        for y_sign in (-1, 1):
            add_cylinder(f"Pulley_{x_sign}_{y_sign}",
                         (x_sign * CAGE_W * 0.35, y_sign * CAGE_D * 0.3,
                          SHAFT_H + FLOOR_Y - 0.15),
                         0.06, 0.04, (0, math.pi/2, 0), cable_mat)

    # Vertical cables from drum to cage (thin cylinders)
    for x_sign in (-1, 1):
        add_cylinder(f"Cable_{x_sign}",
                     (x_sign * CAGE_W * 0.3, CAGE_D/2 + 0.05,
                      (FLOOR_Y + SHAFT_H - 0.3) / 2),
                     0.015, SHAFT_H - 0.6,
                     (0, math.pi/2, 0), cable_mat)


# ── 5. Control Panel ────────────────────────────────────────────
def build_control_panel():
    """Wall-mounted control panel inside cage, right wall."""
    panel_x = CAGE_W/2 - FRAME_THICK - 0.01
    panel_y = 0
    panel_z = 1.2  # Eye level

    # Panel box
    add_cube("Control_Panel",
             (panel_x, panel_y, panel_z),
             (0.02, 0.3, 0.18), panel_mat)

    # Floor indicator arrow
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.015, depth=0.04,
        location=(panel_x + 0.025, panel_y - 0.08, panel_z + 0.05),
        rotation=(math.pi/2, 0, 0), vertices=8
    )
    obj = bpy.context.active_object
    obj.name = "Panel_Knob"
    obj.data.materials.append(steel_dark)

    # Emergency stop button
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.025, depth=0.03,
        location=(panel_x + 0.025, panel_y + 0.08, panel_z + 0.05),
        rotation=(math.pi/2, 0, 0), vertices=8
    )
    obj = bpy.context.active_object
    obj.name = "Stop_Button"
    obj.data.materials.append(steel_light)


# ── 6. Concrete Base Plate ──────────────────────────────────────
def build_base():
    """Concrete pad at floor level."""
    add_cube("Concrete_Base", (0, 0, FLOOR_Y - 0.1),
             (CAGE_W/2 + 0.2, CAGE_D/2 + 0.2, 0.1), concrete)


# ── Build ───────────────────────────────────────────────────────
print("Building elevator...")
build_base()
build_shaft_frame()
build_platform()
build_doors()
build_cable_system()
build_control_panel()

# ── Join into single object hierarchy ───────────────────────────
bpy.ops.object.select_all(action='SELECT')
# Keep objects separate for game engine import (GLTF preserves hierarchy)

# ── Export to GLB ───────────────────────────────────────────────
out_dir = Path(os.environ.get("ASSET_OUTPUT_DIR", Path(__file__).parent))
out = out_dir / "elevator.glb"
bpy.ops.export_scene.gltf(
    filepath=str(out),
    export_format='GLB',
    export_apply=True,
    export_image_format='NONE'
)
print(f"Exported: {out}")
print("Elevator asset complete.")
