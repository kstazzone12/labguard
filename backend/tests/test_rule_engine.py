from datetime import UTC, datetime

import pytest

from app.engine import EvaluationContext, RuleEvaluator, RuleLoader, RuleRegistry
from app.engine.models import RuleDefinition


RULE_DATA = {
    "id": "synthetic.test.rule",
    "name": "Synthetic test rule",
    "version": "1.0",
    "description": "A deliberately fictitious rule for unit testing.",
    "category": "synthetic",
    "analytes": ["SYN-01"],
    "conditions": {
        "all": [
            {"field": "result.numeric_value", "operator": "gte", "value": 10}
        ]
    },
    "severity": "review",
    "suggested_action": "Request professional review.",
    "source": "Synthetic test protocol",
    "effective_from": "2026-01-01",
    "method": "M-01",
    "instrument": "I-01",
    "enabled": True,
}


def test_loader_validates_declarative_rule() -> None:
    rule = RuleDefinition.model_validate(RULE_DATA)

    assert rule.id == "synthetic.test.rule"
    assert rule.conditions.all[0].operator == "gte"


def test_evaluator_returns_triggered_event_with_evidence() -> None:
    registry = RuleRegistry([RuleDefinition.model_validate(RULE_DATA)])
    context = EvaluationContext(
        result={
            "analyte_code": "SYN-01",
            "numeric_value": 12,
            "method_code": "M-01",
            "instrument_code": "I-01",
        },
        evaluated_at=datetime(2026, 2, 1, tzinfo=UTC),
    )

    result = RuleEvaluator().evaluate(context, registry)[0]

    assert result.executed is True
    assert result.applicable is True
    assert result.triggered is True
    assert result.evidence[0].observed_value == 12
    assert result.suggested_action == "Request professional review."


def test_evaluator_registers_non_triggered_rules() -> None:
    registry = RuleRegistry([RuleDefinition.model_validate(RULE_DATA)])
    context = EvaluationContext(
        result={
            "analyte_code": "SYN-01",
            "numeric_value": 3,
            "method_code": "M-01",
            "instrument_code": "I-01",
        }
    )

    result = RuleEvaluator().evaluate(context, registry)[0]

    assert result.executed is True
    assert result.triggered is False
    assert result.reason == "Configured conditions did not match"
    assert result.suggested_action is None


def test_disabled_rule_is_registered_as_not_executed() -> None:
    disabled_rule = RuleDefinition.model_validate({**RULE_DATA, "enabled": False})
    result = RuleEvaluator().evaluate(EvaluationContext(), RuleRegistry([disabled_rule]))[0]

    assert result.executed is False
    assert result.triggered is False
    assert result.skipped_reason == "Rule disabled"


def test_registry_rejects_duplicate_rule_version() -> None:
    rule = RuleDefinition.model_validate(RULE_DATA)

    with pytest.raises(ValueError, match="Duplicate rule"):
        RuleRegistry([rule, rule])


def test_loader_reads_repository_yaml_rules() -> None:
    rules = RuleLoader().load_directory("rules")

    assert {rule.id for rule in rules} >= {
        "synthetic.result.review",
        "synthetic.quality.review",
    }
