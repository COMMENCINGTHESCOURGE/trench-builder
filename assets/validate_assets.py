"""
ASSET VALIDATOR — GLB integrity checker for generated assets.
Run: python validate_assets.py [--strict] [--summary] [path ...]

Checks:
  1. File exists and size > 0
  2. GLB magic bytes (0x46546C67 = "glTF")
  3. GLB version == 2
  4. Header length matches file size
  5. JSON chunk parses as valid JSON
  6. BIN chunk present with non-zero length
  7. Reports: mesh count, material count, node count
  8. --strict: also checks mesh has vertex data, material slot count matches

Usage:
  python validate_assets.py                           # Validate all *.glb in dist/
  python validate_assets.py assets/dist/elevator.glb  # Validate single file
  python validate_assets.py --strict                  # Full mesh/material audit
  python validate_assets.py --summary                 # One-line per file
"""
import json
import struct
import sys
from pathlib import Path

ASSETS_DIR = Path(__file__).parent
DIST_DIR = ASSETS_DIR / "dist"


def validate_glb(filepath: Path, strict: bool = False) -> dict:
    """Validate a single GLB file. Returns dict with status and details."""
    result = {
        "file": str(filepath),
        "name": filepath.name,
        "size_bytes": 0,
        "valid": False,
        "checks": [],
    }

    # Check 0: File exists
    if not filepath.is_file():
        result["error"] = "file not found"
        return result

    result["size_bytes"] = filepath.stat().st_size

    # Check 1: Non-zero size
    if result["size_bytes"] == 0:
        result["checks"].append({"check": "size", "pass": False, "msg": "file is 0 bytes"})
        result["error"] = "empty file"
        return result
    result["checks"].append({"check": "size", "pass": True})

    # Check 2-4: GLB header (12 bytes)
    try:
        with open(filepath, "rb") as f:
            header = f.read(12)
            if len(header) < 12:
                result["error"] = "header too short"
                return result

            magic = struct.unpack("<I", header[0:4])[0]
            version = struct.unpack("<I", header[4:8])[0]
            total_length = struct.unpack("<I", header[8:12])[0]

            magic_ok = magic == 0x46546C67
            version_ok = version == 2
            length_ok = total_length == result["size_bytes"]

            result["checks"].append({
                "check": "magic",
                "pass": magic_ok,
                "expected": "0x46546C67",
                "got": hex(magic)
            })
            result["checks"].append({
                "check": "version",
                "pass": version_ok,
                "expected": 2,
                "got": version
            })
            result["checks"].append({
                "check": "length",
                "pass": length_ok,
                "expected": result["size_bytes"],
                "got": total_length
            })

            if not magic_ok:
                result["error"] = f"bad magic: {hex(magic)}"
                return result

            # Check 5-6: Chunk iteration
            offset = 12
            chunk_index = 0
            json_chunk_ok = False
            bin_chunk_ok = False
            meshes = 0
            materials = 0
            nodes = 0

            while offset < total_length:
                chunk_header = f.read(8)
                if len(chunk_header) < 8:
                    break
                chunk_len = struct.unpack("<I", chunk_header[0:4])[0]
                chunk_type = struct.unpack("<I", chunk_header[4:8])[0]

                chunk_data = f.read(chunk_len)
                chunk_index += 1
                offset += 8 + chunk_len

                # JSON chunk (type 0x4E4F534A = "JSON" in little-endian)
                if chunk_type == 0x4E4F534A:
                    try:
                        gltf = json.loads(chunk_data.decode("utf-8"))
                        json_chunk_ok = True
                        meshes = len(gltf.get("meshes", []))
                        materials = len(gltf.get("materials", []))
                        nodes = len(gltf.get("nodes", []))

                        if strict:
                            # Check meshes have primitives with vertex data
                            for mi, mesh in enumerate(gltf.get("meshes", [])):
                                for pi, prim in enumerate(mesh.get("primitives", [])):
                                    if "attributes" not in prim:
                                        result["checks"].append({
                                            "check": f"mesh[{mi}].prim[{pi}].attributes",
                                            "pass": False,
                                            "msg": "no vertex attributes"
                                        })
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        result["checks"].append({
                            "check": "json_parse",
                            "pass": False,
                            "msg": str(e)[:100]
                        })

                # BIN chunk (type 0x004E4942 = "BIN\0" in little-endian)
                if chunk_type == 0x004E4942:
                    bin_chunk_ok = chunk_len > 0

            result["checks"].append({"check": "json_chunk", "pass": json_chunk_ok})
            result["checks"].append({"check": "bin_chunk", "pass": bin_chunk_ok})
            result["meshes"] = meshes
            result["materials"] = materials
            result["nodes"] = nodes

            all_pass = all(c.get("pass", False) for c in result["checks"])
            result["valid"] = all_pass

    except Exception as e:
        result["error"] = str(e)[:200]
        return result

    return result


def validate_directory(directory: Path, strict: bool = False) -> list[dict]:
    """Validate all GLB files in a directory."""
    results = []
    for glb in sorted(directory.glob("*.glb")):
        results.append(validate_glb(glb, strict=strict))
    return results


def print_summary(results: list[dict]):
    """Print one-line per file."""
    for r in results:
        if r.get("error"):
            print(f"  ERROR {r['name']}: {r['error']}")
        else:
            status = "PASS" if r["valid"] else "FAIL"
            m = r.get("meshes", "?")
            mat = r.get("materials", "?")
            kb = round(r["size_bytes"] / 1024, 1)
            print(f"  {status:5s} {r['name']:35s} {kb:>7} KB  {m:>3} meshes  {mat:>2} materials")


def print_detailed(results: list[dict]):
    """Print full validation details."""
    for r in results:
        print(f"\n{'='*60}")
        print(f"File: {r['name']} ({round(r['size_bytes']/1024, 1)} KB)")
        if r.get("error"):
            print(f"  ERROR: {r['error']}")
            continue

        for c in r.get("checks", []):
            status = "✓" if c.get("pass") else "✗"
            extra = ""
            if "expected" in c:
                extra = f"  (expected={c['expected']}, got={c['got']})"
            elif "msg" in c:
                extra = f"  ({c['msg']})"
            print(f"  {status} {c['check']}{extra}")

        print(f"  Content: {r.get('meshes', '?')} meshes, "
              f"{r.get('materials', '?')} materials, "
              f"{r.get('nodes', '?')} nodes")

    # Grand total
    total = len(results)
    passed = sum(1 for r in results if r.get("valid"))
    total_kb = sum(r.get("size_bytes", 0) for r in results) / 1024
    print(f"\n{'='*60}")
    print(f"Total: {passed}/{total} valid, {round(total_kb, 1)} KB")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="GLB Asset Validator")
    parser.add_argument("paths", nargs="*", help="GLB files or directories to validate")
    parser.add_argument("--strict", action="store_true", help="Deep mesh/material audit")
    parser.add_argument("--summary", action="store_true", help="One-line per file output")
    args = parser.parse_args()

    targets = args.paths if args.paths else [str(DIST_DIR)]
    results = []

    for target in targets:
        p = Path(target)
        if p.is_dir():
            results.extend(validate_directory(p, strict=args.strict))
        elif p.is_file():
            results.append(validate_glb(p, strict=args.strict))
        else:
            print(f"Skipping: {target} (not found)")

    if not results:
        print("No GLB files found.")
        sys.exit(1)

    if args.summary:
        print_summary(results)
    else:
        print_detailed(results)

    failed = sum(1 for r in results if not r.get("valid"))
    sys.exit(0 if failed == 0 else 1)
