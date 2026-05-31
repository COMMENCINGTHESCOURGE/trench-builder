// trench-builder/src/bridge/HyperpolyBridge.ts
import { TerrainEngine, MaterialTensor } from 'hyperpoly-terrain';
import { Scene, Mesh, WebGLRenderer, BufferGeometry, Float32BufferAttribute, Uint8BufferAttribute, ShaderMaterial } from 'three';
import * as THREE from 'three';

export class HyperpolyBridge {
  private engine: TerrainEngine;
  private mesh: Mesh;
  private scene: Scene;

  constructor(scene: Scene, config: { resolution: number }) {
    this.scene = scene;
    this.engine = new TerrainEngine({
      resolution: config.resolution,
      channels: ['rock', 'soil', 'sand', 'water', 'ice', 'organic'],
      conservationEnforced: true
    });
  }

  async initialize(heightmap: Float32Array, materials: Record<string, Float32Array>) {
    // Convert heightmap + materials to 6-channel tensor
    const tensor = MaterialTensor.compose({
      elevation: heightmap,
      ...materials // { rock: ..., soil: ..., etc. }
    });

    await this.engine.initialize(tensor);
    this.mesh = this.createThreeMesh();
    this.scene.add(this.mesh);
  }

  private createThreeMesh(): Mesh {
    // Minimal bridge: extract vertices + normals + material indices
    const { vertices, normals, materialIds } = this.engine.extractMesh({ lod: 1.0 });
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setAttribute('materialId', new THREE.Uint8BufferAttribute(materialIds, 1));
    
    // Use custom shader for material-aware rendering
    const material = new THREE.ShaderMaterial({
      vertexShader: document.getElementById('hyperpoly-vertex')?.textContent || '',
      fragmentShader: document.getElementById('hyperpoly-fragment')?.textContent || '',
      uniforms: {
        materialPalette: { value: this.engine.getMaterialPalette() }
      }
    });
    
    return new THREE.Mesh(geometry, material);
  }

  step(deltaTime: number) {
    // Run simulation + auto-sync mesh if topology changed
    const changed = this.engine.step(deltaTime);
    if (changed) {
      const { vertices, normals, materialIds } = this.engine.extractMesh({ lod: 1.0 });
      this.mesh.geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
      this.mesh.geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
      this.mesh.geometry.setAttribute('materialId', new THREE.Uint8BufferAttribute(materialIds, 1));
      this.mesh.geometry.attributes.position.needsUpdate = true;
    }
  }

  // Hook for CHROMA progression: trigger on geological events
  onEvent(event: 'erosion' | 'deposition' | 'collision', callback: (data: any) => void) {
    this.engine.addEventListener(event, callback);
  }

  dispose() {
    this.scene.remove(this.mesh);
    this.mesh.geometry.dispose();
    this.engine.dispose();
  }
}
