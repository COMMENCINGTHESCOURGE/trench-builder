#!/usr/bin/env python3
"""Pull balance_patch.json from Kaggle kernel output and apply to STACK_CATHEDRAL.html."""
import json, re, sys
from pathlib import Path
import subprocess

GAME_HTML = Path.home() / "Projects/trench_builder/STACK_CATHEDRAL.html"
PATCH_JSON = Path.home() / "Projects/trench_builder/balance_patch.json"

def pull_patch():
    """Download latest balance patch from Kaggle kernel."""
    try:
        subprocess.run([
            "kaggle", "kernels", "output", 
            "commencethescourge/stack-cathedral-balancer",
            "-p", str(Path.home() / "Projects/trench_builder/")
        ], check=True, timeout=30, capture_output=True, text=True)
        if PATCH_JSON.exists():
            return json.loads(PATCH_JSON.read_text())
    except Exception as e:
        print(f"Pull failed: {e}")
    
    # Fallback: use defaults
    return {
        "enemy_hp_mult": {"drift": 1.0, "chain": 1.0, "conflict": 1.0, "paren": 1.0, "bracket": 1.0, "brace": 1.0},
        "weapon_damage": {"apply": 26, "destroy": 90, "plan": 8, "rollback": 999},
        "spawn": {"drones": 25, "chains": 6, "conflicts": 2, "paren_pairs": 8, "bracket_pairs": 6, "brace_pairs": 5},
        "timing": {"wave_spacing": 25, "boss_spawn_wave": 2, "boss_frame_interval": 9},
        "player": {"hp": 100, "shield_regen": 8, "energy_regen": 7, "speed": 45}
    }

def apply_patch(patch):
    """Apply balance patch to game HTML via targeted replacements."""
    html = GAME_HTML.read_text()
    original = html
    
    # Enemy HP
    html = html.replace("hp:38,", f"hp:{int(38*patch['enemy_hp_mult']['drift'])},//drift")
    html = html.replace("hp:120,", f"hp:{int(120*patch['enemy_hp_mult']['chain'])},//chain")
    html = html.replace("hp:350,", f"hp:{int(350*patch['enemy_hp_mult']['conflict'])},//conflict")

    # Weapon damage
    html = html.replace("hit.hp-=26;", f"hit.hp-={patch['weapon_damage']['apply']};")
    html = html.replace("e.hp-=90;", f"e.hp-={patch['weapon_damage']['destroy']};")
    html = html.replace("e.hp-=8;", f"e.hp-={patch['weapon_damage']['plan']};")

    # Spawns
    html = re.sub(r"this\.droneCount=25", f"this.droneCount={patch['spawn']['drones']}", html)
    html = re.sub(r"this\.chainCount=6", f"this.chainCount={patch['spawn']['chains']}", html)
    html = re.sub(r"this\.conflictCount=2", f"this.conflictCount={patch['spawn']['conflicts']}", html)

    # Timing
    if "waveTimer>25" in html:
        html = html.replace("waveTimer>25", f"waveTimer>{patch['timing']['wave_spacing']}")

    if html != original:
        GAME_HTML.write_text(html)
        print("Patch applied successfully")
    else:
        print("No changes needed (already up to date)")

def push_to_git():
    """Commit and push the patched HTML."""
    subprocess.run(["git", "add", "STACK_CATHEDRAL.html"], 
                   cwd=Path.home() / "Projects/trench_builder", check=False)
    subprocess.run(["git", "commit", "-m", "auto-balance patch applied [cron]"], 
                   cwd=Path.home() / "Projects/trench_builder", check=False)
    subprocess.run(["git", "push"], 
                   cwd=Path.home() / "Projects/trench_builder", check=False)

if __name__ == "__main__":
    print("Pulling balance patch from Kaggle...")
    patch = pull_patch()
    apply_patch(patch)
    if "--push" in sys.argv:
        push_to_git()
    print("Done.")
    print(json.dumps(patch, indent=2))
