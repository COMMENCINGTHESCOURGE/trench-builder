# Trench-Builder Product Catalog
## Constraint-Validated Mechanical Assemblies

Every product ships with:
- STL files for 3D printing (verified tolerances, chamfered edges)
- GLB files at 3 resolutions (HP/MP/LP) with physics rigs
- JSON manifest: COM, joint limits, collision bounds, drive_ratios
- Unity ConstraintLoader.cs for auto-configuration
- Assembly guide with print settings and material recommendations

---

## Phase 1 — Ready to Ship

### 3-Stage Spur Gearbox Assembly
**$15 (STL) | $30 (Bundle)**
*Robotics & Mechanical Advantage*

A validated 3-stage spur gear train: 15T driver → 45T idler → 60T driven. 4:1 total reduction. 0.2mm backlash for FDM printing. Each gear ships with a Unity-ready JSON manifest that auto-configures ConfigurableJoints with drive_ratio, friction_coefficient, and driven_by coupling. Includes calculated torque limits (0.07 N·m input, 0.28 N·m output in PLA) with the full formula documented for material substitution.

**Parts (5):** GEARBOX_PRIMARY_GEAR_SHAFT, GEARBOX_REDUCTION_GEAR_SHAFT, GEARBOX_FINAL_GEAR_SHAFT, GEARBOX_GEARBOX_FRONT, GEARBOX_GEARBOX_REAR

---

### Miniature Engine Block Assembly
**$20 (STL) | $38 (Bundle)**
*Functional Prototyping & Education*

Complete 4-cylinder engine block assembly with crankshaft, flywheel, connecting rods, pistons, and bearings. Revolute joints with verified 0-359° rotation. COM calculated from mesh volume for accurate gravity simulation. Includes tolerance card (0.25mm clearance, 0.5mm chamfer) tested on Ender 3 V2.

**Parts (10):** CRANK_CRANKSHAFT, CRANK_FLYWHEEL, CONNECTING_ROD_CONNECTING_ROD, ENG_BLOCK_CYLINDER, ENG_BLOCK_ENG_BLOCK_FRONT, ENG_BLOCK_ENG_BLOCK_REAR, NEW_PART_PISTON, NEW_PART_PISTON_PIN, NEW_PART_PISTON_RING, ENG_BEARING_ENG_BEARING

---

### Carburetor Cutaway Model Set
**$12 (STL) | $22 (Bundle)**
*Education & Display Models*

Detailed carburetor cutaway with manifold, throttle plate, gasket, air filter, control arm, and lever. Fixed and revolute joints mapped. Designed for FDM printing with 0.25mm clearance and chamfered edges.

**Parts (9):** CARBURETOR_CARBURETOR, CARBURETOR_MANIFOLD, CARBURETOR_CARBURETOR_PLATE, CARBURETOR_CARBURETOR_GASKET, CARBURETOR_AIR_FILTER_COVER, CARBURETOR_CARBURETOR_CONTROL_ARM, CARBURETOR_CARBURETOR_LEVER, CARBURETOR_Surface_1, CARBURETOR_Surface_2

---

### Drill Chuck Mechanism Kit
**$10 (STL) | $18 (Bundle)**
*Functional Mechanical Toys*

Working drill chuck mechanism with threaded collar, chuck body, and drill bit. Revolute joint on Z-axis with 0-359° limits. Snap-fit assembly design — print and assemble without tools or glue.

**Parts (4):** DRILL_BIT_DRILL_BIT, DRILL_BIT_Main, DRILL_CHUCK_CHUCK, DRILL_CHUCK_CHUCK_COLLAR

---

### Fuel System Component Pack
**$8 (STL) | $15 (Bundle)**
*Complementary Parts*

Fuel tank with screw-on fuel cap. Revolute joint on cap with 0-720° limits. Designed to complement the Engine Block Assembly.

**Parts (2):** ENG_BLOCK_FUEL_TANK, ENG_BLOCK_FUEL_CAP

---

## Phase 2 — Requires Parametric CAD (Coming Soon)

These products have the full engineering math calculated and verified.
They are ready for parametric modeling in Fusion 360 or Onshape.
Contact for pre-order or CAD collaboration.

### 3-Stage Planetary Gearbox
**$25 (STL) | $50 (Bundle) — Pre-order**
*Robotics & Heavy-Lift Mechanisms*

True epicyclic (planetary) gearbox with sun gear, 3 planet gears, and internal ring gear. 27:1 torque multiplication in a 40mm diameter package. Zero-backlash achievable with proper planet carrier tolerances. Designed for Nylon PA12 printing — PLA will strip the sun gear teeth on first load.

**Engineering Spec:**
```json
{
  "mechanism_type": "epicyclic_gear",
  "stages": 1,
  "sun_teeth": 15,
  "planet_teeth": 21,
  "planet_count": 3,
  "ring_teeth": 57,
  "module_mm": 1.5,
  "pressure_angle_deg": 20,
  "ratio": "4.8:1 per stage (27:1 for 2-stage)",
  "torque_multiplier": 27.0,
  "backlash_mm": 0.15,
  "max_input_torque_nm": 0.12,
  "max_output_torque_nm": 3.24,
  "material": "Nylon PA12 or PETG (PLA too brittle for sun gear)"
}
```

---

### Rack and Pinion Steering System
**$15 (STL) | $30 (Bundle) — Pre-order**
*Linear Motion & Steering*

Converts rotational input (pinion) to precise linear output (rack). 12-tooth pinion with 1.5mm module drives a linear rack with 0.15mm backlash. One full pinion rotation = 56.5mm of linear travel. Includes guide rails and end-stops to prevent derailment under load.

**Engineering Spec:**
```json
{
  "mechanism_type": "rack_and_pinion",
  "pinion_teeth": 12,
  "module_mm": 1.5,
  "pressure_angle_deg": 20,
  "pinion_radius_mm": 9.0,
  "linear_travel_per_rev_mm": 56.5,
  "backlash_mm": 0.15,
  "max_linear_force_n": 25.0,
  "material": "PETG (rack) + Nylon (pinion)"
}
```

---

### Compound Pulley / Block and Tackle
**$10 (STL) | $22 (Bundle) — Pre-order**
*Mechanical Advantage & Rigging*

4-sheave compound pulley system providing 4:1 mechanical advantage. Pull 1 meter of rope → lift 250g load by 0.25 meters. Sheaves spin freely on printed axle pins with 0.25mm clearance. Mounting bracket includes tie-off cleat. Requires 2mm nylon cord (not included).

**Engineering Spec:**
```json
{
  "mechanism_type": "block_and_tackle",
  "sheave_count": 4,
  "mechanical_advantage": "4:1",
  "sheave_diameter_mm": 25.0,
  "rope_groove_width_mm": 2.0,
  "max_lift_force_n": 50.0,
  "material": "PETG (sheaves) + PLA (bracket)",
  "requires_external": "2mm nylon cord (not included)"
}
```

---

## Phase 3 — New Domains: Ships, Buildings, Characters (Coming Soon)

These extend the constraint-validation framework to nautical engineering,
architectural design, and biomechanical character rigging.
Vinculum ratios govern every proportion and joint limit.

### Constraint-Validated Sailboat Hull Kit
**$18 (STL) | $38 (Bundle) — Pre-order**
*Nautical Engineering & Model Ships*

Complete sailboat hull with keel, rudder, mast step, and propeller shaft. Naval architecture constraints verified: 4:1 length-to-beam ratio, draft at 12% of displacement. Rudder ±35° hard stops. Self-righting keel ratio.

**Engineering Spec:**
```json
{
  "domain": "ship",
  "core_vinculums": {
    "hull_length_beam": "4:1",
    "draft_displacement": "0.12",
    "mast_height_hull_length": "1.3",
    "rudder_angle": "\u00b135\u00b0",
    "propeller_rpm_max": 2500
  },
  "stability_requirement": "keel_mass must exceed wind heeling moment"
}
```

---

### Row House Architectural Kit — 8 Archetypes
**$20 (STL) | $42 (Bundle) — Pre-order**
*Architectural Visualization & Urban Planning*

8 architectural archetypes with constraint-validated proportions. Operable doors/windows. Load paths verified: roof → walls → foundation. Stair rise/run at 0.58. Basement includes waterproofing spec.

**Engineering Spec:**
```json
{
  "domain": "building",
  "archetypes": [
    "bungalow",
    "row_house",
    "apartment",
    "commercial",
    "school",
    "hospital",
    "warehouse",
    "pagoda"
  ],
  "core_vinculums": {
    "window_wall_ratio": "0.25",
    "roof_pitch_snow_load": "1.2",
    "stair_rise_run": "0.58",
    "basement_depth_groundwater": "0.5"
  }
}
```

---

### Gunpla-Engineered Character Rig — 22 Bones
**$15 (STL) | $40 (Bundle) — Pre-order**
*Game-Ready Characters & Animation*

22-bone character rig with Gunpla engineering: butterfly shoulders, bicep/thigh swivel cuts, double-hinge knees. Ball-and-socket hips/ankles. All proportions verified against anatomical vinculum ratios. 2,500 verts.

**Engineering Spec:**
```json
{
  "domain": "character",
  "bone_count": 22,
  "core_vinculums": {
    "head_height_total": "0.15",
    "torso_height_total": "0.35",
    "arm_length_total": "0.38",
    "leg_length_total": "0.50",
    "hand_length_total": "0.11",
    "foot_length_total": "0.16"
  },
  "gunpla_engineering": {
    "butterfly_shoulder": "30\u00b0 forward sweep",
    "bicep_swivel_cut": "\u00b190\u00b0 isolated yaw",
    "thigh_swivel_cut": "\u00b145\u00b0 isolated yaw",
    "double_hinge_knee": "full 180\u00b0 fold without clipping"
  }
}
```

---

## Pricing

### Phase 1 — Mechanical Assemblies (Ready)
- Individual: $65 (STL) | $123 (Bundle)
- **Launch Bundle: $98**

### Phase 2 — Advanced Mechanisms (Pre-order)
- Individual: $50 (STL) | $102 (Bundle)

### Phase 3 — Ships, Buildings, Characters (Pre-order)
- Individual: $53 (STL) | $120 (Bundle)

### Complete Collection (All 11)
- **$345** ($258 early access)
