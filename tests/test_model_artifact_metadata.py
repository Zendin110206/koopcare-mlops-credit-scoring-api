from pathlib import Path

import joblib
import pytest

from src.core.config import Settings
from src.services.model_service import get_model_info, load_model_artifact_metadata


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


def test_get_model_info_uses_configuration_when_artifact_missing(tmp_path: Path) -> None:
    settings = make_settings(tmp_path / "missing_model.pkl")

    model_info = get_model_info(settings)

    assert model_info.model_loaded is False
    assert model_info.artifact_status == "missing"
    assert model_info.metadata_source == "configuration"
    assert model_info.artifact_keys == []
    assert model_info.artifact_error is None
    assert model_info.model_name == "XGBoost"
    assert model_info.threshold == 0.6660796
    assert model_info.features_count == 25


def test_get_model_info_reads_valid_artifact_metadata(tmp_path: Path) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    artifact = {
        "features": ["CODE_GENDER", "AMT_CREDIT", "PAYMENT_RATE"],
        "model": "dummy-model",
        "model_name": "XGBoost",
        "preprocessor": "dummy-preprocessor",
        "threshold": 0.42,
    }
    joblib.dump(artifact, model_path)

    model_info = get_model_info(settings)

    assert model_info.model_loaded is True
    assert model_info.artifact_status == "available"
    assert model_info.metadata_source == "artifact"
    assert model_info.artifact_error is None
    assert model_info.model_name == "XGBoost"
    assert model_info.threshold == 0.42
    assert model_info.features_count == 3
    assert model_info.artifact_keys == sorted(artifact.keys())


def test_get_model_info_handles_invalid_artifact_without_crashing(
    tmp_path: Path,
) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    joblib.dump({"features": ["CODE_GENDER"]}, model_path)

    model_info = get_model_info(settings)

    assert model_info.model_loaded is False
    assert model_info.artifact_status == "invalid"
    assert model_info.metadata_source == "configuration"
    assert model_info.artifact_keys == []
    assert "missing required keys" in str(model_info.artifact_error)


def test_load_model_artifact_metadata_validates_feature_list(tmp_path: Path) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    joblib.dump(
        {
            "features": "CODE_GENDER",
            "model": "dummy-model",
            "preprocessor": "dummy-preprocessor",
            "threshold": 0.42,
        },
        model_path,
    )

    with pytest.raises(TypeError, match="features"):
        load_model_artifact_metadata(settings)
