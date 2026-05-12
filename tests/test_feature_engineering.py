import math

from src.schemas.prediction import PredictionRequest
from src.services.model_service import MODEL_FEATURE_COLUMNS, build_model_feature_frame


VALID_PREDICTION_PAYLOAD = {
    "code_gender": "M",
    "name_income_type": "Working",
    "name_education_type": "Secondary / secondary special",
    "name_family_status": "Married",
    "occupation_type": "Laborers",
    "flag_own_car": "N",
    "flag_own_realty": "Y",
    "cnt_children": 0,
    "cnt_fam_members": 2.0,
    "amt_income_total": 135000.0,
    "amt_credit": 568800.0,
    "amt_annuity": 20560.5,
    "amt_goods_price": 450000.0,
    "days_birth": -19241,
    "days_employed": -2329.0,
    "days_last_phone_change": -1740.0,
    "ext_source_1": 0.5,
    "ext_source_2": 0.6,
    "ext_source_3": 0.4,
}


def test_build_model_feature_frame_returns_expected_columns() -> None:
    payload = PredictionRequest(**VALID_PREDICTION_PAYLOAD)

    feature_frame = build_model_feature_frame(payload)

    assert feature_frame.shape == (1, 25)
    assert list(feature_frame.columns) == MODEL_FEATURE_COLUMNS


def test_build_model_feature_frame_maps_raw_fields() -> None:
    payload = PredictionRequest(**VALID_PREDICTION_PAYLOAD)

    feature_row = build_model_feature_frame(payload).iloc[0]

    assert feature_row["CODE_GENDER"] == "M"
    assert feature_row["NAME_INCOME_TYPE"] == "Working"
    assert feature_row["FLAG_OWN_CAR"] == "N"
    assert feature_row["CNT_CHILDREN"] == 0
    assert feature_row["AMT_CREDIT"] == 568800.0
    assert feature_row["DAYS_EMPLOYED"] == -2329.0


def test_build_model_feature_frame_creates_derived_features() -> None:
    payload = PredictionRequest(**VALID_PREDICTION_PAYLOAD)

    feature_row = build_model_feature_frame(payload).iloc[0]

    assert math.isclose(feature_row["AGE_YEARS"], abs(-19241) / 365)
    assert feature_row["DAYS_EMPLOYED_ANOM"] == 0
    assert math.isclose(feature_row["EXT_SOURCE_MEAN"], 0.5)
    assert math.isclose(feature_row["EXT_SOURCE_MIN"], 0.4)
    assert math.isclose(feature_row["EXT_SOURCE_PROD"], 0.5 * 0.6 * 0.4)
    assert math.isclose(feature_row["DEBT_TO_INCOME"], 568800.0 / (135000.0 + 1))
    assert math.isclose(feature_row["PAYMENT_RATE"], 20560.5 / (568800.0 + 1))


def test_build_model_feature_frame_handles_days_employed_anomaly() -> None:
    payload = PredictionRequest(
        **{
            **VALID_PREDICTION_PAYLOAD,
            "days_employed": 365243.0,
        }
    )

    feature_row = build_model_feature_frame(payload).iloc[0]

    assert feature_row["DAYS_EMPLOYED_ANOM"] == 1
    assert math.isnan(feature_row["DAYS_EMPLOYED"])


def test_build_model_feature_frame_handles_missing_external_source() -> None:
    payload = PredictionRequest(
        **{
            **VALID_PREDICTION_PAYLOAD,
            "ext_source_1": None,
        }
    )

    feature_row = build_model_feature_frame(payload).iloc[0]

    assert math.isclose(feature_row["EXT_SOURCE_MEAN"], (0.6 + 0.4) / 2)
    assert math.isclose(feature_row["EXT_SOURCE_MIN"], 0.4)
    assert math.isclose(feature_row["EXT_SOURCE_PROD"], 0.6 * 0.4)
