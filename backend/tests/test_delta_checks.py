from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.delta_checks import (
    DeltaCheckEvaluator,
    DeltaComparisonContext,
    DeltaMeasurement,
    DeltaRuleConfig,
    calculate_absolute_delta,
    calculate_interval,
    calculate_percentage_delta,
)


def measurement(
    value: str,
    *,
    patient_id: str = "patient-1",
    sample_id: str = "sample-1",
    result_id: str = "result-1",
    analyte: str = "ANALYTE-1",
    timestamp: datetime = datetime(2026, 1, 2, tzinfo=UTC),
    unit: str = "unit-1",
    method: str = "method-1",
    instrument: str = "instrument-1",
    reference_interval_id: str | None = "ref-1",
) -> DeltaMeasurement:
    return DeltaMeasurement(
        patient_id=patient_id,
        sample_id=sample_id,
        result_id=result_id,
        analyte=analyte,
        value=Decimal(value),
        unit=unit,
        timestamp=timestamp,
        method=method,
        instrument=instrument,
        reference_interval_id=reference_interval_id,
    )


def rule(rule_type: str = "percentage", **overrides) -> DeltaRuleConfig:
    values = {
        "rule_id": "synthetic.delta.rule",
        "name": "Synthetic delta rule",
        "rule_type": rule_type,
        "severity": "review",
        "recommendation": "Solicitar revisión profesional.",
        "percentage_limit": Decimal("20"),
        "absolute_limit": Decimal("20"),
        "source": "Synthetic delta protocol",
    }
    values.update(overrides)
    return DeltaRuleConfig(**values)


def test_delta_math_matches_conceptual_example() -> None:
    current = measurement("120")
    previous = measurement("100", sample_id="sample-previous", result_id="result-previous", timestamp=datetime(2026, 1, 1, tzinfo=UTC))

    assert calculate_absolute_delta(current.value, previous.value) == Decimal("20")
    assert calculate_percentage_delta(current.value, previous.value) == Decimal("20")
    assert calculate_interval(current.timestamp, previous.timestamp) == timedelta(days=1)


def test_percentage_delta_with_zero_previous_is_not_defined() -> None:
    assert calculate_percentage_delta(Decimal("20"), Decimal("0")) is None


def test_percentage_rule_emits_delta_event() -> None:
    context = DeltaComparisonContext(
        current=measurement("120"),
        previous=measurement("100", sample_id="sample-previous", result_id="result-previous", timestamp=datetime(2026, 1, 1, tzinfo=UTC)),
    )

    event = DeltaCheckEvaluator().evaluate(context, [rule()])[0]

    assert event.event_type == "DELTA_EVENT"
    assert event.comparison_available is True
    assert event.rule_activated == "synthetic.delta.rule"
    assert event.absolute_delta == Decimal("20")
    assert event.percentage_delta == Decimal("20")
    assert event.interval == timedelta(days=1)
    assert event.patient_id == "patient-1"


@pytest.mark.parametrize(
    ("rule_type", "overrides", "expected"),
    [
        ("absolute", {"absolute_limit": Decimal("19")}, True),
        ("limits", {"lower_limit": Decimal("-10"), "upper_limit": Decimal("10")}, True),
        ("limits", {"lower_limit": Decimal("-30"), "upper_limit": Decimal("30")}, False),
    ],
)
def test_absolute_and_configured_limit_rules(rule_type: str, overrides: dict, expected: bool) -> None:
    context = DeltaComparisonContext(
        current=measurement("120"),
        previous=measurement("100", sample_id="sample-previous", result_id="result-previous", timestamp=datetime(2026, 1, 1, tzinfo=UTC)),
    )

    event = DeltaCheckEvaluator().evaluate(context, [rule(rule_type, **overrides)])[0]

    assert event.comparison_available is True
    assert (event.rule_activated is not None) is expected


@pytest.mark.parametrize(
    ("change", "expected_reason"),
    [
        ({"previous": None}, "no hay resultado previo"),
        ({"previous_kwargs": {"unit": "other-unit"}}, "unidad diferente"),
        ({"previous_kwargs": {"method": "other-method"}}, "método diferente"),
        ({"previous_kwargs": {"instrument": "other-instrument"}}, "instrumento diferente"),
        ({"previous_kwargs": {"reference_interval_id": "other-ref"}}, "intervalo de referencia diferente"),
        ({"previous_kwargs": {"timestamp": datetime(2025, 1, 1, tzinfo=UTC)}}, "resultado previo demasiado antiguo"),
    ],
)
def test_invalid_comparison_is_explicit(change: dict, expected_reason: str) -> None:
    current = measurement("120")
    previous = None
    if "previous_kwargs" in change:
        previous_values = {
            "sample_id": "sample-previous",
            "result_id": "result-previous",
            "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
        }
        previous_values.update(change["previous_kwargs"])
        previous = measurement("100", **previous_values)
    configured_rule = rule(max_interval_hours=Decimal("24"))

    event = DeltaCheckEvaluator().evaluate(DeltaComparisonContext(current=current, previous=previous), [configured_rule])[0]

    assert event.comparison_available is False
    assert expected_reason in event.reason
    assert event.rule_activated is None
    assert event.recommendation == "Solicitar revisión profesional."


def test_rule_can_allow_instrument_change_without_equivalence() -> None:
    context = DeltaComparisonContext(
        current=measurement("120", instrument="instrument-new"),
        previous=measurement("100", sample_id="sample-previous", result_id="result-previous", timestamp=datetime(2026, 1, 1, tzinfo=UTC), instrument="instrument-old"),
    )

    event = DeltaCheckEvaluator().evaluate(context, [rule(require_same_instrument=False)])[0]

    assert event.comparison_available is True
    assert event.absolute_delta == Decimal("20")
    assert event.evidence["percentage_limit"] == Decimal("20")
