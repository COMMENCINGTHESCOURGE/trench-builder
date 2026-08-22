#!/usr/bin/env python3
import json, os, urllib.request
from kagglesdk import KaggleClient
from kagglesdk.kernels.types.kernels_api_service import ApiListKernelSessionOutputRequest

cred = json.load(open(os.path.expanduser('~/.kaggle/kaggle.json')))
c = KaggleClient(); c.api_token = cred['key']; c.username = cred['username']
r = ApiListKernelSessionOutputRequest(); r.user_name = 'commencethescourge'; r.kernel_slug = 'scithary-genrator-auto-regenerator'
resp = c.kernels.kernels_api_client.list_kernel_session_output(r)
url = resp.files[0].url
dest = os.path.expanduser('~/Projects/trench_builder/scithary_data.json')
urllib.request.urlretrieve(url, dest)
d = json.load(open(dest))
m = d.get('metadata', {})
print('OK', os.path.getsize(dest), 'bytes')
print('generator:', m.get('generator'))
print('generated_at:', m.get('generated_at'))
print('top keys:', list(d.keys()))
for k in ('regions', 'region_overlap', 'node_integrity', 'connection_topology', 'energy_pulses'):
    v = d.get(k)
    print(k, type(v).__name__, len(v) if hasattr(v, '__len__') else v)
