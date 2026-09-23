from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ConditionOperator = Literal[
    "exists",
    "equals",
    "not_equals",
    "gt",
    "gte",
    "lt",
    "lte",
    "in",
    "contains",
]


class Condition(BaseModel):
    field: str = Field(min_length=1)
    operator: ConditionOperator
    value: Any = None

    @model_validator(mode="after")
    def validate_value(self) -> "Condition":
        if self.operator == "exists" and self.value is not None:
            raise ValueError("exists conditions do not accept a value")
        if self.operator != "exists" and self.value is None:
            raise ValueError(f"{self.operator} conditions require a value")
        return self


class ConditionGroup(BaseModel):
    all: list[Condition] = Field(default_factory=list)
    any: list[Condition] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_condition(self) -> "ConditionGroup":
        if not self.all and not self.any:
            raise ValueError("conditions must define all or any")
        return self


class RuleDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category: str = Field(min_length=1)
    analytes: list[str] = Field(default_factory=list)
    conditions: ConditionGroup
    severity: str = Field(min_length=1)
    suggested_action: str = Field(min_length=1)
    source: str = Field(min_length=1)
    protocol: str | None = None
    effective_from: date | None = None
    method: str | None = None
    instrument: str | None = None
    enabled: bool = True
    parameters: dict[str, Any] = Field(default_factory=dict)


class EvaluationContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    result: dict[str, Any] = Field(default_factory=dict)
    sample: dict[str, Any] = Field(default_factory=dict)
    qc: dict[str, Any] = Field(default_factory=dict)
    previous: dict[str, Any] = Field(default_factory=dict)
    evaluated_at: datetime | None = None

    def as_mapping(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)


class ConditionEvidence(BaseModel):
    field: str
    operator: ConditionOperator
    observed_value: Any = None
    expected_value: Any = None
    matched: bool


class RuleResult(BaseModel):
    rule_id: str
    rule_version: str
    executed: bool
    applicable: bool
    triggered: bool
    severity: str
    reason: str
    evidence: list[ConditionEvidence] = Field(default_factory=list)
    suggested_action: str | None = None
    source: str
    evaluated_at: datetime
    skipped_reason: str | None = None


JsonValue = str | int | float | bool | Decimal | None
