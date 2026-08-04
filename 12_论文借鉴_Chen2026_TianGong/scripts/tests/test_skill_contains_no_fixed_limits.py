from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
import re,unittest
class TestNoFixedLimits(unittest.TestCase):
 def test_no_regulatory_limits(self):
  pat=re.compile(r'\b\d+(?:\.\d+)?\s*(?:mg/m3|mg/m³|mg/L|dB\(A\)|dB|kg/h)\b',re.I)
  for p in (ROOT/'09_环评审核技能库').glob('[01][0-9]_*/SKILL.md'):
   sid=p.parent.name.split('_',1)[0]
   if int(sid)<=15: self.assertIsNone(pat.search(p.read_text(encoding='utf-8')),str(p))
if __name__=='__main__': unittest.main()
