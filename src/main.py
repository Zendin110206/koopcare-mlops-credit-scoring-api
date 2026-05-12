from fastapi import FastAPI

from src.core.config import get_settings


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
