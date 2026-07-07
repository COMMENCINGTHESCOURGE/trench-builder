#!/usr/bin/env python
"""
ONSHAPE FEATURE TREE INSPECTOR
Reads the parametric feature tree from Onshape documents.
Shows what CAD operations were used: lofts, sweeps, shells, fillets, booleans etc.
"""
import urllib.request, json, base64, os, sys
from pathlib import Path
from collections import Counter

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
ACCESS_KEYS = [env.get('ONSHAPE_ACCESS_KEY', ''), env.get('ONSHAPE_ACCESS_KEY_CLAUDECODE', '')]
SECRET_KEY = env.get('ONSHAPE_SECRET_KEY', '')
ACCESS_KEY = env.get('ONSHAPE_ACCESS_KEY', '') or env.get('ONSHAPE_ACCESS_KEY_CLAUDECODE', '')

if not ACCESS_KEY or not SECRET_KEY:
    print("ERROR: Onshape credentials not found in .env")
    sys.exit(1)

AUTH = base64.b64encode(f'{ACCESS_KEY}:{SECRET_KEY}'.encode()).decode()
HDR = {'Accept': 'application/json;charset=UTF-8;qs=0.09', 'Authorization': f'Basic {AUTH}'}

def api(url):
    req = urllib.request.Request(url, headers=HDR)
    resp = urllib.request.urlopen(req, timeout=60)
    return json.loads(resp.read())

# Advanced feature types that indicate sophisticated CAD work
ADVANCED_FEATURES = {
    'loft':         '🔺 LOFT (complex surface transition)',
    'sweep':        '🌀 SWEEP (path-driven geometry)',
    'shell':        '🐚 SHELL (hollow thin-wall)',
    'rib':          '⚙️  RIB (structural reinforcement)',
    'draft':        '📐 DRAFT (mold angle)',
    'helix':        '🔩 HELIX (spring/thread geometry)',
    'coil':         '🔩 COIL (spring geometry)',
    'ruled':        '📏 RULED SURFACE',
    'fillet':       '🔵 FILLET (stress-relief rounding)',
    'chamfer':      '✂️  CHAMFER (edge break)',
    'boolean':      '🔷 BOOLEAN (combine/subtract)',
    'mirror':       '🪞 MIRROR (symmetry op)',
    'pattern':      '🔄 PATTERN (linear/circular repeat)',
    'revolve':      '🔃 REVOLVE (rotational solid)',
    'extrude':      '📦 EXTRUDE (base operation)',
    'sketch':       '✏️  SKETCH (2D constraint layer)',
    'plane':        '📐 REFERENCE PLANE',
    'mate':         '🔗 MATE CONNECTOR (assembly joint)',
    'transform':    '🔄 TRANSFORM',
}

def get_feature_tree(doc_id, ws_id, elem_id):
    url = f'https://cad.onshape.com/api/v10/partstudios/d/{doc_id}/w/{ws_id}/e/{elem_id}/features'
    try:
        data = api(url)
        return data.get('features', [])
    except:
        return []

def inspect_documents(limit=20):
    print("Fetching named documents (skipping 'Untitled')...\n")
    
    # Get all docs - limit must be <=20 per Onshape API
    url = f'https://cad.onshape.com/api/v10/documents?limit=20'
    docs = api(url)
    
    global_feature_counts = Counter()
    advanced_docs = []
    
    named_docs = [d for d in docs.get('items', []) if d.get('name', '').lower() not in ('untitled document', 'untitled')]
    
    print(f"Found {len(named_docs)} named documents. Inspecting feature trees...\n")
    print("=" * 60)
    
    for doc in named_docs[:limit]:
        doc_id = doc['id']
        doc_name = doc.get('name', 'Unknown')
        modified = doc.get('modifiedAt', '')[:10]
        
        try:
            workspaces = api(f'https://cad.onshape.com/api/v10/documents/{doc_id}/workspaces')
            ws_id = workspaces[0]['id']
            elements = api(f'https://cad.onshape.com/api/v10/documents/{doc_id}/elements')
            
            doc_features = Counter()
            for elem in elements:
                if elem.get('type') == 'PARTSTUDIO':
                    features = get_feature_tree(doc_id, ws_id, elem['id'])
                    for f in features:
                        ftype = f.get('featureType', '').lower()
                        doc_features[ftype] += 1
                        global_feature_counts[ftype] += 1
            
            if doc_features:
                # Score sophistication
                advanced_score = sum(
                    count for ftype, count in doc_features.items()
                    if any(k in ftype for k in ['loft', 'sweep', 'shell', 'helix', 'rib', 'boolean', 'revolve'])
                )
                
                print(f"\n📁 {doc_name} ({modified})")
                print(f"   Total features: {sum(doc_features.values())} | Advanced score: {advanced_score}")
                
                # Print top features
                for ftype, count in doc_features.most_common(8):
                    label = next((v for k, v in ADVANCED_FEATURES.items() if k in ftype.lower()), f'   {ftype}')
                    print(f"   {label}: {count}x")
                
                if advanced_score > 0:
                    advanced_docs.append((doc_name, advanced_score, modified))
                    
        except Exception as e:
            print(f"\n📁 {doc_name} — could not read features: {str(e)[:60]}")
    
    print("\n" + "=" * 60)
    print("\n🏆 MOST SOPHISTICATED DOCUMENTS (by advanced feature score):")
    for name, score, date in sorted(advanced_docs, key=lambda x: -x[1])[:10]:
        print(f"   Score {score:3d} | {name} ({date})")
    
    print("\n📊 GLOBAL FEATURE USAGE ACROSS ALL INSPECTED DOCS:")
    for ftype, count in global_feature_counts.most_common(15):
        label = next((v for k, v in ADVANCED_FEATURES.items() if k in ftype.lower()), ftype)
        print(f"   {label}: {count}x total")

if __name__ == '__main__':
    inspect_documents(limit=30)
