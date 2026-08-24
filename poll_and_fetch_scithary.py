#!/usr/bin/env python3
import json, os, time, urllib.request
from kagglesdk import KaggleClient
from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelSessionStatusRequest, ApiListKernelSessionOutputRequest

cred = json.load(open(os.path.expanduser('~/.kaggle/kaggle.json')))
c = KaggleClient(); c.api_token = cred['key']; c.username = cred['username']
st = None
for i in range(38):
    time.sleep(15)
    r = ApiGetKernelSessionStatusRequest(); r.user_name = 'commencethescourge'; r.kernel_slug = 'scithary-genrator-auto-regenerator'
    s = c.kernels.kernels_api_client.get_kernel_session_status(r)
    st = s.status
    print(i * 15, st, flush=True)
    if st in ('COMPLETE', 'ERROR'):
        break

if st != 'COMPLETE':
    raise SystemExit(f'kernel status {st}')

r = ApiListKernelSessionOutputRequest(); r.user_name = 'commencethescourge'; r.kernel_slug = 'scithary-genrator-auto-regenerator'
resp = c.kernels.kernels_api_client.list_kernel_session_output(r)
print([f.url.split('/')[-1] for f in resp.files])

dest = os.path.expanduser('~/Projects/trench_builder/scithary_data.json')
urllib.request.urlretrieve(resp.files[0].url, dest)
d = json.load(open(dest)); m = d.get('metadata', {})
print('OK', os.path.getsize(dest), 'bytes')
print('generated_at:', m.get('generated_at'))
for k in d:
    v = d[k]
    print(k, type(v).__name__, len(v) if hasattr(v, '__len__') else v)
