from fastapi import FastAPI, HTTPException, status

from src.core.config import get_settings
from src.schemas.model_info import ModelInfoResponse
from src.schemas.prediction import PredictionRequest, PredictionResponse
from src.services.model_service import (
    ModelArtifactInvalidError,
    ModelArtifactMissingError,
    ModelPredictionError,
    get_model_info,
    predict_credit_risk,
)


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
        "predict_url": "/predict",
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


@app.post("/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(payload: PredictionRequest) -> PredictionResponse:
    try:
        return predict_credit_risk(payload, settings)
    except ModelArtifactMissingError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_prediction_error_detail("model_artifact_missing", str(exc)),
        ) from exc
    except ModelArtifactInvalidError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_prediction_error_detail("model_artifact_invalid", str(exc)),
        ) from exc
    except ModelPredictionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_prediction_error_detail("prediction_failed", str(exc)),
        ) from exc


def _prediction_error_detail(code: str, message: str) -> dict[str, str]:
    return {
        "error": code,
        "message": message,
    }
