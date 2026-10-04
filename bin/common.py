import json, os, pathlib, subprocess
CONFIG = pathlib.Path(os.environ.get('KIT_CONFIG', '~/.config/headless-kit/kit.json')).expanduser()
def config():
    return json.loads(CONFIG.read_text())
def run(*args):
    c=config()
    p=subprocess.run([c.get('herdr','herdr'),'--session',c['session'],*args],capture_output=True,text=True,timeout=15)
    if p.returncode: raise RuntimeError(p.stderr.strip() or p.stdout.strip() or 'Herdr command failed')
    data=json.loads(p.stdout) if p.stdout.strip() else {}
    if 'error' in data: raise RuntimeError(str(data['error']))
    return data.get('result',data)
def panes(): return run('pane','list').get('panes',[])
def unique(label):
    matches=[p for p in panes() if p.get('label','').casefold()==label.casefold()]
    if len(matches)!=1: raise RuntimeError('Use a unique, exact pane label')
    return matches[0]
def focus(p):
    import socket
    c=config();path=os.path.expanduser(c['socket'])
    with socket.socket(socket.AF_UNIX) as s:
        s.settimeout(5);s.connect(path)
        s.sendall((json.dumps({'id':'kit','method':'pane.focus','params':{'pane_id':p['pane_id']}})+'\n').encode())
        answer=json.loads(s.makefile('r').readline())
        if 'error' in answer: raise RuntimeError(str(answer['error']))
