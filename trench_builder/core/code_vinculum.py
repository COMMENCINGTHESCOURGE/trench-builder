"""
Trench-Builder Core: CodeVinculum — program syntax & constraint validation.
Uses the Vinculum system to audit codebase health, formatting compliance,
and OS-specific path issues at build time.
"""

import os
import re
from typing import Dict, List, Tuple
from .vinculum import Vinculum, Constraint, ConstraintKind


class CodeVinculum(Vinculum):
    """
    A collection of codebase constraints that validate syntax integrity,
    file formatting, and cross-platform path compatibility.
    """

    def __init__(self):
        super().__init__(domain="codebase")
        
        # Add Code Constraints
        self.add(Constraint(
            kind=ConstraintKind.EXACT,
            key="git_conflicts",
            target=0.0,
            description="Presence of git merge conflict indicators"
        ))
        self.add(Constraint(
            kind=ConstraintKind.EXACT,
            key="unsafe_file_writes",
            target=0.0,
            description="Presence of file writes without explicit utf-8 encoding"
        ))
        self.add(Constraint(
            kind=ConstraintKind.EXACT,
            key="drive_casing_drift",
            target=0.0,
            description="Windows drive letter casing anomalies"
        ))

    def audit_file(self, filepath: str) -> Dict[str, float]:
        """Reads a file and measures code-health metrics for validation."""
        filepath = os.path.abspath(filepath)
        
        metrics = {
            "git_conflicts": 0.0,
            "unsafe_file_writes": 0.0,
            "drive_casing_drift": 0.0
        }
        
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            # 1. Check Git Conflict Markers
            # Dynamically constructed to prevent self-matching during codebase audit
            markers = ["<" * 7, "=" * 7, ">" * 7]
            if any(marker in content for marker in markers):
                metrics["git_conflicts"] = 1.0
                
            # Detect unsafe file writes without encoding
            # Regex broken up to prevent self-matching during audit
            open_pattern = r'op' + r'en\([^)]+,\s*["\'](?:w|a|wt|at)["\'][^)]*\)'
            write_opens = re.findall(open_pattern, content)
            for op in write_opens:
                if "encoding=" not in op:
                    metrics["unsafe_file_writes"] += 1.0
                    
            # 3. Check Drive Casing Anomalies (lowercase c:)
            # Matches c:\ or c:\\ but ignores file:/// URLs or standard relative paths
            lowercase_drives = re.findall(r'(?<![a-zA-Z0-9])c:\\{1,2}[a-zA-Z0-9_.-]', content)
            if lowercase_drives:
                metrics["drive_casing_drift"] = float(len(lowercase_drives))
                
        except Exception:
            # File unreadable, count as failure
            metrics["git_conflicts"] = 1.0
            
        return metrics

    def validate_codebase(self, file_paths: List[str]) -> Tuple[bool, List[str]]:
        """Audits all listed files and collects validation errors."""
        failures = []
        for path in file_paths:
            measurements = self.audit_file(path)
            passed, file_failures = self.validate_all(measurements)
            if not passed:
                filename = os.path.basename(path)
                for fail in file_failures:
                    failures.append(f"[{filename}] {fail}")
        return len(failures) == 0, failures
