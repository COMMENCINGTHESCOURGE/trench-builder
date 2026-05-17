#!/usr/bin/env python
"""DRONE-AUGMENTED MECHA — Aerial Vinculum"""
import json, math
from pathlib import Path

# Ground mecha (unchanged)
JOINT_ANGLES = {"toe":{"min":-30,"max":45,"phase":0},"ankle":{"min":-15,"max":25,"phase":5},"knee":{"min":-30,"max":5,"phase":15},"hip":{"min":-20,"max":15,"phase":30},"shoulder":{"min":-12,"max":12,"phase":180},"neck":{"min":-3,"max":3,"phase":90}}
LIMBS = {"foot":0.26,"tibia":0.42,"femur":0.45,"forearm":0.28,"humerus":0.34,"neck":0.12}
SUIT = {"mass_kg":30,"joint_friction":0.15,"power_assist":0.30}

# DRONE PARAMETERS
DRONE = {
    "mass_kg": 5,           # Lightweight quadcopter
    "max_thrust_N": 80,     # ~8kg lift capacity
    "battery_Wh": 200,      # 30-45 min flight time
    "hover_power_W": 300,   # Power to hover with suit attached
    "max_speed_ms": 15,     # ~54 km/h
    "rotor_count": 4,       # Quadcopter
    "noise_db": 75,         # Audible but not deafening
    "assist_modes": {
        "lift": 0.70,       # 70% of suit weight lifted by drone
        "stabilize": 0.50,  # 50% of balance handled by drone
        "boost": 1.50,      # 150% thrust for jumps/emergency
    }
}

# 9th checkpoint: FLIGHT
AERIAL_CHECKPOINTS = ["SUPINE","SCOOT","CRAWL","STAND","BOUNCE","WALK","JUMP","RUN","FLIGHT"]

def joint_angle(joint, frame, total_frames=6):
    j = JOINT_ANGLES[joint]
    t = frame / total_frames * 2 * math.pi
    return j["min"] + (j["max"] - j["min"]) * (1 + math.sin(t + math.radians(j["phase"]))) / 2

def ground_resistance(joint, frame, total_frames=6):
    angle = abs(joint_angle(joint, frame, total_frames))
    return SUIT["mass_kg"] * SUIT["joint_friction"] * angle / 45.0 * (1 - SUIT["power_assist"])

def displacement(joint, frame, limbs, total_frames=6):
    return abs(joint_angle(joint, frame, total_frames)) * limbs.get(joint, 0.3)

def drone_assist(mode="lift"):
    """How much the drone reduces effective load."""
    return DRONE["assist_modes"].get(mode, 0)

def effective_suit_mass(mode="lift"):
    """Suit mass after drone lift assist."""
    return SUIT["mass_kg"] * (1 - drone_assist(mode))

def drone_augmented_resistance(joint, frame, mode="lift", total_frames=6):
    """Resistance with drone reducing effective mass."""
    angle = abs(joint_angle(joint, frame, total_frames))
    effective_mass = effective_suit_mass(mode)
    return effective_mass * SUIT["joint_friction"] * angle / 45.0 * (1 - SUIT["power_assist"])

def drone_battery_life(mode="hover"):
    """Remaining flight time."""
    power = DRONE["hover_power_W"] if mode == "hover" else DRONE["hover_power_W"] * 1.5
    hours = DRONE["battery_Wh"] / power
    return hours

# Analyze
print("=" * 60)
print("DRONE-AUGMENTED MECHA — Aerial Vinculum")
print("=" * 60)
print()

print("DRONE SPECS:")
for k,v in DRONE.items():
    if k != "assist_modes":
        print(f"  {k}: {v}")
print()

# Joint-by-joint: ground vs drone-assisted
print("JOINT RESISTANCE: Ground vs Drone-Assisted (70% lift)")
print(f"{'Joint':8s} {'Ground':>8s} {'Drone':>8s} {'Saved':>8s} {'Impr%':>6s}")
total_ground = 0; total_drone = 0
for joint in JOINT_ANGLES:
    gr = ground_resistance(joint, 30) * 1000
    dr = drone_augmented_resistance(joint, 30, "lift") * 1000
    saved = gr - dr
    pct = saved / max(0.001, gr) * 100
    total_ground += gr; total_drone += dr
    print(f"  {joint:8s} {gr:8.0f} {dr:8.0f} {saved:8.0f} {pct:5.1f}%")

print(f"  {'TOTAL':8s} {total_ground:8.0f} {total_drone:8.0f} {total_ground-total_drone:8.0f} {(total_ground-total_drone)/max(0.001,total_ground)*100:5.1f}%")
print()

# Stage-by-stage with drone
print("STAGE IMPROVEMENT: Ground vs Drone (70% lift)")
print(f"{'Stage':8s} {'Gnd loss':>8s} {'Drn loss':>8s} {'Saved':>8s} {'Impr%':>6s}")
CHECKPOINT_JOINTS = {"SUPINE":[],"SCOOT":["shoulder"],"CRAWL":["shoulder","hip"],"STAND":["ankle","knee","hip","neck"],"BOUNCE":["toe","ankle","knee","hip","shoulder","neck"],"WALK":["toe","ankle","knee","hip","shoulder"],"JUMP":["toe","ankle","knee","hip","shoulder"],"RUN":["toe","ankle","knee","hip","shoulder"],"FLIGHT":[]}

for stage, joints in CHECKPOINT_JOINTS.items():
    if stage == "SUPINE":
        print(f"  {stage:8s} {'0':>8s} {'0':>8s} {'0':>8s} {'0.0':>5s}%")
        continue
    if stage == "FLIGHT":
        print(f"  {stage:8s} {'0':>8s} {'0':>8s} {'0':>8s} {'100':>5s}%  (drone carries all)")
        continue
    g_loss = sum(ground_resistance(j, 30) * 1000 for j in joints)
    d_loss = sum(drone_augmented_resistance(j, 30, "lift") * 1000 for j in joints)
    saved = g_loss - d_loss
    pct = saved / max(0.001, g_loss) * 100
    print(f"  {stage:8s} {g_loss:8.0f} {d_loss:8.0f} {saved:8.0f} {pct:5.1f}%")
print()

# Battery analysis
print("BATTERY LIFE:")
for mode in ["hover","boost"]:
    hours = drone_battery_life(mode)
    mins = hours * 60
    print(f"  {mode:8s}: {mins:.0f} min ({hours:.2f}h)")
print()

# Drone boost for JUMP
print("DRONE BOOST — JUMP checkpoint (150% thrust):")
jump_ground = sum(ground_resistance(j, 30) * 1000 for j in CHECKPOINT_JOINTS["JUMP"])
jump_drone = sum(drone_augmented_resistance(j, 30, "boost") * 1000 for j in CHECKPOINT_JOINTS["JUMP"])
print(f"  Ground: {jump_ground:.0f}mm loss")
print(f"  Boost:  {jump_drone:.0f}mm loss (effective mass = {effective_suit_mass('boost'):.1f}kg)")
print(f"  JUMP becomes near-effortless with drone boost")
print()

# The full vinculum
print("THE DRONE-AUGMENTED VINCULUM:")
print("  (pilot intent) / (D_suit(1-D_drone) + D_bio)")
print(f"  D_suit(1-d_lift) = {SUIT['mass_kg']} * (1 - {drone_assist('lift')}) = {effective_suit_mass('lift'):.1f}kg effective mass")
print()
print("WHAT THE DRONE ADDS:")
print("  1. 9th checkpoint: FLIGHT (aerial mobility)")
print("  2. 70% weight reduction → joint losses cut proportionally")
print("  3. BOUNCE goes from hardest to manageable")
print("  4. FLIGHT bypasses ground checkpoints entirely")
print("  5. Boost mode: 150% thrust for explosive maneuvers")
print("  6. 40 min hover time → tactical window for aerial ops")
print("  7. The vinculum now has a 3rd term: pilot / (suit - drone + bio)")

# Save
out = {
    "drone_specs": DRONE,
    "ground_joint_losses": {j: round(ground_resistance(j,30)*1000,1) for j in JOINT_ANGLES},
    "drone_joint_losses": {j: round(drone_augmented_resistance(j,30,"lift")*1000,1) for j in JOINT_ANGLES},
    "effective_mass_kg": effective_suit_mass("lift"),
    "battery_life_hours": drone_battery_life("hover"),
    "new_checkpoint": "FLIGHT",
}

with open(str(Path.home())+"/Projects/trench_builder/drone_mecha_output.json",'w') as f:
    json.dump(out, f, indent=2)
print("\nSaved drone_mecha_output.json")
