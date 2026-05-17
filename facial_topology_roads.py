#!/usr/bin/env python
"""FACIAL TOPOLOGY ANALYSIS — Bisecting Roads & Dead Ends
Analyzes the get_facial_weights() influence map as a topology grid.
Finds overlaps (roads), isolated vertices (dead ends), and proposes blends."""

import math

# Replicate the weight function in pure Python
def get_facial_weights(x, y, z, h=1.0):
    """Direct port of Blender get_facial_weights."""
    nx = x / (h * 0.35)
    ny = y / (h * 0.5)
    nz = z / (h * 0.4)
    front = max(0.0, min(1.0, (nz - 0.2) * 3.0))

    w = {}
    brow_y = max(0.0, 1.0 - abs(ny - 0.4) * 4.0)
    brow_x = max(0.0, 1.0 - abs(abs(nx) - 0.5) * 4.0)
    w['brow'] = front * brow_y * brow_x * (1.0 if abs(nx) > 0.1 else 0.0)

    eye_y = max(0.0, 1.0 - abs(ny - 0.15) * 5.0)
    eye_x = max(0.0, 1.0 - abs(abs(nx) - 0.45) * 5.0)
    w['eye'] = front * eye_y * eye_x

    mouth_y = max(0.0, 1.0 - abs(ny + 0.3) * 5.0)
    mouth_x = max(0.0, 1.0 - abs(nx) * 3.0)
    w['mouth'] = front * mouth_y * mouth_x

    corner_y = max(0.0, 1.0 - abs(ny + 0.25) * 4.0)
    w['mouth_corner_L'] = front * corner_y * max(0.0, 1.0 - abs(nx + 0.4) * 5.0)
    w['mouth_corner_R'] = front * corner_y * max(0.0, 1.0 - abs(nx - 0.4) * 5.0)

    jaw_y = max(0.0, 1.0 - abs(ny + 0.7) * 3.0)
    w['jaw'] = front * jaw_y * (1.0 if abs(nx) < 0.6 else 0.5)

    cheek_y = max(0.0, 1.0 - abs(ny) * 3.0)
    cheek_x = max(0.0, 1.0 - abs(abs(nx) - 0.6) * 4.0)
    w['cheek'] = front * cheek_y * cheek_x

    return w

# Sample the face grid
ZONES = ['brow','eye','mouth','mouth_corner_L','mouth_corner_R','jaw','cheek']
GRID = 40
bisections = []
dead_ends = {z: [] for z in ZONES}
plots = {z: [] for z in ZONES}

for i in range(GRID):
    for j in range(GRID):
        x = (i / GRID - 0.5) * 0.7  # ±0.35 head units
        y = (j / GRID - 0.3) * 1.0  # −0.3 to +0.7 (jaw to brow)
        z = 0.15                    # front surface
        
        w = get_facial_weights(x, y, z)
        active = [z for z in ZONES if w.get(z, 0) > 0.1]
        
        # BISECTIONS: two or more zones active at same point
        if len(active) >= 2:
            bisections.append((x, y, active, {z: round(w[z], 3) for z in active}))
        
        # PLOTS: single dominant zone
        if len(active) == 1:
            plots[active[0]].append((x, y, w[active[0]]))
        
        # DEAD ENDS: isolated vertex with no secondary influence
        if len(active) == 1 and all(w.get(z, 0) < 0.05 for z in ZONES if z != active[0]):
            dead_ends[active[0]].append((x, y))

print("=" * 65)
print("FACIAL TOPOLOGY ANALYSIS — Vinculum Weight Map")
print("=" * 65)
print()

# BISECTING ROADS
print(f"═══ BISECTING ROADS (Overlapping Zones) ═══")
print(f"Total bisection points: {len(bisections)}")
bisect_pairs = {}
for b in bisections:
    pair = tuple(sorted(b[2]))
    bisect_pairs[pair] = bisect_pairs.get(pair, 0) + 1

for pair, count in sorted(bisect_pairs.items(), key=lambda x: -x[1]):
    bar = chr(9608) * min(30, count // 2)
    print(f"  {' ∩ '.join(pair):<30s} {count:>4d} pts {bar}")

print()

# PLOTS OF LAND
print(f"═══ PLOTS OF LAND (Single-Zone Regions) ═══")
for zone in ZONES:
    pts = plots[zone]
    if pts:
        avg_w = sum(p[2] for p in pts) / len(pts)
        print(f"  {zone:<18s} {len(pts):>4d} vertices  avg influence={avg_w:.3f}")
print()

# DEAD ENDS
print(f"═══ DEAD ENDS (Isolated Vertices) ═══")
total_dead = sum(len(v) for v in dead_ends.values())
for zone in ZONES:
    d = dead_ends[zone]
    if d:
        print(f"  {zone:<18s} {len(d):>4d} isolated  (no secondary influence)")
print(f"  {'TOTAL':18s} {total_dead:>4d}")
print()

# RECOMMENDED CROSS STREETS
print(f"═══ RECOMMENDED CROSS STREETS (Blend Zones) ═══")
recommendations = [
    ("brow ↔ eye", "Upper eyelid crease. Blend brow_lift with eye_squint."),
    ("mouth ↔ cheek", "Nasolabial fold. Blend mouth_open with cheek_puff."),
    ("mouth ↔ jaw", "Lower lip to chin. Blend mouth_corner with jaw_clench."),
    ("mouth_corner_L ↔ cheek", "Left smile line. Blend smirk with cheek_lift."),
    ("eye ↔ cheek", "Lower orbital rim. Blend squint with cheek_puff."),
    ("brow ↔ mouth_corner", "Outer face diagonal. Rare but occurs in grimace."),
]

for pair, desc in recommendations:
    zone_a, zone_b = pair.split(' ↔ ')
    key = tuple(sorted([zone_a, zone_b]))
    count = bisect_pairs.get(key, 0)
    bar = chr(9608) * min(20, count) + chr(9617) * (20 - min(20, count))
    print(f"  {pair:<30s} {bar} {count:>3d} pts")
    print(f"    → {desc}")
    print()

# TOPOLOGY SUMMARY
print("═══ TOPOLOGY SUMMARY ═══")
print(f"  Bisecting roads: {len(bisections)} points where zones overlap")
print(f"  Dead ends:       {total_dead} isolated vertices")
print(f"  Plot regions:    7 zones, {sum(len(v) for v in plots.values())} total vertices")
print(f"  Recommendation:  Add 6 cross-street blend zones between adjacent regions")
print(f"                    to eliminate dead ends and smooth transitions.")
