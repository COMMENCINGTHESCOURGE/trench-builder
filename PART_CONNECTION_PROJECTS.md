# PART CONNECTION PROJECTS — Complete Inventory
# May 16, 2026

PROJECTS = """
═══════════════════════════════════════════════════════════
  5 PROJECTS. ALL ABOUT HOW PARTS CONNECT.
═══════════════════════════════════════════════════════════

  1. K2.6 INSTANT — Part Affordance Engine
     ~/Projects/part_affordance/k26_instant.py  (788 lines, 33KB)
     ~/Projects/part_affordance/k26_dashboard.html

     "A bolt is not a bolt. A brick is a hammer. Geometry IS function."
     
     • Affordance types: STRUT, BRACKET, FASTENER, GUSSET, MOUNT, BEAM,
       COLUMN, TENSION_MEMBER, WORM_SCREW, HELICAL_RACK...
     • Gear meshing validation (module, pitch, center distance)
     • Geometry calculus (lever MA, beam deflection, thermal, resonance)
     • Cross-use assembly (worm drive, rack-pinion, planetary)
     • Aluminum extrusion (8020/4040/4080)
     • MacGyver improvisation (brick→HIT, butterknife→TURN)
     • Tensegrity, wireless charging

  2. ALE — Assembly Logic Engine
     ~/Projects/ale/ale_ingest.py  (573 lines, 26KB)
     ~/Projects/ale/GEMINI.md
     ~/Projects/ale/tent_assembly.json

     "Parses assembly manuals, extracts part lists, classifies functional
     roles, builds dependency graphs, and outputs machine-readable JSON-LD."

     • PDF/Text → JSON-LD Part Ontology
     • Functional role classification
     • Liaison graph (how parts connect to each other)
     • Built-in tent assembly demo
     • Product/demo decision pipeline

  3. ONSHAPE CAD BRIDGE
     ~/Projects/trench_builder/onshape_bridge.py
     ~/Projects/trench_builder/onshape_pull_agent.py
     ~/Projects/trench_builder/cad_imports/ (33 STL files)

     • 33-part CAD motor assembly imported
     • Piston, crankshaft, carburetor, flywheel, gearbox
     • STL files ready for Three.js rendering
     • Cron job: onshape-cad-pull (every 6h)

  4. MANIFESTATION BRIDGE
     ~/Projects/trench_builder/MANIFESTATION_BRIDGE.html

     "Transfer functions — Electrical→Optical→Acoustic→Thermal"

     • How energy flows between parts
     • Brownout propagation simulation
     • Web Audio hum generator
     • PBR material response

  5. BLOOMING ONION — SDF Parts
     ~/Projects/blooming-onion/blooming_onion_sdf.html
     ~/Projects/blooming-onion/engine/
     ~/Projects/blooming-onion/game/

     • Signed Distance Field rendering
     • Parts defined by mathematical distance functions
     • Perspective portal (how parts appear from different views)
     • Thrown Planet Phase 1

═══════════════════════════════════════════════════════════
  THE KIRAGAMI CONNECTION — Where folded metal meets parts
═══════════════════════════════════════════════════════════

  KIRAGAMI needs:
    • Fold affordance (what can this crease DO?)
    • Interlock validation (does fold A lock into fold B?)
    • Assembly sequence (which fold comes first?)
    • D_mat per connection (what's the material resistance at this joint?)

  ALL FIVE PROJECTS CAN HELP:
    K2.6 → Add FOLD as a new AffordanceType
    ALE  → Parse kirigami assembly sequence into JSON-LD graph
    CAD  → Import folded-sheet geometry from Onshape
    Bridge → Model energy flow through folded joints
    SDF  → Render fold geometry as distance fields
"""

NEXT_ACTION = """
  ACTION: Run K2.6 Instant with kirigami-specific parts.
    python ~/Projects/part_affordance/k26_instant.py --part fold_90deg
    python ~/Projects/part_affordance/k26_instant.py --part folded_titanium_plate
    
  Then wire ALE to parse the kirigami assembly:
    python ~/Projects/ale/ale_ingest.py --demo (shows tent assembly)
    → Add kirigami fold sequence as new assembly type
    
  Then import CAD geometry:
    python ~/Projects/trench_builder/onshape_bridge.py
    → Pull folded-sheet models into Three.js
"""
