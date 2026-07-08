"""
Trench-Builder: Blender Market Automated Publisher & Uploader
Compiles 3D models headlessly using Blender and publishes the compiled 
assets/bundles directly to the Blender Market API.

Environment Variables:
  BLENDER_MARKET_API_TOKEN: API token for Blender Market authentication.
  BLENDER_MARKET_API_URL: Target endpoint (defaults to production).
"""

import sys
import os
import json
import urllib.request
import urllib.error
import mimetypes
from pathlib import Path

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def export_mesh_to_glb(output_path):
    import bpy
    print("Initiating Headless Blender Asset Compilation...")
    
    generator_script = os.path.join(os.path.dirname(__file__), "specter_drone_blender.py")
    if not os.path.exists(generator_script):
        generator_script = "specter_drone_blender.py"

    print(f"Executing Asset Generator: {generator_script}")
    with open(generator_script, 'r', encoding='utf-8') as f:
        exec(f.read(), globals())

    # Export to GLB format
    print(f"Exporting compiled mesh to: {output_path}")
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        use_selection=False
    )
    print("Export Complete.")


def upload_to_blender_market(file_path, metadata):
    """Publishes a product file to Blender Market via REST API."""
    token = os.environ.get("BLENDER_MARKET_API_TOKEN")
    api_url = os.environ.get("BLENDER_MARKET_API_URL", "https://blendermarket.com/api/v1/products")

    if not token:
        print("\n[WARNING] BLENDER_MARKET_API_TOKEN not set in environment.")
        print("To enable automated publishing, please configure the token.")
        print("Skipping Blender Market remote API upload step (local build saved).\n")
        return False

    print(f"Connecting to Blender Market API: {api_url}")
    file_path = Path(file_path)
    
    # Construct multipart form body
    boundary = "----WebKitFormBoundaryTrenchBuilderUploader"
    body = []
    
    # Add metadata fields
    for key, val in metadata.items():
        body.append(f"--{boundary}".encode('utf-8'))
        body.append(f'Content-Disposition: form-data; name="{key}"'.encode('utf-8'))
        body.append(b'')
        body.append(str(val).encode('utf-8'))
        
    # Add file field
    mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    body.append(f"--{boundary}".encode('utf-8'))
    body.append(f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"'.encode('utf-8'))
    body.append(f'Content-Type: {mime_type}'.encode('utf-8'))
    body.append(b'')
    with open(file_path, "rb") as f:
        body.append(f.read())
        
    body.append(f"--{boundary}--".encode('utf-8'))
    
    req_body = b"\r\n".join(body)
    
    # Build request
    req = urllib.request.Request(
        api_url,
        data=req_body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(req_body))
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print(f"[SUCCESS] Product published successfully! Product ID: {res_data.get('id', 'N/A')}")
            return True
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8')
        print(f"[ERROR] API Upload failed with status {e.code}: {err_msg}")
        return False
    except Exception as e:
        print(f"[ERROR] Connection to Blender Market failed: {e}")
        return False


if __name__ == "__main__":
    out_dir = os.path.dirname(__file__)
    target_path = os.path.join(out_dir, "specter_drone.glb")
    
    # 1. Compile model headlessly
    try:
        import bpy
        export_mesh_to_glb(target_path)
    except ImportError:
        print("[NOTE] bpy (Blender Python API) not available in this environment. Skipping headless compilation.")
    
    # 2. Run upload if file exists
    if os.path.exists(target_path):
        product_meta = {
            "name": "Specter Drone Assembly",
            "description": "Constraint-validated tactical robot drone.",
            "price": "25.00",
            "tags": "robot,mecha,lowpoly,game-ready"
        }
        upload_to_blender_market(target_path, product_meta)
