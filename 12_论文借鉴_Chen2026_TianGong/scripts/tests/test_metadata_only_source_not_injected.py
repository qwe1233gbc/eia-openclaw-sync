from pathlib import Path
import csv
import json
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[3]


class TestMetadataOnlyIsolation(unittest.TestCase):
    def test_metadata_only_source_not_injected(self):
        mapping = yaml.safe_load((ROOT / "03_指南解析_明文标准库/skills_to_standard_mapping.yaml").read_text(encoding="utf-8"))
        metadata_ids = {
            source_id
            for item in mapping["mappings"]
            for source_id in (item.get("metadata_only_source_ids") or [])
        }
        self.assertEqual(metadata_ids, {"WATER_GBT18920_2020_METADATA"})
        for item in mapping["mappings"]:
            self.assertTrue(metadata_ids.isdisjoint(item.get("candidate_source_ids") or []))

        path = ROOT / "10_消融实验设计/02_RAG冻结快照/rag_contexts_frozen.jsonl"
        contexts = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for row in contexts:
            for source_id in metadata_ids:
                self.assertNotIn(source_id, row.get("retrieved_sources") or [])
                self.assertNotIn(source_id, row.get("rag_context", ""))
                self.assertFalse(any(str(chunk).startswith(source_id + "_") for chunk in row.get("selected_parent_chunks") or []))

    def test_missing_metadata_full_text_forces_safe_degradation(self):
        with (ROOT / "10_消融实验设计/06_运行矩阵/run_matrix_v2.csv").open(encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        blocked = {"PL004_Emission_水污", "PL005_Emission_水污"}
        selected = [row for row in rows if row["question_id"] in blocked]
        self.assertEqual(len(selected), 8)
        for row in selected:
            self.assertEqual(row["status"], "blocked_primary_source_gap")
            self.assertEqual(row["basis_status"], "insufficient")
            self.assertEqual(row["conclusion"], "无法判断")
            self.assertEqual(row["manual_review_needed"], "true")


if __name__ == "__main__":
    unittest.main()
