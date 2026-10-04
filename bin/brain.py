#!/usr/bin/env python3
"""One private Unix-socket brain; SSH transports JSON lines from desktop shells."""
import argparse,asyncio,json,os,pathlib,re
from common import panes, unique, focus, run
from sessions import park,restore
STATE=pathlib.Path(os.environ.get('KIT_STATE','~/.local/state/headless-kit')).expanduser()
SOCK=STATE/'brain.sock'
ACTION_LOCK=asyncio.Lock()
def decide(m):
    text=str(m.get('text','')).strip()
    if m.get('action')=='ping':return {'message':'Brain connected'}
    if text.casefold() in ('status','what needs me'):
        rows=panes()
        return {'message':'\n'.join(p.get('label','untitled')+': '+str(p.get('agent_status','shell')) for p in rows) or 'No panes', 'notify':True}
    match=re.fullmatch(r'(?:go to|focus|park|restore)\s+(.+)',text,re.I)
    if match:
        label=match.group(1);verb=text.split()[0].lower()
        if verb in ('go','focus'):
            p=unique(label);focus(p)
            if verb=='focus':run('pane','zoom',p['pane_id'],'--on')
            return {'message':'Focused '+p['label'],'raise':True}
        return {'message':(park if verb=='park' else restore)(label)}
    if text.casefold()=='unfocus':
        p=next((x for x in panes() if x.get('focused')),None)
        if not p:raise RuntimeError('No focused pane')
        run('pane','zoom',p['pane_id'],'--off');return {'message':'Layout restored'}
    # The shell must show the destination and prompt before requesting submission.
    task=re.fullmatch(r'tell\s+(.+?)\s+to\s+(.+)',text,re.I|re.S)
    if task:
        label,prompt=task.groups();p=unique(label)
        if p.get('agent_status') not in ('idle','done'):raise RuntimeError('Target must be idle or done')
        if m.get('confirmed') is not True:
            return {'message':'Review the destination and prompt before sending', 'confirm':True,'label':p['label'],'prompt':prompt}
        run('pane','send-text',p['pane_id'],prompt)
        run('pane','send-keys',p['pane_id'],'enter')
        return {'message':'Sent to '+p['label']+'; the agent performs the task'}
    # Paste stays unsubmitted; it cannot accidentally launch a turn.
    if m.get('action')=='paste':
        label=str(m.get('label',''));p=unique(label)
        if p.get('agent_status') not in ('idle','done'):raise RuntimeError('Target must be idle or done')
        if not text:raise RuntimeError('Paste text is empty')
        run('pane','send-text',p['pane_id'],text)
        return {'message':'Pasted into '+label+'; review it and press Enter yourself'}
    return {'message':'Try: go to LABEL · focus LABEL · unfocus · status · park LABEL · restore LABEL'}
async def serve(reader,writer):
    try:
        while raw:=await reader.readline():
            try:
                m=json.loads(raw)
                async with ACTION_LOCK:reply=await asyncio.to_thread(decide,m)
            except Exception as e:reply={'message':str(e),'error':True}
            writer.write((json.dumps(reply)+'\n').encode());await writer.drain()
    finally:writer.close();await writer.wait_closed()
async def main():
    import fcntl
    STATE.mkdir(parents=True,exist_ok=True,mode=0o700);STATE.chmod(0o700)
    lock=open(STATE/'brain.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if SOCK.exists():SOCK.unlink()
    server=await asyncio.start_unix_server(serve,path=str(SOCK));SOCK.chmod(0o600)
    async with server:await server.serve_forever()
if __name__=='__main__':asyncio.run(main())
