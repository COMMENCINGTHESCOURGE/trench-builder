"""Trench-Builder: Character Domain — Gunpla-Engineered Biomechanical Rigs."""
from ..core import AssemblySpec, ComponentSpec, Vinculum, JointType


def generate_character(model_id: str = "character_v1", height_mm: float = 100.0) -> AssemblySpec:
    """Generate a 22-bone character rig with Gunpla engineering constraints.
    
    Proportions from anatomical vinculum ratios:
      head/height=0.15, torso/height=0.35, arm/height=0.38, leg/height=0.50
    """
    h = height_mm
    spec = AssemblySpec(
        model_id=model_id,
        domain="character",
        global_vinculum=Vinculum("character", {
            "head_height_total_ratio": 0.15,
            "torso_height_total_ratio": 0.35,
            "arm_length_total_ratio": 0.38,
            "leg_length_total_ratio": 0.50,
            "hand_length_total_ratio": 0.11,
            "foot_length_total_ratio": 0.16,
        }),
        metadata={"material": "PLA", "tolerance_mm": 0.20, "height_mm": h, "poly_target": 2500},
    )

    # Root → Pelvis → Spine chain
    spec.add(ComponentSpec("PELVIS", JointType.FIXED, parent=None,
        parameters={"width_mm": h * 0.15}))

    spec.add(ComponentSpec("SPINE_LOWER", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-15, 15),
        parent="PELVIS"))

    spec.add(ComponentSpec("SPINE_UPPER", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-15, 15),
        parent="SPINE_LOWER"))

    spec.add(ComponentSpec("TORSO", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-30, 30),
        parent="SPINE_UPPER",
        vinculum=Vinculum("character", {"torso_height_total_height_ratio": 0.35})))

    # Neck → Head
    spec.add(ComponentSpec("NECK", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-45, 45),
        parent="TORSO"))

    spec.add(ComponentSpec("HEAD", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-70, 70),
        parent="NECK",
        vinculum=Vinculum("character", {"head_height_total_height_ratio": 0.15})))

    # Left arm — butterfly shoulder + swivel cut
    spec.add(ComponentSpec("SHOULDER_L", JointType.BUTTERFLY, joint_axis="Z", joint_limits=(-90, 90),
        parent="TORSO",
        vinculum=Vinculum("character", {"joint_type": "butterfly", "forward_sweep_deg": 30})))

    spec.add(ComponentSpec("BICEP_SWIVEL_L", JointType.SWIVEL_CUT, joint_axis="Y", joint_limits=(-90, 90),
        parent="SHOULDER_L",
        vinculum=Vinculum("character", {"swivel_cut": True, "isolated_yaw": True})))

    spec.add(ComponentSpec("UPPER_ARM_L", JointType.REVOLUTE, joint_axis="X", joint_limits=(-135, 45),
        parent="BICEP_SWIVEL_L",
        vinculum=Vinculum("character", {"arm_length_total_height_ratio": 0.38})))

    spec.add(ComponentSpec("FOREARM_L", JointType.REVOLUTE, joint_axis="X", joint_limits=(0, 150),
        parent="UPPER_ARM_L",
        vinculum=Vinculum("character", {"forearm_upper_arm_ratio": 0.85})))

    spec.add(ComponentSpec("HAND_L", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-90, 90),
        parent="FOREARM_L",
        vinculum=Vinculum("character", {"hand_length_total_height_ratio": 0.11, "finger_segments": 3})))

    # Right arm
    spec.add(ComponentSpec("SHOULDER_R", JointType.BUTTERFLY, joint_axis="Z", joint_limits=(-90, 90),
        parent="TORSO"))

    spec.add(ComponentSpec("BICEP_SWIVEL_R", JointType.SWIVEL_CUT, joint_axis="Y", joint_limits=(-90, 90),
        parent="SHOULDER_R"))

    spec.add(ComponentSpec("UPPER_ARM_R", JointType.REVOLUTE, joint_axis="X", joint_limits=(-135, 45),
        parent="BICEP_SWIVEL_R"))

    spec.add(ComponentSpec("FOREARM_R", JointType.REVOLUTE, joint_axis="X", joint_limits=(0, 150),
        parent="UPPER_ARM_R"))

    spec.add(ComponentSpec("HAND_R", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-90, 90),
        parent="FOREARM_R"))

    # Left leg — ball-and-socket hip + double-hinge knee + swivel
    spec.add(ComponentSpec("HIP_L", JointType.BALL_AND_SOCKET, joint_axis="X", joint_limits=(-45, 120),
        parent="PELVIS",
        vinculum=Vinculum("character", {"hip_joint_type": "ball_and_socket"})))

    spec.add(ComponentSpec("THIGH_SWIVEL_L", JointType.SWIVEL_CUT, joint_axis="Y", joint_limits=(-45, 45),
        parent="HIP_L"))

    spec.add(ComponentSpec("UPPER_LEG_L", JointType.REVOLUTE, joint_axis="X", joint_limits=(-45, 120),
        parent="THIGH_SWIVEL_L",
        vinculum=Vinculum("character", {"leg_length_total_height_ratio": 0.50})))

    spec.add(ComponentSpec("KNEE_UPPER_L", JointType.REVOLUTE, joint_axis="X", joint_limits=(0, 90),
        parent="UPPER_LEG_L"))

    spec.add(ComponentSpec("KNEE_LOWER_L", JointType.REVOLUTE, joint_axis="X", joint_limits=(0, 90),
        parent="KNEE_UPPER_L",
        vinculum=Vinculum("character", {"knee_double_hinge": True})))

    spec.add(ComponentSpec("FOOT_L", JointType.BALL_AND_SOCKET, joint_axis="Z", joint_limits=(-30, 45),
        parent="KNEE_LOWER_L",
        vinculum=Vinculum("character", {"foot_length_total_height_ratio": 0.16})))

    # Right leg
    spec.add(ComponentSpec("HIP_R", JointType.BALL_AND_SOCKET, joint_axis="X", joint_limits=(-45, 120),
        parent="PELVIS"))

    spec.add(ComponentSpec("THIGH_SWIVEL_R", JointType.SWIVEL_CUT, joint_axis="Y", joint_limits=(-45, 45),
        parent="HIP_R"))

    spec.add(ComponentSpec("UPPER_LEG_R", JointType.REVOLUTE, joint_axis="X", joint_limits=(-45, 120),
        parent="THIGH_SWIVEL_R"))

    spec.add(ComponentSpec("KNEE_UPPER_R", JointType.REVOLUTE, joint_axis="X", joint_limits=(0, 90),
        parent="UPPER_LEG_R"))

    spec.add(ComponentSpec("KNEE_LOWER_R", JointType.REVOLUTE, joint_axis="X", joint_limits=(0, 90),
        parent="KNEE_UPPER_R"))

    spec.add(ComponentSpec("FOOT_R", JointType.BALL_AND_SOCKET, joint_axis="Z", joint_limits=(-30, 45),
        parent="KNEE_LOWER_R"))

    spec.metadata["bone_count"] = len(spec.components)
    return spec
