#!/usr/bin/env python3
"""Build updated Kaggle notebook with GitHub fallback for input data."""
import json

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Read local scithary_genrator.py
with open(BASE_DIR / 'scithary_genrator.py') as f:
    script = f.read()

# Modifications for Kaggle environment:
# 1. Add urllib import
old_imports = "import json\nimport math\nimport os\nfrom datetime import date\nfrom pathlib import Path\nfrom collections import defaultdict\nfrom typing import Dict, List, Tuple\n\nBASE_DIR = Path(__file__).parent"
new_imports = "import json\nimport math\nimport os\nimport urllib.request\nfrom datetime import date\nfrom pathlib import Path\nfrom collections import defaultdict\nfrom typing import Dict, List, Tuple\n\ntry:\n    BASE_DIR = Path(__file__).parent\nexcept NameError:\n    BASE_DIR = Path.cwd()"
script = script.replace(old_imports, new_imports, 1)

# 2. Modify load_vinculum_scan with fallback
old_load_v = '''def load_vinculum_scan() -> dict:
    with open(BASE_DIR / \"vinculum_scan.json\") as f:
        return json.load(f)'''
new_load_v = '''GITHUB_RAW = "https://raw.githubusercontent.com/COMMENCINGTHESCOURGE/trench-builder/master"

def _load_or_fetch(filename: str, url_path: str = None) -> dict:
    local = BASE_DIR / filename
    if local.exists():
        with open(local) as f:
            return json.load(f)
    url = url_path or f"{GITHUB_RAW}/{filename}"
    print(f"  Downloading {url}...")
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode())

def load_vinculum_scan() -> dict:
    return _load_or_fetch("vinculum_scan.json")'''
script = script.replace(old_load_v, new_load_v, 1)

# 3. Modify load_bonds with fallback
old_load_b = '''def load_bonds() -> dict:
    bonds = {}
    bonds_dir = BASE_DIR / \"bonds\"
    if bonds_dir.exists():
        for bond_file in bonds_dir.glob(\"*.json\"):
            with open(bond_file) as f:
                bond_data = json.load(f)
                bonds[bond_file.stem] = bond_data
    return bonds'''
new_load_b = '''def load_bonds() -> dict:
    bonds = {}
    bonds_dir = BASE_DIR / \"bonds\"
    bond_names = [\"erosion\", \"freeze\", \"hydro\", \"storm-cycle\"]
    if bonds_dir.exists():
        for bond_file in bonds_dir.glob(\"*.json\"):
            with open(bond_file) as f:
                bond_data = json.load(f)
                bonds[bond_file.stem] = bond_data
    if not bonds:
        for name in bond_names:
            try:
                url = f"{GITHUB_RAW}/bonds/{name}.json"
                with urllib.request.urlopen(url, timeout=10) as resp:
                    bonds[name] = json.loads(resp.read().decode())
            except Exception as e:
                print(f"  Warning: Could not load bond {name}: {e}")
    return bonds'''
script = script.replace(old_load_b, new_load_b, 1)

# 4. Modify load_mecha with fallback
old_load_m = '''def load_mecha() -> dict:
    path = BASE_DIR / \"mecha_optimization.json\"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}'''
new_load_m = '''def load_mecha() -> dict:
    path = BASE_DIR / \"mecha_optimization.json\"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    try:
        url = f"{GITHUB_RAW}/mecha_optimization.json"
        print(f"  Downloading {url}...")
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  Warning: Could not load mecha data: {e}")
        return {}'''
script = script.replace(old_load_m, new_load_m, 1)

# Build the notebook
nb = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# SCITHARY GENRATOR \u2014 Territory Analysis\n",
                "## Region Overlap \u00b7 Node Integrity \u00b7 Connection Topology \u00b7 Energy Pulse Routing\n",
                "\n",
                "Auto-regenerates territory data from local files or GitHub raw fallback."
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                script
            ],
            "execution_count": None,
            "outputs": []
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.12.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

# Write the notebook
output_path = 'C:/Users/dasha/Projects/trench_builder/kaggle_push/scithary-genrator/scithary-genrator-auto-regenerator.ipynb'
with open(output_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"Notebook written to {output_path}")
print(f"Script size: {len(script)} chars")
