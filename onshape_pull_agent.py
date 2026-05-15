#!/usr/bin/env python3
"""
ONSHAPE AUTONOMOUS PULL AGENT v1.0
Pulls every part from every Onshape document until it hits a wall.
Deploy as Hermes cron job for continuous CAD ingestion.

Usage: python onshape_pull_agent.py [--doc-id DOC_ID]
"""
import urllib.request, json, base64, os, sys, time
from pathlib import Path

# ── Load credentials ──
def load_env():
    env = {}
    for p in [Path.home() / 'AppData/Local/hermes/.env', Path.home() / '.env']:
        if p.exists():
            with open(p) as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        k, v = line.strip().split('=', 1)
                        env[k] = v
    return env

env = load_env()
ACCESS_KEYS = [
    env.get('ONSHAPE_ACCESS_KEY', ''),
    env.get('ONSHAPE_ACCESS_KEY_CLAUDECODE', ''),
]
SECRET_KEY = env.get('ONSHAPE_SECRET_KEY', '')

if not any(ACCESS_KEYS) or not SECRET_KEY:
    print("ERROR: Onshape credentials not found in .env")
    sys.exit(1)

# Use first working access key
for ak in ACCESS_KEYS:
    if ak:
        ACCESS_KEY = ak
        break

AUTH = base64.b64encode(f'{ACCESS_KEY}:{SECRET_KEY}'.encode()).decode()
HDR = {'Accept': 'application/json;charset=UTF-8;qs=0.09', 'Authorization': f'Basic {AUTH}'}

# ── API Helper ──
def api(url, raw=False):
    req = urllib.request.Request(url, headers=HDR if not raw else {**HDR, 'Accept': 'application/octet-stream'})
    resp = urllib.request.urlopen(req, timeout=60)
    return resp.read() if raw else json.loads(resp.read())

# ── Main Pull Loop ──
def pull_all(doc_id, export_dir):
    os.makedirs(export_dir, exist_ok=True)
    
    # Get workspace
    print(f'Document: {doc_id}')
    workspaces = api(f'https://cad.onshape.com/api/v10/documents/{doc_id}/workspaces')
    ws_id = workspaces[0]['id']
    print(f'Workspace: {ws_id}')
    
    # Get all elements
    elements = api(f'https://cad.onshape.com/api/v10/documents/{doc_id}/elements')
    print(f'Elements to process: {len(elements)}')
    
    stats = {'total': 0, 'size': 0, 'cached': 0, 'exported': 0, 'failed': 0}
    manifest_path = os.path.join(export_dir, 'manifest.json')
    
    # Load existing manifest
    existing = set()
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            old = json.load(f)
            for p in old.get('parts', []):
                existing.add(p.get('file', ''))
    
    for elem in elements:
        eid = elem['id']
        ename = elem['name']
        etype = elem.get('type', '?')
        
        try:
            parts = api(f'https://cad.onshape.com/api/v10/parts/d/{doc_id}/w/{ws_id}/e/{eid}')
            
            for part in parts:
                pid = part.get('partId')
                pname = part.get('name', f'part_{pid}')
                safe = f'{ename}_{pname}'.replace(' ', '_').replace('/', '_')[:80]
                fname = os.path.join(export_dir, f'{safe}.stl')
                
                if os.path.exists(fname):
                    stats['cached'] += 1
                    stats['total'] += 1
                    continue
                
                # Export STL
                stl_url = f'https://cad.onshape.com/api/v10/parts/d/{doc_id}/w/{ws_id}/e/{eid}/partid/{pid}/stl'
                stl_data = api(stl_url, raw=True)
                
                with open(fname, 'wb') as f:
                    f.write(stl_data)
                
                stats['exported'] += 1
                stats['total'] += 1
                stats['size'] += len(stl_data)
                print(f'  ✓ {safe} ({len(stl_data):,} bytes)')
                
        except Exception as e:
            stats['failed'] += 1
            body = e.read().decode() if hasattr(e, 'read') else str(e)
            print(f'  ✗ {ename} [{etype}]: {body[:100]}')
    
    # Summary
    print(f'\n{"="*50}')
    print(f'{"WALL HIT" if stats["failed"] > 0 else "COMPLETE — all parts pulled"}')
    print(f'Total parts: {stats["total"]} (cached: {stats["cached"]}, new: {stats["exported"]}, failed: {stats["failed"]})')
    print(f'New data: {stats["size"]/1e6:.1f} MB')
    return stats

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--doc-id', default='e60c4803eaf2ac8be492c18e')
    parser.add_argument('--export-dir', default=None)
    args = parser.parse_args()
    
    export_dir = args.export_dir or os.path.join(os.path.dirname(__file__), 'cad_imports')
    pull_all(args.doc_id, export_dir)
