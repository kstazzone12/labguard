import json
from pathlib import Path
from typing import Any


DATASET_PATH = Path(__file__).parents[3] / "data" / "synthetic" / "minimal_case.json"


def load_minimal_case() -> dict[str, Any]:
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))
