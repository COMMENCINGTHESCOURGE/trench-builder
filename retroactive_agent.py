#!/usr/bin/env python
"""
RETROACTIVE CORRECTION AGENT — The Auditor
═══════════════════════════════════════════════════
Scans ALL existing artifacts and applies fixes retroactively.
Runs after the self-critique protocol is updated with new rules.
Fixes what was built before the rules existed.

DaShawn / Guinea Pig Trench LLC — May 2026
"""
import os, json, re, shutil
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# ═══════════════════════════════════════════════════════
# AUDIT SCOPE — Everything we've built
# ═══════════════════════════════════════════════════════

base_scratch = Path("C:/Users/dasha/.gemini/antigravity-ide/scratch")
AUDIT_PATHS = {
    "trench_builder": base_scratch / "trench-builder" if (base_scratch / "trench-builder").exists() else Path.home() / "Projects/trench_builder",
    "erdos_straus":   base_scratch / "erdos-straus-solver" if (base_scratch / "erdos-straus-solver").exists() else Path.home() / "Projects/erdos-straus",
    "gdrive_trench":  Path("G:/My Drive/Trench_Builder"),
    "gdrive_resonance": Path("G:/My Drive/Resonance_Archive"),
    "desktop":        Path.home() / "Desktop",
}

# ═══════════════════════════════════════════════════════
# CORRECTION RULES — What to fix retroactively
# ═══════════════════════════════════════════════════════

RULES = [
    # ── Path Corrections ──
    {
        "id": "scattered_api_keys",
        "description": "API keys should be in Hermes config, not loose files",
        "pattern": "**/api_key*.txt|**/key*.txt|**/*.env.bak",
        "action": "flag_for_review",  # can't auto-delete, user must confirm
        "severity": "warning"
    },
    {
        "id": "missing_go_pro_folder",
        "description": "Create GoPro drop folder if missing",
        "check": lambda: (Path("G:/My Drive/Trench_Builder/go pro").mkdir(parents=True, exist_ok=True) or True) 
                        if Path("G:/My Drive").exists() else False,
        "action": "auto_create",
        "severity": "info"
    },
    {
        "id": "missing_daily_logs_folder",
        "description": "Create daily logs folder for Erdos-Straus",
        "check": lambda: (Path.home() / "Projects/erdos-straus/daily_logs").mkdir(parents=True, exist_ok=True) or True,
        "action": "auto_create",
        "severity": "info"
    },
    
    # ── File Location Corrections ──
    {
        "id": "steps_file_duplication",
        "description": "ERDOS_STRAUS_STEPS.txt and 10_DAILY_SCRIPTS.txt should exist in Desktop, Documents, and G: drive",
        "check": lambda: check_steps_files(),
        "action": "auto_copy",
        "severity": "info"
    },
    
    # ── HTML Artifact Corrections ──
    {
        "id": "html_uses_standard_material",
        "description": "Flag HTML files using MeshStandardMaterial instead of MeshPhysicalMaterial",
        "pattern": "*.html",
        "check_content": "MeshStandardMaterial",
        "suggest": "MeshPhysicalMaterial with clearcoat/transmission for hyperrealism (Gemini directive)",
        "action": "flag_for_review",
        "severity": "enhancement"
    },
    {
        "id": "html_missing_outlet_height",
        "description": "Flag MEP HTML files where outlets may not be at 15-inch height",
        "pattern": "BACKROOMS_MEP.html",
        "check_content": "outlet",
        "verify": "y=0.38",  # 15 inches = ~0.38 meters — check if outlet position uses this
        "action": "flag_for_review",
        "severity": "warning"
    },
    
    # ── Python Script Corrections ──
    {
        "id": "python_uses_python3_not_python",
        "description": "Flag scripts using 'python3' in shebang — should use explicit Python path or 'python'",
        "pattern": "*.py",
        "check_content": "#!/usr/bin/env py" + "thon3",
        "suggest": "Use explicit Python path or '#!/usr/bin/env python' for Windows compatibility",
        "action": "flag_for_review",
        "severity": "info"
    },
    {
        "id": "python_uses_python3_direct_path",
        "description": "Flag scripts using direct /usr/bin/python3 path in shebang",
        "pattern": "*.py",
        "check_content": "#!/usr/bin/py" + "thon3",
        "suggest": "Use explicit Python path or '#!/usr/bin/env python' for Windows compatibility",
        "action": "flag_for_review",
        "severity": "info"
    },
    {
        "id": "python_fcntl_import",
        "description": "Flag any scripts importing fcntl (doesn't exist on Windows)",
        "pattern": "*.py",
        "check_content": "import " + "fcntl",
        "suggest": "Replace with file-based locking (atomic_writer.py pattern)",
        "action": "flag_for_review",
        "severity": "critical"
    },
    {
        "id": "python_statistics_unused",
        "description": "Flag scripts importing 'statistics' module",
        "pattern": "*.py",
        "check_content": "import " + "statistics",
        "suggest": "Replace with numpy (np.mean, np.std) — already done in procedural_video_learner.py",
        "action": "flag_for_review",
        "severity": "info"
    },
    
    # ── Cron Job Corrections ──
    {
        "id": "cron_duplicate_check",
        "description": "Check for duplicate/overlapping cron jobs",
        "check": lambda: check_cron_overlap(),
        "action": "flag_for_review",
        "severity": "warning"
    },
    
    # ── Missing Infrastructure ──
    {
        "id": "missing_readme",
        "description": "Flag project directories without README.md",
        "check": lambda: check_missing_readmes(),
        "action": "flag_for_review",
        "severity": "info"
    },
    
    # ── Hyperrealism Standard Checks ──
    {
        "id": "scene_missing_rim_light",
        "description": "Flag 3D scenes that may be missing rim lights on dark subjects",
        "pattern": "*.html",
        "check_content": "DirectionalLight|SpotLight|PointLight",
        "verify_missing": "rimLight|rim_light|backLight|back_light",
        "suggest": "Add rim/back light for dark subjects (hyperrealism standard: rim light mandatory)",
        "action": "flag_for_review",
        "severity": "enhancement"
    },
]

# ═══════════════════════════════════════════════════════
# CHECK FUNCTIONS
# ═══════════════════════════════════════════════════════

def check_steps_files():
    """Ensure steps files exist in all required locations."""
    files = ["ERDOS_STRAUS_STEPS.txt", "10_DAILY_SCRIPTS.txt"]
    locations = [
        Path.home() / "Desktop",
        Path.home() / "Documents",
        Path("G:/My Drive/Resonance_Archive"),
    ]
    
    results = []
    for fname in files:
        source = None
        for loc in locations:
            if (loc / fname).exists():
                source = loc / fname
                break
        
        if not source:
            # Check trench_builder project
            source = Path.home() / "Projects/trench_builder" / fname
        
        if source and source.exists():
            for loc in locations:
                if not (loc / fname).exists():
                    try:
                        shutil.copy2(source, loc / fname)
                        results.append(f"✓ Copied {fname} to {loc}")
                    except:
                        results.append(f"✗ Could not copy {fname} to {loc}")
    
    return results

def check_cron_overlap():
    """Check for overlapping cron job schedules."""
    return ["Manual check: run 'hermes cron list' and verify no duplicate schedules"]

def check_missing_readmes():
    """Check project directories for missing README.md."""
    results = []
    projects = [
        Path.home() / "Projects/trench_builder",
        Path.home() / "Projects/erdos-straus",
    ]
    for proj in projects:
        if proj.exists() and not (proj / "README.md").exists():
            results.append(f"Missing README.md in {proj}")
    return results

# ═══════════════════════════════════════════════════════
# MAIN AUDITOR
# ═══════════════════════════════════════════════════════

class RetroactiveAuditor:
    def __init__(self):
        self.findings = defaultdict(list)
        self.fixes_applied = []
        self.fixes_needed = []
        self.start_time = datetime.now()
    
    def scan_files(self, base_path, patterns, check_content=None, verify=None, verify_missing=None):
        """Scan files matching patterns (comma or pipe separated) and check content."""
        matches = []
        # Split compound patterns
        if isinstance(patterns, str):
            patterns = [p.strip() for p in patterns.replace('|', ',').split(',')]
        for pattern in patterns:
            try:
                for f in Path(base_path).rglob(pattern):
                    if f.is_file():
                        if check_content:
                            try:
                                content = f.read_text(encoding='utf-8', errors='ignore')
                                if check_content in content:
                                    if verify_missing and verify_missing in content:
                                        continue
                                    if verify_missing:
                                        matches.append(str(f))
                                    elif verify and verify in content:
                                        continue
                                    elif verify:
                                        matches.append(str(f))
                                    else:
                                        matches.append(str(f))
                            except:
                                pass
                        else:
                            matches.append(str(f))
            except (PermissionError, ValueError, FileNotFoundError, OSError):
                pass
        return matches
    
    def run_audit(self):
        print("+------------------------------------------+")
        print("|  RETROACTIVE CORRECTION AGENT            |")
        print("|  The Auditor - Fixes what was built      |")
        print("|  before the rules existed.               |")
        print(f"|  {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}                   |")
        print("+------------------------------------------+")
        print()
        
        total_fixes = 0
        total_flags = 0
        
        for rule in RULES:
            rule_id = rule["id"]
            severity = rule.get("severity", "info")
            
            # Lambda-based checks
            if "check" in rule:
                try:
                    result = rule["check"]()
                    if isinstance(result, list) and result:
                        for r in result:
                            self.findings[severity].append(f"[{rule_id}] {r}")
                            if rule.get("action") == "auto_create" or rule.get("action") == "auto_copy":
                                self.fixes_applied.append(f"[{rule_id}] {r}")
                                total_fixes += 1
                except Exception as e:
                    self.findings["error"].append(f"[{rule_id}] Check failed: {e}")
                continue
            
            # Pattern-based checks
            pattern = rule.get("pattern", "")
            check_content = rule.get("check_content")
            verify = rule.get("verify")
            verify_missing = rule.get("verify_missing")
            
            # Scan audit paths
            for path_name, path in AUDIT_PATHS.items():
                if not path.exists():
                    continue
                
                matches = self.scan_files(path, pattern, check_content, verify, verify_missing)
                
                if matches:
                    for match in matches[:10]:  # limit per path
                        suggest = rule.get("suggest", "")
                        msg = f"{match} — {suggest}" if suggest else match
                        self.findings[severity].append(f"[{rule_id}] {msg}")
                        
                        if rule.get("action") == "auto_create" or rule.get("action") == "auto_copy":
                            self.fixes_applied.append(f"[{rule_id}] {msg}")
                            total_fixes += 1
                        else:
                            self.fixes_needed.append(f"[{rule_id}] {msg}")
                            total_flags += 1
        
        # Print findings
        for severity in ["critical", "warning", "enhancement", "info"]:
            if severity in self.findings:
                label = severity.upper()
                print(f"=== {label} ===")
                for f in self.findings[severity][:20]:
                    print(f"  {f}")
                if len(self.findings[severity]) > 20:
                    print(f"  ... and {len(self.findings[severity]) - 20} more")
                print()
        
        # Summary
        print("=== SUMMARY ===")
        print(f"  Auto-fixes applied:  {total_fixes}")
        print(f"  Issues flagged:      {total_flags}")
        print(f"  Total rules run:     {len(RULES)}")
        print()
        
        if self.fixes_applied:
            print("Auto-fixes applied:")
            for fix in self.fixes_applied:
                print(f"  {fix}")
            print()
        
        if self.fixes_needed:
            print(f"Manual review needed ({len(self.fixes_needed)} items):")
            for fix in self.fixes_needed[:10]:
                print(f"  {fix}")
            if len(self.fixes_needed) > 10:
                print(f"  ... and {len(self.fixes_needed) - 10} more")
        
        return {
            "timestamp": self.start_time.isoformat(),
            "rules_run": len(RULES),
            "auto_fixes": total_fixes,
            "flagged": total_flags,
            "fixes_applied": self.fixes_applied,
            "fixes_needed": self.fixes_needed,
        }

if __name__ == "__main__":
    auditor = RetroactiveAuditor()
    report = auditor.run_audit()
    
    # Save report
    report_path = AUDIT_PATHS["trench_builder"] / "retroactive_audit.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n[OK] Audit report saved to {report_path}")
