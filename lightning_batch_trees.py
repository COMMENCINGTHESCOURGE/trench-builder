import lightning as L
import os
import argparse

def run_batch_generation(machine_type):
    # 1. Initialize the Lightning Studio connection
    print(f"Starting Lightning Studio (Machine: {machine_type})...")
    studio = L.Studio(name="ghost-braid-forge", machine=machine_type)
    studio.start()

    print("Studio started. Installing Headless Blender...")
    # 2. Install Blender on the remote Linux machine
    studio.run("sudo apt update && sudo apt install -y blender")

    # 3. Push our local pipeline and specs to the remote Studio
    print("Uploading pipeline and specs...")
    pipeline_path = "C:/Users/dasha/.gemini/antigravity-ide/scratch/trench-builder/high_fidelity_tree_pipeline.py"
    specs_dir = "C:/Users/dasha/.gemini/antigravity-ide/scratch/trench-builder/specs"
    
    studio.upload_file(pipeline_path, "/home/zeus/pipeline.py")
    
    # Zip the specs folder to transfer efficiently
    print("Compressing local specs...")
    os.system(f"tar -czvf specs.tar.gz -C {specs_dir} environment")
    
    studio.upload_file("specs.tar.gz", "/home/zeus/specs.tar.gz")
    studio.run("tar -xzvf /home/zeus/specs.tar.gz -C /home/zeus/")
    studio.run("mkdir -p /home/zeus/exports")

    # 4. Execute the Batch Generation
    print("Executing high-fidelity generation parallelized across CPU cores...")
    run_command = """
    find /home/zeus/environment -name '*.json' | xargs -n 1 -P 16 -I {} sh -c '
      export_name=$(basename {} .json)_hf.glb
      blender --background --python /home/zeus/pipeline.py -- --config {} --out /home/zeus/exports/$export_name
    '
    """
    studio.run(run_command)

    # 5. Pull the GLB assets back to your local machine
    print("Downloading finished assets...")
    out_dir = "C:/Users/dasha/.gemini/antigravity-ide/scratch/trench-builder/lightning_exports"
    os.makedirs(out_dir, exist_ok=True)
    studio.download_directory("/home/zeus/exports", out_dir)

    # 6. STOP THE STUDIO (Crucial to only pay for the execution time)
    print("Shutting down Studio to conserve credits.")
    studio.stop()
    print("Ghost Braid batch generation complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lightning AI Ghost Braid Pipeline")
    parser.add_argument("--machine", default="L4", help="Machine type (e.g., L4, A10G, A100)")
    args = parser.parse_args()
    
    run_batch_generation(args.machine)
