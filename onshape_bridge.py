#!/usr/bin/env python
"""
ONSHAPE → TRENCH BUILDER BRIDGE v1.0
Auto-imports parametric CAD geometry into the construction environment.
Pulls parts from Onshape API, exports as STL, generates Three.js loader code.
"""
import os, json, base64, urllib.request

# ── Credentials (from .env) ──
def load_env():
    env = {}
    env_path = os.path.expanduser(r'~\AppData\Local\hermes\.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    k, v = line.strip().split('=', 1)
                    env[k] = v
    return env

env = load_env()
ACCESS = env.get('ONSHAPE_ACCESS_KEY', '')
SECRET = env.get('ONSHAPE_SECRET_KEY', '')
DOC_ID = 'e60c4803eaf2ac8be492c18e'  # Onshape API Guide document
AUTH = base64.b64encode(f'{ACCESS}:{SECRET}'.encode()).decode()
HDR = {'Accept': 'application/json;charset=UTF-8;qs=0.09', 'Authorization': f'Basic {AUTH}'}

def api(url):
    req = urllib.request.Request(url, headers=HDR)
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read())

def export_stl(doc_id, ws_id, elem_id, part_id, filename):
    """Export a single part as STL binary."""
    url = f'https://cad.onshape.com/api/v10/parts/d/{doc_id}/w/{ws_id}/e/{elem_id}/partid/{part_id}/stl'
    req = urllib.request.Request(url, headers={**HDR, 'Accept': 'application/octet-stream'})
    resp = urllib.request.urlopen(req, timeout=60)
    with open(filename, 'wb') as f:
        f.write(resp.read())
    return os.path.getsize(filename)

def sync_all():
    """Pull all elements from Onshape and export as STL."""
    export_dir = os.path.join(os.path.dirname(__file__), 'cad_imports')
    os.makedirs(export_dir, exist_ok=True)
    
    # Get workspace
    workspaces = api(f'https://cad.onshape.com/api/v10/documents/{DOC_ID}/workspaces')
    ws_id = workspaces[0]['id']
    print(f'Workspace: {ws_id}')
    
    # Get elements
    elements = api(f'https://cad.onshape.com/api/v10/documents/{DOC_ID}/elements')
    print(f'Elements: {len(elements)}')
    
    manifest = []
    for elem in elements:
        eid = elem['id']
        ename = elem['name']
        etype = elem.get('type', '?')
        
        try:
            parts = api(f'https://cad.onshape.com/api/v10/parts/d/{DOC_ID}/w/{ws_id}/e/{eid}')
            for part in parts:
                pid = part.get('partId')
                pname = part.get('name', f'part_{pid}')
                safe_name = f'{ename}_{pname}'.replace(' ', '_').replace('/', '_')
                fname = os.path.join(export_dir, f'{safe_name}.stl')
                
                size = export_stl(DOC_ID, ws_id, eid, pid, fname)
                print(f'  [OK] {safe_name} ({size:,} bytes)')
                manifest.append({
                    'element': ename, 'type': etype, 'part': pname,
                    'file': fname, 'size': size
                })
        except Exception as e:
            print(f'  [ERR] {ename}: {e}')
    
    # Save manifest
    with open(os.path.join(export_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f'\n[OK] {len(manifest)} parts exported')
    return manifest

if __name__ == '__main__':
    sync_all()
