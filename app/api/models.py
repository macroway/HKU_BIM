import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.api.schemas import ModelRegisterResponse, SampleInfo
from app.config import MAX_UPLOAD_BYTES, SAMPLES_DIR, UPLOAD_DIR
from app.models.store import register_model

router = APIRouter(prefix="/api/models", tags=["models"])

ALLOWED_SUFFIXES = {".json", ".ifc", ".ifczip"}


def _list_sample_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(SAMPLES_DIR.glob("*.json")):
        if not path.name.endswith(".expected.json"):
            files.append(path)
    demo_dir = SAMPLES_DIR / "demo"
    if demo_dir.exists():
        files.extend(sorted(demo_dir.glob("*.ifc")))
    return files


@router.get("/samples", response_model=list[SampleInfo])
def list_samples():
    items: list[SampleInfo] = []
    for path in _list_sample_files():
        sample_id = path.stem if path.parent.name != "demo" else f"demo/{path.stem}"
        items.append(
            SampleInfo(
                id=sample_id,
                name=path.name,
                path=str(path.relative_to(SAMPLES_DIR.parent)),
                format=path.suffix.lstrip(".").lower(),
            )
        )
    return items


def _resolve_sample_path(sample_id: str) -> Path:
    if sample_id.startswith("demo/"):
        path = SAMPLES_DIR / "demo" / f"{sample_id.removeprefix('demo/')}.ifc"
    else:
        path = SAMPLES_DIR / f"{sample_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Sample not found: {sample_id}")
    return path


@router.post("/select/{sample_id:path}", response_model=ModelRegisterResponse)
def select_sample(sample_id: str):
    """sample_id may contain slashes (e.g. demo/demo-collision)."""
    path = _resolve_sample_path(sample_id)
    try:
        model_id = register_model(path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to load sample: {exc}") from exc
    return ModelRegisterResponse(
        model_id=model_id,
        source="sample",
        format=path.suffix.lstrip(".").lower(),
    )


@router.post("/upload", response_model=ModelRegisterResponse)
async def upload_model(file: UploadFile):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    model_id = f"upload-{uuid.uuid4().hex[:8]}"
    dest = UPLOAD_DIR / f"{model_id}{suffix}"

    size = 0
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                dest.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File too large")
            out.write(chunk)

    try:
        register_model(dest, model_id=model_id)
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Failed to load model: {exc}") from exc

    return ModelRegisterResponse(
        model_id=model_id,
        source="upload",
        format=suffix.lstrip("."),
    )
