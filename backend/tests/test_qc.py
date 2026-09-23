from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.qc import QcLimits, QcObservation, QcRuleConfig, QcRuleEvaluator, calculate_metrics
from app.qc.calculations import (
    POSITION_ABOVE_UPPER,
    POSITION_BELOW_LOWER,
    POSITION_NOT_CONFIGURED,
    POSITION_ON_LOWER,
    POSITION_ON_UPPER,
    POSITION_WITHIN,
)
from app.qc.models import ControlIdentity
from app.qc.synthetic import build_levey_jennings_data


CONTROL = ControlIdentity(
    material="Synthetic control",
    lot="LOT-001",
    level="level-1",
    analyte="SYN-01",
    method="METHOD-01",
    instrument="INSTRUMENT-01",
)


def observation(result: str, mean: str = "100", standard_deviation: str = "2") -> QcObservation:
    return QcObservation(
        control=CONTROL,
        run_number=1,
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        result=Decimal(result),
        mean=Decimal(mean),
        standard_deviation=Decimal(standard_deviation),
    )


def test_qc_metrics_are_calculated_exactly() -> None:
    metrics = calculate_metrics(observation("106"), QcLimits(lower_sd=Decimal("2"), upper_sd=Decimal("3")))

    assert metrics.difference_from_mean == Decimal("6")
    assert metrics.z_score == Decimal("3")
    assert metrics.sd_index == Decimal("3")
    assert metrics.cv_percent == Decimal("2.00")
    assert metrics.lower_limit == Decimal("96")
    assert metrics.upper_limit == Decimal("106")
    assert metrics.position == POSITION_ON_UPPER


def test_cv_is_not_defined_for_zero_mean() -> None:
    metrics = calculate_metrics(observation("2", mean="0"))

    assert metrics.cv_percent is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("95", POSITION_BELOW_LOWER),
        ("96", POSITION_ON_LOWER),
        ("100", POSITION_WITHIN),
        ("104", POSITION_ON_UPPER),
        ("105", POSITION_ABOVE_UPPER),
    ],
)
def test_position_against_configured_limits(value: str, expected: str) -> None:
    metrics = calculate_metrics(observation(value), QcLimits(lower=Decimal("96"), upper=Decimal("104")))

    assert metrics.position == expected


def test_position_is_explicit_when_limits_are_absent() -> None:
    assert calculate_metrics(observation("100")).position == POSITION_NOT_CONFIGURED


def test_levey_jennings_dataset_is_synthetic_and_ordered() -> None:
    observations = build_levey_jennings_data()

    assert len(observations) == 10
    assert [item.run_number for item in observations] == list(range(1, 11))
    assert all(item.control.material == "Synthetic control material" for item in observations)
    assert observations[0].timestamp < observations[-1].timestamp


def build_observations(z_scores: list[str]) -> list[QcObservation]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return [
        QcObservation(
            control=CONTROL,
            run_number=index,
            timestamp=start + timedelta(minutes=index),
            result=Decimal("100") + Decimal(z_score) * Decimal("2"),
            mean=Decimal("100"),
            standard_deviation=Decimal("2"),
        )
        for index, z_score in enumerate(z_scores, start=1)
    ]


@pytest.mark.parametrize(
    ("code", "z_scores", "window_size", "threshold", "triggered"),
    [
        ("1_2s", ["2"], 1, "2", True),
        ("1_3s", ["3"], 1, "3", True),
        ("2_2s", ["2.1", "2.2"], 2, "2", True),
        ("R_4s", ["-2.1", "2.1"], 2, "4", True),
        ("4_1s", ["1.1", "1.2", "1.3", "1.4"], 4, "1", True),
        ("10x", ["0.1"] * 10, 10, "1", True),
    ],
)
def test_each_configurable_qc_rule(code: str, z_scores: list[str], window_size: int, threshold: str, triggered: bool) -> None:
    rule = QcRuleConfig(
        rule_id=f"synthetic.{code}",
        code=code,
        name=f"Synthetic {code}",
        severity="review",
        suggested_action="Request professional review.",
        window_size=window_size,
        threshold_sd=Decimal(threshold),
    )

    decision = QcRuleEvaluator().evaluate(build_observations(z_scores), [rule])[0]

    assert decision.executed is True
    assert decision.triggered is triggered
    assert decision.alert is not None
    assert decision.alert.event_type == "QC_ALERT"
    assert decision.alert.rule_id == f"synthetic.{code}"
    assert decision.alert.control == CONTROL


def test_disabled_qc_rule_is_not_evaluated() -> None:
    rule = QcRuleConfig(
        rule_id="synthetic.disabled",
        code="1_2s",
        name="Synthetic disabled rule",
        enabled=False,
        severity="review",
        suggested_action="No action.",
        window_size=1,
        threshold_sd=Decimal("2"),
    )

    decision = QcRuleEvaluator().evaluate(build_observations(["3"]), [rule])[0]

    assert decision.executed is False
    assert decision.triggered is False
    assert decision.alert is None
