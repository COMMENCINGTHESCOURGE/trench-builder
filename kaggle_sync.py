#!/usr/bin/env python3
"""Push input files to Kaggle kernel, trigger run, download output."""
import os
import sys
import json
import time
import subprocess

# Auth — use API key approach via env vars (should be set in environment or ~/.kaggle/kaggle.json)
if 'KAGGLE_USERNAME' not in os.environ:
    os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME', '')
if 'KAGGLE_KEY' not in os.environ:
    os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY', '')

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    print("✓ Kaggle API authenticated")
except Exception as e:
    print(f"✗ Kaggle API import/auth failed: {e}")
    sys.exit(1)

kernel_owner = 'commencethescourge'
kernel_slug = 'scithary-genrator-auto-regenerator'
kernel_dir = os.path.expanduser('~/Projects/trench_builder/kaggle_push/scithary-genrator')

# Step 1: Check kernel status
print("\n[1] Checking kernel status...")
try:
    status = api.kernel_status(kernel_owner, kernel_slug)
    print(f"  Status: {status}")
except Exception as e:
    print(f"  Could not get status: {e}")

# Step 2: Verify kernel files
print("\n[2] Verifying kernel files...")
try:
    resp = api.kernels_list_files(kernel_owner, kernel_slug)
    files = resp if isinstance(resp, list) else resp.get('files', [])
    for f in files:
        print(f"  {f['name']:40s} {f['size']:>8d} bytes  {f.get('creationDate', '')}")
except Exception as e:
    print(f"  Could not list files: {e}")

# Step 3: Check for output / download
print("\n[3] Checking for kernel output...")
output_dir = os.path.expanduser('~/Projects/trench_builder/kaggle_logs')
os.makedirs(output_dir, exist_ok=True)
try:
    api.kernels_output(kernel_owner, kernel_slug, path=output_dir)
    print(f"  Output downloaded to {output_dir}")
    for f in os.listdir(output_dir):
        fpath = os.path.join(output_dir, f)
        print(f"  {f:50s} {os.path.getsize(fpath):>8d} bytes")
except Exception as e:
    print(f"  Output download failed: {e}")

# Step 4: Try to pull latest run output specifically
print("\n[4] Trying kernels_output with force...")
try:
    api.kernels_output(kernel_owner, kernel_slug, path=output_dir, force=True)
    for f in os.listdir(output_dir):
        fpath = os.path.join(output_dir, f)
        print(f"  {f:50s} {os.path.getsize(fpath):>8d} bytes")
except Exception as e:
    print(f"  Force output download failed: {e}")
