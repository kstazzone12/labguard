from datetime import UTC, datetime
from decimal import Decimal

from app.specimen_quality import (
    InterferenceConfig,
    SpecimenQualityContext,
    SpecimenQualityEvaluator,
)


def context(**overrides) -> SpecimenQualityContext:
    values = {
        "sample_id": "sample-1",
        "analyte": "SYN-ANALYTE-01",
        "method": "SYN-METHOD-01",
        "instrument": "SYN-INSTRUMENT-01",
        "manufacturer": "SYNTHETIC-MANUFACTURER",
        "sample_type": "synthetic-serum",
        "hemolysis": "HIGH",
        "lipemia": "NOT_REPORTED",
        "icteria": "NOT_REPORTED",
        "volume": Decimal("1.0"),
        "volume_unit": "synthetic-unit",
        "collection_time": datetime(2026, 1, 1, 8, tzinfo=UTC),
        "processing_time": datetime(2026, 1, 1, 9, tzinfo=UTC),
        "storage_condition": "DEMO_REFRIGERATED",
        "instrument_flags": {"sample_quality": "DEMO_FLAG"},
    }
    values.update(overrides)
    return SpecimenQualityContext(**values)


def interference(**overrides) -> InterferenceConfig:
    values = {
        "interference_id": "DEMO-INTERFERENCE-001",
        "analyte": "SYN-ANALYTE-01",
        "method": "SYN-METHOD-01",
        "manufacturer": "SYNTHETIC-MANUFACTURER",
        "instrument": "SYN-INSTRUMENT-01",
        "interference_type": "DEMO_HEMOLYSIS_INTERFERENCE",
        "level": "HIGH",
        "source_type": "laboratory_SOP",
        "source_reference": "DEMO_PLACEHOLDER_SOP_001",
        "criterion": {"field": "hemolysis", "operator": "equals", "value": "HIGH"},
        "version": "DEMO-1.0",
        "effective_date": "2026-01-01",
        "suggested_action": "Solicitar revisión profesional.",
    }
    values.update(overrides)
    return InterferenceConfig(**values)


def test_configured_interference_produces_review_event() -> None:
    event = SpecimenQualityEvaluator().evaluate(context(), [interference()])[0]

    assert event.status == "REVIEW_REQUIRED"
    assert event.analyte == "SYN-ANALYTE-01"
    assert event.evidence == "Sample quality flag: hemolysis"
    assert event.possible_impact == "Configured interference"
    assert event.source_reference == "DEMO_PLACEHOLDER_SOP_001"


def test_quality_flag_without_configured_criterion_does_not_claim_impact() -> None:
    event = SpecimenQualityEvaluator().evaluate(context(hemolysis="HIGH"), [interference(criterion={"field": "hemolysis", "operator": "equals", "value": "LOW"})])[0]

    assert event.status == "NO_CONFIGURED_INTERFERENCE"
    assert event.possible_impact is None
    assert "No configured interference" in event.evidence


def test_instrument_method_and_analyte_scope_are_respected() -> None:
    event = SpecimenQualityEvaluator().evaluate(
        context(method="OTHER-METHOD"),
        [interference()],
    )[0]

    assert event.status == "NO_CONFIGURED_INTERFERENCE"
    assert event.interference_id is None


def test_instrument_flags_can_be_the_configured_evidence() -> None:
    config = interference(
        criterion={"field": "instrument_flags.sample_quality", "operator": "equals", "value": "DEMO_FLAG"}
    )

    event = SpecimenQualityEvaluator().evaluate(context(), [config])[0]

    assert event.status == "REVIEW_REQUIRED"
    assert event.evidence == "Sample quality flag: instrument_flags.sample_quality"
