from pipeline_core import (
    AUDIT_DOMAINS,
    COGNITIVE_LEVELS,
    EVIDENCE_SPANS,
    FUNCTIONAL_CAPABILITIES,
    REASONING_TYPES,
    read_jsonl,
    TAXONOMY_JSONL,
)


def test_all_taxonomy_values_are_registered():
    rows = read_jsonl(TAXONOMY_JSONL)
    assert len(rows) == 210
    assert {row["audit_domain"] for row in rows} <= set(AUDIT_DOMAINS)
    assert {row["cognitive_level"] for row in rows} <= set(COGNITIVE_LEVELS)
    assert {row["reasoning_type"] for row in rows} <= set(REASONING_TYPES)
    assert {row["primary_functional_capability"] for row in rows} <= set(FUNCTIONAL_CAPABILITIES)
    assert {row["evidence_span"] for row in rows} <= set(EVIDENCE_SPANS)
