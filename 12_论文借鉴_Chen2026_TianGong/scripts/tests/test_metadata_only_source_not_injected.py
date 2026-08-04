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
        # The closed metadata gap is no longer active in routing, but the
        # record remains in the manifest and must never enter formal evidence.
        self.assertEqual(metadata_ids, set())
        manifest = [json.loads(line) for line in (ROOT / "03_指南解析_明文标准库/formal_rag/source_manifest.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        metadata = next(row for row in manifest if row["source_id"] == "WATER_GBT18920_2020_METADATA")
        self.assertFalse(metadata["eligible_for_formal_rag"])
        self.assertFalse(metadata["full_text_available"])
        isolated_ids = {"WATER_GBT18920_2020_METADATA"}
        for item in mapping["mappings"]:
            self.assertTrue(isolated_ids.isdisjoint(item.get("candidate_source_ids") or []))

        path = ROOT / "10_消融实验设计/02_RAG冻结快照/rag_contexts_frozen.jsonl"
        contexts = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for row in contexts:
            for source_id in isolated_ids:
                self.assertNotIn(source_id, row.get("retrieved_sources") or [])
                self.assertNotIn(source_id, row.get("rag_context", ""))
                self.assertFalse(any(str(chunk).startswith(source_id + "_") for chunk in row.get("selected_parent_chunks") or []))

    def test_verified_formal_replacement_allows_neutral_input_freeze(self):
        with (ROOT / "10_消融实验设计/06_运行矩阵/run_matrix_v2.csv").open(encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        targets = {"PL004_Emission_水污", "PL005_Emission_水污"}
        selected = [row for row in rows if row["question_id"] in targets]
        self.assertEqual(len(selected), 8)
        for row in selected:
            self.assertEqual(row["status"], "ready_input_freeze")
            self.assertEqual(row["basis_status"], "")
            self.assertEqual(row["conclusion"], "")
            self.assertEqual(row["manual_review_needed"], "")


if __name__ == "__main__":
    unittest.main()
