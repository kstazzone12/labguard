from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ImportStatus(StrEnum):
    VALID = "VALID"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ImportIssue(BaseModel):
    code: str
    message: str
    field: str | None = None
    severity: ImportStatus


class ProfessionalRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    patient_id: str = Field(min_length=1)
    sample_id: str = Field(min_length=1)
    date: date
    time: str = Field(min_length=1)
    analyte: str = Field(min_length=1)
    value: float
    unit: str = Field(min_length=1)
    specimen: str = Field(min_length=1)
    method: str = Field(min_length=1)
    instrument: str = Field(min_length=1)
    flag: str = ""
    loinc_code: str | None = None
    id: str | None = None
    previous_value: float | None = None
    previous_date: date | None = None
    hemolysis_index: float | None = None
    icterus_index: float | None = None
    lipemia_index: float | None = None
    qc_status: str = ""


class ImportRecord(BaseModel):
    row_number: int
    status: ImportStatus
    data: ProfessionalRecord | None = None
    issues: list[ImportIssue] = Field(default_factory=list)


class ImportPreview(BaseModel):
    source_format: str
    total_rows: int
    records: list[ImportRecord]
    can_import: bool


class StoredProfessionalRecord(ProfessionalRecord):
    imported_at: datetime
    source_format: str
    source_file_name: str | None = None


class KnowledgeSourceMetadata(BaseModel):
    dataset: str
    version: str
    release_date: date | None = None
    source: str
    license: str
    date_accessed: date
    local_dataset_hash: str | None = None


class LoincTerm(BaseModel):
    loinc_code: str
    component: str
    system: str
    property: str
    scale: str
    method: str | None = None
    long_common_name: str


class UnitResolution(BaseModel):
    original_unit: str
    normalized_unit: str | None = None
    conversion_factor: float | None = None
    conversion_source: str | None = None
    issue_code: str | None = None


class LoincSearchResult(BaseModel):
    status: str
    matches: list[LoincTerm] = Field(default_factory=list)
    issue_code: str | None = None


class ImportPreviewRequest(BaseModel):
    content: str
    source_format: str
