import json
from pathlib import Path
import random

# Seed pools for badging and signage variations
fonts = ["Consolas", "Impact", "Futura Bold", "Roboto Mono", "Helvetica Neue", "Microgramma", "Eurostile Bold"]
materials = ["Brushed Titanium", "Polished Chrome", "Matte Carbon Fiber", "Raw Cast Iron", "Anodized Gold", "Bismuth Crystal", "Obsidian"]
decals = ["Amber Emissive Inlay", "Laser Engraved Etching", "Frosted Glass Edge-glow", "Stenciled White Enamel", "Liquid Copper Spill"]
textures = ["Carbon Fiber weave", "Hammered Steel", "Sandblasted Aluminum", "Machined Swirls", "Matte Oxide"]
texts = ["TRENCH", "VINCULUM", "CONVEYOR", "VANGUARD", "GHOST BRAID", "PANGEA", "OBELISK"]

variants = []
for i in range(20):
    text = random.choice(texts)
    font = random.choice(fonts)
    mat = random.choice(materials)
    decal = random.choice(decals)
    tex = random.choice(textures)
    
    score = (
        len(text) * 0.1 + 
        (0.5 if "Mono" in font or "Consolas" in font else 0.2) +
        (0.8 if "Iron" in mat or "Titanium" in mat else 0.4) +
        (0.9 if "Emissive" in decal or "Edge-glow" in decal else 0.3)
    )
    
    variants.append({
        "id": i + 1,
        "text": text,
        "font": font,
        "badge_material": mat,
        "decal_style": decal,
        "substrate_texture": tex,
        "eval_score": round(score, 2)
    })

# Sort by evaluated score descending
variants.sort(key=lambda x: x["eval_score"], reverse=True)

output = {
    "run_count": 20,
    "variants": variants,
    "best_variant": variants[0]
}

out_path = Path("C:/Users/dasha/.gemini/antigravity-ide/scratch/trench-builder/badging_iterations_20x.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"Generated 20 badging configurations. Best variant ID: {variants[0]['id']}")
print(f"Details: {variants[0]}")
