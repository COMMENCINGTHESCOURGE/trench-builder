TITLE: Wild-Hermes Swinger — Stigmergic Traversal Physics Module
TYPE: TypeScript physics / AI locomotion asset
ENGINE: Three.js + flux-chamber substrate (trench_builder)
PHASE: Beta Demo (promotional slice — visible demo of agent swarmscape)
DIMENSIONS: 1 swing module file, 2 integration touchpoints, extensible to N agents
INPUTS:
  - trench_builder/src/physics/StigmergicEmitter.ts (existing, mocked)
  - trench_builder/src/pathfinder/graph.ts (scaffolding A*)
  - three Vector3
OUTPUTS:
  - trench_builder/src/physics/stigmergicSwing.ts
  - Modified StigmergicEmitter + TensorAStar integration
PROMPT:
  Implement a wild-mode swinging traversal mechanic for Hermes MANIFOLD
  agents in trench_builder. Each agent moves between tensor-field anchor
  nodes by deterministic pendulum arcs. Physics: no bounding-box collision;
  collisions are handled by tensor repulsion via vinculum threshold breach.
  Gradients are central-difference only. Agents queue traversal flux through
  StigmergicEmitter (mocked CRDT) so their passage erodes density and deposits
  cohesion in the wake — stigmergic memory. Integrate into the existing
  TensorAStar graph so A* fallback activates when no valid swing arc exists
  within energy budget. Wild mode: agents spend momentum freely; energy
  decays by dampingFactor per arc. No WGSL atomics; this is TS-side only.

ACCEPTANCE:
  ✅ fileExists: src/physics/stigmergicSwing.ts compiles under vitest (tsc --noEmit)
  ✅ interfaceMatch: exports a class with method queueSwing(from, to) returning Vector3[]
  ✅ queueTraversalFlux: calls StigmergicEmitter.queueTraversalFlux per midpoint voxel
  ✅ tensorRepulsion: uses vinculumThreshold (provided or default 0.75) to detect breach
  ✅ noAABBs: no bounding-box math; all constraint from tensor field
  ✅ wildEnergy: energy decays via dampingFactor; negative energy triggers coast
  ✅ graphIntegration: TensorAStar.findPath delegates to swing when arc viable
  ✅ mockCompat: StigmergicEmitter mocked get/setDensity calls don't throw
  ❗ PARTIAL: no live tensor field consumer wired in this demo — real flux requires hyperpoly-terrain bridge pass-through

VINCULUM CHECK:
  - hit: PHYSICS [no bounding boxes, collision = tensor repulsion via vinculum threshold breach, central-difference gradients only]
  - hit: TG coupling via StigmergicEmitter.batchQueue
  - hit: GRAPH-INTEGRATION: TensorAStar is gateway-node aware via swing fallback
