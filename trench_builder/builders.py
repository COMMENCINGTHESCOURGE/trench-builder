"""
Trench-Builder: Parametric Geometry Builder (Blender Python).
Consumes AssemblySpec, produces GLB + manifest with embedded metadata.
"""
import bpy
import bmesh
import json
import math
from typing import Dict, Any, Optional
from pathlib import Path
from mathutils import Vector

from .core import AssemblySpec, ComponentSpec, JointType


class ReverseEngineerableBuilder:
    """Builds geometry from AssemblySpec, embedding the spec as custom properties."""

    def __init__(self):
        self.built_objects: Dict[str, Any] = {}
        self.armature = None

    def build_assembly(self, spec: AssemblySpec, clear_scene: bool = True) -> Dict[str, Any]:
        """Build all components, establish hierarchy, apply constraints."""
        if clear_scene:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()

        self.built_objects.clear()

        # Create armature
        bpy.ops.object.armature_add(location=(0, 0, 0))
        self.armature = bpy.context.active_object
        self.armature.name = f"Rig_{spec.model_id}"

        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = self.armature.data.edit_bones
        edit_bones.remove(edit_bones[0])

        # Build bones
        bone_map = {}
        for comp in spec.components:
            bone = edit_bones.new(f"Bone_{comp.name}")
            bone.head = Vector((0, 0, 0))
            bone.tail = Vector((0, 0, 1))

            if comp.parent:
                parent_bone = edit_bones.get(f"Bone_{comp.parent}")
                if parent_bone:
                    bone.parent = parent_bone
                    bone.head = parent_bone.tail
                    bone.tail = bone.head + Vector((0, 0, 1))

            bone_map[comp.name] = bone

        bpy.ops.object.mode_set(mode='OBJECT')

        # Embed global metadata
        self.armature["trench_builder_spec"] = spec.to_json()
        self.armature["trench_builder_version"] = "3.0_modular"
        self.armature["model_id"] = spec.model_id
        self.armature["domain"] = spec.domain

        for comp in spec.components:
            self.armature[f"component_{comp.name}"] = json.dumps(comp.to_dict())

        self._apply_pose_constraints(spec)

        return self.built_objects

    def _apply_pose_constraints(self, spec: AssemblySpec):
        """Apply angle limits as Limit Rotation constraints in pose mode."""
        bpy.context.view_layer.objects.active = self.armature
        bpy.ops.object.mode_set(mode='POSE')

        for comp in spec.components:
            bone_name = f"Bone_{comp.name}"
            pose_bone = self.armature.pose.bones.get(bone_name)
            if not pose_bone or not comp.joint_limits:
                continue

            constraint = pose_bone.constraints.new(type='LIMIT_ROTATION')
            constraint.owner_space = 'LOCAL'
            constraint.use_limit_x = True
            constraint.use_limit_y = True
            constraint.use_limit_z = True

            min_val, max_val = comp.joint_limits
            min_rad, max_rad = math.radians(min_val), math.radians(max_val)

            axis = comp.joint_axis or "Z"
            if axis == "X":
                constraint.min_x, constraint.max_x = min_rad, max_rad
            elif axis == "Y":
                constraint.min_y, constraint.max_y = min_rad, max_rad
            else:
                constraint.min_z, constraint.max_z = min_rad, max_rad

        bpy.ops.object.mode_set(mode='OBJECT')

    def export_glb(self, output_path: str) -> str:
        """Export armature as GLB."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        bpy.ops.object.select_all(action='DESELECT')
        self.armature.select_set(True)
        bpy.context.view_layer.objects.active = self.armature

        bpy.ops.export_scene.gltf(
            filepath=str(output_path),
            use_selection=True,
            export_apply=True,
            export_animations=False,
        )
        return str(output_path)

    def export_manifest(self, spec: AssemblySpec, output_path: str) -> str:
        """Export JSON manifest in Unity-consumer format."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        joints = []
        for comp in spec.components:
            joint = {
                "name": comp.name,
                "type": comp.joint_type.value,
                "axis": comp.joint_axis or "Z",
                "limits": {
                    "min_x_deg": 0, "max_x_deg": 0,
                    "min_y_deg": 0, "max_y_deg": 0,
                    "min_z_deg": 0, "max_z_deg": 0,
                },
                "friction_coefficient": 0.15,
                "connected_to": comp.parent or "Root",
            }
            if comp.joint_limits and comp.joint_type == JointType.REVOLUTE:
                axis = comp.joint_axis or "Z"
                if axis == "X":
                    joint["limits"]["min_x_deg"] = comp.joint_limits[0]
                    joint["limits"]["max_x_deg"] = comp.joint_limits[1]
                elif axis == "Y":
                    joint["limits"]["min_y_deg"] = comp.joint_limits[0]
                    joint["limits"]["max_y_deg"] = comp.joint_limits[1]
                else:
                    joint["limits"]["min_z_deg"] = comp.joint_limits[0]
                    joint["limits"]["max_z_deg"] = comp.joint_limits[1]
            if comp.gear_spec:
                joint["drive_ratio"] = comp.gear_spec.get("drive_ratio", 1.0)
                joint["inertia_kg_m2"] = comp.gear_spec.get("inertia", 0.0004)
                if comp.gear_spec.get("driven_by"):
                    joint["driven_by"] = comp.gear_spec["driven_by"]
            joints.append(joint)

        manifest = {
            "model_id": spec.model_id,
            "domain": spec.domain,
            "joints": joints,
            "com_offset_mm": {"x": 0, "y": 0, "z": 0},
            "material": spec.metadata.get("material", "PLA"),
            "tolerance_mm": spec.metadata.get("tolerance_mm", 0.25),
        }
        if spec.global_vinculum:
            manifest["global_vinculum"] = spec.global_vinculum.to_dict()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return str(output_path)

    @staticmethod
    def reverse_engineer(armature_obj: Any) -> Optional[AssemblySpec]:
        """Extract original spec from a built armature's custom properties."""
        if "trench_builder_spec" not in armature_obj:
            return None
        return AssemblySpec.from_json(armature_obj["trench_builder_spec"])
