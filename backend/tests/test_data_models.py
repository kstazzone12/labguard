from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Analyte, Patient, Result, Sample
from app.schemas import ResultCreate, SampleCreate
from app.services.synthetic_data import load_minimal_case


def test_database_contains_core_entities() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    table_names = set(inspect(engine).get_table_names())

    assert {"patients", "samples", "results", "audit_events"}.issubset(table_names)


def test_patient_is_separate_from_analytic_result() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        patient = Patient(synthetic_identifier="SYNTH-TEST-001")
        sample = Sample(
            patient=patient,
            sample_type="synthetic-serum",
            collection_time=datetime(2026, 1, 1, 8, 0),
        )
        analyte = Analyte(
            code="SYNTH-ANALYTE-TEST",
            name="Synthetic analyte",
            discipline="chemistry",
        )
        session.add_all([patient, sample, analyte])
        session.flush()

        result = Result(
            sample=sample,
            analyte_id=analyte.id,
            value="10",
            numeric_value=10,
            unit="synthetic-unit",
            timestamp=datetime(2026, 1, 1, 8, 30),
        )
        session.add(result)
        session.commit()

        assert result.sample.patient.synthetic_identifier == "SYNTH-TEST-001"
        assert not hasattr(result, "synthetic_identifier")


def test_sample_rejects_processing_before_collection() -> None:
    collection_time = datetime(2026, 1, 1, 8, 0)

    with pytest.raises(ValueError, match="processing_time"):
        SampleCreate(
            patient_id="patient-1",
            sample_type="serum",
            collection_time=collection_time,
            processing_time=collection_time - timedelta(minutes=1),
        )


def test_result_schema_keeps_quality_and_prior_result_links() -> None:
    result = ResultCreate(
        analyte_id="analyte-1",
        sample_id="sample-1",
        prior_result_id="result-previous",
        value="12.5",
        numeric_value=12.5,
        unit="synthetic-unit",
        timestamp=datetime(2026, 1, 1, 8, 30),
        quality_info={"qc_available": False},
    )

    assert result.prior_result_id == "result-previous"
    assert result.quality_info == {"qc_available": False}


def test_synthetic_dataset_has_no_reference_or_interference_limits() -> None:
    dataset = load_minimal_case()

    assert dataset["purpose"] == "development-only"
    assert dataset["reference_intervals"] == []
    assert dataset["interferences"] == []
