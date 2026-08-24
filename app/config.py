import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
SAMPLES_DIR = ROOT_DIR / "test_samples"
MAX_UPLOAD_BYTES = 50 * 1024 * 1024

# Legacy OpenAI-compatible provider
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Volcengine Ark (Doubao) — Loop3 default online provider
ARK_API_KEY = os.getenv("ARK_API_KEY", "")
ARK_BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3").rstrip("/")
ARK_MODEL = os.getenv("ARK_MODEL", "doubao-seed-2-0-lite-260428")

# offline | ark | openai | auto
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto").strip().lower()
CHECKBIM_OFFLINE = os.getenv("CHECKBIM_OFFLINE", "0") == "1"


def resolve_llm_provider() -> str | None:
    """Return active provider id, or None when offline / unavailable."""
    if CHECKBIM_OFFLINE or LLM_PROVIDER == "offline":
        return None
    if LLM_PROVIDER == "ark":
        return "ark" if ARK_API_KEY else None
    if LLM_PROVIDER == "openai":
        return "openai" if OPENAI_API_KEY else None
    # auto: prefer Ark Doubao, then OpenAI
    if ARK_API_KEY:
        return "ark"
    if OPENAI_API_KEY:
        return "openai"
    return None


def llm_available() -> bool:
    return resolve_llm_provider() is not None


def planner_label(provider: str | None) -> str:
    if provider == "ark":
        return "doubao"
    if provider == "openai":
        return "llm"
    return "rules"
