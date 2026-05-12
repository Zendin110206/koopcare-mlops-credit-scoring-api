from pathlib import Path

import joblib
import pytest
from fastapi.testclient import TestClient

import src.main as main_module
from src.core.config import Settings
from src.main import app
from src.services.model_service import MODEL_FEATURE_COLUMNS


client = TestClient(app)

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


def test_predict_endpoint_returns_prediction_response(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_path = tmp_path / "best_model.pkl"
    joblib.dump(make_artifact([[0.75, 0.25]], threshold=0.5), model_path)
    monkeypatch.setattr(main_module, "settings", make_settings(model_path))

    response = client.post("/predict", json=VALID_PREDICTION_PAYLOAD)

    assert response.status_code == 200

    data = response.json()

    assert data["ai_recommendation"] == "LAYAK"
    assert data["risk_level"] == "LOW"
    assert data["prob_default"] == 0.25
    assert data["threshold"] == 0.5
    assert data["confidence"] == 0.5
    assert data["model_name"] == "XGBoost"
    assert data["model_version"] == "koopcare-xgboost-v1"
    assert data["human_review_required"] is True
    assert data["final_decision"] is None


def test_predict_endpoint_returns_503_when_model_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        main_module,
        "settings",
        make_settings(tmp_path / "missing_model.pkl"),
    )

    response = client.post("/predict", json=VALID_PREDICTION_PAYLOAD)

    assert response.status_code == 503
    assert response.json()["detail"]["error"] == "model_artifact_missing"


def test_predict_endpoint_returns_503_when_model_invalid(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_path = tmp_path / "best_model.pkl"
    joblib.dump({"features": ["CODE_GENDER"]}, model_path)
    monkeypatch.setattr(main_module, "settings", make_settings(model_path))

    response = client.post("/predict", json=VALID_PREDICTION_PAYLOAD)

    assert response.status_code == 503
    assert response.json()["detail"]["error"] == "model_artifact_invalid"


def test_predict_endpoint_returns_500_when_prediction_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_path = tmp_path / "best_model.pkl"
    artifact = make_artifact([[0.75, 0.25]], threshold=0.5)
    artifact["preprocessor"] = FailingPreprocessor()
    joblib.dump(artifact, model_path)
    monkeypatch.setattr(main_module, "settings", make_settings(model_path))

    response = client.post("/predict", json=VALID_PREDICTION_PAYLOAD)

    assert response.status_code == 500
    assert response.json()["detail"]["error"] == "prediction_failed"


def test_predict_endpoint_returns_422_for_invalid_request() -> None:
    response = client.post(
        "/predict",
        json={
            **VALID_PREDICTION_PAYLOAD,
            "flag_own_car": "INVALID",
        },
    )

    assert response.status_code == 422
