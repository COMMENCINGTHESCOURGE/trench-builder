import os
import argparse
import tarfile
import time
from lightning_sdk import Studio, Teamspace

# Configure Lightning AI credentials and teamspace
os.environ["LIGHTNING_API_KEY"] = "12777834-ef44-49ec-9c5b-5ade3235c2fa"
os.environ["LIGHTNING_USER_ID"] = "35fc4120-1ea1-42e0-adb4-7bda75e606e9"
os.environ["LIGHTNING_USERNAME"] = "dashawnspacem"
LIGHTNING_TEAMSPACE = "erdos-straus-sieve-project"

MACHINE_MAPPING = {
    "t4": "g4dn.xlarge",
    "t4_small": "g4dn.xlarge",
    "t4-small": "g4dn.xlarge",
    "l4": "g6.4xlarge",
    "l4_medium": "g6.4xlarge",
    "l4-medium": "g6.4xlarge",
    "a100": "p4d.24xlarge",
    "rtxp": "g7e.4xlarge",
    "rtx6000": "g7e.4xlarge",
}

def compress_specs(specs_dir, tar_path):
    print("Compressing local specs using tarfile...")
    env_dir = os.path.join(specs_dir, "environment")
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(env_dir, arcname="environment")

def run_batch_generation(machine_type):
    # Determine the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pipeline_path = os.path.join(script_dir, "high_fidelity_tree_pipeline.py")
    specs_dir = os.path.join(script_dir, "specs")
    tar_path = os.path.join(script_dir, "specs.tar.gz")
    out_dir = os.path.join(script_dir, "lightning_exports")
    
    # Map friendly machine type to AWS slug
    machine_lower = machine_type.lower()
    target_machine = MACHINE_MAPPING.get(machine_lower, machine_type)
    
    print(f"Target Machine Type: {machine_type} -> AWS Slug: {target_machine}")
    ts = Teamspace(name=LIGHTNING_TEAMSPACE, org="dashawnspacem-org")
    studio = Studio(name="ghost-braid-forge", teamspace=ts)
    try:
        # Ensure the studio is running first (required to switch machines)
        if studio.status.value != "Running":
            print(f"Starting studio (initial status: {studio.status.value})...")
            studio.start()
            while studio.status.value != "Running":
                print(f"Waiting for studio to start (current: {studio.status.value})...")
                time.sleep(10)
                
        # Now the studio is Running. Check the machine type.
        current_name = studio.machine.name.lower() if studio.machine else ""
        current_slug = studio.machine.slug.lower() if studio.machine else ""
        machine_name_str = studio.machine.name if studio.machine else "None"
        machine_slug_str = studio.machine.slug if studio.machine else "None"
        print(f"Current studio status: {studio.status.value}, machine: {machine_name_str} ({machine_slug_str})")
        
        # Determine if we are already on the target machine
        is_already_target = False
        if target_machine.lower() in [current_name, current_slug]:
            is_already_target = True
        elif target_machine.lower() == "g6.4xlarge" and current_name == "l4":
            is_already_target = True
        elif target_machine.lower() == "g4dn.xlarge" and current_name == "t4":
            is_already_target = True
            
        if not is_already_target:
            print(f"Machine mismatch. Switching from {machine_name_str} to {target_machine}...")
            print("Calling switch_machine on running studio...")
            studio.switch_machine(target_machine)
            
            print("Stopping studio to apply machine type change...")
            studio.stop()
            while studio.status.value != "Stopped":
                print(f"Waiting for studio to stop (current: {studio.status.value})...")
                time.sleep(10)
                
            print("Starting studio on target machine...")
            studio.start()
            while studio.status.value != "Running":
                print(f"Waiting for studio to start on target (current: {studio.status.value})...")
                time.sleep(10)
            
        # Verify readiness
        print("Waiting for Studio setup to complete...")
        max_retries = 30
        for i in range(max_retries):
            try:
                studio.run("echo 'ready'")
                print("Studio is ready!")
                break
            except Exception as e:
                err_msg = str(e)
                print(f"Studio not ready yet (attempt {i+1}/{max_retries}): {err_msg}")
                time.sleep(10)
        else:
            raise RuntimeError("Studio did not become ready.")
            
        print("Studio started. Installing Headless Blender and required libraries...")
        studio.run("sudo apt update && sudo apt install -y blender libxxf86vm1 libxi6 libxrender1 libxfixes3 libxkbcommon0")
    
        # 3. Push our local pipeline and specs to the remote Studio
        print("Uploading pipeline and specs...")
        studio.upload_file(pipeline_path, "pipeline.py")
        
        # Compress and upload specs
        compress_specs(specs_dir, tar_path)
        studio.upload_file(tar_path, "specs.tar.gz")
        studio.run("tar -xzvf specs.tar.gz")
        studio.run("mkdir -p exports")
    
        # 4. Execute the Batch Generation
        print("Executing high-fidelity generation parallelized across CPU cores on GPU machine...")
        run_command = """
        find environment -name '*.json' | xargs -n 1 -P 16 -I {} sh -c '
          export_name=$(basename {} .json)_hf.glb
          blender --background --python pipeline.py -- --config {} --out exports/$export_name
        '
        """
        studio.run(run_command)

    
        # 5. Pull the GLB assets back to your local machine
        print("Downloading finished assets...")
        os.makedirs(out_dir, exist_ok=True)
        studio.download_folder("exports", out_dir)
        print("Finished downloading assets to:", out_dir)
        
    except Exception as e:
        print(f"An error occurred during generation: {e}")
        raise e
    finally:
        # 6. STOP THE STUDIO (Crucial to only pay for the execution time)
        print("Shutting down Studio to conserve credits.")
        try:
            studio.stop()
            print("Studio shut down successfully.")
        except Exception as e:
            print(f"Warning: Failed to stop studio: {e}")
            
    print("Ghost Braid batch generation complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lightning AI Ghost Braid Pipeline")
    parser.add_argument("--machine", default="L4", help="Machine type (e.g., T4, L4, A100)")
    args = parser.parse_args()
    
    run_batch_generation(args.machine)


