#!/usr/bin/env python3
"""Ubuntu GTK orb, typed command/paste box, local microphone, and desktop banners."""
import json,os,pathlib,subprocess,threading,sys
import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk,GLib
from request import request
ROOT=pathlib.Path(__file__).resolve().parent
CONF=pathlib.Path('~/.config/headless-kit').expanduser();CONF.mkdir(parents=True,exist_ok=True)
CTL=CONF/'ui-command';CTL.touch();os.chmod(CTL,0o600)
class Shell:
    def __init__(self):
        self.window=Gtk.Window(title='Jarvis');self.window.set_default_size(470,280);self.window.set_keep_above(True)
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=8);box.set_border_width(16);self.window.add(box)
        self.caption=Gtk.Label(label='◎ Jarvis — VM brain');box.pack_start(self.caption,False,False,0)
        self.label=Gtk.Entry();self.label.set_placeholder_text('Exact pane label (paste only)');box.pack_start(self.label,False,False,0)
        self.text=Gtk.TextView();self.text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR);scroll=Gtk.ScrolledWindow();scroll.add(self.text);box.pack_start(scroll,True,True,0)
        for title,cb in [('Run command',lambda _:self.send()),('Paste into pane (no Enter)',lambda _:self.send(True)),('Listen / Stop dictation',lambda _:self.mic('LISTEN')),('Dictate locally',lambda _:self.mic('DICTATE'))]:
            b=Gtk.Button(label=title);b.connect('clicked',cb);box.pack_start(b,False,False,0)
        self.window.connect('delete-event',lambda *_:(self.window.hide(),True)[1]);self.offset=CTL.stat().st_size
        self.listener=None;self.dictating=False;GLib.timeout_add(150,self.poll)
    def poll(self):
        with CTL.open() as f:
            f.seek(self.offset);lines=f.readlines();self.offset=f.tell()
        for line in lines:
            self.window.show_all();self.window.present()
            if line.strip()=='listen':self.mic('LISTEN')
            elif line.strip()=='dictate':self.mic('DICTATE')
        return True
    def mic(self,cmd):
        if self.dictating:cmd='STOP'
        if not self.listener or self.listener.poll() is not None:
            self.listener=subprocess.Popen([sys.executable,str(ROOT/'listener.py'),'--nowake'],stdout=subprocess.PIPE,text=True)
            threading.Thread(target=self.read_mic,daemon=True).start()
            # Listener clears its command file on startup. Send only after READY.
            self.pending=cmd;return
        self.mic_command(cmd)
    def mic_command(self,cmd):
        if cmd=='DICTATE':self.dictating=True
        with (CONF/'cmd').open('a') as f:f.write(cmd+'\n')
    def read_mic(self):
        for line in self.listener.stdout:
            if line.strip()=='READY':self.mic_command(self.pending)
            elif line.startswith('HEARD '):
                text=line[6:].strip();was=self.dictating;self.dictating=False
                def heard(text=text,was=was):
                    self.text.get_buffer().set_text(text)
                    if not was:self.send()
                    else:self.caption.set_text('Dictation ready — review before paste')
                    return False
                GLib.idle_add(heard)
    def send(self,paste=False):
        b=self.text.get_buffer();text=b.get_text(b.get_start_iter(),b.get_end_iter(),True)
        m={'text':text,'action':'paste' if paste else 'command','label':self.label.get_text()}
        self.caption.set_text('Thinking…')
        def work():
            try:r=request(m)
            except Exception as e:r={'message':str(e),'error':True}
            GLib.idle_add(self.reply,r)
        threading.Thread(target=work,daemon=True).start()
    def reply(self,r):
        if r.get('confirm'):
            dialog=Gtk.MessageDialog(transient_for=self.window,modal=True,message_type=Gtk.MessageType.QUESTION,buttons=Gtk.ButtonsType.OK_CANCEL,text='Send to '+r['label']+'?')
            dialog.format_secondary_text(r['prompt']);answer=dialog.run();dialog.destroy()
            if answer==Gtk.ResponseType.OK:
                text='tell '+r['label']+' to '+r['prompt']
                def submit():
                    try:reply=request({'text':text,'confirmed':True})
                    except Exception as e:reply={'message':str(e),'error':True}
                    GLib.idle_add(self.reply,reply)
                threading.Thread(target=submit,daemon=True).start()
            else:self.caption.set_text('Cancelled — no prompt sent')
            return False
        self.caption.set_text(r.get('message','Done'))
        if r.get('notify') and __import__('shutil').which('notify-send'):subprocess.Popen(['notify-send','Jarvis',r['message']])
        return False
s=Shell();s.window.show_all()
try:Gtk.main()
finally:
    if s.listener and s.listener.poll() is None:s.listener.terminate()
