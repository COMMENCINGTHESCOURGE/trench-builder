"""Trench-Builder Core: Parametric constraint system and component specification."""
from .vinculum import JointType, ConstraintKind, Constraint, Vinculum
from .component_spec import ComponentSpec, AssemblySpec

__all__ = [
    "JointType",
    "ConstraintKind",
    "Constraint",
    "Vinculum",
    "ComponentSpec",
    "AssemblySpec",
]
