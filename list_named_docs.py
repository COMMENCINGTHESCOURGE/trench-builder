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

# Paginate through all docs collecting named ones
named = []
url = 'https://cad.onshape.com/api/v10/documents?limit=20'
while url and len(named) < 200:
    data = api(url)
    for d in data.get('items', []):
        name = d.get('name', '')
        if name.lower() not in ('untitled document', 'untitled', ''):
            named.append({'id': d['id'], 'name': name, 'modified': d.get('modifiedAt','')[:10]})
    url = data.get('next')

print('Named docs found: ' + str(len(named)))
print('')
for d in named[:30]:
    print('  ' + d['modified'] + ' | ' + d['name'])
