#!/usr/bin/env python3
"""Mac push-to-talk: local listener, one utterance, JSON result, no audio upload."""
import json,pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parent
p=subprocess.Popen([sys.executable,str(root/'listener.py'),'--nowake'],stdout=subprocess.PIPE,text=True)
try:
    for line in p.stdout:
        if line.strip()=='READY':
            with pathlib.Path('~/.config/headless-kit/cmd').expanduser().open('a') as f:f.write('LISTEN\n')
        if line.startswith('HEARD '):print(json.dumps({'text':line[6:].strip()}),flush=True);break
        if line.strip()=='NOSPEECH':print(json.dumps({'text':''}),flush=True);break
finally:p.terminate();p.wait()
