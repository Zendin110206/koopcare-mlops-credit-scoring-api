# KoopCare Reviewer Quickstart

This document helps reviewers, teammates, mentors, or portfolio readers understand what is already usable and how to run the KoopCare ML inference API.

## 1. Current Readiness Status

The repository is ready for:

- local API testing;
- backend integration testing;
- frontend/mobile integration planning;
- reviewer demo from source code;
- reviewer demo with Docker;
- portfolio review of the MLOps implementation.

The repository is not yet a production deployment.

It does not currently provide a permanent public API URL.

## 2. What Is Already Implemented

Implemented API endpoints:

```text
GET /
GET /health
GET /model-info
POST /predict
GET /docs
```

Implemented MLOps behavior:

- loads the local `models/best_model.pkl` artifact when available;
- validates artifact keys and runtime components;
- validates exact model feature order;
- applies saved preprocessing before prediction;
- reads class 1 probability as default risk;
- applies the model threshold;
- returns `LAYAK` or `TIDAK_LAYAK`;
- preserves human-in-the-loop decision wording;
- returns clear errors when model artifact is missing or invalid.

Implemented support assets:

- API contract;
- model card;
- prediction examples;
- Postman collection;
- model handoff contract;
- team integration contract;
- Docker support;
- automated test workflow through GitHub Actions.

## 3. What Reviewers Can Check Without the Model Artifact

Reviewers can still inspect and run many parts without `models/best_model.pkl`.

They can:

- install dependencies;
- run tests;
- start the API;
- open `/health`;
- open `/model-info`;
- open `/docs`;
- review API schemas;
- review documentation;
- review Postman collection;
- review Docker setup.

Expected behavior without the artifact:

```text
GET /health works
GET /model-info reports missing artifact
POST /predict returns HTTP 503 model_artifact_missing
```

This is intentional.

The model artifact is not committed to GitHub.

## 4. What Reviewers Need for Full Prediction Demo

For full prediction demo, reviewers need:

```text
models/best_model.pkl
```

Download command:

```powershell
Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/AdityaNugrahaPS/KoopCare-EDA/main/best_model.pkl" `
  -OutFile ".\models\best_model.pkl"
```

The file remains local and ignored by git.

## 5. Run Locally with Python

Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run tests:

```powershell
pytest
```

Run API:

```powershell
uvicorn src.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/model-info
http://127.0.0.1:8000/docs
```

## 6. Run with Docker

Prepare the model artifact if full prediction is needed:

```text
models/best_model.pkl
```

Run:

```powershell
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/model-info
http://127.0.0.1:8000/docs
```

Stop:

```powershell
docker compose down
```

Docker mounts:

```text
./models:/app/models:ro
```

The Docker image does not include `best_model.pkl`.

## 7. Run Prediction

Use:

```text
POST http://127.0.0.1:8000/predict
```

Request example:

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

Expected response shape:

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

## 8. GitHub Actions CI

The repository includes a CI workflow:

```text
.github/workflows/ci.yml
```

The workflow runs on:

- push to `main`;
- pull request to `main`.

The workflow checks:

- dependency installation;
- `pip check`;
- Python compile check;
- full `pytest` suite.

This gives reviewers a visible signal that the repository is maintained and testable.

## 9. Public Demo Options

There are three practical demo levels.

### Option A - Local Demo

Use this when the reviewer is technical and can run Python.

Status:

```text
ready now
```

### Option B - Docker Demo

Use this when the reviewer has Docker installed and wants a more consistent runtime.

Status:

```text
ready now
```

### Option C - Public URL Deployment

Use this when mobile/web teammates need a shared URL and cannot run the API locally.

Status:

```text
not done yet
```

Before public deployment, decide:

- where the API will be hosted;
- how the model artifact will be provided;
- whether the endpoint should require authentication;
- whether the API should be reachable publicly or only by backend services;
- how to avoid exposing a decision-support model as an automatic approval system.

## 10. Recommended Message for Reviewers

```text
This repository contains the KoopCare ML inference API for credit scoring decision support.

It is ready for local and Docker-based testing. The API exposes /health, /model-info, and /predict. The model artifact is not committed to GitHub, so full prediction requires placing best_model.pkl inside the models/ folder.

The API output is only an AI recommendation. Final financing decisions must remain under cooperative officer review.
```

## 11. Important Limitation

The current model is a prototype trained on Home Credit style data.

For real BMT production deployment, the model should be retrained with cooperative-native data and reviewed again with the model handoff contract.
