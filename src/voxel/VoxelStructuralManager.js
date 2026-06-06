/**
 * GOVERNOR: structural load + hydraulic erosion for voxel terrain.
 * consumed by:
 *   - `src/bridge/HyperpolyBridge.ts` via `engine.initialize(tensor)`
 *   - Phase5 extractor via `channelBuffers[5]` (cohesion) + `channelBuffers[0]` (density)
 */
export class VoxelStructuralManager {
  constructor({ device, chunkSize = 32 } = {}) {
    this.device = device;
    this.chunkSize = chunkSize;
    this.chunks = new Map();
    this.pipeline = null;
    this.bindGroupLayout = null;
  }

  initializeComputeShaders() {
    if (!this.device) return;
    const shader = `
      struct Params { chunk: u32, size: u32, padA: u32, padB: u32 };
      @group(0) @binding(0) var<storage,read> voxels: array<u32>;
      @group(0) @binding(1) var<storage,read_write> stress: array<f32>;
      @group(0) @binding(2) var<uniform> p: Params;

      fn idx(x: u32, y: u32, z: u32) -> u32 {
        return x + y * p.size + z * p.size * p.size;
      }

      @compute @workgroup_size(8, 8, 8)
      fn main(@builtin(global_invocation_id) gid: vec3u) {
        if (gid.x >= p.size || gid.y >= p.size || gid.z >= p.size) { return; }
        let cell = idx(gid.x, gid.y, gid.z);
        let above = idx(gid.x, gid.y + 1u, gid.z);
        let load = select(0.0, 9.81, voxels[above] > 0u);
        let lateral = select(0.0, 0.35, voxels[idx(gid.x+1u,gid.y,gid.z)] > 0u)
                     + select(0.0, 0.35, voxels[idx(gid.x-1u,gid.y,gid.z)] > 0u);
        stress[cell] = load + lateral;
      }
    `;
    const module = this.device.createShaderModule({ code: shader });
    this.bindGroupLayout = this.device.createBindGroupLayout({
      entries: [
        { binding: 0, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'read-only-storage' } },
        { binding: 1, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'storage' } },
        { binding: 2, visibility: GPUShaderStage.COMPUTE, buffer: { type: 'uniform' } },
      ],
    });
    this.pipeline = this.device.createComputePipeline({
      layout: this.device.createPipelineLayout({ bindGroupLayouts: [this.bindGroupLayout] }),
      compute: { module, entryPoint: 'main' },
    });
  }

  createChunk(chunkX, chunkY, chunkZ) {
    const key = `${chunkX},${chunkY},${chunkZ}`;
    if (this.chunks.has(key)) return key;
    const n = this.chunkSize ** 3;
    const voxBuf = this.device.createBuffer({
      size: n * 4,
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST | GPUBufferUsage.COPY_SRC,
    });
    const stressBuf = this.device.createBuffer({
      size: n * 4,
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST | GPUBufferUsage.COPY_SRC,
    });
    const paramsBuf = this.device.createBuffer({
      size: 16,
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
      mappedAtCreation: true,
    });
    new Uint32Array(paramsBuf.getMappedRange()).set([this.chunks.size, this.chunkSize, 0, 0]);
    paramsBuf.unmap();
    this.chunks.set(key, { voxBuf, stressBuf, paramsBuf });
    this.initializeComputeShaders();
    return key;
  }

  dispatchStress(encoder) {
    if (!this.pipeline) return;
    const pass = encoder.beginComputePass();
    pass.setPipeline(this.pipeline);
    for (const [, c] of this.chunks) {
      pass.setBindGroup(0, this.device.createBindGroup({
        layout: this.bindGroupLayout,
        entries: [
          { binding: 0, resource: { buffer: c.voxBuf } },
          { binding: 1, resource: { buffer: c.stressBuf } },
          { binding: 2, resource: { buffer: c.paramsBuf } },
        ],
      }));
      pass.dispatchWorkgroups(
        Math.ceil(this.chunkSize / 8),
        Math.ceil(this.chunkSize / 8),
        Math.ceil(this.chunkSize / 8),
      );
    }
    pass.end();
  }

  getStressBuffer(chunkKey) {
    return this.chunks.get(chunkKey)?.stressBuf || null;
  }

  destroy() {
    for (const [, c] of this.chunks) {
      c.voxBuf.destroy();
      c.stressBuf.destroy();
      c.paramsBuf.destroy();
    }
    this.chunks.clear();
  }
}
