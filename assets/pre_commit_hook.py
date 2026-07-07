#!/usr/bin/env python
"""
Git pre-commit hook — if any generator script or material library changed,
regenerate all GLBs, validate them, and add the results to the commit.
Block commit if validation fails.

Install: copy to .git/hooks/pre-commit (no .py extension)
"""
import subprocess
import sys
import os
from pathlib import Path

HOOK_DIR = Path(__file__).resolve().parent
ASSETS_DIR = HOOK_DIR / "assets"

# Files that trigger regeneration
WATCHED = [
    "generate_elevator.py",
    "generate_staircase.py",
    "generate_gear.py",
    "generate_pulley.py",
    "material_library.py",
    "build_all_assets.py",
    "generate_variants.py",
]

def get_staged_files():
    """Return list of staged file paths."""
    r = subprocess.run(["git", "diff", "--cached", "--name-only"],
                      capture_output=True, text=True, cwd=str(HOOK_DIR))
    return [Path(p) for p in r.stdout.strip().split("\n") if p]

def main():
    staged = get_staged_files()
    staged_names = {p.name for p in staged}

    # Check if any watched files changed
    triggered = [w for w in WATCHED if w in staged_names]

    if not triggered:
        # Also check if material_library.py changed
        material_staged = any("material_library" in p.name for p in staged)
        if not material_staged:
            return 0  # Nothing to do

    print(f"[pre-commit] Asset regeneration triggered by: {', '.join(triggered) or 'material library change'}")

    # Build all assets
    build_script = ASSETS_DIR / "build_all_assets.py"
    if build_script.is_file():
        r = subprocess.run([sys.executable, str(build_script)],
                          cwd=str(ASSETS_DIR), capture_output=True, text=True, timeout=300)

        if r.returncode != 0:
            print("[pre-commit] Build failed!")
            print(r.stderr[-500:] if r.stderr else r.stdout[-500:])
            return 1

        # Validate
        validate_script = ASSETS_DIR / "validate_assets.py"
        r = subprocess.run([sys.executable, str(validate_script), "--summary", str(ASSETS_DIR / "dist")],
                          cwd=str(ASSETS_DIR), capture_output=True, text=True, timeout=30)

        if r.returncode != 0:
            print("[pre-commit] Validation failed!")
            print(r.stdout)
            return 1

        # Generate variants
        variants_script = ASSETS_DIR / "generate_variants.py"
        r = subprocess.run([sys.executable, str(variants_script)],
                          cwd=str(ASSETS_DIR), capture_output=True, text=True, timeout=600,
                          env={**os.environ, "PYTHONUNBUFFERED": "1"})

        if r.returncode != 0:
            print("[pre-commit] Variant generation failed! Continuing anyway...")

        # Generate registry
        registry_script = ASSETS_DIR / "generate_registry.py"
        subprocess.run([sys.executable, str(registry_script)],
                      cwd=str(ASSETS_DIR), capture_output=True, timeout=30)

        # Stage generated files
        stage_files = [
            str(ASSETS_DIR / "dist"),
            str(ASSETS_DIR / "asset_registry.json"),
            str(ASSETS_DIR / "build_summary.json"),
            str(ASSETS_DIR / "variant_catalog.json"),
        ]
        for f in stage_files:
            if Path(f).exists():
                subprocess.run(["git", "add", f], cwd=str(HOOK_DIR),
                              capture_output=True, timeout=10)

        print("[pre-commit] Assets regenerated, validated, and staged.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
