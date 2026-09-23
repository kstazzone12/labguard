from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import ResultStatus, SampleStatus


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PatientCreate(BaseModel):
    synthetic_identifier: str = Field(min_length=1, max_length=100)


class PatientRead(SchemaBase):
    id: str
    synthetic_identifier: str
    created_at: datetime


class SampleCreate(BaseModel):
    patient_id: str
    sample_type: str = Field(min_length=1, max_length=100)
    collection_time: datetime
    processing_time: datetime | None = None
    status: SampleStatus = SampleStatus.COLLECTED
    hemolysis_index: Decimal | None = None
    lipemia_index: Decimal | None = None
    icterus_index: Decimal | None = None
    hemolysis_level: str | None = None
    lipemia_level: str | None = None
    icteria_level: str | None = None
    volume: Decimal | None = None
    volume_unit: str | None = None
    storage_condition: str | None = None
    instrument_flags: dict[str, Any] = Field(default_factory=dict)
    preanalytical_observations: str | None = None

    @model_validator(mode="after")
    def processing_cannot_precede_collection(self) -> "SampleCreate":
        if self.processing_time and self.processing_time < self.collection_time:
            raise ValueError("processing_time cannot precede collection_time")
        return self


class SampleRead(SchemaBase):
    id: str
    patient_id: str
    sample_type: str
    collection_time: datetime
    processing_time: datetime | None
    status: str
    hemolysis_index: Decimal | None
    lipemia_index: Decimal | None
    icterus_index: Decimal | None
    hemolysis_level: str | None
    lipemia_level: str | None
    icteria_level: str | None
    volume: Decimal | None
    volume_unit: str | None
    storage_condition: str | None
    instrument_flags: dict[str, Any]
    preanalytical_observations: str | None


class ResultCreate(BaseModel):
    analyte_id: str
    sample_id: str
    instrument_id: str | None = None
    method_id: str | None = None
    prior_result_id: str | None = None
    reference_interval_id: str | None = None
    value: str = Field(min_length=1, max_length=200)
    numeric_value: Decimal | None = None
    unit: str | None = None
    timestamp: datetime
    status: ResultStatus = ResultStatus.PRELIMINARY
    flags: dict[str, Any] = Field(default_factory=dict)
    quality_info: dict[str, Any] = Field(default_factory=dict)


class ResultRead(SchemaBase):
    id: str
    analyte_id: str
    sample_id: str
    instrument_id: str | None
    method_id: str | None
    prior_result_id: str | None
    reference_interval_id: str | None
    value: str
    numeric_value: Decimal | None
    unit: str | None
    timestamp: datetime
    status: str
    flags: dict[str, Any]
    quality_info: dict[str, Any]


class ReferenceIntervalCreate(BaseModel):
    analyte_id: str
    method_id: str | None = None
    instrument_id: str | None = None
    lower_value: Decimal | None = None
    upper_value: Decimal | None = None
    unit: str | None = None
    source: str | None = None
    protocol_version: str | None = None


class InterferenceConfigCreate(BaseModel):
    analyte_id: str
    method_id: str | None = None
    instrument_id: str | None = None
    manufacturer: str | None = None
    interference_type: str = Field(min_length=1)
    level: str | None = None
    parameter_name: str | None = None
    criterion: dict[str, Any] | None = None
    threshold_value: Decimal | None = None
    threshold_operator: str | None = None
    unit: str | None = None
    source: str | None = None
    source_type: str | None = None
    source_reference: str | None = None
    version: str | None = None
    effective_date: datetime | None = None
    enabled: bool = True
    protocol_version: str | None = None
