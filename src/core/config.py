from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default

    return int(value)


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    app_debug: bool
    model_path: str
    model_version: str
    api_host: str
    api_port: int

    @property
    def resolved_model_path(self) -> Path:
        return PROJECT_ROOT / self.model_path


def get_settings() -> Settings:
    load_dotenv(PROJECT_ROOT / ".env")

    return Settings(
        app_name=os.getenv("APP_NAME", "KoopCare ML Inference API"),
        app_env=os.getenv("APP_ENV", "development"),
        app_debug=_get_bool_env("APP_DEBUG", False),
        model_path=os.getenv("MODEL_PATH", "models/best_model.pkl"),
        model_version=os.getenv("MODEL_VERSION", "koopcare-xgboost-v1"),
        api_host=os.getenv("API_HOST", "127.0.0.1"),
        api_port=_get_int_env("API_PORT", 8000),
    )
