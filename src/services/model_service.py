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
