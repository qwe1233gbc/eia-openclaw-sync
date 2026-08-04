from pathlib import Path
import csv
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_rag_mapping_referential_integrity import gbt_activation_ready


ROOT = Path(__file__).resolve().parents[3]
TARGETS = {"PL004_Emission_水污", "PL005_Emission_水污"}


class TestGbt18920RunMatrixGate(unittest.TestCase):
    def test_gate_rejects_each_missing_component(self):
        verification = {"pass": True}
        source = {"eligible_for_formal_rag": True, "full_text_available": True}
        table = [{"table_number": "表1"}]
        self.assertTrue(gbt_activation_ready(verification, source, table))
        self.assertFalse(gbt_activation_ready({}, source, table))
        self.assertFalse(gbt_activation_ready(verification, None, table))
        self.assertFalse(gbt_activation_ready(verification, {**source, "eligible_for_formal_rag": False}, table))
        self.assertFalse(gbt_activation_ready(verification, {**source, "full_text_available": False}, table))
        self.assertFalse(gbt_activation_ready(verification, source, []))

    def test_unblocked_rows_are_neutral_inputs(self):
        with (ROOT / "10_消融实验设计/06_运行矩阵/run_matrix_v2.csv").open(encoding="utf-8-sig") as stream:
            rows = [row for row in csv.DictReader(stream) if row["question_id"] in TARGETS]
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["status"] == "ready_input_freeze" for row in rows))
        self.assertTrue(all(not row["basis_status"] and not row["conclusion"] and not row["manual_review_needed"] for row in rows))


if __name__ == "__main__":
    unittest.main()
