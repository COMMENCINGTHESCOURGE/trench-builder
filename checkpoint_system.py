#!/usr/bin/env python3
"""
CHECKPOINT & HYPERCHECKPOINT SYSTEM
═══════════════════════════════════════════════════
Breaks any goal into atomic steps, validates each,
and generates AI training flashcards + sprite sheets.

Metaphor: Human mobility → Mechanical mobility
  Stand → Balance → Step → Walk → Run (checkpoints)
  Design → Prototype → Test → Validate → Deploy (hypercheckpoints)

DaShawn / Guinea Pig Trench LLC — May 2026
"""
import json, hashlib, os
from datetime import datetime
from pathlib import Path
from collections import OrderedDict

# ═══════════════════════════════════════════════════════
# DOMAIN CHECKPOINT TEMPLATES
# ═══════════════════════════════════════════════════════

HUMAN_MOBILITY = {
    "goal": "Full bipedal locomotion",
    "checkpoints": [
        {"id": "H1", "name": "Supine Rest", "state": "Lying flat, no muscle activation",
         "muscles": ["none active"], "energy": 0, "balance": "N/A", "next": "H2",
         "flashcard": "Body at rest. Zero energy expenditure. All joints neutral."},
        {"id": "H2", "name": "Core Engagement", "state": "Abdominal brace, pelvic tilt",
         "muscles": ["rectus abdominis", "transversus abdominis", "pelvic floor"],
         "energy": 5, "balance": "N/A", "next": "H3",
         "flashcard": "Deep core activates. Foundation for all movement. Brace without holding breath."},
        {"id": "H3", "name": "Roll to Side", "state": "Lateral weight shift, arm assist",
         "muscles": ["obliques", "latissimus dorsi", "gluteus medius"],
         "energy": 15, "balance": "Lateral 30%", "next": "H4",
         "flashcard": "Weight transfers to one side. Obliques fire. Arm pushes against surface."},
        {"id": "H4", "name": "Quadruped Position", "state": "Hands and knees, neutral spine",
         "muscles": ["erector spinae", "deltoids", "quadriceps"],
         "energy": 25, "balance": "4-point base", "next": "H5",
         "flashcard": "Four points of contact. Spine parallel to ground. Shoulders over wrists. Hips over knees."},
        {"id": "H5", "name": "Kneeling", "state": "Both knees down, torso vertical",
         "muscles": ["gluteus maximus", "hamstrings", "core stabilizers"],
         "energy": 35, "balance": "Knee base, narrow", "next": "H6",
         "flashcard": "Vertical torso from kneeling. Hip flexors engage. Arms free for balance."},
        {"id": "H6", "name": "Half-Kneeling", "state": "One knee up, one down, lunge position",
         "muscles": ["quadriceps (front leg)", "glutes (both)", "hip flexors"],
         "energy": 50, "balance": "Tripod base", "next": "H7",
         "flashcard": "Asymmetric stance. Front foot flat. Back knee and toes on ground. Core holds vertical."},
        {"id": "H7", "name": "Standing", "state": "Both feet planted, full extension",
         "muscles": ["gastrocnemius", "soleus", "quadriceps", "glutes", "core"],
         "energy": 60, "balance": "Biped base, narrow", "next": "H8",
         "flashcard": "Full upright posture. Ankles constantly micro-adjust. Center of mass over midfoot."},
        {"id": "H8", "name": "Weight Shift", "state": "Lateral weight transfer, single-leg prep",
         "muscles": ["gluteus medius", "tibialis anterior", "peroneals"],
         "energy": 65, "balance": "Single-leg transition", "next": "H9",
         "flashcard": "Shift weight to stance leg. Glute med fires to prevent hip drop. Swing leg unweights."},
        {"id": "H9", "name": "Step Initiation", "state": "Swing leg forward, heel strike prep",
         "muscles": ["iliopsoas", "rectus femoris", "tibialis anterior"],
         "energy": 75, "balance": "Dynamic single-leg", "next": "H10",
         "flashcard": "Swing leg lifts and advances. Hip flexors drive. Ankle dorsiflexes for heel clearance."},
        {"id": "H10", "name": "Walking", "state": "Reciprocal gait, alternating stance/swing",
         "muscles": ["all lower body cycling"], "energy": 85, "balance": "Dynamic bipedal", "next": "H11",
         "flashcard": "Reciprocal gait cycle. 60% stance phase, 40% swing. Heel strike → mid-stance → toe-off."},
        {"id": "H11", "name": "Running", "state": "Aerial phase, increased cadence",
         "muscles": ["all lower body + arms"], "energy": 100, "balance": "Dynamic with flight", "next": None,
         "flashcard": "Both feet leave ground during stride. Arms counter-rotate. 3× energy of walking."},
    ]
}

MECHANICAL_MOBILITY = {
    "goal": "Functional rotary engine assembly",
    "hypercheckpoints": [
        {"id": "M1", "name": "Requirements Analysis", "phase": "DESIGN",
         "deliverables": ["torque curve spec", "thermal envelope", "material constraints", "cost target"],
         "validation": "Stakeholder sign-off on spec document",
         "flashcard": "Define what the engine must do before designing how it does it. Torque, RPM range, thermal limits."},
        {"id": "M2", "name": "Conceptual Design", "phase": "DESIGN",
         "deliverables": ["rotor geometry", "housing profile", "port timing diagram"],
         "validation": "CFD simulation of combustion chamber",
         "flashcard": "Wankel cycle: intake→compression→ignition→exhaust. Rotor has 3 faces, each fires once per revolution."},
        {"id": "M3", "name": "Material Selection", "phase": "MATERIALS",
         "deliverables": ["apex seal material", "housing coating", "rotor alloy"],
         "validation": "Thermal expansion compatibility check",
         "flashcard": "Apex seals: carbon-aluminum or ceramic. Housing: Nikasil-coated aluminum. Thermal expansion must match."},
        {"id": "M4", "name": "Tolerance Stack Analysis", "phase": "ENGINEERING",
         "deliverables": ["GD&T drawing", "clearance budget", "thermal gap prediction"],
         "validation": "Worst-case stack < 0.05mm at operating temp",
         "flashcard": "Every dimension has a tolerance. The stack of tolerances determines whether parts fit at temperature."},
        {"id": "M5", "name": "Prototype Fabrication", "phase": "PROTOTYPE",
         "deliverables": ["CNC rotor", "cast housing", "ground apex seals"],
         "validation": "CMM inspection against CAD model",
         "flashcard": "First physical article. Differences from CAD are inevitable — CMM measures exactly how much."},
        {"id": "M6", "name": "Assembly", "phase": "PROTOTYPE",
         "deliverables": ["assembled engine", "torque sequence log", "seal gap measurements"],
         "validation": "Leak-down test < 5% at TDC",
         "flashcard": "Assembly order matters. Apex seals inserted last. Housing bolts torqued in spiral pattern from center."},
        {"id": "M7", "name": "Break-In Cycle", "phase": "TEST",
         "deliverables": ["temperature log", "compression curve", "oil analysis"],
         "validation": "Compression stabilizes within 5% across all 3 chambers",
         "flashcard": "First 10 hours: vary RPM, no full load. Seals bed into housing. Compression rises then stabilizes."},
        {"id": "M8", "name": "Performance Mapping", "phase": "TEST",
         "deliverables": ["torque/RPM curve", "BSFC map", "emissions profile"],
         "validation": "Within 3% of design targets across RPM range",
         "flashcard": "Full-throttle sweep from idle to redline. Measures actual output against design predictions."},
        {"id": "M9", "name": "Durability Validation", "phase": "VALIDATE",
         "deliverables": ["100hr endurance log", "wear measurements", "failure mode analysis"],
         "validation": "No catastrophic failure, wear within spec",
         "flashcard": "Extended run at peak torque RPM. Measures how the engine ages. Catches fatigue before production."},
        {"id": "M10", "name": "Production Release", "phase": "DEPLOY",
         "deliverables": ["final BOM", "work instructions", "QC checklist"],
         "validation": "First article inspection passed, PPAP approved",
         "flashcard": "Design frozen. Manufacturing process documented. Quality gates defined at every station."},
    ]
}

# ═══════════════════════════════════════════════════════
# CHECKPOINT GENERATOR
# ═══════════════════════════════════════════════════════

class CheckpointSystem:
    """Breaks a goal into atomic checkpoints and hypercheckpoints."""
    
    def __init__(self, domain_template):
        self.template = domain_template
        self.checkpoints = domain_template.get("checkpoints", [])
        self.hypercheckpoints = domain_template.get("hypercheckpoints", [])
    
    def validate_sequence(self):
        """Verify every checkpoint has a valid next reference."""
        issues = []
        ids = {cp["id"] for cp in self.checkpoints}
        
        for cp in self.checkpoints:
            nxt = cp.get("next")
            if nxt and nxt not in ids:
                issues.append(f"Broken link: {cp['id']} → {nxt} (not found)")
            if cp["energy"] > 100:
                issues.append(f"Energy overflow: {cp['id']} has {cp['energy']}% (>100%)")
        
        return issues if issues else ["✓ Sequence valid — all links intact"]
    
    def generate_flashcards(self):
        """Produce AI-training flashcards for each checkpoint."""
        cards = []
        for cp in self.checkpoints:
            cards.append({
                "id": cp["id"],
                "front": f"State: {cp['name']}",
                "back": cp["flashcard"],
                "muscles": cp.get("muscles", []),
                "energy_percent": cp.get("energy", 0),
                "balance": cp.get("balance", "N/A"),
                "next_state": cp.get("next"),
                "hash": hashlib.sha256(cp["flashcard"].encode()).hexdigest()[:8]
            })
        return cards
    
    def generate_sprite_sheet(self):
        """Generate a sprite sheet layout for the mobility sequence."""
        n = len(self.checkpoints)
        cols = min(6, n)
        rows = (n + cols - 1) // cols
        
        sheet = {
            "layout": f"{cols}×{rows}",
            "cell_size": "64×64px",
            "total_frames": n,
            "frames": []
        }
        
        for i, cp in enumerate(self.checkpoints):
            sheet["frames"].append({
                "frame": i,
                "grid_pos": f"({i % cols}, {i // cols})",
                "label": cp["name"],
                "state": cp["state"],
                "transition_to": cp.get("next", "terminal")
            })
        
        return sheet

# ═══════════════════════════════════════════════════════
# HYPERCHECKPOINT VALIDATOR
# ═══════════════════════════════════════════════════════

class HypercheckpointValidator:
    """Validates that every checkpoint meets domain-specific hypercheckpoint rules."""
    
    RULES = {
        "thermal": "Temperature delta between adjacent states must be ≤15%",
        "mechanical": "Each checkpoint must have at least 1 validation deliverable",
        "electrical": "Power states must transition through intermediate loads",
        "structural": "Stress must not exceed material yield at any checkpoint",
    }
    
    @staticmethod
    def validate(checkpoint, rule_set):
        results = []
        for rule_name, rule_desc in HypercheckpointValidator.RULES.items():
            if rule_name in rule_set:
                results.append(f"[{rule_name}] {rule_desc}")
        return results if results else ["✓ No domain rules to validate"]

# ═══════════════════════════════════════════════════════
# FLASHCARD + SPRITE SHEET EXPORTER
# ═══════════════════════════════════════════════════════

def export_training_data(output_dir=None):
    """Export all checkpoints as training data for AI models."""
    if output_dir is None:
        output_dir = Path.home() / "Projects/trench_builder/training_checkpoints"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("╔══════════════════════════════════════════╗")
    print("║  CHECKPOINT TRAINING DATA GENERATOR      ║")
    print(f"║  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                  ║")
    print("╚══════════════════════════════════════════╝")
    print()
    
    # Human mobility
    print("═══ HUMAN MOBILITY ═══")
    hm = CheckpointSystem(HUMAN_MOBILITY)
    validation = hm.validate_sequence()
    print(f"  Validation: {validation[0]}")
    
    flashcards = hm.generate_flashcards()
    print(f"  Flashcards: {len(flashcards)} generated")
    
    sprite_sheet = hm.generate_sprite_sheet()
    print(f"  Sprite sheet: {sprite_sheet['layout']} grid, {sprite_sheet['total_frames']} frames")
    
    # Save
    with open(output_dir / "human_mobility_flashcards.json", 'w') as f:
        json.dump(flashcards, f, indent=2)
    with open(output_dir / "human_mobility_sprite_sheet.json", 'w') as f:
        json.dump(sprite_sheet, f, indent=2)
    
    # Mechanical mobility
    print("\n═══ MECHANICAL MOBILITY ═══")
    mm = CheckpointSystem(MECHANICAL_MOBILITY)
    mech_cards = []
    for hcp in mm.hypercheckpoints:
        mech_cards.append({
            "id": hcp["id"],
            "phase": hcp["phase"],
            "front": f"Phase: {hcp['name']}",
            "back": hcp["flashcard"],
            "deliverables": hcp["deliverables"],
            "validation": hcp["validation"],
        })
    
    print(f"  Hypercheckpoints: {len(mech_cards)} generated")
    
    with open(output_dir / "mechanical_mobility_hypercheckpoints.json", 'w') as f:
        json.dump(mech_cards, f, indent=2)
    
    # Cross-domain mapping
    print("\n═══ CROSS-DOMAIN MAPPING ═══")
    mapping = []
    for i, (hm_cp, mm_cp) in enumerate(zip(HUMAN_MOBILITY["checkpoints"], MECHANICAL_MOBILITY["hypercheckpoints"])):
        mapping.append({
            "sequence_step": i + 1,
            "human": f"{hm_cp['name']} ({hm_cp['energy']}% energy)",
            "mechanical": f"{mm_cp['name']} [{mm_cp['phase']}]",
            "parallel": f"Both progress from {hm_cp['name'].lower()} → {mm_cp['name'].lower()}: state transition + validation",
        })
    
    print(f"  Cross-domain pairs: {len(mapping)}")
    for m in mapping:
        print(f"    Step {m['sequence_step']:>2}: {m['human']:<25} ↔ {m['mechanical']}")
    
    with open(output_dir / "cross_domain_mapping.json", 'w') as f:
        json.dump(mapping, f, indent=2)
    
    # Training metadata
    metadata = {
        "version": "1.0",
        "generated": datetime.now().isoformat(),
        "total_flashcards": len(flashcards) + len(mech_cards),
        "total_sprite_frames": sprite_sheet["total_frames"],
        "domains": ["human_mobility", "mechanical_mobility"],
        "output_files": [
            "human_mobility_flashcards.json",
            "human_mobility_sprite_sheet.json",
            "mechanical_mobility_hypercheckpoints.json",
            "cross_domain_mapping.json",
        ],
        "usage": "Feed these JSON files to an AI training pipeline. Each flashcard is an image/text pair. Each sprite sheet maps to pixel coordinates for procedural rendering."
    }
    
    with open(output_dir / "training_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n═══ EXPORTED ═══")
    print(f"  Directory: {output_dir}")
    for f in metadata["output_files"]:
        fp = output_dir / f
        print(f"  {f}: {fp.stat().st_size} bytes")
    
    return metadata

if __name__ == "__main__":
    export_training_data()
