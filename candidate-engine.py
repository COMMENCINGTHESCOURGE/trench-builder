#!/usr/bin/env python3
"""
CANDIDATE ENGINE — Combinatorial transformation candidate generator.

Inspired by the AlphaZero-in-name-only ALPHA_RESONANCE.py (3 hardcoded candidates).
Uses the Part Affordance RULE pattern: conditions + confidence functions.

Each candidate is defined as a dict with:
  - conditions: list of callables that check if this candidate applies
  - confidence: callable that returns 0.0-1.0 score
  - category: for deduplication

Usage:
    python candidate-engine.py                        # run demo
    python candidate-engine.py --input grid.json      # transform grid
"""

import sys
import json
import math
import itertools
from typing import List, Dict, Callable, Tuple, Any


# ── Rule-based Candidate Registry ──
# Each candidate: {conditions: [fn], confidence: fn, category: str, fn: actual_transform}

CANDIDATES = []

def candidate(category: str, conditions: List[Callable], confidence_fn: Callable, transform_fn: Callable):
    """Register a transformation candidate."""
    CANDIDATES.append({
        "category": category,
        "conditions": conditions,
        "confidence": confidence_fn,
        "transform": transform_fn,
    })


def register_builtins():
    """Register the default set of transformation candidates."""

    # ── Translation ──
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)]:
        candidate(
            category="translation",
            conditions=[
                lambda g, dx=dx, dy=dy: True,  # translation always possible
            ],
            confidence_fn=lambda g, dx=dx, dy=dy: 0.6 + 0.1 * (abs(dx) == abs(dy)),
            transform_fn=lambda g, dx=dx, dy=dy: translate_grid(g, dx, dy),
        )

    # ── Rotation ──
    for angle in [90, 180, 270]:
        candidate(
            category="rotation",
            conditions=[
                lambda g, a=angle: max(g.shape) == min(g.shape),  # square only
            ],
            confidence_fn=lambda g, a=angle: 0.7 if a == 180 else 0.5,
            transform_fn=lambda g, a=angle: rotate_grid(g, a),
        )

    # ── Reflection ──
    for axis in ["h", "v"]:
        candidate(
            category="reflection",
            conditions=[lambda g: True],
            confidence_fn=lambda g, ax=axis: 0.6,
            transform_fn=lambda g, ax=axis: reflect_grid(g, ax),
        )

    # ── Color Inversion ──
    candidate(
        category="color",
        conditions=[
            lambda g: len(set(g.flatten().tolist())) > 1,  # >1 color present
        ],
        confidence_fn=lambda g: 0.4 + 0.1 * (len(set(g.flatten().tolist())) > 3),
        transform_fn=invert_colors,
    )

    # ── Fractal Expansion (the one from ALPHA_RESONANCE that was hardcoded to 1.34) ──
    candidate(
        category="fractal",
        conditions=[
            lambda g: min(g.shape) > 2,
            lambda g: max(g.shape) <= 30,
        ],
        confidence_fn=lambda g: 0.3 + 0.15 * (g.size > 100),
        transform_fn=fractal_expand,
    )


# ── Transform Implementations ──

def translate_grid(grid, dx, dy):
    import numpy as np
    h, w = grid.shape
    out = np.zeros_like(grid)
    src_y0, src_x0 = max(0, -dy), max(0, -dx)
    dst_y0, dst_x0 = max(0, dy), max(0, dx)
    src_y1, src_x1 = h + min(0, -dy), w + min(0, -dx)
    dst_y1, dst_x1 = h + min(0, dy), w + min(0, dx)
    out[dst_y0:dst_y1, dst_x0:dst_x1] = grid[src_y0:src_y1, src_x0:src_x1]
    return out


def rotate_grid(grid, angle):
    import numpy as np
    k = angle // 90
    return np.rot90(grid, k=k)


def reflect_grid(grid, axis):
    import numpy as np
    if axis == "h":
        return np.fliplr(grid)
    return np.flipud(grid)


def invert_colors(grid):
    import numpy as np
    unique = sorted(set(grid.flatten().tolist()))
    if 0 in unique:
        unique.remove(0)
    mapping = {c: unique[-(i+1)] for i, c in enumerate(unique)}
    out = grid.copy()
    for k, v in mapping.items():
        out[grid == k] = v
    return out


def fractal_expand(grid):
    """Recursive subdivision pattern: each pixel becomes a 2x2 block."""
    import numpy as np
    h, w = grid.shape
    out = np.zeros((h * 2, w * 2), dtype=grid.dtype)
    for y in range(h):
        for x in range(w):
            val = grid[y, x]
            out[2*y:2*y+2, 2*x:2*x+2] = val
    return out


# ── Engine ──

class CandidateEngine:
    """Evaluates all registered candidates against an input and returns ranked results."""

    def __init__(self):
        if not CANDIDATES:
            register_builtins()

    def evaluate(self, input_data: Any, top_k: int = 10) -> List[dict]:
        """
        Run all candidates against input_data.
        Returns list of {category, confidence, transform} sorted by confidence descending.
        """
        results = []
        seen_categories = set()

        for cand in CANDIDATES:
            cat = cand["category"]
            if all(cond(input_data) for cond in cand["conditions"]):
                conf = cand["confidence"](input_data)
                if conf > 0.3 and cat not in seen_categories:
                    results.append({
                        "category": cat,
                        "confidence": round(conf, 3),
                        "transform": cand["transform"],
                    })
                    seen_categories.add(cat)

        # Keep highest per category, sort by confidence
        best_by_cat = {}
        for r in results:
            cat = r["category"]
            if cat not in best_by_cat or r["confidence"] > best_by_cat[cat]["confidence"]:
                best_by_cat[cat] = r

        return sorted(best_by_cat.values(), key=lambda x: -x["confidence"])[:top_k]


def main():
    import numpy as np

    print("=== CANDIDATE ENGINE DEMO ===\n")

    # Test with a 5x5 grid
    test_grid = np.array([
        [0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 2, 2],
        [0, 0, 0, 2, 0],
    ])

    print(f"Input grid:\n{test_grid}\n")

    engine = CandidateEngine()
    results = engine.evaluate(test_grid, top_k=5)

    print(f"Top {len(results)} candidates:")
    for r in results:
        print(f"  [{r['confidence']:.2f}] {r['category']}")
        result_grid = r["transform"](test_grid)
        print(f"    Result:\n{result_grid}\n")

    print("=== DONE ===")


if __name__ == "__main__":
    # Only import numpy at runtime (optional dep)
    main()
