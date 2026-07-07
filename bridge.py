#!/usr/bin/env python
"""Vinculum Bridge — connects the HTML frontend to Gemma 4 via llama.cpp.
   Runs on localhost:5000. No cloud. No API keys. No internet required."""

import subprocess, json, os, sys, tempfile
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Config — adjust paths for your device
LLAMA_CPP = Path.home() / "llama.cpp/build/bin/llama-cli"
MODEL_PATH = Path.home() / "models/gemma-4-2b-it-Q4_K_M.gguf"
PROMPT_TEMPLATES = Path(__file__).parent / "prompts.json"

# Load prompt templates
PROMPTS = json.loads(PROMPT_TEMPLATES.read_text()) if PROMPT_TEMPLATES.exists() else {
    "explain_resource": "You are an infrastructure teacher. Explain this Terraform resource in plain {language}. Keep it under 3 sentences. Resource: {resource_json}",
    "teach_checkpoint": "You are a gamified learning coach. The user is at checkpoint '{stage}'. Give them one tip to reach the next stage. Be encouraging.",
    "translate_terraform": "Translate this Terraform plan into {language}. Use simple terms a beginner would understand. Plan: {plan_json}",
    "recovery_guide": "You are a disaster recovery assistant. The user has lost cloud access but has this local state file. Help them understand what resources exist and how to rebuild. State: {state_json}"
}

SYSTEM_PROMPT = """You are Vinculum, an on-device AI infrastructure companion running Gemma 4 via llama.cpp. 
You are helpful, concise, and speak in plain language. You explain complex cloud concepts simply.
You work offline — no cloud, no API keys, no internet. You respond in 1-3 sentences unless asked for more detail."""

def query_llama(prompt, max_tokens=128, temperature=0.7):
    """Send prompt to llama.cpp and return response."""
    try:
        cmd = [
            str(LLAMA_CPP),
            "-m", str(MODEL_PATH),
            "--prompt", f"<bos><start_of_turn>user\n{prompt}<end_of_turn>\n<start_of_turn>model\n",
            "--temp", str(temperature),
            "--n-predict", str(max_tokens),
            "--no-display-prompt",
            "--simple-io",
            "-ngl", "0",  # CPU-only
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        response = result.stdout.strip()
        # Clean llama.cpp output artifacts
        for prefix in ["<start_of_turn>model\n", "assistant\n", "model\n"]:
            if response.startswith(prefix):
                response = response[len(prefix):]
        return response.strip()
    except subprocess.TimeoutExpired:
        return "[Timeout — model still processing on this device. Try shortening your input.]"
    except Exception as e:
        return f"[Error: {str(e)} — is llama.cpp running?]"

@app.route("/")
def index():
    return jsonify({"status": "Vinculum Bridge active", "model": str(MODEL_PATH), "device": "llama.cpp CPU"})

@app.route("/explain", methods=["POST"])
def explain():
    data = request.json
    language = data.get("language", "English")
    resource = json.dumps(data.get("resource", {}))
    prompt_template = PROMPTS.get("explain_resource", PROMPTS["explain_resource"])
    prompt = prompt_template.format(language=language, resource_json=resource)
    response = query_llama(f"{SYSTEM_PROMPT}\n\n{prompt}")
    return jsonify({"explanation": response, "language": language})

@app.route("/teach", methods=["POST"])
def teach():
    data = request.json
    stage = data.get("stage", "scoot")
    prompt_template = PROMPTS.get("teach_checkpoint", PROMPTS["teach_checkpoint"])
    prompt = prompt_template.format(stage=stage)
    response = query_llama(f"{SYSTEM_PROMPT}\n\n{prompt}")
    return jsonify({"stage": stage, "tip": response})

@app.route("/translate", methods=["POST"])
def translate_plan():
    data = request.json
    language = data.get("language", "Spanish")
    plan = json.dumps(data.get("plan", {}))
    prompt_template = PROMPTS.get("translate_terraform", PROMPTS["translate_terraform"])
    prompt = prompt_template.format(language=language, plan_json=plan)
    response = query_llama(prompt, max_tokens=256)
    return jsonify({"translation": response, "language": language})

@app.route("/recover", methods=["POST"])
def recover():
    data = request.json
    state = json.dumps(data.get("state", {}))
    prompt_template = PROMPTS.get("recovery_guide", PROMPTS["recovery_guide"])
    prompt = prompt_template.format(state_json=state)
    response = query_llama(prompt, max_tokens=256)
    return jsonify({"recovery_plan": response})

@app.route("/health")
def health():
    if MODEL_PATH.exists():
        size_mb = MODEL_PATH.stat().st_size / (1024*1024)
        return jsonify({"status": "healthy", "model": MODEL_PATH.name, "size_mb": round(size_mb, 1), "mode": "offline"})
    return jsonify({"status": "model not found", "path": str(MODEL_PATH)}), 404

if __name__ == "__main__":
    print(f"Vinculum Bridge starting...")
    print(f"  Model: {MODEL_PATH}")
    print(f"  llama.cpp: {LLAMA_CPP}")
    print(f"  Mode: OFFLINE (no cloud)")
    app.run(host="127.0.0.1", port=5000, debug=False)
