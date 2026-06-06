#!/usr/bin/env python3
"""
GEMMA INVOKER — Structured Gemma/GenAI API wrapper.

Fixes the 53-line stub that imported google.generativeai and never called anything.
Uses the google-genai SDK (already installed) with retry logic, structured output,
and usage tracking for the Voltaic Pile pipeline.

Usage:
    python gemma-invoker.py "prompt text"
    python gemma-invoker.py "prompt" --system "You are a helpful assistant"
    python gemma-invoker.py "prompt" --model gemini-2.5-flash --json
    python gemma-invoker.py --list-models
"""

import sys
import json
import os
import time
from typing import Optional, Dict, Any


# ── Configuration ──

DEFAULT_MODEL = "gemini-2.5-flash"
MAX_RETRIES = 3
RETRY_DELAY = 2.0

# Check for API key
API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or None


# ── Client ──

class GemmaInvoker:
    """Structured wrapper around the google-genai SDK."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or API_KEY
        self.client = None
        self.usage = {"calls": 0, "total_tokens": 0, "errors": 0}

    def _ensure_client(self):
        """Lazy init the GenAI client."""
        if self.client is not None:
            return
        if not self.api_key:
            raise ValueError(
                "No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY env var, "
                "or pass api_key= to constructor."
            )
        try:
            from google import genai
            from google.genai.types import HttpOptions
            self.client = genai.Client(
                http_options=HttpOptions(api_version="v1")
            )
        except ImportError:
            raise ImportError(
                "google-genai package required. Run: pip install google-genai"
            )

    def ask(self, prompt: str, system_instruction: Optional[str] = None,
            model: str = DEFAULT_MODEL, output_json: bool = False,
            temperature: float = 0.7) -> Dict[str, Any]:
        """
        Send a prompt to Gemma/Gemini and return structured response.

        Returns:
            {"text": "...", "model": "...", "usage": {...}} on success
            {"error": "..."} on failure
        """
        self._ensure_client()
        self.usage["calls"] += 1

        for attempt in range(MAX_RETRIES):
            try:
                contents = []
                if system_instruction and hasattr(self.client.models, "generate_content"):
                    # Gemini API uses system_instruction parameter
                    pass

                kwargs = {
                    "model": model,
                    "contents": prompt,
                }
                if system_instruction:
                    kwargs["system_instruction"] = system_instruction
                if output_json:
                    kwargs["config"] = {"response_mime_type": "application/json"}

                response = self.client.models.generate_content(**kwargs)

                result = {
                    "text": response.text,
                    "model": model,
                    "usage": {},
                }

                # Extract usage if available
                if hasattr(response, "usage_metadata") and response.usage_metadata:
                    u = response.usage_metadata
                    result["usage"] = {
                        "prompt_tokens": getattr(u, "prompt_token_count", 0),
                        "response_tokens": getattr(u, "candidates_token_count", 0),
                        "total_tokens": getattr(u, "total_token_count", 0),
                    }
                    self.usage["total_tokens"] += result["usage"]["total_tokens"]

                # Parse JSON if requested
                if output_json:
                    try:
                        result["parsed"] = json.loads(response.text)
                    except json.JSONDecodeError as e:
                        result["parse_error"] = str(e)

                return result

            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg:
                    print(f"  [RATE LIMIT] Attempt {attempt + 1}/{MAX_RETRIES}, retrying...")
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                if attempt < MAX_RETRIES - 1:
                    print(f"  [RETRY] Attempt {attempt + 1} failed: {err_msg[:80]}")
                    time.sleep(RETRY_DELAY)
                    continue
                self.usage["errors"] += 1
                return {"error": err_msg, "model": model}

    def list_models(self) -> list:
        """List available models."""
        self._ensure_client()
        try:
            models = self.client.models.list()
            return [m.name for m in models]
        except Exception as e:
            return [f"Error listing models: {e}"]

    def usage_report(self) -> Dict:
        """Return usage stats."""
        return dict(self.usage)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gemma/GenAI structured wrapper")
    parser.add_argument("prompt", nargs="?", help="Prompt text")
    parser.add_argument("--system", "-s", help="System instruction")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument("--json", "-j", action="store_true", help="Request JSON output")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--usage", action="store_true", help="Show usage stats")
    args = parser.parse_args()

    invoker = GemmaInvoker()

    if args.list_models:
        print("Available models:")
        for m in invoker.list_models():
            print(f"  {m}")
        return

    if args.usage:
        print(invoker.usage_report())
        return

    if not args.prompt:
        # Interactive mode
        print("Gemma Invoker — interactive mode. Ctrl+D to exit.")
        try:
            while True:
                prompt = input("> ")
                if not prompt:
                    continue
                result = invoker.ask(prompt, args.system, args.model, args.json, args.temperature)
                if "error" in result:
                    print(f"[ERR] {result['error']}")
                else:
                    print(result["text"])
                    if "parsed" in result:
                        print(json.dumps(result["parsed"], indent=2))
        except EOFError:
            print()
        return

    result = invoker.ask(args.prompt, args.system, args.model, args.json, args.temperature)
    if "error" in result:
        print(f"[ERR] {result['error']}")
        sys.exit(1)
    print(result["text"])
    if args.json:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
