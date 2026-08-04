from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]


class TestSkill07ConditionalApplicability(unittest.TestCase):
    def test_not_applicable_is_not_missing_for_noise_and_solid_waste(self):
        text = (ROOT / "09_环评审核技能库/07_污染物排放标准审核/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`not_applicable`不等于缺失", text)
        self.assertIn("噪声", text)
        self.assertIn("`discharge_destination=not_applicable`不构成缺失", text)
        self.assertIn("固体废物", text)
        self.assertIn("`emission_mode=not_applicable`不构成缺失", text)
        self.assertIn("不得仅因该字段判定`insufficient`", text)


if __name__ == "__main__":
    unittest.main()
