from datetime import UTC, datetime
from typing import Any

from app.analytical_consistency import AnalyticalConsistencyEvaluator
from app.delta_checks import DeltaCheckEvaluator
from app.engine import RuleEvaluator, RuleRegistry
from app.qc import QcRuleEvaluator
from app.specimen_quality import SpecimenQualityEvaluator
from app.validation_engine.models import (
    AuditTrailEntry,
    ReviewItem,
    ValidationInput,
    ValidationProfile,
)


class ValidationEngine:
    """Orchestrates evidence-producing modules without making professional decisions."""

    def evaluate(self, validation_input: ValidationInput) -> ValidationProfile:
        created_at = datetime.now(UTC)
        audit_trail: list[AuditTrailEntry] = []

        self._audit(audit_trail, "RESULT", validation_input.result, validation_input.laboratory_configuration, validation_input.result)

        qc_decisions = QcRuleEvaluator().evaluate(validation_input.qc_observations, validation_input.qc_rules)
        self._audit(audit_trail, "QC", {"observations": len(validation_input.qc_observations)}, validation_input.laboratory_configuration, {"decisions": len(qc_decisions), "triggered": sum(item.triggered for item in qc_decisions)})

        specimen_events = SpecimenQualityEvaluator().evaluate(validation_input.sample, validation_input.interferences)
        self._audit(audit_trail, "SPECIMEN_QUALITY", validation_input.sample.model_dump(), validation_input.laboratory_configuration, {"events": len(specimen_events)})
        self._audit(audit_trail, "INTERFERENCE", {"configurations": len(validation_input.interferences)}, validation_input.laboratory_configuration, {"review_required": sum(event.status == "REVIEW_REQUIRED" for event in specimen_events)})

        delta_events = DeltaCheckEvaluator().evaluate(validation_input.previous_results, validation_input.delta_rules)
        self._audit(audit_trail, "DELTA_CHECK", {"rules": len(validation_input.delta_rules)}, validation_input.laboratory_configuration, {"events": len(delta_events), "activated": sum(event.rule_activated is not None for event in delta_events)})

        consistency_events = AnalyticalConsistencyEvaluator().evaluate(validation_input.consistency, validation_input.consistency_rules)
        self._audit(audit_trail, "CONSISTENCY", {"rules": len(validation_input.consistency_rules)}, validation_input.laboratory_configuration, {"events": len(consistency_events), "triggered": sum(event.triggered for event in consistency_events)})

        rule_results = RuleEvaluator().evaluate(validation_input.rule_context, RuleRegistry(validation_input.rules))
        self._audit(audit_trail, "RULE_ENGINE", {"rules": len(validation_input.rules)}, validation_input.laboratory_configuration, {"results": len(rule_results), "triggered": sum(item.triggered for item in rule_results)})

        review_items = self._review_items(qc_decisions, specimen_events, delta_events, consistency_events, rule_results)
        recommendation = "Se recomienda revisión profesional." if review_items else "No se produjo ninguna señal de revisión configurada."
        self._audit(audit_trail, "VALIDATION_PROFILE", {"result_id": validation_input.result.get("id")}, validation_input.laboratory_configuration, {"review_items": len(review_items), "recommendation": recommendation})
        self._audit(audit_trail, "PROFESSIONAL_REVIEW", {"decision": "not_recorded"}, validation_input.laboratory_configuration, {"decision": "not_recorded"})

        return ValidationProfile(
            created_at=created_at,
            result_id=str(validation_input.result.get("id", "unknown-result")),
            evaluated=[entry.stage for entry in audit_trail],
            result=validation_input.result,
            qc_decisions=qc_decisions,
            specimen_events=specimen_events,
            delta_events=delta_events,
            consistency_events=consistency_events,
            rule_results=rule_results,
            audit_trail=audit_trail,
            review_items=review_items,
            system_recommendation=recommendation,
            professional_decision={"status": "not_recorded"},
        )

    @staticmethod
    def _audit(
        trail: list[AuditTrailEntry],
        stage: str,
        input_summary: dict[str, Any],
        laboratory_configuration,
        output_summary: dict[str, Any],
    ) -> None:
        trail.append(
            AuditTrailEntry(
                stage=stage,
                timestamp=datetime.now(UTC),
                input_summary=input_summary,
                configuration={
                    "configuration_version": laboratory_configuration.configuration_version,
                    "laboratory_identifier": laboratory_configuration.laboratory_identifier,
                },
                output_summary=output_summary,
                evidence={"source": "ValidationEngine"},
            )
        )

    @staticmethod
    def _review_items(qc_decisions, specimen_events, delta_events, consistency_events, rule_results) -> list[ReviewItem]:
        items: list[ReviewItem] = []
        items.extend(
            ReviewItem(source="QC", reason=decision.reason, evidence=decision.evidence, rule_id=decision.rule_id)
            for decision in qc_decisions
            if decision.triggered
        )
        items.extend(
            ReviewItem(source="SPECIMEN_QUALITY", reason=event.evidence, evidence={"possible_impact": event.possible_impact, "source_reference": event.source_reference}, rule_id=event.interference_id)
            for event in specimen_events
            if event.status == "REVIEW_REQUIRED"
        )
        items.extend(
            ReviewItem(source="DELTA_CHECK", reason=event.reason, evidence=event.evidence, rule_id=event.rule_activated)
            for event in delta_events
            if event.rule_activated is not None
        )
        items.extend(
            ReviewItem(source="CONSISTENCY", reason=event.explanation, evidence=event.evidence, rule_id=event.rule_id)
            for event in consistency_events
            if event.triggered
        )
        items.extend(
            ReviewItem(source="RULE_ENGINE", reason=result.reason, evidence={item.field: item.observed_value for item in result.evidence}, rule_id=result.rule_id)
            for result in rule_results
            if result.triggered
        )
        return items
