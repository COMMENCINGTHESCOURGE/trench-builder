# Contributing to trench-builder

> *"Continuity at scale requires discipline."*

Welcome. `trench-builder` is the proof-layer for the MANIFOLD ecosystem. We integrate the raw GPU physics of `hyperpoly-terrain` into a scalable open world.

## 🧭 Philosophy First
- **Zero host-GPU sync**: Even when streaming chunks, simulation state stays on the GPU.
- **Continuity over assets**: We do not load discrete `.gltf` terrain rocks. We resolve tensors.
- **Budget aware**: Open worlds live or die by their memory budget.

## 🚦 Getting Started
1. `git clone https://github.com/COMMENCINGTHESCOURGE/trench-builder.git`
2. `cd trench-builder && npm install`
3. `npm run dev`
4. Verify chunk generation at `http://localhost:8080`.

## 🎯 Good First Issues

We tag tasks with [`good first issue`](https://github.com/COMMENCINGTHESCOURGE/trench-builder/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). Current priorities:

- **[Performance] Tune chunk prefetch radius:** Adjust the hysteresis loop in `ChunkManager` to prevent micro-stutters during high-speed traversal.
- **[Documentation] Document material passthrough to Three.js:** Map the WebGPU material bindings to the Three.js `MeshStandardMaterial` parameters.
- **[Telemetry] Add frame budget logger:** Expose total VRAM and chunk generation times in the HUD.

## 🔄 Pull Request Guidelines
When opening a PR, you must answer two questions:
1. Does this break zero host-GPU sync?
2. How does this affect chunk streaming latency or VRAM?

## ❓ Stuck? Confused?
Open an issue. Confusion at the intersection of Three.js, WebGPU, and field computation is natural. Help us document it.
