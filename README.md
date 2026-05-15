# TRENCH BUILDER 🏗️

> **Democratizing architectural engineering with local AI.**
> Gemma 4 Good Hackathon 2026 — Digital Equity & Ollama Track

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Three.js](https://img.shields.io/badge/Three.js-r128-black)](https://threejs.org/)
[![Ollama](https://img.shields.io/badge/Ollama-gemma4:2b-blue)](https://ollama.com)
[![Hackathon](https://img.shields.io/badge/Gemma%204%20Good-Hackathon%202026-purple)](https://kaggle.com/competitions/gemma-4-good-hackathon)

A **single-file HTML application** that provides professional-grade 3D construction visualization, topography surveying, interior design, CAD import, and AI-assisted design feedback — entirely in the browser. No installation. No license. No GPU required.

**Gemma 4 powers the AI design assistant** — running locally via Ollama, answering construction questions, recommending materials, and explaining the physics behind every structure.

---

## 🎯 The Problem

Architectural engineering software costs $2,000–$10,000 per license. These tools gatekeep who can design, build, and visualize. A community center in a rural area, a disaster-resilient school, or a first-time homeowner — all locked out by cost.

The digital divide in construction is widening.

## ✨ Our Solution

TRENCH BUILDER runs on any device with a web browser. Open the HTML file. Start building. Ask Gemma 4 for guidance.

| Feature | Status |
|---------|--------|
| 🏠 Structure placement (walls, floors, foundations, roofs) | ✅ |
| 🔧 MEP systems (plumbing, electrical, HVAC) | ✅ |
| 🗺️ Topography survey (elevation, slope, drainage, soil type) | ✅ |
| 🏛️ Interior design (room scanning, material assignment, 9 finishes) | ✅ |
| 📐 Vanishing point / perspective grid | ✅ |
| ⚡ EM field visualization (flux lines, particle fields) | ✅ |
| 🔥 Thermal bloom simulation (smoothstep distance field) | ✅ |
| 🌊 Caustic projection (exponential falloff) | ✅ |
| 💡 Wave optics / iridescence (thin-film interference) | ✅ |
| 🎞️ Film grain post-processing | ✅ |
| ☀️ God rays / volumetric light | ✅ |
| ◑ SSAO (ambient occlusion) | ✅ |
| 🎥 Cinematography engine (12-beat Sentai B-roll) | ✅ |
| 🔧 GameShark Creative Mode (wireframe + live parameter inspector) | ✅ |
| 📦 CAD import (Onshape → STL, 33 parts) | ✅ |
| 🎓 Training data export (35K samples for ML) | ✅ |
| 🤖 **Gemma 4 AI Design Assistant (Ollama)** | ✅ |

---

## 🤖 Gemma 4 Integration

```
User asks: "Is the voice coil properly sized for 50Hz?"
           ↓
Scene state sent: {bass_freq: 45, amplitude: 0.6, materials: {copper, ferrite, paper}}
           ↓
Ollama → Gemma 4 2B (local inference, zero API cost)
           ↓
Response: "At 45Hz with 0.6 amplitude, the 55mm voice coil is within spec. 
           For sustained 50Hz operation, consider increasing winding density 
           by 15% to reduce thermal stress."
```

**Why local inference matters:**
- 🌐 Offline communities — no internet after initial page load
- 🔒 Privacy — design data never leaves the device
- 💰 Zero cost — no API fees, no usage limits
- 📱 Accessibility — functions on a $200 Chromebook

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/COMMENCINGTHESCOURGE/trench-builder.git
cd trench-builder

# 2. Start Ollama (for AI assistant)
ollama serve
ollama pull gemma4:2b

# 3. Open in browser
open TRENCH_BUILDER_v5.html
# OR any modern browser → File → Open File → TRENCH_BUILDER_v5.html

# 4. Click "ASK GEMMA 4" button to activate AI assistant
```

---

## 📂 Repository Structure

```
trench-builder/
├── TRENCH_BUILDER_v1.html          Foundation (walls, avatar basics)
├── TRENCH_BUILDER_v2.html          CAD + MEP + landscaping
├── TRENCH_BUILDER_v3.html          Topography + interior design + VP
├── TRENCH_BUILDER_v4.html          18/22 rendering principles
├── TRENCH_BUILDER_v5.html          ★ Perceptual physics subwoofer + Gemma 4
├── CINEMATOGRAPHY_ENGINE.html     12-beat B-roll system + GameShark debug
├── AVATAR_AGENT_v1.html           Digital identity / face forge
├── labyrinth_explorer.py          Terminal-based procedural renderer
├── delta_finder.py                Auto-scans research gaps (38 principles)
├── onshape_bridge.py              Onshape CAD → STL sync
├── onshape_pull_agent.py          Autonomous CAD pull agent
├── image_inspector.py             Offline image metadata + color analysis
├── trench_training_kaggle.py      35K sample generator (color + VP + BRDF)
├── *.md                           Domain frameworks (8 engineering domains)
└── KAGGLE_SUBMISSION_WRITEUP.md   Hackathon submission document
```

---

## 🏆 Competition Tracks

| Track | Fit |
|-------|-----|
| **Digital Equity & Inclusivity** | Single-file HTML, zero cost, any device, offline-capable |
| **Ollama** | Gemma 4 2B running locally via Ollama for design assistance |
| **Future of Education** | Interactive physics, construction, and rendering education |
| **Global Resilience** | Topography survey + disaster-resilient building design |
| **llama.cpp** | Resource-constrained hardware deployment possible |

---

## 🔬 Technical Depth

**Rendering pipeline:** 3 distance-field systems (smoothstep thermal, inverse-square EM, exponential caustic), ACES tone mapping, PCF soft shadows, UnrealBloom post-processing, film grain shader, god rays, SSAO.

**Physics:** Electrodynamic cone response (frequency→displacement→thermal→EM→caustic chain), mechanical physics engine (inertia/damping/torque), Procedural terrain with height-field deformation.

**AI:** Local Gemma 4 2B inference via Ollama API, scene-state-aware prompting, streaming response handling with graceful fallback.

**Domains:** 8 engineering domains documented with convergence framework — Rendering, EM Systems, Industrial Machinery, Architectural Engineering, Cinematography, Emulation, GameShark/Creative Mode, Sentai Streetwear.

---

## 📜 License

MIT — the tools to design our world should belong to everyone.

---

*Built for the Gemma 4 Good Hackathon 2026 by DaShawn / Guinea Pig Trench LLC*
