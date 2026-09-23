from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field


ConsistencyCategory = Literal[
    "DATA_ERROR",
    "ANALYTICAL_REVIEW",
    "SPECIMEN_REVIEW",
    "CONFIGURATION_ERROR",
]
ConsistencyRelation = Literal[
    "difference",
    "ratio",
    "unit_match",
    "limits",
    "calculated_vs_measured",
    "sample_index_vs_result",
]


class AnalyteMeasurement(BaseModel):
    analyte: str = Field(min_length=1)
    value: Decimal | None = None
    unit: str | None = None
    source: Literal["measured", "calculated"] = "measured"


class ConsistencyContext(BaseModel):
    sample_id: str = Field(min_length=1)
    measurements: list[AnalyteMeasurement] = Field(min_length=1)
    sample_indices: dict[str, Decimal | str | None] = Field(default_factory=dict)
    result_flags: dict[str, Any] = Field(default_factory=dict)

    def measurement_map(self) -> dict[str, AnalyteMeasurement]:
        return {measurement.analyte: measurement for measurement in self.measurements}


class ConsistencyRuleConfig(BaseModel):
    rule_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    relation: ConsistencyRelation
    involved_analytes: list[str] = Field(min_length=1)
    category: ConsistencyCategory
    severity: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    version: str = Field(min_length=1)
    source: str = Field(min_length=1)


class ConsistencyEvent(BaseModel):
    event_type: Literal["CONSISTENCY_EVENT"] = "CONSISTENCY_EVENT"
    rule_id: str
    rule_version: str
    triggered: bool
    category: ConsistencyCategory
    involved_analytes: list[str]
    observed_values: dict[str, Any]
    relation_evaluated: str
    evidence: dict[str, Any]
    severity: str
    explanation: str
    recommendation: str
    sample_id: str
