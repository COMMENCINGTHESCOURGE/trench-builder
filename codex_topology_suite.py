bl_info = {
    "name": "Enhanced Topology Suite",
    "author": "Codex",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Topology Suite",
    "description": "GLB import validation, continuity overlays, cleanup-to-base, and unified topology guides.",
    "category": "Mesh",
}

import json
import math
from collections import Counter
from mathutils import Vector

import bpy
import bmesh
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty


CONTINUITY_ATTR = "ets_continuity"
FLOW_ATTR = "ets_flow_risk"
VALIDATION_PROP = "ets_validation_report"
TEMPLATE_COLLECTION = "ETS Unified Topology Guides"


def mesh_objects(context):
    return [obj for obj in context.selected_objects if obj.type == "MESH"]


def active_mesh(context):
    obj = context.object
    return obj if obj and obj.type == "MESH" else None


def ensure_object_mode():
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="OBJECT")


def edge_angle(edge):
    if len(edge.link_faces) != 2:
        return math.pi
    return edge.link_faces[0].normal.angle(edge.link_faces[1].normal, 0.0)


def vert_valence(vert):
    return len(vert.link_edges)


def edge_midpoint(edge):
    return sum((v.co for v in edge.verts), Vector()) / len(edge.verts)


def set_edge_bevel_weight(mesh, edge_indices, weight):
    attr = mesh.attributes.get("bevel_weight_edge")
    if attr is None:
        attr = mesh.attributes.new("bevel_weight_edge", "FLOAT", "EDGE")
    for idx in edge_indices:
        attr.data[idx].value = weight


def ensure_float_edge_attr(mesh, name):
    attr = mesh.attributes.get(name)
    if attr is None:
        attr = mesh.attributes.new(name, "FLOAT", "EDGE")
    return attr


def ensure_face_attr(mesh, name):
    attr = mesh.attributes.get(name)
    if attr is None:
        attr = mesh.attributes.new(name, "FLOAT_COLOR", "FACE")
    return attr


def material(obj, name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    if mat.name not in [slot.material.name for slot in obj.material_slots if slot.material]:
        obj.data.materials.append(mat)
    return list(obj.data.materials).index(mat)


def shade_faces_by_score(obj, face_scores, palette):
    indices = {
        key: material(obj, f"ETS {key}", color)
        for key, color in palette.items()
    }
    for polygon in obj.data.polygons:
        score = face_scores.get(polygon.index, 0.0)
        if score >= 0.75:
            polygon.material_index = indices["Break"]
        elif score >= 0.45:
            polygon.material_index = indices["G0/G1 Risk"]
        elif score >= 0.20:
            polygon.material_index = indices["G2 Drift"]
        else:
            polygon.material_index = indices["Continuous"]


def collect_validation(obj, pole_threshold, curvature_angle, flow_alignment):
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm.verts.index_update()
    bm.edges.index_update()
    bm.faces.index_update()
    bm.normal_update()

    non_manifold = [edge.index for edge in bm.edges if not edge.is_manifold]
    loose_verts = [vert.index for vert in bm.verts if not vert.link_edges]
    poles = [
        {"index": vert.index, "valence": vert_valence(vert)}
        for vert in bm.verts
        if vert_valence(vert) not in (4,) and vert_valence(vert) >= pole_threshold
    ]
    valences = Counter(vert_valence(vert) for vert in bm.verts)

    flow_risks = []
    for face in bm.faces:
        linked = set()
        for edge in face.edges:
            linked.update(edge.link_faces)
        linked.discard(face)
        if not linked:
            continue
        max_normal_delta = max(face.normal.angle(other.normal, 0.0) for other in linked)
        if max_normal_delta < curvature_angle:
            continue

        normal = face.normal.normalized()
        radial = (face.calc_center_median() - obj.location).normalized()
        if radial.length == 0:
            continue
        expected_flow = radial.cross(normal)
        if expected_flow.length == 0:
            continue
        expected_flow.normalize()
        for edge in face.edges:
            tangent = (edge.verts[1].co - edge.verts[0].co).normalized()
            alignment = abs(tangent.dot(expected_flow))
            if alignment < flow_alignment:
                flow_risks.append(
                    {
                        "face": face.index,
                        "edge": edge.index,
                        "alignment": round(alignment, 4),
                        "normal_delta_deg": round(math.degrees(max_normal_delta), 2),
                    }
                )

    sdf_compat = len(non_manifold) == 0 and len(loose_verts) == 0
    report = {
        "object": obj.name,
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "faces": len(mesh.polygons),
        "non_manifold_edges": non_manifold,
        "loose_vertices": loose_verts,
        "poles": poles,
        "valence_histogram": dict(sorted(valences.items())),
        "flow_risks": flow_risks,
        "sdf_compatible": sdf_compat,
        "summary": {
            "non_manifold_edge_count": len(non_manifold),
            "loose_vertex_count": len(loose_verts),
            "pole_count": len(poles),
            "flow_risk_count": len(flow_risks),
            "sdf_ready": sdf_compat,
        },
    }
    bm.free()

    flow_attr = ensure_float_edge_attr(mesh, FLOW_ATTR)
    for item in flow_attr.data:
        item.value = 0.0
    for risk in flow_risks:
        flow_attr.data[risk["edge"]].value = max(flow_attr.data[risk["edge"]].value, 1.0 - risk["alignment"])

    obj[VALIDATION_PROP] = json.dumps(report, indent=2)
    return report


def active_validation_summary(context):
    obj = active_mesh(context)
    if not obj or not obj.get(VALIDATION_PROP):
        return None
    return json.loads(obj[VALIDATION_PROP])["summary"]


def cleanup_target_faces(props):
    if props.cleanup_density == "LOW":
        return 3500
    if props.cleanup_density == "MEDIUM":
        return 12500
    if props.cleanup_density == "HIGH":
        return 40000
    return props.target_faces


def continuity_scores(obj, g1_limit, g2_limit, show_g0=True, show_g1=True, show_g2=True):
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bm.edges.index_update()
    bm.faces.index_update()
    bm.normal_update()

    face_scores = {}
    edge_scores = {}
    for edge in bm.edges:
        if len(edge.link_faces) < 2:
            score = 1.0 if show_g0 else 0.0
        elif len(edge.link_faces) > 2:
            score = 1.0 if show_g0 else 0.0
        else:
            base_angle = edge_angle(edge)
            adjacent_angles = []
            for face in edge.link_faces:
                for other_edge in face.edges:
                    if other_edge == edge or len(other_edge.link_faces) != 2:
                        continue
                    adjacent_angles.append(edge_angle(other_edge))
            g2_delta = max((abs(base_angle - angle) for angle in adjacent_angles), default=0.0)
            if base_angle > g1_limit:
                score = 0.70 + min(base_angle / math.pi, 0.30) if show_g1 else 0.0
            elif g2_delta > g2_limit:
                score = 0.35 + min(g2_delta / math.pi, 0.25) if show_g2 else 0.0
            else:
                score = min(base_angle / max(g1_limit, 0.001), 0.18)
        edge_scores[edge.index] = score
        for face in edge.link_faces:
            face_scores[face.index] = max(face_scores.get(face.index, 0.0), score)

    bm.free()

    attr = ensure_float_edge_attr(mesh, CONTINUITY_ATTR)
    for idx, score in edge_scores.items():
        attr.data[idx].value = score

    shade_faces_by_score(
        obj,
        face_scores,
        {
            "Continuous": (0.12, 0.72, 0.42, 1.0),
            "G2 Drift": (0.95, 0.74, 0.18, 1.0),
            "G0/G1 Risk": (1.0, 0.43, 0.18, 1.0),
            "Break": (0.9, 0.08, 0.12, 1.0),
        },
    )
    return edge_scores


class ETSProperties(bpy.types.PropertyGroup):
    glb_path: StringProperty(
        name="GLB Path",
        subtype="FILE_PATH",
        description="GLB/GLTF file to import and validate",
    )
    pole_threshold: IntProperty(
        name="Pole Valence",
        default=5,
        min=3,
        max=16,
        description="Vertices with valence at or above this count are reported as poles",
    )
    curvature_angle: FloatProperty(
        name="Curvature Angle",
        default=math.radians(12),
        min=math.radians(1),
        max=math.radians(90),
        subtype="ANGLE",
        description="Normal change threshold for curvature-critical surface detection",
    )
    flow_alignment: FloatProperty(
        name="Flow Alignment",
        default=0.28,
        min=0.0,
        max=1.0,
        description="Lower values catch fewer edge-flow direction mismatches",
    )
    check_non_manifold: BoolProperty(name="Non-Manifold Edges", default=True)
    check_loose_verts: BoolProperty(name="Loose Vertices", default=True)
    check_poles: BoolProperty(name="Pole Count", default=True)
    check_edge_flow: BoolProperty(name="Edge Flow Direction", default=True)
    check_sdf: BoolProperty(name="SDF Node Ready", default=True, description="Ensure mesh is watertight for Geometry Nodes SDF")
    continuity_type: EnumProperty(
        name="Continuity Type",
        items=[
            ("ALL", "All", "Show G0, G1, and G2 continuity risks"),
            ("G0", "G0 (Position)", "Show boundary and non-manifold breaks"),
            ("G1", "G1 (Tangent)", "Show tangent discontinuities"),
            ("G2", "G2 (Curvature)", "Show curvature drift"),
        ],
        default="ALL",
    )
    show_g0: BoolProperty(name="G0 (Position)", default=True)
    show_g1: BoolProperty(name="G1 (Tangent)", default=True)
    show_g2: BoolProperty(name="G2 (Curvature)", default=True)
    show_overlay: BoolProperty(name="Overlay", default=True)
    show_lines: BoolProperty(name="Lines", default=False)
    show_sharp_edges: BoolProperty(name="Sharp Edges", default=True)
    g1_limit: FloatProperty(
        name="G1 Limit",
        default=math.radians(7),
        min=math.radians(0.1),
        max=math.radians(80),
        subtype="ANGLE",
    )
    g2_limit: FloatProperty(
        name="G2 Limit",
        default=math.radians(5),
        min=math.radians(0.1),
        max=math.radians(80),
        subtype="ANGLE",
    )
    crease_angle: FloatProperty(
        name="Crease Angle",
        default=math.radians(35),
        min=math.radians(1),
        max=math.radians(120),
        subtype="ANGLE",
    )
    bevel_weight: FloatProperty(
        name="Bevel Weight",
        default=1.0,
        min=0.0,
        max=1.0,
    )
    cleanup_density: EnumProperty(
        name="Target Polycount",
        items=[
            ("LOW", "Low (2k - 5k)", "Fast base mesh for blocking"),
            ("MEDIUM", "Medium (5k - 20k)", "Balanced retopo starting point"),
            ("HIGH", "High (20k - 60k)", "Dense base preserving more source detail"),
            ("CUSTOM", "Custom", "Use the target face count below"),
        ],
        default="MEDIUM",
    )
    preserve_hard_edges: BoolProperty(name="Hard Edges", default=True)
    preserve_creases: BoolProperty(name="Creases", default=True)
    rebuild_quad_topology: BoolProperty(name="Quad Topology", default=True)
    rebuild_edge_flow: BoolProperty(name="Edge Flow", default=True)
    rebuild_bevel_weights: BoolProperty(name="Bevel Weights", default=True)
    use_quadriflow: BoolProperty(
        name="Quad Remesh",
        default=False,
        description="Run Blender's Quadriflow remesher after cleanup when available",
    )
    target_faces: IntProperty(
        name="Target Faces",
        default=6000,
        min=100,
        max=500000,
    )
    template_mode: EnumProperty(
        name="Template",
        items=[
            ("HYBRID", "Hybrid", "Hard-surface panels plus organic deformation loops"),
            ("CHARACTER", "Character", "Organic body continuity loops"),
            ("VEHICLE", "Vehicle", "Hard-surface panel and armor flow"),
        ],
        default="HYBRID",
    )
    template_panel_tank: BoolProperty(name="Tank", default=True)
    template_panel_fairing: BoolProperty(name="Fairing", default=True)
    template_panel_seat: BoolProperty(name="Seat", default=True)
    template_panel_exhaust: BoolProperty(name="Exhaust", default=True)
    template_panel_wheels: BoolProperty(name="Wheels", default=True)
    symmetry_x: BoolProperty(name="X", default=True)
    symmetry_y: BoolProperty(name="Y", default=False)
    symmetry_z: BoolProperty(name="Z", default=False)
    voxel_path: StringProperty(
        name="Voxel Path",
        subtype="FILE_PATH",
        description="JSON manifest containing voxel density to import",
        default="soil_tensor_manifest.json",
    )


class ETS_OT_import_voxel_manifest(bpy.types.Operator):
    bl_idname = "ets.import_voxel_manifest"
    bl_label = "Import Voxel Manifest Mesh"
    bl_description = "Convert 3D voxel density channel from JSON manifest into a polygonal mesh"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        import numpy as np
        props = context.scene.ets_props
        if not props.voxel_path:
            self.report({"ERROR"}, "Please choose a Voxel Path first.")
            return {"CANCELLED"}

        filepath = bpy.path.abspath(props.voxel_path)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.report({"ERROR"}, f"Failed to read file: {e}")
            return {"CANCELLED"}

        if "channels" not in data or "density" not in data["channels"]:
            self.report({"ERROR"}, "Invalid JSON manifest: density channel missing.")
            return {"CANCELLED"}

        density = data["channels"]["density"]
        density_arr = np.array(density)
        nz, ny, nx = density_arr.shape

        # Resolve diagonal checkerboard contacts to ensure manifoldness
        solid = (density_arr >= 0.2)
        # 1. Z-axis edges (dx=1, dy=1, dz=0)
        for z in range(nz):
            for y in range(ny - 1):
                for x in range(nx - 1):
                    if solid[z, y, x] and solid[z, y+1, x+1]:
                        if not solid[z, y+1, x] and not solid[z, y, x+1]:
                            density_arr[z, y+1, x] = 0.2
                            solid[z, y+1, x] = True
                    if solid[z, y, x+1] and solid[z, y+1, x]:
                        if not solid[z, y, x] and not solid[z, y+1, x+1]:
                            density_arr[z, y, x] = 0.2
                            solid[z, y, x] = True
                            
        # 2. Y-axis edges (dx=1, dy=0, dz=1)
        for z in range(nz - 1):
            for y in range(ny):
                for x in range(nx - 1):
                    if solid[z, y, x] and solid[z+1, y, x+1]:
                        if not solid[z+1, y, x] and not solid[z, y, x+1]:
                            density_arr[z+1, y, x] = 0.2
                            solid[z+1, y, x] = True
                    if solid[z, y, x+1] and solid[z+1, y, x]:
                        if not solid[z, y, x] and not solid[z+1, y, x+1]:
                            density_arr[z, y, x] = 0.2
                            solid[z, y, x] = True

        # 3. X-axis edges (dx=0, dy=1, dz=1)
        for z in range(nz - 1):
            for y in range(ny - 1):
                for x in range(nx):
                    if solid[z, y, x] and solid[z+1, y+1, x]:
                        if not solid[z+1, y, x] and not solid[z, y+1, x]:
                            density_arr[z+1, y, x] = 0.2
                            solid[z+1, y, x] = True
                    if solid[z, y+1, x] and solid[z+1, y, x]:
                        if not solid[z, y, x] and not solid[z+1, y+1, x]:
                            density_arr[z, y, x] = 0.2
                            solid[z, y, x] = True

        mesh_name = "Voxelized_SIMP_Mesh"
        mesh_data = bpy.data.meshes.new(mesh_name)
        obj = bpy.data.objects.new(mesh_name, mesh_data)
        context.collection.objects.link(obj)

        bm = bmesh.new()
        vert_map = {}

        def get_vert(x_c, y_c, z_c):
            key = (x_c, y_c, z_c)
            if key not in vert_map:
                vert_map[key] = bm.verts.new((x_c, y_c, z_c))
            return vert_map[key]

        for z in range(nz):
            for y in range(ny):
                for x in range(nx):
                    if density_arr[z, y, x] >= 0.2:
                        v0 = get_vert(x,     y,     z)
                        v1 = get_vert(x + 1, y,     z)
                        v2 = get_vert(x + 1, y + 1, z)
                        v3 = get_vert(x,     y + 1, z)
                        v4 = get_vert(x,     y,     z + 1)
                        v5 = get_vert(x + 1, y,     z + 1)
                        v6 = get_vert(x + 1, y + 1, z + 1)
                        v7 = get_vert(x,     y + 1, z + 1)

                        faces_to_add = []
                        
                        if z == 0 or density_arr[z-1, y, x] < 0.2:
                            faces_to_add.append((v3, v2, v1, v0))
                        if z == nz - 1 or density_arr[z+1, y, x] < 0.2:
                            faces_to_add.append((v4, v5, v6, v7))
                        if x == 0 or density_arr[z, y, x-1] < 0.2:
                            faces_to_add.append((v0, v3, v7, v4))
                        if x == nx - 1 or density_arr[z, y, x+1] < 0.2:
                            faces_to_add.append((v1, v5, v6, v2))
                        if y == 0 or density_arr[z, y-1, x] < 0.2:
                            faces_to_add.append((v0, v4, v5, v1))
                        if y == ny - 1 or density_arr[z, y+1, x] < 0.2:
                            faces_to_add.append((v2, v6, v7, v3))

                        for f_verts in faces_to_add:
                            try:
                                bm.faces.new(f_verts)
                            except ValueError:
                                pass

        bm.to_mesh(mesh_data)
        bm.free()

        context.view_layer.objects.active = obj
        obj.select_set(True)
        
        self.report({"INFO"}, f"Successfully imported voxel mesh: {nx}x{ny}x{nz} grid.")
        return {"FINISHED"}


class ETS_OT_import_validate(bpy.types.Operator):
    bl_idname = "ets.import_validate_glb"
    bl_label = "Import And Validate GLB"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.ets_props
        if not props.glb_path:
            self.report({"ERROR"}, "Choose a GLB/GLTF path first.")
            return {"CANCELLED"}

        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=bpy.path.abspath(props.glb_path))
        imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
        if not imported:
            self.report({"ERROR"}, "No mesh objects were imported.")
            return {"CANCELLED"}

        totals = Counter()
        for obj in imported:
            report = collect_validation(
                obj,
                props.pole_threshold,
                props.curvature_angle,
                props.flow_alignment,
            )
            totals.update(report["summary"])
        self.report(
            {"INFO"},
            "Validated %d mesh(es): %d non-manifold, %d loose, %d poles, %d flow risks. SDF Ready: %s"
            % (
                len(imported),
                totals["non_manifold_edge_count"],
                totals["loose_vertex_count"],
                totals["pole_count"],
                totals["flow_risk_count"],
                str(bool(totals["sdf_ready"])),
            ),
        )
        return {"FINISHED"}


class ETS_OT_validate_selected(bpy.types.Operator):
    bl_idname = "ets.validate_selected"
    bl_label = "Validate Selected Meshes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.ets_props
        objects = mesh_objects(context)
        if not objects:
            self.report({"ERROR"}, "Select at least one mesh.")
            return {"CANCELLED"}
        totals = Counter()
        for obj in objects:
            report = collect_validation(obj, props.pole_threshold, props.curvature_angle, props.flow_alignment)
            totals.update(report["summary"])
        self.report(
            {"INFO"},
            "Validation: %d non-manifold, %d loose, %d poles, %d flow risks. SDF Ready: %s"
            % (
                totals["non_manifold_edge_count"],
                totals["loose_vertex_count"],
                totals["pole_count"],
                totals["flow_risk_count"],
                str(bool(totals["sdf_ready"])),
            ),
        )
        return {"FINISHED"}


class ETS_OT_export_report(bpy.types.Operator):
    bl_idname = "ets.export_validation_report"
    bl_label = "Export Validation Report"
    bl_options = {"REGISTER"}

    filepath: StringProperty(name="Report Path", subtype="FILE_PATH", default="//ets_validation_report.json")

    def execute(self, context):
        reports = []
        for obj in mesh_objects(context):
            raw = obj.get(VALIDATION_PROP)
            if raw:
                reports.append(json.loads(raw))
        if not reports:
            self.report({"ERROR"}, "No validation reports found on selected meshes.")
            return {"CANCELLED"}
        path = bpy.path.abspath(self.filepath)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(reports, handle, indent=2)
        self.report({"INFO"}, f"Exported {path}")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ETS_OT_continuity_overlay(bpy.types.Operator):
    bl_idname = "ets.continuity_overlay"
    bl_label = "Visualize G0/G1/G2"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.ets_props
        obj = active_mesh(context)
        if not obj:
            self.report({"ERROR"}, "Select an active mesh.")
            return {"CANCELLED"}
        ensure_object_mode()
        show_g0 = props.show_g0 and props.continuity_type in {"ALL", "G0"}
        show_g1 = props.show_g1 and props.continuity_type in {"ALL", "G1"}
        show_g2 = props.show_g2 and props.continuity_type in {"ALL", "G2"}
        scores = continuity_scores(obj, props.g1_limit, props.g2_limit, show_g0, show_g1, show_g2)
        if props.show_overlay:
            obj.show_in_front = True
        break_count = sum(1 for score in scores.values() if score >= 0.75)
        drift_count = sum(1 for score in scores.values() if 0.20 <= score < 0.75)
        self.report({"INFO"}, f"Continuity overlay: {break_count} breaks, {drift_count} drift/risk edges")
        return {"FINISHED"}


class ETS_OT_cleanup_to_base(bpy.types.Operator):
    bl_idname = "ets.cleanup_to_base"
    bl_label = "Cleanup To Base Topology"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.ets_props
        obj = active_mesh(context)
        if not obj:
            self.report({"ERROR"}, "Select an active mesh.")
            return {"CANCELLED"}

        ensure_object_mode()
        context.view_layer.objects.active = obj
        obj.select_set(True)

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.mesh.delete_loose()
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        bm.edges.index_update()
        bm.faces.index_update()
        bm.normal_update()
        crease_edges = [
            edge.index
            for edge in bm.edges
            if props.preserve_hard_edges and edge_angle(edge) >= props.crease_angle
        ]
        for edge in bm.edges:
            edge.smooth = edge.index not in crease_edges
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()

        if props.rebuild_bevel_weights and props.preserve_creases:
            set_edge_bevel_weight(obj.data, crease_edges, props.bevel_weight)

        if props.use_quadriflow and props.rebuild_quad_topology and hasattr(bpy.ops.object, "quadriflow_remesh"):
            bpy.ops.object.quadriflow_remesh(target_faces=cleanup_target_faces(props))

        if props.rebuild_bevel_weights and props.preserve_creases:
            bevel = obj.modifiers.get("ETS Crease Bevel") or obj.modifiers.new("ETS Crease Bevel", "BEVEL")
            bevel.width = 0.01
            bevel.segments = 1
            bevel.affect = "EDGES"
            bevel.limit_method = "WEIGHT"

        if props.rebuild_edge_flow:
            normal = obj.modifiers.get("ETS Weighted Normals") or obj.modifiers.new("ETS Weighted Normals", "WEIGHTED_NORMAL")
            normal.keep_sharp = True

        obj["ets_cleanup_result"] = json.dumps(
            {
                "vertices": len(obj.data.vertices),
                "faces": len(obj.data.polygons),
                "target_faces": cleanup_target_faces(props),
                "crease_edges": len(crease_edges),
            },
            indent=2,
        )

        self.report({"INFO"}, f"Cleanup complete. Preserved {len(crease_edges)} crease edges as bevel weights.")
        return {"FINISHED"}


class ETS_OT_apply_template_guides(bpy.types.Operator):
    bl_idname = "ets.apply_template_guides"
    bl_label = "Create Unified Template Guides"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.ets_props
        obj = active_mesh(context)
        if not obj:
            self.report({"ERROR"}, "Select an active mesh.")
            return {"CANCELLED"}

        collection = bpy.data.collections.get(TEMPLATE_COLLECTION)
        if collection is None:
            collection = bpy.data.collections.new(TEMPLATE_COLLECTION)
            context.scene.collection.children.link(collection)

        bounds = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        center = sum(bounds, Vector()) / 8.0
        size = max((max(v[i] for v in bounds) - min(v[i] for v in bounds)) for i in range(3))
        radius = max(size * 0.42, 0.1)

        base_specs = {
            "VEHICLE": [
                ("fairing_panel_belt", (0, 0, 0), "XY", "template_panel_fairing"),
                ("wheel_arch", (0, 0, 0.22), "XZ", "template_panel_wheels"),
                ("tank_crease_break", (0, 0, -0.18), "XY", "template_panel_tank"),
                ("seat_transition", (0, 0, 0.36), "XY", "template_panel_seat"),
                ("exhaust_flow", (0, 0, -0.34), "YZ", "template_panel_exhaust"),
            ],
            "CHARACTER": [
                ("torso_loop", (0, 0, 0), "XY", "template_panel_fairing"),
                ("shoulder_hip_loop", (0, 0, 0.25), "XZ", "template_panel_tank"),
                ("deformation_ring", (0, 0, -0.22), "YZ", "template_panel_seat"),
            ],
            "HYBRID": [
                ("primary_flow", (0, 0, 0), "XY", "template_panel_fairing"),
                ("deformation_flow", (0, 0, 0.25), "XZ", "template_panel_tank"),
                ("panel_crease_flow", (0, 0, -0.22), "YZ", "template_panel_seat"),
                ("transition_loop", (0, 0, 0.45), "XY", "template_panel_wheels"),
                ("exhaust_mechanical_flow", (0, 0, -0.38), "YZ", "template_panel_exhaust"),
            ],
        }[props.template_mode]
        guide_specs = [spec for spec in base_specs if getattr(props, spec[3])]

        for name, offset, plane, _enabled_prop in guide_specs:
            curve = bpy.data.curves.new(f"ETS {name}", "CURVE")
            curve.dimensions = "3D"
            curve.resolution_u = 12
            spline = curve.splines.new("POLY")
            spline.points.add(63)
            for idx, point in enumerate(spline.points):
                angle = (idx / 64.0) * math.tau
                x = math.cos(angle) * radius
                y = math.sin(angle) * radius
                z = 0.0
                if plane == "XZ":
                    y, z = z, y
                elif plane == "YZ":
                    x, z = z, x
                co = center + Vector((x + offset[0], y + offset[1], z + offset[2] * size))
                point.co = (co.x, co.y, co.z, 1.0)
            curve.bevel_depth = size * 0.0025
            curve_obj = bpy.data.objects.new(curve.name, curve)
            collection.objects.link(curve_obj)

        obj["ets_template_mode"] = props.template_mode
        obj["ets_template_symmetry"] = ",".join(
            axis for axis, enabled in (("X", props.symmetry_x), ("Y", props.symmetry_y), ("Z", props.symmetry_z)) if enabled
        )
        obj["ets_template_notes"] = (
            "Guides mark reusable loop intent: primary flow, deformation continuity, hard creases, and transition loops."
        )
        self.report({"INFO"}, f"Created {len(guide_specs)} {props.template_mode.lower()} topology guide curves.")
        return {"FINISHED"}


class ETS_PT_topology_suite(bpy.types.Panel):
    bl_label = "Topology Suite"
    bl_idname = "ETS_PT_topology_suite"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Topology Suite"

    def draw(self, context):
        layout = self.layout
        props = context.scene.ets_props
        summary = active_validation_summary(context)
        obj = active_mesh(context)

        box = layout.box()
        box.label(text="A) Enhanced Import Pipeline", icon="CHECKMARK")
        row = box.row(align=True)
        row.operator("ets.import_validate_glb", text="Import GLB", icon="IMPORT")
        row.prop(props, "glb_path", text="")
        check_box = box.box()
        check_box.label(text="Validation Checks")
        check_box.prop(props, "check_non_manifold")
        check_box.prop(props, "check_loose_verts")
        check_box.prop(props, "check_poles")
        check_box.prop(props, "check_edge_flow")
        check_box.prop(props, "check_sdf")
        row = box.row(align=True)
        row.prop(props, "pole_threshold")
        row.prop(props, "flow_alignment")
        box.prop(props, "curvature_angle")
        box.operator("ets.validate_selected", text="Run All Checks", icon="CHECKMARK")
        if summary:
            report_box = box.box()
            report_box.label(text="Report")
            if props.check_non_manifold:
                report_box.label(text=f"Non-Manifold Edges: {summary['non_manifold_edge_count']}")
            if props.check_loose_verts:
                report_box.label(text=f"Loose Vertices: {summary['loose_vertex_count']}")
            if props.check_poles:
                report_box.label(text=f"Poles ({props.pole_threshold}+): {summary['pole_count']}")
            if props.check_edge_flow:
                flow_text = "Consistent" if summary["flow_risk_count"] == 0 else f"{summary['flow_risk_count']} risks"
                report_box.label(text=f"Edge Flow: {flow_text}")
            if props.check_sdf:
                report_box.label(text="SDF Geometry Ready: YES" if summary['sdf_ready'] else "SDF Geometry Ready: NO (Needs watertight mesh)")
            passed = (
                (not props.check_non_manifold or summary["non_manifold_edge_count"] == 0)
                and (not props.check_loose_verts or summary["loose_vertex_count"] == 0)
                and (not props.check_edge_flow or summary["flow_risk_count"] == 0)
                and (not props.check_sdf or summary["sdf_ready"])
            )
            report_box.label(text="VALIDATION PASSED" if passed else "VALIDATION NEEDS REVIEW", icon="CHECKMARK" if passed else "ERROR")
        box.operator("ets.export_validation_report", text="Export Report", icon="EXPORT")

        box = layout.box()
        box.label(text="B) Continuity Analyzer", icon="MOD_WIREFRAME")
        box.prop(props, "continuity_type")
        vis = box.box()
        vis.label(text="Visualization")
        vis.prop(props, "show_g0")
        vis.prop(props, "show_g1")
        vis.prop(props, "show_g2")
        display = box.box()
        display.label(text="Display")
        display.prop(props, "show_overlay")
        display.prop(props, "show_lines")
        display.prop(props, "show_sharp_edges")
        row = box.row(align=True)
        row.prop(props, "g1_limit", text="G1")
        row.prop(props, "g2_limit", text="G2")
        box.operator("ets.continuity_overlay", text="Update", icon="COLOR")

        box = layout.box()
        box.label(text="C) Mesh Cleanup-to-Base", icon="MESH_CUBE")
        box.prop(props, "cleanup_density")
        preserve = box.box()
        preserve.label(text="Preserve")
        preserve.prop(props, "preserve_hard_edges")
        preserve.prop(props, "preserve_creases")
        rebuild = box.box()
        rebuild.label(text="Reconstruct")
        rebuild.prop(props, "rebuild_quad_topology")
        rebuild.prop(props, "rebuild_edge_flow")
        rebuild.prop(props, "rebuild_bevel_weights")
        box.prop(props, "crease_angle")
        box.prop(props, "bevel_weight")
        box.prop(props, "use_quadriflow")
        if props.use_quadriflow or props.cleanup_density == "CUSTOM":
            box.prop(props, "target_faces")
        box.operator("ets.cleanup_to_base", text="Cleanup & Rebuild", icon="MODIFIER")
        if obj and obj.get("ets_cleanup_result"):
            result = json.loads(obj["ets_cleanup_result"])
            result_box = box.box()
            result_box.label(text="Result")
            result_box.label(text=f"Vertices: {result['vertices']}")
            result_box.label(text=f"Faces: {result['faces']}")
            result_box.label(text=f"Crease Edges: {result['crease_edges']}")

        box = layout.box()
        box.label(text="D) Character/Vehicle Unified Template", icon="OUTLINER_OB_ARMATURE")
        box.prop(props, "template_mode")
        panels = box.box()
        panels.label(text="Panels")
        panels.prop(props, "template_panel_tank")
        panels.prop(props, "template_panel_fairing")
        panels.prop(props, "template_panel_seat")
        panels.prop(props, "template_panel_exhaust")
        panels.prop(props, "template_panel_wheels")
        sym = box.box()
        sym.label(text="Symmetry")
        sym.prop(props, "symmetry_x")
        sym.prop(props, "symmetry_y")
        sym.prop(props, "symmetry_z")
        box.operator("ets.apply_template_guides", text="Generate Template", icon="CURVE_DATA")

        box = layout.box()
        box.label(text="E) Voxel Tensor Optimization Bridge", icon="CUBE")
        row = box.row(align=True)
        row.operator("ets.import_voxel_manifest", text="Import Voxel Mesh", icon="MESH_CUBE")
        row.prop(props, "voxel_path", text="")


classes = (
    ETSProperties,
    ETS_OT_import_validate,
    ETS_OT_validate_selected,
    ETS_OT_export_report,
    ETS_OT_continuity_overlay,
    ETS_OT_cleanup_to_base,
    ETS_OT_apply_template_guides,
    ETS_OT_import_voxel_manifest,
    ETS_PT_topology_suite,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.ets_props = bpy.props.PointerProperty(type=ETSProperties)


def unregister():
    del bpy.types.Scene.ets_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
