#!/usr/bin/env python3
import argparse,json,pathlib,shutil,sys,subprocess
from common import config
p=argparse.ArgumentParser();p.add_argument('role',choices=['vm','desktop']);a=p.parse_args();c=config();bad=[]
if sys.version_info<(3,10):bad.append('Python 3.10+ required')
if a.role=='vm':
    if not shutil.which(c['herdr']):bad.append('Herdr missing')
    if not pathlib.Path(c['socket']).expanduser().exists():bad.append('Herdr session socket absent: start the dedicated service')
    if not pathlib.Path('~/.local/state/headless-kit/brain.sock').expanduser().exists():bad.append('Brain socket absent')
else:
    if c['vm_host']=='YOUR_VM_SSH_ALIAS':bad.append('Set vm_host to your own verified SSH alias')
    if not shutil.which('ssh'):bad.append('SSH client missing')
for b in bad:print('NEEDS: '+b)
if not bad:print('Basic files/config ready; complete the connection and desktop acceptance checks in README')
sys.exit(bool(bad))
