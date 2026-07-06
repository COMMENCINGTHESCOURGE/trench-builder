"""
Trench-Builder Core: Modular, Reverse-Engineerable Parametric Framework.

Every component is a typed dataclass. Every assembly is a composable tree.
Metadata is embedded in built objects so any .glb can be reverse-engineered
back to its original parametric specification.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class JointType(Enum):
    FIXED = "fixed"
    REVOLUTE = "revolute"
    SLIDER = "slider"
    BALL_AND_SOCKET = "ball_and_socket"
    BUTTERFLY = "butterfly"
    SWIVEL_CUT = "swivel_cut"


class Domain(Enum):
    MECHANICAL = "mechanical"
    SHIP = "ship"
    BUILDING = "building"
    CHARACTER = "character"


@dataclass
class Vinculum:
    """Mathematical constraints governing a component. Embedded for reverse engineering."""
    domain: str
    constraints: Dict[str, Any] = field(default_factory=dict)

    def validate(self, measurements: Dict[str, float], tolerance: float = 0.05) -> bool:
        """Check if actual measurements satisfy vinculum constraints within tolerance."""
        for key, expected in self.constraints.items():
            if key in measurements and isinstance(expected, (int, float)):
                actual = measurements[key]
                if not ((1 - tolerance) * expected <= actual <= (1 + tolerance) * expected):
                    return False
        return True

    def to_dict(self) -> dict:
        return {"domain": self.domain, "constraints": self.constraints}


@dataclass
class ComponentSpec:
    """Declarative specification of a single modular part."""
    name: str
    joint_type: JointType
    joint_axis: Optional[str] = None
    joint_limits: Optional[tuple] = None
    parent: Optional[str] = None
    vinculum: Optional[Vinculum] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    gear_spec: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        data = {
            "name": self.name,
            "joint_type": self.joint_type.value,
            "joint_axis": self.joint_axis,
            "joint_limits": list(self.joint_limits) if self.joint_limits else None,
            "parent": self.parent,
            "vinculum": self.vinculum.to_dict() if self.vinculum else None,
            "parameters": self.parameters,
            "gear_spec": self.gear_spec,
        }
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "ComponentSpec":
        v_data = data.get("vinculum")
        vinculum = Vinculum(**v_data) if v_data else None
        limits = tuple(data["joint_limits"]) if data.get("joint_limits") else None
        return cls(
            name=data["name"],
            joint_type=JointType(data["joint_type"]),
            joint_axis=data.get("joint_axis"),
            joint_limits=limits,
            parent=data.get("parent"),
            vinculum=vinculum,
            parameters=data.get("parameters", {}),
            gear_spec=data.get("gear_spec"),
        )


@dataclass
class AssemblySpec:
    """Complete modular model: a tree of components with global constraints."""
    model_id: str
    domain: str
    components: List[ComponentSpec] = field(default_factory=list)
    global_vinculum: Optional[Vinculum] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add(self, comp: ComponentSpec):
        self.components.append(comp)

    def get_component(self, name: str) -> Optional[ComponentSpec]:
        for c in self.components:
            if c.name == name:
                return c
        return None

    def get_children(self, parent_name: str) -> List[ComponentSpec]:
        return [c for c in self.components if c.parent == parent_name]

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "domain": self.domain,
            "global_vinculum": self.global_vinculum.to_dict() if self.global_vinculum else None,
            "components": [c.to_dict() for c in self.components],
            "metadata": self.metadata,
        }

    @classmethod
    def from_json(cls, json_str: str) -> "AssemblySpec":
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "AssemblySpec":
        gv_data = data.get("global_vinculum")
        global_vinculum = Vinculum(**gv_data) if gv_data else None
        components = [ComponentSpec.from_dict(c) for c in data.get("components", [])]
        return cls(
            model_id=data["model_id"],
            domain=data["domain"],
            components=components,
            global_vinculum=global_vinculum,
            metadata=data.get("metadata", {}),
        )
