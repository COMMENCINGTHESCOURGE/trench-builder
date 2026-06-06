#!/usr/bin/env python
"""
CODEX NODE — Compute node wrapper for Codex CLI
================================================
Three integration modes, ordered by capability:

  1. EXEC MODE (simplest):
     codex_node.exec("process this video", image="file.mp4")
     → Shells out to `codex exec`, returns last message.

  2. MCP MODE (deepest):
     codex_node.start_mcp_server()
     → Registers Codex as an MCP server. Hermes can invoke
       Codex tools directly via native MCP client.

  3. OUTPUT-SERVER MODE (browse results):
     Serves results at http://127.0.0.1:8765/report.html
     → Static file server for processed outputs.

CAPABILITIES (what Codex brings that other nodes don't):
  - Video processing (frame extraction, audio isolation, waveform)
  - Format conversion (WebM, GIF, contact sheets)
  - TTS dialogue generation (Windows Speech Synthesis)
  - Caption/subtitle generation (.ass format)
  - Code review (`codex review`)
  - Image-attached prompts (`codex exec --image`)
  - MCP server mode — Hermes-native tool consumption

USAGE:
  python codex_node.py exec "describe this video" --image video.mp4
  python codex_node.py review --uncommitted
  python codex_node.py mcp-server
  python codex_node.py capabilities  # print capability matrix

DaShawn / Guinea Pig Trench LLC — May 2026
"""

import subprocess
import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
import tempfile


# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════

CODEX_BIN = "codex"
OUTPUT_SERVER = "http://127.0.0.1:8765"

# Detect codex binary
def _find_codex():
    """Find the codex binary on the system."""
    for candidate in [
        "codex.cmd",
        str(Path.home() / "AppData/Roaming/npm/codex.cmd"),
        "codex",
        str(Path.home() / "AppData/Roaming/npm/codex"),
    ]:
        try:
            result = subprocess.run(
                [candidate, "--version"],
                capture_output=True, text=True, timeout=5,
                shell=True if candidate.endswith('.cmd') else False
            )
            if result.returncode == 0:
                return candidate
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    return None


CODEX_PATH = _find_codex()


# ═══════════════════════════════════════════════════════
# CAPABILITY MATRIX
# ═══════════════════════════════════════════════════════

@dataclass
class CodexCapabilities:
    """What Codex can do that other nodes cannot."""

    # Video / Media
    video_frame_extraction: bool = True
    audio_isolation: bool = True
    waveform_generation: bool = True
    contact_sheet: bool = True
    tts_dialogue: bool = True       # Windows Speech Synthesis
    subtitle_generation: bool = True  # .ass format with positioning

    # Format Conversion
    mp4_to_webm: bool = True
    mp4_to_gif: bool = True
    mp4_faststart: bool = True      # Browser-ready metadata

    # AI Capabilities
    image_prompting: bool = True    # `codex exec --image`
    code_review: bool = True        # `codex review`
    json_output: bool = True        # `codex exec --json`
    mcp_server: bool = True         # `codex mcp-server`
    remote_executor: bool = True    # `codex exec-server`

    # Infrastructure
    port: int = 8765
    cli_version: str = ""
    status: str = "unknown"

    def __post_init__(self):
        if CODEX_PATH:
            try:
                result = subprocess.run(
                    [CODEX_PATH, "--version"],
                    capture_output=True, text=True, timeout=5
                )
                self.cli_version = result.stdout.strip()
                self.status = "active"
            except Exception:
                self.status = "installed_but_error"
        else:
            self.status = "not_found"

    def matrix(self) -> str:
        """Human-readable capability matrix."""
        lines = [
            "╔══════════════════════════════════════════╗",
            "║  CODEX NODE — Capability Matrix          ║",
            f"║  CLI: {self.cli_version[:35]:35s} ║",
            f"║  Status: {self.status:33s} ║",
            "╠══════════════════════════════════════════╣",
            "║  MEDIA PROCESSING                        ║",
            "║    Video frame extraction    ✓           ║",
            "║    Audio isolation           ✓           ║",
            "║    Waveform generation       ✓           ║",
            "║    Contact sheet             ✓           ║",
            "║    TTS dialogue generation   ✓           ║",
            "║    Subtitle generation (.ass)✓           ║",
            "╠══════════════════════════════════════════╣",
            "║  FORMAT CONVERSION                       ║",
            "║    MP4 → WebM (VP9/Opus)    ✓           ║",
            "║    MP4 → GIF (animated)     ✓           ║",
            "║    MP4 fast-start metadata  ✓           ║",
            "╠══════════════════════════════════════════╣",
            "║  AI CAPABILITIES                         ║",
            "║    Image-attached prompts    ✓           ║",
            "║    Code review               ✓           ║",
            "║    JSONL output mode         ✓           ║",
            "║    MCP server mode           ✓           ║",
            "║    Remote executor mode      ✓           ║",
            "╚══════════════════════════════════════════╝",
        ]
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# EXEC MODE — Run Codex non-interactively
# ═══════════════════════════════════════════════════════

def _build_exec_command(
    sandbox: str,
    json_output: bool,
    ephemeral: bool,
    model: Optional[str],
    cwd: Optional[str],
    images: Optional[list[str]],
    prompt: str,
) -> list[str]:
    cmd = [CODEX_PATH, "exec"]
    if json_output:
        cmd.append("--json")
    if ephemeral:
        cmd.append("--ephemeral")
    if sandbox:
        cmd.extend(["--sandbox", sandbox])
    if model:
        cmd.extend(["--model", model])
    if cwd:
        cmd.extend(["--cd", cwd])
    if images:
        for img in images:
            cmd.extend(["--image", img])
    cmd.append(prompt)
    return cmd


def _parse_jsonl_output(stdout: str) -> Tuple[list, str]:
    events = []
    last_message = ""
    for line in stdout.strip().split("\n"):
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass

    for event in reversed(events):
        if event.get("type") == "assistant":
            msg = event.get("message", {})
            content = msg.get("content", "")
            if isinstance(content, list):
                texts = [c.get("text", "") for c in content if isinstance(c, dict)]
                last_message = " ".join(texts)
            elif isinstance(content, str):
                last_message = content
            if last_message.strip():
                break
    return events, last_message


def exec_prompt(
    prompt: str,
    images: list[str] = None,
    model: str = None,
    cwd: str = None,
    sandbox: str = "workspace-write",
    json_output: bool = True,
    timeout: int = 600,
    ephemeral: bool = True,
) -> dict:
    """
    Run Codex non-interactively with a prompt.

    Args:
        prompt: The instruction for Codex.
        images: Optional list of image file paths to attach.
        model: Model override (default: uses config.toml setting).
        cwd: Working directory for the agent.
        sandbox: Sandbox mode (read-only, workspace-write, danger-full-access).
        json_output: Emit JSONL events (parseable by caller).
        timeout: Max seconds to wait for completion.
        ephemeral: Don't persist session to disk.

    Returns:
        dict with: success, output, last_message, duration, model_used, error
    """
    if not CODEX_PATH:
        return {
            "success": False,
            "error": "Codex CLI not found on system",
            "codex_path": CODEX_PATH,
        }

    cmd = _build_exec_command(sandbox, json_output, ephemeral, model, cwd, images, prompt)
    start = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or os.getcwd(),
        )

        duration = time.time() - start

        events = []
        last_message = ""
        if json_output and result.stdout:
            events, last_message = _parse_jsonl_output(result.stdout)

        return {
            "success": result.returncode == 0,
            "output": result.stdout[:10000] if result.stdout else "",
            "stderr": result.stderr[:2000] if result.stderr else "",
            "last_message": last_message[:5000],
            "duration": round(duration, 1),
            "events_count": len(events),
            "exit_code": result.returncode,
            "error": result.stderr[:500] if result.returncode != 0 else None,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Timed out after {timeout}s",
            "duration": timeout,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "duration": time.time() - start,
        }


def exec_review(
    prompt: str = None,
    uncommitted: bool = False,
    base_branch: str = None,
    commit_sha: str = None,
    timeout: int = 300,
) -> dict:
    """
    Run Codex code review.

    Args:
        prompt: Custom review instructions.
        uncommitted: Review staged + unstaged changes.
        base_branch: Review against a base branch.
        commit_sha: Review a specific commit.
        timeout: Max seconds.

    Returns:
        dict with review results.
    """
    if not CODEX_PATH:
        return {"success": False, "error": "Codex CLI not found"}

    cmd = [CODEX_PATH, "review", "--json"]

    if uncommitted:
        cmd.append("--uncommitted")
    if base_branch:
        cmd.extend(["--base", base_branch])
    if commit_sha:
        cmd.extend(["--commit", commit_sha])
    if prompt:
        cmd.append(prompt)

    start = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        duration = time.time() - start
        events = []
        for line in result.stdout.strip().split("\n"):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass

        return {
            "success": result.returncode == 0,
            "output": result.stdout[:10000],
            "events_count": len(events),
            "duration": round(duration, 1),
            "exit_code": result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Timed out after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════
# MCP MODE — Codex as MCP server for Hermes
# ═══════════════════════════════════════════════════════

def mcp_server_config() -> dict:
    """
    Generate the MCP server configuration for Hermes to consume.
    Add this to ~/AppData/Local/hermes/config.yaml under mcp_servers.

    Usage:
        python codex_node.py mcp-config
    """
    return {
        "codex": {
            "command": CODEX_PATH or "codex",
            "args": ["mcp-server"],
            "description": "OpenAI Codex CLI — code generation, review, media processing",
            "capabilities": [
                "code_generation",
                "code_review",
                "image_analysis",
                "file_processing",
                "shell_execution",
            ],
        }
    }


def start_mcp_server(config_overrides: dict = None):
    """
    Start Codex as an MCP server process.
    Hermes can then invoke Codex tools via native MCP client.

    This is a BLOCKING call — run in background or as a subprocess.
    For background use: codex_node.py mcp-server &
    """
    if not CODEX_PATH:
        print("Codex CLI not found", file=sys.stderr)
        sys.exit(1)

    cmd = [CODEX_PATH, "mcp-server"]

    if config_overrides:
        for key, val in config_overrides.items():
            cmd.extend(["-c", f"{key}={val}"])

    print(f"[codex_node] Starting MCP server: {' '.join(cmd)}", file=sys.stderr)
    subprocess.run(cmd)


# ═══════════════════════════════════════════════════════
# OUTPUT SERVER — Browse processed results
# ═══════════════════════════════════════════════════════

def check_output_server() -> dict:
    """Check if the Codex output server is running."""
    import urllib.request
    try:
        req = urllib.request.Request(f"{OUTPUT_SERVER}/")
        urllib.request.urlopen(req, timeout=3)
        return {"running": True, "url": OUTPUT_SERVER}
    except Exception:
        return {"running": False, "url": OUTPUT_SERVER}


def get_report() -> dict:
    """Fetch the latest report summary from the output server."""
    import urllib.request
    try:
        req = urllib.request.Request(f"{OUTPUT_SERVER}/reports/summary.md")
        resp = urllib.request.urlopen(req, timeout=5)
        return {
            "available": True,
            "summary": resp.read().decode()[:5000],
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


# ═══════════════════════════════════════════════════════
# ORCHESTRATOR INTEGRATION — Erdos node interface
# ═══════════════════════════════════════════════════════

def orchestrator_status() -> dict:
    """
    Status report formatted for Erdos orchestrator integration.
    Same format as master_orchestrator.py merge_node_result expects.
    """
    caps = CodexCapabilities()
    server = check_output_server()

    return {
        "node": "codex",
        "type": "Codex CLI — AI agent + media processor",
        "status": caps.status,
        "cli_version": caps.cli_version,
        "output_server": server,
        "capabilities": {
            "video_processing": caps.video_frame_extraction,
            "audio_isolation": caps.audio_isolation,
            "tts_dialogue": caps.tts_dialogue,
            "code_review": caps.code_review,
            "image_prompting": caps.image_prompting,
            "mcp_server": caps.mcp_server,
        },
        "automation_level": "90% — fully automatable via `codex exec`",
        "bottleneck": "Requires OpenAI credits. No offline mode. MCP server needs Hermes config update.",
        "fix": "Add to Hermes config.yaml mcp_servers. Use --ephemeral for stateless tasks.",
        "solutions": 0,   # Not a sieve node — produces media/analysis output
        "last_run": datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Codex Node — Compute node wrapper for Codex CLI"
    )
    sub = parser.add_subparsers(dest="command")

    # exec
    exec_p = sub.add_parser("exec", help="Run Codex non-interactively")
    exec_p.add_argument("prompt", help="Instruction for Codex")
    exec_p.add_argument("--image", action="append", help="Image file(s) to attach")
    exec_p.add_argument("--model", help="Model override")
    exec_p.add_argument("--cwd", help="Working directory")
    exec_p.add_argument("--sandbox", default="workspace-write",
                        choices=["read-only", "workspace-write", "danger-full-access"])
    exec_p.add_argument("--timeout", type=int, default=600)
    exec_p.add_argument("--no-json", action="store_true", help="Disable JSONL output")

    # review
    review_p = sub.add_parser("review", help="Run Codex code review")
    review_p.add_argument("prompt", nargs="?", help="Custom review instructions")
    review_p.add_argument("--uncommitted", action="store_true")
    review_p.add_argument("--base", help="Base branch")
    review_p.add_argument("--commit", help="Commit SHA")
    review_p.add_argument("--timeout", type=int, default=300)

    # mcp
    sub.add_parser("mcp-server", help="Start Codex as MCP server (blocking)")
    sub.add_parser("mcp-config", help="Print MCP server config for Hermes config.yaml")

    # info
    sub.add_parser("capabilities", help="Print capability matrix")
    sub.add_parser("status", help="Print orchestrator status report")

    args = parser.parse_args()

    if args.command == "exec":
        result = exec_prompt(
            prompt=args.prompt,
            images=args.image,
            model=args.model,
            cwd=args.cwd,
            sandbox=args.sandbox,
            json_output=not args.no_json,
            timeout=args.timeout,
        )
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "review":
        result = exec_review(
            prompt=args.prompt,
            uncommitted=args.uncommitted,
            base_branch=args.base,
            commit_sha=args.commit,
            timeout=args.timeout,
        )
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "mcp-server":
        start_mcp_server()

    elif args.command == "mcp-config":
        print(json.dumps(mcp_server_config(), indent=2))

    elif args.command == "capabilities":
        caps = CodexCapabilities()
        print(caps.matrix())

    elif args.command == "status":
        print(json.dumps(orchestrator_status(), indent=2, default=str))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
