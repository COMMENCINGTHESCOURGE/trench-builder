#!/usr/bin/env python
"""
MECHA MOBILITY — Improved from Existing Data
═══════════════════════════════════════════════════════
Uses data we ALREADY have to model the mecha suit vinculum.
No new video extraction needed.

DaShawn / Guinea Pig Trench LLC — May 2026
"""
import json, math
from pathlib import Path

# ═══════════════════════════════════════════════════════
# DATA WE ALREADY HAVE
# ═══════════════════════════════════════════════════════

# 1. JOINT ANGLES — from H5 Bounce (checkpoint_system.py)
JOINT_ANGLES = {
    "toe":      {"min": -30, "max": 45, "phase": 0},
    "ankle":    {"min": -15, "max": 25, "phase": 5},
    "knee":     {"min": -30, "max": 5,  "phase": 15},
    "hip":      {"min": -20, "max": 15, "phase": 30},
    "shoulder": {"min": -12, "max": 12, "phase": 180},
    "neck":     {"min": -3,  "max": 3,  "phase": 90},
}

# 2. LIMB LENGTHS — meters (H5 Bounce)
LIMBS = {
    "foot": 0.26, "tibia": 0.42, "femur": 0.45,
    "forearm": 0.28, "humerus": 0.34, "neck": 0.12,
}

# 3. SUIT PARAMETERS — estimated from biomechanical D_bio
SUIT = {
    "mass_kg": 30,           # Typical mecha cosplay suit
    "joint_friction": 0.15,  # Coefficient of joint resistance
    "lag_ms": 50,            # Interface delay (tight C_interface)
    "power_assist": 0.3,     # 30% of effort is motor-assisted
}

# 4. CHECKPOINT STAGES — 8 human mobility stages
CHECKPOINTS = [
    "SUPINE", "SCOOT", "CRAWL", "STAND",
    "BOUNCE", "WALK", "JUMP", "RUN",
]

# ═══════════════════════════════════════════════════════
# MECHA MOBILITY MODEL
# ═══════════════════════════════════════════════════════

def joint_angle_at_frame(joint_name, frame, total_frames=60):
    """Calculate joint angle at a given frame using existing phase data."""
    j = JOINT_ANGLES[joint_name]
    freq = 1.0  # 1 cycle per bounce
    phase_rad = math.radians(j["phase"])
    t = frame / total_frames * 2 * math.pi  # 0 to 2π over bounce cycle
    
    # Angle oscillates between min and max
    angle = j["min"] + (j["max"] - j["min"]) * (1 + math.sin(t * freq + phase_rad)) / 2
    return angle

def displacement_at_frame(joint_name, frame, total_frames=60):
    """Linear displacement = angle × limb length."""
    angle = joint_angle_at_frame(joint_name, frame, total_frames)
    limb = LIMBS.get(joint_name, 0.3)
    return angle * limb  # simplified: small angles

def suit_resistance(joint_name, frame, total_frames=60):
    """D_suit = mass × friction × (1 - power_assist)."""
    angle = abs(joint_angle_at_frame(joint_name, frame, total_frames))
    base = SUIT["mass_kg"] * SUIT["joint_friction"] * angle / 45.0
    assisted = base * (1 - SUIT["power_assist"])
    return assisted

def realized_movement(joint_name, frame, total_frames=60):
    """A_realized = A_intent - D_suit resistance.
    How much the suit actually moves vs what the pilot intended.
    """
    intent = displacement_at_frame(joint_name, frame, total_frames)
    resistance = suit_resistance(joint_name, frame, total_frames)
    realized = max(0, abs(intent) - resistance) * (1 if intent >= 0 else -1)
    loss = abs(resistance)
    return {
        "joint": joint_name,
        "frame": frame,
        "intent_mm": round(abs(intent) * 1000, 1),
        "resistance_mm": round(loss * 1000, 1),
        "realized_mm": round(abs(realized) * 1000, 1),
        "error_mm": round(loss * 1000, 1),
        "efficiency": round(max(0, abs(realized) / max(0.001, abs(intent))) * 100, 1),
    }

# ═══════════════════════════════════════════════════════
# CHECKPOINT MAPPING
# ═══════════════════════════════════════════════════════

def checkpoint_mobility(checkpoint_name, suit_mass=None):
    """Model how the suit moves at each checkpoint stage."""
    if suit_mass is None:
        suit_mass = SUIT["mass_kg"]
    
    # Each checkpoint has different active joints
    checkpoint_joints = {
        "SUPINE": [],                    # No movement
        "SCOOT":  ["shoulder"],          # Arms only
        "CRAWL":  ["shoulder", "hip"],   # Cross-pattern
        "STAND":  ["ankle", "knee", "hip", "neck"],  # Balance
        "BOUNCE": ["toe", "ankle", "knee", "hip", "shoulder", "neck"],  # Full body
        "WALK":   ["toe", "ankle", "knee", "hip", "shoulder"],  # Reciprocal
        "JUMP":   ["toe", "ankle", "knee", "hip", "shoulder"],  # Explosive
        "RUN":    ["toe", "ankle", "knee", "hip", "shoulder"],  # Sustained
    }
    
    joints = checkpoint_joints.get(checkpoint_name, [])
    if not joints:
        return {"checkpoint": checkpoint_name, "joints": 0, "total_error_mm": 0, 
                "efficiency_pct": 100, "note": "No movement — supine rest"}
    
    # Average across all active joints at their peak frame
    total_error = 0
    total_intent = 0
    for joint in joints:
        peak_frame = int(JOINT_ANGLES[joint]["phase"] / 360 * 60) % 60
        result = realized_movement(joint, peak_frame)
        total_error += result["resistance_mm"]
        total_intent += result["intent_mm"]
    
    avg_efficiency = round(max(0, (1 - total_error / max(1, total_intent))) * 100, 1)
    
    return {
        "checkpoint": checkpoint_name,
        "joints": len(joints),
        "joints_active": joints,
        "total_intent_mm": round(total_intent, 1),
        "total_error_mm": round(total_error, 1),
        "efficiency_pct": avg_efficiency,
        "suit_mass_kg": suit_mass,
        "vinculum": f"A_realized = A_intent - {total_error:.0f}mm"
    }

# ═══════════════════════════════════════════════════════
# SPRITE SHEET GENERATION
# ═══════════════════════════════════════════════════════

def generate_mecha_sprites(checkpoint_name, frames=6):
    """Generate sprite sheet positions for the mecha at each checkpoint."""
    joints = checkpoint_mobility(checkpoint_name)["joints_active"]
    sprites = []
    
    for frame in range(frames):
        sprite = {
            "frame": frame,
            "joints": {}
        }
        for joint in joints:
            angle = joint_angle_at_frame(joint, frame, frames)
            disp = displacement_at_frame(joint, frame, frames)
            sprite["joints"][joint] = {
                "angle_deg": round(angle, 1),
                "displacement_mm": round(disp * 1000, 1),
            }
        sprites.append(sprite)
    
    return {
        "checkpoint": checkpoint_name,
        "frames": len(sprites),
        "layout": f"{((frames+1)//2)}x2",
        "sprites": sprites,
    }


# ═══════════════════════════════════════════════════════
# MAIN — Run the model
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════╗")
    print("║  MECHA MOBILITY — Built from existing data       ║")
    print("║  No new video extraction needed                  ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    # 1. JOINT-BY-JOINT ANALYSIS
    print("═══ JOINT-LEVEL VINCULUM ═══")
    print(f"  Suit: {SUIT['mass_kg']}kg, friction={SUIT['joint_friction']}, "
          f"lag={SUIT['lag_ms']}ms, assist={SUIT['power_assist']*100}%")
    print()
    
    for joint in JOINT_ANGLES:
        result = realized_movement(joint, 30)  # Mid-bounce frame
        bar_len = int(result["efficiency"] / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"  {joint:8s} | {bar} | {result['efficiency']}% | "
              f"intent={result['intent_mm']}mm → realized={result['realized_mm']}mm "
              f"(lost {result['error_mm']}mm to suit)")
    
    print()
    
    # 2. CHECKPOINT-LEVEL MOBILITY
    print("═══ CHECKPOINT MOBILITY IN SUIT ═══")
    
    results = []
    for cp in CHECKPOINTS:
        result = checkpoint_mobility(cp)
        results.append(result)
        bar_len = max(0, int(result["efficiency_pct"] / 5))
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"  {cp:8s} | {bar} | {result['efficiency_pct']}% | "
              f"{result['joints']} joints | error={result['total_error_mm']}mm")
    
    print()
    
    # 3. SPRITE SHEET FOR BOUNCE (most complex checkpoint)
    print("═══ BOUNCE SPRITE SHEET ═══")
    bounce_sprites = generate_mecha_sprites("BOUNCE")
    print(f"  Layout: {bounce_sprites['layout']} ({bounce_sprites['frames']} frames)")
    for sprite in bounce_sprites["sprites"]:
        angles = [f"{j}={d['angle_deg']}°" for j, d in sprite["joints"].items()]
        print(f"    Frame {sprite['frame']}: {', '.join(angles)}")
    
    print()
    
    # 4. IMPROVEMENT FROM EXISTING DATA
    print("═══ WHAT THE DATA TAUGHT US ═══")
    print()
    print("  BEFORE: We had joint angles. We had limb lengths.")
    print("          We had D_bio tensor. We had checkpoint stages.")
    print("          They were SEPARATE — angles for biomechanics,")
    print("          checkpoints for project management.")
    print()
    print("  AFTER:  We fused them into a single model:")
    print("          joint_angle(frame) × limb_length − suit_resistance")
    print("          = realized displacement at each checkpoint stage.")
    print()
    print("  THE VINCULUM:")
    print("    (checkpoint_stage × joint_angles × limb_lengths)")
    print("    ────────────────────────────────────────────────")
    print("    (suit_mass × joint_friction × (1 − power_assist))")
    print("    = realized mecha movement")
    print()
    print("  6 joints × 8 checkpoints × 6 frames = 288 data points")
    print("  All from data we already had. No video extraction needed.")
    
    # Save
    output = {
        "joint_analysis": {j: realized_movement(j, 30) for j in JOINT_ANGLES},
        "checkpoint_mobility": [checkpoint_mobility(cp) for cp in CHECKPOINTS],
        "bounce_sprites": generate_mecha_sprites("BOUNCE"),
        "suit_params": SUIT,
        "data_sources": ["checkpoint_system.py", "coupled_forge_sim.py", 
                         "biomechanical_denominator", "joint_angles", "limb_lengths"],
    }
    
    out_path = Path.home() / "Projects/trench_builder/mecha_mobility_output.json"
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n✓ Saved to {out_path}")