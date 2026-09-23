from datetime import timedelta
from decimal import Decimal

from app.delta_checks.models import DeltaComparisonContext, DeltaMetrics


def calculate_absolute_delta(current_value: Decimal, previous_value: Decimal) -> Decimal:
    return current_value - previous_value


def calculate_percentage_delta(current_value: Decimal, previous_value: Decimal) -> Decimal | None:
    if previous_value == 0:
        return None
    return (calculate_absolute_delta(current_value, previous_value) / abs(previous_value)) * Decimal("100")


def calculate_interval(current_timestamp, previous_timestamp) -> timedelta:
    return current_timestamp - previous_timestamp


def calculate_metrics(context: DeltaComparisonContext) -> DeltaMetrics | None:
    if context.previous is None:
        return None
    interval = calculate_interval(context.current.timestamp, context.previous.timestamp)
    return DeltaMetrics(
        absolute_delta=calculate_absolute_delta(context.current.value, context.previous.value),
        percentage_delta=calculate_percentage_delta(context.current.value, context.previous.value),
        interval=interval,
        interval_hours=Decimal(str(interval.total_seconds())) / Decimal("3600"),
    )
