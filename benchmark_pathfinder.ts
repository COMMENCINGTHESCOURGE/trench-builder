// trench-builder/benchmark_pathfinder.ts

import { Vector3 } from 'three';
import { TensorCostField } from './src/pathfinder/cost_field';
import { TensorAStar } from './src/pathfinder/graph';
import { MaterialTensor } from 'hyperpoly-terrain'; // Mock dependency

async function runBenchmark() {
    console.log("--- Tensor-Aware Pathfinder Benchmark ---");
    
    // 1. Mock the 6-channel tensor
    const resolution = 512;
    // (Assuming a mock creation here for testing)
    const mockTensor = new MaterialTensor({
        resolution,
        channels: ['rock', 'soil', 'sand', 'water', 'ice', 'organic']
    });

    const costField = new TensorCostField(mockTensor, resolution);
    const pathfinder = new TensorAStar(costField, resolution);

    const start = new Vector3(10, 50, 10);
    const end = new Vector3(500, 20, 500);

    const t0 = performance.now();
    const path = pathfinder.findPath(start, end, { maxIncline: 45, canSwim: false });
    const t1 = performance.now();

    const extractionTime = (t1 - t0).toFixed(2);
    console.log(`Path Query Time (Distance: ~700 units): ${extractionTime}ms`);
    
    if (parseFloat(extractionTime) > 3.0) {
        console.warn("⚠️ Target failed: Path query took longer than 3ms.");
    } else {
        console.log("✅ Target passed: Path query < 3ms.");
    }
}

runBenchmark();
