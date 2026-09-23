from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field


QcRuleCode = Literal["1_2s", "1_3s", "2_2s", "R_4s", "4_1s", "10x"]


class ControlIdentity(BaseModel):
    material: str = Field(min_length=1)
    lot: str = Field(min_length=1)
    level: str = Field(min_length=1)
    analyte: str = Field(min_length=1)
    method: str = Field(min_length=1)
    instrument: str = Field(min_length=1)


class QcObservation(BaseModel):
    control: ControlIdentity
    run_number: int = Field(ge=1)
    timestamp: datetime
    result: Decimal
    mean: Decimal
    standard_deviation: Decimal = Field(gt=0)
    operator: str | None = None


class QcLimits(BaseModel):
    lower: Decimal | None = None
    upper: Decimal | None = None
    lower_sd: Decimal | None = Field(default=None, gt=0)
    upper_sd: Decimal | None = Field(default=None, gt=0)


class QcMetrics(BaseModel):
    difference_from_mean: Decimal
    z_score: Decimal
    sd_index: Decimal
    cv_percent: Decimal | None
    position: str
    lower_limit: Decimal | None
    upper_limit: Decimal | None


class QcRuleConfig(BaseModel):
    rule_id: str = Field(min_length=1)
    code: QcRuleCode
    name: str = Field(min_length=1)
    enabled: bool = True
    severity: str = Field(min_length=1)
    suggested_action: str = Field(min_length=1)
    window_size: int = Field(ge=1)
    threshold_sd: Decimal = Field(gt=0)
    require_same_side: bool = True


class QcAlert(BaseModel):
    event_type: Literal["QC_ALERT"] = "QC_ALERT"
    rule_id: str
    control: ControlIdentity
    result: Decimal
    evidence: dict[str, Any]
    severity: str
    timestamp: datetime
    suggested_action: str | None = None


class QcRuleDecision(BaseModel):
    rule_id: str
    code: QcRuleCode
    executed: bool
    triggered: bool
    reason: str
    evidence: dict[str, Any]
    alert: QcAlert | None = None
