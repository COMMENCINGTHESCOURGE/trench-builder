#!/usr/bin/env python3
"""Trigger a new run of the Vinculum Interiors Kaggle kernel, wait for completion, download output."""
import os
import sys
import time
import json
import subprocess

# Read token
token_path = os.path.expanduser('~/.kaggle/access_token')
with open(token_path) as f:
    token = f.read().strip()

env = os.environ.copy()
env['KAGGLE_API_TOKEN'] = token

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
KERNEL = 'commencethescourge/vinculum-interiors'
OUTPUT_DIR = str(BASE_DIR / 'kaggle_logs')

def run(cmd, timeout=120):
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)
    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            print(f"  STDOUT: {line}")
    if result.stderr:
        for line in result.stderr.strip().split('\n'):
            print(f"  STDERR: {line}")
    print(f"  Exit: {result.returncode}")
    return result

# Step 1: Check current status
print("[1] Current kernel status:")
run(['kaggle', 'kernels', 'status', KERNEL])

# Step 2: Push a new version
print("\n[2] Pushing kernel update / triggering new run...")
push_dir = str(BASE_DIR / 'kaggle_push')
if os.path.isdir(push_dir):
    print(f"  Push dir exists: {push_dir}")
    # List contents
    for f in os.listdir(push_dir):
        fpath = os.path.join(push_dir, f)
        print(f"    {f} ({os.path.getsize(fpath)} bytes)")
    result = run(['kaggle', 'kernels', 'push', '-p', push_dir], timeout=300)
else:
    print(f"  ERROR: Push dir {push_dir} not found")
    sys.exit(1)

# Step 3: Wait for completion
print("\n[3] Waiting for kernel to complete...")
max_wait = 300
poll_interval = 15
elapsed = 0
while elapsed < max_wait:
    time.sleep(poll_interval)
    elapsed += poll_interval
    result = run(['kaggle', 'kernels', 'status', KERNEL])
    if 'COMPLETE' in result.stdout:
        print("  Kernel completed!")
        break
    if 'ERROR' in result.stdout or 'FAILED' in result.stdout:
        print("  Kernel failed!")
        break
    print(f"  Still running... (elapsed {elapsed}s)")

# Step 4: Download output
print("\n[4] Downloading output...")
os.makedirs(OUTPUT_DIR, exist_ok=True)
run(['kaggle', 'kernels', 'output', KERNEL, '-p', OUTPUT_DIR])

# Step 5: Verify
data_path = os.path.join(OUTPUT_DIR, 'vinculum_interiors_data.json')
if os.path.exists(data_path):
    with open(data_path) as f:
        data = json.load(f)
    print(f"\n[5] Output verified: {data.get('generator', 'unknown')}")
    print(f"  Rooms: {len(data.get('rooms', {}))}")
else:
    print(f"\n[5] Output NOT FOUND at {data_path}")
    for f in os.listdir(OUTPUT_DIR):
        print(f"  Found: {f}")
