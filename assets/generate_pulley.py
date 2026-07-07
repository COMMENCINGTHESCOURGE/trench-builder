"""
PARAMETRIC PULLEY GENERATOR — V-belt, flat crowned, and timing-belt pulleys.
Run inside Blender: Scripting workspace → Open → Run Script.
Exports: pulley_{type}.glb to the same directory.

Pulley types:
  - vbelt: V-belt pulley with trapezoidal grooves (38° standard)
  - flat_crowned: Flat belt pulley with slight crown for belt tracking
  - timing: Timing belt pulley with trapezoidal teeth (GT2 profile)

Mechanical parameters:
  - Pitch diameter: effective diameter at belt neutral axis
  - Groove angle: V-belt wedge angle (34-40°, standard 38°)
  - Number of grooves: for multi-belt V-belt pulleys
"""
import bpy
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from material_library import get_material

# ── Clean scene ─────────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ── Pulley Parameters (edit these) ──────────────────────────────
PULLEY_TYPE = "vbelt"           # "vbelt", "flat_crowned", or "timing"
PITCH_DIAMETER = 120.0          # mm — effective diameter at belt neutral axis
BORE_RADIUS = 12.0              # mm — shaft hole
FACE_WIDTH = 35.0               # mm — total pulley width along axis
HUB_RADIUS = 22.0               # mm — hub boss
HUB_OFFSET = 10.0               # mm — hub extension beyond face each side
KEYWAY_WIDTH = 6.0              # mm
KEYWAY_DEPTH = 4.0              # mm

# V-belt specific
V_GROOVE_ANGLE = 38.0           # degrees — wedge angle
V_GROOVE_DEPTH = 12.0           # mm — depth of each groove
V_NUM_GROOVES = 3               # number of belt grooves

# Flat crowned specific
CROWN_HEIGHT = 0.8              # mm — center rise above edge

# Timing belt specific
TIMING_TEETH = 40               # number of teeth
TIMING_PITCH = 2.0              # mm — tooth pitch (GT2 = 2mm)


# ── Helper functions ────────────────────────────────────────────

def revolve_profile(profile_points_2d, axis=(0, 0, 1), segments=64):
    """Create a solid of revolution from a 2D profile in XZ plane."""
    import bmesh

    # profile_points_2d are (r, z) pairs
    verts_3d = []
    faces = []
    n_profile = len(profile_points_2d)

    for i in range(segments):
        angle = 2 * math.pi * i / segments
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        for r, z in profile_points_2d:
            verts_3d.append((r * cos_a, r * sin_a, z))

    for i in range(segments):
        for j in range(n_profile - 1):
            v0 = i * n_profile + j
            v1 = i * n_profile + j + 1
            v2 = ((i + 1) % segments) * n_profile + j + 1
            v3 = ((i + 1) % segments) * n_profile + j
            faces.append((v0, v1, v2, v3))

    mesh = bpy.data.meshes.new("Pulley_Mesh")
    mesh.from_pydata(verts_3d, [], faces)
    mesh.update()

    obj = bpy.data.objects.new("Pulley", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def add_bore_and_keyway(target_obj):
    """Boolean-difference a bore hole and keyway into the target."""
    total_depth = FACE_WIDTH + 2 * HUB_OFFSET + 4

    # Bore
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=BORE_RADIUS, depth=total_depth,
        location=(0, 0, FACE_WIDTH / 2)
    )
    bore = bpy.context.active_object
    bore.name = "Bore_Cutter"

    bpy.context.view_layer.objects.active = target_obj
    mod = target_obj.modifiers.new(name="Bore", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = bore
    bpy.ops.object.modifier_apply(modifier="Bore")
    bpy.data.objects.remove(bore)

    # Keyway
    if KEYWAY_WIDTH > 0:
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(BORE_RADIUS + KEYWAY_DEPTH / 2, 0, FACE_WIDTH / 2)
        )
        key = bpy.context.active_object
        key.name = "Keyway_Cutter"
        key.scale = (KEYWAY_DEPTH / 2, KEYWAY_WIDTH / 2, total_depth / 2)
        bpy.ops.object.transform_apply(scale=True)

        bpy.context.view_layer.objects.active = target_obj
        mod = target_obj.modifiers.new(name="Keyway", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = key
        bpy.ops.object.modifier_apply(modifier="Keyway")
        bpy.data.objects.remove(key)

    return target_obj


# ── V-Belt Pulley ───────────────────────────────────────────────

def build_vbelt_pulley():
    """V-belt pulley with trapezoidal grooves revolved around Z axis."""
    r_inner = PITCH_DIAMETER / 2 - V_GROOVE_DEPTH
    r_pitch = PITCH_DIAMETER / 2
    r_outer = r_pitch + V_GROOVE_DEPTH * 0.15  # Slight crown above pitch
    groove_angle_rad = math.radians(V_GROOVE_ANGLE / 2)

    # Build 2D profile (r, z) in XZ plane
    # Profile goes from z=0 to z=FACE_WIDTH, with grooves cut in
    profile = []

    # Bottom edge: hub surface
    profile.append((r_inner - 2, 0))
    profile.append((r_outer, 0))

    groove_width = (FACE_WIDTH - 6) / V_NUM_GROOVES  # minus margins
    margin = 3.0

    for g in range(V_NUM_GROOVES):
        z_center = margin + groove_width / 2 + g * groove_width
        z_left = z_center - groove_width * 0.35
        z_right = z_center + groove_width * 0.35
        groove_half_w = (groove_width * 0.35) * math.tan(groove_angle_rad)

        # Profile: outer → down groove wall → bottom of groove → up groove wall → outer
        profile.append((r_outer, z_left))
        profile.append((r_pitch - groove_half_w, z_center))
        profile.append((r_outer, z_right))

    profile.append((r_outer, FACE_WIDTH))
    profile.append((r_inner - 2, FACE_WIDTH))

    print("Building V-belt pulley...")
    obj = revolve_profile(profile, segments=64)
    obj = add_bore_and_keyway(obj)
    obj.data.materials.append(get_material("cast_iron"))
    obj.name = f"Pulley_VBelt_{int(PITCH_DIAMETER)}mm_{V_NUM_GROOVES}gr"
    return obj


# ── Flat Crowned Pulley ─────────────────────────────────────────

def build_flat_crowned_pulley():
    """Flat belt pulley with crowned center for self-tracking."""
    r_base = PITCH_DIAMETER / 2
    r_crown = r_base + CROWN_HEIGHT

    # Profile with parabolic-like crown
    profile = []
    n_segments = 20
    for i in range(n_segments + 1):
        z = i * FACE_WIDTH / n_segments
        # Crown profile: parabolic rise from edges to center
        t = 2 * abs(z - FACE_WIDTH / 2) / FACE_WIDTH  # 0 at center, 1 at edges
        r = r_base + CROWN_HEIGHT * (1 - t * t)
        profile.append((r, z))

    # Add hub flanges
    profile.insert(0, (r_base - 3, 0))
    profile.append((r_base - 3, FACE_WIDTH))

    print("Building flat crowned pulley...")
    obj = revolve_profile(profile, segments=64)
    obj = add_bore_and_keyway(obj)
    obj.data.materials.append(get_material("cast_iron"))
    obj.name = f"Pulley_FlatCrowned_{int(PITCH_DIAMETER)}mm"
    return obj


# ── Timing Pulley ───────────────────────────────────────────────

def build_timing_pulley():
    """Timing belt pulley with trapezoidal teeth (GT2 profile).
    Uses constructive solid geometry approach: cylinder base + tooth extrusion."""
    r_pitch = TIMING_TEETH * TIMING_PITCH / (2 * math.pi)
    r_root = r_pitch - 1.0    # GT2: tooth height ~1.0mm
    tooth_height = 1.35       # GT2 tooth height
    tooth_width = 1.4         # GT2 tooth width at tip
    tooth_base_width = 1.9    # GT2 tooth width at base

    print(f"Building timing pulley: {TIMING_TEETH} teeth, "
          f"pitch_diameter={2 * r_pitch:.1f}mm")

    # Base cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64, radius=r_root, depth=FACE_WIDTH,
        location=(0, 0, FACE_WIDTH / 2)
    )
    base = bpy.context.active_object
    base.name = "Timing_Pulley_Base"

    # Add teeth as individual meshes merged via boolean
    angular_pitch = 2 * math.pi / TIMING_TEETH
    for i in range(TIMING_TEETH):
        angle = i * angular_pitch
        x = r_pitch * math.cos(angle)
        y = r_pitch * math.sin(angle)

        # Trapezoidal tooth (small box approximation)
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x, y, FACE_WIDTH / 2),
            rotation=(0, 0, angle)
        )
        tooth = bpy.context.active_object
        tooth.name = f"Tooth_{i}"
        tooth.scale = (tooth_height / 2, tooth_width / 2, FACE_WIDTH / 2)
        bpy.ops.object.transform_apply(scale=True)

        # Union with base
        bpy.context.view_layer.objects.active = base
        mod = base.modifiers.new(name=f"Tooth_{i}_Union", type='BOOLEAN')
        mod.operation = 'UNION'
        mod.object = tooth
        bpy.ops.object.modifier_apply(modifier=f"Tooth_{i}_Union")
        bpy.data.objects.remove(tooth)

    base = add_bore_and_keyway(base)
    base.data.materials.append(get_material("aluminum_brushed"))
    base.name = f"Pulley_Timing_{TIMING_TEETH}t_GT2"
    return base


# ── Build ───────────────────────────────────────────────────────

if PULLEY_TYPE == "vbelt":
    obj = build_vbelt_pulley()
    out_name = f"pulley_vbelt_{int(PITCH_DIAMETER)}mm_{V_NUM_GROOVES}gr.glb"
elif PULLEY_TYPE == "flat_crowned":
    obj = build_flat_crowned_pulley()
    out_name = f"pulley_flat_{int(PITCH_DIAMETER)}mm.glb"
elif PULLEY_TYPE == "timing":
    obj = build_timing_pulley()
    out_name = f"pulley_timing_{TIMING_TEETH}t_GT2.glb"
else:
    raise ValueError(f"Unknown pulley type: {PULLEY_TYPE}")

# ── Export ──────────────────────────────────────────────────────
out_dir = Path(os.environ.get("ASSET_OUTPUT_DIR", Path(__file__).parent))
out = out_dir / out_name
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath=str(out),
    export_format='GLB',
    export_apply=True,
    export_image_format='NONE'
)
print(f"Exported: {out}")
print("Pulley asset complete.")
