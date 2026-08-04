from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[3]
TARGETS = {"PL004_Emission_水污", "PL005_Emission_水污"}


class TestGbt18920RetrievalScope(unittest.TestCase):
    def test_formal_source_is_not_mechanically_injected(self):
        paths = [
            ROOT / "10_消融实验设计/02_RAG冻结快照/rag_contexts_frozen.jsonl",
            ROOT / "10_消融实验设计/knowledge_skill_2x2/real_report_experiment/rag/formal_rag_v2/04_rag_snapshots/rag_contexts_frozen_v2.jsonl",
        ]
        for path in paths:
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            hits = {row["question_id"] for row in rows if "WATER_GBT18920_2020" in (row.get("required_sources") or []) or "WATER_GBT18920_2020" in (row.get("retrieved_sources") or []) or "WATER_GBT18920_2020" in row.get("rag_context", "")}
            self.assertEqual(hits, TARGETS)
            self.assertNotIn("PL003_Emission_水污", hits)


if __name__ == "__main__":
    unittest.main()
