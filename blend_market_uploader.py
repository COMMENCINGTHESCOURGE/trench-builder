import sys
import os
import bpy

def export_mesh_to_glb(output_path):
    print("Initiating Headless Blender Asset Compilation...")
    
    # Path to the generator script
    generator_script = os.path.join(os.path.dirname(__file__), "specter_drone_blender.py")
    if not os.path.exists(generator_script):
        # Fallback to current working directory
        generator_script = "specter_drone_blender.py"

    print(f"Executing Asset Generator: {generator_script}")
    with open(generator_script, 'r') as f:
        exec(f.read(), globals())

    # Export to GLB format
    print(f"Exporting compiled mesh to: {output_path}")
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        use_selection=False
    )
    print("Export Complete.")

if __name__ == "__main__":
    out_dir = os.path.dirname(__file__)
    target_path = os.path.join(out_dir, "specter_drone.glb")
    export_mesh_to_glb(target_path)
