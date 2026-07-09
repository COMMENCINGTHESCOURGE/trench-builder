#!/usr/bin/env python
"""
optimize_mecha_knee.py
======================
Applies the Step 3 SIMP Voxel Solver to synthesize the 3D topology of a 
mecha knee joint bracket. Implements passive solid/void regions to form:
  1. Hinge pin hole (passive void)
  2. Hinge pin sleeve (passive solid)
  3. Mount plate bolt holes (passive voids)

Outputs the 6-channel optimized tensor to: mecha_knee_tensor.json
Guinea Pig Trench LLC — June 2026
"""

import sys
import json
import math
import numpy as np
from pathlib import Path

# Add current folder to sys.path to import the base solver
sys.path.append(str(Path(__file__).parent))
from simp_voxel_solver import SimpVoxelSolver, setup_cantilever


class MechaKneeSolver(SimpVoxelSolver):
    def __init__(self, nelx, nely, nelz, volfrac, penal=3.0, rmin=1.5, nu=0.3):
        super().__init__(nelx, nely, nelz, volfrac, penal, rmin, nu)
        self.passive_voids = []
        self.passive_solids = []

    def set_passive_regions(self, voids, solids):
        """Sets element indices for passive solids and voids."""
        self.passive_voids = np.array(voids, dtype=int)
        self.passive_solids = np.array(solids, dtype=int)
        
        # Enforce initial values
        if len(self.passive_voids) > 0:
            self.x[self.passive_voids] = 1.0e-3
            self.x_phys[self.passive_voids] = 1.0e-3
        if len(self.passive_solids) > 0:
            self.x[self.passive_solids] = 1.0
            self.x_phys[self.passive_solids] = 1.0

    def optimize_step(self, u, K):
        """Runs compliance sensitivities and updates densities, enforcing passive constraints."""
        compliance, change, ce = super().optimize_step(u, K)
        
        # Re-enforce passive regions after Optimality Criteria update
        if len(self.passive_voids) > 0:
            self.x[self.passive_voids] = 1.0e-3
            self.x_phys[self.passive_voids] = 1.0e-3
        if len(self.passive_solids) > 0:
            self.x[self.passive_solids] = 1.0
            self.x_phys[self.passive_solids] = 1.0
            
        return compliance, change, ce


def main():
    # Grid dimensions: 30 x 15 x 15 (6,750 voxels)
    nelx, nely, nelz = 30, 15, 15
    volfrac = 0.30  # 30% target density
    penal = 3.0
    rmin = 3.0         # increased from 2.0 to kill checkerboard diagonals (42 non-manifold faults)
    maxiter = 35
    tol = 0.01

    print("=== INITIALIZING MECHA KNEE TOPOLOGY OPTIMIZER ===")
    print(f"  Voxel Grid: {nelx}x{nely}x{nelz} ({nelx * nely * nelz} elements)")
    print(f"  Target Volume Fraction: {volfrac}")
    print()

    solver = MechaKneeSolver(nelx, nely, nelz, volfrac, penal, rmin)

    # 1. Identify Passive Solids and Voids
    voids = []
    solids = []

    # Bolt hole parameters in mount plate (x <= 1)
    bolt_coords = [
        (3.5, 3.5),   # (y, z)
        (11.5, 3.5),
        (3.5, 11.5),
        (11.5, 11.5)
    ]
    bolt_radius = 1.6

    # Hinge pin parameters at right side (x = 26, cylinder along Y axis)
    pin_x, pin_z = 26.0, 7.5
    pin_void_radius = 2.2
    pin_solid_radius = 3.8

    for elz in range(nelz):
        for ely in range(nely):
            for elx in range(nelx):
                el = elz * nely * nelx + ely * nelx + elx
                
                # Check mounting plate bolt holes (x_centroid <= 2.0)
                if elx <= 1:
                    # centroid coords: x = elx + 0.5, y = ely + 0.5, z = elz + 0.5
                    cy, cz = ely + 0.5, elz + 0.5
                    for bx, bz in bolt_coords:
                        dist = math.sqrt((cy - bx)**2 + (cz - bz)**2)
                        if dist <= bolt_radius:
                            voids.append(el)
                            break
                            
                # Check hinge pin hole (void cylinder) and sleeve (solid cylinder) along Y
                cx, cz = elx + 0.5, elz + 0.5
                dist_to_pin = math.sqrt((cx - pin_x)**2 + (cz - pin_z)**2)
                
                if dist_to_pin <= pin_void_radius:
                    voids.append(el)
                elif dist_to_pin <= pin_solid_radius:
                    solids.append(el)

    # Remove duplicates
    voids = list(set(voids))
    solids = list(set(solids) - set(voids))  # solids cannot be voids

    solver.set_passive_regions(voids, solids)
    print(f"  Enforced passive constraints: {len(voids)} void voxels, {len(solids)} solid voxels")

    # 2. Define Boundary Conditions and Loads
    # Fixed nodes at left face x=0
    num_nodes = (nelx + 1) * (nely + 1) * (nelz + 1)
    num_dofs = num_nodes * 3
    fixed_dofs = []
    
    for elz in range(nelz + 1):
        for ely in range(nely + 1):
            node = elz + ely * (nelz + 1)  # node at x=0
            fixed_dofs.extend([node * 3, node * 3 + 1, node * 3 + 2])
            
    fixed_dofs = np.array(fixed_dofs)

    # Forces applied at hinge sleeve center (x=26, z=pin_z, distributed along y=5 to y=9)
    f = np.zeros(num_dofs)
    
    # Helper to map coordinates to node index
    def get_node(nx, ny, nz):
        return nx * (nely + 1) * (nelz + 1) + ny * (nelz + 1) + nz

    # Target nodes along the sleeve interior
    load_nodes = []
    for ny in range(5, 10):
        # Nodes at bottom/sides of the pin void circle (x=26, z=5 to 6)
        n1 = get_node(int(pin_x), ny, int(pin_z - pin_void_radius))
        n2 = get_node(int(pin_x), ny, int(pin_z - 1))
        load_nodes.extend([n1, n2])
        
    load_nodes = list(set(load_nodes))
    
    # Apply distributed load: F_z = -10.0 (bounce weight), F_y = 3.0 (torsional turn force)
    for node in load_nodes:
        # Distributed downward load
        f[node * 3 + 2] = -10.0 / len(load_nodes)
        # Distributed lateral load
        f[node * 3 + 1] = 3.0 / len(load_nodes)

    print(f"  Applied loads at {len(load_nodes)} hinge interface nodes.")
    print()

    # 3. Run Optimization Loop
    print("  Starting Mecha Knee Topology Optimization Loop...")
    print(f"  {'Iter':<6} | {'Compliance':<12} | {'Change':<10}")
    print("-" * 40)

    u = None
    ce = None
    for it in range(1, maxiter + 1):
        K = solver.assemble_stiffness()
        u = solver.solve_fea(K, f, fixed_dofs, use_cg=False)
        compliance, change, ce = solver.optimize_step(u, K)

        print(f"  {it:<6} | {compliance:<12.5f} | {change:<10.5f}")

        if change < tol:
            print(f"  Converged after {it} iterations (change < {tol}).")
            break
    else:
        print("  Reached maximum iterations.")

    print()
    print("  Generating optimized 6-channel material tensor...")
    channels = solver.get_stress_and_channels(u, ce)

    # Prepare output manifest
    manifest = {
        "metadata": {
            "grid_dimensions": [nelx, nely, nelz],
            "load_case": "mecha_knee_joint",
            "volume_fraction": volfrac,
            "penalty": penal,
            "filter_radius": rmin,
            "loss_recovered_mm": 476.0  # From mecha_optimization
        },
        "channels": channels
    }

    # Save to file
    out_path = Path("mecha_knee_tensor.json")
    with open(out_path, "w", encoding="utf-8") as out_file:
        json.dump(manifest, out_file, indent=2)

    print(f"  Successfully exported optimized knee bracket tensor to: {out_path.absolute()}")
    print("=== MECHA KNEE OPTIMIZATION DONE ===")


if __name__ == "__main__":
    main()
