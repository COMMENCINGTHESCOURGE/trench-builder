import os
import re
from pathlib import Path

# Paths to scan
base_dir = Path("C:/Users/dasha/.gemini/antigravity-ide/scratch/trench-builder")

# Targets to upgrade
targets = [
    "BACKROOMS_MEP.html",
    "CAD_VIEWER.html",
    "CINEMATOGRAPHY_ENGINE.html",
    "FACIAL_CITY_GRID.html",
    "HYPERPOLY_v5.html",
    "KIRAGAMI_MECH.html",
    "MANIFESTATION_BRIDGE.html",
    "MECHA_VINCULUM.html",
    "NOVA_HORIZON_3D.html",
    "nova_horizon_subwoofer.html"
]

def upgrade_scene(filepath: Path):
    if not filepath.exists():
        print(f"Skipping: {filepath.name} (does not exist)")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    modified = False

    # 1. Swap MeshStandardMaterial for MeshPhysicalMaterial
    if "MeshStandardMaterial" in content:
        content = content.replace("MeshStandardMaterial", "MeshPhysicalMaterial")
        modified = True
        print(f"Upgraded {filepath.name}: MeshStandardMaterial -> MeshPhysicalMaterial")

        # 2. Inject parameters inside material configuration blocks
        # Pattern to look for materials definition: new THREE.MeshPhysicalMaterial({ ... })
        # We'll inject: clearcoat: 1.0, clearcoatRoughness: 0.1, transmission: 0.3, thickness: 0.5
        param_pattern = r"(new\s+THREE\.MeshPhysicalMaterial\s*\(\s*\{)([^}]*)(\}\s*\))"
        
        def inject_params(match):
            prefix = match.group(1)
            body = match.group(2)
            suffix = match.group(3)
            
            # Check if fields are already defined
            injections = []
            if "clearcoat" not in body:
                injections.append("clearcoat: 1.0")
            if "clearcoatRoughness" not in body:
                injections.append("clearcoatRoughness: 0.1")
            if "transmission" not in body:
                injections.append("transmission: 0.3")
            if "thickness" not in body:
                injections.append("thickness: 0.5")
                
            if injections:
                separator = ",\n        "
                injected_body = body.rstrip()
                if injected_body and not injected_body.endswith(","):
                    injected_body += ","
                injected_body += "\n        " + separator.join(injections) + "\n    "
                return f"{prefix}{injected_body}{suffix}"
            return match.group(0)

        content, count = re.subn(param_pattern, inject_params, content, flags=re.DOTALL)
        if count > 0:
            print(f"Injected MeshPhysical properties into {count} instances inside {filepath.name}")

    # 3. Inject Rim Light if missing
    light_check = ["rimLight", "rim_light", "backLight", "back_light"]
    if not any(lc in content for lc in light_check):
        # Find where lights are usually added, e.g., scene.add( ... )
        # Or look for directionalLight, ambientLight definitions
        light_pattern = r"(scene\.add\s*\(\s*\w+\s*\);)"
        rim_light_js = """
        // Programmatic Rim Light Addition (Hyperrealism Baseline)
        const rimLight = new THREE.DirectionalLight(0xffffff, 1.5);
        rimLight.position.set(-5, 5, -5); // Position behind the subject
        scene.add(rimLight);
        """
        
        # Insert rim light before the first scene addition if found
        match = re.search(light_pattern, content)
        if match:
            pos = match.start()
            content = content[:pos] + rim_light_js + "\n        " + content[pos:]
            modified = True
            print(f"Injected programmatic Rim Light into {filepath.name}")

    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    
    return False

if __name__ == "__main__":
    upgraded_count = 0
    for target in targets:
        full_path = base_dir / target
        if upgrade_scene(full_path):
            upgraded_count += 1
            
    print(f"\nCompleted pipeline run. Upgraded {upgraded_count} scene files.")
