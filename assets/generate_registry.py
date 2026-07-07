"""
ASSET REGISTRY GENERATOR — Scans dist/ for GLBs, hashes source scripts,
hashes GLB files, produces asset_registry.json conforming to the schema.
Run: python generate_registry.py
"""
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone

ASSETS_DIR = Path(__file__).parent
DIST_DIR = ASSETS_DIR / "dist"
SCHEMA_PATH = ASSETS_DIR / "asset_registry_schema.json"

# Parameter extraction from filenames:
# gear_3m_24t.glb → module=3, teeth=24
# pulley_vbelt_120mm_3gr.glb → type=vbelt, diameter=120, grooves=3
# elevator.glb → default params
# staircase.glb → default params

def parse_gear_params(name):
    """Extract module and teeth from 'gear_3m_24t.glb'."""
    import re
    m = re.match(r'gear_(\d+)m_(\d+)t', name)
    if m:
        return {"module_mm": int(m.group(1)), "teeth": int(m.group(2))}
    return {}

def parse_pulley_params(name):
    """Extract type, diameter, grooves from pulley filenames."""
    import re
    m = re.match(r'pulley_(vbelt|flat|timing)_(\d+)mm(?:_(\d+)gr)?', name)
    if m:
        params = {"type": m.group(1), "pitch_diameter_mm": int(m.group(2))}
        if m.group(3):
            params["grooves"] = int(m.group(3))
        return params
    return {}

def sha256_file(path):
    """SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_registry():
    """Scan dist/, hash everything, produce registry."""
    assets = []

    # Map GLB filenames to their source scripts
    glb_to_script = {}
    for glb in DIST_DIR.glob("*.glb"):
        name = glb.name.lower()
        if "gear" in name:
            glb_to_script[glb.name] = "generate_gear.py"
        elif "pulley" in name:
            glb_to_script[glb.name] = "generate_pulley.py"
        elif "elevator" in name:
            glb_to_script[glb.name] = "generate_elevator.py"
        elif "staircase" in name:
            glb_to_script[glb.name] = "generate_staircase.py"

    # Hash source scripts once
    script_hashes = {}
    for script_name in set(glb_to_script.values()):
        sp = ASSETS_DIR / script_name
        if sp.is_file():
            script_hashes[script_name] = sha256_file(sp)

    # Validate each GLB (basic check)
    def quick_validate(glb_path):
        try:
            with open(glb_path, "rb") as f:
                header = f.read(12)
                if len(header) < 12:
                    return "fail"
                magic = int.from_bytes(header[:4], "little")
                if magic != 0x46546C67:
                    return "fail"
                return "pass"
        except Exception:
            return "fail"

    now = datetime.now(timezone.utc).isoformat()

    for glb in sorted(DIST_DIR.glob("*.glb")):
        script = glb_to_script.get(glb.name, "unknown")
        glb_hash = sha256_file(glb)
        stat = glb.stat()
        name_lower = glb.name.lower()

        # Parse parameters from filename
        params = {}
        if "gear" in name_lower:
            params = parse_gear_params(glb.stem)
        elif "pulley" in name_lower:
            params = parse_pulley_params(glb.stem)
        elif "elevator" in name_lower:
            params = {"type": "architectural", "cage_width_m": 2.0, "cage_height_m": 3.0}
        elif "staircase" in name_lower:
            params = {"type": "architectural", "steps": 14, "rise_m": 0.214, "run_m": 0.28}

        assets.append({
            "name": glb.stem,
            "source_script": script,
            "source_sha256": script_hashes.get(script, "unknown"),
            "generated_at": now,
            "parameters": params,
            "glb": {
                "filename": glb.name,
                "sha256": glb_hash,
                "size_bytes": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 1),
            },
            "validation": {
                "status": quick_validate(glb),
                "last_validated": now,
            },
            "deployment": {
                "targets": ["trench-builder"]
            }
        })

    registry = {
        "version": "1.0",
        "generated": now,
        "project": "trench-builder",
        "asset_count": len(assets),
        "assets": assets,
    }

    out = ASSETS_DIR / "asset_registry.json"
    out.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(f"Registry: {len(assets)} assets → {out}")
    return registry


if __name__ == "__main__":
    generate_registry()
