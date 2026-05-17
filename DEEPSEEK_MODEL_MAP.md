# DEEPSEEK HUGGINGFACE — Available Models for Our Pipeline
# May 16, 2026

# ═══════════════════════════════════════════════════════
# EVERY MODEL. EVERY APPLICATION TO OUR SYSTEM.
# ═══════════════════════════════════════════════════════

DEEPSEEK_APPLICATIONS = """

  MODEL                      PARAMS    WHAT IT DOES FOR US
  ─────                      ──────    ────────────────────
  DeepSeek-V4-Pro            862B      RUNNING RIGHT NOW — this conversation
  DeepSeek-V4-Flash          158B      Fast/cheap alternative for cron jobs
  DeepSeek-OCR               3B        IMAGE → TEXT — read spectrograms, diagrams, labels
  DeepSeek-OCR-2             3B        Improved OCR — better text extraction for photo agent
  DeepSeek-VL2               ?         VISION → UNDERSTANDING — the correction drone's EYES
  Janus-Pro-7B               7B        SEE + GENERATE — compare pose AND draw corrections
  JanusFlow-1.3B             1.3B      Lightweight multimodal for edge (RPi5 on drone!)
  DeepSeek-Math-V2           685B      ERDOS CONJECTURE VERIFIER — autonomous proof checking
  DeepSeek-V3.2              685B      General reasoning for supervisor agent
  DeepSeek-Coder-33B         33B       Code generation for auto-fix pipeline
  PRISM (paper)              —         Text super-resolution — upscale drone camera text
  DualPath (paper)           —         Agent inference optimization — faster pipeline

"""

# ═══════════════════════════════════════════════════════
# CONCRETE PIPELINE UPGRADES
# ═══════════════════════════════════════════════════════

PIPELINE_UPGRADES = """

  1. CORRECTION DRONE — Vision Pipeline
     Camera → DeepSeek-OCR (read labels, gauges) → 
     DeepSeek-VL2 (understand scene, detect pose) → 
     Janus-Pro (compare observed vs ideal, generate correction overlay) →
     Haptic feedback

  2. PHOTO AGENT — Image Analysis
     PNG/JPG → DeepSeek-OCR (extract text from diagrams) →
     DeepSeek-VL2 (classify: spectrogram vs waveform vs chart) →
     Structured data export

  3. ERDOS CONJECTURE — Math Verification
     Sieve output → DeepSeek-Math-V2 (verify STABLE/BREACH) →
     Classified solutions → progression dashboard

  4. MULTI-AGENT PIPELINE — Inference Optimization
     DualPath architecture → reduce agent idle time →
     3x throughput on same hardware

  5. SUPERVISOR AGENT — Enhanced Review
     Code output → DeepSeek-Coder-33B (review for correctness) →
     Deeper than current self-critique (uses dedicated code model)

"""

# ═══════════════════════════════════════════════════════
# THE VINCULUM: Models as Fractions
# ═══════════════════════════════════════════════════════

MODEL_VINCULUM = """

  (Camera Feed / DeepSeek-VL2) = Scene Understanding
  (Scene Understanding / DeepSeek-OCR) = Extracted Text
  (Extracted Text / DeepSeek-Math-V2) = Verified Solution
  (Verified Solution / DeepSeek-V4-Pro) = Actionable Insight
  
  Each model is a vinculum node.
  The pipeline is a CHAIN of vinculums.
  Input / Model = Output → becomes input for next model.

"""

# ═══════════════════════════════════════════════════════
# EDGE DEPLOYMENT — Small models for the drone
# ═══════════════════════════════════════════════════════

EDGE_MODELS = """

  DRONE (Raspberry Pi 5 — 8GB RAM):
    DeepSeek-OCR-2 (3B)  → too large for RPi5 (needs 6GB+ VRAM)
    JanusFlow-1.3B       → MIGHT FIT on RPi5 with quantization
    ONNX-optimized pose  → MediaPipe is better for edge (runs at 30fps on RPi5)
    
  STRATEGY:
    Edge:    MediaPipe pose + Ridge regression (our trained corrector)
    Cloud:   DeepSeek-VL2 via API for complex scene understanding
    Hybrid:  Edge handles real-time (30fps pose). Cloud handles analysis (batch).

  The vinculum: (edge-inference / cloud-understanding) = real-time-correction

"""
