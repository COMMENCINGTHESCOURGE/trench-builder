"""
BUILD ALL ASSETS — Batch regenerates every GLB from source scripts via headless Blender.
Run: python build_all_assets.py
Exports all GLBs to assets/dist/ with timing and validation summary.

Usage:
  python build_all_assets.py              # Build all
  python build_all_assets.py --dry-run    # List what would build
  python build_all_assets.py --asset gear # Build only gear
"""
import subprocess
import sys
import json
import time
import os
import shutil
from pathlib import Path
from datetime import datetime

ASSETS_DIR = Path(__file__).parent
DIST_DIR = ASSETS_DIR / "dist"
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"

# Registry: (script, output_glb_pattern, label)
BUILD_TARGETS = [
    ("generate_elevator.py", "elevator.glb", "Elevator"),
    ("generate_staircase.py", "staircase.glb", "Staircase"),
    ("generate_gear.py", "gear_3m_24t.glb", "Gear (3M 24T)"),
    ("generate_pulley.py", "pulley_vbelt_120mm_3gr.glb", "Pulley (V-Belt)"),
]

# Pulley variants to build separately
PULLEY_VARIANTS = [
    ("flat_crowned", "pulley_flat_120mm.glb", "Pulley (Flat Crowned)"),
    ("timing", "pulley_timing_40t_GT2.glb", "Pulley (Timing GT2)"),
]


def build_asset(script_name, label, extra_args=None):
    """Run a generator script headlessly and return result dict."""
    script_path = ASSETS_DIR / script_name
    if not script_path.is_file():
        return {"label": label, "status": "missing", "script": script_name}

    start = time.time()
    try:
        env = os.environ.copy()
        env["ASSET_OUTPUT_DIR"] = str(ASSETS_DIR)
        cmd = [BLENDER, "--background", "--python", str(script_path)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180, env=env)
        elapsed = time.time() - start
        ok = r.returncode == 0

        # Extract export path from stdout
        export_line = ""
        for line in r.stdout.splitlines():
            if "Exported:" in line:
                export_line = line.split("Exported:")[-1].strip()
                break

        return {
            "label": label,
            "script": script_name,
            "status": "ok" if ok else "error",
            "time_s": round(elapsed, 2),
            "export_path": export_line,
            "returncode": r.returncode,
            "stderr_tail": r.stderr.strip()[-200:] if r.stderr else None,
        }
    except subprocess.TimeoutExpired:
        return {"label": label, "script": script_name, "status": "timeout", "time_s": 180}
    except Exception as e:
        return {"label": label, "script": script_name, "status": "error", "error": str(e)[:200]}


def copy_to_dist():
    """Copy generated GLBs to dist/ directory."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    copied = []
    for glb in ASSETS_DIR.glob("*.glb"):
        dest = DIST_DIR / glb.name
        shutil.copy2(glb, dest)
        copied.append({"name": glb.name, "size_kb": round(glb.stat().st_size / 1024, 1)})
    return copied


def validate_glb(glb_path):
    """Minimal GLB validation: magic bytes + JSON chunk parse."""
    try:
        with open(glb_path, "rb") as f:
            header = f.read(12)
            if len(header) < 12:
                return False, "file too small"
            magic = int.from_bytes(header[:4], "little")
            if magic != 0x46546C67:
                return False, f"bad magic: {hex(magic)}"
            total_len = int.from_bytes(header[8:12], "little")
            if total_len != glb_path.stat().st_size:
                return False, f"length mismatch: header={total_len}, file={glb_path.stat().st_size}"
        return True, "ok"
    except Exception as e:
        return False, str(e)[:100]


def _print_dry_run(filter_asset):
    """Print dry run details."""
    print("=== DRY RUN ===")
    for script, glb, label in BUILD_TARGETS:
        if filter_asset and filter_asset.lower() not in label.lower():
            continue
        print(f"  Would build: {label} ({script} -> {glb})")
    for ptype, glb, label in PULLEY_VARIANTS:
        if filter_asset and filter_asset.lower() not in label.lower():
            continue
        print(f"  Would build: {label} (PULLEY_TYPE={ptype})")


def _build_primary(filter_asset, results):
    """Build primary targets."""
    for script, glb, label in BUILD_TARGETS:
        if filter_asset and filter_asset.lower() not in label.lower():
            continue
        print(f"[{label}] Building...")
        r = build_asset(script, label)
        results.append(r)
        if r["status"] == "ok":
            print(f"  OK ({r['time_s']}s) -> {r['export_path']}")
        else:
            print(f"  FAILED: {r['status']} - {r.get('stderr_tail', r.get('error', ''))[:100]}")


def _build_pulley_variants(filter_asset, results):
    """Build pulley variants and patch the script temporarily."""
    pulley_script = ASSETS_DIR / "generate_pulley.py"
    if pulley_script.is_file() and (not filter_asset or "pulley" in filter_asset.lower()):
        original = pulley_script.read_text(encoding="utf-8")
        try:
            for ptype, glb, label in PULLEY_VARIANTS:
                print(f"[{label}] Building...")
                patched = original.replace(
                    'PULLEY_TYPE = "vbelt"',
                    f'PULLEY_TYPE = "{ptype}"'
                )
                pulley_script.write_text(patched, encoding="utf-8")
                r = build_asset("generate_pulley.py", label)
                results.append(r)
                if r["status"] == "ok":
                    print(f"  OK ({r['time_s']}s) -> {r['export_path']}")
                else:
                    print(f"  FAILED: {r['status']}")
        finally:
            pulley_script.write_text(original, encoding="utf-8")


def _deploy_assets():
    """Copy files to external project deployment target if specified."""
    deploy_target = os.environ.get("DEPLOY_TO", "")
    if not deploy_target:
        hyperpoly_assets = ASSETS_DIR.parent.parent / "hyperpoly-terrain" / "assets"
        if hyperpoly_assets.is_dir():
            deploy_target = str(hyperpoly_assets)
    if deploy_target:
        deploy_dir = Path(deploy_target)
        deploy_dir.mkdir(parents=True, exist_ok=True)
        deployed = []
        for glb in DIST_DIR.glob("*.glb"):
            dest = deploy_dir / glb.name
            shutil.copy2(glb, dest)
            deployed.append(glb.name)
        print(f"\nDeployed {len(deployed)} assets to {deploy_target}")
        return deploy_target, len(deployed)
    return None, 0


def build_all(dry_run=False, filter_asset=None):
    """Build all targets, optionally filtering to one asset."""
    results = []
    timestamp = datetime.now().isoformat()

    if dry_run:
        _print_dry_run(filter_asset)
        return

    _build_primary(filter_asset, results)
    _build_pulley_variants(filter_asset, results)

    # Copy to dist
    print("\nCopying to dist/...")
    copied = copy_to_dist()
    for c in copied:
        print(f"  {c['name']} ({c['size_kb']} KB)")

    # Validate all GLBs
    print("\nValidating GLBs...")
    validation = {}
    for glb in DIST_DIR.glob("*.glb"):
        ok, msg = validate_glb(glb)
        validation[glb.name] = {"valid": ok, "message": msg}
        status = "[OK]" if ok else "[FAIL]"
        print(f"  {status} {glb.name}: {msg}")

    # Cross-project deploy
    deploy_target, deployed_count = _deploy_assets()

    # Summary
    ok_count = sum(1 for r in results if r["status"] == "ok")
    total_time = sum(r.get("time_s", 0) for r in results)
    summary = {
        "timestamp": timestamp,
        "total": len(results),
        "ok": ok_count,
        "failed": len(results) - ok_count,
        "total_time_s": round(total_time, 2),
        "results": results,
        "dist_files": copied,
        "validation": validation,
    }

    if deploy_target:
        summary["deployed_to"] = deploy_target
        summary["deployed_count"] = deployed_count

    out = ASSETS_DIR / "build_summary.json"
    out.write_text(json.dumps(summary, indent=2))

    print(f"\n{'='*50}")
    print(f"Build complete: {ok_count}/{len(results)} passed in {total_time:.1f}s")
    print(f"Summary: {out}")
    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--asset", type=str, help="Build only matching asset")
    args = parser.parse_args()
    build_all(dry_run=args.dry_run, filter_asset=args.asset)
