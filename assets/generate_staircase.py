"""
STAIRCASE ASSET GENERATOR — Industrial steel staircase for Trench Builder.
Run inside Blender: Scripting workspace → Open → Run Script.
Exports: staircase.glb to the same directory.

Design: Steel C-channel stringers, checkered tread plates (individual steps),
pipe handrails with stanchions, top landing platform, bolt/rivet details.
Construction-site aesthetic — exposed structure, raw steel, utilitarian.
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

steel_dark  = steel_material("Steel_Dark",  (0.15, 0.14, 0.13, 1.0))
steel_med   = steel_material("Steel_Med",   (0.28, 0.27, 0.25, 1.0))
steel_light = steel_material("Steel_Light", (0.45, 0.43, 0.40, 1.0))
tread_mat   = steel_material("Tread",        (0.35, 0.30, 0.22, 1.0))
pipe_mat    = steel_material("Pipe",         (0.22, 0.21, 0.19, 1.0))

# ── Dimensions (meters) ─────────────────────────────────────────
TOTAL_RISE = 3.0     # Total vertical height
NUM_STEPS = 14       # Number of steps
RISE = TOTAL_RISE / NUM_STEPS      # Per-step rise (~0.214m)
RUN = 0.28           # Tread depth (going)
WIDTH = 1.2          # Stair width (clear between stringers)
STRINGER_H = 0.25    # Stringer beam height
STRINGER_T = 0.06    # Stringer thickness
TREAD_T = 0.04       # Tread plate thickness
LANDING_L = 1.5      # Landing platform length at top
LANDING_W = WIDTH    # Landing width
RAIL_H = 1.1         # Handrail height above tread nosing
POST_RADIUS = 0.02   # Stanchion radius
RAIL_RADIUS = 0.022  # Handrail pipe radius


# ── Helper functions ────────────────────────────────────────────
def add_cube(name, location, scale, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = rotation
    obj.data.materials.append(material)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.transform_apply(rotation=True)
    return obj

def add_cylinder(name, location, radius, depth, rotation, material, vertices=12):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, location=location,
        rotation=rotation, vertices=vertices
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj


# ── 1. Stringers ────────────────────────────────────────────────
def build_stringers():
    """Two C-channel stringers (left and right) with zigzag top profile."""
    for side in (-1, 1):
        x = side * (WIDTH / 2 + STRINGER_T / 2)
        y_center = NUM_STEPS * RUN / 2

        add_cube(f"Stringer_{side}",
                 (x, y_center, STRINGER_H / 2),
                 (STRINGER_T / 2, NUM_STEPS * RUN / 2, STRINGER_H / 2),
                 steel_dark)

        # Bottom flange plate
        add_cube(f"Stringer_Flange_{side}",
                 (x, y_center, 0.02),
                 (STRINGER_T / 2 + 0.02, NUM_STEPS * RUN / 2, 0.015),
                 steel_med)


# ── 2. Treads ───────────────────────────────────────────────────
def build_treads():
    """Individual checkered tread plates with nose overhang."""
    for i in range(NUM_STEPS):
        z = i * RISE + TREAD_T / 2
        y = i * RUN
        # Main tread plate
        add_cube(f"Tread_{i}",
                 (0, y + RUN * 0.45, z),
                 (WIDTH / 2, RUN / 2 - 0.01, TREAD_T / 2),
                 tread_mat)

        # Nose overhang (front lip)
        add_cube(f"Tread_Nose_{i}",
                 (0, y + RUN - 0.01, z),
                 (WIDTH / 2, 0.015, TREAD_T / 2 + 0.005),
                 steel_light)

        # Tread support bracket (under tread, welded to stringer)
        add_cube(f"Tread_Bracket_{i}",
                 (0, y + RUN * 0.45, z - TREAD_T / 2 - 0.015),
                 (WIDTH / 2 - 0.02, 0.015, 0.02),
                 steel_dark)


# ── 3. Handrail Posts (Stanchions) ──────────────────────────────
def build_stanchions():
    """Vertical stanchions at each tread nose, both sides."""
    for i in range(NUM_STEPS + 1):  # +1 for post at landing
        z_base = i * RISE if i < NUM_STEPS else NUM_STEPS * RISE
        y = i * RUN
        z_top = z_base + RAIL_H

        for side in (-1, 1):
            x = side * (WIDTH / 2)

            # Main post
            add_cylinder(f"Post_{i}_{side}",
                         (x, y, (z_base + z_top) / 2),
                         POST_RADIUS, RAIL_H,
                         (0, 0, 0), pipe_mat)

            # Base plate (flange where post meets tread/stringer)
            add_cube(f"Post_Flange_{i}_{side}",
                     (x, y, z_base + 0.01),
                     (0.04, 0.04, 0.012), steel_dark)


# ── 4. Handrails ────────────────────────────────────────────────
def build_handrails():
    """Continuous pipe handrails following the stair pitch."""
    angle = math.atan2(RISE, RUN)  # Stair pitch angle

    for side in (-1, 1):
        x = side * (WIDTH / 2)

        # Top rail — follows stair angle
        for i in range(NUM_STEPS):
            z0 = i * RISE + RAIL_H
            z1 = (i + 1) * RISE + RAIL_H
            y0 = i * RUN
            y1 = (i + 1) * RUN
            cy = (y0 + y1) / 2
            cz = (z0 + z1) / 2

            # Rail segment (approximated as cylinder along the pitch)
            seg_len = math.sqrt(RUN**2 + RISE**2)
            add_cylinder(f"Rail_Top_{side}_{i}",
                         (x, cy, cz),
                         RAIL_RADIUS, seg_len,
                         (math.pi/2, 0, angle),
                         pipe_mat)

        # Mid rail
        mid_h = RAIL_H * 0.55
        for i in range(NUM_STEPS):
            z0 = i * RISE + mid_h
            z1 = (i + 1) * RISE + mid_h
            y0 = i * RUN
            y1 = (i + 1) * RUN
            cy = (y0 + y1) / 2
            cz = (z0 + z1) / 2
            seg_len = math.sqrt(RUN**2 + RISE**2)
            add_cylinder(f"Rail_Mid_{side}_{i}",
                         (x, cy, cz),
                         RAIL_RADIUS * 0.8, seg_len,
                         (math.pi/2, 0, angle),
                         pipe_mat)

        # Horizontal continuation onto landing
        land_y_start = NUM_STEPS * RUN
        land_y_end = land_y_start + LANDING_L
        land_z = NUM_STEPS * RISE + RAIL_H
        land_cy = (land_y_start + land_y_end) / 2

        add_cylinder(f"Rail_Landing_Top_{side}",
                     (x, land_cy, land_z),
                     RAIL_RADIUS, LANDING_L,
                     (math.pi/2, math.pi/2, 0),
                     pipe_mat)
        add_cylinder(f"Rail_Landing_Mid_{side}",
                     (x, land_cy, land_z - RAIL_H * 0.45),
                     RAIL_RADIUS * 0.8, LANDING_L,
                     (math.pi/2, math.pi/2, 0),
                     pipe_mat)


# ── 5. Top Landing ──────────────────────────────────────────────
def build_landing():
    """Platform at the top of the stairs."""
    land_y = NUM_STEPS * RUN + LANDING_L / 2
    land_z = NUM_STEPS * RISE + 0.04

    # Landing platform
    add_cube("Landing_Deck", (0, land_y, land_z),
             (WIDTH / 2, LANDING_L / 2, TREAD_T / 2), tread_mat)

    # Support frame under landing (two cross beams)
    support_y = NUM_STEPS * RUN + LANDING_L * 0.25
    add_cube("Landing_Beam_1", (0, support_y, land_z - TREAD_T / 2 - 0.06),
             (WIDTH / 2, 0.04, 0.06), steel_dark)
    support_y2 = NUM_STEPS * RUN + LANDING_L * 0.75
    add_cube("Landing_Beam_2", (0, support_y2, land_z - TREAD_T / 2 - 0.06),
             (WIDTH / 2, 0.04, 0.06), steel_dark)

    # Landing posts (extend from last tread to landing edge)
    land_y_edge = NUM_STEPS * RUN + LANDING_L
    for side in (-1, 1):
        x = side * (WIDTH / 2)
        add_cylinder(f"Landing_Post_{side}",
                     (x, land_y_edge, land_z + RAIL_H / 2),
                     POST_RADIUS, RAIL_H,
                     (0, 0, 0), pipe_mat)


# ── 6. Bolts / Rivets (detail elements) ─────────────────────────
def build_rivets():
    """Decorative bolt heads on stringer connections."""
    for i in range(0, NUM_STEPS + 1, 2):  # Every other step
        y = i * RUN
        for side in (-1, 1):
            x = side * (WIDTH / 2 + STRINGER_T / 2)
            for v_offset in (-0.08, 0.08):
                # Bolt head on stringer
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=0.012, depth=0.02,
                    location=(x, y + v_offset, STRINGER_H * 0.7),
                    rotation=(math.pi/2, 0, 0), vertices=6
                )
                obj = bpy.context.active_object
                obj.name = f"Bolt_{i}_{side}_{v_offset}"
                obj.data.materials.append(steel_light)


# ── 7. Concrete Base Strips ─────────────────────────────────────
def build_base_strips():
    """Concrete footings under stringers."""
    for side in (-1, 1):
        x = side * (WIDTH / 2 + STRINGER_T / 2)
        y_center = NUM_STEPS * RUN / 2
        # Simple concrete strip
        add_cylinder("Concrete_Strip", (x, y_center, -0.05),
                     0.08, NUM_STEPS * RUN + 0.5,
                     (math.pi/2, math.pi/2, 0),
                     steel_dark, vertices=4)
        # Override material to look like concrete
        obj = bpy.context.active_object
        mat = bpy.data.materials.new(name="Concrete")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.35, 0.33, 0.30, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.85
        bsdf.inputs["Metallic"].default_value = 0.0
        obj.data.materials.clear()
        obj.data.materials.append(mat)


# ── Build ───────────────────────────────────────────────────────
print("Building staircase...")
build_stringers()
build_treads()
build_stanchions()
build_handrails()
build_landing()
build_rivets()
build_base_strips()

# ── Export to GLB ───────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
out_dir = Path(os.environ.get("ASSET_OUTPUT_DIR", Path(__file__).parent))
out = out_dir / "staircase.glb"
bpy.ops.export_scene.gltf(
    filepath=str(out),
    export_format='GLB',
    export_apply=True,
    export_image_format='NONE'
)
print(f"Exported: {out}")
print("Staircase asset complete.")
