import json
from pathlib import Path
from typing import Any

import yaml

from app.engine.models import RuleDefinition


class RuleLoader:
    """Carga reglas declarativas YAML o JSON y las valida con Pydantic."""

    SUPPORTED_SUFFIXES = {".yaml", ".yml", ".json"}

    def load_file(self, path: str | Path) -> RuleDefinition:
        rule_path = Path(path)
        if rule_path.suffix.lower() not in self.SUPPORTED_SUFFIXES:
            raise ValueError(f"Unsupported rule format: {rule_path.suffix}")
        data = self._read_document(rule_path)
        return RuleDefinition.model_validate(data)

    def load_directory(self, directory: str | Path) -> list[RuleDefinition]:
        root = Path(directory)
        if not root.is_dir():
            raise FileNotFoundError(root)
        rules = [
            self.load_file(path)
            for path in sorted(root.rglob("*"))
            if path.is_file() and path.suffix.lower() in self.SUPPORTED_SUFFIXES
        ]
        return rules

    def _read_document(self, path: Path) -> dict[str, Any]:
        with path.open(encoding="utf-8") as document:
            data = yaml.safe_load(document) if path.suffix.lower() in {".yaml", ".yml"} else json.load(document)
        if not isinstance(data, dict):
            raise ValueError(f"Rule document must contain an object: {path}")
        return data
