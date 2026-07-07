"""
VARIANT MATRIX GENERATOR — Sweep parameters across gear and pulley generators.
Run: python generate_variants.py
Produces 12 gear variants + 9 pulley variants, validates, and catalogs.
"""
import subprocess
import sys
import json
import time
import os
from pathlib import Path
from datetime import datetime

ASSETS_DIR = Path(__file__).parent
DIST_DIR = ASSETS_DIR / "dist"
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"


def build_with_params(script_name, param_patches, label):
    """Patch a generator script's parameters, run it, restore original."""
    script_path = ASSETS_DIR / script_name
    original = script_path.read_text(encoding="utf-8")

    try:
        # Apply patches
        patched = original
        for old, new in param_patches.items():
            patched = patched.replace(old, new)

        # Handle second replacement for matching patterns
        for old, new in param_patches.items():
            if old.startswith("MODULE") or old.startswith("TEETH") or old.startswith("PITCH_DIAMETER") or old.startswith("V_NUM_GROOVES"):
                # Only do one replacement
                pass

        script_path.write_text(patched, encoding="utf-8")

        start = time.time()
        env = os.environ.copy()
        env["ASSET_OUTPUT_DIR"] = str(ASSETS_DIR)
        cmd = [BLENDER, "--background", "--python", str(script_path)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180, env=env)
        elapsed = time.time() - start

        ok = r.returncode == 0
        export_line = ""
        for line in r.stdout.splitlines():
            if "Exported:" in line:
                export_line = line.split("Exported:")[-1].strip()
                break

        return {
            "label": label,
            "status": "ok" if ok else "error",
            "time_s": round(elapsed, 2),
            "export_path": export_line,
        }
    finally:
        script_path.write_text(original, encoding="utf-8")


def main():
    results = []
    timestamp = datetime.now().isoformat()

    # ── Gear variants: 4 modules × 3 teeth ─────────────────
    gear_modules = [
        ("MODULE = 2.0", "TEETH = 16", "Gear 2M 16T"),
        ("MODULE = 2.0", "TEETH = 20", "Gear 2M 20T"),
        ("MODULE = 2.0", "TEETH = 24", "Gear 2M 24T"),
        ("MODULE = 3.0", "TEETH = 16", "Gear 3M 16T"),
        ("MODULE = 3.0", "TEETH = 20", "Gear 3M 20T"),
        ("MODULE = 3.0", "TEETH = 24", "Gear 3M 24T"),
        ("MODULE = 4.0", "TEETH = 16", "Gear 4M 16T"),
        ("MODULE = 4.0", "TEETH = 20", "Gear 4M 20T"),
        ("MODULE = 4.0", "TEETH = 24", "Gear 4M 24T"),
        ("MODULE = 5.0", "TEETH = 12", "Gear 5M 12T"),
        ("MODULE = 5.0", "TEETH = 16", "Gear 5M 16T"),
        ("MODULE = 5.0", "TEETH = 20", "Gear 5M 20T"),
    ]

    print("=== Gear Variant Matrix === (4 modules × 3 teeth)")
    for mod_patch, teeth_patch, label in gear_modules:
        print(f"  [{label}]", end=" ", flush=True)
        r = build_with_params("generate_gear.py",
                             {"MODULE = 3.0": mod_patch, "TEETH = 24": teeth_patch},
                             label)
        results.append(r)
        status = "OK" if r["status"] == "ok" else "FAIL"
        print(f"{status} ({r['time_s']}s)")

    # ── Pulley variants: 3 types × 3 diameters ─────────────
    pulley_configs = [
        ("PULLEY_TYPE = \"vbelt\"", "PITCH_DIAMETER = 80.0", "V-Belt D=80mm"),
        ("PULLEY_TYPE = \"vbelt\"", "PITCH_DIAMETER = 120.0", "V-Belt D=120mm"),
        ("PULLEY_TYPE = \"vbelt\"", "PITCH_DIAMETER = 160.0", "V-Belt D=160mm"),
        ("PULLEY_TYPE = \"flat_crowned\"", "PITCH_DIAMETER = 80.0", "Flat D=80mm"),
        ("PULLEY_TYPE = \"flat_crowned\"", "PITCH_DIAMETER = 120.0", "Flat D=120mm"),
        ("PULLEY_TYPE = \"flat_crowned\"", "PITCH_DIAMETER = 160.0", "Flat D=160mm"),
        ("PULLEY_TYPE = \"timing\"", "PITCH_DIAMETER = 80.0", "Timing D=80mm"),
        ("PULLEY_TYPE = \"timing\"", "PITCH_DIAMETER = 120.0", "Timing D=120mm"),
        ("PULLEY_TYPE = \"timing\"", "PITCH_DIAMETER = 160.0", "Timing D=160mm"),
    ]

    print("\n=== Pulley Variant Matrix === (3 types × 3 diameters)")
    for type_patch, diam_patch, label in pulley_configs:
        print(f"  [{label}]", end=" ", flush=True)
        r = build_with_params("generate_pulley.py",
                             {"PULLEY_TYPE = \"vbelt\"": type_patch,
                              "PITCH_DIAMETER = 120.0": diam_patch},
                             label)
        results.append(r)
        status = "OK" if r["status"] == "ok" else "FAIL"
        print(f"{status} ({r['time_s']}s)")

    # ── Copy to dist ─────────────────────────────────────
    import shutil
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    copied = []
    for glb in ASSETS_DIR.glob("*.glb"):
        dest = DIST_DIR / glb.name
        shutil.copy2(glb, dest)
        copied.append({"name": glb.name, "size_kb": round(glb.stat().st_size / 1024, 1)})

    # ── Summary ──────────────────────────────────────────
    ok_count = sum(1 for r in results if r["status"] == "ok")
    total_time = sum(r.get("time_s", 0) for r in results)

    catalog = {
        "timestamp": timestamp,
        "total_variants": len(results),
        "ok": ok_count,
        "failed": len(results) - ok_count,
        "total_time_s": round(total_time, 2),
        "gear_variants": len(gear_modules),
        "pulley_variants": len(pulley_configs),
        "results": results,
        "dist_files": copied,
    }

    out = ASSETS_DIR / "variant_catalog.json"
    out.write_text(json.dumps(catalog, indent=2))

    print(f"\n{'='*50}")
    print(f"Variant matrix: {ok_count}/{len(results)} passed in {total_time:.1f}s")
    print(f"Catalog: {out}")
    print(f"Dist: {len(copied)} files in {DIST_DIR}")

    return catalog


if __name__ == "__main__":
    main()
