import json
from pathlib import Path


POSTMAN_COLLECTION_PATH = Path(
    "postman/koopcare_ml_inference_api.postman_collection.json"
)


def _flatten_items(items: list[dict]) -> list[dict]:
    flattened: list[dict] = []

    for item in items:
        if "request" in item:
            flattened.append(item)
        flattened.extend(_flatten_items(item.get("item", [])))

    return flattened


def test_postman_collection_is_valid_json() -> None:
    collection = json.loads(POSTMAN_COLLECTION_PATH.read_text(encoding="utf-8"))

    assert collection["info"]["name"] == "KoopCare ML Inference API"
    assert collection["info"]["schema"].endswith("/collection/v2.1.0/collection.json")
    assert collection["variable"][0]["key"] == "base_url"
    assert collection["variable"][0]["value"] == "http://127.0.0.1:8000"


def test_postman_collection_documents_core_endpoints() -> None:
    collection = json.loads(POSTMAN_COLLECTION_PATH.read_text(encoding="utf-8"))
    requests = _flatten_items(collection["item"])
    endpoint_map = {
        request["request"]["url"]["raw"]: request["request"]["method"]
        for request in requests
    }

    assert endpoint_map["{{base_url}}/"] == "GET"
    assert endpoint_map["{{base_url}}/health"] == "GET"
    assert endpoint_map["{{base_url}}/model-info"] == "GET"
    assert endpoint_map["{{base_url}}/predict"] == "POST"


def test_prediction_usage_guide_exists() -> None:
    guide_path = Path("docs/prediction_usage_examples.md")
    guide = guide_path.read_text(encoding="utf-8")

    assert "POST /predict" in guide
    assert "human_review_required" in guide
    assert "model_artifact_missing" in guide


def test_public_deployment_guide_exists() -> None:
    guide = Path("docs/public_deployment.md").read_text(encoding="utf-8")

    assert "Railway" in guide
    assert "railway.toml" in guide
    assert "models/best_model.pkl" in guide
    assert "ML_API_BASE_URL" in guide
    assert "docs/railway_variables.md" in guide


def test_railway_variables_guide_documents_safe_production_values() -> None:
    guide = Path("docs/railway_variables.md").read_text(encoding="utf-8")

    assert "APP_ENV=production" in guide
    assert "APP_DEBUG=false" in guide
    assert "MODEL_PATH=models/best_model.pkl" in guide
    assert "Do not add these" in guide
    assert "API_HOST" in guide
    assert "API_PORT" in guide
    assert "PORT" in guide


def test_public_checkpoint_document_exists() -> None:
    guide = Path("docs/checkpoints/public_ml_api_deployment_checkpoint.md").read_text(
        encoding="utf-8"
    )

    assert "Public ML API Deployment Readiness" in guide
    assert "models/best_model.pkl" in guide
    assert "railway.toml" in guide
    assert "docs/railway_variables.md" in guide


def test_model_handoff_contract_documents_retraining_risks() -> None:
    guide = Path("docs/model_handoff_contract.md").read_text(encoding="utf-8")

    assert "No silent model replacement" in guide
    assert "EXT_SOURCE" in guide
    assert "predict_proba" in guide
    assert "exactly two probability columns" in guide


def test_team_integration_contract_documents_client_responsibilities() -> None:
    guide = Path("docs/team_integration_contract.md").read_text(encoding="utf-8")

    assert "backend" in guide.lower()
    assert "frontend" in guide.lower()
    assert "mobile" in guide.lower()
    assert "AI recommends, cooperative officers decide" in guide
