from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
import re,unittest
class TestNoGold(unittest.TestCase):
 def test_no_project_or_gold(self):
  pat=re.compile(r'\bPL\d{3}\b|人工金标|人工答案|本题正确|本题无误')
  for p in (ROOT/'09_环评审核技能库').glob('[01][0-9]_*/SKILL.md'):
   sid=p.parent.name.split('_',1)[0]
   if int(sid)<=15: self.assertIsNone(pat.search(p.read_text(encoding='utf-8')),str(p))
if __name__=='__main__': unittest.main()
