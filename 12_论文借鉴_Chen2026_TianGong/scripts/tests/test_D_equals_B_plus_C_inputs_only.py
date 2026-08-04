from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
import csv,unittest
class TestDComposition(unittest.TestCase):
 def test_d_is_union(self):
  with (ROOT/'10_消融实验设计/06_运行矩阵/run_matrix_v2.csv').open(encoding='utf-8-sig') as f:
   rows=list(csv.DictReader(f))
  q={}
  for r in rows:q.setdefault(r['question_id'],{})[r['group']]=r
  for x,g in q.items():
   self.assertEqual(g['D']['report_context_sha256'],g['B']['report_context_sha256']);self.assertEqual(g['D']['rag_context_sha256'],g['B']['rag_context_sha256']);self.assertEqual(g['D']['skill_sha256'],g['C']['skill_sha256'])
   self.assertFalse(g['A']['rag_context_sha256'] or g['A']['skill_sha256']);self.assertFalse(g['B']['skill_sha256']);self.assertFalse(g['C']['rag_context_sha256'])
if __name__=='__main__': unittest.main()
