#!/usr/bin/env python
"""FRACTYPE v6 — Overline Mode. Every vinculum afterlife as a typed diacritic macro."""

# Modes
MODES = {
    "overline":   {"glyph": chr(9472), "meaning": "GROUPING", "origin": "Al-Hassar 12thC"},
    "radical":    {"glyph": chr(9472), "meaning": "ROOT", "origin": "Rudolff 1525"},
    "repeat":     {"glyph": chr(9472), "meaning": "INFINITE", "origin": "Marsh 18thC"},
    "conjugate":  {"glyph": chr(9472), "meaning": "MIRROR", "origin": "Modern"},
    "complement": {"glyph": chr(9472), "meaning": "OUTSIDE", "origin": "Modern"},
    "negation":   {"glyph": chr(9472), "meaning": "CORRECT", "origin": "Modern"},
    "amplify":    {"glyph": chr(9472), "meaning": "MULTIPLY", "origin": "Roman"},
    "fraction":   {"glyph": chr(9472), "meaning": "DIVIDE", "origin": "Al-Hassar 12thC"},
}

COMBINING = chr(773)

class Vinculum:
    def __init__(self, content, mode="overline"):
        self.content = content
        self.mode = mode
        self.spec = MODES.get(mode, MODES["overline"])
    
    def render_overline(self, width=60):
        bar = self.spec["glyph"] * (len(self.content)+4)
        return f"  {bar}\n  {self.content}  [{self.spec['meaning']}]"

    def render_inline(self):
        out = ""
        for i, ch in enumerate(self.content):
            out += ch + COMBINING if i==len(self.content)-1 and self.mode in ["repeat","negation"] else ch
        return f"{out} [{self.spec['meaning']}]" if self.mode in ["repeat","negation","conjugate","complement"] else out

    def render_fraction(self, den=""):
        if not den: return self.render_overline()
        w = max(len(self.content), len(den))+4
        bar = self.spec["glyph"]*w
        return f"  {self.content}\n  {bar}  [{self.spec['meaning']}]\n  {den}"

    def render_roman(self):
        box = "|" + self.content + COMBINING + "|"
        return f"{box} = {self.content} x 1,000 [{self.spec['meaning']}]"

    def __str__(self):
        if self.mode == "fraction": return self.render_fraction()
        if self.mode == "amplify": return self.render_roman()
        if self.mode in ["negation","repeat","conjugate","complement"]: return self.render_inline()
        return self.render_overline()

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
