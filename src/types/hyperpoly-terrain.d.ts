// C:\Users\dasha\.gemini\antigravity-ide\scratch\trench-builder\src\types\hyperpoly-terrain.d.ts

declare module 'hyperpoly-terrain' {
  export interface MaterialData {
    rock: number;
    soil: number;
    sand: number;
    water: number;
    ice: number;
    organic: number;
  }

  export class MaterialTensor {
    constructor(config: {
      resolution: number;
      channels: string[];
    });

    static compose(config: {
      elevation: Float32Array;
      [key: string]: Float32Array;
    }): MaterialTensor;

    getDataAt(x: number, y: number, z: number): MaterialData;
  }

  export class TerrainEngine {
    constructor(config: {
      resolution: number;
      channels: string[];
      conservationEnforced: boolean;
    });

    initialize(tensor: MaterialTensor): Promise<void>;
    extractMesh(config: { lod: number }): {
      vertices: Float32Array;
      normals: Float32Array;
      materialIds: Uint8Array;
    };
    getMaterialPalette(): any;
    step(deltaTime: number): boolean;
    addEventListener(event: string, callback: (data: any) => void): void;
    dispose(): void;
  }
}
