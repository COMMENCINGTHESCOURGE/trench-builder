#!/usr/bin/env python3
"""
Trench-Builder CLI: generate constraint-validated assemblies from modular specs.

Usage:
  python -m trench_builder.cli ship sailboat_v2
  python -m trench_builder.cli character hero_v1 --height 150
  python -m trench_builder.cli building tavern_v1 --archetype row_house
  python -m trench_builder.cli reverse ./output/model.glb

Output:
  output/<model_id>_HP.glb     — High-poly GLB with embedded spec
  output/<model_id>_manifest.json — Unity-consumer constraint manifest
  output/<model_id>_spec.json  — Full parametric specification (human-readable)
"""
import sys
import json
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "modular"


def cmd_ship(args):
    from .domains.nautical import generate_sailboat, generate_cargo_ship
    model_id = args[0] if args else "sailboat_v1"
    kind = "cargo" if "cargo" in model_id else "sailboat"
    if kind == "cargo":
        spec = generate_cargo_ship(model_id)
    else:
        spec = generate_sailboat(model_id)
    return spec


def cmd_character(args):
    from .domains.character import generate_character
    model_id = args[0] if args else "character_v1"
    height = 100.0
    for i, a in enumerate(args):
        if a == "--height" and i + 1 < len(args):
            height = float(args[i + 1])
    return generate_character(model_id, height_mm=height)


def cmd_building(args):
    from .domains.building import generate_building
    model_id = args[0] if args else "building_v1"
    archetype = "row_house"
    for i, a in enumerate(args):
        if a == "--archetype" and i + 1 < len(args):
            archetype = args[i + 1]
    return generate_building(model_id, archetype=archetype)


def cmd_reverse(args):
    """Reverse-engineer a built GLB: read embedded spec and print it."""
    glb_path = args[0] if args else None
    if not glb_path:
        print("Usage: python -m trench_builder.cli reverse <path/to/model.glb>")
        return None

    print(f"Reverse-engineering {glb_path}...")
    print("(Requires Blender runtime. Run inside Blender to extract embedded spec.)")
    print(f"To extract manually: read custom property 'trench_builder_spec' from the armature.")
    return None


COMMANDS = {
    "ship": cmd_ship,
    "character": cmd_character,
    "building": cmd_building,
    "reverse": cmd_reverse,
}


def build_and_export(spec):
    """Build the assembly in Blender and export GLB + manifest + spec JSON."""
    try:
        import bpy
        from .builders import ReverseEngineerableBuilder
    except ImportError:
        # Running outside Blender — just export the spec JSON
        spec_path = OUTPUT_DIR / f"{spec.model_id}_spec.json"
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        with open(spec_path, "w") as f:
            f.write(spec.to_json())
        print(f"Spec exported (no Blender): {spec_path}")
        print(f"Run inside Blender to generate GLB + manifest.")
        return

    print(f"Building: {spec.model_id} ({spec.domain}, {len(spec.components)} components)")

    builder = ReverseEngineerableBuilder()
    builder.build_assembly(spec)

    glb_path = builder.export_glb(str(OUTPUT_DIR / f"{spec.model_id}_HP.glb"))
    manifest_path = builder.export_manifest(spec, str(OUTPUT_DIR / f"{spec.model_id}_manifest.json"))
    spec_path = OUTPUT_DIR / f"{spec.model_id}_spec.json"
    with open(spec_path, "w") as f:
        f.write(spec.to_json())

    print(f"  GLB:      {glb_path}")
    print(f"  Manifest:  {manifest_path}")
    print(f"  Spec:      {spec_path}")

    # Vinculum validation
    if spec.global_vinculum:
        print(f"  Vinculum:  {len(spec.global_vinculum.constraints)} global constraints")


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m trench_builder.cli <domain> [model_id] [options]")
        print(f"Domains: {list(COMMANDS.keys())}")
        print("\nExamples:")
        print("  python -m trench_builder.cli ship sailboat_v2")
        print("  python -m trench_builder.cli character hero --height 150")
        print("  python -m trench_builder.cli building tavern --archetype row_house")
        print("  python -m trench_builder.cli reverse model.glb")
        return

    domain = sys.argv[1]
    cmd = COMMANDS.get(domain)
    if not cmd:
        print(f"Unknown domain: {domain}. Available: {list(COMMANDS.keys())}")
        return

    spec = cmd(sys.argv[2:])
    if spec:
        build_and_export(spec)
        # Print summary
        print(f"\nComponents:")
        for c in spec.components:
            limits = f" {c.joint_limits}" if c.joint_limits else ""
            parent = f" → {c.parent}" if c.parent else " (root)"
            print(f"  {c.name:20s} {c.joint_type.value:14s}{limits:20s}{parent}")
    else:
        print("No spec generated.")


if __name__ == "__main__":
    main()
