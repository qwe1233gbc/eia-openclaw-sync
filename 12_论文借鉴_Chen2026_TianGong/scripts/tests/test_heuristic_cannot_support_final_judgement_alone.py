from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
import unittest
class TestHeuristicBoundary(unittest.TestCase):
 def test_all_skills_constrain_hints(self):
  for p in (ROOT/'09_环评审核技能库').glob('[01][0-9]_*/SKILL.md'):
   sid=p.parent.name.split('_',1)[0]
   if int(sid)<=15:
    t=p.read_text(encoding='utf-8');self.assertIn('不能单独支撑最终正确/错误结论',t);self.assertIn('risk_hints',t)
if __name__=='__main__': unittest.main()
