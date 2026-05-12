# KoopCare MLOps Credit Scoring API

FastAPI-based machine learning inference service for KoopCare, an AI-assisted credit scoring decision-support system for BMT/cooperative financing workflows.

## Project Status

This repository is currently in the initial MLOps/API setup phase.

The current focus is to prepare a clean, documented, and reproducible API repository before implementing the full prediction service.

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

## Planned API Features

- `GET /health` for service health checks
- `GET /model-info` for model metadata
- `POST /predict` for credit risk prediction
- FastAPI OpenAPI documentation at `/docs`
- human-in-the-loop response design

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
