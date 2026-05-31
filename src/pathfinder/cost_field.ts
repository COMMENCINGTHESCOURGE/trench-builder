// trench-builder/src/pathfinder/cost_field.ts

import { MaterialTensor } from 'hyperpoly-terrain';
import { Vector3 } from 'three';

export interface CostField {
    getCost(x: number, y: number, z: number): number;
}

export class TensorCostField implements CostField {
    constructor(private tensor: MaterialTensor, private resolution: number) {}

    /**
     * Translates a 6-channel material tensor into a pathfinding resistance metric.
     * Uses a blended equation prioritizing thermodynamic stability and agent traversal capability.
     */
    getCost(x: number, y: number, z: number): number {
        // Bounds checking
        if (x < 0 || x >= this.resolution || y < 0 || y >= this.resolution || z < 0 || z >= this.resolution) {
            return Infinity; // Impassable boundary
        }

        const data = this.tensor.getDataAt(x, y, z);
        
        const density = data.rock + data.soil + data.sand;
        const viscosity = data.water + data.ice;
        const entropy = data.organic; // Example mapping: organic matter increases traversal entropy/resistance

        // Base traversal cost in empty space
        let baseCost = 1.0;

        // Severe penalty for walking through solid rock (density)
        if (density > 0.8) return Infinity; 

        // Penalty for traversing highly viscous areas (deep mud/water)
        const viscosityPenalty = viscosity * 5.0;

        // Entropy penalty (e.g. dense vegetation)
        const entropyPenalty = entropy * 2.5;

        // Blended thermodynamic resistance
        return baseCost + (density * 10.0) + viscosityPenalty + entropyPenalty;
    }
}
