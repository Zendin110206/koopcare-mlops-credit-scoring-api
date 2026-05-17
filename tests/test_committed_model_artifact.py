import pytest

from src.core.config import get_settings
from src.schemas.prediction import PredictionRequest
from src.services.model_service import (
    clear_model_artifact_cache,
    get_model_info,
    predict_credit_risk,
)


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


@pytest.mark.filterwarnings("ignore:.*serialized model.*:UserWarning")
def test_committed_model_artifact_serves_documented_prediction() -> None:
    settings = get_settings()
    clear_model_artifact_cache()

    model_info = get_model_info(settings)

    assert settings.resolved_model_path.exists()
    assert model_info.model_loaded is True
    assert model_info.artifact_status == "available"
    assert model_info.metadata_source == "artifact"
    assert model_info.features_count == 25

    prediction = predict_credit_risk(
        PredictionRequest(**VALID_PREDICTION_PAYLOAD),
        settings,
    )

    assert prediction.ai_recommendation == "LAYAK"
    assert prediction.risk_level == "MEDIUM"
    assert prediction.prob_default == 0.581492
    assert prediction.threshold == 0.66608
    assert prediction.human_review_required is True
    assert prediction.final_decision is None
