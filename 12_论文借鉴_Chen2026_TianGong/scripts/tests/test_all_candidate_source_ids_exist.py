from pathlib import Path
import json
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[3]


class TestCandidateIdsExist(unittest.TestCase):
    def test_all_candidate_source_ids_exist(self):
        mapping = yaml.safe_load((ROOT / "03_指南解析_明文标准库/skills_to_standard_mapping.yaml").read_text(encoding="utf-8"))
        manifest = {
            json.loads(line)["source_id"]
            for line in (ROOT / "03_指南解析_明文标准库/formal_rag/source_manifest.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
        for item in mapping["mappings"]:
            for source_id in item.get("candidate_source_ids") or []:
                self.assertIn(source_id, manifest, f"Skill {item['skill_id']}: {source_id}")


if __name__ == "__main__":
    unittest.main()
