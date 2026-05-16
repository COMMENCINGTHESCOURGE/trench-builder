#!/usr/bin/env python
"""
DELTA FINDER v1.0 — Research Gap Analysis & Knowledge Catapult
=============================================================
Scans all projects, agent sessions, memory, and research corpus.
Identifies deltas between current state and cutting edge.
Generates prioritized action plans.

Domain coverage:
  - Rendering theory (22 principles + 16 extensions)
  - CAD/mechanical simulation (Onshape engine assembly)
  - Electromagnetic/Powertrain visualization
  - GPU compute (Kaggle, Colab, HuggingFace, Groq)
  - AI agent swarm (Kimi, Claude, Gemini, Hermes)
  - Multi-sensory simulation (audio + physics + rendering)

Usage: python delta_finder.py [--domain all|rendering|cad|simulation]
"""

import os, json, re, sys
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════
# 1. KNOWLEDGE CORPUS — What we know exists
# ═══════════════════════════════════════════════════════

RENDERING_PRINCIPLES = {
    # From 22-principle document
    "light_transport":     {"status": "implemented", "where": "v3/v4 ACES+PBR pipeline"},
    "global_illumination": {"status": "partial",    "where": "v4 SSAO pass (faux GI)"},
    "pbr_materials":       {"status": "implemented", "where": "MeshPhysicalMaterial throughout"},
    "microfacet":          {"status": "implemented", "where": "roughness/metalness maps"},
    "fresnel":             {"status": "implemented", "where": "clearcoat+specular on skin"},
    "color_science":       {"status": "implemented", "where": "ACES tone mapping, 315 named blacks"},
    "hyperrealism":        {"status": "implemented", "where": "film grain + god rays"},
    "vanishing_points":    {"status": "implemented", "where": "VP placement in v3"},
    "atmospheric":         {"status": "implemented", "where": "FogExp2 distance fog"},
    "caustics":            {"status": "implemented", "where": "v5 subwoofer: screen-space caustic projection"},
    "noise_realism":       {"status": "implemented", "where": "v4 film grain shader"},
    "mechanical_physics":  {"status": "implemented", "where": "v4 physics engine + v5 cone animation"},
    "subsurface":          {"status": "implemented", "where": "transmission+thickness on skin"},
    "volumetrics":         {"status": "implemented", "where": "v4 god rays pass"},
    "motion_blur":         {"status": "implemented", "where": "GoPro temporal frames"},
    "raytracing":          {"status": "partial",    "where": "v4 raytrace toggle (boost only)"},
    "neural_rendering":    {"status": "planned",    "where": "training data exported, no model yet"},
    "optical_illusions":   {"status": "planned",    "where": "v5 roadmap — forced perspective"},
    "spectral":            {"status": "started",    "where": "v5 wave-optics iridescence on terminals"},
    "differentiable":      {"status": "missing",     "where": "no differentiable renderer"},
    "hybrid_rendering":    {"status": "started",   "where": "v5: physics+thermal+EM+caustics"},
    "core_principle":      {"status": "implemented", "where": "light+material+time coherence"},
}

PERCEPTUAL_EXTENSIONS = {
    # From 16-principle extension document
    "perception_sim":       {"status": "planned",    "where": "v5 roadmap"},
    "unified_stack":        {"status": "implemented", "where": "v4 layers: geo/materials/lighting/post"},
    "energy_simulation":    {"status": "implemented", "where": "v5: thermal radiation on voice coil + magnet"},
    "temporal_realism":     {"status": "partial",    "where": "GoPro frames, no eye tracking"},
    "physics_beyond_rigid": {"status": "started",   "where": "v4 physics + v5 cone electrodynamic response"},
    "wave_optics":          {"status": "implemented", "where": "v5: iridescent thin-film interference on terminals"},
    "spectral_computation": {"status": "started",   "where": "v5: HSL-based spectral shifts on iridescent materials"},
    "perceptual_ai":        {"status": "planned",    "where": "training data ready, no model trained"},
    "optical_illusions_sys": {"status": "planned",   "where": "v5: forced perspective engine"},
    "mechanical_rendering": {"status": "started",   "where": "v5 subwoofer animation, CAD imported"},
    "multisensory":         {"status": "started",   "where": "v5: audio frequency → visual cone + thermal + EM"},
    "hierarchical_realism": {"status": "implemented", "where": "fog, shadow, lighting priority"},
    "procedural_entropy":   {"status": "missing",     "where": "no aging/wear/dust systems"},
    "simulation_merge":     {"status": "started",   "where": "v5: thermal+EM+caustics unified in one scene"},
    "coherence":            {"status": "started",   "where": "v5: audio freq → cone → thermal → EM → caustics chain"},
    "perceptual_physics":   {"status": "started",   "where": "v5: all systems respond to one frequency input"},
}

# ═══════════════════════════════════════════════════════
# 2. SCAN PROJECTS — What we've built
# ═══════════════════════════════════════════════════════

def scan_project(project_path):
    """Scan a project directory for key files and capabilities."""
    path = Path(project_path)
    if not path.exists():
        return {"exists": False}
    
    files = list(path.rglob("*"))
    html_files = [f for f in files if f.suffix == '.html']
    py_files = [f for f in files if f.suffix == '.py']
    stl_files = [f for f in files if f.suffix == '.stl']
    md_files = [f for f in files if f.suffix == '.md']
    
    return {
        "exists": True,
        "path": str(path),
        "total_files": len(files),
        "html_artifacts": len(html_files),
        "python_scripts": len(py_files),
        "cad_parts": len(stl_files),
        "docs": len(md_files),
        "largest_html": max([f.stat().st_size for f in html_files]) if html_files else 0,
    }

# ═══════════════════════════════════════════════════════
# 3. DELTA ANALYSIS — Find the gaps
# ═══════════════════════════════════════════════════════

def find_deltas():
    """Core delta analysis engine."""
    
    # Scan all projects
    projects = {
        "trench_builder": scan_project(os.path.expanduser("~/Projects/trench_builder")),
        "avatar": scan_project(os.path.expanduser("~/Projects/avatar")),
        "erdos_straus": scan_project(os.path.expanduser("~/Projects/erdos-straus")),
        "ale": scan_project(os.path.expanduser("~/Projects/ale")),
    }
    
    # Count statuses
    statuses = {"implemented": 0, "partial": 0, "started": 0, "planned": 0, "missing": 0}
    
    all_principles = {**RENDERING_PRINCIPLES, **PERCEPTUAL_EXTENSIONS}
    
    for name, data in all_principles.items():
        statuses[data["status"]] += 1
    
    total = len(all_principles)
    
    # Find highest-leverage deltas
    missing_high_impact = []
    for name, data in all_principles.items():
        if data["status"] in ("missing", "planned"):
            # Determine impact
            impact = 1
            if name in ("caustics", "wave_optics", "energy_simulation", 
                       "mechanical_rendering", "spectral_computation"):
                impact = 3  # High impact — unlocks new visualization domains
            elif name in ("perceptual_ai", "procedural_entropy", "multisensory"):
                impact = 2  # Medium impact — enhances existing systems
            
            missing_high_impact.append({
                "principle": name,
                "status": data["status"],
                "impact": impact,
                "location": data["where"],
            })
    
    missing_high_impact.sort(key=lambda x: -x["impact"])
    
    return {
        "total_principles": total,
        "status_breakdown": statuses,
        "coverage_pct": round(statuses["implemented"] / total * 100, 1),
        "highest_leverage_deltas": missing_high_impact[:5],
        "projects": projects,
    }

# ═══════════════════════════════════════════════════════
# 4. CROSS-AGENT INSIGHT EXTRACTION
# ═══════════════════════════════════════════════════════

def extract_agent_insights():
    """Extract actionable insights from agent session histories."""
    insights = []
    
    # Gemini CLI insights
    gemini_brain = Path.home() / ".gemini/antigravity/brain"
    if gemini_brain.exists():
        for entry in gemini_brain.iterdir():
            if entry.is_dir():
                plan = entry / "implementation_plan.md"
                if plan.exists():
                    with open(plan) as f:
                        content = f.read()
                        # Extract technologies mentioned
                        techs = re.findall(r'WebGL|WebGPU|Three\.js|PBR|Verlet|SSS|Compute Shader|Path Trac\w+|Ray Trac\w+|Gaussian Splat\w+|NeRF', content)
                        if techs:
                            insights.append({
                                "source": f"Gemini brain: {entry.name[:8]}",
                                "technologies": list(set(techs)),
                                "summary": content[:200].strip()
                            })
    
    # Kimi CLI insights
    kimi_history = Path.home() / ".kimi/user-history"
    if kimi_history.exists():
        for f in kimi_history.glob("*.jsonl"):
            size = f.stat().st_size
            insights.append({
                "source": f"Kimi history: {f.name}",
                "size_kb": round(size / 1024),
                "extractable": size > 10000  # Only large histories have substance
            })
    
    return insights

# ═══════════════════════════════════════════════════════
# 5. ACTION GENERATOR — What to build next
# ═══════════════════════════════════════════════════════

def generate_action_plan(deltas):
    """Generate a prioritized action plan from deltas."""
    
    actions = []
    
    for d in deltas["highest_leverage_deltas"]:
        principle = d["principle"]
        
        if principle == "caustics":
            actions.append({
                "priority": 1,
                "action": "Add simplified caustics via screen-space photon splatting",
                "domain": "rendering",
                "impact": "Unlocks: glass, water, gemstone realism",
                "effort": "medium",
                "file": "TRENCH_BUILDER_v5.html",
                "technique": "SS caustics from sun direction + water surface normal perturbation"
            })
        
        elif principle == "mechanical_rendering":
            actions.append({
                "priority": 1,
                "action": "Animate Onshape engine assembly with physics-based crank rotation",
                "domain": "simulation",
                "impact": "Unlocks: full powertrain visualization, NVH analysis overlay",
                "effort": "medium",
                "file": "TRENCH_BUILDER_v5.html",
                "technique": "Sinusoidal crank rotation → piston oscillation → vibration field"
            })
        
        elif principle == "energy_simulation":
            actions.append({
                "priority": 2,
                "action": "Add thermal radiation shader (heat haze) to running engine",
                "domain": "rendering",
                "impact": "Unlocks: thermal mapping visualization",
                "effort": "low",
                "file": "TRENCH_BUILDER_v5.html",
                "technique": "Screen-space distortion pass driven by engine temperature gradient"
            })
        
        elif principle == "procedural_entropy":
            actions.append({
                "priority": 3,
                "action": "Implement material aging: dust accumulation, scratch patterns",
                "domain": "simulation",
                "impact": "Increases perceptual realism (Principle 13)",
                "effort": "low",
                "file": "TRENCH_BUILDER_v5.html",
                "technique": "Time-based procedural wear textures overlaid on materials"
            })
    
    return actions

# ═══════════════════════════════════════════════════════
# 6. MAIN — Run the delta finder
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════╗")
    print("║     DELTA FINDER v1.0 — Research Gap Engine     ║")
    print("║     DaShawn / Guinea Pig Trench LLC             ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    # Run delta analysis
    deltas = find_deltas()
    
    print("═══ RESEARCH COVERAGE ═══")
    print(f"  Total principles tracked: {deltas['total_principles']}")
    print(f"  Implemented: {deltas['status_breakdown']['implemented']} ({deltas['coverage_pct']}%)")
    print(f"  Partial:     {deltas['status_breakdown']['partial']}")
    print(f"  Started:     {deltas['status_breakdown']['started']}")
    print(f"  Planned:     {deltas['status_breakdown']['planned']}")
    print(f"  Missing:     {deltas['status_breakdown']['missing']}")
    print()
    
    print("═══ PROJECT INVENTORY ═══")
    for name, proj in deltas["projects"].items():
        if proj.get("exists"):
            print(f"  {name}: {proj['total_files']} files, {proj['cad_parts']} CAD, {proj['html_artifacts']} HTML")
    
    print()
    print("═══ HIGHEST-LEVERAGE DELTAS ═══")
    for i, d in enumerate(deltas["highest_leverage_deltas"], 1):
        print(f"  {i}. {d['principle']} [{d['status']}] — impact={d['impact']}")
        print(f"     Current: {d['location']}")
    print()
    
    print("═══ CROSS-AGENT INSIGHTS ═══")
    insights = extract_agent_insights()
    for ins in insights:
        print(f"  {ins['source']}")
        if 'technologies' in ins:
            print(f"    Technologies: {', '.join(ins['technologies'])}")
    print()
    
    print("═══ RECOMMENDED ACTIONS ═══")
    actions = generate_action_plan(deltas)
    for a in sorted(actions, key=lambda x: x["priority"]):
        print(f"  P{a['priority']}: {a['action']}")
        print(f"     Impact: {a['impact']} | Effort: {a['effort']} | → {a['file']}")
    print()
    
    print("═══ CATAPULT TARGET ═══")
    print("  Next strike: TRENCH BUILDER v5")
    print("  Domain: Perceptual Physics Rendering")
    print("  Key unlocks: Engine animation + caustics + thermal + aging")
    print("  Deployment: Single-file HTML (Three.js CDN, zero deps)")
    print()
    
    # Export JSON
    export = {
        "timestamp": datetime.now().isoformat(),
        "deltas": deltas,
        "actions": actions,
        "insights": insights,
    }
    
    export_path = Path.home() / "Projects/trench_builder/delta_report.json"
    with open(export_path, 'w') as f:
        json.dump(export, f, indent=2, default=str)
    print(f"  Report exported: {export_path}")
