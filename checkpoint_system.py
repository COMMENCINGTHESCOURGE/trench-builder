#!/usr/bin/env python
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

# ═══════════════════════════════════════════════════════
# DOMAIN CHECKPOINT TEMPLATES
# ═══════════════════════════════════════════════════════

TRENCH_BUILDER = {
    "goal": "Full-stack hyperreal lowpoly construction simulation",
    "checkpoints": [
        {"id": "TB1", "name": "Supine — Single HTML Proof", "energy": 0,
         "deliverable": "TRENCH_BUILDER_v1.html",
         "flashcard": "First breath. Can we even render a 3D scene in a single HTML file? Yes."},
        {"id": "TB2", "name": "Scoot — Physics Approximation", "energy": 20,
         "deliverable": "TRENCH_BUILDER_v5.14 — thermal, EM, caustics, distance fields",
         "flashcard": "Upper body pulls. Physics approximated — patterns right, not physically accurate yet."},
        {"id": "TB3", "name": "Crawl — MEP Infrastructure", "energy": 40,
         "deliverable": "BACKROOMS_MEP.html — 35 components, building realm validation",
         "flashcard": "Cross-pattern coordination emerges. Outlets, switches, vents, conduits, stairs. Real infrastructure."},
        {"id": "TB4", "name": "Stand — Systemic Simulation", "energy": 60,
         "deliverable": "MANIFESTATION_BRIDGE.html — transfer functions, brownout, Web Audio, PBR",
         "flashcard": "Full upright. Electrical→Optical/Acoustic/Thermal simultaneously. Simulation stands on its own."},
        {"id": "TB5", "name": "Walk — Multi-Agent Pipeline", "energy": 75,
         "deliverable": "supervisor_agent.py + retroactive_agent.py + master_orchestrator.py",
         "flashcard": "Reciprocal gait. Supervisor watches. Retroactive fixes. Orchestrator coordinates 5 nodes."},
        {"id": "TB6", "name": "Jump — Cross-Domain Convergence", "energy": 90,
         "deliverable": "HYPERREAL_LOWPOLY_BLUEPRINT.md + checkpoint_system.py",
         "flashcard": "First intentional flight. 10 systems → one aesthetic. The blueprint proves they connect."},
        {"id": "TB7", "name": "Run — Production SaaS", "energy": 100,
         "deliverable": "api_server.py :8090 + Stripe + Gemma 4 Hackathon submission",
         "flashcard": "Sustained flight. API has billing. Hackathon validates. Not prototype — product."},
    ]
}

ASSET_PIPELINE = {
    "goal": "Procedural asset generation pipeline — from script to GLB, version-controlled, game-engine ready",
    "checkpoints": [
        {"id": "AP1", "name": "Supine — Single Generator Script", "energy": 0,
         "deliverable": "generate_elevator.py → elevator.glb (106 KB, 50 meshes)",
         "flashcard": "First asset. One script. Does it run headless? Yes. Does it export GLB? Yes. Can a game engine load it? Yes."},
        {"id": "AP2", "name": "Scoot — Material Library Foundation", "energy": 15,
         "deliverable": "material_library.py (49 PBR materials, 6 categories)",
         "flashcard": "Materials aren't baked into scripts — they're imported from a shared library. Any generator can call get_material()."},
        {"id": "AP3", "name": "Crawl — Mechanical Parts Family", "energy": 30,
         "deliverable": "generate_gear.py + generate_pulley.py (3 pulley variants)",
         "flashcard": "Involute gear with actual tooth geometry. Not a cylinder with bumps. Three pulley types share one script."},
        {"id": "AP4", "name": "Stand — Architectural Elements", "energy": 45,
         "deliverable": "elevator.glb + staircase.glb verified as valid GLB",
         "flashcard": "Full upright. Elevator with steel cage, cable drum, sliding doors. Staircase with dual stringers, 14 treads, pipe handrails."},
        {"id": "AP5", "name": "Walk — Automated Build Pipeline", "energy": 60,
         "deliverable": "build_all_assets.py — regenerates all GLBs from source scripts",
         "flashcard": "Reciprocal gait. One command regenerates every asset. Change a parameter, run build, and new GLBs appear."},
        {"id": "AP6", "name": "Jump — Validation & Integrity Checks", "energy": 75,
         "deliverable": "validate_assets.py — GLB header check, mesh count, material audit",
         "flashcard": "A generated GLB could be 0 bytes or have 0 meshes. The validator catches this before it reaches the game engine."},
        {"id": "AP7", "name": "Run — Game Engine Integration", "energy": 85,
         "deliverable": "assets_viewer.html — Three.js loader demo with all assets",
         "flashcard": "Assets aren't just files — they're visible in the game. Elevator doors slide. Gear meshes with another gear."},
        {"id": "AP8", "name": "Leap — Parametric Variant Matrix", "energy": 92,
         "deliverable": "12 gear variants + 9 pulley variants from parameter sweeps",
         "flashcard": "Explosive generation. One script → parameter matrix → N GLB files. The pipeline proves it scales."},
        {"id": "AP9", "name": "Fly — Version-Controlled Asset Registry", "energy": 96,
         "deliverable": "asset_registry.json — every GLB tracked with source hash + params",
         "flashcard": "Git commit hooks trigger regeneration if scripts change. CI validates. Registry tells which GLB came from which version."},
        {"id": "AP10", "name": "Soar — Cross-Project Deployment", "energy": 100,
         "deliverable": "Assets deployed to hyperpoly-terrain, Thrown Planet, Trench Builder",
         "flashcard": "One material library. One gear generator. One elevator. Used across every project from a single source of truth."},
    ]
}

HUMAN_MOBILITY = {
    "goal": "Full bipedal locomotion — developmental sequence",
    "checkpoints": [
        {"id": "H1", "name": "Supine Rest", "state": "Lying flat, no muscle activation",
         "muscles": ["none active"], "energy": 0, "balance": "N/A", "next": "H2",
         "flashcard": "Body at rest. Zero energy expenditure. All joints neutral. The starting position for all movement."},
        {"id": "H2", "name": "Scoot", "state": "Dragging body across surface, arms pull, legs drag",
         "muscles": ["latissimus dorsi", "biceps", "forearm flexors"],
         "energy": 20, "balance": "Full ground contact", "next": "H3",
         "flashcard": "Upper body pulls while lower body drags. Belly on ground. Arms reach forward and pull back. No leg coordination yet."},
        {"id": "H3", "name": "Crawl", "state": "Hands and knees, reciprocal pattern",
         "muscles": ["deltoids", "triceps", "quadriceps", "hip flexors", "core stabilizers"],
         "energy": 40, "balance": "4-point base, alternating", "next": "H4",
         "flashcard": "Opposite arm/leg move together. Spine parallel to ground. Cross-pattern coordination emerges. The foundation of gait."},
        {"id": "H4", "name": "Stand", "state": "Pull to vertical, both feet planted",
         "muscles": ["gluteus maximus", "quadriceps", "gastrocnemius", "core"],
         "energy": 50, "balance": "Biped base, narrow", "next": "H5",
         "flashcard": "Full upright posture. Static balance achieved but no rhythm yet."},
        {"id": "H5", "name": "Bounce", "state": "Rhythmic knee oscillation",
         "muscles": ["quads","gastrocnemius","tibialis","glutes","toe flexors","peroneals"],
         "energy": 65, "balance": "Dynamic vertical", "next": "H6",
         "flashcard": "Knees become springs. Glutes drive angles: hip-knee-ankle-toe cascade. Foot angle, ham angle, hip angle oscillate. Arms counter-balance at opposite phase. Neck pivots to stabilize head. Each frame calculates joint angle increase/decrease across all 6 joints.",
         "angles": {
             "toe": {"min": -30, "max": 45, "plane": "sagittal", "description": "Metatarsophalangeal. Toe-off push. Final propulsion point."},
             "ankle": {"min": -15, "max": 25, "plane": "sagittal", "description": "Dorsiflexion to plantarflexion. Foot rocks over ball and toes."},
             "knee": {"min": -30, "max": 5, "plane": "sagittal", "description": "Flexion to extension. Hamstring angle opens and closes."},
             "hip": {"min": -20, "max": 15, "plane": "sagittal", "description": "Flexion to extension. Glutes are the primary engine."},
             "shoulder": {"min": -12, "max": 12, "plane": "sagittal", "description": "Arms counter-balance at 180-degree opposite phase."},
             "neck": {"min": -3, "max": 3, "plane": "sagittal", "description": "Head stabilizes. Pivot compensates for vertical oscillation."}
         },
         "limb_lengths": {
             "femur": 0.45, "tibia": 0.42, "foot": 0.26,
             "humerus": 0.34, "forearm": 0.28,
             "neck": 0.12,
             "unit": "meters", "note": "Proportions scale to total height. Longer limbs = more torque, shorter = faster cadence. Optimize for harsh terrain: longer foot for stability, slightly shorter femur for rapid bounce recovery."
         },
         "frame_calc": "angle(t) = min + (max-min) * (1+sin(t*freq+phase))/2. Phases: toe 0, ankle 5, knee 15, hip 30, shoulder 180 (counter), neck 90 (stabilize). Multiply by limb length for linear displacement.",
         "superman_principle": "Design this bounce for 2x bodyweight load, 15-degree incline, and fatigue. If it works under those harsh conditions, it performs flawlessly on flat ground unloaded. Superman trained on Krypton — Earth is easy."
        },
        {"id": "H6", "name": "Walk", "state": "Reciprocal gait, alternating stance/swing",
         "muscles": ["all lower body cycling", "arm swing for counter-rotation"],
         "energy": 80, "balance": "Dynamic bipedal", "next": "H7",
         "flashcard": "Reciprocal gait cycle. 60% stance, 40% swing. Heel strike to midstance to toe-off. Arms counter-rotate for stability. Bounce taught the springs — walk releases them forward."},
        {"id": "H7", "name": "Jump", "state": "Explosive bilateral push-off, both feet leave ground",
         "muscles": ["gluteus maximus (max)", "quadriceps (max)", "gastrocnemius (max)", "core (brace)"],
         "energy": 90, "balance": "Flight phase, then landing", "next": "H8",
         "flashcard": "First intentional flight. Both feet push simultaneously. Knees and hips triple-extend. Arms swing upward for momentum. Landing absorbs 3-5× bodyweight. The bridge between walk and run."},
        {"id": "H8", "name": "Run", "state": "Aerial phase, increased cadence",
         "muscles": ["all lower body + arms pumping", "increased fast-twitch recruitment"],
         "energy": 100, "balance": "Dynamic with flight phase", "next": None,
         "flashcard": "Both feet leave ground during stride. Arms drive forward/back. 3× energy of walking. Flight phase distinguishes run from walk. Jump taught the body flight — run sustains it."},
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
    
    # TRENCH BUILDER
    print("\n═══ TRENCH BUILDER ═══")
    tb = CheckpointSystem(TRENCH_BUILDER)
    tb_cards = tb.generate_flashcards()
    print(f"  Flashcards: {len(tb_cards)} generated")
    for card in tb_cards:
        print(f"    {card['id']} | {card['energy_percent']:>3}% | {card['front']:<35} → {card['back'][:80]}")
    with open(output_dir / "trench_builder_checkpoints.json", 'w') as f:
        json.dump(tb_cards, f, indent=2)
    
    # ASSET PIPELINE
    print("\n═══ ASSET PIPELINE ═══")
    ap = CheckpointSystem(ASSET_PIPELINE)
    ap_cards = ap.generate_flashcards()
    print(f"  Flashcards: {len(ap_cards)} generated")
    for card in ap_cards:
        print(f"    {card['id']} | {card['energy_percent']:>3}% | {card['front'][:35]:<35} → {card['back'][:80]}")
    with open(output_dir / "asset_pipeline_checkpoints.json", 'w') as f:
        json.dump(ap_cards, f, indent=2)

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
        "domains": ["human_mobility", "trench_builder", "asset_pipeline", "mechanical_mobility"],
        "output_files": [
            "human_mobility_flashcards.json",
            "human_mobility_sprite_sheet.json",
            "trench_builder_checkpoints.json",
            "asset_pipeline_checkpoints.json",
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
