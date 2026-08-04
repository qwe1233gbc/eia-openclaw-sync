from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
import unittest
class TestCardBoundary(unittest.TestCase):
 def test_allow_and_block_lists(self):
  allow=(ROOT/'03_指南解析_明文标准库/formal_rag_quality/rag_field_allowlist.yaml').read_text(encoding='utf-8')
  block=(ROOT/'03_指南解析_明文标准库/formal_rag_quality/rag_field_blocklist.yaml').read_text(encoding='utf-8')
  self.assertIn('whole_card_cannot_enter_B_group_body',allow);self.assertIn('check_logic',block);self.assertIn('output_example',block)
if __name__=='__main__': unittest.main()
