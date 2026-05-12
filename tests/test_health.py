import pytest
from fastapi.testclient import TestClient

import src.main as main_module
from src.core.config import Settings
from src.main import app


client = TestClient(app)
TEST_MODEL_PATH = "models/test_missing_model.pkl"


@pytest.fixture(autouse=True)
def use_missing_model_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    test_settings = Settings(
        app_name="KoopCare ML Inference API",
        app_env="development",
        app_debug=True,
        model_path=TEST_MODEL_PATH,
        model_name="XGBoost",
        model_version="koopcare-xgboost-v1",
        model_threshold=0.6660796,
        model_features_count=25,
        api_host="127.0.0.1",
        api_port=8000,
    )
    monkeypatch.setattr(main_module, "settings", test_settings)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "KoopCare ML Inference API"
    assert data["environment"] == "development"
    assert data["model_loaded"] is False
    assert data["model_path"] == TEST_MODEL_PATH


def test_root_endpoint_points_to_docs_and_health() -> None:
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "KoopCare ML Inference API"
    assert data["health_url"] == "/health"
    assert data["model_info_url"] == "/model-info"
    assert data["docs_url"] == "/docs"


def test_model_info_endpoint_returns_expected_metadata() -> None:
    response = client.get("/model-info")

    assert response.status_code == 200

    data = response.json()

    assert data["model_loaded"] is False
    assert data["model_name"] == "XGBoost"
    assert data["model_version"] == "koopcare-xgboost-v1"
    assert data["model_path"] == TEST_MODEL_PATH
    assert data["threshold"] == 0.6660796
    assert data["features_count"] == 25
    assert data["artifact_status"] == "missing"
    assert data["artifact_keys"] == []
    assert data["artifact_error"] is None
    assert data["metadata_source"] == "configuration"
    assert "best_model.pkl" in data["note"]
