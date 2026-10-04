import asyncio,contextlib,importlib,json,os,pathlib,socket,subprocess,sys,tempfile,time,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'bin'))
import common,brain,sessions,request
P={'pane_id':'w1:p1','terminal_id':'term','label':'Research','agent':'claude','agent_status':'idle','tab_id':'w1:t1','workspace_id':'w1'}
class KitTests(unittest.TestCase):
    def test_duplicate_labels_refused(self):
        with patch.object(common,'panes',return_value=[P,P]):
            with self.assertRaises(RuntimeError):common.unique('Research')
    def test_exact_label_only(self):
        with patch.object(common,'panes',return_value=[P]):
            with self.assertRaises(RuntimeError):common.unique('Res')
            self.assertEqual(common.unique('research'),P)
    def test_focus_uses_socket_then_zoom(self):
        with patch.object(brain,'unique',return_value=P),patch.object(brain,'focus') as f,patch.object(brain,'run') as r:
            self.assertTrue(brain.decide({'text':'focus Research'})['raise']);f.assert_called_once_with(P)
            r.assert_called_once_with('pane','zoom','w1:p1','--on')
    def test_literal_paste_no_enter(self):
        text='quotes "\n$(example) `example`'
        with patch.object(brain,'unique',return_value=P),patch.object(brain,'run') as r:
            brain.decide({'action':'paste','label':'Research','text':text})
            r.assert_called_once_with('pane','send-text','w1:p1',text)
    def test_blocked_and_unknown_paste_refused(self):
        for status in ('working','blocked','unknown',None):
            with self.subTest(status=status),patch.object(brain,'unique',return_value={**P,'agent_status':status}),patch.object(brain,'run') as r:
                with self.assertRaises(RuntimeError):brain.decide({'action':'paste','label':'Research','text':'hello'})
                r.assert_not_called()
    def test_busy_park_refused(self):
        with patch.object(sessions,'unique',return_value={**P,'agent_status':'working'}),patch.object(sessions,'saved',return_value={'Research':{'kind':'claude'}}),patch.object(sessions,'run') as r:
            with self.assertRaises(RuntimeError):sessions.park('Research')
            r.assert_not_called()
    def test_unregistered_park_refused(self):
        with patch.object(sessions,'unique',return_value=P),patch.object(sessions,'saved',return_value={}):
            with self.assertRaises(RuntimeError):sessions.park('Research')
    def test_idle_park_reads_back(self):
        with patch.object(sessions,'unique',return_value=P),patch.object(sessions,'saved',return_value={'Research':{'kind':'claude'}}),patch.object(sessions,'run',return_value={'pane':{**P,'agent':None}}) as r:
            self.assertIn('Parked',sessions.park('Research'))
            self.assertEqual(r.call_args_list[0].args,('pane','send-keys','w1:p1','ctrl+c','ctrl+c'))
    def test_restore_refuses_live_agent(self):
        with patch.object(sessions,'unique',return_value=P),patch.object(sessions,'saved',return_value={'Research':{'kind':'claude'}}):
            with self.assertRaises(RuntimeError):sessions.restore('Research')
    def test_restore_refuses_unknown_process(self):
        with patch.object(sessions,'unique',return_value={**P,'agent':None}),patch.object(sessions,'saved',return_value={'Research':{'kind':'claude'}}),patch.object(sessions,'run',return_value={'process_info':{'foreground_processes':[{'argv':['vim']}]}}):
            with self.assertRaises(RuntimeError):sessions.restore('Research')
    def test_resume_quotes_folder_and_no_old_prompt(self):
        with tempfile.TemporaryDirectory(prefix='kit project ') as d:
            rec={'kind':'claude','session':'synthetic-session','cwd':d}
            with patch.object(sessions,'unique',return_value={**P,'agent':None}),patch.object(sessions,'saved',return_value={'Research':rec}),patch.object(sessions,'run',side_effect=[{'process_info':{'foreground_processes':[{'argv':['/bin/bash']}] }},{}]) as r:
                sessions.restore('Research');cmd=r.call_args_list[-1].args[-1]
                self.assertIn('claude --resume synthetic-session',cmd);self.assertIn("cd '",cmd)
    def test_registration_private_and_readback(self):
        with tempfile.TemporaryDirectory() as d,patch.object(sessions,'STORE',pathlib.Path(d)/'restore.json'),patch.object(sessions,'unique',return_value=P):
            sessions.register('Research','claude','synthetic-session',d)
            self.assertEqual(sessions.saved()['Research']['session'],'synthetic-session')
            self.assertEqual(sessions.STORE.stat().st_mode&0o777,0o600)
    def test_ssh_request_uses_json_stdin(self):
        with patch.object(request,'config',return_value={'vm_host':'fake-alias'}),patch.object(request.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'{"message":"ok"}\n','')) as r:
            text='literal $(example)';request.request({'text':text})
            self.assertEqual(r.call_args.args[0][5],'fake-alias')
            self.assertEqual(json.loads(r.call_args.kwargs['input'])['text'],text)
    def test_actual_brain_socket_and_connect(self):
        with tempfile.TemporaryDirectory() as d:
            env={**os.environ,'KIT_STATE':d}
            p=subprocess.Popen([sys.executable,str(ROOT/'bin/brain.py')],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                for _ in range(50):
                    if pathlib.Path(d,'brain.sock').exists():break
                    if p.poll() is not None:self.fail(p.stderr.read().decode())
                    time.sleep(.03)
                q=subprocess.run([sys.executable,str(ROOT/'bin/connect.py')],input='{"action":"ping"}\nnot-json\n',capture_output=True,text=True,env=env,timeout=5)
                replies=[json.loads(x) for x in q.stdout.splitlines()]
                self.assertEqual(replies[0]['message'],'Brain connected');self.assertTrue(replies[1]['error'])
                self.assertEqual(pathlib.Path(d,'brain.sock').stat().st_mode&0o777,0o600)
            finally:
                p.terminate();p.communicate(timeout=5)
    def test_vm_installer_idempotent_and_preserves_config(self):
        with tempfile.TemporaryDirectory() as d:
            h=pathlib.Path(d);fake=h/'tools';fake.mkdir();b=fake/'herdr';b.write_text('#!/bin/sh\nexit 0\n');b.chmod(0o755)
            env={**os.environ,'HOME':d,'PATH':str(fake)+':'+os.environ['PATH']}
            for _ in range(2):
                q=subprocess.run(['bash',str(ROOT/'install.sh'),'vm'],env=env,capture_output=True,text=True,timeout=5)
                self.assertEqual(q.returncode,0,q.stderr)
                conf=h/'.config/headless-kit/kit.json';c=json.loads(conf.read_text())
                if _==0:c['vm_host']='my-own-alias';conf.write_text(json.dumps(c))
            self.assertEqual(json.loads(conf.read_text())['vm_host'],'my-own-alias')
            self.assertTrue((h/'.local/share/headless-kit/bin/brain.py').exists())
            unit=(h/'.config/systemd/user/headless-kit-herdr.service').read_text();self.assertIn('server.py',unit)
if __name__=='__main__':unittest.main()
