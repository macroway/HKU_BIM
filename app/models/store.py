from pathlib import Path

from app.models.loader import load_model
from app.models.schema import InternalModel

_models: dict[str, InternalModel] = {}


def register_model(path: Path, model_id: str | None = None) -> str:
    model = load_model(path, model_id=model_id)
    _models[model.model_id] = model
    return model.model_id


def get_model(model_id: str) -> InternalModel:
    if model_id not in _models:
        raise KeyError(f"Model not found: {model_id}")
    return _models[model_id]


def clear_models() -> None:
    _models.clear()
