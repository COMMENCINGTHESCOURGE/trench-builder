# CORRECTION DRONE — 3rd Person Observer
# May 16, 2026

# This drone doesn't carry weight. It CARRIES FEEDBACK.
# It watches from above and tells the suit: "fix this."

DRONE_OBSERVER = """
THE CORRECTION DRONE:

  POSITION:  3m above, 2m behind the suit. Orbiting slowly.
  CAMERA:    3D pose estimation (joint positions in world space)
  COMPARE:   Intended movement (checkpoint model) vs realized (camera)
  OUTPUT:    Per-joint delta feedback in real-time

  ARCHITECTURE:
    Drone captures joint positions → maps to checkpoint stage →
    compares against ideal angles → broadcasts corrections →
    suit adjusts next movement cycle.

  VINCULUM (observer):
    (observed_angle / ideal_angle) = correction_factor
    If > 1.0: you're over-extending → pull back
    If < 1.0: you're under-performing → push harder
    If = 1.0: perfect. Drone stays silent.
"""

# CONNECTION TO SUPERVISOR AGENT
SUPERVISOR_PATTERN = """
  CODE SUPERVISOR                    MOVEMENT SUPERVISOR
  ──────────────                     ───────────────────
  Watches Hermes build code          Watches pilot move suit
  Checks building realm rules        Checks biomechanical range
  Flags orientation mistakes         Flags joint angle errors
  Outputs supervisor_directives.json Outputs correction_vector.json
  Retroactive fixes past mistakes    Corrects next movement cycle
  
  SAME PATTERN. DIFFERENT DOMAIN.
  The drone IS the supervisor agent for the body.
"""

# WHAT THE DRONE CORRECTS
CORRECTIONS = """
  JOINT-BY-JOINT FEEDBACK:

  toe:      "Push off 3° harder. You're losing propulsion."
  ankle:    "Plantarflexion is early by 2 frames. Delay the release."
  knee:     "Extension is lagging by 8°. Increase quad activation."
  hip:      "Counter-rotation missing. Shoulders are fighting hips."
  shoulder: "Arms are 15° behind counter-phase. Swing faster."
  neck:     "Head is drifting. Lock eyes forward. Stabilize."

  CHECKPOINT DETECTION:
    Drone sees the movement pattern → identifies checkpoint stage →
    loads ideal angles for that stage → compares frame-by-frame →
    returns delta vector for next cycle.

  BOUNCE CORRECTION (hardest stage):
    Observed:   toe=42° ankle=22° knee=3° hip=14° shoulder=-9° neck=2°
    Ideal:      toe=45° ankle=25° knee=5° hip=15° shoulder=-12° neck=3°
    Delta:       -3°     -3°    -2°    -1°       +3°       -1°
    Feedback:   "Toe and ankle need +3°. Shoulders overshooting by 3°."
"""

# FEEDBACK LOOP
FEEDBACK_LOOP = """
  CYCLE N:
    Pilot moves → drone captures → compare to ideal →
    delta calculated → haptic/audio feedback → pilot adjusts →
  
  CYCLE N+1:
    Pilot moves with correction → drone captures → smaller delta →
    feedback confirms improvement → pilot internalizes →
  
  CYCLE N+5:
    Pilot moves correctly → delta ≈ 0 → drone stays silent →
    muscle memory formed → checkpoint mastered

  THE DRONE MAKES THE VINCULUM SELF-CORRECTING:
    (observed / ideal) → correction → (next_observed / ideal) → smaller delta
    The vinculum converges to 1.0 over cycles.
"""

# TRAINING DATA GENERATION
TRAINING_DATA = """
  The drone GENERATES training data:
  
  For each movement cycle:
    • 6 joints × 6 frames = 36 observed angles
    • 36 ideal angles (from checkpoint model)
    • 36 delta values (observed − ideal)
    • Correction string ("knee: +2°")
    • Time to correct (how many cycles to converge)
  
  Over 100 cycles:
    • 3,600 data points per checkpoint stage
    • 28,800 points across all 8 stages
    • Learning: which joints need most correction, fastest learning rate
  
  THIS DATA FEEDS BACK INTO:
    • The checkpoint system (refine ideal angles)
    • The mecha optimization (where to add assist)
    • The sprite sheet generator (actual vs ideal frames)
    • Kaggle training dataset (supervised learning for pose estimation)
"""

# SUMMARY
SUMMARY = """
  THE DETACHABLE DRONE:
    1. Is the supervisor agent for physical movement
    2. Sees what the pilot can't see (3rd person view)
    3. Auto-corrects joint angles in real-time
    4. Generates training data from every movement cycle
    5. Makes the vinculum self-converging: observed → ideal
    6. Same architecture as code supervisor — different domain
    
  The drone doesn't carry weight. It carries TRUTH.
  It tells the suit what the pilot's body already knows but can't see.
"""
