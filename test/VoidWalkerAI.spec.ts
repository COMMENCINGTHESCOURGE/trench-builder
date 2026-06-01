// trench-builder/test/VoidWalkerAI.spec.ts
import { expect } from 'chai';
import { VoidWalkerAI } from '../src/ai/VoidWalkerAI';

describe('VoidWalker AI (ONNX Neural Engine)', () => {
    it('should gracefully degrade to A* fallback if CDN weights are inaccessible', async () => {
        const ai = new VoidWalkerAI();
        // Override model URL to force a 404 failure
        (ai as any).modelUrl = 'https://cdn.manifold.network/invalid_model.onnx';

        await ai.initialize();
        
        // Mock 6-channel 32x32x32 chunk tensor (196608 floats)
        const mockTensor = new Float32Array(196608).fill(0.5);
        
        const path = await ai.calculateOptimalPath(mockTensor);

        expect(path).to.exist;
        expect(path.x).to.equal(1.0);
        expect(path.z).to.equal(-1.0); // Verifies fallback was hit
    });
});
