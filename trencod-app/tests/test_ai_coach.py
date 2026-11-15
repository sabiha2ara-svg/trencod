import unittest
from ai_coach import COACHES, instructions, teaching_answer
class CoachTests(unittest.TestCase):
 def test_different_learning_levels(self):
  self.assertLess(COACHES['normal']['tokens'],COACHES['smart']['tokens'])
  for kind in COACHES:
   self.assertIn('Never write complete games/apps',instructions(kind))
   self.assertIn('never claim to have edited',instructions(kind))
 def test_code_budget(self):
  answer='Why: a small example.\n```python\n'+'print(1)\n'*9+'```'
  self.assertNotEqual(teaching_answer(answer,'normal'),answer)
  self.assertEqual(teaching_answer(answer,'smart'),answer)
  self.assertNotEqual(teaching_answer('```js\n'+'x();\n'*21+'```','smart'),'```js\n'+'x();\n'*21+'```')
 def test_document_rejected(self):
  for kind in COACHES:
   self.assertIn('one small step',teaching_answer('<!DOCTYPE html><html>game</html>',kind))
