import json

from app.imports.models import ImportStatus, LoincTerm
from app.imports.service import preview_csv, preview_json, resolve_unit, search_loinc
from app.main import app
from fastapi.testclient import TestClient


VALID_CSV = """patient_id,sample_id,date,time,analyte,value,unit,specimen,method,instrument,flag
pseudo-1,sample-1,2026-01-15,08:30,glucose,5.2,mmol/L,serum,method-1,instrument-1,
"""
client = TestClient(app)


def test_valid_csv_preview_is_importable() -> None:
    preview = preview_csv(VALID_CSV, {"mmol/L"})
    assert preview.can_import is True
    assert preview.records[0].status == ImportStatus.VALID


def test_excel_style_csv_with_bom_semicolon_and_decimal_comma_is_importable() -> None:
    content = "\ufeffpatient_id;sample_id;date;time;analyte;value;unit;specimen;method;instrument;flag\n"
    content += "pseudo-1;sample-1;2026-01-15;08:30;glucose;5,2;g/L;serum;method-1;instrument-1;OK\n"
    preview = preview_csv(content)
    assert preview.can_import is True
    assert preview.records[0].data is not None
    assert preview.records[0].data.value == 5.2


def test_corrupt_csv_and_non_numeric_value_are_blocked() -> None:
    assert preview_csv("not,a,valid,header\n1,2,3,4").can_import is False
    preview = preview_csv(VALID_CSV.replace("5.2", "not-a-number"))
    assert preview.records[0].issues[0].code == "INVALID_NUMERIC_VALUE"


def test_invalid_date_and_unknown_unit_are_reported() -> None:
    preview = preview_csv(VALID_CSV.replace("2026-01-15", "15/01/2026"), {"mmol/L"})
    assert any(issue.code == "INVALID_DATE" for issue in preview.records[0].issues)
    preview = preview_csv(VALID_CSV.replace("mmol/L", "unknown-unit"), {"mmol/L"})
    assert preview.records[0].status == ImportStatus.WARNING
    assert preview.records[0].issues[0].code == "UNKNOWN_UNIT"


def test_duplicate_records_are_blocked() -> None:
    preview = preview_csv(VALID_CSV + VALID_CSV.splitlines()[1] + "\n")
    assert preview.can_import is False
    assert preview.records[1].issues[0].code == "DUPLICATE_RECORD"


def test_json_preview_and_unit_conversion_are_explicit() -> None:
    payload = json.dumps([{
        "patient_id": "pseudo-1", "sample_id": "sample-1", "date": "2026-01-15", "time": "08:30",
        "analyte": "glucose", "value": 5.2, "unit": "mmol/L", "specimen": "serum",
        "method": "method-1", "instrument": "instrument-1", "flag": "",
    }])
    assert preview_json(payload).can_import is True
    assert resolve_unit("unknown", {}).issue_code == "UNIT_CONVERSION_UNAVAILABLE"
    assert resolve_unit("mmol/L", {"mmol/L": {"normalized_unit": "mmol/L", "conversion_factor": 1}}).conversion_factor == 1


def test_loinc_not_found_and_ambiguous_mapping() -> None:
    terms = [
        LoincTerm(loinc_code="1000-0", component="Glucose", system="Ser/Plas", property="SCnc", scale="Qn", long_common_name="Glucose"),
        LoincTerm(loinc_code="1001-9", component="Glucose", system="Urine", property="SCnc", scale="Qn", long_common_name="Glucose"),
    ]
    assert search_loinc(terms, "missing").issue_code == "LOINC_MAPPING_NOT_FOUND"
    assert search_loinc(terms, "glucose").issue_code == "MAPPING_REVIEW_REQUIRED"


def test_professional_record_runs_all_validation_stages() -> None:
    response = client.post("/validation/evaluate-record", json={
        "id": "local-result-1", "patient_id": "pseudo-1", "sample_id": "sample-1",
        "date": "2026-01-15", "time": "08:30", "analyte": "glucose", "value": 5.2,
        "unit": "mmol/L", "specimen": "serum", "method": "method-1", "instrument": "instrument-1", "flag": "",
    })
    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["sample_id"] == "sample-1"
    assert payload["evaluated"] == ["RESULT", "QC", "SPECIMEN_QUALITY", "INTERFERENCE", "DELTA_CHECK", "CONSISTENCY", "RULE_ENGINE", "VALIDATION_PROFILE", "PROFESSIONAL_REVIEW"]