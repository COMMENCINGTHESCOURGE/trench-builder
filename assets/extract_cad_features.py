#!/usr/bin/env python
"""CAD Feature Extractor — 78 STLs -> cad_feature_table.json
Extracts vinculum-relevant geometric features per part:
bbox dims, volume, area, triangle count, watertightness, genus (bore count),
rotational symmetry order, elongation ratio. CPU-only.
"""
import json, os, sys, math
import numpy as np

try:
    import trimesh
except ImportError:
    sys.exit("pip install trimesh")

CAD_DIR = "C:/Users/dasha/Projects/trench_builder/cad_imports"
OUT = "C:/Users/dasha/Projects/trench_builder/assets/data/cad_feature_table.json"

def rotational_symmetry_order(mesh):
    """Detect rotational symmetry about principal axis via cross-section vertex count sampling."""
    # Cheap proxy: sample mesh cross-sections perpendicular to longest axis,
    # count angular clusters of vertices in the largest section polygon.
    try:
        extents = mesh.extents
        axis = int(np.argmax(extents))
        origin = mesh.centroid
        normal = np.zeros(3); normal[axis] = 1.0
        section = mesh.section(plane_origin=origin, plane_normal=normal)
        if section is None:
            return 1
        planar, _ = section.to_planar()
        poly = planar.polygons_full
        if len(poly) == 0:
            return 1
        p = poly[0]
        return max(1, len(p.exterior.coords) - 1)
    except Exception:
        return 1

def extract(path):
    m = trimesh.load(path, force='mesh')
    feats = {
        "file": os.path.basename(path),
        "triangles": int(len(m.faces)),
        "vertices": int(len(m.vertices)),
        "watertight": bool(m.is_watertight),
        "bbox_mm": [round(float(x), 2) for x in sorted(m.extents, reverse=True)],
        "volume_cm3": round(abs(float(m.volume)) / 1000.0, 3) if m.is_watertight else None,
        "area_cm2": round(float(m.area) / 100.0, 2),
        "genus": None,
        "elongation": round(float(max(m.extents) / max(min(m.extents), 1e-6)), 2),
    }
    if m.is_watertight:
        # Euler characteristic: V - E + F = 2 - 2g  =>  g = (2 - chi)/2
        feats["genus"] = int(max(0, (2 - int(m.euler_number)) // 2))
    # class label from filename prefix
    base = os.path.basename(path)
    feats["class"] = base.split("_")[0].split(".")[0]
    return feats

def main():
    rows, errors = [], []
    for f in sorted(os.listdir(CAD_DIR)):
        if not f.lower().endswith(".stl"):
            continue
        try:
            rows.append(extract(os.path.join(CAD_DIR, f)))
        except Exception as e:
            errors.append({"file": f, "error": str(e)[:120]})
    table = {
        "version": "1.0",
        "generated": __import__("datetime").datetime.utcnow().isoformat() + "+00:00",
        "parts_extracted": len(rows),
        "errors": len(errors),
        "watertight_count": sum(1 for r in rows if r["watertight"]),
        "classes": sorted({r["class"] for r in rows}),
        "features": rows,
        "extract_errors": errors,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(table, fh, indent=2)
    print(f"EXTRACTED {len(rows)} parts ({table['watertight_count']} watertight, {len(errors)} errors)")
    print("classes:", table["classes"])
    for r in rows[:8]:
        print(f"  {r['file'][:44]:<44} tri={r['triangles']:>6} genus={r['genus']} bbox={r['bbox_mm']}")

if __name__ == "__main__":
    main()
