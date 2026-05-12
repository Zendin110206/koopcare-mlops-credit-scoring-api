# KoopCare MLOps Credit Scoring API

FastAPI-based machine learning inference service for KoopCare, an AI-assisted credit scoring decision-support system for BMT/cooperative financing workflows.

## Project Status

This repository is currently in the initial MLOps/API implementation phase.

The current API includes working health and model metadata endpoints. The prediction endpoint is planned for the next implementation checkpoints.

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
- `GET /model-info` returns configured model metadata and local artifact status
- `POST /predict` is planned for credit risk prediction; request/response schemas and feature mapping are prepared
- FastAPI OpenAPI documentation is available at `/docs` when the server is running
- human-in-the-loop response design is planned for prediction output

## Current Model Direction

The API is planned to use the KoopCare prototype model artifact:

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
- scikit-learn
- XGBoost
- joblib
- pytest

## Project Structure

```text
.
├── data/
├── docs/
│   ├── api_contract.md
│   ├── development_log.md
│   └── model_card.md
├── models/
├── postman/
├── references/
├── src/
│   ├── core/
│   ├── schemas/
│   └── services/
├── tests/
├── .env.example
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

Copy environment configuration:

```powershell
Copy-Item .env.example .env
```

Run the API:

```powershell
uvicorn src.main:app --reload
```

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

Run tests:

```powershell
pytest
```

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
  "metadata_source": "configuration",
  "note": "Model artifact is not available yet. Copy best_model.pkl into models/ before enabling prediction."
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

## Documentation

- [API Contract](docs/api_contract.md)
- [Model Card](docs/model_card.md)
- [Development Log](docs/development_log.md)
- [Data Notes](data/README.md)
- [Model Artifact Notes](models/README.md)

## Important Limitation

The current model direction is based on a prototype trained on Home Credit style data, not real BMT production data.

Some prototype features, such as external credit source scores, may not be available for real unbankable BMT members. A production-ready model should be retrained and validated using cooperative-native data such as saving balance, member active duration, saving consistency, previous financing history, and repayment behavior.

## Disclaimer

This API is intended to provide AI recommendations only.

Final financing decisions must remain under cooperative officer review.
