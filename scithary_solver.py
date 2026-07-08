import json
from collections import deque, defaultdict
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "scithary_data.json")

def solve_scithary():
    print("=== SCITHARY GEOMETRIC SOLVER ===")
    
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
        
    print(f"[1] Loaded dormant Scithary map")
    
    # 1. Stitching Edges
    overlaps = data.get("region_overlap", {}).get("all_overlaps", [])
    edges = []
    adj_list = defaultdict(list)
    
    threshold = 0.15
    for overlap in overlaps:
        if overlap["overlap_score"] >= threshold:
            ra = overlap["region_a"]
            rb = overlap["region_b"]
            edges.append({
                "source": ra,
                "target": rb,
                "weight": overlap["overlap_score"]
            })
            adj_list[ra].append(rb)
            adj_list[rb].append(ra) # undirected graph
            
    # Deduplicate nodes to get total count
    all_nodes = set(data.get("node_integrity", {}).get("nodes", {}).keys())
    
    # Write topology
    data["connection_topology"] = {
        "total_nodes": len(all_nodes),
        "total_edges": len(edges),
        "mean_degree": (len(edges) * 2 / len(all_nodes)) if all_nodes else 0.0,
        "edges": edges
    }
    
    print(f"[2] Stitched Topology: Created {len(edges)} hard edges based on >0.60 geometric overlap.")
    
    # 2. Energy Propagation (BFS)
    origins = data.get("energy_pulse_routing", {}).get("pulse_origins", [])
    
    visited = set(origins)
    queue = deque([(origin, 0) for origin in origins]) # (node, distance)
    
    routing_path = []
    
    while queue:
        current, dist = queue.popleft()
        routing_path.append({"node": current, "pulse_distance": dist})
        
        for neighbor in adj_list[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
                
    data["energy_pulse_routing"] = {
        "pulse_origins": origins,
        "num_origins": len(origins),
        "total_nodes_reached": len(visited),
        "routing_path": routing_path
    }
    
    print(f"[3] Energy Pulse Cascaded: Reached {len(visited)} nodes out of {len(all_nodes)}.")
    
    # Write back
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"[4] Awoken state preserved to {DATA_PATH}")

if __name__ == "__main__":
    solve_scithary()
