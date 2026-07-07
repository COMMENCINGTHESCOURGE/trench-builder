#!/usr/bin/env python
"""
optimize_mecha_arm.py — SIMP topology optimization for mecha arm bracket.
Arm pushes/pulls (not bounces like knee). Elbow joint, shoulder fixed.
"""
import sys, json, math, numpy as np
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from simp_voxel_solver import SimpVoxelSolver

class MechaArmSolver(SimpVoxelSolver):
    def __init__(self, nelx, nely, nelz, volfrac, penal=3.0, rmin=1.5, nu=0.3):
        super().__init__(nelx, nely, nelz, volfrac, penal, rmin, nu)
        self.passive_voids = []
        self.passive_solids = []

    def set_passive_regions(self, voids, solids):
        self.passive_voids = np.array(voids, dtype=int)
        self.passive_solids = np.array(solids, dtype=int)
        if len(self.passive_voids) > 0:
            self.x[self.passive_voids] = 1.0e-3
            self.x_phys[self.passive_voids] = 1.0e-3
        if len(self.passive_solids) > 0:
            self.x[self.passive_solids] = 1.0
            self.x_phys[self.passive_solids] = 1.0

def main():
    # Arm is longer (40) and thinner (10×10)
    nelx, nely, nelz = 40, 10, 10
    volfrac = 0.25
    penal = 3.0
    rmin = 3.0
    maxiter = 35
    tol = 0.01

    print("=== MECHA ARM TOPOLOGY OPTIMIZER ===")
    print(f"  Grid: {nelx}x{nely}x{nelz} ({nelx*nely*nelz} voxels)")
    
    solver = MechaArmSolver(nelx, nely, nelz, volfrac, penal, rmin)
    
    # Passive regions: elbow joint at x=30, shoulder mount at x=0-2
    voids, solids = [], []
    elbow_cx, elbow_cy, elbow_cz = 32.0, 5.0, 5.0
    elbow_void_r = 1.8   # elbow pin hole
    elbow_solid_r = 3.0  # elbow socket
    
    for ez in range(nelz):
        for ey in range(nely):
            for ex in range(nelx):
                el = ez * nely * nelx + ey * nelx + ex
                cx, cy, cz = ex + 0.5, ey + 0.5, ez + 0.5
                
                # Shoulder mount: solid at x=0
                if ex <= 1 and 3 <= ey <= 6 and 3 <= ez <= 6:
                    solids.append(el)
                
                # Elbow joint
                dist = math.sqrt((cx - elbow_cx)**2 + (cy - elbow_cy)**2 + (cz - elbow_cz)**2)
                if dist <= elbow_void_r:
                    voids.append(el)
                elif dist <= elbow_solid_r:
                    solids.append(el)
    
    voids = list(set(voids))
    solids = list(set(solids) - set(voids))
    solver.set_passive_regions(voids, solids)
    print(f"  Passive: {len(voids)} voids, {len(solids)} solids")
    
    # BCs: shoulder fixed (x=0), load at elbow (x=32)
    num_nodes = (nelx+1)*(nely+1)*(nelz+1)
    num_dofs = num_nodes * 3
    fixed_dofs = []
    
    def get_node(nx, ny, nz):
        return nx*(nely+1)*(nelz+1) + ny*(nelz+1) + nz
    
    for ez in range(nelz+1):
        for ey in range(nely+1):
            node = get_node(0, ey, ez)
            fixed_dofs.extend([node*3, node*3+1, node*3+2])
    
    fixed_dofs = np.array(fixed_dofs)
    f = np.zeros(num_dofs)
    
    # Push/pull load at elbow center
    for ey in range(4, 7):
        for ez in range(4, 7):
            node = get_node(int(elbow_cx), ey, ez)
            f[node*3] = 15.0  # push force along arm axis
    
    # Run optimization
    print(f"  {'Iter':<6} | {'Compliance':<12} | {'Change':<10}")
    print("-" * 40)
    
    u = None; ce = None
    for it in range(1, maxiter+1):
        K = solver.assemble_stiffness()
        u = solver.solve_fea(K, f, fixed_dofs, use_cg=False)
        compliance, change, ce = solver.optimize_step(u, K)
        print(f"  {it:<6} | {compliance:<12.5f} | {change:<10.5f}")
        if change < tol:
            print(f"  Converged after {it} iterations.")
            break
    
    # Save
    channels = solver.get_stress_and_channels(u, ce)
    manifest = {
        "metadata": {
            "grid_dimensions": [nelx, nely, nelz],
            "load_case": "mecha_arm_push",
            "volume_fraction": volfrac,
            "penalty": penal,
            "filter_radius": rmin,
        },
        "channels": channels
    }
    
    out = Path("../mecha_arm_tensor.json")
    with open(out, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Saved: {out}")

if __name__ == "__main__":
    main()
