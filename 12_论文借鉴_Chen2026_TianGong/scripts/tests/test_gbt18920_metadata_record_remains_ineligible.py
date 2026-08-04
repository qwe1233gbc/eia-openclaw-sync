from pathlib import Path
import json
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[3]


class TestGbt18920MetadataSeparation(unittest.TestCase):
    def test_metadata_record_remains_ineligible_and_outside_candidates(self):
        rows = [json.loads(line) for line in (ROOT / "03_指南解析_明文标准库/formal_rag/source_manifest.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        metadata = next(row for row in rows if row["source_id"] == "WATER_GBT18920_2020_METADATA")
        self.assertFalse(metadata["full_text_available"])
        self.assertFalse(metadata["eligible_for_formal_rag"])
        self.assertEqual(metadata["superseded_by_source_id"], "WATER_GBT18920_2020")
        mapping = yaml.safe_load((ROOT / "03_指南解析_明文标准库/skills_to_standard_mapping.yaml").read_text(encoding="utf-8"))
        for item in mapping["mappings"]:
            self.assertNotIn("WATER_GBT18920_2020_METADATA", item.get("candidate_source_ids") or [])
            self.assertNotIn("WATER_GBT18920_2020", item.get("metadata_only_source_ids") or [])


if __name__ == "__main__":
    unittest.main()
