# Drill Chuck Mechanism Kit
## Trench-Builder Constraint-Validated Assembly

**Category:** Functional Mechanical Toys
**Price:** $10 (STL only) | $18 (Full Bundle)

---

### What This Is

Working drill chuck mechanism with threaded collar, chuck body, and drill bit. Revolute joint on Z-axis with 0-359° limits. Snap-fit assembly design — print and assemble without tools or glue.

### What You Get

**STL Pack ($10):**
- Individual STL files for each part, ready for 3D printing
- Tolerance card: verified 0.25mm clearance, 0.5mm chamfer
- Print orientation guide
- Material recommendations

**Full Bundle ($18):**
- Everything in the STL Pack
- **Digital Twin License:** GLB files at 3 resolutions (HP/MP/LP)
- **Physics Manifest:** JSON files with COM, joint limits, collision bounds
- Unity ConstraintLoader.cs script for auto-configuration
- Assembly guide with exploded view

### Parts

  - DRILL_BIT_DRILL_BIT
  - DRILL_BIT_Main
  - DRILL_CHUCK_CHUCK
  - DRILL_CHUCK_CHUCK_COLLAR

### Use Cases

  - Mechanical fidget hardware
  - Tool demonstrator models
  - Engineering student projects

### Print Settings

- **Orientation:** Print flat on the bed (axial Z-axis)
- **Material:** PETG minimum. PLA acceptable for low-load demos.
- **Infill:** 4-5 perimeters, 100% infill or 60% gyroid
- **Lubrication:** PTFE dry grease recommended for moving parts

### Digital Twin License

The JSON manifest auto-configures physics in Unity:
1. Drop ConstraintLoader.cs on the root GameObject
2. Assign the DRILL_BIT_DRILL_BIT_manifest.json
3. ConfigurableJoints, collision bounds, and drive_ratios auto-configure

No manual joint setup. No guessing torque limits. The audit report IS the physics configuration.

---

Generated: 2026-06-15 18:42
Pipeline: mechanical_rig_pipeline.py (Blender 5.1.1)
Tolerances verified on: Ender 3 V2, 0.4mm nozzle, PLA
