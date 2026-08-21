#!/usr/bin/env python3
"""Re-run Vinculum Interiors Optimizer locally when Kaggle API is unreachable.
Mirrors the notebook cells at kaggle_push/vinculum-interiors.ipynb exactly.
Produces vinculum_interiors_data.json with the same schema the HTML template expects."""

import json, hashlib, sys

ROOMS = {
    'SUPINE': {'dims': {'w': 12, 'd': 10, 'h': 4}, 'chroma': {'hue': 220},
               'props': [{'tag': 'bed'}, {'tag': 'locker'}, {'tag': 'lamp'}],
               'warn': [], 'doors': [{'x': 0, 'z': -5, 'w': 2}]},
    'SCOOT': {'dims': {'w': 4, 'd': 18, 'h': 3.5}, 'chroma': {'hue': 200},
               'props': [{'tag': 'fire_extinguisher'}, {'tag': 'floor_light'}],
               'warn': [], 'doors': [{'x': 1, 'z': -9, 'w': 2}, {'x': 1, 'z': 9, 'w': 2}]},
    'CRAWL': {'dims': {'w': 3, 'd': 14, 'h': 2.8}, 'chroma': {'hue': 30},
               'props': [{'tag': 'pipe'}, {'tag': 'valve'}],
               'warn': [], 'doors': [{'x': 0.75, 'z': -7, 'w': 1.5}, {'x': 0.75, 'z': 7, 'w': 1.5}]},
    'STAND': {'dims': {'w': 16, 'd': 14, 'h': 5}, 'chroma': {'hue': 170},
               'props': [{'tag': 'hologram_table'}, {'tag': 'server'}, {'tag': 'server'}],
               'warn': [], 'doors': [{'x': 0, 'z': -7, 'w': 3}, {'x': -7, 'z': 0, 'w': 3}]},
    'BOUNCE': {'dims': {'w': 20, 'd': 18, 'h': 8}, 'chroma': {'hue': 140},
               'props': [{'tag': 'training_mat'}, {'tag': 'target_dummy'}, {'tag': 'pole'}],
               'warn': [], 'doors': [{'x': 0, 'z': -9, 'w': 4}]},
    'WALK': {'dims': {'w': 14, 'd': 20, 'h': 6}, 'chroma': {'hue': 190},
             'props': [{'tag': 'platform'}, {'tag': 'ticket_kiosk'}],
             'warn': [], 'doors': [{'x': 0, 'z': 10, 'w': 4}, {'x': 0, 'z': -10, 'w': 4}]},
    'JUMP': {'dims': {'w': 24, 'd': 24, 'h': 12}, 'chroma': {'hue': 10},
             'props': [{'tag': 'launch_pad'}, {'tag': 'fuel_tank'}, {'tag': 'console'}],
             'warn': [], 'doors': [{'x': 0, 'z': 12, 'w': 6}]},
    'RUN': {'dims': {'w': 10, 'd': 10, 'h': 5}, 'chroma': {'hue': 0},
            'props': [{'tag': 'reactor_core'}, {'tag': 'coolant'}, {'tag': 'coolant'}],
            'warn': [], 'doors': [{'x': 0, 'z': -5, 'w': 2.5}]}
}

STAGES = ['SUPINE', 'SCOOT', 'CRAWL', 'STAND', 'BOUNCE', 'WALK', 'JUMP', 'RUN']

def analyze(rooms, stages):
    for name, room in rooms.items():
        dims = room['dims']
        area = dims['w'] * dims['d']
        volume = area * dims['h']
        prop_count = len(room['props'])
        door_count = len(room['doors'])
        props_per_100sqm = prop_count / area * 100
        warnings = []
        if dims['h'] < 2.8:
            warnings.append('CEILING TOO LOW')
        if props_per_100sqm > 8:
            warnings.append('OVER-FURNISHED')
        if door_count == 1 and area > 150:
            warnings.append('SINGLE EXIT IN LARGE ROOM')
        if warnings:
            room['warn'] = warnings
        print(f'  {name:8s}: {area:4.0f}m2 ({volume:5.0f}m3)  {prop_count} props  {door_count} doors')
        for w in warnings:
            print(f'    WARNING: {w}')

    for i in range(len(stages)):
        a = rooms[stages[i]]['chroma']['hue']
        b = rooms[stages[(i+1) % len(stages)]]['chroma']['hue']
        diff = min(abs(a-b), 360-abs(a-b))
        status = 'GOOD' if diff > 30 else 'LOW'
        print(f'  {stages[i]:6s}({a:3d}) → {stages[(i+1)%8]:6s}({b:3d})  Δ={diff:3d}°  {status}')

    for name, room in rooms.items():
        dims = room['dims']
        area = dims['w'] * dims['d']
        prop_footprint = len(room['props']) * 3
        clearance = (area - prop_footprint) / area * 100
        status = 'GOOD' if clearance > 70 else ('FAIR' if clearance > 50 else 'TIGHT')
        print(f'  {name:8s}: footprint={prop_footprint:.0f}m2  clearance={clearance:.0f}%  {status}')

    for name, room in rooms.items():
        score = sum(1 for d in room['doors'] if d['w'] >= 2)
        multi_dir = len(set(d['z'] > 0 for d in room['doors'])) > 1 if room['doors'] else False
        if multi_dir:
            score += 1
        print(f'  {name:8s}: score={score}/4  wide_enough={"Y" if score>0 else "N"}  multi_dir={"Y" if multi_dir else "N"}')

    return {
        'generator': 'Vinculum Interiors Optimizer (Kaggle GPU — local recompute)',
        'rooms': rooms,
        'stage_order': stages,
        'analysis': {
            'total_rooms': len(rooms),
            'total_doors': sum(len(r['doors']) for r in rooms.values()),
            'total_props': sum(len(r['props']) for r in rooms.values()),
        }
    }

if __name__ == '__main__':
    print('Interiors Optimizer — local recompute')
    output = analyze(ROOMS, STAGES)
    out_path = sys.argv[1] if len(sys.argv) > 1 else 'vinculum_interiors_data.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    md5 = hashlib.md5(json.dumps(output, sort_keys=True).encode()).hexdigest()
    print(f'\nExported: {out_path}')
    print(f'Rooms: {output["analysis"]["total_rooms"]}  Doors: {output["analysis"]["total_doors"]}  Props: {output["analysis"]["total_props"]}')
    print(f'Integrity MD5: {md5}')
