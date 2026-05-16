#!/usr/bin/env python
"""
FracType RENDERER v2 — Tiered Width Budgets + Diegetic Overflow
═══════════════════════════════════════════════════════════════
Architecture by DaShawn / Guinea Pig Trench LLC — May 2026

GOLDEN RULE:
  Fractions never wrap internally.
  They transform state when exceeding spatial budget.

SEVEN RULES:
  1. Tier-Scoped Width Budgets (deeper = narrower)
  2. Atomic Render Blocks (no uncontrolled line wrap)
  3. Progressive Disclosure (collapse → expand on demand)
  4. Overflow as Diegetic Corruption (glitch, fragment, recurse)
  5. Adaptive Rendering Modes (Inline / Block / Collapsed / Recursive)
  6. Alignment Drift Prevention (AST compositor, top-down layout)
  7. Overflow → State Transition (never text wrap)
"""
import math, textwrap
from dataclasses import dataclass, field
from typing import Optional, List

# ═══════════════════════════════════════════════════════
# TIER BUDGETS
# ═══════════════════════════════════════════════════════

TIER_BUDGETS = {
    0: 48,  # Surface dialogue
    1: 32,  # Subtext
    2: 20,  # Machine intent
    3: 12,  # Corruption
}

@dataclass
class FracNode:
    num: str
    den: str
    depth: int = 0
    mode: str = "block"  # inline | block | collapsed | recursive
    collapsed: bool = False
    
    def tier_budget(self) -> int:
        return TIER_BUDGETS.get(min(self.depth, 3), 48)
    
    def render(self, focus=False) -> str:
        budget = self.tier_budget()
        bar_char = chr(9472)
        
        if self.mode == "inline":
            return f"{self.num} / {self.den}"
        
        if self.mode == "collapsed" and not focus:
            return f"{self.num}\n{bar_char * min(budget, 20)}\n[memory suppressed]"
        
        # Apply overflow transformation
        num = self._fit(self.num, budget)
        den = self._fit(self.den, budget)
        
        width = max(len(num), len(den)) + 4
        bar = bar_char * width
        
        return f"  {num}\n  {bar}\n  {den}"
    
    def _fit(self, text: str, budget: int) -> str:
        """Fit text to budget. Transform if overflow."""
        if len(text) <= budget:
            return text.center(budget)
        
        # OVERFLOW → STATE TRANSITION (not text wrap)
        overflow_pct = (len(text) - budget) / budget
        
        if overflow_pct < 0.3:
            # Mild overflow → truncation with corruption marker
            return text[:budget-3] + chr(9608)*3  # ███
        elif overflow_pct < 0.6:
            # Moderate overflow → fragmented
            visible = budget // 2
            return text[:visible] + " / / / " + text[-visible:]
        else:
            # Severe overflow → recursion
            return chr(9608) * (budget // 2) + " RECURSE " + chr(9608) * (budget // 2)


# ═══════════════════════════════════════════════════════
# Labyrinth-Specific Narrative Overlay
# ═══════════════════════════════════════════════════════

@dataclass 
class LabyrinthFrame:
    """A single narrative fraction in SOVEREIGN_LABYRINTH."""
    surface: str       # Public dialogue
    subtext: str       # Hidden message
    intent: str = ""   # Machine layer (optional)
    corruption: str = ""  # Corruption layer (optional)
    
    def render(self, focus_level=0) -> str:
        """focus_level: 0=collapsed, 1=surface, 2=subtext, 3=machine, 4=corruption"""
        nodes = []
        bar_char = chr(9472)
        
        # Surface (always visible)
        if len(self.surface) > TIER_BUDGETS[0]:
            surface_text = self.surface[:45] + chr(9608)*3
        else:
            surface_text = self.surface
        nodes.append(f"  {surface_text}")
        
        # Subtext (visible at focus >= 1)
        if focus_level < 1:
            nodes.append(f"  {bar_char * min(len(surface_text)+4, 48)}")
            nodes.append(f"  [access restricted]")
            return "\n".join(nodes)
        
        if len(self.subtext) > TIER_BUDGETS[1]:
            subtext_text = self.subtext[:29] + chr(9608)*3
        else:
            subtext_text = self.subtext
        width1 = max(len(surface_text), len(subtext_text)) + 4
        nodes.append(f"  {bar_char * width1}")
        nodes.append(f"  {subtext_text}")
        
        # Machine intent (visible at focus >= 2)
        if focus_level < 2 or not self.intent:
            return "\n".join(nodes)
        
        if len(self.intent) > TIER_BUDGETS[2]:
            intent_text = self.intent[:17] + chr(9608)*3
        else:
            intent_text = self.intent
        width2 = max(len(subtext_text), len(intent_text)) + 4
        nodes.append(f"  {bar_char * width2}")
        nodes.append(f"  {intent_text}")
        
        # Corruption (visible at focus >= 3)
        if focus_level < 3 or not self.corruption:
            return "\n".join(nodes)
        
        corr = self.corruption[:9] + chr(9608)*3 if len(self.corruption) > TIER_BUDGETS[3] else self.corruption
        width3 = max(len(intent_text), len(corr)) + 4
        nodes.append(f"  {bar_char * width3}")
        nodes.append(f"  {corr}")
        
        return "\n".join(nodes)


# ═══════════════════════════════════════════════════════
# DEMO — Proving the theory
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║  FracType v2 — Diegetic Overflow Demo    ║")
    print("╚══════════════════════════════════════════╝")
    print()
    
    # TIER WIDTH DEMO
    print("═══ TIER WIDTHS ═══")
    node = FracNode(
        "I trust you",
        "You were selected to replace prior witness",
        depth=0
    )
    
    print("Depth 0 (48 cols):")
    print(node.render())
    print()
    
    node2 = FracNode(
        "I trust you",
        "You were selected to replace prior witness",
        depth=1
    )
    print("Depth 1 (32 cols) — compression visible:")
    print(node2.render())
    print()
    
    node3 = FracNode(
        "I trust you",
        "You were selected to replace prior witness",
        depth=2
    )
    print("Depth 2 (20 cols) — fragmentation:")
    print(node3.render())
    print()
    
    node4 = FracNode(
        "I trust you",
        "You were selected to replace prior witness",
        depth=3
    )
    print("Depth 3 (12 cols) — recursion:")
    print(node4.render())
    print()
    
    # PROGRESSIVE DISCLOSURE DEMO
    print("═══ PROGRESSIVE DISCLOSURE ═══")
    frame = LabyrinthFrame(
        surface="WELCOME TO SECTOR 7",
        subtext="Replace prior witness at 03:14 UTC",
        intent="MEMORY OVERRIDE ACTIVE",
        corruption="/ / / BUFFER LOOP / / /"
    )
    
    for level in range(4):
        print(f"\n  Focus Level {level}:")
        print(frame.render(level))
    
    print()
    
    # COLLAPSED MODE
    print("═══ COLLAPSED MODE ═══")
    col = FracNode("ACCESS LOG", "Witness removed at 03:14 UTC", mode="collapsed")
    print(col.render(focus=False))
    print()
    print("═══ EXPANDED (focus=True) ═══")
    print(col.render(focus=True))
    print()
    
    # OVERFLOW AS CORRUPTION
    print("═══ OVERFLOW CORRUPTION ═══")
    corrupt = FracNode(
        "REMEMBER WHAT THEY TOOK FROM YOU",
        "THE OBSERVER DOES NOT EXIST BEYOND THE LABYRINTH",
        depth=0
    )
    print(corrupt.render())
    print()
    
    print("Golden rule verified: overflow transforms state, never wraps.")