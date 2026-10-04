import sys,pathlib,unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'bin'))
import brain
P={'pane_id':'w1:p1','label':'Research','agent_status':'idle'}
class DeliveryTests(unittest.TestCase):
 def test_unconfirmed_never_sends(self):
  with patch.object(brain,'unique',return_value=P),patch.object(brain,'run') as run:
   reply=brain.decide({'text':'tell Research to write a note'})
   self.assertTrue(reply['confirm']);run.assert_not_called()
 def test_confirmed_literal_prompt_then_enter(self):
  with patch.object(brain,'unique',return_value=P),patch.object(brain,'run') as run:
   brain.decide({'text':'tell Research to write $(literal) `words`','confirmed':True})
   self.assertEqual(run.call_args_list[0].args,('pane','send-text','w1:p1','write $(literal) `words`'))
   self.assertEqual(run.call_args_list[1].args,('pane','send-keys','w1:p1','enter'))
 def test_busy_target_never_sends(self):
  with patch.object(brain,'unique',return_value={**P,'agent_status':'working'}),patch.object(brain,'run') as run:
   with self.assertRaises(RuntimeError):brain.decide({'text':'tell Research to write a note','confirmed':True})
   run.assert_not_called()
