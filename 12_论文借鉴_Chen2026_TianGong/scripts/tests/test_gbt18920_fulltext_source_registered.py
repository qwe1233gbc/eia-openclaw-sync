from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[3]


class TestGbt18920FormalSource(unittest.TestCase):
    def test_verified_fulltext_source_is_registered(self):
        rows = [json.loads(line) for line in (ROOT / "03_指南解析_明文标准库/formal_rag/source_manifest.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        source = next(row for row in rows if row["source_id"] == "WATER_GBT18920_2020")
        report = json.loads((ROOT / "09_环评审核技能库/quality/gbt18920_fulltext_verification_report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["pass"])
        self.assertEqual(source["source_sha256"], report["file_sha256"])
        self.assertTrue(source["full_text_available"])
        self.assertTrue(source["eligible_for_formal_rag"])
        self.assertEqual(source["acquisition_method"], "user_provided_verified_fulltext")
        self.assertNotIn("E:/", source["repository_locator"])


if __name__ == "__main__":
    unittest.main()
