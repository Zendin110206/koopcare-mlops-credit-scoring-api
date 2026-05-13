# KoopCare MLOps Credit Scoring API

[![CI](https://github.com/Zendin110206/koopcare-mlops-credit-scoring-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Zendin110206/koopcare-mlops-credit-scoring-api/actions/workflows/ci.yml)

FastAPI-based machine learning inference service for KoopCare, an AI-assisted credit scoring decision-support system for BMT/cooperative financing workflows.

## Project Status

This repository is currently in the prototype MLOps/API implementation phase.

The current API includes working health, model metadata, and prediction endpoints. The prediction endpoint loads the local model artifact, applies the saved preprocessor, runs XGBoost probability inference, and returns a human-in-the-loop decision-support response.

## Project Context

KoopCare is designed to support BMT/cooperative officers when reviewing financing applications from unbankable or underbanked members.

The product principle is:

```text
AI recommends, cooperative officers decide.
```

This repository focuses on the ML Ops and ML integration layer. The goal is to wrap a trained credit scoring model into an API that can be integrated with backend, web, or mobile applications.

## My Role

ML Ops / ML Integration.

Main responsibilities in this repository:

- prepare the machine learning inference API
- load the trained model artifact
- preserve preprocessing parity between training and inference
- define request and response schemas
- expose health, model metadata, and prediction endpoints
- document model assumptions and limitations
- support backend, web, and mobile integration

## API Status

- `GET /` returns basic service navigation
- `GET /health` returns service health and local model availability
- `GET /model-info` returns configured model metadata and validated local artifact status
- `POST /predict` returns credit risk prediction and decision-support output
- FastAPI OpenAPI documentation is available at `/docs` when the server is running
- human-in-the-loop response design is implemented for prediction output
- Docker support is available for reproducible local API serving
- GitHub Actions CI is available for automated test checks on push and pull request

## Current Model Direction

The API uses the KoopCare prototype model artifact when it is available locally:

```text
models/best_model.pkl
```

Based on artifact inspection during project audit, the current prototype artifact contains:

```text
model_name: XGBoost
threshold: 0.6660796
required_features: 25
```

The model artifact itself is not committed to this repository because model files are generated artifacts and may require permission from the project team.

## Tech Stack

- Python 3.12
- FastAPI
- Uvicorn
- pandas
- NumPy
- scikit-learn 1.6.1 for compatibility with the current `best_model.pkl` artifact
- XGBoost 3.2.0
- joblib
- pytest

## Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
├── docs/
│   ├── api_contract.md
│   ├── development_log.md
│   ├── docker_usage.md
│   ├── model_handoff_contract.md
│   ├── model_card.md
│   ├── prediction_usage_examples.md
│   ├── reviewer_quickstart.md
│   └── team_integration_contract.md
├── models/
├── postman/
├── references/
├── src/
│   ├── core/
│   ├── schemas/
│   └── services/
├── tests/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── .gitignore
├── requirements.txt
└── README.md
```

## Local Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

The current `best_model.pkl` artifact was created with scikit-learn 1.6.1. If you previously installed unpinned dependencies, rerun the command above so the local environment uses the compatible version.

Copy environment configuration:

```powershell
Copy-Item .env.example .env
```

Run the API:

```powershell
uvicorn src.main:app --reload
```

Or run with Docker Compose:

```powershell
docker compose up --build
```

Docker mounts `./models` into the container as read-only. The image does not include `models/best_model.pkl`.

Open local health check:

```text
http://127.0.0.1:8000/health
```

Open model metadata:

```text
http://127.0.0.1:8000/model-info
```

Open FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

Open prediction usage examples:

```text
docs/prediction_usage_examples.md
```

Open reviewer quickstart:

```text
docs/reviewer_quickstart.md
```

Run tests:

```powershell
pytest
```

Prepare the local model artifact when you need `/model-info` to validate the runtime model:

```powershell
Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/AdityaNugrahaPS/KoopCare-EDA/main/best_model.pkl" `
  -OutFile ".\models\best_model.pkl"
```

The downloaded `.pkl` file stays local and is ignored by git.

## Current Endpoint Examples

Health check:

```json
{
  "status": "ok",
  "service": "KoopCare ML Inference API",
  "environment": "development",
  "model_loaded": false,
  "model_path": "models/best_model.pkl"
}
```

Model metadata:

```json
{
  "model_loaded": false,
  "model_name": "XGBoost",
  "model_version": "koopcare-xgboost-v1",
  "model_path": "models/best_model.pkl",
  "threshold": 0.6660796,
  "features_count": 25,
  "artifact_status": "missing",
  "artifact_keys": [],
  "artifact_error": null,
  "metadata_source": "configuration",
  "note": "Model artifact is not available yet. Copy best_model.pkl into models/ before enabling prediction."
}
```

Model metadata after a valid local artifact is available:

```json
{
  "model_loaded": true,
  "model_name": "XGBoost",
  "model_version": "koopcare-xgboost-v1",
  "model_path": "models/best_model.pkl",
  "threshold": 0.6660796,
  "features_count": 25,
  "artifact_status": "available",
  "artifact_keys": [
    "features",
    "model",
    "model_name",
    "preprocessor",
    "threshold"
  ],
  "artifact_error": null,
  "metadata_source": "artifact",
  "note": "Model artifact is available and runtime components were validated."
}
```

Prediction request schema preview:

```json
{
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
  "ext_source_3": 0.4
}
```

Prepared model feature mapping:

```text
PredictionRequest -> 25 model feature columns
```

Derived features prepared by the service layer:

- `AGE_YEARS` from `days_birth`
- `DAYS_EMPLOYED_ANOM` from the Home Credit anomaly value `365243`
- `EXT_SOURCE_MEAN` from `ext_source_1`, `ext_source_2`, and `ext_source_3`
- `EXT_SOURCE_MIN` from `ext_source_1`, `ext_source_2`, and `ext_source_3`
- `EXT_SOURCE_PROD` from `ext_source_1`, `ext_source_2`, and `ext_source_3`
- `DEBT_TO_INCOME` from `amt_credit / (amt_income_total + 1)`
- `PAYMENT_RATE` from `amt_annuity / (amt_credit + 1)`

Model artifact metadata handling:

- missing artifact returns `artifact_status: "missing"`
- valid artifact returns `artifact_status: "available"` and `metadata_source: "artifact"`
- invalid artifact returns `artifact_status: "invalid"` without crashing the API
- valid artifact loading checks required keys, exact expected feature order, `model.predict_proba(...)`, `preprocessor.transform(...)`, and a threshold between `0` and `1`

Prepared prediction decision helpers:

- `prob_default >= threshold` returns `TIDAK_LAYAK`
- `prob_default < threshold` returns `LAYAK`
- risk level is derived from probability bands around the threshold
- confidence is derived from the distance between probability and threshold
- every prediction response defaults to `human_review_required: true`

Prediction inference flow:

```text
PredictionRequest
-> build_model_feature_frame(...)
-> preprocessor.transform(...)
-> model.predict_proba(...)
-> class 1 probability as prob_default
-> PredictionResponse
```

`POST /predict` with the example payload currently returns:

```json
{
  "ai_recommendation": "LAYAK",
  "risk_level": "MEDIUM",
  "prob_default": 0.581492,
  "threshold": 0.66608,
  "confidence": 0.126993,
  "model_name": "XGBoost",
  "model_version": "koopcare-xgboost-v1",
  "human_review_required": true,
  "final_decision": null,
  "note": "AI recommendation only. Final financing decision must be reviewed and approved by cooperative officers."
}
```

Prediction endpoint error handling:

- missing local model artifact returns HTTP `503` with `model_artifact_missing`
- invalid model artifact returns HTTP `503` with `model_artifact_invalid`
- runtime inference failure returns HTTP `500` with `prediction_failed`
- invalid request body returns FastAPI/Pydantic HTTP `422`

## Documentation

- [API Contract](docs/api_contract.md)
- [Model Card](docs/model_card.md)
- [Model Handoff Contract](docs/model_handoff_contract.md)
- [Prediction Usage Examples](docs/prediction_usage_examples.md)
- [Reviewer Quickstart](docs/reviewer_quickstart.md)
- [Team Integration Contract](docs/team_integration_contract.md)
- [Docker Usage](docs/docker_usage.md)
- [Development Log](docs/development_log.md)
- [Data Notes](data/README.md)
- [Model Artifact Notes](models/README.md)
- [Postman Collection Notes](postman/README.md)

## Important Limitation

The current model direction is based on a prototype trained on Home Credit style data, not real BMT production data.

Some prototype features, such as external credit source scores, may not be available for real unbankable BMT members. A production-ready model should be retrained and validated using cooperative-native data such as saving balance, member active duration, saving consistency, previous financing history, and repayment behavior.

## Disclaimer

This API is intended to provide AI recommendations only.

Final financing decisions must remain under cooperative officer review.
