import tomllib
from pathlib import Path


def test_dockerfile_uses_runtime_safe_api_settings() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

    assert "FROM python:3.12-slim" in dockerfile
    assert "libgomp1" in dockerfile
    assert "COPY requirements.txt" in dockerfile
    assert "COPY src ./src" in dockerfile
    assert "COPY models/best_model.pkl ./models/best_model.pkl" in dockerfile
    assert "uvicorn" in dockerfile
    assert "0.0.0.0" in dockerfile
    assert "${PORT:-${API_PORT:-8000}}" in dockerfile
    assert "8000" in dockerfile


def test_dockerignore_excludes_private_and_large_local_files() -> None:
    dockerignore = Path(".dockerignore").read_text(encoding="utf-8")

    assert ".env" in dockerignore
    assert ".venv/" in dockerignore
    assert "local_context/" in dockerignore
    assert "models/*" in dockerignore
    assert "!models/README.md" in dockerignore
    assert "!models/best_model.pkl" in dockerignore
    assert "data/*" in dockerignore


def test_railway_config_uses_dockerfile_and_healthcheck() -> None:
    railway_config = Path("railway.toml").read_text(encoding="utf-8")
    parsed_config = tomllib.loads(railway_config)

    assert 'builder = "DOCKERFILE"' in railway_config
    assert 'dockerfilePath = "Dockerfile"' in railway_config
    assert 'healthcheckPath = "/health"' in railway_config
    assert "healthcheckTimeout = 300" in railway_config
    assert parsed_config["build"]["builder"] == "DOCKERFILE"
    assert parsed_config["build"]["dockerfilePath"] == "Dockerfile"
    assert parsed_config["deploy"]["healthcheckPath"] == "/health"
    assert parsed_config["deploy"]["healthcheckTimeout"] == 300
    assert parsed_config["deploy"]["restartPolicyType"] == "ON_FAILURE"
    assert parsed_config["deploy"]["restartPolicyMaxRetries"] == 3


def test_docker_compose_mounts_model_artifacts_read_only() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "koopcare-mlops-credit-scoring-api:local" in compose
    assert '"8000:8000"' in compose
    assert "MODEL_PATH: models/best_model.pkl" in compose
    assert "./models:/app/models:ro" in compose
    assert "API_HOST: 0.0.0.0" in compose


def test_docker_usage_guide_documents_model_volume_rule() -> None:
    guide = Path("docs/docker_usage.md").read_text(encoding="utf-8")

    assert "docker compose up --build" in guide
    assert "models/best_model.pkl" in guide
    assert "./models:/app/models:ro" in guide
    assert "Railway" in guide
    assert "/model-info" in guide
