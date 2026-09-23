from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import (
    AlertSeverity,
    AlertStatus,
    AuditAction,
    QcStatus,
    ResultStatus,
    RuleStatus,
    SampleStatus,
    ValidationOutcome,
)


def new_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    synthetic_identifier: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    samples: Mapped[list["Sample"]] = relationship(back_populates="patient")


class Sample(Base):
    __tablename__ = "samples"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), nullable=False)
    sample_type: Mapped[str] = mapped_column(String(100), nullable=False)
    collection_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    processing_time: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(30), default=SampleStatus.COLLECTED.value, nullable=False)
    hemolysis_index: Mapped[Decimal | None] = mapped_column(Numeric)
    lipemia_index: Mapped[Decimal | None] = mapped_column(Numeric)
    icterus_index: Mapped[Decimal | None] = mapped_column(Numeric)
    hemolysis_level: Mapped[str | None] = mapped_column(String(50))
    lipemia_level: Mapped[str | None] = mapped_column(String(50))
    icteria_level: Mapped[str | None] = mapped_column(String(50))
    volume: Mapped[Decimal | None] = mapped_column(Numeric)
    volume_unit: Mapped[str | None] = mapped_column(String(50))
    storage_condition: Mapped[str | None] = mapped_column(String(200))
    instrument_flags: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    preanalytical_observations: Mapped[str | None] = mapped_column(Text)

    patient: Mapped[Patient] = relationship(back_populates="samples")
    results: Mapped[list["Result"]] = relationship(back_populates="sample")


class Analyte(Base):
    __tablename__ = "analytes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    discipline: Mapped[str] = mapped_column(String(100), nullable=False)


class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(200))
    model: Mapped[str | None] = mapped_column(String(200))
    serial_number: Mapped[str | None] = mapped_column(String(200))
    active: Mapped[bool] = mapped_column(default=True, nullable=False)


class Method(Base):
    __tablename__ = "methods"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(200))
    protocol_version: Mapped[str | None] = mapped_column(String(100))


class ReferenceInterval(Base):
    __tablename__ = "reference_intervals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analyte_id: Mapped[str] = mapped_column(ForeignKey("analytes.id"), nullable=False)
    method_id: Mapped[str | None] = mapped_column(ForeignKey("methods.id"))
    instrument_id: Mapped[str | None] = mapped_column(ForeignKey("instruments.id"))
    lower_value: Mapped[Decimal | None] = mapped_column(Numeric)
    upper_value: Mapped[Decimal | None] = mapped_column(Numeric)
    unit: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str | None] = mapped_column(String(200))
    protocol_version: Mapped[str | None] = mapped_column(String(100))


class Result(Base):
    __tablename__ = "results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analyte_id: Mapped[str] = mapped_column(ForeignKey("analytes.id"), nullable=False)
    sample_id: Mapped[str] = mapped_column(ForeignKey("samples.id"), nullable=False)
    instrument_id: Mapped[str | None] = mapped_column(ForeignKey("instruments.id"))
    method_id: Mapped[str | None] = mapped_column(ForeignKey("methods.id"))
    prior_result_id: Mapped[str | None] = mapped_column(ForeignKey("results.id"))
    reference_interval_id: Mapped[str | None] = mapped_column(ForeignKey("reference_intervals.id"))
    value: Mapped[str] = mapped_column(String(200), nullable=False)
    numeric_value: Mapped[Decimal | None] = mapped_column(Numeric)
    unit: Mapped[str | None] = mapped_column(String(50))
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default=ResultStatus.PRELIMINARY.value, nullable=False)
    flags: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    quality_info: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    sample: Mapped[Sample] = relationship(back_populates="results")
    prior_result: Mapped["Result | None"] = relationship(remote_side=[id])


class QcRun(Base):
    __tablename__ = "qc_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    instrument_id: Mapped[str] = mapped_column(ForeignKey("instruments.id"), nullable=False)
    method_id: Mapped[str] = mapped_column(ForeignKey("methods.id"), nullable=False)
    control_material: Mapped[str] = mapped_column(String(200), nullable=False)
    run_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    run_number: Mapped[int] = mapped_column(nullable=False)
    level: Mapped[str] = mapped_column(String(100), nullable=False)
    lot_identifier: Mapped[str | None] = mapped_column(String(100))
    operator: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), default=QcStatus.ACCEPTED.value, nullable=False)


class QcResult(Base):
    __tablename__ = "qc_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    qc_run_id: Mapped[str] = mapped_column(ForeignKey("qc_runs.id"), nullable=False)
    analyte_id: Mapped[str] = mapped_column(ForeignKey("analytes.id"), nullable=False)
    value: Mapped[str] = mapped_column(String(200), nullable=False)
    result_value: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    mean: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    standard_deviation: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    cv_percent: Mapped[Decimal | None] = mapped_column(Numeric)
    z_score: Mapped[Decimal | None] = mapped_column(Numeric)
    sd_index: Mapped[Decimal | None] = mapped_column(Numeric)
    position: Mapped[str | None] = mapped_column(String(50))
    unit: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default=QcStatus.ACCEPTED.value, nullable=False)
    flags: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class Interference(Base):
    __tablename__ = "interferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    analyte_id: Mapped[str] = mapped_column(ForeignKey("analytes.id"), nullable=False)
    method_id: Mapped[str | None] = mapped_column(ForeignKey("methods.id"))
    instrument_id: Mapped[str | None] = mapped_column(ForeignKey("instruments.id"))
    manufacturer: Mapped[str | None] = mapped_column(String(200))
    interference_type: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[str | None] = mapped_column(String(100))
    parameter_name: Mapped[str | None] = mapped_column(String(100))
    criterion: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    source_type: Mapped[str | None] = mapped_column(String(50))
    source_reference: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str | None] = mapped_column(String(50))
    effective_date: Mapped[datetime | None] = mapped_column(DateTime)
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    threshold_value: Mapped[Decimal | None] = mapped_column(Numeric)
    threshold_operator: Mapped[str | None] = mapped_column(String(10))
    unit: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str | None] = mapped_column(String(200))
    protocol_version: Mapped[str | None] = mapped_column(String(100))


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(150), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    discipline: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default=RuleStatus.DRAFT.value, nullable=False)
    definition: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    rule_id: Mapped[str | None] = mapped_column(ForeignKey("rules.id"))
    result_id: Mapped[str | None] = mapped_column(ForeignKey("results.id"))
    severity: Mapped[str] = mapped_column(String(30), default=AlertSeverity.REVIEW.value, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default=AlertStatus.OPEN.value, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class ValidationEvent(Base):
    __tablename__ = "validation_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    sample_id: Mapped[str | None] = mapped_column(ForeignKey("samples.id"))
    result_id: Mapped[str | None] = mapped_column(ForeignKey("results.id"))
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_role: Mapped[str | None] = mapped_column(String(100))
    outcome: Mapped[str] = mapped_column(String(30), default=ValidationOutcome.PENDING.value, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    action: Mapped[str] = mapped_column(String(30), default=AuditAction.CREATED.value, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(100))
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
