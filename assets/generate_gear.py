"""
PARAMETRIC GEAR GENERATOR — Involute spur gear with proper tooth profile.
Run inside Blender: Scripting workspace → Open → Run Script.
Exports: gear_{module}m_{teeth}t.glb to the same directory.

Mechanical parameters:
  - Module (m): tooth size in mm per tooth. Standard values: 1, 1.5, 2, 2.5, 3, 4, 5
  - Teeth (N): number of teeth. Minimum ~12 for 20° pressure angle before undercut
  - Pressure angle (φ): 20° standard, 14.5° for finer mesh, 25° for higher strength
  - Face width: gear thickness along axis
  - Bore diameter: center hole for shaft

Profile: Involute curve from base circle, with addendum/dedendum, root fillet.
"""
import bpy
import math
import os
import sys
from pathlib import Path

# Add parent for material library
sys.path.insert(0, str(Path(__file__).parent))
from material_library import get_material

# ── Clean scene ─────────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ── Gear Parameters (edit these) ────────────────────────────────
MODULE = 3.0              # Tooth module (mm)
TEETH = 24                # Number of teeth
PRESSURE_ANGLE = 20.0     # Degrees (standard: 20)
FACE_WIDTH = 20.0         # Gear thickness along axis (mm)
BORE_RADIUS = 8.0         # Center shaft hole (mm)
HUB_RADIUS = 14.0         # Hub boss radius (mm)
HUB_HEIGHT = 8.0          # Hub boss height beyond face (mm each side)
KEYWAY_WIDTH = 5.0        # Keyway slot width (mm), set 0 for none
KEYWAY_DEPTH = 3.0        # Keyway depth into hub (mm)
ADDENDUM_FACTOR = 1.0     # Standard: 1.0 × module
DEDENDUM_FACTOR = 1.25    # Standard: 1.25 × module
FILLET_RADIUS = 0.38      # Root fillet radius × module
SEGMENTS_PER_TOOTH = 24   # Curve resolution per tooth face

# ── Derived parameters ──────────────────────────────────────────
PITCH_RADIUS = MODULE * TEETH / 2
BASE_RADIUS = PITCH_RADIUS * math.cos(math.radians(PRESSURE_ANGLE))
ADDENDUM = ADDENDUM_FACTOR * MODULE
DEDENDUM = DEDENDUM_FACTOR * MODULE
OUTER_RADIUS = PITCH_RADIUS + ADDENDUM
ROOT_RADIUS = PITCH_RADIUS - DEDENDUM
FILLET_R = FILLET_RADIUS * MODULE
ANGULAR_PITCH = 2 * math.pi / TEETH

print(f"Gear: module={MODULE}, teeth={TEETH}, pitch_radius={PITCH_RADIUS:.2f}")
print(f"  base_radius={BASE_RADIUS:.3f}, outer={OUTER_RADIUS:.2f}, root={ROOT_RADIUS:.2f}")


# ── Involute profile ────────────────────────────────────────────

def involute_point(t, r_b):
    """Point on involute curve at parameter t from base circle radius r_b."""
    x = r_b * (math.cos(t) + t * math.sin(t))
    y = r_b * (math.sin(t) - t * math.cos(t))
    return (x, y)

def tooth_profile_points():
    """Generate (x, y) points for one tooth profile — both flanks + tip arc + root."""
    points = []

    # Angle to tooth centerline
    tooth_half_angle = ANGULAR_PITCH / 2

    # Involute parameter range (starts at base circle, goes to outer radius)
    t_max = math.sqrt(max(0, (OUTER_RADIUS / BASE_RADIUS)**2 - 1))
    t_start = 0.0  # Involute starts at base circle

    # Number of points on the involute flank
    t_vals = [t_start + i * t_max / SEGMENTS_PER_TOOTH
              for i in range(SEGMENTS_PER_TOOTH + 1)]

    # Right flank (from base circle to tip)
    right_pts = []
    for t in t_vals:
        x, y = involute_point(t, BASE_RADIUS)
        ang = math.atan2(y, x) - tooth_half_angle
        r = math.sqrt(x*x + y*y)
        right_pts.append((r * math.cos(ang), r * math.sin(ang)))

    # Radial line from root circle to base circle (right side)
    if ROOT_RADIUS < BASE_RADIUS:
        # Angle at base circle for right flank
        bx, by = involute_point(t_start, BASE_RADIUS)
        bang = math.atan2(by, bx) - tooth_half_angle
        points.append((ROOT_RADIUS * math.cos(bang), ROOT_RADIUS * math.sin(bang)))
        # Fillet arc at root
        fa_start = bang
        fa_end = -tooth_half_angle + ANGULAR_PITCH
        for i in range(5):
            a = fa_start + i * (fa_end - fa_start) / 4
            points.append((ROOT_RADIUS * math.cos(a), ROOT_RADIUS * math.sin(a)))
    else:
        points.append((ROOT_RADIUS * math.cos(tooth_half_angle + ANGULAR_PITCH * 0.3),
                       ROOT_RADIUS * math.sin(tooth_half_angle + ANGULAR_PITCH * 0.3)))

    points.extend(right_pts)

    # Tip arc (across top of tooth)
    n_tip = 7
    for i in range(n_tip):
        a = tooth_half_angle - i * (2 * tooth_half_angle) / (n_tip - 1)
        points.append((OUTER_RADIUS * math.cos(-a),
                       OUTER_RADIUS * math.sin(-a)))

    # Left flank (from tip to base circle)
    left_pts = []
    for t in reversed(t_vals):
        x, y = involute_point(t, BASE_RADIUS)
        ang = math.atan2(y, x) + tooth_half_angle
        r = math.sqrt(x*x + y*y)
        left_pts.append((r * math.cos(ang), r * math.sin(ang)))
    points.extend(left_pts)

    # Radial line from base circle to root (left side)
    if ROOT_RADIUS < BASE_RADIUS:
        bx, by = involute_point(t_start, BASE_RADIUS)
        bang = math.atan2(by, bx) + tooth_half_angle
        points.append((ROOT_RADIUS * math.cos(bang), ROOT_RADIUS * math.sin(bang)))

    # Root arc back to next tooth
    fa_start = -tooth_half_angle
    fa_end = -tooth_half_angle + ANGULAR_PITCH
    for i in range(6):
        a = fa_start + i * (fa_end - fa_start) / 5
        points.append((ROOT_RADIUS * math.cos(a), ROOT_RADIUS * math.sin(a)))

    return points


def build_gear_profile():
    """Create the 2D gear profile curve for all teeth."""
    all_verts = []
    all_edges = []

    tooth_pts = tooth_profile_points()
    pts_per_tooth = len(tooth_pts)

    for tooth_idx in range(TEETH):
        angle_offset = tooth_idx * ANGULAR_PITCH
        cos_a = math.cos(angle_offset)
        sin_a = math.sin(angle_offset)
        for x, y in tooth_pts:
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            all_verts.append((rx, ry, 0))

        base = tooth_idx * pts_per_tooth
        for i in range(pts_per_tooth - 1):
            all_edges.append((base + i, base + i + 1))
        # Close tooth
        all_edges.append((base + pts_per_tooth - 1, base))

    # Create mesh from profile
    mesh = bpy.data.meshes.new("Gear_Profile")
    mesh.from_pydata(all_verts, all_edges, [])
    mesh.update()

    # Create face from the profile outline
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Find boundary edges and fill
    bmesh.ops.triangle_fill(bm, edges=bm.edges[:])
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Gear_Profile", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ── 3D Gear Body ────────────────────────────────────────────────

def build_gear_body(profile_obj):
    """Extrude the profile into a 3D gear with hub and bore."""
    # Extrude profile to face width
    bpy.context.view_layer.objects.active = profile_obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # Extrude along Z
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={"value": (0, 0, FACE_WIDTH)}
    )
    bpy.ops.object.mode_set(mode='OBJECT')

    # Apply material
    profile_obj.data.materials.append(get_material("gear_steel_oiled"))
    profile_obj.name = f"Gear_{MODULE}m_{TEETH}t"

    return profile_obj


def build_hub(gear_obj):
    """Add hub boss to both sides of the gear."""
    # Hub cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=HUB_RADIUS,
        depth=FACE_WIDTH + 2 * HUB_HEIGHT,
        location=(0, 0, FACE_WIDTH / 2)
    )
    hub = bpy.context.active_object
    hub.name = "Hub"
    hub.data.materials.append(get_material("gear_steel_oiled"))

    # Boolean join with gear
    bpy.context.view_layer.objects.active = gear_obj
    mod = gear_obj.modifiers.new(name="Hub_Union", type='BOOLEAN')
    mod.operation = 'UNION'
    mod.object = hub
    bpy.ops.object.modifier_apply(modifier="Hub_Union")
    bpy.data.objects.remove(hub)

    # Bore hole
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=BORE_RADIUS,
        depth=FACE_WIDTH + 2 * HUB_HEIGHT + 2,
        location=(0, 0, FACE_WIDTH / 2)
    )
    bore = bpy.context.active_object
    bore.name = "Bore"

    bpy.context.view_layer.objects.active = gear_obj
    mod = gear_obj.modifiers.new(name="Bore_Diff", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.ops.object.modifier_apply(modifier="Bore_Diff")
    bpy.data.objects.remove(bore)

    # Keyway slot
    if KEYWAY_WIDTH > 0:
        kw = KEYWAY_WIDTH / 2
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(BORE_RADIUS + KEYWAY_DEPTH / 2, 0, FACE_WIDTH / 2)
        )
        key = bpy.context.active_object
        key.name = "Keyway"
        key.scale = (KEYWAY_DEPTH / 2, kw, FACE_WIDTH + 2 * HUB_HEIGHT + 2)
        bpy.ops.object.transform_apply(scale=True)

        bpy.context.view_layer.objects.active = gear_obj
        mod = gear_obj.modifiers.new(name="Keyway_Diff", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = key
        bpy.ops.object.modifier_apply(modifier="Keyway_Diff")
        bpy.data.objects.remove(key)

    return gear_obj


# ── Build ───────────────────────────────────────────────────────
print("Building involute gear...")
profile = build_gear_profile()
gear = build_gear_body(profile)
gear = build_hub(gear)

# ── Export ──────────────────────────────────────────────────────
out_dir = Path(os.environ.get("ASSET_OUTPUT_DIR", Path(__file__).parent))
out = out_dir / f"gear_{MODULE:.0f}m_{TEETH}t.glb"
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath=str(out),
    export_format='GLB',
    export_apply=True,
    export_image_format='NONE'
)
print(f"Exported: {out}")
print("Gear asset complete.")
