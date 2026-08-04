from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
import json,re,unittest
class TestRagPurity(unittest.TestCase):
 def test_rag_content_only(self):
  pat=re.compile(r'\bcheck_logic\b|\brequired_evidence\b|审核步骤|审核顺序|输出模板|output_example|人工答案|人工金标',re.I)
  for name in ['parent_chunks.jsonl','child_chunks.jsonl']:
   p=ROOT/'03_指南解析_明文标准库/formal_rag_chunks'/name
   for line in p.read_text(encoding='utf-8').splitlines(): self.assertIsNone(pat.search(str(json.loads(line).get('content',''))))
if __name__=='__main__': unittest.main()
