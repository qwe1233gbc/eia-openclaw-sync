from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
import unittest
class TestNoRagDegrade(unittest.TestCase):
 def test_all_skills_declare_safe_degrade(self):
  for p in (ROOT/'09_环评审核技能库').glob('[01][0-9]_*/SKILL.md'):
   sid=p.parent.name.split('_',1)[0]
   if int(sid)>15: continue
   t=p.read_text(encoding='utf-8'); self.assertIn('basis_status=insufficient',t); self.assertIn('不得根据模型记忆',t)
 def test_noise_example_cannot_emit_limit_without_rag(self):
  t=(ROOT/'09_环评审核技能库/06_环境质量执行标准审核/SKILL.md').read_text(encoding='utf-8')
  self.assertIn('RAG为空',t); self.assertNotRegex(t,r'65\s*/\s*55')
if __name__=='__main__': unittest.main()
