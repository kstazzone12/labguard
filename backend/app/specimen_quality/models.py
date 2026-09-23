from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field


SourceType = Literal["manufacturer", "laboratory_SOP", "published_reference", "regulatory_document"]
CriterionOperator = Literal["equals", "not_equals", "in", "gt", "gte", "lt", "lte"]


class SpecimenQualityContext(BaseModel):
    sample_id: str = Field(min_length=1)
    analyte: str = Field(min_length=1)
    method: str | None = None
    instrument: str | None = None
    manufacturer: str | None = None
    sample_type: str = Field(min_length=1)
    hemolysis: str | None = None
    hemolysis_index: Decimal | None = None
    lipemia: str | None = None
    lipemia_index: Decimal | None = None
    icteria: str | None = None
    icteria_index: Decimal | None = None
    volume: Decimal | None = None
    volume_unit: str | None = None
    collection_time: datetime | None = None
    processing_time: datetime | None = None
    storage_condition: str | None = None
    observations: str | None = None
    instrument_flags: dict[str, Any] = Field(default_factory=dict)


class InterferenceCriterion(BaseModel):
    field: str = Field(min_length=1)
    operator: CriterionOperator
    value: Any


class InterferenceConfig(BaseModel):
    interference_id: str = Field(min_length=1)
    analyte: str = Field(min_length=1)
    method: str | None = None
    manufacturer: str | None = None
    instrument: str | None = None
    interference_type: str = Field(min_length=1)
    level: str = Field(min_length=1)
    source_type: SourceType
    source_reference: str = Field(min_length=1)
    criterion: InterferenceCriterion
    version: str = Field(min_length=1)
    effective_date: date
    enabled: bool = True
    suggested_action: str = Field(min_length=1)


class SpecimenQualityEvent(BaseModel):
    event_type: Literal["SPECIMEN_QUALITY_EVENT"] = "SPECIMEN_QUALITY_EVENT"
    analyte: str
    sample_id: str
    evidence: str
    possible_impact: str | None
    status: Literal["REVIEW_REQUIRED", "NO_CONFIGURED_INTERFERENCE"]
    interference_id: str | None
    source_type: SourceType | None
    source_reference: str | None
    criterion: dict[str, Any] | None
    timestamp: datetime
    recommendation: str
