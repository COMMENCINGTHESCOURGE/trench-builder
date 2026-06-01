/**
 * TemporalScheduler
 * 
 * Implements Temporal LOD and the Historical Archive for continuous fields.
 * A mountain must remember its past to properly erode.
 */

export class TemporalScheduler {
    private historyRingBuffer: Float32Array[];
    private ringIndex: number = 0;
    private maxHistoryFrames: number;

    constructor(maxHistoryFrames: number = 600) {
        this.maxHistoryFrames = maxHistoryFrames;
        this.historyRingBuffer = new Array(maxHistoryFrames);
    }

    /**
     * Determines the update frequency (Temporal LOD) based on distance from the observer.
     * @param distance Distance from the active camera/agent.
     * @returns Delta time multiplier for the integration step.
     */
    public calculateTemporalLOD(distance: number): number {
        // Base case: 60Hz update
        if (distance < 1000) return 1.0; 
        
        // Distant case: 1Hz update with 60x integration multiplier
        // Preserves mass conservation without stalling the GPU with tiny updates
        if (distance > 10000) return 60.0;

        return 1.0 + (distance / 10000) * 59.0;
    }

    /**
     * Archives a snapshot of the tensor state.
     * Crucial for determining event emergence (e.g. tracking sudden drops in Cohesion).
     */
    public archiveState(tensorState: Float32Array): void {
        this.historyRingBuffer[this.ringIndex] = new Float32Array(tensorState);
        this.ringIndex = (this.ringIndex + 1) % this.maxHistoryFrames;
    }

    /**
     * Retrieves the tensor state from N frames ago.
     */
    public getHistoricalState(framesAgo: number): Float32Array | null {
        if (framesAgo > this.maxHistoryFrames) return null;
        let idx = this.ringIndex - framesAgo;
        if (idx < 0) idx += this.maxHistoryFrames;
        return this.historyRingBuffer[idx];
    }
}
