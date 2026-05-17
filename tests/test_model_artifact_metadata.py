from pathlib import Path

import joblib
import pytest

import src.services.model_service as model_service
from src.core.config import Settings
from src.services.model_service import (
    MODEL_FEATURE_COLUMNS,
    ModelArtifactInvalidError,
    clear_model_artifact_cache,
    get_model_info,
    load_model_artifact,
    load_model_artifact_metadata,
)


class DummyModel:
    def predict_proba(self, transformed_features):
        return [[0.7, 0.3]]


class DummyPreprocessor:
    def transform(self, feature_frame):
        return feature_frame


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


def make_valid_artifact(**overrides):
    artifact = {
        "features": MODEL_FEATURE_COLUMNS.copy(),
        "model": DummyModel(),
        "model_name": "XGBoost",
        "preprocessor": DummyPreprocessor(),
        "threshold": 0.42,
    }
    artifact.update(overrides)
    return artifact


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
    artifact = make_valid_artifact()
    joblib.dump(artifact, model_path)

    model_info = get_model_info(settings)

    assert model_info.model_loaded is True
    assert model_info.artifact_status == "available"
    assert model_info.metadata_source == "artifact"
    assert model_info.artifact_error is None
    assert model_info.model_name == "XGBoost"
    assert model_info.threshold == 0.42
    assert model_info.features_count == 25
    assert model_info.artifact_keys == sorted(artifact.keys())


def test_load_model_artifact_returns_runtime_components(tmp_path: Path) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    artifact = make_valid_artifact()
    joblib.dump(artifact, model_path)

    loaded_artifact = load_model_artifact(settings)

    assert isinstance(loaded_artifact.model, DummyModel)
    assert isinstance(loaded_artifact.preprocessor, DummyPreprocessor)
    assert loaded_artifact.features == MODEL_FEATURE_COLUMNS
    assert loaded_artifact.threshold == 0.42
    assert loaded_artifact.model_name == "XGBoost"
    assert loaded_artifact.features_count == 25
    assert loaded_artifact.artifact_keys == sorted(artifact.keys())


def test_load_model_artifact_caches_valid_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    artifact = make_valid_artifact()
    joblib.dump(artifact, model_path)
    clear_model_artifact_cache()
    real_joblib_load = joblib.load
    load_calls = []

    def counting_joblib_load(path):
        load_calls.append(path)
        return real_joblib_load(path)

    monkeypatch.setattr(model_service.joblib, "load", counting_joblib_load)

    first_loaded_artifact = load_model_artifact(settings)
    second_loaded_artifact = load_model_artifact(settings)

    assert first_loaded_artifact is second_loaded_artifact
    assert len(load_calls) == 1

    clear_model_artifact_cache()


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
    joblib.dump(make_valid_artifact(features="CODE_GENDER"), model_path)

    with pytest.raises(ModelArtifactInvalidError, match="features"):
        load_model_artifact_metadata(settings)


def test_load_model_artifact_validates_feature_order(tmp_path: Path) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    artifact = make_valid_artifact(features=MODEL_FEATURE_COLUMNS[:-1])
    joblib.dump(artifact, model_path)

    with pytest.raises(ModelArtifactInvalidError, match="expected KoopCare"):
        load_model_artifact(settings)


def test_load_model_artifact_validates_model_predict_proba(tmp_path: Path) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    artifact = make_valid_artifact(model=object())
    joblib.dump(artifact, model_path)

    with pytest.raises(ModelArtifactInvalidError, match="predict_proba"):
        load_model_artifact(settings)


def test_load_model_artifact_validates_preprocessor_transform(tmp_path: Path) -> None:
    model_path = tmp_path / "best_model.pkl"
    settings = make_settings(model_path)
    artifact = make_valid_artifact(preprocessor=object())
    joblib.dump(artifact, model_path)

    with pytest.raises(ModelArtifactInvalidError, match="transform"):
        load_model_artifact(settings)
