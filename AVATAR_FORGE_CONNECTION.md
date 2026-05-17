# AVATAR_FORGE v2.0 — Connection to Our System
# May 16, 2026

CONNECTION = """
═══════════════════════════════════════════════════════
AVATAR_FORGE v2.0 — The Pilot Container
═══════════════════════════════════════════════════════

  The mecha suit needs a pilot. The pilot needs a body.
  This is the BODY FACTORY.

DIRECT MAPPING:

  Avatar bones → Checkpoint joints:
    Shoulder → shoulder joint angle
    UpperArm → arm motion plane
    ForeArm → fine motor control
    Hand → tool grip
    Thigh → hip flexion
    Shin → knee angle
    Foot → ankle angle
    Toe → push-off

  The avatar IS the pilot of the KIRAGAMI mech.
  The armature IS the skeleton the correction drone tracks.
  The shape keys ARE the expression checkpoints.

PBR MATERIALS → D_mat LAYER:
  Skin (SSS)      → D_bio (biomechanical denominator — the pilot's body)
  Eyes (Glass)    → camera lens (the drone's view)
  Hair (Aniso)    → anisotropic reflection (same as Champagne Gold edges)
  Cyber (Metal)   → D_suit (the mecha's outer shell)
  Clothing        → D_cloth (flexible interface layer)

LIGHTING → CORRECTION DRONE CAMERA:
  Key light   → primary observation angle (warm, human)
  Fill light  → secondary observation (cool, shadow fill)
  Rim light   → silhouette detection (edge highlight for pose estimation)
  Hair light  → overhead detail (top-down drone view)

THE COMPLETE STACK:
  AVATAR_FORGE → generates the pilot
  KIRAGAMI     → generates the armor over the pilot
  Codex Topology Drone → validates fold angles on the armor
  Correction Drone     → watches pilot + armor movement
  Checkpoint System    → maps stages to joint angles

THE VINCULUM:
  (pilot body / armor shell) = one complete mecha
  The avatar is the numerator. The kirigami is the denominator.
  The vinculum IS the interface between skin and metal.
"""
