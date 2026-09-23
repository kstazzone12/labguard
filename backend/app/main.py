from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.validation_engine import ValidationEngine, ValidationInput

app = FastAPI(
    title="LABGUARD",
    description=(
        "Prototipo de apoyo a la validacion profesional de resultados "
        "de laboratorio con datos sinteticos."
    ),
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "synthetic-data-only"}


@app.post("/validation/evaluate", tags=["validation"])
def evaluate_validation(payload: ValidationInput) -> dict:
    return ValidationEngine().evaluate(payload).model_dump(mode="json")
