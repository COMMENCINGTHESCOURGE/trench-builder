#!/usr/bin/env python
"""
TRENCH CONFIG — Shared configuration for all Trench Builder + Erdos-Straus tools.

Single source of truth for paths, keys, and environment. Every script imports
this instead of hardcoding Path.home() / "Projects/...".

Usage:
    from trench_config import PATHS, KEYS
    output = PATHS.trench_builder / "supervisor_directives.json"

Override: create ~/.trench_config.json to override defaults.
Environment variables: TRENCH_PROJECTS_DIR, TRENCH_GDRIVE, etc.
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, fields


@dataclass
class TrenchPaths:
    """All filesystem paths used across the projects."""

    # ── Base directories ──
    home: Path = Path.home()
    projects: Path = Path.home() / "Projects"

    # ── Project directories ──
    trench_builder: Path = Path.home() / "Projects/trench_builder"
    erdos_straus: Path = Path.home() / "Projects/erdos-straus"
    research: Path = Path.home() / "Projects/research"

    # ── Hermes paths ──
    hermes_home: Path = Path.home() / "AppData/Local/hermes"
    hermes_env: Path = Path.home() / "AppData/Local/hermes/.env"
    hermes_memory: Path = Path.home() / "AppData/Local/hermes/memories"
    hermes_skills: Path = Path.home() / "AppData/Local/hermes/skills"

    # ── Cloud / G: drive ──
    gdrive_trench: Path = Path("G:/My Drive/Trench_Builder")
    gdrive_resonance: Path = Path("G:/My Drive/Resonance_Archive")
    gopro_footage: Path = Path("G:/My Drive/Trench_Builder/go pro")

    # ── AI agent paths ──
    gemini_brain: Path = Path.home() / ".gemini/antigravity/brain"
    gemini_chats: Path = Path.home() / ".gemini/tmp/dasha/chats"
    kimi_plans: Path = Path.home() / ".kimi/plans"
    kimi_sessions: Path = Path.home() / ".kimi/sessions"
    claude_sessions: Path = Path.home() / ".claude/projects/C--Users-dasha"

    # ── Output / state files ──
    supervisor_output: Path = Path.home() / "Projects/trench_builder/supervisor_directives.json"
    api_state: Path = Path.home() / "Projects/trench_builder/api_state.json"
    delta_report: Path = Path.home() / "Projects/trench_builder/delta_report.json"
    delta_learning: Path = Path.home() / "Projects/trench_builder/delta_learning.json"
    retroactive_audit: Path = Path.home() / "Projects/trench_builder/retroactive_audit.json"
    training_checkpoints: Path = Path.home() / "Projects/trench_builder/training_checkpoints"

    # ── Erdos-Straus specific ──
    erdos_output: Path = Path.home() / "Projects/erdos-straus/KAGGLE_OUTPUT_RECORD.jsonl"
    erdos_manifest: Path = Path.home() / "Projects/erdos-straus/work_manifest.json"
    erdos_verified: Path = Path.home() / "Projects/erdos-straus/verified_solutions.jsonl"
    erdos_daily_logs: Path = Path.home() / "Projects/erdos-straus/daily_logs"
    erdos_lock: Path = Path.home() / "Projects/erdos-straus/.sieve.lock"

    def ensure_dirs(self):
        """Create all required directories if they don't exist."""
        dirs = [
            self.trench_builder,
            self.erdos_straus,
            self.training_checkpoints,
            self.erdos_daily_logs,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        return self


def _load_api_keys(hermes_env: Path) -> dict:
    """Extract API keys from Hermes .env file."""
    keys = {}
    if hermes_env.exists():
        for line in hermes_env.read_text().split("\n"):
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key == "DEEPSEEK_API_KEY":
                keys["deepseek"] = val
            elif key == "OPENAI_API_KEY":
                keys["openai"] = val
            elif key == "STRIPE_SECRET_KEY":
                keys["stripe_secret"] = val
            elif key == "STRIPE_WEBHOOK_SECRET":
                keys["stripe_webhook"] = val
    return keys


def _load_overrides() -> dict:
    """Load user overrides from ~/.trench_config.json."""
    override_path = Path.home() / ".trench_config.json"
    if override_path.exists():
        try:
            return json.loads(override_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _apply_overrides(paths: TrenchPaths, overrides: dict) -> TrenchPaths:
    """Apply any user-specified path overrides."""
    path_field_names = {f.name for f in fields(TrenchPaths) if f.type == Path}
    for key, val in overrides.get("paths", {}).items():
        if key in path_field_names:
            setattr(paths, key, Path(val).expanduser().resolve())
    return paths


# ── Singleton instances ──
PATHS = _apply_overrides(TrenchPaths(), _load_overrides())
KEYS = _load_api_keys(PATHS.hermes_env)

# Auto-create essential dirs on import
PATHS.ensure_dirs()


# ── Convenience accessors ──
def deepseek_key():
    return KEYS.get("deepseek")


def openai_key():
    return KEYS.get("openai")


def stripe_secret():
    return os.getenv("STRIPE_SECRET_KEY", KEYS.get("stripe_secret", ""))


def stripe_webhook_secret():
    return os.getenv("STRIPE_WEBHOOK_SECRET", KEYS.get("stripe_webhook", ""))
