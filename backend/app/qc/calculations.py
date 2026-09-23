from decimal import Decimal

from app.qc.models import QcLimits, QcMetrics, QcObservation


POSITION_NOT_CONFIGURED = "not_configured"
POSITION_BELOW_LOWER = "below_lower"
POSITION_ON_LOWER = "on_lower"
POSITION_WITHIN = "within"
POSITION_ON_UPPER = "on_upper"
POSITION_ABOVE_UPPER = "above_upper"


def calculate_difference(observation: QcObservation) -> Decimal:
    return observation.result - observation.mean


def calculate_z_score(observation: QcObservation) -> Decimal:
    return calculate_difference(observation) / observation.standard_deviation


def calculate_sd_index(observation: QcObservation) -> Decimal:
    """SD index is the signed distance from the mean in SD units."""
    return calculate_z_score(observation)


def calculate_cv_percent(observation: QcObservation) -> Decimal | None:
    if observation.mean == 0:
        return None
    return (observation.standard_deviation / abs(observation.mean)) * Decimal("100")


def resolve_limits(observation: QcObservation, limits: QcLimits) -> tuple[Decimal | None, Decimal | None]:
    lower = limits.lower
    upper = limits.upper
    if lower is None and limits.lower_sd is not None:
        lower = observation.mean - limits.lower_sd * observation.standard_deviation
    if upper is None and limits.upper_sd is not None:
        upper = observation.mean + limits.upper_sd * observation.standard_deviation
    return lower, upper


def position_against_limits(
    value: Decimal,
    lower: Decimal | None,
    upper: Decimal | None,
) -> str:
    if lower is None and upper is None:
        return POSITION_NOT_CONFIGURED
    if lower is not None and value < lower:
        return POSITION_BELOW_LOWER
    if lower is not None and value == lower:
        return POSITION_ON_LOWER
    if upper is not None and value > upper:
        return POSITION_ABOVE_UPPER
    if upper is not None and value == upper:
        return POSITION_ON_UPPER
    return POSITION_WITHIN


def calculate_metrics(observation: QcObservation, limits: QcLimits | None = None) -> QcMetrics:
    configured_limits = limits or QcLimits()
    lower, upper = resolve_limits(observation, configured_limits)
    return QcMetrics(
        difference_from_mean=calculate_difference(observation),
        z_score=calculate_z_score(observation),
        sd_index=calculate_sd_index(observation),
        cv_percent=calculate_cv_percent(observation),
        position=position_against_limits(observation.result, lower, upper),
        lower_limit=lower,
        upper_limit=upper,
    )
