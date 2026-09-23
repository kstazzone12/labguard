from decimal import Decimal

import pytest

from app.analytical_consistency import (
    AnalyteMeasurement,
    AnalyticalConsistencyEvaluator,
    ConsistencyContext,
    ConsistencyRuleConfig,
)


def context(*measurements, sample_indices=None) -> ConsistencyContext:
    return ConsistencyContext(
        sample_id="sample-demo-001",
        measurements=list(measurements),
        sample_indices=sample_indices or {},
    )


def measurement(analyte: str, value: str | None, unit: str | None = "synthetic-unit", source: str = "measured") -> AnalyteMeasurement:
    return AnalyteMeasurement(analyte=analyte, value=value, unit=unit, source=source)


def rule(relation: str, analytes: list[str], parameters: dict, category: str = "ANALYTICAL_REVIEW") -> ConsistencyRuleConfig:
    return ConsistencyRuleConfig(
        rule_id=f"DEMO-{relation}",
        name=f"Demo {relation}",
        relation=relation,
        involved_analytes=analytes,
        category=category,
        severity="review",
        explanation="Demo explanation.",
        recommendation="Solicitar revisión técnica.",
        parameters=parameters,
        version="DEMO-1.0",
        source="DEMO_PLACEHOLDER_PROTOCOL",
    )


def test_difference_relation_triggers_with_configured_tolerance() -> None:
    event = AnalyticalConsistencyEvaluator().evaluate(
        context(measurement("SYN-A", "120"), measurement("SYN-B", "100")),
        [rule("difference", ["SYN-A", "SYN-B"], {"tolerance": 10})],
    )[0]

    assert event.event_type == "CONSISTENCY_EVENT"
    assert event.triggered is True
    assert event.category == "ANALYTICAL_REVIEW"
    assert event.observed_values == {"SYN-A": Decimal("120"), "SYN-B": Decimal("100")}
    assert event.evidence["difference"] == Decimal("20")


def test_ratio_and_limits_are_configurable() -> None:
    ratio_event = AnalyticalConsistencyEvaluator().evaluate(
        context(measurement("SYN-A", "20"), measurement("SYN-B", "10")),
        [rule("ratio", ["SYN-A", "SYN-B"], {"lower": "1.5", "upper": "1.8"})],
    )[0]
    limits_event = AnalyticalConsistencyEvaluator().evaluate(
        context(measurement("SYN-A", "120")),
        [rule("limits", ["SYN-A"], {"lower": "0", "upper": "100"}, "DATA_ERROR")],
    )[0]

    assert ratio_event.triggered is True
    assert limits_event.triggered is True
    assert limits_event.category == "DATA_ERROR"


def test_unit_mismatch_is_a_data_error_signal() -> None:
    event = AnalyticalConsistencyEvaluator().evaluate(
        context(measurement("SYN-A", "10", "unit-a"), measurement("SYN-B", "10", "unit-b")),
        [rule("unit_match", ["SYN-A", "SYN-B"], {}, "DATA_ERROR")],
    )[0]

    assert event.triggered is True
    assert event.category == "DATA_ERROR"
    assert event.evidence["units"] == ["unit-a", "unit-b"] or set(event.evidence["units"]) == {"unit-a", "unit-b"}


def test_calculated_vs_measured_uses_tolerance() -> None:
    event = AnalyticalConsistencyEvaluator().evaluate(
        context(measurement("CALCULATED", "100", source="calculated"), measurement("MEASURED", "106")),
        [rule("calculated_vs_measured", ["CALCULATED", "MEASURED"], {"tolerance": 5})],
    )[0]

    assert event.triggered is True
    assert event.evidence["difference"] == Decimal("-6")


def test_sample_index_relation_is_configurable() -> None:
    event = AnalyticalConsistencyEvaluator().evaluate(
        context(measurement("SYN-A", "10"), sample_indices={"hemolysis": "HIGH"}),
        [rule("sample_index_vs_result", ["SYN-A"], {"index_field": "hemolysis", "operator": "equals", "expected": "LOW"}, "SPECIMEN_REVIEW")],
    )[0]

    assert event.triggered is True
    assert event.category == "SPECIMEN_REVIEW"


@pytest.mark.parametrize("missing", [True, False])
def test_missing_data_or_configuration_is_explicit(missing: bool) -> None:
    measurements = [measurement("SYN-A", None if missing else "10")]
    event = AnalyticalConsistencyEvaluator().evaluate(
        context(*measurements),
        [rule("limits", ["SYN-A"], {} if missing else {"lower": "0", "upper": "20"}, "CONFIGURATION_ERROR")],
    )[0]

    if missing:
        assert event.triggered is False
        assert event.category == "DATA_ERROR"
        assert "missing" in event.evidence["error"]
    else:
        assert event.triggered is False


def test_invalid_rule_parameters_are_configuration_error() -> None:
    event = AnalyticalConsistencyEvaluator().evaluate(
        context(measurement("SYN-A", "10")),
        [rule("limits", ["SYN-A"], {}, "ANALYTICAL_REVIEW")],
    )[0]

    assert event.triggered is False
    assert event.category == "CONFIGURATION_ERROR"
    assert "parameter" in event.evidence["error"]
