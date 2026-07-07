#!/usr/bin/env python
"""VINCULUM FAST SCAN — Optimized for A100 / any GPU"""
import json, os, re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

t0 = __import__('time').time()
print('VINCULUM FAST SCAN')

BASE = Path.home() / 'Projects'
PATTERNS = {
    'fraction':     re.compile(r'\([^)]*/[^)]*\)'),
    'overline':     re.compile(r'─{2,}'),
    'group_brace':  re.compile(r'\{[^}]*\}'),
    'chain':        re.compile(r'\w+\s*[/|]\s*\w+\s*[/|]\s*\w+'),
    'hyphen_bind':  re.compile(r'\w+-\w+-\w+'),
    'auto_close':   re.compile(r'[\(\[][^\)\]]*[\)\]]'),
    'repeat':       re.compile(r'(?:every|cron|forever|repeat)', re.I),
    'negation':     re.compile(r'(?:fixme|FIXME|TODO|HACK|XXX)[:\s]', re.I),
}

results = []
counts = Counter()
projects = defaultdict(lambda: {'files':0,'v':0,'kb':0})

proj_dirs = [d for d in sorted(BASE.iterdir()) if d.is_dir() and not d.name.startswith('.')]
total_dirs = len(proj_dirs)
for di, proj_dir in enumerate(proj_dirs):
    print(f'[{di+1}/{total_dirs}] {proj_dir.name}...', flush=True)
    
    for root, dirs, files in os.walk(proj_dir):
        # Prune directories we never want to descend into
        dirs[:] = [d for d in dirs if d not in ('.git','__pycache__','node_modules')]
        for fname in files:
            fp = Path(root) / fname
            ext = os.path.splitext(fname)[1]
            if ext not in ('.py','.html','.md','.json','.ipynb'): continue
            if not fp.exists(): continue
        
            try:
                content = fp.read_text(errors='ignore')[:100000]  # cap at 100KB
                lines = content.count('\n')
                fv = 0
                ftypes = []
                
                for name, pat in PATTERNS.items():
                    m = pat.findall(content)
                    if m:
                        c = len(m)
                        fv += c
                        counts[name] += c
                        ftypes.append(name)
                
                if fv > 0:
                    density = fv / max(1, lines) * 100
                    results.append({
                        'p': proj_dir.name, 'f': fp.name,
                        'l': lines, 'v': fv, 'd': round(density, 1),
                        't': ftypes[:5]
                    })
                    projects[proj_dir.name]['files'] += 1
                    projects[proj_dir.name]['v'] += fv
                    projects[proj_dir.name]['kb'] += len(content) / 1024
            except: pass

# Summary
total_v = sum(d['v'] for d in results)
total_f = len(results)
print(f'Files: {total_f} | Vinculums: {total_v:,} | Mean: {total_v/max(1,total_f):.1f}/file')
print(f'Runtime: {__import__("time").time()-t0:.1f}s')

# Top patterns
for name, c in counts.most_common(5):
    print(f'  {name}: {c}')

# Top files
for r in sorted(results, key=lambda x: x['d'], reverse=True)[:5]:
    print(f'  {r["p"]}/{r["f"]}: {r["d"]}% density ({r["v"]} vinculums in {r["l"]} lines)')

# Projects
for p, s in sorted(projects.items(), key=lambda x: x[1]['v'], reverse=True):
    print(f'  {p}: {s["files"]} files, {s["v"]} vinculums, {s["kb"]:.0f}KB')

# Save
out = {
    'total_files': total_f, 'total_vinculums': total_v,
    'patterns': dict(counts), 'projects': dict(projects),
    'top_files': results[:20], 'runtime_s': round(__import__('time').time()-t0, 1)
}
with open(Path.home() / 'Projects/trench_builder/vinculum_scan.json', 'w') as f:
    json.dump(out, f, indent=2, default=str)
print(f'Saved vinculum_scan.json')
print(json.dumps({'files':total_f,'vinculums':total_v}))
