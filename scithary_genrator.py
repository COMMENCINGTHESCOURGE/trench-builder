#!/usr/bin/env python3
"""
SCITHARY GENRATOR — Territory Analysis Engine
===============================================
Computes region overlap, node integrity, connection topology,
and energy pulse routing across the Trench Builder territory network.

Inputs:
  - vinculum_scan.json   (project territories with vinculum counts)
  - bonds/*.json         (connection bonds between regions)
  - mecha_optimization.json (mobility/energy data)

Output:
  - scithary_data.json   (full territory analysis)
"""

import json
import math
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).parent

# ═══════════════════════════════════════════════════════════
# 1. LOAD DATA
# ═══════════════════════════════════════════════════════════

def load_vinculum_scan() -> dict:
    with open(BASE_DIR / "vinculum_scan.json") as f:
        return json.load(f)

def load_bonds() -> dict:
    bonds = {}
    bonds_dir = BASE_DIR / "bonds"
    if bonds_dir.exists():
        for bond_file in bonds_dir.glob("*.json"):
            with open(bond_file) as f:
                bond_data = json.load(f)
                bonds[bond_file.stem] = bond_data
    return bonds

def load_mecha() -> dict:
    path = BASE_DIR / "mecha_optimization.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


# ═══════════════════════════════════════════════════════════
# 2. REGION OVERLAP ANALYSIS
# ═══════════════════════════════════════════════════════════

def compute_region_overlap(projects: dict) -> dict:
    """Compute overlap between project regions based on size proximity and name affinity."""
    project_names = list(projects.keys())
    n = len(project_names)
    
    # Build feature vectors for each project
    vectors = {}
    for name, data in projects.items():
        v = data.get("v", 0)
        files = data.get("files", 0)
        kb = data.get("kb", 0)
        vectors[name] = [
            math.log(files + 1),
            math.log(v + 1),
            math.log(kb + 1),
        ]
    
    overlaps = []
    for i in range(n):
        for j in range(i + 1, n):
            a_name = project_names[i]
            b_name = project_names[j]
            a_vec = vectors[a_name]
            b_vec = vectors[b_name]
            
            dot = sum(x * y for x, y in zip(a_vec, b_vec))
            norm_a = math.sqrt(sum(x * x for x in a_vec))
            norm_b = math.sqrt(sum(y * y for y in b_vec))
            cosine_sim = dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0
            
            # Name affinity via shared tokens
            a_toks = set(a_name.lower().replace("-", " ").replace("_", " ").split())
            b_toks = set(b_name.lower().replace("-", " ").replace("_", " ").split())
            name_affinity = len(a_toks & b_toks) / max(len(a_toks | b_toks), 1) if a_toks and b_toks else 0
            
            # Size proximity
            max_v = max(projects[a_name]["v"], projects[b_name]["v"], 1)
            size_proximity = 1.0 - abs(projects[a_name]["v"] - projects[b_name]["v"]) / max_v
            
            combined_score = 0.4 * cosine_sim + 0.3 * name_affinity + 0.3 * size_proximity
            
            if combined_score > 0.15:
                overlaps.append({
                    "region_a": a_name,
                    "region_b": b_name,
                    "cosine_similarity": round(cosine_sim, 4),
                    "name_affinity": round(name_affinity, 4),
                    "size_proximity": round(size_proximity, 4),
                    "overlap_score": round(combined_score, 4),
                })
    
    overlaps.sort(key=lambda x: x["overlap_score"], reverse=True)
    
    return {
        "total_regions": n,
        "total_overlaps_detected": len(overlaps),
        "top_overlaps": overlaps[:50],
        "all_overlaps": overlaps,
        "summary": {
            "mean_overlap_score": round(sum(o["overlap_score"] for o in overlaps) / max(len(overlaps), 1), 4),
            "max_overlap_score": round(max(o["overlap_score"] for o in overlaps) if overlaps else 0, 4),
        }
    }


# ═══════════════════════════════════════════════════════════
# 3. NODE INTEGRITY ANALYSIS
# ═══════════════════════════════════════════════════════════

def compute_node_integrity(projects: dict, bonds: dict) -> dict:
    """Compute integrity score for each node based on density, stability, and bond connectivity."""
    node_results = {}
    
    for name, data in projects.items():
        v = data.get("v", 0)
        files = data.get("files", 0)
        kb = data.get("kb", 0)
        
        v_density = v / max(files, 1)
        kb_per_v = kb / max(v, 1)
        
        # Bond connectivity score
        bond_score = 0.0
        name_lower = name.lower()
        for bond_name, bond_data in bonds.items():
            channels = bond_data.get("channels", [])
            for ch in channels:
                if ch in name_lower or name_lower in ch:
                    bond_score += bond_data.get("rate", 0) * 10
                    if bond_data.get("classification") == "STABLE":
                        bond_score += 0.2
        
        isolation_risk = 1.0 / (1.0 + bond_score)
        
        density_norm = min(v_density / 100, 1.0)
        stability_norm = 1.0 / (1.0 + kb_per_v)
        bond_norm = min(bond_score / 2.0, 1.0)
        
        integrity = 0.35 * density_norm + 0.25 * stability_norm + 0.40 * bond_norm
        
        node_results[name] = {
            "files": files,
            "vinculums": v,
            "size_kb": round(kb, 2),
            "vinculum_density": round(v_density, 2),
            "kb_per_vinculum": round(kb_per_v, 4),
            "bond_connectivity": round(bond_score, 4),
            "isolation_risk": round(isolation_risk, 4),
            "integrity_score": round(integrity, 4),
            "status": (
                "CRITICAL" if integrity < 0.1 else
                "FRAGILE" if integrity < 0.25 else
                "STABLE" if integrity < 0.5 else
                "ROBUST" if integrity < 0.75 else
                "FORTIFIED"
            ),
        }
    
    scores = [n["integrity_score"] for n in node_results.values()]
    
    return {
        "nodes": node_results,
        "summary": {
            "total_nodes": len(node_results),
            "mean_integrity": round(sum(scores) / max(len(scores), 1), 4),
            "min_integrity": round(min(scores) if scores else 0, 4),
            "max_integrity": round(max(scores) if scores else 0, 4),
            "critical_nodes": sum(1 for n in node_results.values() if n["status"] == "CRITICAL"),
            "fragile_nodes": sum(1 for n in node_results.values() if n["status"] == "FRAGILE"),
            "stable_nodes": sum(1 for n in node_results.values() if n["status"] == "STABLE"),
            "robust_nodes": sum(1 for n in node_results.values() if n["status"] == "ROBUST"),
            "fortified_nodes": sum(1 for n in node_results.values() if n["status"] == "FORTIFIED"),
        }
    }


# ═══════════════════════════════════════════════════════════
# 4. CONNECTION TOPOLOGY
# ═══════════════════════════════════════════════════════════

def compute_connection_topology(projects: dict, bonds: dict) -> dict:
    """Analyze connection topology: degree centrality, hubs, components."""
    project_names = list(projects.keys())
    adjacency = defaultdict(set)
    
    for bond_name, bond_data in bonds.items():
        channels = bond_data.get("channels", [])
        matching_projects = []
        for ch in channels:
            ch_lower = ch.lower()
            for pname in project_names:
                if ch_lower in pname.lower() or pname.lower() in ch_lower:
                    matching_projects.append(pname)
        for i in range(len(matching_projects)):
            for j in range(i + 1, len(matching_projects)):
                adjacency[matching_projects[i]].add(matching_projects[j])
                adjacency[matching_projects[j]].add(matching_projects[i])
    
    degree_centrality = {name: len(adjacency.get(name, set())) for name in project_names}
    sorted_by_deg = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
    mean_degree = sum(degree_centrality.values()) / max(len(degree_centrality), 1)
    hubs = [(name, deg) for name, deg in sorted_by_deg if deg > mean_degree * 2][:15]
    isolated = [name for name, deg in degree_centrality.items() if deg == 0]
    
    # Connected components (BFS)
    visited = set()
    components = []
    for name in project_names:
        if name not in visited:
            comp = []
            queue = [name]
            while queue:
                node = queue.pop(0)
                if node not in visited:
                    visited.add(node)
                    comp.append(node)
                    queue.extend(adjacency.get(node, set()) - visited)
            components.append(comp)
    
    comp_sizes = [len(c) for c in components]
    
    return {
        "total_nodes": len(project_names),
        "total_edges": sum(len(v) for v in adjacency.values()) // 2,
        "mean_degree": round(mean_degree, 2),
        "max_degree": max(degree_centrality.values()) if degree_centrality else 0,
        "hubs": [{"name": name, "degree": deg, "project_size_v": projects[name]["v"]} 
                 for name, deg in hubs],
        "isolated_nodes": isolated,
        "num_isolated": len(isolated),
        "connected_components": len(components),
        "component_sizes": comp_sizes,
        "largest_component_pct": round(max(comp_sizes) / max(len(project_names), 1) * 100, 1) if comp_sizes else 0,
        "topology_type": (
            "STAR" if len(hubs) <= 2 and max(comp_sizes, default=0) > len(project_names) * 0.8 else
            "MESH" if mean_degree > 3 else
            "HUB_SPOKE" if len(hubs) >= 3 else
            "FRAGMENTED" if len(components) > len(project_names) * 0.3 else
            "SPARSE"
        ),
    }


# ═══════════════════════════════════════════════════════════
# 5. ENERGY PULSE ROUTING
# ═══════════════════════════════════════════════════════════

def compute_energy_pulse_routing(projects: dict, bonds: dict, topology: dict) -> dict:
    """Simulate energy pulse routing with BFS dissipation through bond channels."""
    project_names = list(projects.keys())
    
    # Pulse origins: top 10% by vinculum density
    ranked = sorted(projects.items(), key=lambda x: x[1].get("v", 0) / max(x[1].get("files", 1), 1), reverse=True)
    top_n = max(1, len(ranked) // 10)
    origins = [name for name, _ in ranked[:top_n]]
    
    # Build routing graph
    routing_graph = defaultdict(list)
    for bond_name, bond_data in bonds.items():
        channels = bond_data.get("channels", [])
        rate = bond_data.get("rate", 0.005)
        matching = []
        for ch in channels:
            ch_lower = ch.lower()
            for pname in project_names:
                if ch_lower in pname.lower() or pname.lower() in ch_lower:
                    matching.append(pname)
        for i in range(len(matching)):
            for j in range(i + 1, len(matching)):
                routing_graph[matching[i]].append((matching[j], rate, bond_name))
                routing_graph[matching[j]].append((matching[i], rate, bond_name))
    
    # Simulate pulse propagation
    max_hops = 6
    pulse_routes = {}
    total_reached = set()
    
    for origin in origins:
        energy = 1.0
        visited = {origin: energy}
        queue = [(origin, energy, 0)]
        
        while queue:
            node, e, hop = queue.pop(0)
            if hop >= max_hops:
                continue
            for neighbor, rate, bond_name in routing_graph.get(node, []):
                if neighbor not in visited:
                    dissipation = rate * (hop + 1) * 0.5
                    new_energy = e * (1.0 - dissipation)
                    if new_energy > 0.01:
                        visited[neighbor] = new_energy
                        queue.append((neighbor, new_energy, hop + 1))
        
        reachable = {k: round(v, 4) for k, v in visited.items() if k != origin}
        pulse_routes[origin] = {
            "origin_vinculums": projects[origin]["v"],
            "reachable_nodes": len(reachable),
            "coverage_pct": round(len(reachable) / max(len(project_names) - 1, 1) * 100, 2),
            "energy_map": reachable,
            "routing_efficiency": round(
                sum(reachable.values()) / max(len(reachable), 1), 4
            ) if reachable else 0,
        }
        total_reached.update(reachable.keys())
    
    all_eff = [r["routing_efficiency"] for r in pulse_routes.values()]
    
    return {
        "pulse_origins": origins,
        "num_origins": len(origins),
        "total_nodes_reached": len(total_reached),
        "network_coverage_pct": round(len(total_reached) / max(len(project_names) - len(origins), 1) * 100, 2),
        "mean_routing_efficiency": round(sum(all_eff) / max(len(all_eff), 1), 4),
        "best_origin": max(pulse_routes.items(), key=lambda x: x[1]["coverage_pct"])[0] if pulse_routes else None,
        "routes": pulse_routes,
        "bond_routing_metadata": {
            "total_bonds": len(bonds),
            "bond_types": list(set(b.get("type", "unknown") for b in bonds.values())),
            "mean_dissipation_rate": round(
                sum(b.get("rate", 0) for b in bonds.values()) / max(len(bonds), 1), 6
            ),
        },
    }


# ═══════════════════════════════════════════════════════════
# 6. MAIN
# ═══════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  SCITHARY GENRATOR — Territory Analysis")
    print("=" * 60)
    
    print("\n[1/5] Loading territory data...")
    vin_data = load_vinculum_scan()
    projects = vin_data.get("projects", {})
    total_vinculums = vin_data.get("total_vinculums", 0)
    total_files = vin_data.get("total_files", 0)
    patterns = vin_data.get("patterns", {})
    print(f"  Loaded {len(projects)} regions, {total_files} files, {total_vinculums:,} vinculums")
    
    bonds = load_bonds()
    print(f"  Loaded {len(bonds)} bonds: {list(bonds.keys())}")
    
    mecha = load_mecha()
    if mecha:
        print(f"  Loaded mecha optimization data")
    
    print("\n[2/5] Computing region overlap...")
    overlap = compute_region_overlap(projects)
    print(f"  Found {overlap['total_overlaps_detected']} significant overlaps "
          f"(mean score: {overlap['summary']['mean_overlap_score']})")
    
    print("\n[3/5] Computing node integrity...")
    integrity = compute_node_integrity(projects, bonds)
    s = integrity["summary"]
    print(f"  Analyzed {s['total_nodes']} nodes")
    print(f"  Fortified: {s['fortified_nodes']}, Robust: {s['robust_nodes']}, "
          f"Stable: {s['stable_nodes']}, Fragile: {s['fragile_nodes']}, "
          f"Critical: {s['critical_nodes']}")
    
    print("\n[4/5] Computing connection topology...")
    topology = compute_connection_topology(projects, bonds)
    print(f"  Topology: {topology['topology_type']}")
    print(f"  {topology['total_edges']} edges, {topology['num_isolated']} isolated nodes")
    print(f"  {len(topology['hubs'])} hubs, {topology['connected_components']} components")
    print(f"  Largest component: {topology['largest_component_pct']}% of network")
    
    print("\n[5/5] Computing energy pulse routing...")
    routing = compute_energy_pulse_routing(projects, bonds, topology)
    print(f"  {routing['num_origins']} pulse origins")
    print(f"  Network coverage: {routing['network_coverage_pct']}%")
    print(f"  Mean routing efficiency: {routing['mean_routing_efficiency']}")
    print(f"  Best origin: {routing['best_origin']}")
    
    # Assemble output
    scithary_data = {
        "metadata": {
            "generator": "scithary-genrator",
            "version": "1.0.0",
            "generated_at": "2026-06-15",
            "source": "trench_builder",
            "input_summary": {
                "total_regions": len(projects),
                "total_files": total_files,
                "total_vinculums": total_vinculums,
                "vinculum_patterns": patterns,
                "bonds_loaded": len(bonds),
                "bond_names": list(bonds.keys()),
            }
        },
        "region_overlap": overlap,
        "node_integrity": integrity,
        "connection_topology": topology,
        "energy_pulse_routing": routing,
    }
    
    output_path = BASE_DIR / "scithary_data.json"
    with open(output_path, "w") as f:
        json.dump(scithary_data, f, indent=2, default=str)
    
    file_size_kb = output_path.stat().st_size / 1024
    print(f"\n{'=' * 60}")
    print(f"  Output: {output_path}")
    print(f"  Size: {file_size_kb:.1f} KB")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
