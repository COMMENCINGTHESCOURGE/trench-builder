"""Quick syntax + import check for mechanical_rig_pipeline.py"""
import sys
sys.path.insert(0, r"C:\Users\dasha\trench-builder")

# Just verify the file parses
with open(r"C:\Users\dasha\trench-builder\mechanical_rig_pipeline.py") as f:
    source = f.read()
compile(source, "mechanical_rig_pipeline.py", "exec")

print("SYNTAX: OK")

# Check STL file count
from pathlib import Path
cad_dir = Path(r"C:\Users\dasha\trench-builder\cad_imports")
stls = list(cad_dir.glob("*.stl"))
print(f"STL FILES: {len(stls)}")
for s in sorted(stls)[:5]:
    size_mb = s.stat().st_size / (1024*1024)
    print(f"  {s.name} ({size_mb:.1f} MB)")
if len(stls) > 5:
    print(f"  ... and {len(stls)-5} more")
