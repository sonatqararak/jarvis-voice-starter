#!/usr/bin/env python3
import os,socket,sys,threading
path=os.path.expanduser(os.environ.get('KIT_STATE','~/.local/state/headless-kit'))+'/brain.sock'
s=socket.socket(socket.AF_UNIX);s.connect(path)
def up():
    try:
        for line in sys.stdin.buffer:s.sendall(line)
        s.shutdown(socket.SHUT_WR)
    except OSError:pass
threading.Thread(target=up,daemon=True).start()
for line in s.makefile('rb'):
    sys.stdout.buffer.write(line);sys.stdout.buffer.flush()
