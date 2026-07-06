import urllib.request, json, base64
from pathlib import Path

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

# Priority docs to inspect
PRIORITY_NAMES = ['boomhower', 'spacedoor', 'spacehenge', 'spiral', 'flight528', 'ghost', 'arm', 'space mining']

# Find them
targets = {}
url = 'https://cad.onshape.com/api/v10/documents?limit=20'
while url:
    data = api(url)
    for d in data.get('items', []):
        name = d.get('name', '')
        if name in PRIORITY_NAMES or name.lower() in PRIORITY_NAMES:
            targets[d['id']] = {
                'name': name,
                'created': d.get('createdAt','')[:10],
                'modified': d.get('modifiedAt','')[:10],
                'defaultWorkspaceId': d.get('defaultWorkspace', {}).get('id', '')
            }
    url = data.get('next')

print('Found ' + str(len(targets)) + ' priority documents.\n')

for doc_id, info in sorted(targets.items(), key=lambda x: x[1]['created']):
    print('=' * 60)
    print('DOC: ' + info['name'])
    print('Created: ' + info['created'] + ' | Modified: ' + info['modified'])
    
    ws_id = info['defaultWorkspaceId']
    
    # If no default workspace in doc list, fetch it
    if not ws_id:
        try:
            ws = api('https://cad.onshape.com/api/v10/documents/' + doc_id + '/workspaces')
            ws_id = ws[0]['id'] if ws else ''
        except:
            print('  Could not get workspace.')
            continue
    
    try:
        elements = api('https://cad.onshape.com/api/v10/documents/' + doc_id + '/elements?withThumbnails=false')
        
        for elem in elements:
            etype = elem.get('type', '')
            eid = elem.get('id', '')
            ename = elem.get('name', 'unnamed')
            
            if etype != 'PARTSTUDIO':
                continue
            
            print('\n  [PART STUDIO] ' + ename)
            
            # Try features endpoint
            feat_url = 'https://cad.onshape.com/api/v10/partstudios/d/' + doc_id + '/w/' + ws_id + '/e/' + eid + '/features'
            try:
                fdata = api(feat_url)
                features = fdata.get('features', [])
                
                if not features:
                    print('    (no features returned by API)')
                    continue
                
                print('    Feature count: ' + str(len(features)))
                print('')
                
                for f in features:
                    ftype = f.get('featureType', 'unknown')
                    msg = f.get('message', {})
                    fname = msg.get('name', '') or f.get('name', '')
                    suppressed = msg.get('suppressed', False)
                    
                    # Pull sketch entities if sketch
                    extra = ''
                    if ftype.lower() == 'sketch':
                        entities = msg.get('entities', [])
                        entity_types = list(set(e.get('type','').replace('BTMSketch','').lower() for e in entities if e.get('type')))
                        if entity_types:
                            extra = ' [' + ', '.join(entity_types[:5]) + ']'
                    
                    # Pull loft profiles
                    if ftype.lower() == 'loft':
                        profiles = msg.get('profilesQuery', [])
                        extra = ' [' + str(len(profiles)) + ' profiles]'
                    
                    flag = ' <<SUPPRESSED>>' if suppressed else ''
                    print('    -> ' + ftype.upper() + ': ' + fname + extra + flag)
                    
            except Exception as e:
                err = str(e)
                if hasattr(e, 'read'):
                    err = e.read().decode()[:150]
                print('    Feature API error: ' + err)
                
    except Exception as e:
        print('  ERROR: ' + str(e)[:100])

print('\nDONE.')
