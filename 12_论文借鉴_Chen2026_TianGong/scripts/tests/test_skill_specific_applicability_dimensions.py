from pathlib import Path
import json
import re
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[3]
EXPECTED = {
    "01": ["product", "usage", "material", "process", "main_business_activity", "valid_time"],
    "02": ["report_date", "investment_scope", "calculation_basis"],
    "03": ["region", "control_unit", "project_location", "industry", "process", "valid_time"],
    "04": ["report_type", "project_type", "industry", "process", "construction_stage", "valid_time"],
    "05": ["region", "data_year", "bulletin_type", "pollution_medium", "waterbody_or_station", "valid_time"],
    "06": ["region", "functional_zone", "pollution_medium", "waterbody_or_area", "standard_category", "valid_time"],
    "07": ["region", "industry", "process", "pollutant", "pollution_medium", "emission_mode", "discharge_destination", "valid_time"],
    "08": ["industry", "product", "process", "raw_material", "pollutant", "activity_level", "valid_time"],
    "09": ["industry", "process", "pollutant", "calculation_method", "activity_level", "operating_condition", "valid_time"],
    "10": ["process", "pollutant", "source_type", "collection_mode", "enclosure_condition", "valid_time"],
    "11": ["hood_type", "source_geometry", "control_velocity_basis", "air_change_basis", "operating_condition", "valid_time"],
    "12": ["process", "pollutant", "collection_mode", "enclosure_condition", "efficiency_basis", "valid_time"],
    "13": ["pollutant", "inlet_concentration", "airflow", "operating_time", "adsorbent_type", "replacement_cycle", "valid_time"],
    "14": ["generation_process", "composition", "physical_state", "hazardous_characteristics", "waste_code_basis", "valid_time"],
    "15": ["region", "industry", "process", "VOCs_scope", "calculation_period", "policy_valid_time"],
}


class TestSkillSpecificDimensions(unittest.TestCase):
    def test_mapping_and_registry_use_exact_skill_specific_dimensions(self):
        mapping = yaml.safe_load((ROOT / "03_指南解析_明文标准库/skills_to_standard_mapping.yaml").read_text(encoding="utf-8"))
        registry = yaml.safe_load((ROOT / "09_环评审核技能库/formal_skill_registry.yaml").read_text(encoding="utf-8"))
        mapped = {str(item["skill_id"]): item for item in mapping["mappings"]}
        registered = {str(item["skill_id"]): item for item in registry["skills"] if str(item["skill_id"]) != "99"}
        self.assertEqual(set(mapped), set(EXPECTED))
        self.assertEqual(set(registered), set(EXPECTED))
        for sid, dimensions in EXPECTED.items():
            self.assertEqual(mapped[sid]["required_applicability_dimensions"], dimensions, sid)
            self.assertEqual(registered[sid]["required_applicability_dimensions"], dimensions, sid)
            skill_text = (ROOT / "09_环评审核技能库" / registered[sid]["path"]).read_text(encoding="utf-8")
            for dimension in dimensions:
                self.assertIn(f"`{dimension}`", skill_text, f"Skill {sid}: {dimension}")
            json_blocks = [json.loads(block) for block in re.findall(r"```json\n(.*?)\n```", skill_text, re.S)]
            rag_unit = next(block for block in json_blocks if "source_id" in block)
            self.assertEqual(list(rag_unit["applicability"]), dimensions, f"Skill {sid} rag_evidence contract")


if __name__ == "__main__":
    unittest.main()
