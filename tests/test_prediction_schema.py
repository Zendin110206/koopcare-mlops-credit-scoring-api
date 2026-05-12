import pytest
from pydantic import ValidationError

from src.schemas.prediction import PredictionRequest, PredictionResponse


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


def test_prediction_request_accepts_valid_payload() -> None:
    payload = PredictionRequest(**VALID_PREDICTION_PAYLOAD)

    assert payload.code_gender == "M"
    assert payload.flag_own_car == "N"
    assert payload.cnt_children == 0
    assert payload.ext_source_1 == 0.5


def test_prediction_request_strips_text_fields() -> None:
    payload = PredictionRequest(
        **{
            **VALID_PREDICTION_PAYLOAD,
            "code_gender": " M ",
            "occupation_type": " Laborers ",
        }
    )

    assert payload.code_gender == "M"
    assert payload.occupation_type == "Laborers"


def test_prediction_request_rejects_invalid_ext_source_range() -> None:
    with pytest.raises(ValidationError):
        PredictionRequest(**{**VALID_PREDICTION_PAYLOAD, "ext_source_2": 1.4})


def test_prediction_request_rejects_positive_days_birth() -> None:
    with pytest.raises(ValidationError):
        PredictionRequest(**{**VALID_PREDICTION_PAYLOAD, "days_birth": 19241})


def test_prediction_request_rejects_invalid_ownership_flag() -> None:
    with pytest.raises(ValidationError):
        PredictionRequest(**{**VALID_PREDICTION_PAYLOAD, "flag_own_car": "YES"})


def test_prediction_response_defaults_to_human_review() -> None:
    response = PredictionResponse(
        ai_recommendation="LAYAK",
        risk_level="LOW",
        prob_default=0.2911,
        threshold=0.6660796,
        confidence=0.56,
        model_name="XGBoost",
        model_version="koopcare-xgboost-v1",
        note=(
            "AI recommendation only. Final financing decision must be reviewed "
            "and approved by cooperative officers."
        ),
    )

    assert response.human_review_required is True
    assert response.final_decision is None
