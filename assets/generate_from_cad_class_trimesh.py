
import json, hashlib, random, sys
from pathlib import Path
import numpy as np
import trimesh

ASSETS = Path("C:/Users/dasha/Projects/trench_builder/assets")
TABLE = ASSETS / "data" / "cad_feature_table.json"
OUTDIR = ASSETS / "cad_derived"
OUTDIR.mkdir(exist_ok=True)

argv = sys.argv[1:]
TARGET_CLASS = argv[argv.index("--class")+1] if "--class" in argv else "GEARBOX"
COUNT = int(argv[argv.index("--count")+1]) if "--count" in argv else 2
SEED = int(argv[argv.index("--seed")+1]) if "--seed" in argv else 42
random.seed(SEED); np.random.seed(SEED)

table = json.loads(TABLE.read_text())
members = [f for f in table["features"] if f["class"] == TARGET_CLASS and f["watertight"]]
assert members, f"no watertight members for {TARGET_CLASS}"

dims = [f["bbox_mm"] for f in members]
elong = [f["elongation"] for f in members]
genus = [f["genus"] or 0 for f in members]

def sr(vals, pad=0.9):
    lo, hi = min(vals), max(vals)
    return random.uniform(lo*pad, hi*1.1)

entries = []
for i in range(COUNT):
    L = sr([d[0] for d in dims])
    W = L / sr(elong)
    H = sr([d[2] for d in dims])
    # shaft body along Z
    body = trimesh.creation.cylinder(radius=W/2, height=L, sections=32)

    target_genus = max(1, round(sum(genus)/len(genus)))
    n_bores = min(target_genus, 4)
    bores = []
    for b in range(n_bores):
        r = W * random.uniform(0.15, 0.35) / 2
        off = (b-(n_bores-1)/2)*W*0.55 if n_bores>1 else 0
        c = trimesh.creation.cylinder(radius=r, height=L*1.05, sections=24)
        c.apply_translation([off,0,0])
        bores.append(c)

    mesh = body
    for br in bores:
        try:
            mesh = mesh.difference(br)
        except Exception:
            pass  # keep solid if boolean fails

    out = OUTDIR / f"{TARGET_CLASS.lower()}_variant_{i}.glb"
    scene = trimesh.Scene({"body": mesh})
    scene.export(str(out))

    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    entries.append({
        "name": out.stem,
        "source_script": "generate_from_cad_class_trimesh.py",
        "derived_from": {"cad_class": TARGET_CLASS, "measured_members": len(members),
                          "seed": SEED},
        "parameters": {"type": "cad_derived", "length_mm": round(L,2),
                        "width_mm": round(W,2), "bores": n_bores,
                        "elongation_class_mean": round(sum(elong)/len(elong),2)},
        "glb": {"filename": out.name, "sha256": sha, "size_bytes": out.stat().st_size},
        "validation": {"status": "unverified_boolean", "note": "watertightness post-boolean not checked"},
        "deployment": {"targets": ["trench-builder"]},
    })
    print(f"EXPORTED {out.name} {out.stat().st_size}B genus_target={n_bores}")

(OUTDIR / f"{TARGET_CLASS.lower()}_variants_registry.json").write_text(json.dumps(entries, indent=2))
print(f"CAD_DERIVED_OK {len(entries)}")
