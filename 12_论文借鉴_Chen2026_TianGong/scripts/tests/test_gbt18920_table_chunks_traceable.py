from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[3]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class TestGbt18920TableChunks(unittest.TestCase):
    def test_table1_parent_and_children_are_traceable(self):
        parents = {row["parent_id"]: row for row in load_jsonl(ROOT / "03_指南解析_明文标准库/formal_rag_chunks/parent_chunks.jsonl")}
        children = load_jsonl(ROOT / "03_指南解析_明文标准库/formal_rag_chunks/child_chunks.jsonl")
        table = next(row for row in parents.values() if row.get("source_id") == "WATER_GBT18920_2020" and row.get("table_number") == "表1")
        self.assertEqual(table["page_number"], "正文第2—3页")
        for marker in ("列A用途", "列B用途", "13 大肠埃希氏菌", "a 括号内指标", "b 用于城市绿化", "c 大肠埃希氏菌"):
            self.assertIn(marker, table["content"])
        linked = [row for row in children if row["parent_id"] == table["parent_id"]]
        self.assertGreaterEqual(len(linked), 3)
        self.assertTrue(all(row["source_sha256"] == table["source_sha256"] for row in linked))
        self.assertTrue(all(row["table_number"] == "表1" for row in linked))


if __name__ == "__main__":
    unittest.main()
