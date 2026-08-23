import os
from kagglesdk import KaggleClient
from kagglesdk.kernels.types.kernels_api_service import (
    ApiListKernelSessionOutputRequest, ApiDownloadKernelOutputRequest)

c = KaggleClient()

try:
    req = ApiListKernelSessionOutputRequest()
    req.user_name = "commencethescourge"
    req.kernel_slug = "scithary-genrator"
    resp = c.kernels.kernels_api_client.list_kernel_session_output(req)
    print("session output ok:", resp)
except Exception as e:
    print("list_kernel_session_output failed:", e)

try:
    dl = ApiDownloadKernelOutputRequest()
    dl.owner_slug = "commencethescourge"
    dl.kernel_slug = "scithary-genrator"
    red = c.kernels.kernels_api_client.download_kernel_output(dl)
    print("redirect:", red)
    url = getattr(red, "target_url", None) or str(red)
    import requests
    r = requests.get(url)
    print("status", r.status_code, "len", len(r.content))
    if r.ok:
        outp = os.path.expanduser("~/Projects/trench_builder/scithary_data.json")
        with open(outp, "wb") as fh:
            fh.write(r.content)
        print("saved", outp)
except Exception as e:
    print("download failed:", repr(e))
