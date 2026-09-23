import hashlib
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

REQUIRED_METADATA = ("source_name", "source_url", "version", "release_date", "license", "date_accessed", "dataset_name", "local_file")
DATASET_NAMES = ("LOINC", "UCUM", "reference_intervals", "qc", "interferences", "rules")


@dataclass(frozen=True)
class KnowledgeIssue:
    code: str
    message: str
    dataset_name: str | None = None


@dataclass(frozen=True)
class KnowledgeValidationResult:
    datasets: list[dict[str, Any]]
    issues: list[KnowledgeIssue]

    @property
    def valid(self) -> bool:
        return not self.issues


def _issue(code: str, message: str, dataset_name: str | None = None) -> KnowledgeIssue:
    return KnowledgeIssue(code, message, dataset_name)


def _check_date(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def validate_dataset_manifest(manifest: dict[str, Any], root: Path) -> list[KnowledgeIssue]:
    name = manifest.get("dataset_name")
    issues: list[KnowledgeIssue] = []
    for field in REQUIRED_METADATA:
        if not manifest.get(field):
            issues.append(_issue("KNOWLEDGE_METADATA_MISSING", f"Falta {field}.", name))
    if manifest.get("release_date") and not _check_date(manifest["release_date"]):
        issues.append(_issue("INVALID_RELEASE_DATE", "release_date no es válida.", name))
    if manifest.get("date_accessed") and not _check_date(manifest["date_accessed"]):
        issues.append(_issue("INVALID_ACCESS_DATE", "date_accessed no es válida.", name))
    local_file = manifest.get("local_file")
    if local_file:
        target = root / local_file
        if not target.is_file():
            issues.append(_issue("KNOWLEDGE_MISSING", f"No existe local_file: {local_file}.", name))
        expected_hash = manifest.get("hash") or manifest.get("local_dataset_hash")
        if expected_hash and target.is_file():
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            if digest != expected_hash:
                issues.append(_issue("KNOWLEDGE_HASH_MISMATCH", f"Hash incorrecto para {local_file}.", name))
    if name == "LOINC" and manifest.get("version") in {None, "", "UNPOPULATED", "NOT_INSTALLED"}:
        issues.append(_issue("LOINC_VERSION_INVALID", "El dataset LOINC local no tiene una release instalada.", name))
    return issues


def validate_rule_definition(rule: dict[str, Any]) -> list[KnowledgeIssue]:
    issues: list[KnowledgeIssue] = []
    for field in ("rule_id", "version", "name", "description", "source", "source_url", "source_version", "effective_date", "review_date", "applicability", "status"):
        if not rule.get(field):
            issues.append(_issue("RULE_METADATA_MISSING", f"Falta {field}.", rule.get("rule_id")))
    if rule.get("status") == "RETIRED":
        issues.append(_issue("RULE_RETIRED", "La regla está retirada y no puede ejecutarse.", rule.get("rule_id")))
    if not rule.get("source") or not rule.get("source_url"):
        issues.append(_issue("RULE_SOURCE_MISSING", "La regla no tiene evidencia de fuente.", rule.get("rule_id")))
    return issues


def validate_reference_interval(interval: dict[str, Any]) -> list[KnowledgeIssue]:
    status = interval.get("verification_status")
    if status != "VERIFIED":
        return [_issue("REFERENCE_INTERVAL_NOT_VERIFIED", "El intervalo no está verificado y no puede fundamentar validación automática.", interval.get("analyte"))]
    return []


def load_knowledge_status(root: Path) -> KnowledgeValidationResult:
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        return KnowledgeValidationResult([], [_issue("KNOWLEDGE_MISSING", "No existe knowledge/manifest.json.")])
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return KnowledgeValidationResult([], [_issue("KNOWLEDGE_DATASET_CORRUPT", "El manifiesto local no es JSON válido.")])
    datasets = payload.get("datasets") if isinstance(payload, dict) else None
    if not isinstance(datasets, list):
        return KnowledgeValidationResult([], [_issue("KNOWLEDGE_DATASET_CORRUPT", "El manifiesto debe contener datasets.")])
    issues: list[KnowledgeIssue] = []
    found = {dataset.get("dataset_name") for dataset in datasets if isinstance(dataset, dict)}
    for required_name in DATASET_NAMES:
        if required_name.casefold() not in {str(value).casefold() for value in found}:
            issues.append(_issue("KNOWLEDGE_MISSING", f"Falta el conjunto {required_name}."))
    for dataset in datasets:
        if isinstance(dataset, dict):
            issues.extend(validate_dataset_manifest(dataset, root))
    return KnowledgeValidationResult(datasets=datasets, issues=issues)


def knowledge_snapshot(root: Path, engine_version: str) -> dict[str, str]:
    result = load_knowledge_status(root)
    versions = {str(dataset.get("dataset_name")): str(dataset.get("version") or "NOT_INSTALLED") for dataset in result.datasets}
    return {
        "loinc_version": versions.get("LOINC", "NOT_INSTALLED"),
        "unit_dataset_version": versions.get("UCUM", "NOT_INSTALLED"),
        "reference_interval_version": versions.get("reference_intervals", "NOT_INSTALLED"),
        "qc_rules_version": versions.get("qc", "NOT_INSTALLED"),
        "interference_rules_version": versions.get("interferences", "NOT_INSTALLED"),
        "labguard_engine_version": engine_version,
    }
