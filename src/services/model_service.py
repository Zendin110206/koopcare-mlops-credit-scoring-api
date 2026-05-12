from dataclasses import dataclass
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.core.config import Settings
from src.schemas.model_info import ModelInfoResponse
from src.schemas.prediction import PredictionRequest, PredictionResponse


MODEL_FEATURE_COLUMNS = [
    "CODE_GENDER",
    "NAME_INCOME_TYPE",
    "NAME_EDUCATION_TYPE",
    "NAME_FAMILY_STATUS",
    "OCCUPATION_TYPE",
    "FLAG_OWN_CAR",
    "FLAG_OWN_REALTY",
    "CNT_CHILDREN",
    "CNT_FAM_MEMBERS",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",
    "DAYS_EMPLOYED",
    "DAYS_LAST_PHONE_CHANGE",
    "AGE_YEARS",
    "DAYS_EMPLOYED_ANOM",
    "EXT_SOURCE_1",
    "EXT_SOURCE_2",
    "EXT_SOURCE_3",
    "EXT_SOURCE_MEAN",
    "EXT_SOURCE_MIN",
    "EXT_SOURCE_PROD",
    "DEBT_TO_INCOME",
    "PAYMENT_RATE",
]

REQUIRED_ARTIFACT_KEYS = {"features", "model", "preprocessor", "threshold"}
DECISION_SUPPORT_NOTE = (
    "AI recommendation only. Final financing decision must be reviewed and "
    "approved by cooperative officers."
)


class ModelArtifactError(RuntimeError):
    """Base exception for model artifact loading and validation failures."""


class ModelArtifactMissingError(ModelArtifactError):
    """Raised when the configured model artifact path does not exist."""


class ModelArtifactInvalidError(ModelArtifactError):
    """Raised when the model artifact exists but cannot be used safely."""


class ModelPredictionError(RuntimeError):
    """Raised when a loaded model cannot generate a valid prediction."""


@dataclass(frozen=True)
class LoadedModelArtifact:
    model: Any
    preprocessor: Any
    features: list[str]
    threshold: float
    model_name: str
    artifact_keys: list[str]

    @property
    def features_count(self) -> int:
        return len(self.features)


def get_model_info(settings: Settings) -> ModelInfoResponse:
    if not settings.resolved_model_path.exists():
        return ModelInfoResponse(
            model_loaded=False,
            model_name=settings.model_name,
            model_version=settings.model_version,
            model_path=settings.model_path,
            threshold=settings.model_threshold,
            features_count=settings.model_features_count,
            artifact_status="missing",
            artifact_keys=[],
            artifact_error=None,
            metadata_source="configuration",
            note=(
                "Model artifact is not available yet. Copy best_model.pkl into "
                "models/ before enabling prediction."
            ),
        )

    try:
        loaded_artifact = load_model_artifact(settings)
    except Exception as exc:
        return ModelInfoResponse(
            model_loaded=False,
            model_name=settings.model_name,
            model_version=settings.model_version,
            model_path=settings.model_path,
            threshold=settings.model_threshold,
            features_count=settings.model_features_count,
            artifact_status="invalid",
            artifact_keys=[],
            artifact_error=str(exc),
            metadata_source="configuration",
            note=(
                "Model artifact exists but could not be validated. Use a trusted "
                "KoopCare best_model.pkl artifact before enabling prediction."
            ),
        )

    return ModelInfoResponse(
        model_loaded=True,
        model_name=loaded_artifact.model_name,
        model_version=settings.model_version,
        model_path=settings.model_path,
        threshold=loaded_artifact.threshold,
        features_count=loaded_artifact.features_count,
        artifact_status="available",
        artifact_keys=loaded_artifact.artifact_keys,
        artifact_error=None,
        metadata_source="artifact",
        note="Model artifact is available and runtime components were validated.",
    )


def load_model_artifact(settings: Settings) -> LoadedModelArtifact:
    if not settings.resolved_model_path.exists():
        raise ModelArtifactMissingError(
            f"Model artifact not found at {settings.model_path}."
        )

    try:
        artifact = joblib.load(settings.resolved_model_path)
    except Exception as exc:
        raise ModelArtifactInvalidError(
            f"Unable to load model artifact at {settings.model_path}: {exc}"
        ) from exc

    return _validate_model_artifact(artifact, settings)


def load_model_artifact_metadata(settings: Settings) -> dict[str, Any]:
    loaded_artifact = load_model_artifact(settings)

    return {
        "model_name": loaded_artifact.model_name,
        "threshold": loaded_artifact.threshold,
        "features_count": loaded_artifact.features_count,
        "artifact_keys": loaded_artifact.artifact_keys,
    }


def predict_credit_risk(
    payload: PredictionRequest,
    settings: Settings,
) -> PredictionResponse:
    loaded_artifact = load_model_artifact(settings)
    feature_frame = build_model_feature_frame(payload)
    model_input = feature_frame[loaded_artifact.features]

    try:
        transformed_features = loaded_artifact.preprocessor.transform(model_input)
        probabilities = loaded_artifact.model.predict_proba(transformed_features)
    except Exception as exc:
        raise ModelPredictionError(f"Unable to generate prediction: {exc}") from exc

    prob_default = _extract_default_probability(probabilities)

    return build_prediction_response(
        prob_default=prob_default,
        threshold=loaded_artifact.threshold,
        model_name=loaded_artifact.model_name,
        model_version=settings.model_version,
    )


def _validate_model_artifact(
    artifact: Any,
    settings: Settings,
) -> LoadedModelArtifact:
    if not isinstance(artifact, dict):
        raise ModelArtifactInvalidError("Model artifact must be a dictionary.")

    missing_keys = REQUIRED_ARTIFACT_KEYS.difference(artifact)
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ModelArtifactInvalidError(
            f"Model artifact is missing required keys: {missing}."
        )

    features = artifact["features"]
    if not isinstance(features, (list, tuple)):
        raise ModelArtifactInvalidError(
            "Model artifact 'features' value must be a list or tuple."
        )

    feature_names = list(features)
    if not all(isinstance(feature, str) for feature in feature_names):
        raise ModelArtifactInvalidError(
            "Model artifact 'features' value must contain only strings."
        )

    if feature_names != MODEL_FEATURE_COLUMNS:
        raise ModelArtifactInvalidError(
            "Model artifact features do not match expected KoopCare feature columns."
        )

    model = artifact["model"]
    if not hasattr(model, "predict_proba"):
        raise ModelArtifactInvalidError(
            "Model artifact 'model' must provide a predict_proba method."
        )

    preprocessor = artifact["preprocessor"]
    if not hasattr(preprocessor, "transform"):
        raise ModelArtifactInvalidError(
            "Model artifact 'preprocessor' must provide a transform method."
        )

    try:
        threshold = float(artifact["threshold"])
        _validate_probability_value(threshold, "threshold")
    except (TypeError, ValueError) as exc:
        raise ModelArtifactInvalidError(str(exc)) from exc

    return LoadedModelArtifact(
        model=model,
        preprocessor=preprocessor,
        features=feature_names,
        threshold=threshold,
        model_name=str(artifact.get("model_name", settings.model_name)),
        artifact_keys=sorted(artifact.keys()),
    )


def build_model_feature_frame(payload: PredictionRequest) -> pd.DataFrame:
    raw_features = {
        "CODE_GENDER": payload.code_gender,
        "NAME_INCOME_TYPE": payload.name_income_type,
        "NAME_EDUCATION_TYPE": payload.name_education_type,
        "NAME_FAMILY_STATUS": payload.name_family_status,
        "OCCUPATION_TYPE": payload.occupation_type,
        "FLAG_OWN_CAR": payload.flag_own_car,
        "FLAG_OWN_REALTY": payload.flag_own_realty,
        "CNT_CHILDREN": payload.cnt_children,
        "CNT_FAM_MEMBERS": payload.cnt_fam_members,
        "AMT_INCOME_TOTAL": payload.amt_income_total,
        "AMT_CREDIT": payload.amt_credit,
        "AMT_ANNUITY": payload.amt_annuity,
        "AMT_GOODS_PRICE": payload.amt_goods_price,
        "DAYS_BIRTH": payload.days_birth,
        "DAYS_EMPLOYED": payload.days_employed,
        "DAYS_LAST_PHONE_CHANGE": payload.days_last_phone_change,
        "EXT_SOURCE_1": payload.ext_source_1,
        "EXT_SOURCE_2": payload.ext_source_2,
        "EXT_SOURCE_3": payload.ext_source_3,
    }

    feature_frame = pd.DataFrame([raw_features])

    feature_frame["DAYS_EMPLOYED_ANOM"] = (
        feature_frame["DAYS_EMPLOYED"] == 365243
    ).astype(int)
    feature_frame["DAYS_EMPLOYED"] = feature_frame["DAYS_EMPLOYED"].replace(
        365243,
        np.nan,
    )

    feature_frame["AGE_YEARS"] = feature_frame["DAYS_BIRTH"].abs() / 365
    feature_frame["DEBT_TO_INCOME"] = feature_frame["AMT_CREDIT"] / (
        feature_frame["AMT_INCOME_TOTAL"] + 1
    )
    feature_frame["PAYMENT_RATE"] = feature_frame["AMT_ANNUITY"] / (
        feature_frame["AMT_CREDIT"] + 1
    )

    ext_source_columns = ["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"]
    feature_frame["EXT_SOURCE_MEAN"] = feature_frame[ext_source_columns].mean(axis=1)
    feature_frame["EXT_SOURCE_MIN"] = feature_frame[ext_source_columns].min(axis=1)
    feature_frame["EXT_SOURCE_PROD"] = feature_frame[ext_source_columns].prod(axis=1)

    return feature_frame[MODEL_FEATURE_COLUMNS]


def get_ai_recommendation(prob_default: float, threshold: float) -> str:
    _validate_probability_value(prob_default, "prob_default")
    _validate_probability_value(threshold, "threshold")

    return "TIDAK_LAYAK" if prob_default >= threshold else "LAYAK"


def get_risk_level(prob_default: float, threshold: float) -> str:
    _validate_probability_value(prob_default, "prob_default")
    _validate_probability_value(threshold, "threshold")

    if prob_default >= threshold:
        return "HIGH"
    if prob_default >= threshold * 0.75:
        return "MEDIUM"
    return "LOW"


def calculate_confidence(prob_default: float, threshold: float) -> float:
    _validate_probability_value(prob_default, "prob_default")
    _validate_probability_value(threshold, "threshold")

    distance = abs(prob_default - threshold)
    normalizer = max(threshold, 1 - threshold)

    if normalizer == 0:
        return 1.0

    return min(1.0, distance / normalizer)


def build_prediction_response(
    prob_default: float,
    threshold: float,
    model_name: str,
    model_version: str,
) -> PredictionResponse:
    return PredictionResponse(
        ai_recommendation=get_ai_recommendation(prob_default, threshold),
        risk_level=get_risk_level(prob_default, threshold),
        prob_default=round(prob_default, 6),
        threshold=round(threshold, 6),
        confidence=round(calculate_confidence(prob_default, threshold), 6),
        model_name=model_name,
        model_version=model_version,
        human_review_required=True,
        final_decision=None,
        note=DECISION_SUPPORT_NOTE,
    )


def _extract_default_probability(probabilities: Any) -> float:
    probability_array = np.asarray(probabilities)

    if (
        probability_array.ndim != 2
        or probability_array.shape[0] != 1
        or probability_array.shape[1] < 2
    ):
        raise ModelPredictionError(
            "predict_proba must return one row with probability columns for "
            "class 0 and class 1."
        )

    try:
        prob_default = float(probability_array[0, 1])
        _validate_probability_value(prob_default, "prob_default")
    except (TypeError, ValueError) as exc:
        raise ModelPredictionError(str(exc)) from exc

    return prob_default


def _validate_probability_value(value: float, name: str) -> None:
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1.")
