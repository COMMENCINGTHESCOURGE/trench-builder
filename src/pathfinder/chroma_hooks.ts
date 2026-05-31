// trench-builder/src/pathfinder/chroma_hooks.ts

import { Vector3 } from 'three';
import { TensorAStar, PathConstraints } from './graph';

export interface GeologicalEvent {
    type: 'erosion' | 'deposition' | 'collision';
    magnitude: number;
    epicenter: Vector3;
}

export class ChromaProgressionSystem {
    constructor(private pathfinder: TensorAStar) {}

    replanOnEvent(event: GeologicalEvent, currentPath: Vector3[], constraints: PathConstraints): Vector3[] {
        if (event.magnitude < 0.5) {
            // Event is too minor to disrupt path
            return currentPath;
        }

        // Check if the epicenter intersects the current path bounds
        const disrupted = currentPath.some(pt => pt.distanceTo(event.epicenter) < event.magnitude * 10);
        
        if (disrupted) {
            console.log(`[CHROMA] Path disrupted by ${event.type}. Replanning...`);
            // Extrapolate start/end from current progress and replan
            const currentPosition = currentPath[0]; 
            const endPosition = currentPath[currentPath.length - 1];
            return this.pathfinder.findPath(currentPosition, endPosition, constraints);
        }

        return currentPath;
    }

    triggerChromaCheckpoint(milestoneId: string): void {
        console.log(`[CHROMA CHECKPOINT] Milestone unlocked: ${milestoneId}`);
        // Integration point for NOVA HORIZON 3D achievement/narrative system
        // e.g., dispatchEvent(new CustomEvent('chroma-unlocked', { detail: milestoneId }))
    }
}
