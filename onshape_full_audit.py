"""
ONSHAPE PARTS BANK AUDIT
Scans all named documents, extracts feature trees, and catalogs
the engineering methods and intentions behind each design.
"""
import urllib.request, json, base64, sys
from pathlib import Path
from collections import Counter

env = {}
for p in [Path.home() / 'AppData/Local/hermes/.env', Path.home() / '.env']:
    if p.exists():
        with open(p) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    k, v = line.strip().split('=', 1)
                    env[k] = v

ACCESS_KEY = env.get('ONSHAPE_ACCESS_KEY', '') or env.get('ONSHAPE_ACCESS_KEY_CLAUDECODE', '')
SECRET_KEY = env.get('ONSHAPE_SECRET_KEY', '')
AUTH = base64.b64encode((ACCESS_KEY + ':' + SECRET_KEY).encode()).decode()
HDR = {'Accept': 'application/json;charset=UTF-8;qs=0.09', 'Authorization': 'Basic ' + AUTH}

def api(url):
    req = urllib.request.Request(url, headers=HDR)
    resp = urllib.request.urlopen(req, timeout=60)
    return json.loads(resp.read())

# Feature type classification
METHOD_MAP = {
    'BTMSketch-151': 'SKETCH',
    'BTMFeature-134': 'FEATURE',
}

def classify_feature(f):
    """Extract the engineering method from a feature node."""
    bt = f.get('btType', '')
    name = f.get('name', '') or f.get('message', {}).get('name', '')
    ftype = f.get('featureType', '')
    suppressed = f.get('suppressed', False) or f.get('message', {}).get('suppressed', False)
    
    # Detect sketch geometry types
    sketch_types = []
    if bt == 'BTMSketch-151':
        for ent in f.get('entities', []):
            geo = ent.get('geometry', {})
            geo_bt = geo.get('btType', '')
            if 'Spline' in geo_bt or 'Interpolated' in geo_bt:
                sketch_types.append('SPLINE')
            elif 'Circle' in geo_bt:
                sketch_types.append('CIRCLE')
            elif 'Line' in geo_bt:
                sketch_types.append('LINE')
            elif 'Ellipse' in geo_bt:
                sketch_types.append('ELLIPSE')
            elif 'Conic' in geo_bt:
                sketch_types.append('CONIC')
            else:
                sketch_types.append('OTHER')
    
    # Extract operation type from name
    op = name.split(' ')[0].upper() if name else ftype.upper()
    
    return {
        'name': name,
        'operation': op,
        'sketch_geometry': list(set(sketch_types)),
        'suppressed': suppressed,
    }

# Collect all named documents
print('Scanning all named Onshape documents...')
all_docs = []
url = 'https://cad.onshape.com/api/v10/documents?limit=20'
while url:
    data = api(url)
    for d in data.get('items', []):
        name = d.get('name', '')
        if name.lower() not in ('untitled document', 'untitled', ''):
            all_docs.append({
                'id': d['id'],
                'name': name,
                'created': d.get('createdAt', '')[:10],
                'modified': d.get('modifiedAt', '')[:10],
            })
    url = data.get('next')

print('Found ' + str(len(all_docs)) + ' named documents.\n')

# Process each document
results = []
global_ops = Counter()
global_sketch_geo = Counter()

for doc in sorted(all_docs, key=lambda x: x['created']):
    doc_id = doc['id']
    entry = {
        'name': doc['name'],
        'created': doc['created'],
        'modified': doc['modified'],
        'features': [],
        'total_features': 0,
        'operations': Counter(),
        'sketch_geometry': Counter(),
        'has_splines': False,
        'has_fillets': False,
        'has_thicken': False,
        'has_loft': False,
        'has_sweep': False,
        'has_revolve': False,
        'has_boolean': False,
        'has_shell': False,
        'has_pattern': False,
        'has_mirror': False,
        'error': None,
    }
    
    try:
        ws = api('https://cad.onshape.com/api/v10/documents/' + doc_id + '/workspaces')
        ws_id = ws[0]['id']
        elements = api('https://cad.onshape.com/api/v10/documents/' + doc_id + '/elements')
        
        for elem in elements:
            if elem.get('elementType') != 'PARTSTUDIO' and elem.get('type') != 'Part Studio':
                continue
            
            eid = elem['id']
            feat_url = 'https://cad.onshape.com/api/v10/partstudios/d/' + doc_id + '/w/' + ws_id + '/e/' + eid + '/features'
            
            try:
                fdata = api(feat_url)
                features = fdata.get('features', [])
                entry['total_features'] += len(features)
                
                for f in features:
                    info = classify_feature(f)
                    entry['operations'][info['operation']] += 1
                    global_ops[info['operation']] += 1
                    
                    for sg in info['sketch_geometry']:
                        entry['sketch_geometry'][sg] += 1
                        global_sketch_geo[sg] += 1
                    
                    op_lower = info['operation'].lower()
                    if 'SPLINE' in info['sketch_geometry']:
                        entry['has_splines'] = True
                    if 'fillet' in op_lower:
                        entry['has_fillets'] = True
                    if 'thicken' in op_lower:
                        entry['has_thicken'] = True
                    if 'loft' in op_lower:
                        entry['has_loft'] = True
                    if 'sweep' in op_lower:
                        entry['has_sweep'] = True
                    if 'revolve' in op_lower:
                        entry['has_revolve'] = True
                    if 'boolean' in op_lower:
                        entry['has_boolean'] = True
                    if 'shell' in op_lower:
                        entry['has_shell'] = True
                    if 'pattern' in op_lower or 'linear' in op_lower or 'circular' in op_lower:
                        entry['has_pattern'] = True
                    if 'mirror' in op_lower:
                        entry['has_mirror'] = True
                    
                    entry['features'].append(info['operation'] + ': ' + info['name'])
            except:
                pass
    except Exception as e:
        entry['error'] = str(e)[:80]
    
    results.append(entry)
    
    # Progress
    status = entry['name'] + ' (' + entry['created'] + ') - ' + str(entry['total_features']) + ' features'
    if entry['error']:
        status += ' [ERROR]'
    print(status)

# Output full report as JSON
report = {
    'total_named_docs': len(all_docs),
    'total_features_scanned': sum(r['total_features'] for r in results),
    'global_operation_counts': dict(global_ops.most_common(30)),
    'global_sketch_geometry': dict(global_sketch_geo.most_common(10)),
    'documents': [],
}

for r in results:
    doc_entry = {
        'name': r['name'],
        'created': r['created'],
        'modified': r['modified'],
        'total_features': r['total_features'],
        'operations': dict(r['operations'].most_common(10)),
        'sketch_geometry': dict(r['sketch_geometry'].most_common(5)),
        'advanced_methods': [],
        'feature_list': r['features'][:20],
    }
    
    if r['has_splines']:
        doc_entry['advanced_methods'].append('INTERPOLATED_SPLINES')
    if r['has_loft']:
        doc_entry['advanced_methods'].append('LOFT')
    if r['has_sweep']:
        doc_entry['advanced_methods'].append('SWEEP')
    if r['has_revolve']:
        doc_entry['advanced_methods'].append('REVOLVE')
    if r['has_thicken']:
        doc_entry['advanced_methods'].append('SURFACE_THICKEN')
    if r['has_boolean']:
        doc_entry['advanced_methods'].append('BOOLEAN')
    if r['has_shell']:
        doc_entry['advanced_methods'].append('SHELL')
    if r['has_fillets']:
        doc_entry['advanced_methods'].append('FILLET')
    if r['has_pattern']:
        doc_entry['advanced_methods'].append('PATTERN')
    if r['has_mirror']:
        doc_entry['advanced_methods'].append('MIRROR')
    
    if r['error']:
        doc_entry['error'] = r['error']
    
    report['documents'].append(doc_entry)

out_path = str(Path(__file__).parent / 'onshape_audit_report.json')
with open(out_path, 'w') as f:
    json.dump(report, f, indent=2)

print('\n' + '=' * 60)
print('AUDIT COMPLETE')
print('Total named documents: ' + str(report['total_named_docs']))
print('Total features scanned: ' + str(report['total_features_scanned']))
print('Report saved to: ' + out_path)
print('\nTop 15 operations used across all projects:')
for op, count in global_ops.most_common(15):
    print('  ' + op + ': ' + str(count) + 'x')
print('\nSketch geometry types:')
for sg, count in global_sketch_geo.most_common(10):
    print('  ' + sg + ': ' + str(count) + 'x')
