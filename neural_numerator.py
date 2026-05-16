#!/usr/bin/env python
"""
NEURAL NUMERATOR — Completes the Vinculum
═══════════════════════════════════════════════════════
The vinculum V(A) = A_intent / (D_mat ⊗ D_bio) 
has been missing its numerator. A_intent was a placeholder.
N_neuro is the tensor that generates it from the player's will.

DaShawn / Guinea Pig Trench LLC — May 2026
"""
import numpy as np
from dataclasses import dataclass, field
from typing import Tuple

# ═══════════════════════════════════════════════════════
# NEURAL NUMERATOR TENSOR — N_neuro
# ═══════════════════════════════════════════════════════
# Maps motor-cortex intent → [Force, Velocity, Precision]
# Three irreducible subspaces — same structure as D_bio

@dataclass
class NeuralNumerator:
    """N_neuro: rank-2 symmetric tensor mapping will → action vector."""
    
    # Diagonal — pure neural resistances
    N_ff: float = 1.0   # Focus-Fatigue: sustained attention decay
    N_sc: float = 1.0   # Skill-Calibration: motor learning accuracy
    N_ar: float = 1.0   # Arousal-Regulation: optimal activation window
    
    # Off-diagonal — cross-couplings (Yerkes-Dodson law)
    N_fs: float = 0.0   # Focus-Skill coupling
    N_fa: float = 0.0   # Focus-Arousal coupling  
    N_sa: float = 0.0   # Skill-Arousal coupling
    
    # State variables
    focus_pool: float = 100.0       # Attentional resource (decays with time)
    skill_level: float = 0.5        # Motor learning (0-1, improves with practice)
    arousal: float = 0.7            # Yerkes-Dodson optimal: 0.5-0.8
    
    # Parameters
    tau_focus: float = 3600.0       # Attention half-life (seconds)
    learning_rate: float = 0.001    # Skill improvement per successful strike
    arousal_optimal: float = 0.65   # Peak performance arousal
    
    def update(self, dt: float, strike_success: bool, distraction: float = 0.0):
        """Update neural state over time dt."""
        # Focus decays with time, recovers with rest
        self.focus_pool = max(0, self.focus_pool - dt * 0.028 - distraction * 10)
        
        # Skill improves with successful strikes (Hebbian learning)
        if strike_success:
            self.skill_level = min(1.0, self.skill_level + self.learning_rate)
        else:
            self.skill_level = max(0.1, self.skill_level - self.learning_rate * 0.3)
        
        # Compute tensor components from state
        self._compute_tensor()
    
    def _compute_tensor(self):
        """Update tensor components from neural state."""
        # N_ff: focus fatigue resistance
        focus_pct = self.focus_pool / 100.0
        self.N_ff = 1.0 + (1.0 - focus_pct) * 2.0  # 1.0 → 3.0 as focus depletes
        
        # N_sc: skill calibration (inverse — higher skill = lower resistance)
        self.N_sc = 1.0 / (0.1 + self.skill_level)  # 10.0 → 0.91 as skill improves
        
        # N_ar: arousal regulation (Yerkes-Dodson inverted-U)
        arousal_error = abs(self.arousal - self.arousal_optimal)
        self.N_ar = 1.0 + arousal_error * 5.0  # 1.0 at optimal, spikes at extremes
        
        # Cross-couplings
        self.N_fs = 0.3 * (1.0 - focus_pct) * (1.0 - self.skill_level)
        self.N_fa = 0.2 * (1.0 - focus_pct) * arousal_error * 5.0
        self.N_sa = 0.25 * self.skill_level * arousal_error * 3.0
    
    @property
    def matrix(self) -> np.ndarray:
        """N_neuro as 3x3 symmetric matrix."""
        return np.array([
            [self.N_ff, self.N_fs, self.N_fa],
            [self.N_fs, self.N_sc, self.N_sa],
            [self.N_fa, self.N_sa, self.N_ar],
        ])
    
    def generate_intent(self, raw_intent: np.ndarray) -> np.ndarray:
        """Map raw neural will → realized action intent vector.
        
        A_intent = N_neuro^{-1} · A_raw
        
        A_raw = [Force_desired, Velocity_desired, Precision_desired]
        The neural tensor transforms raw will into executable intent.
        """
        try:
            N_inv = np.linalg.inv(self.matrix)
            return N_inv @ raw_intent
        except np.linalg.LinAlgError:
            # Singular matrix — neural overload
            # Player "blanks out" — intent collapses to random twitch
            return np.random.normal(0, 0.1, 3)
    
    def singularity_condition(self) -> float:
        """det(N_neuro) → 0 means the player cannot form intent.
        
        This happens when:
        - Focus is depleted AND skill is low AND arousal is extreme
        - The neural tensor becomes singular
        - The numerator of the vinculum collapses
        """
        return np.linalg.det(self.matrix)


# ═══════════════════════════════════════════════════════
# COMPLETE VINCULUM SIMULATOR
# ═══════════════════════════════════════════════════════

class ForgeSimulator:
    """Complete forging vinculum: N_neuro → A_intent → D_total → A_realized."""
    
    def __init__(self):
        self.neural = NeuralNumerator()
        self.time = 0.0
        self.strikes = 0
        self.successes = 0
    
    def strike(self, raw_will: np.ndarray, D_mat_trace: float, D_bio_matrix: np.ndarray,
               C_strike: np.ndarray = None) -> dict:
        """Execute one forging strike through the complete vinculum.
        
        V(A) = (N_neuro^{-1} · A_raw) / (Tr(D_mat)·I_3 + D_bio + C_strike)
        """
        # Step 1: Neural numerator generates intent
        A_intent = self.neural.generate_intent(raw_will)
        
        # Step 2: Build total denominator
        D_total = (D_mat_trace * np.eye(3) + D_bio_matrix + 
                   (C_strike if C_strike is not None else np.zeros((3,3))))
        
        # Step 3: The vinculum — intent divided by resistance
        try:
            A_realized = np.linalg.inv(D_total) @ A_intent
        except np.linalg.LinAlgError:
            # Biomechanical singularity — catastrophic failure
            return {
                "A_intent": A_intent.tolist(),
                "A_realized": [0, 0, 0],
                "success": False,
                "failure_mode": "SINGULARITY",
                "det_D_total": 0.0,
                "det_N_neuro": self.neural.singularity_condition(),
                "blade_shattered": True,
                "rotator_cuff_torn": True,
            }
        
        # Step 4: Evaluate success
        precision_error = np.linalg.norm(A_intent - A_realized)
        success = precision_error < 0.3 and all(A_realized > 0)
        
        # Step 5: Update neural state (learning)
        dt = 2.0  # ~2 seconds per strike
        self.neural.update(dt, success)
        self.time += dt
        self.strikes += 1
        if success:
            self.successes += 1
        
        return {
            "strike": self.strikes,
            "A_intent": A_intent.tolist(),
            "A_realized": A_realized.tolist(),
            "precision_error": float(precision_error),
            "success": success,
            "N_neuro_det": float(self.neural.singularity_condition()),
            "D_total_det": float(np.linalg.det(D_total)),
            "focus": self.neural.focus_pool,
            "skill": self.neural.skill_level,
            "complete_vinculum": True,
        }


# ═══════════════════════════════════════════════════════
# DEMO — Run the complete vinculum
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════╗")
    print("║  COMPLETE VINCULUM SIMULATOR                 ║")
    print("║  N_neuro / (D_mat ⊗ D_bio) = A_realized     ║")
    print("╚══════════════════════════════════════════════╝")
    print()
    
    sim = ForgeSimulator()
    
    # Scenario: Post-famine, residual fatigue, poorly balanced hammer
    D_mat_trace = 1.8  # Blade has micro-fractures — high resistance
    D_bio = np.array([
        [2.1, 0.4, 0.3],   # D_gg=2.1 (starving), couplings active
        [0.4, 1.6, 0.5],   # D_ll=1.6 (acidotic tremor)
        [0.3, 0.5, 2.2],   # D_ii=2.2 (top-heavy hammer precession)
    ])
    C_strike = np.array([
        [0, 0, 0.45 * 2.2],  # ξ·D_ii
        [0, 0, 0.22 * 1.6],  # ψ·D_ll
        [0.45 * 2.2, 0.22 * 1.6, 0],
    ])
    
    print("SCENARIO: Starving (G=600kJ), acidotic ([La]=0.008), top-heavy hammer")
    print(f"  D_mat trace = {D_mat_trace}")
    print(f"  D_bio = diagonal [{D_bio[0,0]:.1f}, {D_bio[1,1]:.1f}, {D_bio[2,2]:.1f}]")
    print()
    
    # Simulate 10 strikes
    for i in range(10):
        # Raw will: deliberate strike [force, velocity, precision]
        raw = np.array([1.0, 1.0, 1.0])  # Full intent
        
        result = sim.strike(raw, D_mat_trace, D_bio, C_strike)
        
        status = "✓ HIT" if result['success'] else "✗ MISS"
        if result.get('failure_mode') == 'SINGULARITY':
            status = "☠ SINGULARITY"
        
        print(f"  Strike {result['strike']:2d}: {status} | "
              f"error={result['precision_error']:.3f} | "
              f"focus={result['focus']:.0f} | "
              f"skill={result['skill']:.3f} | "
              f"det(N)={result['N_neuro_det']:.3f}")
    
    print()
    print(f"  Results: {sim.successes}/{sim.strikes} successful")
    print()
    print("THE COMPLETE VINCULUM:")
    print("  N_neuro⁻¹(will)         ← neural numerator (what player wants)")
    print("  ─────────────────────   ← vinculum (divides intent by resistance)")
    print("  D_mat ⊗ D_bio + C       ← biomechanical denominator (what world demands)")
    print("  = A_realized            ← what actually happens")
    print()
    print("When det(D_total) ≈ 0: blade shatters, rotator cuff tears.")
    print("When det(N_neuro) ≈ 0: player blanks out, cannot form intent.")
    print("When both ≈ 0: the forge becomes a medical emergency.")
