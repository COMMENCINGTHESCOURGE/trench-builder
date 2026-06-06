#!/usr/bin/env python3
"""
PROCESS WARDEN — Process supervisor with health checks.

Replaces the RESONANCE_ORCHESTRATOR pattern (subprocess.Popen + while True + file size checks)
with a proper supervisor that restarts crashed processes, checks health endpoints,
and logs structured output.

Usage:
    python process-warden.py --config processes.json
    python process-warden.py --cmd "python server.py" --health http://localhost:8000/health
"""

import sys
import os
import json
import time
import signal
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime


class Process:
    """A supervised process with health checks and auto-restart."""

    def __init__(self, name: str, cmd: list, health_url: str = "",
                 cwd: str = "", restart_delay: float = 2.0,
                 max_restarts: int = 0):
        self.name = name
        self.cmd = cmd
        self.health_url = health_url
        self.cwd = cwd or os.getcwd()
        self.restart_delay = restart_delay
        self.max_restarts = max_restarts
        self.proc = None
        self.restart_count = 0
        self.start_time = 0

    def start(self):
        """Start the process."""
        self.start_time = time.time()
        self.proc = subprocess.Popen(
            self.cmd,
            cwd=self.cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        log(f"[{self.name}] Started PID {self.proc.pid}")

    def is_healthy(self) -> bool:
        """Check health endpoint or process liveness."""
        if not self.health_url:
            return self.proc is not None and self.proc.poll() is None
        try:
            resp = urllib.request.urlopen(self.health_url, timeout=3)
            return resp.status == 200
        except (urllib.error.URLError, Exception):
            return False

    def poll(self) -> bool:
        """Returns True if still running and healthy."""
        if self.proc is None:
            return False
        ret = self.proc.poll()
        if ret is not None:
            log(f"[{self.name}] Exited with code {ret}")
            return False
        return True

    def restart(self):
        """Restart the process if under limit."""
        if self.max_restarts > 0 and self.restart_count >= self.max_restarts:
            log(f"[{self.name}] Max restarts ({self.max_restarts}) reached. Giving up.")
            return False
        self.restart_count += 1
        log(f"[{self.name}] Restarting ({self.restart_count}/{self.max_restarts})...")
        time.sleep(self.restart_delay)
        self.start()
        return True

    def stop(self):
        """Graceful stop."""
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
            log(f"[{self.name}] Stopped")


def log(msg: str):
    """Structured log line with timestamp."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Process supervisor with health checks")
    parser.add_argument("--cmd", nargs="+", help="Command to run (e.g. --cmd python server.py)")
    parser.add_argument("--name", default="process", help="Process name")
    parser.add_argument("--health", default="", help="Health check URL")
    parser.add_argument("--config", help="JSON config file with process list")
    parser.add_argument("--restart-delay", type=float, default=2.0, help="Seconds between restarts")
    parser.add_argument("--max-restarts", type=int, default=3, help="Max auto-restarts (0=unlimited)")
    parser.add_argument("--check-interval", type=float, default=10.0, help="Health check interval")
    args = parser.parse_args()

    processes = []

    if args.config:
        # Load from JSON config
        with open(args.config) as f:
            config = json.load(f)
        for entry in config.get("processes", []):
            p = Process(
                name=entry.get("name", "unnamed"),
                cmd=entry["cmd"] if isinstance(entry["cmd"], list) else entry["cmd"].split(),
                health_url=entry.get("health_url", ""),
                cwd=entry.get("cwd", os.getcwd()),
                restart_delay=entry.get("restart_delay", args.restart_delay),
                max_restarts=entry.get("max_restarts", args.max_restarts),
            )
            processes.append(p)
            p.start()
    elif args.cmd:
        p = Process(
            name=args.name,
            cmd=args.cmd if isinstance(args.cmd, list) else args.cmd.split(),
            health_url=args.health,
            restart_delay=args.restart_delay,
            max_restarts=args.max_restarts,
        )
        processes.append(p)
        p.start()
    else:
        parser.print_help()
        sys.exit(1)

    # Handle shutdown
    shutdown = False

    def handler(sig, frame):
        nonlocal shutdown
        log("Shutting down...")
        shutdown = True

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    # Main loop
    try:
        while not shutdown:
            for p in list(processes):
                if not p.poll():
                    if not p.restart():
                        processes.remove(p)
                        log(f"[{p.name}] Removed from supervision")

                if p.health_url and p.proc and p.proc.poll() is None:
                    if not p.is_healthy():
                        log(f"[{p.name}] Health check failed! Restarting...")
                        p.stop()
                        if not p.restart():
                            processes.remove(p)
                            log(f"[{p.name}] Removed from supervision")

            time.sleep(args.check_interval)
    except KeyboardInterrupt:
        pass
    finally:
        for p in processes:
            p.stop()

    log("All processes stopped.")


if __name__ == "__main__":
    main()
