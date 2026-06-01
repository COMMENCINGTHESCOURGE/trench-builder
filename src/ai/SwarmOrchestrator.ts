// trench-builder/src/ai/SwarmOrchestrator.ts
import { VoidWalkerAI } from './VoidWalkerAI';

export class SwarmOrchestrator {
    private agents: VoidWalkerAI[] = [];
    private readonly SWARM_SIZE = 5;

    public async igniteSwarm(): Promise<void> {
        console.log(`[SwarmOrchestrator] Igniting swarm of ${this.SWARM_SIZE} VoidWalkers...`);
        for (let i = 0; i < this.SWARM_SIZE; i++) {
            const agent = new VoidWalkerAI();
            await agent.initialize();
            this.agents.push(agent);
        }
        console.log(`[SwarmOrchestrator] Swarm active and awaiting spatial tensors.`);
    }

    /**
     * Parallel execution of the ONNX pathfinders across the swarm.
     */
    public async evaluateSwarm(terrainTensorData: Float32Array): Promise<{x: number, y: number, z: number}[]> {
        const pathPromises = this.agents.map(agent => agent.calculateOptimalPath(terrainTensorData));
        return Promise.all(pathPromises);
    }
}
