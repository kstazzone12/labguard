from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field


DeltaRuleType = Literal["percentage", "absolute", "limits"]
DeltaLimitMetric = Literal["absolute", "percentage"]


class DeltaMeasurement(BaseModel):
    patient_id: str = Field(min_length=1)
    sample_id: str = Field(min_length=1)
    result_id: str = Field(min_length=1)
    analyte: str = Field(min_length=1)
    value: Decimal
    unit: str | None = None
    timestamp: datetime
    method: str | None = None
    instrument: str | None = None
    reference_interval_id: str | None = None


class DeltaComparisonContext(BaseModel):
    current: DeltaMeasurement
    previous: DeltaMeasurement | None = None


class DeltaRuleConfig(BaseModel):
    rule_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    rule_type: DeltaRuleType
    analytes: list[str] = Field(default_factory=list)
    enabled: bool = True
    severity: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)
    percentage_limit: Decimal | None = Field(default=None, ge=0)
    absolute_limit: Decimal | None = Field(default=None, ge=0)
    lower_limit: Decimal | None = None
    upper_limit: Decimal | None = None
    limit_metric: DeltaLimitMetric = "absolute"
    min_interval_hours: Decimal | None = Field(default=None, ge=0)
    max_interval_hours: Decimal | None = Field(default=None, ge=0)
    require_same_unit: bool = True
    require_same_method: bool = True
    require_same_instrument: bool = True
    require_same_reference_interval: bool = True
    source: str = Field(min_length=1)


class DeltaMetrics(BaseModel):
    absolute_delta: Decimal
    percentage_delta: Decimal | None
    interval: timedelta
    interval_hours: Decimal


class DeltaEvent(BaseModel):
    event_type: Literal["DELTA_EVENT"] = "DELTA_EVENT"
    patient_id: str
    current_sample_id: str
    current_result_id: str
    previous_result_id: str | None
    analyte: str
    absolute_delta: Decimal | None
    percentage_delta: Decimal | None
    interval: timedelta | None
    rule_activated: str | None
    comparison_available: bool
    reason: str
    evidence: dict[str, Any]
    recommendation: str
    timestamp: datetime
