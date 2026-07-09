#!/usr/bin/env python
"""
FULL SUIT MECHANICS — Vinculum-Driven Modular Design
=====================================================
Every subsystem is a vinculum: what it preserves / what it sacrifices.
Modularity = each subsystem is independently swappable.
The suit is the ratio between pilot intent and realized output.

Iteration 1: Skeleton (identify all subsystems)
Iteration 2: Interfaces (define modular boundaries)
Iteration 3: Constraints (tighten vinculum ratios)
Devil's Advocacy: stress-test every assumption
"""
import json, math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════
# ITERATION 1: SKELETON — Every Subsystem as a Vinculum
# ═══════════════════════════════════════════════════════════

@dataclass
class Vinculum:
    """A vinculum is a ratio: what the system preserves vs what it sacrifices."""
    name: str
    preserves: str       # What this subsystem guarantees
    sacrifices: str      # What it gives up for that guarantee
    ratio_formula: str   # How to compute the vinculum value
    base_value: float = 1.0

# The full suit has 10 subsystems. Each one is a vinculum.
FULL_SUIT_V1 = {
    "name": "MECHA SUIT v3.0 — Vinculum Skeleton",
    "subsystems": {
        "mobility": Vinculum(
            name="MOBILITY",
            preserves="Joint range of motion and checkpoint traversal",
            sacrifices="Mass budget — every degree of freedom costs 1.2kg",
            ratio_formula="realized_displacement / pilot_intent",
            base_value=0.75
        ),
        "armor": Vinculum(
            name="ARMOR",
            preserves="Survivability against impact, ballistic, and energy damage",
            sacrifices="Mobility — every 5mm of plating adds 3.8kg and reduces joint ROM by 2°",
            ratio_formula="damage_absorbed / mass_penalty",
            base_value=0.60
        ),
        "power": Vinculum(
            name="POWER",
            preserves="Sustained operation time and peak output for all subsystems",
            sacrifices="Heat — every watt of output generates 0.4W of waste heat",
            ratio_formula="available_joules / total_demand",
            base_value=0.85
        ),
        "sensors": Vinculum(
            name="SENSORS",
            preserves="Situational awareness: radar, lidar, thermal, acoustic",
            sacrifices="Power — active scanning drains 15W per sensor; passive is 3W",
            ratio_formula="detection_range / power_draw",
            base_value=0.70
        ),
        "weapons": Vinculum(
            name="WEAPONS",
            preserves="Offensive capability at range",
            sacrifices="Hardpoint slots and power budget — each weapon occupies 1-3 slots",
            ratio_formula="damage_output / (slots * power_draw)",
            base_value=0.50
        ),
        "thermal": Vinculum(
            name="THERMAL",
            preserves="Heat dissipation to prevent subsystem shutdown",
            sacrifices="Signature — radiators increase detection radius by 40%",
            ratio_formula="heat_dissipated / heat_generated",
            base_value=0.90
        ),
        "life_support": Vinculum(
            name="LIFE_SUPPORT",
            preserves="Pilot survivability in hostile environments",
            sacrifices="Power and mass — sealed environment adds 8kg and 25W continuous",
            ratio_formula="environmental_tolerance / power_mass_cost",
            base_value=0.95
        ),
        "neural_interface": Vinculum(
            name="NEURAL_INTERFACE",
            preserves="Pilot-to-suit response time",
            sacrifices="Mental fatigue — every hour of neural link reduces pilot cognition by 4%",
            ratio_formula="(1.0 - lag_ms/1000) / fatigue_rate",
            base_value=0.88
        ),
        "modular_hardpoints": Vinculum(
            name="MODULAR_HARDPOINTS",
            preserves="Swappable component slots for mission-specific loadouts",
            sacrifices="Structural integrity — each hardpoint weakens the frame by 3%",
            ratio_formula="available_slots / structural_penalty",
            base_value=0.65
        ),
        "damage_control": Vinculum(
            name="DAMAGE_CONTROL",
            preserves="Graceful degradation — subsystems fail independently, not cascading",
            sacrifices="Redundancy mass — backup systems add 15% to total mass",
            ratio_formula="independent_failure_modes / redundant_mass",
            base_value=0.80
        ),
    }
}

# ═══════════════════════════════════════════════════════════
# ITERATION 2: INTERFACES — Modular Boundaries
# ═══════════════════════════════════════════════════════════

# Every subsystem exposes a standard interface:
#   inputs:  what it consumes from other subsystems
#   outputs: what it provides to other subsystems
#   state:   internal state variables
#   update:  how it evolves per tick

@dataclass
class SubsystemInterface:
    """Standard modular interface for every suit subsystem."""
    name: str
    inputs: Dict[str, str]    # input_name -> source_subsystem
    outputs: Dict[str, str]   # output_name -> description
    state: Dict[str, float]   # internal state variables
    mass_kg: float
    power_draw_w: float
    hardpoint_slots: int = 0
    
    def vinculum_value(self) -> float:
        """Every subsystem computes its own vinculum health."""
        raise NotImplementedError

# Define modular interfaces for all 10 subsystems
MOBILITY_INTERFACE = SubsystemInterface(
    name="mobility",
    inputs={"power_w": "power.available", "neural_lag_ms": "neural_interface.lag_ms"},
    outputs={"position_delta": "position update per tick", "joint_stress": "wear accumulation"},
    state={"velocity_ms": 0.0, "joint_wear": 0.0, "checkpoint": "STAND"},
    mass_kg=40.8, power_draw_w=80.0
)

ARMOR_INTERFACE = SubsystemInterface(
    name="armor",
    inputs={"incoming_damage": "external", "structural_integrity": "damage_control.frame"},
    outputs={"damage_reduction_pct": "damage mitigation", "plating_mass_kg": "mass contribution"},
    state={"plating_mm": 11.5, "ablative_remaining": 100.0, "breach_count": 0},
    mass_kg=40.0, power_draw_w=5.0
)

POWER_INTERFACE = SubsystemInterface(
    name="power",
    inputs={"total_demand_w": "sum(all_subsystems.power_draw)"},
    outputs={"available_w": "power budget", "waste_heat_w": "thermal input"},
    state={"capacity_j": 500000.0, "current_j": 500000.0, "output_w": 0.0, "efficiency": 0.85},
    mass_kg=28.0, power_draw_w=0.0  # power source, not consumer
)

SENSORS_INTERFACE = SubsystemInterface(
    name="sensors",
    inputs={"power_w": "power.available"},
    outputs={"detection_range_m": "radar/lidar range", "targets_locked": "target count"},
    state={"radar_range_m": 500.0, "thermal_range_m": 200.0, "targets_tracked": 0, "mode": "passive"},
    mass_kg=12.0, power_draw_w=15.0
)

WEAPONS_INTERFACE = SubsystemInterface(
    name="weapons",
    inputs={"power_w": "power.available", "target_data": "sensors.targets_locked"},
    outputs={"damage_per_sec": "offensive output", "heat_generated_w": "thermal input"},
    state={"slots_used": 2, "max_slots": 4, "cooldown_s": 0.0, "ammo": {"kinetic": 200, "energy": 100}},
    mass_kg=18.0, power_draw_w=120.0, hardpoint_slots=2
)

THERMAL_INTERFACE = SubsystemInterface(
    name="thermal",
    inputs={"heat_generated_w": "sum(power.waste_heat, weapons.heat, mobility.heat)"},
    outputs={"heat_dissipated_w": "cooling rate", "signature_radius_m": "detection penalty"},
    state={"current_temp_c": 35.0, "max_temp_c": 120.0, "radiator_efficiency": 0.72},
    mass_kg=14.0, power_draw_w=10.0
)

LIFE_SUPPORT_INTERFACE = SubsystemInterface(
    name="life_support",
    inputs={"power_w": "power.available"},
    outputs={"environmental_seal": "vacuum/toxin/underwater tolerance", "o2_hours": "remaining"},
    state={"o2_hours": 8.0, "water_hours": 24.0, "sealed": True, "internal_temp_c": 22.0},
    mass_kg=8.0, power_draw_w=25.0
)

NEURAL_INTERFACE = SubsystemInterface(
    name="neural_interface",
    inputs={"pilot_fatigue": "cumulative strain"},
    outputs={"lag_ms": "response delay", "command_fidelity": "intent translation accuracy"},
    state={"lag_ms": 50.0, "fatigue_pct": 0.0, "calibration": 0.95, "hours_linked": 0.0},
    mass_kg=2.0, power_draw_w=8.0
)

MODULAR_HARDPOINTS_INTERFACE = SubsystemInterface(
    name="modular_hardpoints",
    inputs={"attached_modules": "list of installed components"},
    outputs={"available_slots": "free hardpoints", "structural_penalty_pct": "frame weakening"},
    state={"total_slots": 8, "used_slots": 4, "structural_integrity": 1.0},
    mass_kg=6.0, power_draw_w=2.0
)

DAMAGE_CONTROL_INTERFACE = SubsystemInterface(
    name="damage_control",
    inputs={"subsystem_states": "all subsystem health values"},
    outputs={"cascade_risk": "failure propagation probability", "redundancy_active": "backup online"},
    state={"redundant_mass_kg": 0.0, "independent_failures": 0, "cascading_failures": 0},
    mass_kg=0.0, power_draw_w=3.0  # mass added to other subsystems as redundancy
)

# ═══════════════════════════════════════════════════════════
# ITERATION 3: CONSTRAINTS — Tighten Vinculum Ratios
# ═══════════════════════════════════════════════════════════

# The suit's total mass budget, power budget, and hardpoint budget
# create constraints. Every subsystem competes for shared resources.
# The vinculum ratios must sum to coherence.

SUIT_CONSTRAINTS_V3 = {
    "mass_budget_kg": 250.0,      # Total suit mass including pilot
    "power_budget_w": 500.0,      # Peak power output
    "hardpoint_slots": 8,          # Total modular slots
    "pilot_mass_kg": 80.0,         # Pilot + basic harness
    "target_uptime_hours": 4.0,    # Operational endurance
    "target_speed_ms": 8.0,        # Sprint speed
    "target_armor_mm": 20.0,       # Effective armor thickness
}

def validate_suit_constraints(subsystems: Dict[str, SubsystemInterface]) -> Dict:
    """Verify all subsystem interfaces satisfy the suit constraints."""
    total_mass = SUIT_CONSTRAINTS_V3["pilot_mass_kg"]
    total_power = 0.0
    total_slots = 0
    
    for name, iface in subsystems.items():
        total_mass += iface.mass_kg
        total_power += iface.power_draw_w
        total_slots += iface.hardpoint_slots
    
    return {
        "mass_kg": {"total": total_mass, "budget": SUIT_CONSTRAINTS_V3["mass_budget_kg"],
                     "pass": total_mass <= SUIT_CONSTRAINTS_V3["mass_budget_kg"]},
        "power_w": {"total": total_power, "budget": SUIT_CONSTRAINTS_V3["power_budget_w"],
                     "pass": total_power <= SUIT_CONSTRAINTS_V3["power_budget_w"]},
        "hardpoint_slots": {"total": total_slots, "budget": SUIT_CONSTRAINTS_V3["hardpoint_slots"],
                            "pass": total_slots <= SUIT_CONSTRAINTS_V3["hardpoint_slots"]},
    }

# ═══════════════════════════════════════════════════════════
# DEVIL'S ADVOCACY — Stress-Test Every Assumption
# ═══════════════════════════════════════════════════════════

def devils_advocacy():
    """Adversarial stress test on the full suit design.
    
    The Dialectical Vinculum: D-attack destabilizes, V-bind reconstitutes.
    Every assumption gets attacked. Only the survivors stay.
    """
    attacks = []
    
    # Attack 1: Mass budget is impossible
    subsystems = {
        "mobility": MOBILITY_INTERFACE,
        "armor": ARMOR_INTERFACE,
        "power": POWER_INTERFACE,
        "sensors": SENSORS_INTERFACE,
        "weapons": WEAPONS_INTERFACE,
        "thermal": THERMAL_INTERFACE,
        "life_support": LIFE_SUPPORT_INTERFACE,
        "neural_interface": NEURAL_INTERFACE,
        "modular_hardpoints": MODULAR_HARDPOINTS_INTERFACE,
        "damage_control": DAMAGE_CONTROL_INTERFACE,
    }
    
    constraints = validate_suit_constraints(subsystems)
    
    # A1: Mass budget attack
    total_mass = constraints["mass_kg"]["total"]
    budget = constraints["mass_kg"]["budget"]
    if total_mass > budget:
        over = total_mass - budget
        attacks.append({
            "attack": "MASS BUDGET VIOLATION",
            "finding": f"Total mass {total_mass}kg exceeds {budget}kg budget by {over}kg",
            "severity": "CRITICAL",
            "fix": f"Reduce armor plating (-{min(over, 20)}kg), remove 1 weapon hardpoint (-8kg), "
                   f"or accept reduced mobility (joint ROM -3° saves {over*0.4:.0f}kg)"
        })
    
    # A2: Power budget attack
    total_power = constraints["power_w"]["total"]
    power_budget = constraints["power_w"]["budget"]
    if total_power > power_budget:
        over = total_power - power_budget
        attacks.append({
            "attack": "POWER BUDGET VIOLATION",
            "finding": f"Peak draw {total_power}W exceeds {power_budget}W by {over}W",
            "severity": "HIGH",
            "fix": f"Weapons draw {WEAPONS_INTERFACE.power_draw_w}W — fire rate limited or downgrade to kinetic-only"
        })
    
    # A3: Heat death attack
    heat_generated = POWER_INTERFACE.power_draw_w + WEAPONS_INTERFACE.power_draw_w + MOBILITY_INTERFACE.power_draw_w
    heat_dissipated = heat_generated * THERMAL_INTERFACE.state["radiator_efficiency"]
    if heat_dissipated < heat_generated * 0.5:
        attacks.append({
            "attack": "THERMAL RUNAWAY",
            "finding": f"Heat dissipation {heat_dissipated:.0f}W < 50% of generation {heat_generated:.0f}W",
            "severity": "HIGH",
            "fix": "Larger radiators (+4kg, +40% detection radius) or thermal cycling (weapon cooldown +2s)"
        })
    
    # A4: Neural fatigue attack
    fatigue_rate = 0.04  # 4% cognition loss per hour
    uptime = SUIT_CONSTRAINTS_V3["target_uptime_hours"]
    final_fatigue = fatigue_rate * uptime
    if final_fatigue > 0.15:
        attacks.append({
            "attack": "PILOT COGNITIVE DEGRADATION",
            "finding": f"After {uptime}h, pilot at {final_fatigue*100:.0f}% cognition loss "
                       f"(threshold: 15% before mission-critical errors)",
            "severity": "MEDIUM",
            "fix": "Mandatory neural rest cycles every 2h or backup manual controls (+3kg)"
        })
    
    # A5: Single point of failure attack
    # Power is the only subsystem with no redundancy
    if POWER_INTERFACE.state["current_j"] < POWER_INTERFACE.state["capacity_j"] * 0.3:
        attacks.append({
            "attack": "CASCADE RISK — SINGLE POWER SOURCE",
            "finding": "Power subsystem has no redundant capacitor. Failure kills ALL subsystems.",
            "severity": "CRITICAL",
            "fix": "Add secondary capacitor bank (+5kg, +$12,000) or accept mission abort on power loss"
        })
    
    # A6: Modularity vs structural integrity
    hardpoints = MODULAR_HARDPOINTS_INTERFACE
    structural_loss = hardpoints.state["used_slots"] * 0.03  # 3% per slot
    if structural_loss > 0.10:
        attacks.append({
            "attack": "STRUCTURAL WEAKENING FROM MODULARITY",
            "finding": f"{hardpoints.state['used_slots']} hardpoints in use = {structural_loss*100:.0f}% frame weakening",
            "severity": "MEDIUM",
            "fix": "Reinforced hardpoint mounts (+2kg per slot) or limit to 4 active modules"
        })
    
    # A7: The knee is still the bottleneck
    # From mecha_optimization.py: knee loses 1192mm/cycle baseline
    if MOBILITY_INTERFACE.mass_kg > 40.8:
        attacks.append({
            "attack": "KNOWN BOTTLENECK — KNEE JOINT",
            "finding": "Knee loses 1192mm/cycle (mecha_optimization.py). "
                       "SIMP bracket optimized but not installed in mobility model.",
            "severity": "HIGH",
            "fix": "Apply SIMP knee bracket to mobility subsystem: mass -4.2kg, efficiency +18%"
        })
    
    # A8: No environmental sealing for vacuum
    life = LIFE_SUPPORT_INTERFACE
    if not life.state["sealed"]:
        attacks.append({
            "attack": "VACUUM VULNERABILITY",
            "finding": "Suit not rated for vacuum operations. Space deployment impossible.",
            "severity": "HIGH",
            "fix": "Enable sealed mode (+2kg gasket mass, +5W pressurization)"
        })
    
    return {
        "attacks_filed": len(attacks),
        "critical": sum(1 for a in attacks if a["severity"] == "CRITICAL"),
        "high": sum(1 for a in attacks if a["severity"] == "HIGH"),
        "medium": sum(1 for a in attacks if a["severity"] == "MEDIUM"),
        "findings": attacks,
        "constraints": constraints,
        "verdict": "BREACH" if any(a["severity"] == "CRITICAL" for a in attacks) else "PASS"
    }


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  FULL SUIT MECHANICS — Vinculum Modular Design")
    print("  Iteration 1: Skeleton → Iteration 2: Interfaces → Iteration 3: Constraints")
    print("=" * 60)
    print()
    
    # ITERATION 1 OUTPUT
    print("--- ITERATION 1: SKELETON ---")
    print(f"  {len(FULL_SUIT_V1['subsystems'])} subsystems identified")
    for name, v in FULL_SUIT_V1["subsystems"].items():
        print(f"  {name:20s} | preserves: {v.preserves[:45]}...")
        print(f"  {'':20s} | sacrifices: {v.sacrifices[:45]}...")
    print()
    
    # ITERATION 2 OUTPUT
    print("--- ITERATION 2: INTERFACES ---")
    subsystems = {
        "mobility": MOBILITY_INTERFACE, "armor": ARMOR_INTERFACE,
        "power": POWER_INTERFACE, "sensors": SENSORS_INTERFACE,
        "weapons": WEAPONS_INTERFACE, "thermal": THERMAL_INTERFACE,
        "life_support": LIFE_SUPPORT_INTERFACE, "neural_interface": NEURAL_INTERFACE,
        "modular_hardpoints": MODULAR_HARDPOINTS_INTERFACE,
        "damage_control": DAMAGE_CONTROL_INTERFACE,
    }
    for name, iface in subsystems.items():
        print(f"  {name:20s} | {iface.mass_kg:5.1f}kg | {iface.power_draw_w:5.0f}W | {iface.hardpoint_slots} slots")
    print()
    
    # ITERATION 3 OUTPUT
    print("--- ITERATION 3: CONSTRAINTS ---")
    constraints = validate_suit_constraints(subsystems)
    for budget_name, result in constraints.items():
        status = "PASS" if result["pass"] else "FAIL"
        print(f"  {budget_name:20s} | {result['total']:.0f} / {result['budget']:.0f} | {status}")
    print()
    
    # DEVIL'S ADVOCACY
    print("--- DEVIL'S ADVOCACY ---")
    da = devils_advocacy()
    print(f"  Attacks filed: {da['attacks_filed']}")
    print(f"  CRITICAL: {da['critical']} | HIGH: {da['high']} | MEDIUM: {da['medium']}")
    print(f"  VERDICT: {da['verdict']}")
    print()
    for a in da["findings"]:
        print(f"  [{a['severity']}] {a['attack']}")
        print(f"         {a['finding'][:80]}...")
        print(f"         Fix: {a['fix'][:80]}...")
        print()
