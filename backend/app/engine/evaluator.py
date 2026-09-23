from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime
from operator import contains, eq, ge, gt, le, lt, ne
from typing import Any, Callable

from app.engine.models import (
    Condition,
    ConditionEvidence,
    EvaluationContext,
    RuleDefinition,
    RuleResult,
)
from app.engine.registry import RuleRegistry


_MISSING = object()
_OPERATORS: dict[str, Callable[[Any, Any], bool]] = {
    "equals": eq,
    "not_equals": ne,
    "gt": gt,
    "gte": ge,
    "lt": lt,
    "lte": le,
    "contains": contains,
}


class RuleEvaluator:
    def evaluate(
        self,
        context: EvaluationContext | Mapping[str, Any],
        registry: RuleRegistry,
    ) -> list[RuleResult]:
        evaluation_context = (
            context if isinstance(context, EvaluationContext) else EvaluationContext.model_validate(context)
        )
        evaluated_at = evaluation_context.evaluated_at or datetime.now(UTC)
        return [
            self.evaluate_rule(evaluation_context, rule, evaluated_at)
            for rule in registry.all()
        ]

    def evaluate_rule(
        self,
        context: EvaluationContext,
        rule: RuleDefinition,
        evaluated_at: datetime | None = None,
    ) -> RuleResult:
        timestamp = evaluated_at or context.evaluated_at or datetime.now(UTC)
        applicable, skipped_reason = self._is_applicable(context, rule, timestamp.date())
        if not rule.enabled or not applicable:
            return RuleResult(
                rule_id=rule.id,
                rule_version=rule.version,
                executed=False,
                applicable=applicable,
                triggered=False,
                severity=rule.severity,
                reason="Rule not executed",
                source=rule.source,
                evaluated_at=timestamp,
                skipped_reason=skipped_reason or "Rule disabled",
            )

        evidence = [
            self._evaluate_condition(context.as_mapping(), condition)
            for condition in [*rule.conditions.all, *rule.conditions.any]
        ]
        all_match = all(item.matched for item in evidence[: len(rule.conditions.all)])
        any_offset = len(rule.conditions.all)
        any_evidence = evidence[any_offset:]
        any_match = not any_evidence or any(item.matched for item in any_evidence)
        triggered = all_match and any_match
        return RuleResult(
            rule_id=rule.id,
            rule_version=rule.version,
            executed=True,
            applicable=True,
            triggered=triggered,
            severity=rule.severity,
            reason=("Configured conditions matched" if triggered else "Configured conditions did not match"),
            evidence=evidence,
            suggested_action=rule.suggested_action if triggered else None,
            source=rule.source,
            evaluated_at=timestamp,
        )

    def _is_applicable(
        self,
        context: EvaluationContext,
        rule: RuleDefinition,
        evaluated_date: date,
    ) -> tuple[bool, str | None]:
        if not rule.enabled:
            return False, "Rule disabled"
        if rule.effective_from and evaluated_date < rule.effective_from:
            return False, "Rule is not effective yet"
        analyte_code = context.result.get("analyte_code")
        if rule.analytes and analyte_code not in rule.analytes:
            return False, "Analyte is outside rule scope"
        if rule.method and context.result.get("method_code") != rule.method:
            return False, "Method is outside rule scope"
        if rule.instrument and context.result.get("instrument_code") != rule.instrument:
            return False, "Instrument is outside rule scope"
        return True, None

    def _evaluate_condition(
        self,
        context: Mapping[str, Any],
        condition: Condition,
    ) -> ConditionEvidence:
        observed = self._resolve_path(context, condition.field)
        matched = self._match(condition, observed)
        return ConditionEvidence(
            field=condition.field,
            operator=condition.operator,
            observed_value=None if observed is _MISSING else observed,
            expected_value=condition.value,
            matched=matched,
        )

    def _match(self, condition: Condition, observed: Any) -> bool:
        if condition.operator == "exists":
            return observed is not _MISSING and observed is not None
        if observed is _MISSING:
            return False
        try:
            if condition.operator == "in":
                return observed in condition.value
            return _OPERATORS[condition.operator](observed, condition.value)
        except (TypeError, KeyError):
            return False

    @staticmethod
    def _resolve_path(context: Mapping[str, Any], path: str) -> Any:
        current: Any = context
        for segment in path.split("."):
            if not isinstance(current, Mapping) or segment not in current:
                return _MISSING
            current = current[segment]
        return current
