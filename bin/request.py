#!/usr/bin/env python3
"""Single SSH request, also used by Mac Hammerspoon. No shell interpolation of text."""
import json,subprocess,sys
from common import config
def request(m):
    c=config()
    p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8',c['vm_host'],
       'python3 .local/share/headless-kit/bin/connect.py'],input=json.dumps(m)+'\n',capture_output=True,text=True,timeout=30)
    if p.returncode:raise RuntimeError(p.stderr.strip() or 'SSH or brain connection failed')
    return json.loads(p.stdout.splitlines()[0])
if __name__=='__main__':
    try:print(json.dumps(request(json.loads(sys.stdin.read()))),flush=True)
    except Exception as e:print(json.dumps({'message':str(e),'error':True}),flush=True);sys.exit(1)
