from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from operator import contains, eq, ge, gt, le, lt, ne
from typing import Any, Callable

from app.specimen_quality.models import (
    InterferenceConfig,
    SpecimenQualityContext,
    SpecimenQualityEvent,
)

_OPERATORS: dict[str, Callable[[Any, Any], bool]] = {
    "equals": eq,
    "not_equals": ne,
    "gt": gt,
    "gte": ge,
    "lt": lt,
    "lte": le,
    "in": lambda observed, expected: observed in expected,
    "contains": contains,
}
_MISSING = object()


class SpecimenQualityEvaluator:
    def evaluate(
        self,
        context: SpecimenQualityContext,
        configurations: Sequence[InterferenceConfig],
    ) -> list[SpecimenQualityEvent]:
        applicable = [config for config in configurations if self._applies(context, config)]
        matched = [config for config in applicable if config.enabled and self._matches(context, config)]
        timestamp = context.processing_time or context.collection_time or datetime.now(UTC)
        if not matched:
            return [
                SpecimenQualityEvent(
                    analyte=context.analyte,
                    sample_id=context.sample_id,
                    evidence="No configured interference criterion matched.",
                    possible_impact=None,
                    status="NO_CONFIGURED_INTERFERENCE",
                    interference_id=None,
                    source_type=None,
                    source_reference=None,
                    criterion=None,
                    timestamp=timestamp,
                    recommendation="No specimen-quality review signal was configured for this context.",
                )
            ]
        return [
            SpecimenQualityEvent(
                analyte=context.analyte,
                sample_id=context.sample_id,
                evidence=f"Sample quality flag: {config.criterion.field}",
                possible_impact="Configured interference",
                status="REVIEW_REQUIRED",
                interference_id=config.interference_id,
                source_type=config.source_type,
                source_reference=config.source_reference,
                criterion=config.criterion.model_dump(),
                timestamp=timestamp,
                recommendation=config.suggested_action,
            )
            for config in matched
        ]

    @staticmethod
    def _applies(context: SpecimenQualityContext, config: InterferenceConfig) -> bool:
        return (
            config.enabled
            and config.analyte == context.analyte
            and (config.method is None or config.method == context.method)
            and (config.manufacturer is None or config.manufacturer == context.manufacturer)
            and (config.instrument is None or config.instrument == context.instrument)
        )

    @staticmethod
    def _matches(context: SpecimenQualityContext, config: InterferenceConfig) -> bool:
        observed = SpecimenQualityEvaluator._resolve(context.model_dump(), config.criterion.field)
        if observed is _MISSING:
            return False
        try:
            return _OPERATORS[config.criterion.operator](observed, config.criterion.value)
        except (TypeError, KeyError):
            return False

    @staticmethod
    def _resolve(value: Mapping[str, Any], path: str) -> Any:
        current: Any = value
        for segment in path.split("."):
            if not isinstance(current, Mapping) or segment not in current:
                return _MISSING
            current = current[segment]
        return current
