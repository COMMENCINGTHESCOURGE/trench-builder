import urllib.request, json, base64, os, sys
from pathlib import Path

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

ACCESS_KEY = ''
for ak in ACCESS_KEYS:
    if ak:
        ACCESS_KEY = ak
        break

if not ACCESS_KEY or not SECRET_KEY:
    print("ERROR: Onshape credentials not found in .env")
    sys.exit(1)

AUTH = base64.b64encode(f'{ACCESS_KEY}:{SECRET_KEY}'.encode()).decode()
HDR = {'Accept': 'application/json;charset=UTF-8;qs=0.09', 'Authorization': f'Basic {AUTH}'}

def api(url):
    req = urllib.request.Request(url, headers=HDR)
    resp = urllib.request.urlopen(req, timeout=60)
    return json.loads(resp.read())

try:
    print("Fetching documents...")
    # Fetch user's documents (limit 50, sort by createdAt ascending)
    docs = api('https://cad.onshape.com/api/v10/documents?limit=20&sortColumn=createdAt&sortOrder=asc')
    
    if not docs or 'items' not in docs:
        print("No documents found or bad response.")
        sys.exit(0)
        
    print("\nOLDEST ONSHAPE DOCUMENTS:")
    print("-" * 50)
    for d in docs['items']:
        name = d.get('name', 'Unknown')
        created = d.get('createdAt', 'Unknown')
        print(f"Created: {created} | Name: {name}")
except Exception as e:
    body = e.read().decode() if hasattr(e, 'read') else str(e)
    print(f"API Error: {body}")
