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
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        raw = resp.read()
        return json.loads(raw), None
    except urllib.error.HTTPError as e:
        return None, 'HTTP ' + str(e.code) + ': ' + e.read().decode()[:200]
    except Exception as e:
        return None, str(e)

# Find boomhower
boomhower_id = None
url = 'https://cad.onshape.com/api/v10/documents?limit=20'
while url:
    data, err = api(url)
    if err or not data:
        break
    for d in data.get('items', []):
        if d.get('name') == 'boomhower':
            boomhower_id = d['id']
            print('FOUND boomhower: ' + boomhower_id)
            print('defaultWorkspace: ' + str(d.get('defaultWorkspace')))
            break
    if boomhower_id:
        break
    url = data.get('next')

if not boomhower_id:
    print('Could not find boomhower doc.')
    exit()

# Step 1: Get workspaces
print('\n--- WORKSPACES ---')
ws_data, err = api('https://cad.onshape.com/api/v10/documents/' + boomhower_id + '/workspaces')
if err:
    print('Workspace error: ' + err)
    exit()
print(json.dumps(ws_data, indent=2)[:500])
ws_id = ws_data[0]['id']
print('Using ws_id: ' + ws_id)

# Step 2: Get elements
print('\n--- ELEMENTS ---')
elem_data, err = api('https://cad.onshape.com/api/v10/documents/' + boomhower_id + '/elements')
if err:
    print('Elements error: ' + err)
    exit()
print(json.dumps(elem_data, indent=2)[:800])

# Step 3: Try features for each element
for elem in elem_data:
    eid = elem.get('id')
    etype = elem.get('type')
    ename = elem.get('name')
    print('\n--- FEATURES for [' + etype + '] ' + ename + ' ---')
    
    feat_url = 'https://cad.onshape.com/api/v10/partstudios/d/' + boomhower_id + '/w/' + ws_id + '/e/' + eid + '/features'
    print('URL: ' + feat_url)
    feat_data, err = api(feat_url)
    if err:
        print('Error: ' + err)
    else:
        features = feat_data.get('features', [])
        print('Feature count: ' + str(len(features)))
        for f in features[:5]:
            print('  ' + json.dumps(f, indent=2)[:300])
