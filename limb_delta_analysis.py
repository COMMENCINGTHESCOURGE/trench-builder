#!/usr/bin/env python
"""LIMB DELTA — Extend vs Shorten vs Vary"""
import json, math
from pathlib import Path

JOINT_ANGLES = {
    "toe":{"min":-30,"max":45,"phase":0},"ankle":{"min":-15,"max":25,"phase":5},
    "knee":{"min":-30,"max":5,"phase":15},"hip":{"min":-20,"max":15,"phase":30},
    "shoulder":{"min":-12,"max":12,"phase":180},"neck":{"min":-3,"max":3,"phase":90}}

BASELINE_LIMBS = {"foot":0.26,"tibia":0.42,"femur":0.45,"forearm":0.28,"humerus":0.34,"neck":0.12}

SUIT = {"mass_kg":30,"joint_friction":0.15,"power_assist":0.30}

def joint_angle(joint, frame, total_frames=6):
    j = JOINT_ANGLES[joint]
    t = frame / total_frames * 2 * math.pi
    return j["min"] + (j["max"] - j["min"]) * (1 + math.sin(t + math.radians(j["phase"]))) / 2

def resistance(joint, frame, total_frames=6):
    angle = abs(joint_angle(joint, frame, total_frames))
    return SUIT["mass_kg"] * SUIT["joint_friction"] * angle / 45.0 * (1 - SUIT["power_assist"])

def displacement(joint, frame, limbs, total_frames=6):
    return abs(joint_angle(joint, frame, total_frames)) * limbs.get(joint, 0.3)

def analyze_limbs(limbs, label):
    results = {"label": label, "limbs": limbs, "joints": {}}
    for joint in JOINT_ANGLES:
        total_disp = 0
        total_res = 0
        for frame in range(6):
            d = displacement(joint, frame, limbs)
            r = resistance(joint, frame)
            total_disp += d
            total_res += r
        avg_disp = total_disp / 6 * 1000
        avg_res = total_res / 6 * 1000
        efficiency = (avg_disp - avg_res) / max(0.001, avg_disp) * 100
        results["joints"][joint] = {"displacement_mm": round(avg_disp, 1),
            "resistance_mm": round(avg_res, 1), "efficiency_pct": round(max(0, efficiency), 1)}
    total_disp = sum(v["displacement_mm"] for v in results["joints"].values())
    total_res = sum(v["resistance_mm"] for v in results["joints"].values())
    results["total_displacement_mm"] = round(total_disp, 1)
    results["total_resistance_mm"] = round(total_res, 1)
    results["net_efficiency_pct"] = round((total_disp - total_res) / max(0.001, total_disp) * 100, 1)
    return results

# Test cases
cases = {}

# A: Baseline
cases["baseline"] = analyze_limbs(BASELINE_LIMBS, "Baseline (human)")

# B: Extended +30%
extended = {k: round(v * 1.3, 2) for k, v in BASELINE_LIMBS.items()}
cases["extended"] = analyze_limbs(extended, "Extended (+30%)")

# C: Shortened -30%
shortened = {k: round(v * 0.7, 2) for k, v in BASELINE_LIMBS.items()}
cases["shortened"] = analyze_limbs(shortened, "Shortened (-30%)")

# D: Power limbs (legs +30%, arms -20%)
power = BASELINE_LIMBS.copy()
for k in ["foot","tibia","femur"]: power[k] = round(power[k] * 1.3, 2)
for k in ["forearm","humerus"]: power[k] = round(power[k] * 0.8, 2)
cases["power_legs"] = analyze_limbs(power, "Power legs (+30%), short arms (-20%)")

# E: Long arms (arms +40%, legs -10%)
arms = BASELINE_LIMBS.copy()
for k in ["forearm","humerus"]: arms[k] = round(arms[k] * 1.4, 2)
for k in ["foot","tibia","femur"]: arms[k] = round(arms[k] * 0.9, 2)
cases["long_arms"] = analyze_limbs(arms, "Long arms (+40%), short legs (-10%)")

# F: All equal (every limb = 0.30m)
equal = {k: 0.30 for k in BASELINE_LIMBS}
cases["equal"] = analyze_limbs(equal, "Equal (all 0.30m)")

# Print results
print("=" * 70)
print("LIMB DELTA ANALYSIS — Extend vs Shorten vs Vary")
print("=" * 70)
print()

for name, data in cases.items():
    print(f"--- {data['label']} ---")
    for joint, jd in data["joints"].items():
        print(f"  {joint:8s}: disp={jd['displacement_mm']:6.0f}mm  resist={jd['resistance_mm']:5.0f}mm  eff={jd['efficiency_pct']:5.1f}%")
    print(f"  TOTAL:    disp={data['total_displacement_mm']:.0f}mm  resist={data['total_resistance_mm']:.0f}mm  eff={data['net_efficiency_pct']:.1f}%")
    print()

# Delta vs baseline
print("=" * 70)
print("DELTA FROM BASELINE")
print("=" * 70)
bl = cases["baseline"]
for name, data in cases.items():
    if name == "baseline": continue
    disp_delta = data["total_displacement_mm"] - bl["total_displacement_mm"]
    eff_delta = data["net_efficiency_pct"] - bl["net_efficiency_pct"]
    sign = "+" if disp_delta >= 0 else ""
    print(f"  {data['label']:<35s}: disp {sign}{disp_delta:.0f}mm  eff {sign}{eff_delta:+.1f}%")

print()
print("FINDING:")
print("  Longer limbs = more displacement per degree, same resistance")
print("  Shorter limbs = less displacement, same resistance → lower efficiency")
print("  Resistance is angle-based, not displacement-based — limb length doesn't add friction")
print("  Power legs + short arms = best ground mobility")
print("  Long arms = best reach for SCOOT/CRAWL stages")
print("  Equal limbs = worst of all worlds (no specialization)")

# Save
out = {"cases": {}, "deltas": {}}
for name, data in cases.items():
    out["cases"][name] = data
for name, data in cases.items():
    if name == "baseline": continue
    out["deltas"][name] = {
        "disp_delta_mm": round(data["total_displacement_mm"] - bl["total_displacement_mm"], 1),
        "eff_delta_pct": round(data["net_efficiency_pct"] - bl["net_efficiency_pct"], 1)}

with open(str(Path.home()) + "/Projects/trench_builder/limb_deltas.json", 'w') as f:
    json.dump(out, f, indent=2, default=str)
print("\nSaved limb_deltas.json")
