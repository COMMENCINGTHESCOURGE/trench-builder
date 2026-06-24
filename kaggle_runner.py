#!/usr/bin/env python3
"""Run Kaggle CLI commands with proper auth token."""
import subprocess
import os
import sys

# Read token from file
token_path = os.path.expanduser('~/.kaggle/api_token')
with open(token_path) as f:
    token = f.read().strip()

env = os.environ.copy()
env['KAGGLE_API_TOKEN'] = token

cmd = sys.argv[1:] if len(sys.argv) > 1 else ['kaggle', 'kernels', 'status', 
    'commencethescourge/scithary-genrator-auto-regenerator']

print(f"Running: {' '.join(cmd)}")
print(f"Token length: {len(token)}")

result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
print("STDOUT:", result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print(f"Exit code: {result.returncode}")
sys.exit(result.returncode)
