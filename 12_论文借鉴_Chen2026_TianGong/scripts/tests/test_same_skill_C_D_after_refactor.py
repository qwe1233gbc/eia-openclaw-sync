from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
import csv,unittest
class TestSkillHashes(unittest.TestCase):
 def test_c_d_equal(self):
  with (ROOT/'10_消融实验设计/06_运行矩阵/run_matrix_v2.csv').open(encoding='utf-8-sig') as f:
   rows=list(csv.DictReader(f))
  q={}
  for r in rows:q.setdefault(r['question_id'],{})[r['group']]=r
  for x,g in q.items():self.assertTrue(g['C']['skill_sha256']);self.assertEqual(g['C']['skill_sha256'],g['D']['skill_sha256'])
if __name__=='__main__': unittest.main()
