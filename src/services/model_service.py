from src.core.config import Settings
from src.schemas.model_info import ModelInfoResponse


def get_model_info(settings: Settings) -> ModelInfoResponse:
    model_exists = settings.resolved_model_path.exists()

    artifact_status = "available" if model_exists else "missing"
    note = (
        "Model artifact is available locally."
        if model_exists
        else (
            "Model artifact is not available yet. Copy best_model.pkl into "
            "models/ before enabling prediction."
        )
    )

    return ModelInfoResponse(
        model_loaded=model_exists,
        model_name=settings.model_name,
        model_version=settings.model_version,
        model_path=settings.model_path,
        threshold=settings.model_threshold,
        features_count=settings.model_features_count,
        artifact_status=artifact_status,
        metadata_source="configuration",
        note=note,
    )
