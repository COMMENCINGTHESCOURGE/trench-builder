#!/usr/bin/env python
"""VINCULUM SCANNER — A100: Scan all 732 project files for vinculum patterns"""
import json, os, re, math
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime

start = __import__('time').time()
print('=' * 50)
print('VINCULUM SCANNER — A100 Project-Wide Analysis')
print(f'Start: {datetime.now().isoformat()}')
print('=' * 50)

BASE = Path.home() / 'Projects'
PATTERNS = {
    'fraction':     r'\(.*/.*\)',           # (a/b)
    'overline':     r'─+',                  # vinculum bar
    'group_brace':  r'\{.*\}',              # {block}
    'group_paren':  r'\(.*\)',              # (group)  
    'chain':        r'.*[/|].*[/|].*',      # a/b/c pipeline
    'hyphen_bind':  r'\w+-\w+-\w+',         # state-of-the-art
    'auto_close':   r'[\(\[\{].*[\)\]\}]',  # balanced containers
    'repeat':       r'every\s+\d+[hmd]',    # cron schedule
    'negation':     r'(?:fix|correct|error|todo).*',  # correction flag
    'roman_mult':   r'\b[IVX]+\b',          # Roman numerals
}

results = []
file_counts = Counter()
domain_counts = defaultdict(Counter)
compression_data = []

for project_dir in sorted(BASE.iterdir()):
    if not project_dir.is_dir() or project_dir.name.startswith('.'):
        continue
    
    proj_files = 0
    proj_vinculums = 0
    
    for filepath in project_dir.rglob('*'):
        if filepath.suffix not in ('.py', '.html', '.md', '.json', '.ipynb', '.js'):
            continue
        if any(p in filepath.parts for p in ('.git', '__pycache__', 'node_modules')):
            continue
        
        try:
            content = filepath.read_text(errors='ignore')
            lines = content.split('\n')
            proj_files += 1
            file_vinculums = 0
            
            for pattern_name, pattern in PATTERNS.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    file_vinculums += len(matches)
                    file_counts[pattern_name] += len(matches)
            
            proj_vinculums += file_vinculums
            if file_vinculums > 0:
                domain_counts[project_dir.name][filepath.suffix] += 1
            
            # Track per-file vinculum density
            if file_vinculums > 0:
                compression_data.append({
                    'project': project_dir.name,
                    'file': filepath.name,
                    'ext': filepath.suffix,
                    'size_bytes': len(content),
                    'lines': len(lines),
                    'vinculums': file_vinculums,
                    'density': round(file_vinculums / max(1, len(lines)) * 100, 1)
                })
        except:
            pass
    
    if proj_vinculums > 0:
        pct = proj_vinculums / max(1, proj_files)
        print(f'  {project_dir.name:<25s} {proj_files:>4d} files  {proj_vinculums:>5d} vinculums  {pct:.1f}/file')

print()
print(f'Scanned across all projects')
print(f'Total files: {len(compression_data)} with vinculums')

# Vinculum type distribution
print(f'\n=== VINCULUM TYPE DISTRIBUTION ===')
for name, count in file_counts.most_common():
    bar = chr(9608) * min(50, count // 10)
    print(f'  {name:<15s} {count:>6d} {bar}')

# Top vinculum-dense files
print(f'\n=== HIGHEST VINCULUM DENSITY ===')
for item in sorted(compression_data, key=lambda x: x['density'], reverse=True)[:15]:
    print(f'  {item["project"]}/{item["file"]:<40s} {item["lines"]:>4d} lines  '
          f'{item["vinculums"]:>4d} vinculums  {item["density"]:>5.1f}% density')

# Project statistics
print(f'\n=== PROJECT VINCULUM DENSITY ===')
project_stats = defaultdict(lambda: {'files': 0, 'vinculums': 0, 'size': 0})
for item in compression_data:
    p = item['project']
    project_stats[p]['files'] += 1
    project_stats[p]['vinculums'] += item['vinculums']
    project_stats[p]['size'] += item['size_bytes']

for proj, stats in sorted(project_stats.items(), key=lambda x: x[1]['vinculums'], reverse=True):
    density = stats['vinculums'] / max(1, stats['files'])
    size_kb = stats['size'] / 1024
    bar = chr(9608) * int(density / 2)
    print(f'  {proj:<25s} {stats["files"]:>4d} files  {stats["vinculums"]:>5d} vinculums  '
          f'{density:.1f}/file  {size_kb:.0f}KB  {bar}')

# Overall vinculum compression ratio
total_files = sum(s['files'] for s in project_stats.values())
total_vinculums = sum(s['vinculums'] for s in project_stats.values())
print(f'\n=== OVERALL VINCULUM COMPRESSION ===')
print(f'Total projects: {len(project_stats)}')
print(f'Total files: {total_files}')
print(f'Total vinculums: {total_vinculums:,}')
print(f'Mean density: {total_vinculums/max(1,total_files):.1f} vinculums/file')
print(f'Runtime: {__import__("time").time()-start:.1f}s')

# Save
output = {
    'scanner': 'vinculum_a100',
    'timestamp': datetime.now().isoformat(),
    'total_vinculums': total_vinculums,
    'total_files': total_files,
    'pattern_counts': dict(file_counts),
    'top_density': compression_data[:20],
    'project_stats': {k: dict(v) for k, v in project_stats.items()},
    'runtime_s': round(__import__('time').time()-start, 1)
}

out_path = Path.home() / 'Projects/trench_builder/vinculum_a100_scan.json'
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f'\nSaved: {out_path}')
print(json.dumps({'total_vinculums':total_vinculums,'files':total_files,
    'runtime_s':round(__import__('time').time()-start,1)}))
