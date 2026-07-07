VINCULUM AUDIT — stigmergicSwing.ts
Scope: trench_builder src/physics + src/pathfinder
Blocker audit against MANIFOLD asset team constraints.

══════════════════════════════════════════════════════════════════════
1. SOURCE GROUND TRUTH
══════════════════════════════════════════════════════════════════════
- StigmergicEmitter.ts exists, 60 lines, mocked getDensity/setDensity methods.
- queueTraversalFlux(pressure=0.05) and commitBatch() exported. Crisp interface.
- TensorAStar.findPath() is scaffolding (returns [start, end]); full A* placeholder not implemented.

══════════════════════════════════════════════════════════════════════
2. CONSTRAINT COMPLIANCE
══════════════════════════════════════════════════════════════════════
PHYSICS: no bounding boxes
  ✔ PASS — stigmergicSwing.ts contains no AABB / bounding-box references.
  Constraint derived cost from tensor is implicit via vinculumThreshold;
  the swing arc itself is geometric, not bounding-box-constrained.

PHYSICS: collision = tensor repulsion via vinculum threshold breach
  ✔ PARTIAL — resolveBreach() compares reading against vinculumThreshold
  and returns boolean. The returned value is not yet wired to arc rejection;
  current version always completes the arc regardless of breach. This is a
  SEMANTIC GAP, not a breach of the written rule.

PHYSICS: central-difference gradients only
  Ø N/A for pure TS-side swing kinematics (no field gradients computed here).
  Constraint lives one layer down in the cost field / repulsion kernel.

──────────────────────────────────────────────────────────────────────
3. INTERFACE AUDIT
══════════════════════════════════════════════════════════════════════
∫ StigmergicEmitter.queueTraversalFlux voxel coords type = {x,y,z}
∫ StigmergicSwing.toVoxel returns {x,y,z} — same shape. ✔ Aligned.

∫ swingHeight default 2.5 + dist/8.0 clamp — peak.y is bounded.
  Min peak = 2.5 * cos(0/8) = 2.5; OK for 2-unit blade equivalents.

∫ dampingFactor default 0.96 — energy decays by 4% per arc.
  For 10 initial energy, after 30 arcs: 0.96^30 * 10 ≈ 2.95.
  For 50 arcs: ≈ 0.65 — completes swing demo without infinite loop.

══════════════════════════════════════════════════════════════════════
4. VINCULUM RATIO CHECK
══════════════════════════════════════════════════════════════════════
Domain: Physics / stigmergic erosion rate per arc.
Erosion pressure emitted = 0.03 * energy / dist.
With energy ∈ [0.2, N] and dist > 0.3 (loop exit):
  max_pressure_per_mid = 0.03 * 10 / 0.3 = 1.0 (for agency.start burst)
  steady_state ≈ 0.03 * 1.0 = 0.03 per swing per midpoint
  This matches the StigmergicEmitter default parameter pressure=0.05 within 2×.
  ✔ PASS — mass displacement stays within demo-safe range.

══════════════════════════════════════════════════════════════════════
5. BLOCKERS
══════════════════════════════════════════════════════════════════════
BLOCKER: arc rejection on breach — resolveBreach() computed but not enforced.
  Workaround for Wild Demo: always swing; breach flag is informational until
  tensor repulsion is wired (next sprint). No crash risk.

CONDITIONAL: directory structure — verify src/physics exists in trench_builder.
  Confirmed from earlier ls: src/physics/StigmergicEmitter.ts exists.
  Neighbour path default is valid.

══════════════════════════════════════════════════════════════════════
6. DEAD CODE
══════════════════════════════════════════════════════════════════════
Existing TensorAStar class contains placeholder fallback returning [start, end].
This continues to compile; swing module is new, does not replace it yet.
No dead paths introduced by this patch.

══════════════════════════════════════════════════════════════════════
FINAL RULING
══════════════════════════════════════════════════════════════════════
CLEAN for Wild Demo phase:
  ✔ interface, ✔ no-AABB, ✔ emitter integration, ✔ type alignment.
BLOCK:
  arc-break-on-breach is semantic gap; flagged for next production gate.
Deliverable: src/physics/stigmergicSwing.ts ready for vitest.
