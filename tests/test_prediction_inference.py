from pathlib import Path

import joblib
import pytest

from src.core.config import Settings
from src.schemas.prediction import PredictionRequest
from src.services.model_service import (
    MODEL_FEATURE_COLUMNS,
    ModelPredictionError,
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


class FixedProbabilityModel:
    def __init__(self, probabilities):
        self.probabilities = probabilities

    def predict_proba(self, transformed_features):
        return self.probabilities


class PassThroughPreprocessor:
    def transform(self, feature_frame):
        if list(feature_frame.columns) != MODEL_FEATURE_COLUMNS:
            raise ValueError("Unexpected feature order.")
        return feature_frame


class FailingPreprocessor:
    def transform(self, feature_frame):
        raise RuntimeError("transform failed")


def make_settings(model_path: Path) -> Settings:
    return Settings(
        app_name="KoopCare ML Inference API",
        app_env="development",
        app_debug=True,
        model_path=str(model_path),
        model_name="XGBoost",
        model_version="koopcare-xgboost-v1",
        model_threshold=0.6660796,
        model_features_count=25,
        api_host="127.0.0.1",
        api_port=8000,
    )


def make_artifact(probabilities, threshold: float = 0.5):
    return {
        "features": MODEL_FEATURE_COLUMNS.copy(),
        "model": FixedProbabilityModel(probabilities),
        "model_name": "XGBoost",
        "preprocessor": PassThroughPreprocessor(),
        "threshold": threshold,
    }


def test_predict_credit_risk_returns_layak_response(tmp_path: Path) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    joblib.dump(make_artifact([[0.75, 0.25]], threshold=0.5), model_path)
    payload = PredictionRequest(**VALID_PREDICTION_PAYLOAD)

    prediction = predict_credit_risk(payload, settings)

    assert prediction.ai_recommendation == "LAYAK"
    assert prediction.risk_level == "LOW"
    assert prediction.prob_default == 0.25
    assert prediction.threshold == 0.5
    assert prediction.confidence == 0.5
    assert prediction.model_name == "XGBoost"
    assert prediction.model_version == "koopcare-xgboost-v1"
    assert prediction.human_review_required is True
    assert prediction.final_decision is None


def test_predict_credit_risk_returns_tidak_layak_response(tmp_path: Path) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    joblib.dump(make_artifact([[0.2, 0.8]], threshold=0.5), model_path)
    payload = PredictionRequest(**VALID_PREDICTION_PAYLOAD)

    prediction = predict_credit_risk(payload, settings)

    assert prediction.ai_recommendation == "TIDAK_LAYAK"
    assert prediction.risk_level == "HIGH"
    assert prediction.prob_default == 0.8
    assert prediction.threshold == 0.5
    assert prediction.confidence == 0.6


def test_predict_credit_risk_rejects_invalid_probability_shape(
    tmp_path: Path,
) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    joblib.dump(make_artifact([[1.0]], threshold=0.5), model_path)
    payload = PredictionRequest(**VALID_PREDICTION_PAYLOAD)

    with pytest.raises(ModelPredictionError, match="class 0 and class 1"):
        predict_credit_risk(payload, settings)


def test_predict_credit_risk_rejects_multiclass_probability_shape(
    tmp_path: Path,
) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    joblib.dump(make_artifact([[0.2, 0.3, 0.5]], threshold=0.5), model_path)
    payload = PredictionRequest(**VALID_PREDICTION_PAYLOAD)

    with pytest.raises(ModelPredictionError, match="exactly two"):
        predict_credit_risk(payload, settings)


def test_predict_credit_risk_rejects_invalid_default_probability(
    tmp_path: Path,
) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    joblib.dump(make_artifact([[0.2, 1.2]], threshold=0.5), model_path)
    payload = PredictionRequest(**VALID_PREDICTION_PAYLOAD)

    with pytest.raises(ModelPredictionError, match="prob_default"):
        predict_credit_risk(payload, settings)


def test_predict_credit_risk_wraps_transform_errors(tmp_path: Path) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    artifact = make_artifact([[0.75, 0.25]], threshold=0.5)
    artifact["preprocessor"] = FailingPreprocessor()
    joblib.dump(artifact, model_path)
    payload = PredictionRequest(**VALID_PREDICTION_PAYLOAD)

    with pytest.raises(ModelPredictionError, match="Unable to generate prediction"):
        predict_credit_risk(payload, settings)
