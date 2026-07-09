#!/usr/bin/env python
"""
pip_version_guard.py — detect dependency pins that block future Python versions.

Same pattern as node24-ci-guard: scan constraints → detect pins that fail
on newer runtimes → flag before install breaks. Applied to Python/pip instead
of GitHub Actions/Node.

Usage:
  python pip_version_guard.py requirements.txt --target 3.13
  python pip_version_guard.py pyproject.toml --target 3.12 3.13
"""
import sys
import subprocess
import argparse
from pathlib import Path


def check_dependency(reqs_file, target_py_version):
    """Try installing requirements in a dry-run against target Python version.
    
    Uses pip's --dry-run and --python-version flags to simulate installation
    without actually modifying the environment.
    """
    reqs_path = Path(reqs_file)
    if not reqs_path.exists():
        print(f"SKIP: {reqs_file} not found")
        return True
    
    cmd = [
        sys.executable, "-m", "pip", "install",
        "-r", str(reqs_path),
        "--dry-run",
        "--python-version", target_py_version,
        "--only-binary", ":all:",
        "--report", "-",  # JSON report to stdout
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"  PASS: {reqs_file} resolves on Python {target_py_version}")
            return True
        else:
            print(f"  FAIL: {reqs_file} BLOCKED on Python {target_py_version}")
            # Extract the blocking dependency from stderr
            for line in result.stderr.split('\n'):
                if 'Cannot install' in line or 'not supported' in line or 'requires' in line:
                    print(f"    -> {line.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: {reqs_file} on Python {target_py_version}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Guard against dependency pins blocking future Python versions"
    )
    parser.add_argument("requirements", nargs="+", help="requirements.txt or pyproject.toml files")
    parser.add_argument("--target", nargs="+", default=["3.13"],
                        help="Target Python versions to test (default: 3.13)")
    args = parser.parse_args()
    
    current = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"pip_version_guard — current Python {current}")
    print(f"Testing against: {', '.join(args.target)}\n")
    
    failures = 0
    for reqs_file in args.requirements:
        for target in args.target:
            if not check_dependency(reqs_file, target):
                failures += 1
    
    print(f"\n{failures} blocker(s) found.")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
