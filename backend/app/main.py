from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.imports.models import ImportPreviewRequest, ProfessionalRecord
from app.imports.service import preview_csv, preview_json, to_validation_input
from app.knowledge import knowledge_snapshot, load_knowledge_status
from app.validation_engine import ValidationEngine, ValidationInput

app = FastAPI(
    title="LABGUARD",
    description="Validación profesional local de resultados de laboratorio.",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

KNOWLEDGE_ROOT = Path(__file__).parents[2] / "knowledge"


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "local-data-only", "external_credentials": "not_required"}


@app.get("/knowledge/status", tags=["knowledge"])
def knowledge_status() -> dict:
    result = load_knowledge_status(KNOWLEDGE_ROOT)
    return {
        "valid": result.valid,
        "snapshot": knowledge_snapshot(KNOWLEDGE_ROOT, settings.app_version),
        "datasets": result.datasets,
        "issues": [issue.__dict__ for issue in result.issues],
    }


@app.post("/imports/preview", tags=["imports"])
def preview_import(payload: ImportPreviewRequest) -> dict:
    if payload.source_format.lower() == "csv":
        return preview_csv(payload.content).model_dump(mode="json")
    if payload.source_format.lower() == "json":
        return preview_json(payload.content).model_dump(mode="json")
    return {"source_format": payload.source_format, "total_rows": 0, "records": [], "can_import": False, "error": "UNSUPPORTED_FORMAT"}


@app.post("/validation/evaluate", tags=["validation"])
def evaluate_validation(payload: ValidationInput) -> dict:
    return ValidationEngine().evaluate(payload).model_dump(mode="json")


@app.post("/validation/evaluate-record", tags=["validation"])
def evaluate_professional_record(payload: ProfessionalRecord) -> dict:
    """Run every validation phase for one locally supplied professional record."""
    return ValidationEngine().evaluate(to_validation_input(payload)).model_dump(mode="json")
