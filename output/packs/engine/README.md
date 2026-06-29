# Miniature Engine Block Assembly
## Trench-Builder Constraint-Validated Assembly

**Category:** Functional Prototyping & Education
**Price:** $20 (STL only) | $38 (Full Bundle)

---

### What This Is

Complete 4-cylinder engine block assembly with crankshaft, flywheel, connecting rods, pistons, and bearings. Revolute joints with verified 0-359° rotation. COM calculated from mesh volume for accurate gravity simulation. Includes tolerance card (0.25mm clearance, 0.5mm chamfer) tested on Ender 3 V2.

### What You Get

**STL Pack ($20):**
- Individual STL files for each part, ready for 3D printing
- Tolerance card: verified 0.25mm clearance, 0.5mm chamfer
- Print orientation guide
- Material recommendations

**Full Bundle ($38):**
- Everything in the STL Pack
- **Digital Twin License:** GLB files at 3 resolutions (HP/MP/LP)
- **Physics Manifest:** JSON files with COM, joint limits, collision bounds
- Unity ConstraintLoader.cs script for auto-configuration
- Assembly guide with exploded view

### Parts

  - CRANK_CRANKSHAFT
  - CRANK_FLYWHEEL
  - CONNECTING_ROD_CONNECTING_ROD
  - ENG_BLOCK_CYLINDER
  - ENG_BLOCK_ENG_BLOCK_FRONT
  - ENG_BLOCK_ENG_BLOCK_REAR
  - NEW_PART_PISTON
  - NEW_PART_PISTON_PIN
  - NEW_PART_PISTON_RING
  - ENG_BEARING_ENG_BEARING

### Use Cases

  - Mechanics training simulators
  - Custom RC engine mockups
  - STEM classroom demonstrations
  - Cosplay mechanical props

### Print Settings

- **Orientation:** Print flat on the bed (axial Z-axis)
- **Material:** PETG minimum. PLA acceptable for low-load demos.
- **Infill:** 4-5 perimeters, 100% infill or 60% gyroid
- **Lubrication:** PTFE dry grease recommended for moving parts

### Digital Twin License

The JSON manifest auto-configures physics in Unity:
1. Drop ConstraintLoader.cs on the root GameObject
2. Assign the CRANK_CRANKSHAFT_manifest.json
3. ConfigurableJoints, collision bounds, and drive_ratios auto-configure

No manual joint setup. No guessing torque limits. The audit report IS the physics configuration.

---

Generated: 2026-06-15 18:42
Pipeline: mechanical_rig_pipeline.py (Blender 5.1.1)
Tolerances verified on: Ender 3 V2, 0.4mm nozzle, PLA
