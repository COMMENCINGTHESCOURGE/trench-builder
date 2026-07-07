# 3-Stage Spur Gearbox Assembly
## Trench-Builder Constraint-Validated Assembly

**Category:** Robotics & Mechanical Advantage
**Price:** $15 (STL only) | $30 (Full Bundle)

---

### What This Is

A validated 3-stage spur gear train: 15T driver → 45T idler → 60T driven. 4:1 total reduction. 0.2mm backlash for FDM printing. Each gear ships with a Unity-ready JSON manifest that auto-configures ConfigurableJoints with drive_ratio, friction_coefficient, and driven_by coupling. Includes calculated torque limits (0.07 N·m input, 0.28 N·m output in PLA) with the full formula documented for material substitution.

### What You Get

**STL Pack ($15):**
- Individual STL files for each part, ready for 3D printing
- Tolerance card: verified 0.25mm clearance, 0.5mm chamfer
- Print orientation guide
- Material recommendations

**Full Bundle ($30):**
- Everything in the STL Pack
- **Digital Twin License:** GLB files at 3 resolutions (HP/MP/LP)
- **Physics Manifest:** JSON files with COM, joint limits, collision bounds
- Unity ConstraintLoader.cs script for auto-configuration
- Assembly guide with exploded view

### Parts

  - GEARBOX_PRIMARY_GEAR_SHAFT
  - GEARBOX_REDUCTION_GEAR_SHAFT
  - GEARBOX_FINAL_GEAR_SHAFT
  - GEARBOX_GEARBOX_FRONT
  - GEARBOX_GEARBOX_REAR

### Use Cases

  - RC car drivetrain prototyping
  - Robotics gear reduction (4:1 ratio)
  - Engineering capstone projects
  - Physics sandbox games (Besiege, Scrap Mechanic)

### Print Settings

- **Orientation:** Print flat on the bed (axial Z-axis)
- **Material:** PETG minimum. PLA acceptable for low-load demos.
- **Infill:** 4-5 perimeters, 100% infill or 60% gyroid
- **Lubrication:** PTFE dry grease recommended for moving parts

### Digital Twin License

The JSON manifest auto-configures physics in Unity:
1. Drop ConstraintLoader.cs on the root GameObject
2. Assign the GEARBOX_PRIMARY_GEAR_SHAFT_manifest.json
3. ConfigurableJoints, collision bounds, and drive_ratios auto-configure

No manual joint setup. No guessing torque limits. The audit report IS the physics configuration.

---

Generated: 2026-06-15 18:42
Pipeline: mechanical_rig_pipeline.py (Blender 5.1.1)
Tolerances verified on: Ender 3 V2, 0.4mm nozzle, PLA
