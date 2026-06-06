"""
PURPLE / BROWN FREIGHT ELEVATOR — Alternate color scheme for franchise localization.

Changes from default:
 - Steel tones shifted to purple-plated (anodized) and rust-brown (weathered)
 - Floor plate becomes dark brown (iron oxide)
 - Guardrails purple
 - Chains brown
 - Concrete base unchanged
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
    bsdf.inputs["Roughness"].default_value = 0.6
    bsdf.inputs["Metallic"].default_value = 0.95
    return mat

def concrete_material(name="Concrete"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.35, 0.33, 0.30, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    bsdf.inputs["Metallic"].default_value = 0.0
    return mat

steel_dark = steel_material("Steel_Dark", (0.35, 0.15, 0.45, 1.0))   # purple-plated dark
steel_med  = steel_material("Steel_Med",  (0.55, 0.25, 0.65, 1.0))   # purple-plated medium
steel_light = steel_material("Steel_Light", (0.75, 0.45, 0.85, 1.0))  # purple-plated light
chain_mat  = steel_material("Chain",      (0.30, 0.20, 0.10, 1.0))   # rust-brown chain
plate_mat  = steel_material("Plate",      (0.40, 0.28, 0.18, 1.0))   # iron oxide floor
concrete   = concrete_material()

# ── Dimensions (meters) ─────────────────────────────────────────
CAGE_W = 2.8    # Wider than passenger (2.0)
CAGE_D = 2.2    # Deeper
CAGE_H = 3.2    # Taller interior
SHAFT_H = 5.0   # Total travel height
PLATFORM_H = 0.20
RAIL_H = 1.2    # Higher guardrail
FRAME_THICK = 0.10
FLOOR_Y = 0.20

# ── Helpers ─────────────────────────────────────────────────────
def add_cube(name, location, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    bpy.ops.object.transform_apply(scale=True)
    return obj

def add_cylinder(name, location, radius, depth, rotation, material, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, location=location,
        rotation=rotation, vertices=vertices
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

# ── 1. Base Plate (heavy duty) ─────────────────────────────────
def build_base():
    add_cube("Base_Plate", (0, 0, FLOOR_Y - 0.15),
             (CAGE_W/2 + 0.3, CAGE_D/2 + 0.3, 0.15), concrete)
    # Steel edge trim
    for x_sign in (-1, 1):
        add_cube(f"Base_Edge_X{x_sign}", (x_sign*(CAGE_W/2 + 0.1), 0, FLOOR_Y - 0.05),
                 (0.08, CAGE_D/2 + 0.2, 0.08), steel_med)
    for y_sign in (-1, 1):
        add_cube(f"Base_Edge_Y{y_sign}", (0, y_sign*(CAGE_D/2 + 0.1), FLOOR_Y - 0.05),
                 (CAGE_W/2 + 0.2, 0.08, 0.08), steel_med)

# ── 2. Open Cage Frame (no side panels) ────────────────────────
def build_cage_frame():
    # Four corner posts, taller
    for x in (-CAGE_W/2, CAGE_W/2):
        for y in (-CAGE_D/2, CAGE_D/2):
            add_cube(f"Post_{x:.1f}_{y:.1f}",
                     (x, y, FLOOR_Y + CAGE_H/2),
                     (FRAME_THICK, FRAME_THICK, CAGE_H/2), steel_dark)

    # Top header beam
    h = FLOOR_Y + CAGE_H
    add_cube("Header_X", (0, CAGE_D/2, h),
             (CAGE_W/2 + FRAME_THICK, FRAME_THICK, FRAME_THICK), steel_med)
    add_cube("Header_Y", (0, -CAGE_D/2, h),
             (CAGE_W/2 + FRAME_THICK, FRAME_THICK, FRAME_THICK), steel_med)

    # Cross-bracing — X face only (front is open, back is solid)
    for y_sign in (-1, 1):  # back face only
        y = y_sign * CAGE_D/2
        for i in range(4):
            z0 = FLOOR_Y + i * (CAGE_H / 4)
            z1 = z0 + CAGE_H / 4
            for x_dir in (-1, 1):
                x0 = -x_dir * CAGE_W/2
                x1 = x_dir * CAGE_W/2
                cx = (x0 + x1) / 2
                cz = (z0 + z1) / 2
                dx = abs(x1 - x0)
                dz = abs(z1 - z0)
                length = math.sqrt(dx**2 + dz**2)
                angle = math.atan2(dx, dz)
                add_cube(f"Brace_{y_sign}_{i}_{x_dir}",
                         (cx, y, cz),
                         (FRAME_THICK*0.7, FRAME_THICK*0.7, length/2), steel_dark)
                bpy.context.active_object.rotation_euler = (0, angle, 0)

# ── 3. Forklift-Grade Floor Plating ────────────────────────────
def build_floor():
    # Main plate
    add_cube("Floor_Plate", (0, 0, FLOOR_Y + PLATFORM_H/2),
             (CAGE_W/2 - FRAME_THICK, CAGE_D/2 - FRAME_THICK, PLATFORM_H/2), plate_mat)

    # Tread pattern — raised ribs
    rib_count = 6
    rib_w = 0.06
    rib_h = 0.02
    spacing = (CAGE_W - 0.4) / rib_count
    for i in range(rib_count):
        x = -CAGE_W/2 + 0.2 + i * spacing + spacing/2
        add_cube(f"Rib_{i}", (x, 0, FLOOR_Y + PLATFORM_H + rib_h/2),
                 (rib_w/2, CAGE_D/2 - 0.1, rib_h/2), steel_light)

# ── 4. Guardrails (three sides, front open) ─────────────────────
def build_guardrails():
    rail_top = FLOOR_Y + CAGE_H
    mid_z = FLOOR_Y + RAIL_H * 0.6

    # Front (Y+) — open, just a mid-rail for safety
    add_cube("Rail_Front", (0, CAGE_D/2 - FRAME_THICK*0.5, mid_z),
             (CAGE_W/2 - FRAME_THICK*2, FRAME_THICK*0.4, FRAME_THICK*0.4), steel_med)

    # Left side (X-)
    add_cube("Rail_Left_Top", (-CAGE_W/2 + FRAME_THICK*0.5, 0, rail_top),
             (FRAME_THICK*0.4, CAGE_D/2 - FRAME_THICK, FRAME_THICK*0.4), steel_light)
    add_cube("Rail_Left_Mid", (-CAGE_W/2 + FRAME_THICK*0.5, 0, mid_z),
             (FRAME_THICK*0.4, CAGE_D/2 - FRAME_THICK, FRAME_THICK*0.4), steel_med)

    # Right side (X+)
    add_cube("Rail_Right_Top", (CAGE_W/2 - FRAME_THICK*0.5, 0, rail_top),
             (FRAME_THICK*0.4, CAGE_D/2 - FRAME_THICK, FRAME_THICK*0.4), steel_light)
    add_cube("Rail_Right_Mid", (CAGE_W/2 - FRAME_THICK*0.5, 0, mid_z),
             (FRAME_THICK*0.4, CAGE_D/2 - FRAME_THICK, FRAME_THICK*0.4), steel_med)

    # Back side (Y-)
    add_cube("Rail_Back_Top", (0, -CAGE_D/2 + FRAME_THICK*0.5, rail_top),
             (CAGE_W/2 - FRAME_THICK*2, FRAME_THICK*0.4, FRAME_THICK*0.4), steel_light)
    add_cube("Rail_Back_Mid", (0, -CAGE_D/2 + FRAME_THICK*0.5, mid_z),
             (CAGE_W/2 - FRAME_THICK*2, FRAME_THICK*0.4, FRAME_THICK*0.4), steel_med)

# ── 5. Overhead Trolley / Jib ──────────────────────────────────
def build_trolley():
    # Trolley beam spanning top front
    trolley_y = CAGE_D/2 + 0.4
    trolley_z = FLOOR_Y + CAGE_H + 0.3

    # Main beam
    add_cube("Trolley_Beam", (0, trolley_y, trolley_z),
             (CAGE_W/2 + 0.2, 0.12, 0.12), steel_med)

    # Trolley carriage
    for x_sign in (-1, 1):
        add_cube(f"Trolley_Carriage_{x_sign}",
                 (x_sign * CAGE_W * 0.3, trolley_y, trolley_z),
                 (0.15, 0.2, 0.2), steel_light)

    # Jib arm extending forward (for loading)
    jib_x = 0
    jib_y = trolley_y + 0.6
    jib_z = trolley_z - 0.3
    add_cube("Jib_Arm", (jib_x, jib_y, jib_z),
             (0.08, 0.8, 0.08), steel_dark)

    # Hook block
    add_cylinder("Hook_Block", (jib_x, jib_y + 0.5, jib_z - 0.2),
                 0.08, 0.15, (math.pi/2, 0, 0), chain_mat)

# ── 6. Heavy-Duty Chain Drives ──────────────────────────────────
def build_chains():
    # Chains on both sides, thicker than passenger cables
    chain_z = FLOOR_Y + CAGE_H * 0.3
    chain_y = CAGE_D/2 + 0.15

    for x_sign in (-1, 1):
        x = x_sign * (CAGE_W/2 - 0.1)
        # Upper run
        add_cylinder(f"Chain_Upper_{x_sign}", (x, chain_y, FLOOR_Y + CAGE_H - 0.3),
                     0.04, 0.6, (0, math.pi/2, 0), chain_mat, vertices=8)
        # Lower run
        add_cylinder(f"Chain_Lower_{x_sign}", (x, chain_y, FLOOR_Y + 0.3),
                     0.04, 0.6, (0, math.pi/2, 0), chain_mat, vertices=8)

    # Drive sprocket at top
    add_cylinder("Drive_Sprocket", (0, CAGE_D/2 + 0.1, FLOOR_Y + CAGE_H + 0.1),
                 0.2, 0.1, (math.pi/2, 0, 0), steel_dark, vertices=12)

# ── 7. Field-Responsive FracType Panel ──────────────────────────
def build_fracfield_panel():
    """Side panel with a small display showing eigenmode state (decorative)."""
    panel_x = -CAGE_W/2 - 0.05
    panel_z = 1.5
    add_cube("Frac_Panel", (panel_x, 0, panel_z),
             (0.03, 0.4, 0.25), steel_light)

    # Screen inset
    screen_x = panel_x - 0.02
    add_cube("Frac_Screen", (screen_x, 0, panel_z + 0.05),
             (0.01, 0.25, 0.12), steel_dark)

# ── 8. Build All ────────────────────────────────────────────────
print("Building freight elevator...")
build_base()
build_cage_frame()
build_floor()
build_guardrails()
build_trolley()
build_chains()
build_fracfield_panel()

# ── Export ──────────────────────────────────────────────────────
out_dir = Path(os.environ.get("ASSET_OUTPUT_DIR", Path(__file__).parent))
out = out_dir / "freight_elevator_purple_brown.glb"
bpy.ops.export_scene.gltf(
    filepath=str(out),
    export_format='GLB',
    export_apply=True,
    export_image_format='NONE'
)
print(f"Exported: {out}")
print("Freight elevator asset complete.")
