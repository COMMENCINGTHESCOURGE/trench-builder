# Vinculum · On-Device AI to Demystify Infrastructure for Everyone

**Gemma 4 Good Hackathon — llama.cpp Track**

A no-code Terraform companion that explains, teaches, and recovers infrastructure — running entirely on a $150 Android phone with Gemma 4 via llama.cpp. No cloud. No API keys. No connectivity required.

[![Demo](https://img.shields.io/badge/Demo-Live-green)](https://commencingthescourge.github.io/trench_builder/STACK_CATHEDRAL.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Gemma 4](https://img.shields.io/badge/Model-Gemma_4_2B-blue)](https://www.kaggle.com/models/google/gemma-4)
[![llama.cpp](https://img.shields.io/badge/Runtime-llama.cpp-orange)](https://github.com/ggerganov/llama.cpp)

## The Problem

Infrastructure-as-code (Terraform) powers the cloud, but it's locked behind:
- **YAML/HCL syntax** that requires engineering literacy
- **English-only documentation** excluding 75% of the world
- **Always-on internet** — useless during disasters or in rural areas
- **No feedback loop** — you type, pray, and hope `terraform apply` works

These barriers exclude non-English speakers, beginners, students, and communities with intermittent connectivity — precisely the people who need infrastructure knowledge most.

## The Solution

**Vinculum** is a web-based no-code Terraform interface powered by Gemma 4 running locally via llama.cpp on commodity Android hardware.

| Component | What It Does |
|-----------|-------------|
| **Vinculum Canvas** | Drag-and-drop infrastructure builder (S3, EC2, VPC) — outputs valid Terraform JSON |
| **Gemma 4 Explainer** | Translates every plan into plain language in Spanish, French, Arabic + more |
| **Stack Cathedral** | Gamified learning journey: 8 checkpoint stages from `scoot` → `run` |
| **Local Recovery** | Airplane mode? No problem. Full Terraform state inspection and restoration offline |
| **FracType Metrics** | Knowledge density tracking — measures what the user actually learned |

All running on a **Motorola Moto G Power (2022)** — $150, 4GB RAM, no GPU.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  ANDROID PHONE                       │
│  ┌───────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Vinculum  │  │  Flask   │  │  llama.cpp        │ │
│  │  HTML/JS  │──│  Bridge  │──│  Gemma 4 (Q4_K_M) │ │
│  │  Canvas   │  │  :5000   │  │  ~8 tk/s on CPU   │ │
│  └───────────┘  └──────────┘  └──────────────────┘ │
│       │                              │              │
│       │    Terraform JSON            │ Plain-lang   │
│       │    State files               │ explanations │
│       ▼                              ▼              │
│  ┌──────────────────────────────────────────────┐   │
│  │            Local Storage (SQLite)             │   │
│  │   Plans · State · Checkpoint progress        │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ✈ AIRPLANE MODE — everything still works           │
└─────────────────────────────────────────────────────┘
```

## Hardware Requirements

Tested on:
- **Moto G Power (2022)** — MediaTek Helio G37, 4GB RAM
- **Termux** (Android terminal emulator)
- **llama.cpp** built from source with `-DGGML_OPENMP=ON`
- **Gemma 4 2B** quantized to Q4_K_M (~1.5GB)
- Token generation: **~8 tokens/second** on CPU

## Quick Start

### 1. Install Termux on Android
```
pkg update && pkg upgrade
pkg install git cmake python build-essential
```

### 2. Build llama.cpp
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
mkdir build && cd build
cmake .. -DGGML_OPENMP=ON
make -j4
```

### 3. Download Gemma 4 GGUF
```bash
# From Kaggle (requires kaggle.json API key)
pip install kagglehub
python -c "import kagglehub; kagglehub.model_download('google/gemma-4/gguf/gemma-4-2b-it-Q4_K_M.gguf')"
```

### 4. Start the bridge server
```bash
cd trench_builder
pip install flask
python bridge.py  # serves on localhost:5000
```

### 5. Open the demo
```
http://127.0.0.1:8081/STACK_CATHEDRAL.html
```

## Demo Videos

| Clip | What It Shows |
|------|--------------|
| [Canvas Build](demo/) | Drag-and-drop S3 bucket creation, Gemma 4 explains in Spanish |
| [Airplane Mode](demo/) | Wi-Fi off, state recovery still works |
| [Checkpoint Progression](demo/) | User completes `crawl` → `stand`, FracType badge awarded |

## Track Alignment

- **llama.cpp** ($10K): Gemma 4 fully on-device, resource-constrained hardware
- **Digital Equity** ($10K): Multilingual, offline, no-code access to infrastructure knowledge
- **Global Resilience** ($10K): Post-disaster state recovery without internet

## Team

- **DaShawn** (@commencingthescourge) — Architecture, frontend, phone deployment
- Built with: Three.js, llama.cpp, Gemma 4, Python/Flask, Kaggle

## License

MIT — Open weight model, open source code, open future.
