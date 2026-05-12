from fastapi import FastAPI

from src.core.config import get_settings
from src.schemas.model_info import ModelInfoResponse
from src.services.model_service import get_model_info


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=(
        "Machine learning inference API for KoopCare credit scoring "
        "decision support."
    ),
    version="0.1.0",
)


@app.get("/", tags=["system"])
def read_root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "health_url": "/health",
        "model_info_url": "/model-info",
        "docs_url": "/docs",
    }


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "model_loaded": settings.resolved_model_path.exists(),
        "model_path": settings.model_path,
    }


@app.get("/model-info", response_model=ModelInfoResponse, tags=["model"])
def model_info() -> ModelInfoResponse:
    return get_model_info(settings)
