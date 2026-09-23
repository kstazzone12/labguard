from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.delta_checks.calculations import calculate_metrics
from app.delta_checks.models import (
    DeltaComparisonContext,
    DeltaEvent,
    DeltaMetrics,
    DeltaRuleConfig,
)


class DeltaCheckEvaluator:
    """Evaluates configurable comparisons without unit or method equivalence."""

    def evaluate(
        self,
        context: DeltaComparisonContext,
        rules: Sequence[DeltaRuleConfig],
    ) -> list[DeltaEvent]:
        return [self._evaluate_rule(context, rule) for rule in rules]

    def _evaluate_rule(self, context: DeltaComparisonContext, rule: DeltaRuleConfig) -> DeltaEvent:
        current = context.current
        timestamp = current.timestamp
        base = {
            "patient_id": current.patient_id,
            "current_sample_id": current.sample_id,
            "current_result_id": current.result_id,
            "previous_result_id": context.previous.result_id if context.previous else None,
            "analyte": current.analyte,
            "absolute_delta": None,
            "percentage_delta": None,
            "interval": None,
            "rule_activated": None,
            "comparison_available": False,
            "evidence": {"comparison_available": False},
            "timestamp": timestamp,
        }
        if not rule.enabled:
            return DeltaEvent(**base, reason="Delta check no disponible: regla deshabilitada.", recommendation=rule.recommendation)
        if rule.analytes and current.analyte not in rule.analytes:
            return DeltaEvent(**base, reason="Delta check no disponible: analito fuera del alcance.", recommendation=rule.recommendation)
        if context.previous is None:
            return DeltaEvent(**base, reason="Delta check no disponible: no hay resultado previo.", recommendation=rule.recommendation)

        invalid_reason = self._invalid_reason(context, rule)
        metrics = calculate_metrics(context)
        if invalid_reason or metrics is None:
            return self._unavailable(base, invalid_reason or "Delta check no disponible: datos incompletos.", rule, metrics)

        triggered, evidence = self._matches(metrics, rule)
        event_data = dict(base)
        event_data.update(
            absolute_delta=metrics.absolute_delta,
            percentage_delta=metrics.percentage_delta,
            interval=metrics.interval,
            rule_activated=rule.rule_id if triggered else None,
            comparison_available=True,
            evidence=evidence,
        )
        return DeltaEvent(
            **event_data,
            reason=("Delta check activado" if triggered else "Delta check no activado"),
            recommendation=rule.recommendation,
        )

    def _invalid_reason(self, context: DeltaComparisonContext, rule: DeltaRuleConfig) -> str | None:
        current = context.current
        previous = context.previous
        assert previous is not None
        if current.patient_id != previous.patient_id:
            return "Delta check no disponible: paciente diferente."
        if current.analyte != previous.analyte:
            return "Delta check no disponible: analito diferente."
        if current.timestamp <= previous.timestamp:
            return "Delta check no disponible: intervalo temporal inválido."
        if rule.require_same_unit and current.unit != previous.unit:
            return "Delta check no disponible: unidad diferente."
        if rule.require_same_method and current.method != previous.method:
            return "Delta check no disponible: método diferente."
        if rule.require_same_instrument and current.instrument != previous.instrument:
            return "Delta check no disponible: instrumento diferente."
        if rule.require_same_reference_interval and current.reference_interval_id != previous.reference_interval_id:
            return "Delta check no disponible: intervalo de referencia diferente."
        interval_hours = Decimal(str((current.timestamp - previous.timestamp).total_seconds())) / Decimal("3600")
        if rule.min_interval_hours is not None and interval_hours < rule.min_interval_hours:
            return "Delta check no disponible: resultados demasiado próximos."
        if rule.max_interval_hours is not None and interval_hours > rule.max_interval_hours:
            return "Delta check no disponible: resultado previo demasiado antiguo."
        return None

    @staticmethod
    def _matches(metrics: DeltaMetrics, rule: DeltaRuleConfig) -> tuple[bool, dict[str, Any]]:
        if rule.rule_type == "percentage":
            triggered = metrics.percentage_delta is not None and abs(metrics.percentage_delta) >= (rule.percentage_limit or Decimal("0"))
            return triggered, {"rule_type": rule.rule_type, "percentage_delta": metrics.percentage_delta, "percentage_limit": rule.percentage_limit}
        if rule.rule_type == "absolute":
            triggered = abs(metrics.absolute_delta) >= (rule.absolute_limit or Decimal("0"))
            return triggered, {"rule_type": rule.rule_type, "absolute_delta": metrics.absolute_delta, "absolute_limit": rule.absolute_limit}
        observed = metrics.absolute_delta if rule.limit_metric == "absolute" else metrics.percentage_delta
        if observed is None:
            return False, {"rule_type": rule.rule_type, "limit_metric": rule.limit_metric, "observed": None}
        lower_ok = rule.lower_limit is None or observed >= rule.lower_limit
        upper_ok = rule.upper_limit is None or observed <= rule.upper_limit
        return not (lower_ok and upper_ok), {"rule_type": rule.rule_type, "limit_metric": rule.limit_metric, "observed": observed, "lower_limit": rule.lower_limit, "upper_limit": rule.upper_limit}

    @staticmethod
    def _unavailable(base: dict[str, Any], reason: str, rule: DeltaRuleConfig, metrics: DeltaMetrics | None) -> DeltaEvent:
        event_data = dict(base)
        event_data.update(
            absolute_delta=metrics.absolute_delta if metrics else None,
            percentage_delta=metrics.percentage_delta if metrics else None,
            interval=metrics.interval if metrics else None,
            evidence={"comparison_available": False, "reason": reason},
        )
        return DeltaEvent(
            **event_data,
            reason=reason,
            recommendation=rule.recommendation,
        )
