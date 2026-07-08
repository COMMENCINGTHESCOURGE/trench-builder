import pytest
from trench_builder.core.vinculum import Vinculum, ConstraintKind

def test_typography_vinculum_definition():
    """Verify that Vinculum.typography() initializes all required constraints."""
    vinc = Vinculum.typography()
    assert vinc.domain == "typography"
    
    # Required keys
    keys = ["bevel_continuity", "extrusion_depth_ratio", "kerning_tolerance", "chamfer_segments", "coverage_ratio"]
    for key in keys:
        assert key in vinc.constraints
        
    # Check types
    assert vinc.constraints["bevel_continuity"].kind == ConstraintKind.CURVATURE
    assert vinc.constraints["extrusion_depth_ratio"].kind == ConstraintKind.RATIO
    assert vinc.constraints["kerning_tolerance"].kind == ConstraintKind.TOLERANCE
    assert vinc.constraints["chamfer_segments"].kind == ConstraintKind.RANGE
    assert vinc.constraints["coverage_ratio"].kind == ConstraintKind.RATIO


def test_typography_vinculum_validation():
    """Verify that typography constraints validate measurements correctly."""
    vinc = Vinculum.typography()
    
    # Valid parameters
    measurements = {
        "bevel_continuity": 2.0,            # G2
        "extrusion_depth_ratio": 0.15,      # exactly target
        "kerning_tolerance": 0.0,           # exactly target
        "chamfer_segments": 16,             # between 8 and 64
        "coverage_ratio": 0.65,             # exactly target
    }
    passed, failures = vinc.validate_all(measurements)
    assert passed
    assert len(failures) == 0
    
    # Invalid parameters (out of bounds)
    bad_measurements = {
        "bevel_continuity": 1.0,            # G1 (requires G2 min)
        "extrusion_depth_ratio": 0.05,      # target 0.15 with 5% tol
        "kerning_tolerance": 0.2,           # too high
        "chamfer_segments": 4,              # too low
        "coverage_ratio": 0.95,             # too high
    }
    passed, failures = vinc.validate_all(bad_measurements)
    assert not passed
    assert len(failures) == 5
