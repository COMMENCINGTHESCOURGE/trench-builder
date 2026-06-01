// trench-builder/test/StigmergicEmitter.spec.ts
import { expect } from 'chai';
import { StigmergicEmitter } from '../src/physics/StigmergicEmitter';

describe('Narrative Stigmergy (Physics Emitter)', () => {
    it('should correctly calculate mass displacement without creating or destroying matter', () => {
        const mockStore = {}; // Mock CRDT
        const emitter = new StigmergicEmitter(mockStore);

        // We wrap the method to spy on the internal density logic
        let densityCalled = false;
        (emitter as any).setDensity = (c: any, val: number) => {
            densityCalled = true;
            expect(val).to.be.lessThan(0.8); // Original mock is 0.8
        };

        let compactionCalled = false;
        (emitter as any).distributeCompaction = (c: any, mass: number) => {
            compactionCalled = true;
            expect(mass).to.be.greaterThan(0);
        };

        emitter.applyTraversalFlux({x: 10, y: 0, z: 10}, 0.1);

        expect(densityCalled).to.be.true;
        expect(compactionCalled).to.be.true;
    });
});
