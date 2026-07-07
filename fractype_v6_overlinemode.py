#!/usr/bin/env python
"""FRACTYPE v6 — Overline Mode. Every vinculum afterlife as a typed diacritic macro."""

import sys
from pathlib import Path

# Anchor to the canonical bridge schema
bridge_path = Path(__file__).parent.parent / "fractype" / "bridge"
sys.path.insert(0, str(bridge_path))

from fractype_schema import FracNode, VinculumRole

# Modes mapping from ad-hoc strings to canonical VinculumRole
MODE_TO_ROLE = {
    "overline":   VinculumRole.GROUPING,
    "radical":    VinculumRole.RADICAL,
    "repeat":     VinculumRole.REPETITION,
    "conjugate":  VinculumRole.CONJUGATE,
    "complement": VinculumRole.COMPLEMENT,
    "negation":   VinculumRole.NEGATION,
    "amplify":    VinculumRole.MULTIPLICATION,
    "fraction":   VinculumRole.DIVISION,
}


class Vinculum:
    def __init__(self, content, mode="overline"):
        self.content = content
        self.mode = mode
        self.role = MODE_TO_ROLE.get(mode, VinculumRole.GROUPING)
        # Binds content using the canonical FracNode
        self.node = FracNode(top=content, bottom="", role=self.role)
    
    def __str__(self):
        # Delegate to the canonical FracNode's terminal lines
        lines = self.node.to_terminal_lines()
        
        # Highlight semantic meaning dynamically from the schema's role
        meaning = self.role.name
        if self.role == VinculumRole.DIVISION:
            meaning = "DIVIDE"
        elif self.role == VinculumRole.MULTIPLICATION:
            meaning = "MULTIPLY"
        elif self.role == VinculumRole.REPETITION:
            meaning = "INFINITE"
        elif self.role == VinculumRole.CONJUGATE:
            meaning = "MIRROR"
        elif self.role == VinculumRole.COMPLEMENT:
            meaning = "OUTSIDE"
        elif self.role == VinculumRole.NEGATION:
            meaning = "CORRECT"
            
        # Format the output block with the semantic annotation tag
        if len(lines) >= 2:
            main_content_idx = 1 if self.role in (VinculumRole.GROUPING, VinculumRole.CONJUGATE, VinculumRole.MULTIPLICATION, VinculumRole.REPETITION, VinculumRole.RADICAL) else 0
            lines[main_content_idx] = f"{lines[main_content_idx]}  [{meaning}]"
            return "\n".join(lines)
        elif len(lines) == 1:
            return f"{lines[0]}  [{meaning}]"
        return "\n".join(lines)


# Demo
if __name__ == "__main__":
    print("FRACTYPE v6 — OVERLINE MODE")
    print("="*50)

    examples = [
        ("KIRAGAMI MECH", "overline"),
        ("suit-resistance", "radical"),
        ("erdos-sieve", "repeat"),
        ("WALK", "conjugate"),
        ("STAGES-NOT-DONE", "complement"),
        ("knee", "negation"),
        ("RUN", "amplify"),
    ]

    for content, mode in examples:
        v = Vinculum(content, mode)
        print(v)
        print()

    # Fraction mode
    print(Vinculum("PILOT INTENT", "fraction"))
    print(Vinculum("SUIT RESISTANCE", "fraction"))
    print()

    print("The vinculum does not compute. It re-contextualizes.")
