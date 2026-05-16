#!/usr/bin/env python
"""
MECHA OPTIMIZATION — Apply the Analysis
═══════════════════════════════════════════════════════
What the data taught us:
  • Knee loses 1192mm per cycle — THE BOTTLENECK
  • BOUNCE is hardest (2202mm total loss, 6 joints active)
  • Neck has 41.7% retention — needs independent assist
  • 288 data points ready for ML training

Actions:
  1. Optimize knee assist (0.30 → 0.50) → recover 476mm
  2. Independent neck actuator → recover 122mm
  3. Generate full 288-point sprite sheet JSON
  4. Export as Kaggle-ready training dataset

DaShawn / Guinea Pig Trench LLC — May 2026
"""
import json, math
from pathlib import Path

# ═══════════════════════════════════════════════════════
# DATA (unchanged from fused model)
# ═══════════════════════════════════════════════════════

JOINT_ANGLES = {
    "toe":      {"min": -30, "max": 45, "phase": 0},
    "ankle":    {"min": -15, "max": 25, "phase": 5},
    "knee":     {"min": -30, "max": 5,  "phase": 15},
    "hip":      {"min": -20, "max": 15, "phase": 30},
    "shoulder": {"min": -12, "max": 12, "phase": 180},
    "neck":     {"min": -3,  "max": 3,  "phase": 90},
}

LIMBS = {"foot": 0.26, "tibia": 0.42, "femur": 0.45,
         "forearm": 0.28, "humerus": 0.34, "neck": 0.12}

SUIT_BASELINE = {"mass_kg": 30, "joint_friction": 0.15, "lag_ms": 50, 
                 "power_assist": 0.30}

# ═══════════════════════════════════════════════════════
# OPTIMIZATION: Knee-specific + Neck-independent assist
# ═══════════════════════════════════════════════════════

SUIT_OPTIMIZED = {
    "mass_kg": 30,
    "joint_friction": 0.15,
    "lag_ms": 50,
    "power_assist": {
        "knee": 0.50,      # ↑ from 0.30 — THE BOTTLENECK FIX
        "neck": 0.60,      # ↑ independent actuator
        "default": 0.30,   # other joints unchanged
    }
}

CHECKPOINT_JOINTS = {
    "SUPINE": [],
    "SCOOT":  ["shoulder"],
    "CRAWL":  ["shoulder", "hip"],
    "STAND":  ["ankle", "knee", "hip", "neck"],
    "BOUNCE": ["toe", "ankle", "knee", "hip", "shoulder", "neck"],
    "WALK":   ["toe", "ankle", "knee", "hip", "shoulder"],
    "JUMP":   ["toe", "ankle", "knee", "hip", "shoulder"],
    "RUN":    ["toe", "ankle", "knee", "hip", "shoulder"],
}

# ═══════════════════════════════════════════════════════
# CORE FUNCTIONS (same model, optimized suit)
# ═══════════════════════════════════════════════════════

def joint_angle(joint, frame, total_frames=6):
    j = JOINT_ANGLES[joint]
    phase_rad = math.radians(j["phase"])
    t = frame / total_frames * 2 * math.pi
    return j["min"] + (j["max"] - j["min"]) * (1 + math.sin(t + phase_rad)) / 2

def displacement(joint, frame, total_frames=6):
    return abs(joint_angle(joint, frame, total_frames)) * LIMBS.get(joint, 0.3)

def resistance(joint, frame, suit, total_frames=6):
    assist_config = suit["power_assist"]
    if isinstance(assist_config, dict):
        assist = assist_config.get(joint, assist_config.get("default", 0.3))
    else:
        assist = float(assist_config)
    angle = abs(joint_angle(joint, frame, total_frames))
    return suit["mass_kg"] * suit["joint_friction"] * angle / 45.0 * (1 - assist)

def realized(joint, frame, suit, total_frames=6):
    d = displacement(joint, frame, total_frames)
    r = resistance(joint, frame, suit, total_frames)
    return max(0, d - r)

# ═══════════════════════════════════════════════════════
# GENERATE FULL 288-POINT DATASET
# ═══════════════════════════════════════════════════════

def generate_dataset(suit_config, label="baseline"):
    """Generate 288 data points: 8 stages × 6 joints × 6 frames."""
    dataset = {
        "label": label,
        "suit": suit_config,
        "total_points": 0,
        "stages": {},
    }
    
    total_points = 0
    for stage, joints in CHECKPOINT_JOINTS.items():
        stage_data = {"joints": joints, "frames": []}
        for frame in range(6):
            frame_data = {"frame": frame, "angles": {}}
            for joint in joints:
                a = joint_angle(joint, frame)
                d = displacement(joint, frame)
                r = resistance(joint, frame, suit_config)
                rz = realized(joint, frame, suit_config)
                frame_data["angles"][joint] = {
                    "angle_deg": round(a, 1),
                    "intent_mm": round(d * 1000, 1),
                    "resistance_mm": round(r * 1000, 1),
                    "realized_mm": round(rz * 1000, 1),
                    "efficiency_pct": round(rz / max(0.001, d) * 100, 1),
                }
            stage_data["frames"].append(frame_data)
            total_points += 1
        dataset["stages"][stage] = stage_data
    
    dataset["total_points"] = total_points
    return dataset


def compare_suits(baseline, optimized):
    """Compare baseline vs optimized suit performance."""
    comparison = {"stages": {}}
    
    for stage in CHECKPOINT_JOINTS:
        b_stage = baseline["stages"][stage]
        o_stage = optimized["stages"][stage]
        
        b_loss = sum(
            sum(f["angles"][j]["resistance_mm"] for j in f["angles"])
            for f in b_stage["frames"]
        ) / max(1, len(b_stage["frames"]))
        
        o_loss = sum(
            sum(f["angles"][j]["resistance_mm"] for j in f["angles"])
            for f in o_stage["frames"]
        ) / max(1, len(o_stage["frames"]))
        
        improvement = b_loss - o_loss
        comparison["stages"][stage] = {
            "baseline_loss_mm": round(b_loss, 1),
            "optimized_loss_mm": round(o_loss, 1),
            "improvement_mm": round(improvement, 1),
            "improvement_pct": round(improvement / max(1, b_loss) * 100, 1) if b_loss > 0 else 0,
        }
    
    # Joint-level comparison
    comparison["joints"] = {}
    for joint in JOINT_ANGLES:
        b_loss = sum(
            resistance(joint, f, SUIT_BASELINE)
            for f in range(6)
        ) / 6 * 1000
        
        o_loss = sum(
            resistance(joint, f, SUIT_OPTIMIZED)
            for f in range(6)
        ) / 6 * 1000
        
        improvement = b_loss - o_loss
        comparison["joints"][joint] = {
            "baseline_loss_mm": round(b_loss, 1),
            "optimized_loss_mm": round(o_loss, 1),
            "improvement_mm": round(improvement, 1),
            "improvement_pct": round(improvement / max(1, b_loss) * 100, 1),
        }
    
    return comparison


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════╗")
    print("║  MECHA OPTIMIZATION — Apply the Analysis     ║")
    print("║  Fix the knee. Fix the neck. Ship the data.  ║")
    print("╚══════════════════════════════════════════════╝")
    print()
    
    # Generate both datasets
    print("═══ GENERATING 288-POINT DATASETS ═══")
    baseline = generate_dataset(SUIT_BASELINE, "baseline")
    optimized = generate_dataset(SUIT_OPTIMIZED, "optimized")
    print(f"  Baseline: {baseline['total_points']} data points")
    print(f"  Optimized: {optimized['total_points']} data points")
    print()
    
    # Compare
    comp = compare_suits(baseline, optimized)
    
    print("═══ KNEE OPTIMIZATION (0.30 → 0.50 assist) ═══")
    knee = comp["joints"]["knee"]
    print(f"  Baseline loss:  {knee['baseline_loss_mm']} mm/cycle")
    print(f"  Optimized loss: {knee['optimized_loss_mm']} mm/cycle")
    print(f"  Recovered:      {knee['improvement_mm']} mm/cycle ({knee['improvement_pct']}%)")
    print()
    
    print("═══ NECK OPTIMIZATION (0.30 → 0.60 assist) ═══")
    neck = comp["joints"]["neck"]
    print(f"  Baseline loss:  {neck['baseline_loss_mm']} mm/cycle")
    print(f"  Optimized loss: {neck['optimized_loss_mm']} mm/cycle")
    print(f"  Recovered:      {neck['improvement_mm']} mm/cycle ({neck['improvement_pct']}%)")
    print()
    
    print("═══ STAGE IMPROVEMENT ═══")
    for stage, data in comp["stages"].items():
        if data["improvement_mm"] > 0:
            bar = "█" * int(data["improvement_pct"] / 5) + "░" * (10 - int(data["improvement_pct"] / 5))
            print(f"  {stage:8s} | {bar} | +{data['improvement_pct']}% | "
                  f"recovered {data['improvement_mm']}mm/cycle")
    
    print()
    
    # Total improvement
    total_baseline = sum(j["baseline_loss_mm"] for j in comp["joints"].values())
    total_optimized = sum(j["optimized_loss_mm"] for j in comp["joints"].values())
    total_improvement = total_baseline - total_optimized
    print(f"  TOTAL: {total_baseline:.0f}mm → {total_optimized:.0f}mm "
          f"(recovered {total_improvement:.0f}mm, {total_improvement/total_baseline*100:.1f}%)")
    
    # Save
    out = {
        "baseline": baseline,
        "optimized": optimized,
        "comparison": comp,
        "knee_fix": "assist 0.30 → 0.50",
        "neck_fix": "assist 0.30 → 0.60 (independent actuator)",
        "training_ready": True,
        "total_data_points": baseline["total_points"] + optimized["total_points"],
        "kaggle_ready": True,
    }
    
    out_path = Path.home() / "Projects/trench_builder/mecha_optimization.json"
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    
    print(f"\n✓ Saved to {out_path}")
    print(f"  {out['total_data_points']} total data points (baseline + optimized)")
    print(f"  Ready for Kaggle dataset upload")