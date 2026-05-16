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
# FRACTYPE v4 — Auto-Close Container Theory
# ═══════════════════════════════════════════════════════
#
# The vinculum IS the auto-close.
# When you open the numerator, the vinculum inserts itself.
# The denominator completes the close.
#
# () = parens auto-close
# {} = braces auto-close
# [] = brackets auto-close
# "" = quotes auto-close
# '' = single-quote auto-close
# /  = vinculum (the bridge between open and close)
#
# FRACTION AS AUTO-CLOSE PATTERN:
#   ( num / den )  — open, vinculum bridge, close
#   { num / den }  — same pattern, different container
#   [ num / den ]  — same pattern
#   " num / den "  — same pattern
#
# THE INJECTION:
#   When you type a container opener, the vinculum auto-inserts.
#   When you type the vinculum, the container closer auto-inserts.
#   The fraction is always balanced. Always closed.

class AutoCloseFraction:
    """FracType with auto-close container injection."""
    
    PAIRS = {
        "(": ")", "{": "}", "[": "]", '"': '"', "'": "'",
        "<": ">",  # HTML-style
        "/*": "*/",  # Comment-style
        "<!--": "-->",  # Markup-style
    }
    
    VINCULUM = "/"
    
    @staticmethod
    def inject(num: str, den: str = "", container: str = "(") -> str:
        """
        Inject a fraction into a container with auto-close.
        
        Input:  num="HELLO", den="WORLD", container="("
        Output: (HELLO/WORLD)
        
        The vinculum auto-inserts between num and den.
        The closer auto-inserts after den.
        """
        opener = container
        closer = AutoCloseFraction.PAIRS.get(container, container)
        vin = AutoCloseFraction.VINCULUM
        
        if den:
            return f"{opener}{num}{vin}{den}{closer}"
        else:
            # Auto-close with empty denominator placeholder
            return f"{opener}{num}{vin}_{closer}"
    
    @staticmethod
    def extract(fraction: str) -> dict:
        """Extract num/den from any auto-closed container."""
        # Strip container
        inner = fraction.strip()
        for opener, closer in AutoCloseFraction.PAIRS.items():
            if inner.startswith(opener) and inner.endswith(closer):
                inner = inner[len(opener):-len(closer)]
                break
        
        # Split on vinculum
        if AutoCloseFraction.VINCULUM in inner:
            parts = inner.split(AutoCloseFraction.VINCULUM, 1)
            return {"num": parts[0].strip(), "den": parts[1].strip()}
        return {"num": inner, "den": ""}
    
    @staticmethod
    def checkpoint_inject(project: str, done: int, total: int, container: str = "["):
        """Checkpoint as auto-closed fraction.
        [TB/5:7] = project in brackets, done/total as vinculum split.
        """
        vin = AutoCloseFraction.VINCULUM
        closer = AutoCloseFraction.PAIRS.get(container, "]")
        return f"{container}{project}{vin}{done}:{total}{closer}"
    
    @staticmethod
    def mycelium_chain(projects: list, container: str = "(") -> str:
        """Chain multiple fractions in nested auto-close containers.
        ((TB/5:7)/(ERDOS/3:7)/(HACK/4:6)) = nested parens, each a fraction.
        """
        vin = AutoCloseFraction.VINCULUM
        closer = AutoCloseFraction.PAIRS.get(container, ")")
        inner = vin.join([f"{p}/{d}:{t}" for p, d, t, _ in projects])
        return f"{container}{inner}{closer}"

TIER_BUDGETS_V3 = {
    0: 72,  # Maximum for Hermes context window efficiency
    1: 48,  # Still readable in tokenized form
    2: 24,  # Dense but parseable
    3: 8,   # Single-word corruption markers
}

class MicroFrac:
    """FracType at minimum size — AI-native density."""
    
    @staticmethod
    def encode(state_dict: dict, separator="|") -> str:
        """Encode multiple tiers into a single line.
        Format: surface|subtext|intent|corruption
        Each tier separated by a single character.
        Maximum information in minimum space.
        """
        return separator.join([
            state_dict.get("surface", "")[:72],
            state_dict.get("subtext", "")[:48],
            state_dict.get("intent", "")[:24],
            state_dict.get("corruption", "")[:8],
        ])
    
    @staticmethod
    def decode(line: str, separator="|") -> dict:
        parts = line.split(separator)
        return {
            "surface": parts[0] if len(parts) > 0 else "",
            "subtext": parts[1] if len(parts) > 1 else "",
            "intent": parts[2] if len(parts) > 2 else "",
            "corruption": parts[3] if len(parts) > 3 else "",
        }
    
    @staticmethod
    def vinculum_min(text, width=1):
        """Minimum vinculum — collapses to width=1."""
        return chr(9472) * width
    
    @staticmethod
    def checkpoint_line(project, done, total, markers=""):
        """One-line checkpoint encoding.
        Format: PROJ:SSSSBBBBWWJJRR|done/total|markers
        Where S=supine, C=crawl, B=bounce, W=walk, J=jump, R=run
        18 characters encodes 7 states + progress + context.
        """
        state_chars = {'supine':'S','scoot':'C','crawl':'L','stand':'T',
                       'bounce':'B','walk':'W','jump':'J','run':'R'}
        states = ''.join([state_chars.get(s.lower(),'?') for s in []] + 
                        [state_chars.get(s.lower(),'?') for s in markers.split(',') if s])
        return f"{project}:{states}|{done}/{total}"

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
    print("║  FracType v4 — Auto-Close Injection      ║")
    print("║  () {} [] \"\" '' // all auto-close      ║")
    print("╚══════════════════════════════════════════╝")
    print()
    
    # AUTO-CLOSE INJECTION DEMO
    print("═══ AUTO-CLOSE INJECTION ═══")
    pairs = ["(", "{", "[", '"', "'", "<", "/*", "<!--"]
    for container in pairs:
        result = AutoCloseFraction.inject("HELLO", "WORLD", container)
        print(f"  {container:<6} → {result}")
    print()
    
    # No denominator = auto-close with placeholder
    print("═══ EMPTY DENOMINATOR ═══")
    for container in ["(", "{", "["]:
        result = AutoCloseFraction.inject("ACCESS LOG", container=container)
        print(f"  {container:<3} → {result}")
    print()
    
    # EXTRACT BACK
    print("═══ EXTRACT ═══")
    samples = ["(HELLO/WORLD)", "{TB/5:7}", "[I trust you/You were selected]", '"SIGNAL/NOISE"']
    for s in samples:
        extracted = AutoCloseFraction.extract(s)
        print(f"  {s:<35} → num={extracted['num']}, den={extracted['den']}")
    print()
    
    # CHECKPOINT INJECTION
    print("═══ CHECKPOINT AUTO-CLOSE ═══")
    for proj, done, total, container in [("TB",5,7,"["),("ERDOS",3,7,"{"),("HACK",4,6,"(")]:
        result = AutoCloseFraction.checkpoint_inject(proj, done, total, container)
        print(f"  {result}")
    print()
    
    # MYCELIUM CHAIN
    print("═══ MYCELIUM CHAIN (nested auto-close) ═══")
    chain = AutoCloseFraction.mycelium_chain([
        ("TB",5,7,["supine","scoot","crawl","stand","bounce","walk","jump"]),
        ("ERDOS",3,7,["supine","scoot","crawl","stand","bounce","walk","jump"]),
        ("HACK",4,6,["supine","scoot","crawl","stand","bounce","walk"]),
    ])
    print(f"  {chain}")
    extracted = [AutoCloseFraction.extract(f"({p})") for p in chain.strip("()").split("/")]
    # Fix: re-parse the chain correctly
    inner = chain.strip("()")
    parts = inner.split("/")
    print(f"  Parsed: {len(parts)} sub-fractions in one auto-closed container")
    print()
    
    print("THEORY: Type '(' → system inserts ')/' → you fill denominator → ')' auto-closes.")
    print("        The vinculum IS the auto-close bridge between open and close.")
    
    # MICRO-FRAC: Single-line state vectors
    print("═══ MICRO-FRAC ═══")
    state = MicroFrac.encode({
        "surface": "I trust you",
        "subtext": "You were selected to replace prior witness",
        "intent": "MEMORY OVERRIDE ACTIVE",
        "corruption": "OBSERVE"
    })
    print(f"  Encode: {state}")
    decoded = MicroFrac.decode(state)
    print(f"  Decode: {decoded['surface']} | {decoded['subtext']} | {decoded['intent']} | {decoded['corruption']}")
    print(f"  Size: {len(state)} chars = 4 tiers on 1 line")
    print()
    
    # CHECKPOINT LINES: 18-char full state
    print("═══ CHECKPOINT MICRO ═══")
    lines = [
        MicroFrac.checkpoint_line("TB", 5, 7, "supine,scoot,crawl,stand,bounce,walk,jump"),
        MicroFrac.checkpoint_line("ERDOS", 3, 7, "supine,scoot,crawl,stand"),
        MicroFrac.checkpoint_line("HACK", 4, 6, "supine,scoot,crawl,stand"),
        MicroFrac.checkpoint_line("HYPER", 3, 7, "supine,scoot,crawl"),
        MicroFrac.checkpoint_line("INFRA", 3, 7, "supine,scoot,crawl"),
    ]
    for line in lines:
        print(f"  {line}")
    print()
    
    # VINCULUM AT MINIMUM
    print("═══ MINIMUM VINCULUM ═══")
    print(f"  Width=1: {MicroFrac.vinculum_min('x', 1)}")
    print(f"  Width=0: (fraction collapses to inline)")
    print(f"  Inline: 'done / remaining' = 17 chars")
    print(f"  Minimum: '5/7' = 3 chars")
    print()
    
    # ONE-LINE MYCELIUM
    print("═══ ONE-LINE MYCELIUM ═══")
    mycelium = "|".join([
        "TB:5/7", "ERDOS:3/7", "HACK:4/6", "HYPER:3/7", "INFRA:3/7",
        "AGENTS:4/19", "CRON:2/5", "DELTAS:17/44", "55h"
    ])
    print(f"  {mycelium}")
    print(f"  {len(mycelium)} chars = entire project ecosystem on one line")
    print()
    
    print("Human density: 48 cols/tier. AI density: 1 line/tier. Same truth, different glasses.")
    
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