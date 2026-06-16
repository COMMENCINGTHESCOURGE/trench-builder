#!/usr/bin/env python3
# VINCULUM INTERIORS OPTIMIZER — local regeneration (Kaggle auth expired)
# Adapted from: erdos-straus-solver/kaggle_kernels/vinculum-interiors/vinculum-interiors.ipynb
# Output: vinculum_interiors_data.json -> trench_builder root

import numpy as np
import json
import math
import os
import sys

print('Interiors Optimizer — Local (Kaggle GPU replaced with NumPy)')

# ROOM DATA — same as the HTML template
ROOMS = {
  'SUPINE': {'dims':{'w':12,'d':10,'h':4},'chroma':{'hue':220},'props':[
    {'tag':'bed'},{'tag':'locker'},{'tag':'lamp'}],
  'warn':[], 'doors':[{'x':0,'z':-5,'w':2}]},
  'SCOOT': {'dims':{'w':4,'d':18,'h':3.5},'chroma':{'hue':200},'props':[
    {'tag':'fire_extinguisher'},{'tag':'floor_light'}],
    'warn':[], 'doors':[{'x':1,'z':-9,'w':2},{'x':1,'z':9,'w':2}]},
  'CRAWL': {'dims':{'w':3,'d':14,'h':2.8},'chroma':{'hue':30},'props':[
    {'tag':'pipe'},{'tag':'valve'}],
    'warn':[], 'doors':[{'x':0.75,'z':-7,'w':1.5},{'x':0.75,'z':7,'w':1.5}]},
  'STAND': {'dims':{'w':16,'d':14,'h':5},'chroma':{'hue':170},'props':[
    {'tag':'hologram_table'},{'tag':'server'},{'tag':'server'}],
    'warn':[], 'doors':[{'x':0,'z':-7,'w':3},{'x':-7,'z':0,'w':3}]},
  'BOUNCE': {'dims':{'w':20,'d':18,'h':8},'chroma':{'hue':140},'props':[
    {'tag':'training_mat'},{'tag':'target_dummy'},{'tag':'pole'}],
    'warn':[], 'doors':[{'x':0,'z':-9,'w':4}]},
  'WALK': {'dims':{'w':14,'d':20,'h':6},'chroma':{'hue':190},'props':[
    {'tag':'platform'},{'tag':'ticket_kiosk'}],
    'warn':[], 'doors':[{'x':0,'z':10,'w':4},{'x':0,'z':-10,'w':4}]},
  'JUMP': {'dims':{'w':24,'d':24,'h':12},'chroma':{'hue':10},'props':[
    {'tag':'launch_pad'},{'tag':'fuel_tank'},{'tag':'console'}],
    'warn':[], 'doors':[{'x':0,'z':12,'w':6}]},
  'RUN': {'dims':{'w':10,'d':10,'h':5},'chroma':{'hue':0},'props':[
    {'tag':'reactor_core'},{'tag':'coolant'},{'tag':'coolant'}],
    'warn':[], 'doors':[{'x':0,'z':-5,'w':2.5}]}
}
print(f'Rooms: {len(ROOMS)}')

# 1. DIMENSION VALIDATION — clearance and volume
print('\nDIMENSION ANALYSIS:')
for name, room in ROOMS.items():
    dims = room['dims']
    area = dims['w'] * dims['d']
    volume = area * dims['h']
    prop_count = len(room['props'])
    door_count = len(room['doors'])
    props_per_100sqm = prop_count / area * 100
    
    # Too cramped?
    warnings = []
    if dims['h'] < 2.8: warnings.append('CEILING TOO LOW')
    if props_per_100sqm > 8: warnings.append('OVER-FURNISHED')
    if door_count == 1 and area > 150: warnings.append('SINGLE EXIT IN LARGE ROOM')
    
    print(f'  {name:8s}: {area:4.0f}m2 ({volume:5.0f}m3)  {prop_count} props  {door_count} doors')
    for w in warnings: print(f'    WARNING: {w}')

# 2. CHROMA OPTIMIZATION — verify hue contrast between adjacent stages
STAGES = ['SUPINE','SCOOT','CRAWL','STAND','BOUNCE','WALK','JUMP','RUN']
print('\nCHROMA ANALYSIS:')
for i in range(len(STAGES)):
    a = ROOMS[STAGES[i]]['chroma']['hue']
    b = ROOMS[STAGES[(i+1)%len(STAGES)]]['chroma']['hue']
    diff = min(abs(a-b), 360-abs(a-b))
    bar = chr(9608)*int(diff/5) + chr(9617)*(12-int(diff/5))
    status = 'GOOD' if diff > 30 else 'LOW'
    print(f'  {STAGES[i]:6s}({a:3d}) -> {STAGES[(i+1)%8]:6s}({b:3d})  d={diff:3d}  {bar}  {status}')

# 3. PROP DENSITY vs NAVIGATION CLEARANCE
print('\nNAVIGATION CLEARANCE:')
for name, room in ROOMS.items():
    dims = room['dims']
    area = dims['w'] * dims['d']
    # Estimate prop footprint (each prop occupies ~3m2 including walking space)
    prop_footprint = len(room['props']) * 3
    clearance = (area - prop_footprint) / area * 100
    bar = chr(9608)*int(clearance/5) + chr(9617)*(20-int(clearance/5))
    status = 'GOOD' if clearance > 70 else ('FAIR' if clearance > 50 else 'TIGHT')
    print(f'  {name:8s}: prop footprint={prop_footprint:.0f}m2  clearance={clearance:.0f}%  {bar} {status}')

# 4. DOOR ACCESSIBILITY SCORING
print('\nDOOR ACCESSIBILITY:')
for name, room in ROOMS.items():
    dims = room['dims']
    score = 0
    for door in room['doors']:
        width_ok = door['w'] >= 2
        if width_ok: score += 1
    
    multi_dir = len(set(d['z'] > 0 for d in room['doors'])) > 1 if room['doors'] else False
    if multi_dir: score += 1
    
    bar = chr(9608)*score + chr(9617)*(4-score)
    print(f'  {name:8s}: score={score}/4  {bar}  wide_enough={"Y" if score>0 else "N"}  multi_dir={"Y" if multi_dir else "N"}')

# 5. EXPORT — optimized room data
# Determine output path: first CLI arg, or next to this script
if len(sys.argv) > 1:
    output_path = sys.argv[1]
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'vinculum_interiors_data.json')

output = {
    'generator': 'Vinculum Interiors Optimizer (local — Kaggle GPU replaced with NumPy)',
    'rooms': ROOMS,
    'stage_order': STAGES,
    'analysis': {
        'total_rooms': len(ROOMS),
        'total_doors': sum(len(r['doors']) for r in ROOMS.values()),
        'total_props': sum(len(r['props']) for r in ROOMS.values()),
    }
}

with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f'\nExported: {output_path}')
print(f'Rooms: {len(ROOMS)}  Doors: {output["analysis"]["total_doors"]}  Props: {output["analysis"]["total_props"]}')
