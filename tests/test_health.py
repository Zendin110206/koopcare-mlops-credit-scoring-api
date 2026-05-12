from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "KoopCare ML Inference API"
    assert data["environment"] == "development"
    assert data["model_loaded"] is False
    assert data["model_path"] == "models/best_model.pkl"


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
    assert data["model_path"] == "models/best_model.pkl"
    assert data["threshold"] == 0.6660796
    assert data["features_count"] == 25
    assert data["artifact_status"] == "missing"
    assert data["metadata_source"] == "configuration"
    assert "best_model.pkl" in data["note"]
