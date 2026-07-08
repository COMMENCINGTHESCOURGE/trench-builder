"""
Trench-Builder Core: ComponentSpec and AssemblySpec.

The declarative specification layer. A ComponentSpec describes a single
modular part. An AssemblySpec collects them into a complete model.

Serialization: to_dict() / from_dict() with YAML and JSON support.
Reverse engineering: AssemblySpec.to_json() embeds the full blueprint.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import json
import yaml

from .vinculum import JointType, Vinculum, Constraint


@dataclass
class ComponentSpec:
    """
    Declarative specification of a single modular part.
    
    Attributes:
        name: Unique component identifier (e.g., "left_arm", "head")
        component_type: Category (e.g., "limb", "torso", "head", "gear")
        parent: Name of parent component in the hierarchy
        joint_type: How this component connects to its parent
        joint_axis: Axis of rotation/movement if not FIXED
        joint_limits: (min, max) in degrees for REVOLUTE/HINGE joints
        vinculum: Constraint set governing this component
        parameters: Domain-specific geometry params (length, radius, scale...)
        mount_points: Named attachment locations on this component
        tags: Searchable labels
    """
    name: str
    component_type: str = "generic"
    parent: Optional[str] = None
    joint_type: JointType = JointType.FIXED
    joint_axis: Optional[str] = None       # "X", "Y", "Z"
    joint_limits: Optional[tuple] = None   # (min_deg, max_deg)
    vinculum: Optional[Vinculum] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    mount_points: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    # Surface attachment for decals/badges — projects onto parent geometry
    surface_normal: Optional[List[float]] = None       # [nx, ny, nz] projection direction
    projection_mode: Optional[str] = None              # "shrinkwrap" | "uv_decal" | "planar"
    surface_conformity: float = 0.0                    # 0.0 = flat, 1.0 = full surface conform

    def to_dict(self) -> dict:
        d = asdict(self)
        d["joint_type"] = self.joint_type.value
        if self.vinculum:
            d["vinculum"] = self.vinculum.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "ComponentSpec":
        jt = JointType(data.get("joint_type", "fixed"))
        vinc = None
        if data.get("vinculum"):
            vinc = Vinculum.from_dict(data["vinculum"])
        return cls(
            name=data["name"],
            component_type=data.get("component_type", "generic"),
            parent=data.get("parent"),
            joint_type=jt,
            joint_axis=data.get("joint_axis"),
            joint_limits=tuple(data["joint_limits"]) if data.get("joint_limits") else None,
            vinculum=vinc,
            parameters=data.get("parameters", {}),
            mount_points=data.get("mount_points", []),
            tags=data.get("tags", []),
            surface_normal=data.get("surface_normal"),
            projection_mode=data.get("projection_mode"),
            surface_conformity=data.get("surface_conformity", 0.0),
        )

    def validate_against_vinculum(self, measurements: Dict[str, float]) -> List[str]:
        """Check measurements against this component's vinculum constraints."""
        if self.vinculum is None:
            return []
        return self.vinculum.get_failures(measurements)


@dataclass
class AssemblySpec:
    """
    A collection of components forming a complete modular model.
    
    Attributes:
        model_id: Unique identifier for this assembly
        domain: Domain namespace (character, ship, building, mecha...)
        components: Ordered list of ComponentSpec objects
        global_vinculum: Cross-component constraints (e.g., proportions)
        metadata: Freeform key-value tags
        version: Schema version for forward compatibility
    """
    model_id: str
    domain: str = "generic"
    components: List[ComponentSpec] = field(default_factory=list)
    global_vinculum: Optional[Vinculum] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"

    def add_component(self, comp: ComponentSpec) -> "AssemblySpec":
        self.components.append(comp)
        return self

    def get_component(self, name: str) -> Optional[ComponentSpec]:
        for c in self.components:
            if c.name == name:
                return c
        return None

    def get_children(self, parent_name: str) -> List[ComponentSpec]:
        return [c for c in self.components if c.parent == parent_name]

    def get_root(self) -> Optional[ComponentSpec]:
        """Return the root component (one with no parent)."""
        roots = [c for c in self.components if c.parent is None]
        return roots[0] if roots else None

    def validate_hierarchy(self) -> List[str]:
        """Check that all parent references exist and there are no cycles."""
        errors = []
        names = {c.name for c in self.components}
        for c in self.components:
            if c.parent and c.parent not in names:
                errors.append(f"{c.name}: parent '{c.parent}' not found")
        if not self.get_root():
            errors.append("No root component found (no component with parent=None)")
        return errors

    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "domain": self.domain,
            "version": self.version,
            "global_vinculum": self.global_vinculum.to_dict() if self.global_vinculum else None,
            "metadata": self.metadata,
            "components": [c.to_dict() for c in self.components],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AssemblySpec":
        gv = None
        if data.get("global_vinculum"):
            gv = Vinculum.from_dict(data["global_vinculum"])
        components = [ComponentSpec.from_dict(c) for c in data.get("components", [])]
        return cls(
            model_id=data["model_id"],
            domain=data.get("domain", "generic"),
            version=data.get("version", "1.0"),
            global_vinculum=gv,
            metadata=data.get("metadata", {}),
            components=components,
        )

    # -- Serialization formats --
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, s: str) -> "AssemblySpec":
        return cls.from_dict(json.loads(s))

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, s: str) -> "AssemblySpec":
        return cls.from_dict(yaml.safe_load(s))

    # -- File I/O --
    def save_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    def save_yaml(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_yaml())

    @classmethod
    def load_json(cls, path: str) -> "AssemblySpec":
        with open(path, "r") as f:
            return cls.from_json(f.read())

    @classmethod
    def load_yaml(cls, path: str) -> "AssemblySpec":
        with open(path, "r") as f:
            return cls.from_yaml(f.read())

    # -- Validation --
    def validate_all(self, measurements: Dict[str, float]) -> List[str]:
        """Run vinculum validation across global + all component constraints."""
        errors = []
        if self.global_vinculum:
            errors.extend(self.global_vinculum.get_failures(measurements))
        for c in self.components:
            errors.extend(c.validate_against_vinculum(measurements))
        return errors

    def is_valid(self, measurements: Dict[str, float]) -> bool:
        return len(self.validate_all(measurements)) == 0

    # -- Convenience: list component names in hierarchy order --
    def component_names(self) -> List[str]:
        return [c.name for c in self.components]

    def tree(self, indent: int = 0) -> str:
        """Pretty-print the component hierarchy."""
        lines = []
        root = self.get_root()
        if root is None:
            return "(no root)"

        def _recurse(name: str, depth: int):
            comp = self.get_component(name)
            if comp is None:
                return
            prefix = "  " * depth
            jt = comp.joint_type.value
            lines.append(f"{prefix}\u251c\u2500 {comp.name} [{comp.component_type}] ({jt})")
            for child in self.get_children(name):
                _recurse(child.name, depth + 1)

        lines.append(f"{root.name} [{root.component_type}] ({root.joint_type.value})")
        for child in self.get_children(root.name):
            _recurse(child.name, 1)
        return "\n".join(lines)
