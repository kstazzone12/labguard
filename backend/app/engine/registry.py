from collections.abc import Iterable

from app.engine.models import RuleDefinition


class RuleRegistry:
    def __init__(self, rules: Iterable[RuleDefinition] = ()) -> None:
        self._rules: dict[tuple[str, str], RuleDefinition] = {}
        for rule in rules:
            self.register(rule)

    def register(self, rule: RuleDefinition) -> None:
        key = (rule.id, rule.version)
        if key in self._rules:
            raise ValueError(f"Duplicate rule: {rule.id} version {rule.version}")
        self._rules[key] = rule

    def all(self) -> tuple[RuleDefinition, ...]:
        return tuple(self._rules.values())

    def enabled(self) -> tuple[RuleDefinition, ...]:
        return tuple(rule for rule in self._rules.values() if rule.enabled)

    def get(self, rule_id: str, version: str) -> RuleDefinition:
        try:
            return self._rules[(rule_id, version)]
        except KeyError as error:
            raise KeyError(f"Unknown rule: {rule_id} version {version}") from error
