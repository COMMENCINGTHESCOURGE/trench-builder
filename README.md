# trench-builder

> Continuity at scale. Worlds that load, breathe, and persist without discrete asset swaps.

[![WebGPU](https://img.shields.io/badge/WebGPU-enabled-blue)](https://gpuweb.github.io/gpuweb/)
[![Three.js](https://img.shields.io/badge/Three.js-integration-black.svg)](https://threejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**trench-builder** is the open-world integration demo layer of the MANIFOLD field computation system. It scales continuous field simulations into traversable, chunk-streamed environments. Traditional open worlds swap static LOD meshes; `trench-builder` streams continuous material tensors into Three.js geometries, keeping the simulation alive at infinite horizons.

---

## 🌍 The MANIFOLD Open-World Philosophy

Open worlds built on discrete assets suffer from LOD popping and static environments. If you blow up a mountain, you have to swap a mesh and write a custom crater decal. 

In `trench-builder`, the world is a continuous 6-channel material tensor driven by `hyperpoly-terrain`. As chunks load, tensors are extracted into QEF meshes directly on the GPU and passed to the Three.js scene graph. There is no asset popping, only material density refinement. The world is a single, unbroken substrate.

---

## 🖼️ Visual Onboarding

*(Placeholders — replace with actual assets)*

| Visual | Purpose | Status |
|--------|---------|--------|
| ![Chunk Stream](./docs/assets/chunk-streaming.gif) | Chunk streaming with continuous tensor handoff | 🟡 TODO |
| ![Pipeline](./docs/assets/pipeline-manifold-threejs.svg) | Tensor → QEF Mesh → Three.js BufferGeometry | 🟡 TODO |
| ![HUD](./docs/assets/hud-overlay.png) | Telemetry HUD showing async load times and chunk grids | 🟡 TODO |
| ![Performance](./docs/assets/vram-budget.svg) | VRAM budget badge: "64 active chunks @ <1GB VRAM" | 🟡 TODO |

> 💡 **Contributor opportunity**: Help capture these! See [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## 🚀 Quickstart

**Requirements**:
- WebGPU-capable browser
- Node.js 18+

```bash
git clone https://github.com/COMMENCINGTHESCOURGE/trench-builder.git
cd trench-builder
npm install && npm run dev
```

Open `http://localhost:8080` in a WebGPU browser. 

### 🔧 Quick Controls
- `WASD` / `Mouse` — Spectator flight
- `C` — Toggle chunk grid overlay
- `P` — Toggle telemetry / frame budget logger

---

## 🧠 Core Concepts

### Chunk Streaming
Spatial partitioning handles infinite scaling. Tensors are streamed asynchronously; as the camera moves, out-of-bounds chunks sleep while incoming chunks are generated entirely on the GPU.

### MANIFOLD ↔ Three.js Bridge
Tensors are resolved via cohesion-weighted QEF into vertex and index buffers. These are mapped zero-copy to `Three.js BufferGeometry` for rendering.

### Performance Targets
- **Streaming Target:** 12 chunks/sec async generation
- **Memory Ceiling:** <1.5GB VRAM allocation
- **Frame Budget:** 16.6ms (60 FPS minimum)

---

## 🤝 Contribute

Scale introduces sharp edges. `trench-builder` needs your systems architecture skills. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

**Good first issues**:
- [ ] Tune chunk prefetch radius
- [ ] Document material passthrough to Three.js
- [ ] Add frame budget logger to HUD

---

## 📜 License & Ecosystem

MIT © 2026 DaShawn McLaughlin / Guinea Pig Trench LLC  
Part of the **MANIFOLD** ecosystem.
