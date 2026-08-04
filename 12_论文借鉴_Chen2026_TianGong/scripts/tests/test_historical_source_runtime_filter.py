from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_historical_source_runtime_filter import evaluate_source, load_manifest


class TestHistoricalSourceRuntimeFilter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()

    def test_wrong_versions_fail_by_report_date(self):
        cases = [
            ("2024-06-30", "SOLID_HW2025_CURRENT", "not_yet_effective"),
            ("2025-06-30", "SOLID_HW2021_HIST", "expired_or_repealed"),
            ("2026-02-28", "SOLID_GB34330_2025", "not_yet_effective"),
            ("2026-03-01", "SOLID_GB34330_2017_HIST", "expired_or_repealed"),
        ]
        for report_date, source_id, expected in cases:
            with self.subTest(source_id=source_id, report_date=report_date):
                result = evaluate_source(report_date, self.manifest[source_id], competing_versions_exist=True)
                self.assertEqual(result["applicability_result"], expected)

    def test_missing_report_date_requires_manual_review(self):
        result = evaluate_source(None, self.manifest["SOLID_HW2021_HIST"], competing_versions_exist=True)
        self.assertEqual(result["applicability_result"], "manual_review_required_missing_report_date")
        self.assertTrue(result["manual_review_needed"])


if __name__ == "__main__":
    unittest.main()
