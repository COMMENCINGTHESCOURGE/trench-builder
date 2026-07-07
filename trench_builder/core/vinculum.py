"""
Trench-Builder Core: Vinculum — constraint system for parametric validation.

A Vinculum is a set of mathematical constraints that govern a component or
assembly. They enable:
  - Build-time validation (does the geometry satisfy the constraint?)
  - Reverse engineering (extract constraints from a built model)
  - Domain-specific physics (proportions, joint limits, material bounds)
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import math


class JointType(Enum):
    """Kinematic joint types. Extensible per domain."""
    FIXED = "fixed"
    REVOLUTE = "revolute"
    PRISMATIC = "prismatic"
    SPHERICAL = "spherical"
    BUTTERFLY = "butterfly"      # Gunpla/mecha specific — dual-axis shoulder
    BALL_SOCKET = "ball_socket"  # Character limbs
    HINGE = "hinge"              # Simple single-axis


class ConstraintKind(Enum):
    """Categories of vinculum constraints."""
    ANGLE = "angle"
    RATIO = "ratio"
    RANGE = "range"
    EXACT = "exact"
    MASS = "mass"
    TOLERANCE = "tolerance"


@dataclass
class Constraint:
    """
    A single constraint rule.
    
    Examples:
        Constraint(kind=ANGLE, key="elbow_flexion", min=-5, max=150)
        Constraint(kind=RATIO, key="arm_span_to_height", target=1.0, tolerance=0.05)
        Constraint(kind=RANGE, key="grip_strength_kg", min=20, max=200)
        Constraint(kind=EXACT, key="spine_segments", target=24)
    """
    kind: ConstraintKind
    key: str
    target: Optional[float] = None      # For RATIO, EXACT
    min: Optional[float] = None         # For ANGLE, RANGE
    max: Optional[float] = None         # For ANGLE, RANGE
    tolerance: float = 0.05             # 5% default tolerance for RATIO
    description: str = ""

    def validate(self, value: float) -> Tuple[bool, str]:
        """Check whether a measured value satisfies this constraint."""
        if self.kind == ConstraintKind.ANGLE:
            if self.min is not None and value < self.min:
                return False, f"{self.key}: {value} < min {self.min}"
            if self.max is not None and value > self.max:
                return False, f"{self.key}: {value} > max {self.max}"
            return True, "ok"

        elif self.kind == ConstraintKind.RATIO:
            if self.target is None:
                return True, "ok"
            lo = self.target * (1 - self.tolerance)
            hi = self.target * (1 + self.tolerance)
            if lo <= value <= hi:
                return True, "ok"
            return False, f"{self.key}: {value} outside [{lo:.4f}, {hi:.4f}]"

        elif self.kind == ConstraintKind.RANGE:
            if self.min is not None and value < self.min:
                return False, f"{self.key}: {value} < min {self.min}"
            if self.max is not None and value > self.max:
                return False, f"{self.key}: {value} > max {self.max}"
            return True, "ok"

        elif self.kind == ConstraintKind.EXACT:
            if self.target is not None and not math.isclose(value, self.target, rel_tol=self.tolerance):
                return False, f"{self.key}: {value} != {self.target}"
            return True, "ok"

        elif self.kind == ConstraintKind.MASS:
            if self.min is not None and value < self.min:
                return False, f"{self.key}: mass {value} < min {self.min}"
            if self.max is not None and value > self.max:
                return False, f"{self.key}: mass {value} > max {self.max}"
            return True, "ok"

        elif self.kind == ConstraintKind.TOLERANCE:
            half = self.tolerance / 2
            if self.target is not None and abs(value - self.target) > half:
                return False, f"{self.key}: {value} outside tolerance \u00b1{half}"
            return True, "ok"

        return True, "ok"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["kind"] = self.kind.value
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Constraint":
        kind = ConstraintKind(data.pop("kind"))
        return cls(kind=kind, **data)

    # -- Convenience constructors --
    @classmethod
    def angle(cls, key: str, min_deg: float, max_deg: float, desc: str = "") -> "Constraint":
        return cls(kind=ConstraintKind.ANGLE, key=key, min=min_deg, max=max_deg, description=desc)

    @classmethod
    def ratio(cls, key: str, target: float, tolerance: float = 0.05, desc: str = "") -> "Constraint":
        return cls(kind=ConstraintKind.RATIO, key=key, target=target, tolerance=tolerance, description=desc)

    @classmethod
    def bounds(cls, key: str, min_val: float, max_val: float, desc: str = "") -> "Constraint":
        return cls(kind=ConstraintKind.RANGE, key=key, min=min_val, max=max_val, description=desc)


@dataclass
class Vinculum:
    """
    A collection of constraints governing a component or assembly.
    Embedded in built objects for reverse engineering.
    """
    domain: str
    constraints: Dict[str, Constraint] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add(self, constraint: Constraint) -> "Vinculum":
        self.constraints[constraint.key] = constraint
        return self

    def validate_all(self, measurements: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Check all constraints against actual measurements.
        Returns (passed, list_of_failures).
        """
        failures = []
        for key, constraint in self.constraints.items():
            if key in measurements:
                ok, msg = constraint.validate(measurements[key])
                if not ok:
                    failures.append(msg)
        return len(failures) == 0, failures

    def get_failures(self, measurements: Dict[str, float]) -> List[str]:
        _, failures = self.validate_all(measurements)
        return failures

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "constraints": {k: v.to_dict() for k, v in self.constraints.items()},
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Vinculum":
        constraints = {}
        for k, v in data.get("constraints", {}).items():
            constraints[k] = Constraint.from_dict(v)
        return cls(
            domain=data["domain"],
            constraints=constraints,
            metadata=data.get("metadata", {}),
        )

    # -- Domain-specific factory presets --
    @classmethod
    def humanoid(cls) -> "Vinculum":
        return cls(domain="character").add(
            Constraint.ratio("arm_span_to_height", 1.0, 0.05, "Wingspan \u2248 height")
        ).add(
            Constraint.ratio("head_to_body", 0.125, 0.02, "Head \u2248 1/8 total height")
        ).add(
            Constraint.ratio("leg_to_torso", 1.1, 0.08, "Legs slightly longer than torso")
        )

    @classmethod
    def mecha(cls) -> "Vinculum":
        return cls(domain="mecha").add(
            Constraint.ratio("arm_to_torso", 0.85, 0.05, "Arms 85% of torso height")
        ).add(
            Constraint.ratio("head_to_body", 0.15, 0.03, "Mecha heads are larger proportionally")
        ).add(
            Constraint.bounds("joint_torque_nm", 10, 5000, "Joint torque in newton-meters")
        )

    @classmethod
    def corrupted(cls) -> "Vinculum":
        """Corrupted variant: asymmetric, twisted constraints."""
        return cls(domain="character").add(
            Constraint.angle("left_shoulder_abduction", -15, 180, "Hyperflexible left")
        ).add(
            Constraint.angle("right_shoulder_abduction", -90, 45, "Locked right \u2014 corruption")
        ).add(
            Constraint.ratio("torso_twist_degrees", 15, 0.3, "Permanent spinal twist")
        )
