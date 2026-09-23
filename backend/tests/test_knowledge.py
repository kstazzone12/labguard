import hashlib
import json

from app.knowledge.validator import (
    load_knowledge_status,
    validate_dataset_manifest,
    validate_reference_interval,
    validate_rule_definition,
)


def base_manifest(tmp_path):
    dataset = tmp_path / "data.json"
    dataset.write_text("[]", encoding="utf-8")
    return {
        "dataset_name": "local",
        "source_name": "Official source",
        "source_url": "https://example.invalid/source",
        "version": "1.0.0",
        "release_date": "2026-01-01",
        "license": "Documented license",
        "date_accessed": "2026-01-02",
        "local_file": "data.json",
    }


def test_source_and_version_are_required(tmp_path):
    manifest = base_manifest(tmp_path)
    manifest.pop("source_name")
    manifest.pop("version")
    codes = {issue.code for issue in validate_dataset_manifest(manifest, tmp_path)}
    assert "KNOWLEDGE_METADATA_MISSING" in codes


def test_hash_mismatch_is_detected(tmp_path):
    manifest = base_manifest(tmp_path)
    manifest["hash"] = "wrong"
    assert any(issue.code == "KNOWLEDGE_HASH_MISMATCH" for issue in validate_dataset_manifest(manifest, tmp_path))


def test_corrupt_manifest_is_detected(tmp_path):
    (tmp_path / "manifest.json").write_text("{broken", encoding="utf-8")
    result = load_knowledge_status(tmp_path)
    assert result.issues[0].code == "KNOWLEDGE_DATASET_CORRUPT"


def test_missing_knowledge_dataset_is_detected(tmp_path):
    (tmp_path / "manifest.json").write_text(json.dumps({"datasets": []}), encoding="utf-8")
    result = load_knowledge_status(tmp_path)
    assert any(issue.code == "KNOWLEDGE_MISSING" for issue in result.issues)


def test_wrong_loinc_version_is_detected(tmp_path):
    manifest = base_manifest(tmp_path)
    manifest["dataset_name"] = "LOINC"
    manifest["version"] = "NOT_INSTALLED"
    assert any(issue.code == "LOINC_VERSION_INVALID" for issue in validate_dataset_manifest(manifest, tmp_path))


def test_rule_without_source_and_retired_rule_are_blocked():
    rule = {"rule_id": "rule-1", "version": "1.0", "name": "Rule", "description": "Description", "status": "RETIRED"}
    codes = {issue.code for issue in validate_rule_definition(rule)}
    assert "RULE_SOURCE_MISSING" in codes
    assert "RULE_RETIRED" in codes


def test_unverified_interval_cannot_be_used():
    interval = {"analyte": "glucose", "verification_status": "REVIEW_REQUIRED"}
    assert validate_reference_interval(interval)[0].code == "REFERENCE_INTERVAL_NOT_VERIFIED"


def test_hash_is_valid_when_matching(tmp_path):
    manifest = base_manifest(tmp_path)
    manifest["hash"] = hashlib.sha256(b"[]").hexdigest()
    assert validate_dataset_manifest(manifest, tmp_path) == []
