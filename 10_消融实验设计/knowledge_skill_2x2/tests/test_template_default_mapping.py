from pipeline_core import TEMPLATE_DEFAULTS


def test_seven_templates_have_unique_domains():
    assert len(TEMPLATE_DEFAULTS) == 7
    assert len({value["audit_domain"] for value in TEMPLATE_DEFAULTS.values()}) == 7
