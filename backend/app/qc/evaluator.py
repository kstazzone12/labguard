from collections.abc import Sequence
from datetime import UTC, datetime

from app.qc.models import QcAlert, QcObservation, QcRuleConfig, QcRuleDecision
from app.qc.rules import RULE_FUNCTIONS, calculate_observation_z_scores


class QcRuleEvaluator:
    """Applies configurable QC rule policies to observations.

    Mathematical functions remain separate from laboratory policy such as
    severity and suggested action.
    """

    def evaluate(
        self,
        observations: Sequence[QcObservation],
        configurations: Sequence[QcRuleConfig],
    ) -> list[QcRuleDecision]:
        if not observations:
            return []
        z_scores = calculate_observation_z_scores(observations)
        latest = observations[-1]
        decisions: list[QcRuleDecision] = []
        for configuration in configurations:
            if not configuration.enabled:
                decisions.append(self._skipped(configuration, "Rule disabled"))
                continue
            rule_function = RULE_FUNCTIONS[configuration.code]
            if len(z_scores) < configuration.window_size:
                decisions.append(self._skipped(configuration, "Insufficient observations for configured window"))
                continue
            triggered, evidence = rule_function(z_scores, configuration.threshold_sd)
            alert = None
            if triggered:
                alert = QcAlert(
                    rule_id=configuration.rule_id,
                    control=latest.control,
                    result=latest.result,
                    evidence=evidence,
                    severity=configuration.severity,
                    timestamp=latest.timestamp,
                    suggested_action=configuration.suggested_action,
                )
            decisions.append(
                QcRuleDecision(
                    rule_id=configuration.rule_id,
                    code=configuration.code,
                    executed=True,
                    triggered=triggered,
                    reason=("QC rule triggered" if triggered else "QC rule not triggered"),
                    evidence=evidence,
                    alert=alert,
                )
            )
        return decisions

    @staticmethod
    def _skipped(configuration: QcRuleConfig, reason: str) -> QcRuleDecision:
        return QcRuleDecision(
            rule_id=configuration.rule_id,
            code=configuration.code,
            executed=False,
            triggered=False,
            reason=reason,
            evidence={},
        )
