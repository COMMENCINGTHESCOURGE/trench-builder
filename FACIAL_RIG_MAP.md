# CORRECTION DRONE — Facial Rig + Vinculum System
# 14-joint complete. 8 expressions mapped to 8 checkpoints.

FACIAL_RIG_MAP = """
═══════════════════════════════════════════════════════
  CORRECTION DRONE — 14 JOINT MAP
═══════════════════════════════════════════════════════

  BODY (6):
    toe, ankle, knee, hip, shoulder, neck

  FACE (8):
    jaw, brow_L, brow_R, eye_L, eye_R, 
    mouth_corner_L, mouth_corner_R, cheek

  CHECKPOINT → EXPRESSION:
    SUPINE → neutral (baseline)
    SCOOT  → strain (brows tight)
    CRAWL  → effort (jaw clenched, cheeks puffed)
    STAND  → confident (slight smile, brows up)
    BOUNCE → joy (eyes wide, mouth open, cheeks lifted)
    WALK   → focus (eyes narrowed)
    JUMP   → exertion (grimace, jaw tight)
    RUN    → intensity (determined, mouth firm)

  VINCULUM SYSTEM:
    movement_state custom property (0.0-7.0)
    → drivers blend shape keys
    → Vinculum.evaluate() detects mismatch
    → UI panel shows ALIGNED or MISMATCH

  BLENDER UI:
    3D Viewport → Sidebar → Correction Drone tab
    • Movement State slider
    • Expression output display
    • Vinculum mismatch alert
    • Expression override field
    • Build Facial Rig button
    • Scan Vinculum button
"""
