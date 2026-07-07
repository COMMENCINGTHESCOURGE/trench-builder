#!/usr/bin/env python3
"""
compute_sha256.py — SHA256 provenance ledger for trench_builder/assets.
Walks all production asset files (.glb, .fbx, .blend, .jpg, .png, .hdr,
.exr, .gltf, .mtl, .bin) and writes a sha256_registry.json keyed by
relative path with size_bytes, mtime, and sha256.

Output: assets/data/sha256_registry.json
Run after every build_all_assets.py or manual asset import.
"""

import hashlib
import json
import os
import sys
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
OUTPUT_PATH = ASSETS_DIR / "data" / "sha256_registry.json"

EXTENSIONS = {
    ".glb", ".gltf", ".fbx", ".blend", ".obj", ".ply",
    ".jpg", ".jpeg", ".png", ".hdr", ".exr", ".tga",
    ".mtl", ".bin", ".usdc", ".tres", ".mtlx",
}

SKIP_DIRS = {
    "__pycache__", ".git", "node_modules", "dist",
}

def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def walk_assets(root: Path):
    registry = {}
    for dirpath, dirnames, filenames in os.walk(root):
        # prune skip dirs in-place
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() not in EXTENSIONS:
                continue
            rel = p.relative_to(ASSETS_DIR).as_posix()
            try:
                stat = p.stat()
                sha = sha256_of(p)
                registry[rel] = {
                    "sha256": sha,
                    "size_bytes": stat.st_size,
                    "mtime": stat.st_mtime,
                }
            except Exception as e:
                print(f"WARN: failed to hash {rel}: {e}", file=sys.stderr)
    return registry


def main():
    print(f"Scanning {ASSETS_DIR} ...")
    registry = walk_assets(ASSETS_DIR)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    print(f"Wrote {len(registry)} entries to {OUTPUT_PATH}")
    for rel, info in sorted(registry.items()):
        size_kb = info["size_bytes"] / 1024
        print(f"  {rel:70s}  {info['sha256'][:16]}...  {size_kb:8.1f} KB")


if __name__ == "__main__":
    main()
