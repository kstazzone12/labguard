from collections.abc import Sequence
from decimal import Decimal

from app.qc.models import QcObservation, QcRuleCode


def _same_side(values: Sequence[Decimal]) -> bool:
    return all(value > 0 for value in values) or all(value < 0 for value in values)


def rule_1_2s(z_scores: Sequence[Decimal], threshold: Decimal) -> tuple[bool, dict[str, object]]:
    latest = z_scores[-1]
    return abs(latest) >= threshold, {"latest_z_score": latest, "threshold_sd": threshold}


def rule_1_3s(z_scores: Sequence[Decimal], threshold: Decimal) -> tuple[bool, dict[str, object]]:
    latest = z_scores[-1]
    return abs(latest) >= threshold, {"latest_z_score": latest, "threshold_sd": threshold}


def rule_2_2s(z_scores: Sequence[Decimal], threshold: Decimal) -> tuple[bool, dict[str, object]]:
    window = z_scores[-2:]
    triggered = len(window) == 2 and all(abs(value) >= threshold for value in window) and _same_side(window)
    return triggered, {"z_scores": list(window), "threshold_sd": threshold, "same_side": _same_side(window)}


def rule_r_4s(z_scores: Sequence[Decimal], threshold: Decimal) -> tuple[bool, dict[str, object]]:
    window = z_scores[-2:]
    triggered = len(window) == 2 and (max(window) - min(window)) >= threshold and _same_side_opposite(window)
    return triggered, {"z_scores": list(window), "range_sd": max(window) - min(window) if len(window) == 2 else None, "threshold_sd": threshold}


def _same_side_opposite(values: Sequence[Decimal]) -> bool:
    return len(values) == 2 and ((values[0] > 0 and values[1] < 0) or (values[0] < 0 and values[1] > 0))


def rule_4_1s(z_scores: Sequence[Decimal], threshold: Decimal) -> tuple[bool, dict[str, object]]:
    window = z_scores[-4:]
    triggered = len(window) == 4 and all(abs(value) >= threshold for value in window) and _same_side(window)
    return triggered, {"z_scores": list(window), "threshold_sd": threshold, "same_side": _same_side(window)}


def rule_10x(z_scores: Sequence[Decimal], threshold: Decimal) -> tuple[bool, dict[str, object]]:
    window = z_scores[-10:]
    triggered = len(window) == 10 and _same_side(window)
    return triggered, {"z_scores": list(window), "threshold_sd": threshold, "same_side": _same_side(window)}


def calculate_observation_z_scores(observations: Sequence[QcObservation]) -> list[Decimal]:
    return [(observation.result - observation.mean) / observation.standard_deviation for observation in observations]


RULE_FUNCTIONS = {
    "1_2s": rule_1_2s,
    "1_3s": rule_1_3s,
    "2_2s": rule_2_2s,
    "R_4s": rule_r_4s,
    "4_1s": rule_4_1s,
    "10x": rule_10x,
}
