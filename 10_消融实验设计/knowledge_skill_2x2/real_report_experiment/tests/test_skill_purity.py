from .helpers import skill_purity_violations


def test_procedure_skills_contain_no_normative_answers():
    assert skill_purity_violations() == []
