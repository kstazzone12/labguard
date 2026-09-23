from collections.abc import Callable, Mapping, Sequence
from decimal import Decimal, InvalidOperation
from operator import contains, eq, ge, gt, le, lt, ne
from typing import Any

from app.analytical_consistency.models import (
    AnalyteMeasurement,
    ConsistencyContext,
    ConsistencyEvent,
    ConsistencyRuleConfig,
)

_OPERATORS: dict[str, Callable[[Any, Any], bool]] = {
    "equals": eq,
    "not_equals": ne,
    "gt": gt,
    "gte": ge,
    "lt": lt,
    "lte": le,
    "contains": contains,
}


class AnalyticalConsistencyEvaluator:
    def evaluate(
        self,
        context: ConsistencyContext,
        rules: Sequence[ConsistencyRuleConfig],
    ) -> list[ConsistencyEvent]:
        return [self._evaluate_rule(context, rule) for rule in rules]

    def _evaluate_rule(self, context: ConsistencyContext, rule: ConsistencyRuleConfig) -> ConsistencyEvent:
        measurements = context.measurement_map()
        observed_values = {
            analyte: measurements[analyte].value
            for analyte in rule.involved_analytes
            if analyte in measurements
        }
        base = {
            "rule_id": rule.rule_id,
            "rule_version": rule.version,
            "category": rule.category,
            "involved_analytes": rule.involved_analytes,
            "observed_values": observed_values,
            "severity": rule.severity,
            "explanation": rule.explanation,
            "recommendation": rule.recommendation,
            "sample_id": context.sample_id,
        }
        if not rule.enabled:
            return ConsistencyEvent(
                **base,
                triggered=False,
                relation_evaluated="Rule disabled",
                evidence={"configuration": "disabled"},
            )
        try:
            triggered, relation, evidence = self._evaluate_relation(context, rule, measurements)
        except ValueError as error:
            error_message = str(error)
            error_category = (
                "DATA_ERROR"
                if "measurement value is missing" in error_message
                or "Required analyte is missing" in error_message
                or "sample index is missing" in error_message
                else "CONFIGURATION_ERROR"
            )
            error_base = dict(base)
            error_base["category"] = error_category
            return ConsistencyEvent(
                **error_base,
                triggered=False,
                relation_evaluated="Configuration could not be evaluated",
                evidence={"error": error_message},
            )
        return ConsistencyEvent(
            **base,
            triggered=triggered,
            relation_evaluated=relation,
            evidence=evidence,
        )

    def _evaluate_relation(
        self,
        context: ConsistencyContext,
        rule: ConsistencyRuleConfig,
        measurements: Mapping[str, AnalyteMeasurement],
    ) -> tuple[bool, str, dict[str, Any]]:
        if any(analyte not in measurements for analyte in rule.involved_analytes):
            raise ValueError("Required analyte is missing from context")
        if rule.relation == "difference":
            return self._difference(rule, measurements)
        if rule.relation == "ratio":
            return self._ratio(rule, measurements)
        if rule.relation == "unit_match":
            return self._unit_match(rule, measurements)
        if rule.relation == "limits":
            return self._limits(rule, measurements)
        if rule.relation == "calculated_vs_measured":
            return self._calculated_vs_measured(rule, measurements)
        if rule.relation == "sample_index_vs_result":
            return self._sample_index_vs_result(context, rule, measurements)
        raise ValueError(f"Unsupported relation: {rule.relation}")

    @staticmethod
    def _require_values(rule: ConsistencyRuleConfig, measurements: Mapping[str, AnalyteMeasurement]) -> list[Decimal]:
        values = [measurements[analyte].value for analyte in rule.involved_analytes]
        if any(value is None for value in values):
            raise ValueError("Required measurement value is missing")
        return [value for value in values if value is not None]

    def _difference(self, rule: ConsistencyRuleConfig, measurements: Mapping[str, AnalyteMeasurement]):
        values = self._require_values(rule, measurements)
        if len(values) != 2:
            raise ValueError("difference requires exactly two analytes")
        difference = values[0] - values[1]
        tolerance = self._decimal_parameter(rule, "tolerance")
        return abs(difference) > tolerance, f"abs({rule.involved_analytes[0]} - {rule.involved_analytes[1]}) <= configured tolerance", {"difference": difference, "tolerance": tolerance}

    def _ratio(self, rule: ConsistencyRuleConfig, measurements: Mapping[str, AnalyteMeasurement]):
        values = self._require_values(rule, measurements)
        if len(values) != 2 or values[1] == 0:
            raise ValueError("ratio requires two analytes and a non-zero denominator")
        ratio = values[0] / values[1]
        lower = self._decimal_parameter(rule, "lower")
        upper = self._decimal_parameter(rule, "upper")
        triggered = ratio < lower or ratio > upper
        return triggered, f"{rule.involved_analytes[0]} / {rule.involved_analytes[1]} within configured limits", {"ratio": ratio, "lower": lower, "upper": upper}

    @staticmethod
    def _unit_match(rule: ConsistencyRuleConfig, measurements: Mapping[str, AnalyteMeasurement]):
        units = {measurements[analyte].unit for analyte in rule.involved_analytes}
        triggered = len(units) > 1 or None in units
        return triggered, "Units compatible between configured analytes", {"units": list(units)}

    def _limits(self, rule: ConsistencyRuleConfig, measurements: Mapping[str, AnalyteMeasurement]):
        values = self._require_values(rule, measurements)
        if len(values) != 1:
            raise ValueError("limits requires exactly one analyte")
        lower = self._decimal_parameter(rule, "lower")
        upper = self._decimal_parameter(rule, "upper")
        triggered = values[0] < lower or values[0] > upper
        return triggered, f"{rule.involved_analytes[0]} within configured limits", {"value": values[0], "lower": lower, "upper": upper}

    def _calculated_vs_measured(self, rule: ConsistencyRuleConfig, measurements: Mapping[str, AnalyteMeasurement]):
        values = self._require_values(rule, measurements)
        tolerance = self._decimal_parameter(rule, "tolerance")
        difference = values[0] - values[1]
        triggered = abs(difference) > tolerance
        return triggered, "Calculated value compared with measured value using configured tolerance", {"difference": difference, "tolerance": tolerance}

    def _sample_index_vs_result(self, context: ConsistencyContext, rule: ConsistencyRuleConfig, measurements: Mapping[str, AnalyteMeasurement]):
        field = rule.parameters.get("index_field")
        operator = rule.parameters.get("operator")
        expected = rule.parameters.get("expected")
        if not isinstance(field, str) or operator not in _OPERATORS:
            raise ValueError("sample_index_vs_result requires index_field and supported operator")
        observed = context.sample_indices.get(field)
        if observed is None:
            raise ValueError("Configured sample index is missing")
        triggered = not _OPERATORS[operator](observed, expected)
        return triggered, f"Sample index {field} satisfies configured relation", {"index_field": field, "observed": observed, "operator": operator, "expected": expected}

    @staticmethod
    def _decimal_parameter(rule: ConsistencyRuleConfig, name: str) -> Decimal:
        value = rule.parameters.get(name)
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError):
            raise ValueError(f"Missing or invalid decimal parameter: {name}")
