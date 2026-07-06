# MANIFOLD ARCHITECTURE — IP & TECHNICAL RECORD

**Owner:** Dashawn McLaughlin, Guinea Pig Trench LLC (PA Domestic LLC #13674084)
**Project:** AURORA / MANIFOLD 6-Channel Voxel Engine (`fractype`, `trench_builder`)
**Record opened:** 2026-07-05
**Status:** Living document — append new deltas and corrections as sessions close.

---

## 1. Purpose

This document is the authoritative technical record of the MANIFOLD architecture's
distinguishing engineering decisions — the "moat" — plus a running log of corrective
decisions made during development. It exists to establish a dated, specific paper trail
of original design choices for IP purposes, independent of any single engine's output
(Claude / Gemini / Perplexity), consistent with the three-engine pipeline standard.

---

## 2. The Architectural Moat — Four Deltas

MANIFOLD is defined against the current state of the art (Voxel Farm, Media Molecule's
Dreams, Nanite) by four specific, mechanical differences. These are not marketing claims —
each is a concrete implementation choice with a measurable tradeoff.

### 2.1 State Authority: Local VRAM vs. Network/CPU Sync
Conventional voxel MMOs (Voxel Farm-class engines) are bound by network round-trips and
CPU-side authority for world state — every edit has to reconcile against a server or a
CPU-held master copy. MANIFOLD's state authority lives entirely on the GPU, bound only by
local VRAM allocation. There is no CPU/network reconciliation step in the edit loop.

### 2.2 Boolean CSG vs. Vinculum Strain
Dreams and comparable sculpting engines represent space via boolean CSG operations —
addition and subtraction of primitive volumes. MANIFOLD's Vinculums instead evaluate
continuous thermodynamic *strain* fields (e.g., Oxidation vs. Cohesion channels), not
boolean set operations. This is a categorical difference in representation, not a
performance optimization of the same idea.

### 2.3 Topological Integrity: QEF Extraction vs. Gaussian Splatting
Gaussian Splatting produces an optical illusion of geometry — a point cloud rendered to
look solid, with no underlying topology. MANIFOLD uses Quadratic Error Function (QEF)
dual contouring to extract watertight, structurally sound collision meshes in a single
pass. The output is real geometry, not a view-dependent approximation.

### 2.4 The Hardware Tax: 24-Byte Semantic Cell
Traditional sparse voxel representations optimize for memory efficiency, often at ~1 byte
per cell. MANIFOLD deliberately spends 24 bytes per cell to store a dense 6-Channel
Tensor. This is a conscious trade of raw geometric scale for deep, per-cell systemic
physics — the tax is the point, not a cost to be optimized away.

---

## 3. Corrective Decision Log

### 3.1 `fractype/game/index.html` — Physics/Render Desync Fix
**Problem:** The WebGPU compute pipeline generated a dual-contoured mesh from the QEF
solver, but the CPU-side physics/camera height was computed against a fake `Math.sin()`
plane — two disconnected realities.

**Decision:** Read the QEF vertex buffer (≈199MB) back from GPU to CPU exactly once, at
initialization, into a local `Float32Array`, and use it for exact collision coordinates.

**Governing rule:** Patch vi — Zero Host-GPU Synchronization. A single startup read
respects this: it avoids per-frame GPU stalls while still rooting physics in the actual
simulation output rather than an approximation. The player now collides with the literal
output of the tensor field, not a stand-in.

### 3.2 `trench_builder/lit_server.py` — Payload Serialization Fix
**Problem:** Initial API attempted to serialize heavy multidimensional float data as JSON,
which would fail/crash WebGPU clients on parse at scale.

**Misstep (flagged and corrected):** Initial attempt violated Patch xix — the Intrinsic
Capacity Doctrine — by trying to outsource the payload engineering to a third-party
prompt (Lightning AI) instead of solving it directly.

**Decision:** Replaced JSON with native `numpy.tobytes()` binary serialization wrapped in
Base64, with the `(Batch, 6, 16, 16, 16)` tensor shape hardcoded into both server and
client. This is a bespoke transport layer built specifically for the 6-Channel `.mft`
format — not a generic placeholder.

---

## 4. Append Log

*Add new entries below with date, file, problem, decision, and governing rule/patch as
each session closes.*

- **2026-07-05** — Initial record created; Sections 2 and 3 above established.

---

## 5. Session Close Checklist (per Standard Protocol)

- [ ] Download all `.docx`/`.md` deliverables from this session
- [ ] Download build scripts worth keeping (`index.html`, `lit_server.py`, `lit_client.py`)
- [ ] Confirm this IP record reflects the session's final decisions, not intermediate ones
- [ ] Note anything pending for next session below

**Pending for next session:** Connect WebGPU front-end to the LitServe API endpoint.
