#!/usr/bin/env python
"""
Step 3 Topology Optimization Solver — SIMP Voxel Implementation
==============================================================
Solves compliance minimization under volume constraints on a 3D voxel grid.
Interfaces with the Pangea Principle by exporting a 6-channel material tensor:
  1. density      -> element density field
  2. cohesion     -> von Mises stress / stiffness
  3. permeability -> void paths (1 - density)
  4. water        -> thermal/cooling constraints (distance to boundary)
  5. sediment     -> support structures / overhang limits
  6. oxidation    -> fatigue life / damage accumulation (strain energy density)

Author: Antigravity / Guinea Pig Trench LLC
"""

import sys
import json
import math
import argparse
import numpy as np
from pathlib import Path
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve, cg
from scipy.ndimage import distance_transform_edt


def get_element_stiffness(nu=0.3):
    """
    Computes the 24x24 element stiffness matrix k0 for an 8-node brick element (unit cube).
    Assumes isotropic material with Young's Modulus E=1.0 and Poisson's ratio nu.
    Uses Gauss integration with 8 integration points.
    """
    # Gauss points and weights
    gp = [-1.0 / math.sqrt(3.0), 1.0 / math.sqrt(3.0)]
    w = [1.0, 1.0]

    # Node coordinate offsets for natural coordinates [-1, 1]^3
    # Ordered: (-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
    #          (-1,-1,1),  (1,-1,1),  (1,1,1),  (-1,1,1)
    corners = np.array([
        [-1, -1, -1], [ 1, -1, -1], [ 1,  1, -1], [-1,  1, -1],
        [-1, -1,  1], [ 1, -1,  1], [ 1,  1,  1], [-1,  1,  1]
    ], dtype=float)

    # Elasticity matrix C for isotropic 3D solid
    # Stress vector: [sigma_xx, sigma_yy, sigma_zz, tau_xy, tau_yz, tau_zx]
    fact = 1.0 / ((1.0 + nu) * (1.0 - 2.0 * nu))
    C = np.zeros((6, 6))
    C[0, 0] = C[1, 1] = C[2, 2] = fact * (1.0 - nu)
    C[0, 1] = C[0, 2] = C[1, 0] = C[1, 2] = C[2, 0] = C[2, 1] = fact * nu
    C[3, 3] = C[4, 4] = C[5, 5] = fact * (0.5 - nu)

    k0 = np.zeros((24, 24))

    # Perform numerical integration
    for xi in gp:
        for eta in gp:
            for zeta in gp:
                # Shape function derivatives w.r.t natural coordinates
                dN = np.zeros((8, 3))
                for i in range(8):
                    cx, cy, cz = corners[i]
                    dN[i, 0] = 0.125 * cx * (1.0 + cy * eta) * (1.0 + cz * zeta)
                    dN[i, 1] = 0.125 * cy * (1.0 + cx * xi)  * (1.0 + cz * zeta)
                    dN[i, 2] = 0.125 * cz * (1.0 + cx * xi)  * (1.0 + cy * eta)

                # Physical derivatives (unit cube element has side length h=1.0)
                # Physical coordinates: x = 0.5 * (1 + xi), Jacobian = 0.5 * I, Inverse Jacobian = 2 * I
                dN_dxyz = dN * 2.0

                # Assemble strain-displacement B-matrix
                B = np.zeros((6, 24))
                for i in range(8):
                    col = i * 3
                    # du/dx, dv/dy, dw/dz
                    B[0, col]   = dN_dxyz[i, 0]
                    B[1, col+1] = dN_dxyz[i, 1]
                    B[2, col+2] = dN_dxyz[i, 2]
                    # du/dy + dv/dx
                    B[3, col]   = dN_dxyz[i, 1]
                    B[3, col+1] = dN_dxyz[i, 0]
                    # dv/dz + dw/dy
                    B[4, col+1] = dN_dxyz[i, 2]
                    B[4, col+2] = dN_dxyz[i, 1]
                    # dw/dx + du/dz
                    B[5, col]   = dN_dxyz[i, 2]
                    B[5, col+2] = dN_dxyz[i, 0]

                # Accumulate k0 += B^T * C * B * det(J) * w_x * w_y * w_z
                # det(J) = 0.125 for natural to physical mapping on unit cube
                detJ = 0.125
                k0 += np.dot(B.T, np.dot(C, B)) * detJ * 1.0

    return k0


class SimpVoxelSolver:
    def __init__(self, nelx, nely, nelz, volfrac, penal=3.0, rmin=1.5, nu=0.3):
        self.nelx = nelx
        self.nely = nely
        self.nelz = nelz
        self.volfrac = volfrac
        self.penal = penal
        self.rmin = rmin
        self.nu = nu

        self.nele = nelx * nely * nelz
        self.num_nodes = (nelx + 1) * (nely + 1) * (nelz + 1)
        self.num_dofs = self.num_nodes * 3

        # Elements density
        self.x = np.ones(self.nele) * volfrac
        self.x_phys = np.ones(self.nele) * volfrac

        # Get base element stiffness matrix
        self.k0 = get_element_stiffness(nu=self.nu)

        # Precompute FEA index mapping and sensitivity filter weights
        self._prepare_fea_indices()
        self._prepare_sensitivity_filter()

    def _node_index(self, i, j, k):
        return i * (self.nely + 1) * (self.nelz + 1) + j * (self.nelz + 1) + k

    def _prepare_fea_indices(self):
        """Precomputes the global DOF maps for all elements to accelerate assembly."""
        self.edofMat = np.zeros((self.nele, 24), dtype=int)
        for elz in range(self.nelz):
            for ely in range(self.nely):
                for elx in range(self.nelx):
                    el = elz * self.nely * self.nelx + ely * self.nelx + elx
                    
                    # 8 Node indices of this voxel
                    nodes = [
                        self._node_index(elx,     ely,     elz),
                        self._node_index(elx + 1, ely,     elz),
                        self._node_index(elx + 1, ely + 1, elz),
                        self._node_index(elx,     ely + 1, elz),
                        self._node_index(elx,     ely,     elz + 1),
                        self._node_index(elx + 1, ely,     elz + 1),
                        self._node_index(elx + 1, ely + 1, elz + 1),
                        self._node_index(elx,     ely + 1, elz + 1)
                    ]
                    
                    # Map nodes to DOFs (3 DOFs per node)
                    edofs = []
                    for node in nodes:
                        edofs.extend([node * 3, node * 3 + 1, node * 3 + 2])
                    self.edofMat[el, :] = edofs

        # Replicated indices for sparse matrix construction
        self.iK = np.kron(self.edofMat, np.ones((24, 1))).flatten()
        self.jK = np.kron(self.edofMat, np.ones((1, 24))).flatten()

    def _prepare_sensitivity_filter(self):
        """Computes neighborhood filter weights for mesh-independent filtering."""
        # Calculate centroids of all elements
        centroids = np.zeros((self.nele, 3))
        for elz in range(self.nelz):
            for ely in range(self.nely):
                for elx in range(self.nelx):
                    el = elz * self.nely * self.nelx + ely * self.nelx + elx
                    centroids[el] = [elx + 0.5, ely + 0.5, elz + 0.5]

        # Use bounding boxes to gather close element indices within rmin radius
        H_rows = []
        H_cols = []
        H_vals = []
        
        # Bounding box width
        r_ceil = int(math.ceil(self.rmin))
        
        for elz in range(self.nelz):
            for ely in range(self.nely):
                for elx in range(self.nelx):
                    el = elz * self.nely * self.nelx + ely * self.nelx + elx
                    
                    # Range of search
                    z_min, z_max = max(0, elz - r_ceil), min(self.nelz, elz + r_ceil + 1)
                    y_min, y_max = max(0, ely - r_ceil), min(self.nely, ely + r_ceil + 1)
                    x_min, x_max = max(0, elx - r_ceil), min(self.nelx, elx + r_ceil + 1)
                    
                    for nz in range(z_min, z_max):
                        for ny in range(y_min, y_max):
                            for nx in range(x_min, x_max):
                                n_el = nz * self.nely * self.nelx + ny * self.nelx + nx
                                dist = math.sqrt((elx - nx)**2 + (ely - ny)**2 + (elz - nz)**2)
                                if dist < self.rmin:
                                    weight = self.rmin - dist
                                    H_rows.append(el)
                                    H_cols.append(n_el)
                                    H_vals.append(weight)

        self.H = coo_matrix((H_vals, (H_rows, H_cols)), shape=(self.nele, self.nele)).tocsr()
        self.H_sum = np.array(self.H.sum(axis=1)).flatten()

    def assemble_stiffness(self):
        """Assembles the global stiffness matrix scaled by penalised element densities."""
        E = 1.0e-9 + (self.x_phys ** self.penal) * (1.0 - 1.0e-9)
        # Vectorized data creation
        sK = np.dot(self.k0.flatten().reshape(24*24, 1), E.reshape(1, self.nele)).transpose().flatten()
        K = coo_matrix((sK, (self.iK, self.jK)), shape=(self.num_dofs, self.num_dofs)).tocsr()
        return K

    def solve_fea(self, K, f, fixed_dofs, use_cg=False):
        """Solves K * u = f under fixed degrees of freedom."""
        free_dofs = np.setdiff1d(np.arange(self.num_dofs), fixed_dofs)
        u = np.zeros(self.num_dofs)
        
        # Extract submatrix for free DOFs
        K_free = K[free_dofs, :][:, free_dofs]
        f_free = f[free_dofs]

        if use_cg:
            # Solve using Conjugate Gradient with Jacobi (diagonal) preconditioning
            M_diag = K_free.diagonal()
            M_diag[M_diag == 0] = 1.0
            M = coo_matrix((1.0 / M_diag, (np.arange(len(free_dofs)), np.arange(len(free_dofs))))).tocsr()
            u_free, info = cg(K_free, f_free, M=M, tol=1e-5, maxiter=2000)
            if info != 0:
                # Fallback to direct solve if CG fails or takes too long
                u_free = spsolve(K_free, f_free)
        else:
            # Direct solver
            u_free = spsolve(K_free, f_free)

        u[free_dofs] = u_free
        return u

    def optimize_step(self, u, K):
        """Executes a single SIMP optimization iteration (compliance sensitivity + filtering + OC update)."""
        # Calculate element compliance (u_e^T * k0 * u_e)
        ce = np.zeros(self.nele)
        for el in range(self.nele):
            u_e = u[self.edofMat[el, :]]
            ce[el] = np.dot(u_e, np.dot(self.k0, u_e))

        # Objective compliance
        compliance = np.sum((1.0e-9 + (self.x_phys ** self.penal) * (1.0 - 1.0e-9)) * ce)

        # Compliance sensitivity w.r.t physical densities
        dc = -self.penal * (self.x_phys ** (self.penal - 1.0)) * (1.0 - 1.0e-9) * ce
        dv = np.ones(self.nele)

        # Apply sensitivity filter
        dc = np.array(self.H.dot(dc / self.x_phys) / self.H_sum) * self.x_phys
        dv = np.array(self.H.dot(dv) / self.H_sum)

        # Optimality Criteria (OC) update
        l1, l2 = 0.0, 1.0e9
        move = 0.2
        eta = 0.5
        x_new = np.zeros(self.nele)

        while (l2 - l1) / (l1 + 1.0e-10) > 1.0e-4:
            l_mid = 0.5 * (l1 + l2)
            
            # OC update formula
            ratio = -dc / (dv * l_mid)
            ratio[ratio < 0.0] = 0.0
            x_new = np.maximum(1e-3, np.maximum(self.x - move, np.minimum(1.0, np.minimum(self.x + move, self.x * (ratio ** eta)))))
            
            # Check volume fraction constraint
            if np.mean(x_new) > self.volfrac:
                l1 = l_mid
            else:
                l2 = l_mid

        change = np.max(np.abs(x_new - self.x))
        self.x = x_new
        self.x_phys = x_new  # Simple density filter mapping
        
        return compliance, change, ce

    def get_stress_and_channels(self, u, ce):
        """
        Calculates stress distribution and extracts all 6 tensor channels.
        Returns a dictionary containing the volumetric arrays.
        """
        # Node locations for natural coordinates center (0,0,0)
        corners = np.array([
            [-1, -1, -1], [ 1, -1, -1], [ 1,  1, -1], [-1,  1, -1],
            [-1, -1,  1], [ 1, -1,  1], [ 1,  1,  1], [-1,  1,  1]
        ], dtype=float)

        # Compute strain-displacement matrix B0 at the center (0,0,0) of the element
        # dN_dxi = 0.125 * cx * (1 + cy*eta) * (1 + cz*zeta) -> at (0,0,0) equals 0.125 * cx
        # Since physical derivatives dN_dxyz = 2 * dN_dxi:
        dN_dxyz_center = corners * 0.25 # (8x3)
        
        B0 = np.zeros((6, 24))
        for i in range(8):
            col = i * 3
            B0[0, col]   = dN_dxyz_center[i, 0]
            B0[1, col+1] = dN_dxyz_center[i, 1]
            B0[2, col+2] = dN_dxyz_center[i, 2]
            B0[3, col]   = dN_dxyz_center[i, 1]
            B0[3, col+1] = dN_dxyz_center[i, 0]
            B0[4, col+1] = dN_dxyz_center[i, 2]
            B0[4, col+2] = dN_dxyz_center[i, 1]
            B0[5, col]   = dN_dxyz_center[i, 2]
            B0[5, col+2] = dN_dxyz_center[i, 0]

        fact = 1.0 / ((1.0 + self.nu) * (1.0 - 2.0 * self.nu))
        C = np.zeros((6, 6))
        C[0, 0] = C[1, 1] = C[2, 2] = fact * (1.0 - self.nu)
        C[0, 1] = C[0, 2] = C[1, 0] = C[1, 2] = C[2, 0] = C[2, 1] = fact * self.nu
        C[3, 3] = C[4, 4] = C[5, 5] = fact * (0.5 - self.nu)

        # Compute stresses for each element
        stresses = np.zeros(self.nele)
        for el in range(self.nele):
            u_e = u[self.edofMat[el, :]]
            strain = np.dot(B0, u_e)
            stress_vec = np.dot(C, strain)
            
            # von Mises stress:
            s_xx, s_yy, s_zz, t_xy, t_yz, t_zx = stress_vec
            s_vm = math.sqrt(0.5 * ((s_xx - s_yy)**2 + (s_yy - s_zz)**2 + (s_zz - s_xx)**2 + 6 * (t_xy**2 + t_yz**2 + t_zx**2)))
            stresses[el] = s_vm

        # Reshape physical fields to 3D grid
        density_grid = self.x_phys.reshape((self.nelz, self.nely, self.nelx))
        stress_grid = stresses.reshape((self.nelz, self.nely, self.nelx))
        compliance_grid = ce.reshape((self.nelz, self.nely, self.nelx))

        # Channel 1: Density
        density_channel = density_grid.tolist()

        # Channel 2: Cohesion (normalized stress scaled by density representing stiffness)
        max_stress = np.max(stress_grid) if np.max(stress_grid) > 0 else 1.0
        cohesion_grid = (stress_grid / max_stress) * density_grid
        cohesion_channel = cohesion_grid.tolist()

        # Channel 3: Permeability (1.0 - density representing void paths)
        permeability_grid = 1.0 - density_grid
        permeability_channel = permeability_grid.tolist()

        # Channel 4: Water (distance transform to solid boundary)
        # EDT of solid elements (where density < 0.2 is considered void)
        solid_mask = (density_grid >= 0.2).astype(int)
        water_grid = distance_transform_edt(1 - solid_mask)
        # Normalize distance transform
        max_water = np.max(water_grid) if np.max(water_grid) > 0 else 1.0
        water_grid = water_grid / max_water
        water_channel = water_grid.tolist()

        # Channel 5: Sediment (Overhang risk check against gravity vector -Z)
        # Check density of element below. If density above is high but below is low -> overhang risk!
        sediment_grid = np.zeros_like(density_grid)
        for z in range(1, self.nelz):
            # Risk = max(0, density[z] - density[z-1])
            sediment_grid[z, :, :] = np.maximum(0, density_grid[z, :, :] - density_grid[z-1, :, :])
        # Bottom-most layer suspended elements are also overhangs
        sediment_grid[0, :, :] = density_grid[0, :, :] * (density_grid[0, :, :] < 0.5)
        sediment_channel = sediment_grid.tolist()

        # Channel 6: Oxidation (normalized strain energy density representing fatigue wear)
        max_ce = np.max(compliance_grid) if np.max(compliance_grid) > 0 else 1.0
        oxidation_grid = compliance_grid / max_ce
        oxidation_channel = oxidation_grid.tolist()

        return {
            "density": density_channel,
            "cohesion": cohesion_channel,
            "permeability": permeability_channel,
            "water": water_channel,
            "sediment": sediment_channel,
            "oxidation": oxidation_channel
        }


def setup_cantilever(nelx, nely, nelz):
    """
    Configures a classic 3D cantilever beam setup.
    Fixed at x=0 (entire left face).
    Point load applied downwards at the bottom-center of the right face (x=nelx, y=nely/2, z=0).
    """
    num_nodes = (nelx + 1) * (nely + 1) * (nelz + 1)
    num_dofs = num_nodes * 3

    # Force vector f
    f = np.zeros(num_dofs)
    
    # Boundary nodes (fixed at left face x=0)
    fixed_dofs = []
    for elz in range(nelz + 1):
        for ely in range(nely + 1):
            # Node index at x=0
            node = elz + ely * (nelz + 1)
            fixed_dofs.extend([node * 3, node * 3 + 1, node * 3 + 2])
    
    fixed_dofs = np.array(fixed_dofs)

    # Force load at right face (bottom-center node)
    right_node_y = nely // 2
    right_node_z = 0
    # Node index mapping: node_index = elx * (nely+1)*(nelz+1) + ely * (nelz+1) + elz
    load_node = nelx * (nely + 1) * (nelz + 1) + right_node_y * (nelz + 1) + right_node_z
    
    # Apply force in negative Z direction (direction -Z: DOF = load_node * 3 + 2)
    f[load_node * 3 + 2] = -1.0

    return f, fixed_dofs


def setup_bridge(nelx, nely, nelz):
    """
    Configures a classic 3D bridge/arch setup.
    Fixed at bottom four corners.
    Distributed load applied downwards along the top-middle deck.
    """
    num_nodes = (nelx + 1) * (nely + 1) * (nelz + 1)
    num_dofs = num_nodes * 3

    f = np.zeros(num_dofs)
    fixed_dofs = []

    # Helper function for node index
    def get_node(x, y, z):
        return x * (nely + 1) * (nelz + 1) + y * (nelz + 1) + z

    # Fixed bottom corners (at z=0, y=0 and y=nely, x=0 and x=nelx)
    corners = [
        get_node(0, 0, 0),
        get_node(0, nely, 0),
        get_node(nelx, 0, 0),
        get_node(nelx, nely, 0)
    ]
    for c in corners:
        fixed_dofs.extend([c * 3, c * 3 + 1, c * 3 + 2])
    fixed_dofs = np.array(fixed_dofs)

    # Distributed downward load along top-middle deck (z=nelz, y=nely/2, for all x)
    for x in range(1, nelx):
        node = get_node(x, nely // 2, nelz)
        f[node * 3 + 2] = -1.0 / nelx

    return f, fixed_dofs


def main():
    parser = argparse.ArgumentParser(description="Step 3 SIMP Voxel Topology Optimizer")
    parser.add_argument("--nelx", type=int, default=30, help="Grid size in X")
    parser.add_argument("--nely", type=int, default=15, help="Grid size in Y")
    parser.add_argument("--nelz", type=int, default=15, help="Grid size in Z")
    parser.add_argument("--volfrac", type=float, default=0.4, help="Volume fraction limit")
    parser.add_argument("--penal", type=float, default=3.0, help="SIMP penalty parameter")
    parser.add_argument("--rmin", type=float, default=1.5, help="Filter radius")
    parser.add_argument("--maxiter", type=int, default=30, help="Maximum optimizer iterations")
    parser.add_argument("--tol", type=float, default=0.01, help="Convergence tolerance on density change")
    parser.add_argument("--case", type=str, choices=["cantilever", "bridge"], default="cantilever", help="Load boundary case")
    parser.add_argument("--use-cg", action="store_true", help="Use CG solver instead of direct sparse solver")
    parser.add_argument("--output", type=str, default="soil_tensor_manifest.json", help="Path to write 6-channel JSON")
    args = parser.parse_args()

    print(f"=== STEP 3 SIMP SOLVER INITIALIZATION ===")
    print(f"  Voxel Grid: {args.nelx}x{args.nely}x{args.nelz} ({args.nelx * args.nely * args.nelz} elements)")
    print(f"  Volume Fraction: {args.volfrac} | Penalty: {args.penal} | Filter Radius: {args.rmin}")
    print(f"  Load Case: {args.case} | FEA Solver: {'Conjugate Gradient' if args.use_cg else 'Direct spsolve'}")
    print()

    solver = SimpVoxelSolver(
        nelx=args.nelx, nely=args.nely, nelz=args.nelz,
        volfrac=args.volfrac, penal=args.penal, rmin=args.rmin
    )

    # Setup boundary conditions
    if args.case == "cantilever":
        f, fixed_dofs = setup_cantilever(args.nelx, args.nely, args.nelz)
    elif args.case == "bridge":
        f, fixed_dofs = setup_bridge(args.nelx, args.nely, args.nelz)
    else:
        raise ValueError("Invalid load case.")

    # Run Optimization Loop
    print("  Starting Topology Optimization Loop...")
    print(f"  {'Iter':<6} | {'Compliance':<12} | {'Change':<10}")
    print("-" * 40)

    u = None
    ce = None
    for it in range(1, args.maxiter + 1):
        # Assemble global stiffness matrix
        K = solver.assemble_stiffness()

        # Solve FEA
        u = solver.solve_fea(K, f, fixed_dofs, use_cg=args.use_cg)

        # Optimize step
        compliance, change, ce = solver.optimize_step(u, K)

        print(f"  {it:<6} | {compliance:<12.5f} | {change:<10.5f}")

        if change < args.tol:
            print(f"  Converged after {it} iterations (change < {args.tol}).")
            break
    else:
        print("  Reached maximum iterations.")

    print()
    print("  Mapping output fields to 6-channel material tensor...")
    channels = solver.get_stress_and_channels(u, ce)

    # Prepare complete output manifest JSON
    manifest = {
        "metadata": {
            "grid_dimensions": [args.nelx, args.nely, args.nelz],
            "load_case": args.case,
            "volume_fraction": args.volfrac,
            "penalty": args.penal,
            "filter_radius": args.rmin
        },
        "channels": channels
    }

    # Write output to file
    out_path = Path(args.output)
    with open(out_path, "w", encoding="utf-8") as out_file:
        json.dump(manifest, out_file, indent=2)

    print(f"  Successfully exported 6-channel tensor to: {out_path.absolute()}")
    print("=== SIMP SOLVER DONE ===")


if __name__ == "__main__":
    main()
