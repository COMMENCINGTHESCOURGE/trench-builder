# Carburetor Cutaway Model Set
## Trench-Builder Constraint-Validated Assembly

**Category:** Education & Display Models
**Price:** $12 (STL only) | $22 (Full Bundle)

---

### What This Is

Detailed carburetor cutaway with manifold, throttle plate, gasket, air filter, control arm, and lever. Fixed and revolute joints mapped. Designed for FDM printing with 0.25mm clearance and chamfered edges.

### What You Get

**STL Pack ($12):**
- Individual STL files for each part, ready for 3D printing
- Tolerance card: verified 0.25mm clearance, 0.5mm chamfer
- Print orientation guide
- Material recommendations

**Full Bundle ($22):**
- Everything in the STL Pack
- **Digital Twin License:** GLB files at 3 resolutions (HP/MP/LP)
- **Physics Manifest:** JSON files with COM, joint limits, collision bounds
- Unity ConstraintLoader.cs script for auto-configuration
- Assembly guide with exploded view

### Parts

  - CARBURETOR_CARBURETOR
  - CARBURETOR_MANIFOLD
  - CARBURETOR_CARBURETOR_PLATE
  - CARBURETOR_CARBURETOR_GASKET
  - CARBURETOR_AIR_FILTER_COVER
  - CARBURETOR_CARBURETOR_CONTROL_ARM
  - CARBURETOR_CARBURETOR_LEVER
  - CARBURETOR_Surface_1
  - CARBURETOR_Surface_2

### Use Cases

  - Automotive training aids
  - Mechanical engineering coursework
  - Museum display models
  - Desk display pieces

### Print Settings

- **Orientation:** Print flat on the bed (axial Z-axis)
- **Material:** PETG minimum. PLA acceptable for low-load demos.
- **Infill:** 4-5 perimeters, 100% infill or 60% gyroid
- **Lubrication:** PTFE dry grease recommended for moving parts

### Digital Twin License

The JSON manifest auto-configures physics in Unity:
1. Drop ConstraintLoader.cs on the root GameObject
2. Assign the CARBURETOR_CARBURETOR_manifest.json
3. ConfigurableJoints, collision bounds, and drive_ratios auto-configure

No manual joint setup. No guessing torque limits. The audit report IS the physics configuration.

---

Generated: 2026-06-15 18:42
Pipeline: mechanical_rig_pipeline.py (Blender 5.1.1)
Tolerances verified on: Ender 3 V2, 0.4mm nozzle, PLA
