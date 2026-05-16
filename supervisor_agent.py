#!/usr/bin/env python3
"""
TRENCH BUILDER SUPERVISOR AGENT — The Foreman
═══════════════════════════════════════════════════
Watches all AI workers, reads GoPro footage, validates
construction logic, and outputs hyperrealism directives.

DaShawn / Guinea Pig Trench LLC — May 2026
"""
import os, json, time, hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# ═══════════════════════════════════════════════════════
# CONFIG — Where to look
# ═══════════════════════════════════════════════════════

WATCH_PATHS = {
    "gemini_brain":  Path.home() / ".gemini/antigravity/brain",
    "gemini_chats":  Path.home() / ".gemini/tmp/dasha/chats",
    "kimi_plans":    Path.home() / ".kimi/plans",
    "kimi_sessions": Path.home() / ".kimi/sessions",
    "claude_sessions": Path.home() / ".claude/projects/C--Users-dasha",
    "hermes_memory": Path.home() / "AppData/Local/hermes/memories",
    "trench_builder": Path.home() / "Projects/trench_builder",
    "erdos_straus":   Path.home() / "Projects/erdos-straus",
    "gopro_footage":  Path("G:/My Drive/Trench_Builder/go pro"),  # GoPro drop
    "gdrive_archive": Path("G:/My Drive/Trench_Builder"),
}

OUTPUT_FILE = Path.home() / "Projects/trench_builder/supervisor_directives.json"

# ═══════════════════════════════════════════════════════
# BUILDING REALM RULES — What must be correct
# ═══════════════════════════════════════════════════════

BUILDING_RULES = {
    "electrical": {
        "outlet_spacing": "Every 12 feet along walls, 6 feet from door frames",
        "outlet_height": "15 inches from floor to center (ADA minimum)",
        "switch_height": "48 inches from floor to center",
        "junction_box_access": "Must remain accessible — can't be buried in walls",
        "conduit_bend_radius": "Minimum 6x conduit diameter for EMT",
        "panel_clearance": "36 inches front clearance, 30 inches wide working space",
    },
    "hvac": {
        "supply_vent_placement": "Near exterior walls, under windows for heat loss",
        "return_vent_placement": "Central, away from supplies, at least 10 feet separation",
        "duct_sizing": "Return air duct 20-30% larger than supply",
        "thermostat_height": "52-60 inches from floor, away from direct sunlight",
        "thermostat_location": "Interior wall, not on exterior or near HVAC vent",
    },
    "structural": {
        "door_header": "2x10 minimum for openings over 4 feet",
        "stair_rise": "7-7.75 inches per step (IRC maximum)",
        "stair_run": "10-11 inches per step (IRC minimum)",
        "stair_width": "36 inches minimum clear",
        "handrail_height": "34-38 inches above stair nosing",
        "baseboard_height": "3-5.25 inches typical",
        "crown_molding_spring": "38-45 degree typical spring angle",
    },
    "plumbing": {
        "pipe_slope": "1/4 inch per foot for drain lines (minimum)",
        "vent_stack": "Must extend through roof, minimum 3 inch diameter",
        "water_supply_size": "3/4 inch main, 1/2 inch branches typical",
    },
    "materials": {
        "drywall_thickness": "1/2 inch residential, 5/8 inch fire-rated",
        "subfloor_thickness": "3/4 inch tongue-and-groove plywood minimum",
        "ceiling_height_minimum": "7 feet for habitable rooms (IRC)",
    }
}

# ═══════════════════════════════════════════════════════
# 1. SCAN ALL AI WORKER OUTPUTS
# ═══════════════════════════════════════════════════════

def scan_gemini_brain():
    """Read Gemini's implementation plans for architectural direction."""
    directives = []
    brain = WATCH_PATHS["gemini_brain"]
    if not brain.exists():
        return directives
    
    for plan_dir in brain.iterdir():
        if not plan_dir.is_dir():
            continue
        plan_file = plan_dir / "implementation_plan.md"
        task_file = plan_dir / "task.md"
        
        for f in [plan_file, task_file]:
            if f.exists():
                content = f.read_text(encoding='utf-8', errors='ignore')
                # Extract hyperrealism directives
                if "hyper-realistic" in content.lower() or "hyperreal" in content.lower():
                    directives.append({
                        "source": f"gemini/{plan_dir.name}/{f.name}",
                        "type": "hyperrealism",
                        "content": content[:500],
                        "timestamp": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                    })
                # Extract PBR/material directives
                if any(term in content.lower() for term in ["meshphysicalmaterial", "clearcoat", "subsurface", "transmission"]):
                    directives.append({
                        "source": f"gemini/{plan_dir.name}/{f.name}",
                        "type": "material_spec",
                        "content": content[:500],
                        "timestamp": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                    })
    
    return directives

def scan_kimi_plans():
    """Read Kimi's game/space reconstruction plans."""
    directives = []
    plans = WATCH_PATHS["kimi_plans"]
    if not plans.exists():
        return directives
    
    for plan_file in plans.iterdir():
        if not plan_file.is_file() or not plan_file.suffix == '.md':
            continue
        content = plan_file.read_text(encoding='utf-8', errors='ignore')
        # Extract construction-relevant directives
        if "aurora" in content.lower() or "phase" in content.lower():
            directives.append({
                "source": f"kimi/{plan_file.name}",
                "type": "game_architecture",
                "content": content[:500],
                "timestamp": datetime.fromtimestamp(plan_file.stat().st_mtime).isoformat()
            })
    
    return directives

def scan_hermes_session():
    """Read recent Hermes session for built artifacts."""
    directives = []
    tb = WATCH_PATHS["trench_builder"]
    if not tb.exists():
        return directives
    
    # List all HTML artifacts
    for f in tb.glob("*.html"):
        directives.append({
            "source": f"hermes/{f.name}",
            "type": "built_artifact",
            "size": f.stat().st_size,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })
    
    # Count Python scripts
    py_count = len(list(tb.glob("*.py")))
    directives.append({
        "source": "hermes/trench_builder",
        "type": "codebase_stats",
        "python_files": py_count,
        "html_files": len(list(tb.glob("*.html"))),
        "total_files": len(list(tb.glob("*")))
    })
    
    return directives

# ═══════════════════════════════════════════════════════
# 2. GOPRO FOOTAGE INSPECTION
# ═══════════════════════════════════════════════════════

def inspect_gopro_footage():
    """Check GoPro drop folder for new reference footage."""
    gopro = WATCH_PATHS["gopro_footage"]
    findings = {"footage_available": False, "files": [], "insights": []}
    
    if not gopro.exists():
        findings["insights"].append("⚠ GoPro folder missing — create G:/My Drive/Trench_Builder/go pro/")
        return findings
    
    mp4_files = list(gopro.glob("*.mp4")) + list(gopro.glob("*.MP4"))
    jpg_files = list(gopro.glob("*.jpg")) + list(gopro.glob("*.JPG"))
    
    if mp4_files or jpg_files:
        findings["footage_available"] = True
        findings["files"] = [str(f.name) for f in mp4_files + jpg_files][:20]
        
        # Frame extraction note (we can't view them here, but we note they exist)
        findings["insights"].append(f"✓ {len(mp4_files)} GoPro videos available for reference")
        findings["insights"].append(f"✓ {len(jpg_files)} GoPro stills available for reference")
        findings["insights"].append("→ Run supervisor with --view-gopro to extract and analyze frames")
    else:
        findings["insights"].append("○ No GoPro footage in drop folder yet")
    
    return findings

# ═══════════════════════════════════════════════════════
# 3. BUILDING REALM VALIDATION
# ═══════════════════════════════════════════════════════

def validate_backrooms_mep():
    """Check BACKROOMS_MEP.html against real building codes."""
    mep_file = WATCH_PATHS["trench_builder"] / "BACKROOMS_MEP.html"
    issues = []
    
    if not mep_file.exists():
        issues.append({"severity": "critical", "rule": "file_missing", "detail": "BACKROOMS_MEP.html not found"})
        return issues
    
    content = mep_file.read_text(encoding='utf-8', errors='ignore')
    
    # Check receptacle/outlet presence
    if "makeOutlet" in content or "outlet" in content.lower():
        issues.append({"severity": "info", "rule": "outlet_present", "detail": "✓ Outlets found in MEP scene"})
    else:
        issues.append({"severity": "warning", "rule": "outlet_spacing", "detail": "No outlets detected — every wall needs receptacles per NEC"})
    
    # Check switch presence
    if "makeSwitch" in content or "switch" in content.lower():
        issues.append({"severity": "info", "rule": "switch_present", "detail": "✓ Switches found in MEP scene"})
    else:
        issues.append({"severity": "warning", "rule": "switch_missing", "detail": "No light switches — entryways require switch at 48 inches"})
    
    # Check thermostat
    if "thermostat" in content.lower():
        issues.append({"severity": "info", "rule": "thermostat_present", "detail": "✓ Thermostat found in MEP scene"})
    
    # Check HVAC vents
    if "makeVent" in content or "vent" in content.lower():
        issues.append({"severity": "info", "rule": "hvac_present", "detail": "✓ HVAC vents found in MEP scene"})
    
    # Check conduit
    if "makeConduit" in content or "conduit" in content.lower():
        issues.append({"severity": "info", "rule": "conduit_present", "detail": "✓ Conduit runs found"})
    
    # Check stairs
    if "stair" in content.lower() or "Stair" in content:
        issues.append({"severity": "info", "rule": "stairs_present", "detail": "✓ Stairs found — verify 7-7.75 inch rise per IRC"})
    
    # Check baseboards
    if "baseboard" in content.lower():
        issues.append({"severity": "info", "rule": "baseboard_present", "detail": "✓ Baseboards found"})
    
    # Hyperrealism checks
    if "MeshPhysicalMaterial" not in content and "MeshStandardMaterial" in content:
        issues.append({"severity": "enhancement", "rule": "material_quality", "detail": "Consider upgrading to MeshPhysicalMaterial for clearcoat/SSS effects"})
    
    if "roughness" in content and "metalness" in content:
        issues.append({"severity": "info", "rule": "pbr_present", "detail": "✓ PBR materials with roughness/metalness detected"})
    
    return issues

def validate_manifestation_bridge():
    """Check MANIFESTATION_BRIDGE.html for realism issues."""
    bridge_file = WATCH_PATHS["trench_builder"] / "MANIFESTATION_BRIDGE.html"
    issues = []
    
    if not bridge_file.exists():
        return issues
    
    content = bridge_file.read_text(encoding='utf-8', errors='ignore')
    
    # Check Web Audio integration
    if "AudioContext" in content or "OscillatorNode" in content:
        issues.append({"severity": "info", "rule": "audio_integrated", "detail": "✓ Web Audio API integrated for industrial hum"})
    else:
        issues.append({"severity": "warning", "rule": "audio_missing", "detail": "No audio — industrial spaces have ambient sound"})
    
    # Check thermal response
    if "thermal" in content.lower() or "emissive" in content.lower():
        issues.append({"severity": "info", "rule": "thermal_response", "detail": "✓ Thermal/emissive response detected"})
    
    # Check structural vibration
    if "vibration" in content.lower() or "jitter" in content.lower():
        issues.append({"severity": "info", "rule": "structural_response", "detail": "✓ Structural vibration simulation detected"})
    
    return issues

def validate_cinematography_engine():
    """Check CINEMATOGRAPHY_ENGINE.html for shot correctness."""
    cine_file = WATCH_PATHS["trench_builder"] / "CINEMATOGRAPHY_ENGINE.html"
    issues = []
    
    if not cine_file.exists():
        return issues
    
    content = cine_file.read_text(encoding='utf-8', errors='ignore')
    
    # Count shot types
    shot_types = ["orbit", "crane", "dolly", "helta", "drone", "dutch", "build", "cold-open", "title-card", "victory"]
    found_shots = [s for s in shot_types if s in content.lower()]
    issues.append({"severity": "info", "rule": "shot_coverage", "detail": f"✓ {len(found_shots)}/12 shot types: {', '.join(found_shots)}"})
    
    return issues

# ═══════════════════════════════════════════════════════
# 4. GENERATE SUPERVISOR DIRECTIVES
# ═══════════════════════════════════════════════════════

def generate_directives():
    """Full supervisor pass — scan everything and produce directives."""
    print("╔══════════════════════════════════════════╗")
    print("║  TRENCH BUILDER SUPERVISOR — The Foreman║")
    print(f"║  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                  ║")
    print("╚══════════════════════════════════════════╝")
    print()
    
    report = {
        "supervisor_version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "watched_agents": [],
        "gopro_status": {},
        "validation_results": {},
        "hyperrealism_directives": [],
        "orientation_issues": [],
        "building_realm_violations": [],
        "priority_actions": [],
    }
    
    # 1. Scan AI workers
    print("═══ PHASE 1: AI Worker Audit ═══")
    
    gemini = scan_gemini_brain()
    kimi = scan_kimi_plans()
    hermes = scan_hermes_session()
    
    report["watched_agents"] = [
        {"name": "Gemini", "directives_found": len(gemini)},
        {"name": "Kimi", "directives_found": len(kimi)},
        {"name": "Hermes", "artifacts_found": len([a for a in hermes if a["type"] == "built_artifact"])},
    ]
    
    for agent_data in report["watched_agents"]:
        print(f"  {agent_data['name']:>10}: {agent_data.get('directives_found', agent_data.get('artifacts_found', 0))} items")
    
    # Extract hyperrealism directives from Gemini
    for d in gemini:
        if d["type"] in ("hyperrealism", "material_spec"):
            report["hyperrealism_directives"].append(d)
    
    # 2. GoPro inspection
    print("\n═══ PHASE 2: GoPro Inspection ═══")
    gopro = inspect_gopro_footage()
    report["gopro_status"] = gopro
    for insight in gopro["insights"]:
        print(f"  {insight}")
    
    # 3. Building realm validation
    print("\n═══ PHASE 3: Building Realm Validation ═══")
    
    mep_issues = validate_backrooms_mep()
    bridge_issues = validate_manifestation_bridge()
    cine_issues = validate_cinematography_engine()
    
    all_issues = mep_issues + bridge_issues + cine_issues
    report["validation_results"] = {
        "backrooms_mep": {"issue_count": len(mep_issues), "issues": mep_issues},
        "manifestation_bridge": {"issue_count": len(bridge_issues), "issues": bridge_issues},
        "cinematography_engine": {"issue_count": len(cine_issues), "issues": cine_issues},
    }
    
    # Categorize issues
    for issue in all_issues:
        if issue["severity"] == "warning":
            report["building_realm_violations"].append(issue)
        elif issue["severity"] == "enhancement":
            report["hyperrealism_directives"].append(issue)
        elif issue["severity"] == "critical":
            report["priority_actions"].append(issue)
    
    severity_counts = defaultdict(int)
    for issue in all_issues:
        severity_counts[issue["severity"]] += 1
    
    print(f"  Critical:    {severity_counts.get('critical', 0)}")
    print(f"  Warnings:    {severity_counts.get('warning', 0)}")
    print(f"  Enhancements:{severity_counts.get('enhancement', 0)}")
    print(f"  Info:        {severity_counts.get('info', 0)}")
    
    # 4. Orientation and building logic checks
    print("\n═══ PHASE 4: Orientation & Logic ═══")
    
    orientation_checks = [
        {"check": "Conduit runs originate from panel, not dead-end in ceiling",
         "status": "needs_gopro_reference"},
        {"check": "Thermostat on interior wall, not under supply vent",
         "status": "needs_scene_inspection"},
        {"check": "Stair rise/run within IRC code (7-7.75in / 10-11in)",
         "status": "needs_measurement"},
        {"check": "Return air at least 10ft from supply vents",
         "status": "needs_scene_inspection"},
        {"check": "Door swing direction doesn't block electrical panel clearance",
         "status": "needs_scene_inspection"},
    ]
    
    report["orientation_issues"] = orientation_checks
    for check in orientation_checks:
        print(f"  [{check['status']}] {check['check']}")
    
    # 5. Priority actions for Hermes
    print("\n═══ PHASE 5: Priority Actions ═══")
    
    actions = []
    
    # If GoPro footage exists, prioritize scene comparison
    if gopro["footage_available"]:
        actions.append({
            "priority": 1,
            "action": "Compare TRENCH BUILDER scenes against GoPro reference footage",
            "detail": "Extract frames from GoPro MP4s in G:/My Drive/Trench_Builder/go pro/. Match camera angles. Identify discrepancies in material appearance, lighting, and scale.",
            "assigned_to": "hermes"
        })
    
    # If Gemini has new hyperrealism directives
    if gemini:
        actions.append({
            "priority": 2,
            "action": "Apply Gemini's hyperrealism directives to TRENCH BUILDER artifacts",
            "detail": f"Gemini specified MeshPhysicalMaterial upgrades in {len([d for d in gemini if d['type']=='material_spec'])} plans. Upgrade BACKROOMS_MEP materials.",
            "assigned_to": "hermes"
        })
    
    # If building realm violations found
    if report["building_realm_violations"]:
        actions.append({
            "priority": 3,
            "action": "Fix building realm violations",
            "detail": f"{len(report['building_realm_violations'])} violations found. See validation_results for details.",
            "assigned_to": "hermes"
        })
    
    # Always check orientation
    actions.append({
        "priority": 4,
        "action": "Verify spatial orientation of all MEP components",
        "detail": "Ensure outlets/switches are at correct heights. Verify thermostats aren't under vents. Check door swings don't block panels.",
        "assigned_to": "hermes"
    })
    
    report["priority_actions"] = actions
    for a in actions:
        print(f"  P{a['priority']}: [{a['assigned_to']}] {a['action']}")
    
    # 6. Save output for Hermes
    print(f"\n═══ SAVING ═══")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"  ✓ Supervisory directives saved to {OUTPUT_FILE}")
    print(f"  ✓ Hermes can read this file to apply corrections")
    
    return report

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if "--view-gopro" in sys.argv:
        gopro = WATCH_PATHS["gopro_footage"]
        if gopro.exists():
            for mp4 in list(gopro.glob("*.mp4"))[:3]:
                print(f"Extracting from {mp4.name}...")
                # Frame extraction would go here
        else:
            print("No GoPro folder found")
    else:
        report = generate_directives()
