from pathlib import Path
import hashlib
import json
import unittest


ROOT = Path(__file__).resolve().parents[3]
TARGETS = {"PL004_Emission_水污", "PL005_Emission_水污"}


def load(path: Path) -> dict[str, dict]:
    return {row["question_id"]: row for row in (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())}


class TestGbt18920Snapshots(unittest.TestCase):
    def test_both_snapshot_sets_use_same_verified_context(self):
        left = load(ROOT / "10_消融实验设计/02_RAG冻结快照/rag_contexts_frozen.jsonl")
        right = load(ROOT / "10_消融实验设计/knowledge_skill_2x2/real_report_experiment/rag/formal_rag_v2/04_rag_snapshots/rag_contexts_frozen_v2.jsonl")
        for question_id in TARGETS:
            for side in (left[question_id], right[question_id]):
                self.assertIn("WATER_GBT18920_2020", side["required_sources"])
                self.assertIn("WATER_GBT18920_2020", side["retrieved_sources"])
                self.assertNotIn("WATER_GBT18920_2020_METADATA", side["rag_context"])
                self.assertEqual(side["missing_required_sources"], [])
                self.assertIn("WATER_GBT18920_2020_P0004", side["selected_parent_chunks"])
                self.assertEqual(side["rag_context_sha256"], hashlib.sha256(side["rag_context"].encode("utf-8")).hexdigest())
            self.assertEqual(left[question_id]["rag_context"], right[question_id]["rag_context"])
            self.assertEqual(left[question_id]["rag_context_sha256"], right[question_id]["rag_context_sha256"])


if __name__ == "__main__":
    unittest.main()
