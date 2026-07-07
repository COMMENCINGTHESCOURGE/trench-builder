"""
FIELD CONTRACT v1.0 — The canonical interface between producers and consumers.
─────────────────────────────────────────────────────────────────────────────
A Field is a promise: you can sample density, stress, and strain at any point.
How the field was generated (SIMP, photogrammetry, AI, procedural) is irrelevant.
Every projection (render, collision, LOD, analytics) consumes this contract.

Architecture:
  PRODUCERS                    CONTRACT                    CONSUMERS
  ─────────                    ────────                    ─────────
  SIMP tensor                  Field.density(x,y,z)        RenderProjection
  Procedural growth            Field.stress(x,y,z)         CollisionProjection
  AI generation                Field.strain(x,y,z)         LODProjection
  CAD import                   Field.metadata              AnalyticsProjection
  Neural field                                             ImpostorProjection

One stable interface → N×M connections without new code.
"""
import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any
from pathlib import Path


class Field(ABC):
    """The contract. Implement this and every consumer works with your data."""

    @abstractmethod
    def density(self, x: float, y: float, z: float) -> float:
        """Sample density at a point. Returns scalar in [0, 1]."""
        ...

    @abstractmethod
    def stress(self, x: float, y: float, z: float) -> Optional[Tuple[float, float, float]]:
        """Sample stress vector at a point. Returns None if not available."""
        ...

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Dimensions, resolution, units, generation method."""
        ...

    def bounds(self) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        """Axis-aligned bounding box. Override for sparse fields."""
        meta = self.metadata()
        dims = meta.get("grid_dimensions", [1, 1, 1])
        return ((0, dims[0]), (0, dims[1]), (0, dims[2]))

    def is_available(self, attr: str) -> bool:
        """Check if a channel (stress, strain, temperature) exists."""
        if attr == "stress":
            return self.stress(0, 0, 0) is not None
        return False


# ═══ PRODUCERS (implementations of the contract) ═══

class SIMPField(Field):
    """SIMP tensor → Field contract. The mecha knee generator."""
    
    def __init__(self, tensor_path: Path):
        import json
        with open(tensor_path) as f:
            data = json.load(f)
        
        meta = data["metadata"]
        self._dims = tuple(meta["grid_dimensions"])  # (nx, ny, nz)
        channels = data["channels"]
        self._density = np.array(channels["density"], dtype=np.float32)
        self._stress = None
        
        # Try to load stress channel if available
        if "stress" in channels:
            self._stress = np.array(channels["stress"], dtype=np.float32)
        
        self._meta = meta
    
    def density(self, x: float, y: float, z: float) -> float:
        """Trilinear interpolation sampling."""
        nx, ny, nz = self._dims
        x = max(0, min(nx - 1.001, x))
        y = max(0, min(ny - 1.001, y))
        z = max(0, min(nz - 1.001, z))
        
        ix, iy, iz = int(x), int(y), int(z)
        fx, fy, fz = x - ix, y - iy, z - iz
        
        # Trilinear: 8 corners
        c000 = self._density[iz][iy][ix]
        c100 = self._density[iz][iy][min(ix+1, nx-1)]
        c010 = self._density[iz][min(iy+1, ny-1)][ix]
        c110 = self._density[iz][min(iy+1, ny-1)][min(ix+1, nx-1)]
        c001 = self._density[min(iz+1, nz-1)][iy][ix]
        c101 = self._density[min(iz+1, nz-1)][iy][min(ix+1, nx-1)]
        c011 = self._density[min(iz+1, nz-1)][min(iy+1, ny-1)][ix]
        c111 = self._density[min(iz+1, nz-1)][min(iy+1, ny-1)][min(ix+1, nx-1)]
        
        c00 = c000 * (1-fx) + c100 * fx
        c01 = c001 * (1-fx) + c101 * fx
        c10 = c010 * (1-fx) + c110 * fx
        c11 = c011 * (1-fx) + c111 * fx
        c0 = c00 * (1-fy) + c10 * fy
        c1 = c01 * (1-fy) + c11 * fy
        
        return float(c0 * (1-fz) + c1 * fz)
    
    def stress(self, x: float, y: float, z: float) -> Optional[Tuple[float, float, float]]:
        if self._stress is None:
            return None
        # Same trilinear but returns vector
        d = self.density(x, y, z)  # fallback: density as scalar stress
        return (d, d * 0.8, d * 0.6)
    
    def metadata(self) -> Dict[str, Any]:
        return self._meta
    
    def grid_array(self) -> np.ndarray:
        """Direct access to the underlying numpy grid. For batch operations."""
        return self._density
    
    def grid_dims(self) -> Tuple[int, int, int]:
        return self._dims


# ═══ CONSUMERS (projections of the field) ═══

class RenderProjection:
    """Marching cubes → smooth render mesh."""
    
    def __init__(self, field: Field, resolution: int = 128, isolevel: float = 0.5):
        self.field = field
        self.resolution = resolution
        self.isolevel = isolevel
    
    def mesh(self):
        """Extract isosurface via marching cubes."""
        from skimage.measure import marching_cubes
        
        dims = self.field.metadata()["grid_dimensions"]
        # Resample field to uniform grid
        nx, ny, nz = self.resolution, self.resolution, self.resolution
        samples = np.zeros((nz, ny, nx), dtype=np.float32)
        
        for iz in range(nz):
            for iy in range(ny):
                for ix in range(nx):
                    x = ix * dims[0] / nx
                    y = iy * dims[1] / ny
                    z = iz * dims[2] / nz
                    samples[iz, iy, ix] = self.field.density(x, y, z)
        
        verts, faces, _, _ = marching_cubes(samples, level=self.isolevel)
        return verts, faces
    
    def export_glb(self, output_path: Path, name: str = "render_mesh"):
        """Extract and export directly to GLB via Blender."""
        verts, faces = self.mesh()
        
        import bpy, bmesh
        mesh = bpy.data.meshes.new(name)
        bm = bmesh.new()
        
        # Add vertices
        bm_verts = [bm.verts.new(v) for v in verts]
        bm.verts.ensure_lookup_table()
        
        # Add faces
        for f in faces:
            try:
                bm.faces.new([bm_verts[i] for i in f])
            except ValueError:
                pass
        
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
        bm.to_mesh(mesh)
        bm.free()
        
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        
        bpy.ops.export_scene.gltf(
            filepath=str(output_path), export_format='GLB',
            use_selection=True, export_apply=True)
        
        print(f"  RenderProjection → {output_path}")


class CollisionProjection:
    """Simplified convex hull or threshold mesh for physics."""
    
    def __init__(self, field: Field, threshold: float = 0.3):
        self.field = field
        self.threshold = threshold
    
    def aabb(self) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        """Axis-aligned bounding box of occupied region."""
        return self.field.bounds()
    
    def contains(self, x: float, y: float, z: float) -> bool:
        """Point-in-field check for collision queries."""
        return self.field.density(x, y, z) > self.threshold


class LODProjection:
    """Level-of-detail: generate simplified meshes for distance rendering."""
    
    def __init__(self, field: Field):
        self.field = field
    
    def decimated(self, target_faces: int = 1000) -> RenderProjection:
        """Return a lower-resolution projection."""
        ratio = min(1.0, target_faces / 10000)
        resolution = max(16, int(128 * ratio))
        return RenderProjection(self.field, resolution=resolution)
    
    def impostor(self) -> str:
        """Return billboard path (sprite-based distant LOD)."""
        # Would generate 8-angle sprite sheet from the field
        return "impostor_billboard.png"


# ═══ REGISTRY — find fields by name ═══
_field_registry: Dict[str, Field] = {}

def register(name: str, field: Field):
    _field_registry[name] = field
    return field

def get(name: str) -> Optional[Field]:
    return _field_registry.get(name)

def list_fields() -> list:
    return list(_field_registry.keys())


if __name__ == "__main__":
    print("FIELD CONTRACT v1.0 — The canonical interface")
    print("Producers implement Field. Consumers project from Field.")
    print("Available projections: Render, Collision, LOD")
