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
