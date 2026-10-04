#!/usr/bin/env python3
"""Explicit registration avoids copying or guessing another person's session history."""
import argparse,json,os,pathlib,re,shlex,time
from common import run, unique, config
STORE=pathlib.Path('~/.local/state/headless-kit/restore.json').expanduser()
def saved(): return json.loads(STORE.read_text()) if STORE.exists() else {}
def write(data):
    STORE.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    tmp=STORE.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2));tmp.chmod(0o600);tmp.replace(STORE)
def register(label,kind,session,cwd):
    p=unique(label)
    if p.get('agent')!=kind: raise RuntimeError('Start the matching agent and register its own session ID')
    if not re.fullmatch(r'[a-zA-Z0-9_-]{8,128}',session): raise RuntimeError('Invalid session ID')
    cwd=str(pathlib.Path(cwd).expanduser().resolve())
    if not pathlib.Path(cwd).is_dir(): raise RuntimeError('Project folder does not exist')
    data=saved();data[label]={'kind':kind,'session':session,'cwd':cwd};write(data)
def park(label):
    p=unique(label)
    rec=saved().get(label)
    if not rec or p.get('agent')!=rec['kind']: raise RuntimeError('Register this agent session before parking')
    if p.get('agent_status') not in ('idle','done'): raise RuntimeError('Only idle/done agents can be parked')
    run('pane','send-keys',p['pane_id'],'ctrl+c','ctrl+c')
    for _ in range(20):
        live=run('pane','get',p['pane_id']).get('pane',{})
        if live and not live.get('agent'): return 'Parked; history stays in the agent account'
        time.sleep(.25)
    raise RuntimeError('Agent still running; inspect it before trying again')
def restore(label):
    p=unique(label);rec=saved().get(label)
    if not rec: raise RuntimeError('No registered session')
    if p.get('agent'): raise RuntimeError('Pane already has an agent')
    info=run('pane','process-info','--pane',p['pane_id']).get('process_info',{})
    fg=info.get('foreground_processes',[])
    if not fg or any(pathlib.Path((x.get('argv') or [''])[0]).name not in ('bash','zsh','fish','sh','dash') for x in fg):
        raise RuntimeError('Cannot verify an available foreground shell')
    cwd=pathlib.Path(rec['cwd'])
    if not cwd.is_dir(): raise RuntimeError('Saved project folder is missing')
    argv=['claude','--resume',rec['session']] if rec['kind']=='claude' else ['codex','resume',rec['session']]
    run('pane','run',p['pane_id'],'cd '+shlex.quote(str(cwd))+' && '+shlex.join(argv))
    return 'Resume launched; complete trust/login prompts yourself'
def main():
    a=argparse.ArgumentParser();s=a.add_subparsers(dest='cmd',required=True)
    r=s.add_parser('register');r.add_argument('label');r.add_argument('kind',choices=['claude','codex']);r.add_argument('session_id');r.add_argument('cwd')
    for name in ('park','restore'): s.add_parser(name).add_argument('label')
    s.add_parser('list');x=a.parse_args()
    if x.cmd=='register':register(x.label,x.kind,x.session_id,x.cwd);print('Registered')
    elif x.cmd=='list':print(json.dumps(saved(),indent=2))
    else:print(globals()[x.cmd](x.label))
if __name__=='__main__':main()
