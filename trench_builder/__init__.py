"""
Trench-Builder: Modular, Reverse-Engineerable Parametric Framework.

Three layers:
  core/        — Constraint system + Component/Assembly specifications
  domains/     — Domain-specific assembly generators (character, ship, building, mecha, typography)
  builders/    — Backend implementations (Blender, OpenSCAD, Unity)
"""
from .core import JointType, ConstraintKind, Constraint, Vinculum, ComponentSpec, AssemblySpec

__all__ = [
    "JointType",
    "ConstraintKind",
    "Constraint",
    "Vinculum",
    "ComponentSpec",
    "AssemblySpec",
]
