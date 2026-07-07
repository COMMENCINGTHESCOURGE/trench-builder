#!/usr/bin/env python
"""
KINETIC_TORSION_ENGINE v2.0 — Production-Hardened
═══════════════════════════════════════════════════════
Measures Logical Density, Input Velocity, and Semantic Drift.
Wired to the vinculum: torsion = vinculum stress metric.

IMPROVEMENTS OVER v1:
  • Configurable constants (norm, edit_penalty, thresholds)
  • Pure _calculate() returns value, doesn't mutate self
  • Division-by-zero guard on velocity
  • reset() method for session reuse
  • .vinculum property: maps torsion to mod9 classification
  • Type hints throughout

DaShawn / Guinea Pig Trench LLC — May 2026
"""
import time
from collections import deque
from typing import Dict, Optional, Literal

StatusType = Literal['STABLE','CANDIDATE','BREACH','SINGULARITY']

class TorsionEngine:
    """Measures rhythm regularity with edit-aware torsion metric.
    
    Low torsion = events at constant intervals = STABLE vinculum.
    High torsion = variance + edits = BREACH or collapse.
    """
    def __init__(self, window_size: int = 20, mode: str = "GENERIC",
                 norm_constant: Optional[float] = None,
                 edit_penalty_multiplier: float = 10.0,
                 thresholds: Optional[Dict[str, float]] = None):
        self.intervals = deque(maxlen=window_size)
        self.last_time = time.time()
        self.torsion = 0.0
        self.total_steps = 0
        self.saved_steps = 0
        self.recent_edits = deque(maxlen=window_size)
        self.mode = mode
        self.window_size = window_size
        
        # Configurable constants
        MODE_NORMS = {"LOCAL": 50.0, "GENERIC": 1.0, "SIM": 1.0, "HERMES": 5.0}
        self.norm_constant = norm_constant if norm_constant is not None else MODE_NORMS.get(mode, 1.0)
        self.edit_penalty = edit_penalty_multiplier
        
        # Configurable thresholds
        self.thresholds = thresholds or {
            "STABLE": 0.01, "CANDIDATE": 0.15, "BREACH": 1.00
        }

    def record_event(self, is_edit: bool = False, is_swallow: bool = False):
        """Record a single event (keystroke, API call, logic step)."""
        now = time.time()
        diff = now - self.last_time
        self.last_time = now
        self.intervals.append(diff)
        self.total_steps += 1
        if is_swallow:
            self.saved_steps += 1
        self.recent_edits.append(1 if is_edit else 0)
        self.torsion = self._calculate() 

    @property
    def efficiency(self) -> float:
        """Ratio of swallows to total steps."""
        if self.total_steps == 0: return 0.0
        return (self.saved_steps / self.total_steps) * 100

    def _calculate(self) -> float:
        """Pure computation of torsion. Returns value, doesn't mutate.
        
        Torsion = (sum |interval[i] - interval[i-1]| / (n * norm)) * edit_penalty
        """
        if len(self.intervals) < 2: return 0.0
        
        diff_of_diffs = sum(
            abs(self.intervals[i] - self.intervals[i-1])
            for i in range(1, len(self.intervals))
        )
        base = diff_of_diffs / (len(self.intervals) * max(0.001, self.norm_constant))
        
        if self.recent_edits:
            edit_ratio = sum(self.recent_edits) / max(1, len(self.recent_edits))
            base *= (1 + edit_ratio * self.edit_penalty)
        
        return round(base, 6)

    @property
    def velocity(self) -> float:
        """Event rate (Hz). Zero-division safe."""
        if not self.intervals: return 0.0
        avg = sum(self.intervals) / len(self.intervals)
        return 1.0 / avg if avg > 0 else 0.0

    def get_status(self) -> StatusType:
        """Classify torsion into STABLE/CANDIDATE/BREACH/SINGULARITY."""
        t = self.torsion
        if t < self.thresholds["STABLE"]:     return "STABLE"
        if t < self.thresholds["CANDIDATE"]:  return "CANDIDATE"
        if t < self.thresholds["BREACH"]:     return "BREACH"
        return "SINGULARITY"

    @property
    def mod9_class(self) -> int:
        """Map torsion to mod9 class for vinculum pipeline."""
        mapping = {"STABLE": 1, "CANDIDATE": 4, "BREACH": 3, "SINGULARITY": 0}
        return mapping.get(self.get_status(), 0)

    @property
    def vinculum(self) -> str:
        """Human-readable vinculum status."""
        status = self.get_status()
        return {
            "STABLE":      f"(intent/resistance)=balanced [{status}]",
            "CANDIDATE":   f"(intent/resistance)=under_stress [{status}]",
            "BREACH":      f"(intent/resistance)=breaking [{status}]",
            "SINGULARITY": f"(intent/resistance)=collapsed [DET→0]",
        }.get(status, f"({status})")

    def get_metrics(self) -> Dict[str, float]:
        """Full kinetic metrics + vinculum mapping."""
        return {
            "torsion": self.torsion,
            "efficiency": self.efficiency,
            "velocity": self.velocity,
            "status": self.get_status(),
            "mod9_class": self.mod9_class,
            "steps": self.total_steps,
            "swallows": self.saved_steps,
            "vinculum": self.vinculum,
        }

    def reset(self):
        """Reset for a new session — preserves configuration."""
        self.intervals.clear()
        self.recent_edits.clear()
        self.last_time = time.time()
        self.torsion = 0.0
        self.total_steps = 0
        self.saved_steps = 0


if __name__ == "__main__":
    print("═══ KINETIC TORSION ENGINE v2.0 ═══")
    engine = TorsionEngine(mode="HERMES", window_size=10)
    
    # Simulate a session: stable → edits → recovery
    print("Phase 1: STABLE — regular rhythm")
    for i in range(10):
        time.sleep(0.05)
        engine.record_event()
    
    print("Phase 2: BREACH — heavy editing")
    for i in range(10):
        time.sleep(0.05 + (0.02 * (i % 3)))
        engine.record_event(is_edit=(i % 2 == 0))
    
    m = engine.get_metrics()
    print(f"  Torsion: {m['torsion']:.4f} | {m['vinculum']} | mod9={m['mod9_class']}")
    
    print("Phase 3: RECOVERY — stable again")
    engine.reset()
    for i in range(10):
        time.sleep(0.05)
        engine.record_event(is_swallow=(i > 5))
    
    m = engine.get_metrics()
    print(f"  Torsion: {m['torsion']:.4f} | {m['vinculum']} | efficiency={m['efficiency']:.1f}%")
    
    print("\n✓ Production-hardened. Vinculum heartbeat active.")
