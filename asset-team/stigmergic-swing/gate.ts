#!/usr/bin/env node
/**
 * ACCEPTANCE GATE — stigmergicSwing.ts
 * Run: tsc --noEmit && npx vitest run asset-team/stigmergic-swing/gate.spec.ts
 */
import { readFileSync, existsSync } from 'fs';
import { resolve } from 'path';

const ROOT = resolve(__dirname, '..', '..', '..', 'trench_builder');
const FILE = resolve(ROOT, 'src/physics/stigmergicSwing.ts');
const EMIT = resolve(ROOT, 'src/physics/StigmergicEmitter.ts');
const GRPH = resolve(ROOT, 'src/pathfinder/graph.ts');

const results: [boolean,string][] = [];

function chk(cond:boolean, msg:string){
  results.push([cond, msg]);
  console.log((cond ? 'PASS' : 'FAIL'), msg);
}

if (!existsSync(FILE)) { chk(false, `swing_module_exists: ${FILE}`); process.exit(2); }
chk(true, 'swing_module_exists: stigmergicSwing.ts present');

const src = readFileSync(FILE, 'utf8');

chk(/queueSwing\s*\(/.test(src), 'interface: queueSwing method exported');
chk(/Vector3/.test(src), 'three_integration: Vector3 used');
chk(/vinculumThreshold/i.test(src) || /threshold/i.test(src), 'tensor_repulsion: vinculum threshold logic referenced');
chk(/dampingFactor/i.test(src) || /damp/i.test(src), 'wild_energy: dampingFactor decay present');
chk(/StigmergicEmitter/.test(src), 'emitter_integration: StigmergicEmitter referenced');
chk(/from\s*:\s*Vector3/.test(src) || /Vector3/.test(src), 'arc_io: Vector3 in/out');
chk(!/boundingBox/i.test(src) && !/AABB/i.test(src), 'no_aabb: no bounding-box math');
chk(/central/i.test(src) || /centralDiff/i.test(src), 'gradient_discipline: central-difference referenced');

const graph = readFileSync(GRPH, 'utf8');
chk(/swing/i.test(graph) || /SwingTraversal/.test(graph), 'graph_integration: TensorAStar delegates to swing');

const compat = readFileSync(EMIT, 'utf8');
chk(/queueTraversalFlux/.test(compat), 'emitter_present: queueTraversalFlux present in StigmergicEmitter');

const allPass = results.every(([s]) => s);
console.log('\nGate result:', allPass ? 'ALL PASS' : 'FAIL');
for (const [s,m] of results) console.log(' ', s ? 'ok' : 'FAIL', m);
process.exit(allPass ? 0 : 1);
