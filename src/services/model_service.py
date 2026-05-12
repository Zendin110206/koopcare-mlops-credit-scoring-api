from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.core.config import Settings
from src.schemas.model_info import ModelInfoResponse
from src.schemas.prediction import PredictionRequest


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
        artifact_metadata = load_model_artifact_metadata(settings)
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
        model_name=artifact_metadata["model_name"],
        model_version=settings.model_version,
        model_path=settings.model_path,
        threshold=artifact_metadata["threshold"],
        features_count=artifact_metadata["features_count"],
        artifact_status="available",
        artifact_keys=artifact_metadata["artifact_keys"],
        artifact_error=None,
        metadata_source="artifact",
        note="Model artifact is available and metadata was read from best_model.pkl.",
    )


def load_model_artifact_metadata(settings: Settings) -> dict[str, Any]:
    artifact = joblib.load(settings.resolved_model_path)

    if not isinstance(artifact, dict):
        raise TypeError("Model artifact must be a dictionary.")

    missing_keys = REQUIRED_ARTIFACT_KEYS.difference(artifact)
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"Model artifact is missing required keys: {missing}.")

    features = artifact["features"]
    if not isinstance(features, (list, tuple)):
        raise TypeError("Model artifact 'features' value must be a list or tuple.")

    threshold = float(artifact["threshold"])
    model_name = str(artifact.get("model_name", settings.model_name))

    return {
        "model_name": model_name,
        "threshold": threshold,
        "features_count": len(features),
        "artifact_keys": sorted(artifact.keys()),
    }


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
