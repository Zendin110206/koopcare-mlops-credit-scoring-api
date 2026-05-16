# KoopCare Reviewer Quickstart

This document helps reviewers, teammates, mentors, or portfolio readers
understand what is already usable and how to run the KoopCare ML inference API.

## 1. Current Readiness Status

The repository is ready for:

- local API testing;
- backend integration testing;
- frontend/mobile integration planning;
- reviewer demo from source code;
- reviewer demo with Docker;
- public API deployment using the included Dockerfile and `railway.toml`;
- portfolio review of the MLOps implementation.

The repository is still a prototype decision-support service, not a real
production credit approval system.

For the approved public portfolio checkpoint, the repository now includes the
current prototype artifact:

```text
models/best_model.pkl
```

Earlier local-only checkpoints kept this file outside Git. The team has now
allowed the artifact to be included so the public Docker deployment can run
`/predict` without manual file upload.

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

- loads `models/best_model.pkl`;
- validates artifact keys and runtime components;
- validates exact model feature order;
- applies saved preprocessing before prediction;
- reads class 1 probability as default risk;
- applies the model threshold;
- returns `LAYAK` or `TIDAK_LAYAK`;
- preserves human-in-the-loop decision wording;
- returns clear errors when the model artifact is missing or invalid.

Implemented support assets:

- API contract;
- model card;
- prediction examples;
- Postman collection;
- model handoff contract;
- team integration contract;
- Docker support;
- Railway deployment config;
- automated test workflow through GitHub Actions.

## 3. What Reviewers Can Check From a Clean Clone

Because the approved artifact is now committed, a reviewer can clone the
repository and run the full local or Docker demo immediately after installing
dependencies.

They can:

- install dependencies;
- run tests;
- start the API;
- open `/health`;
- open `/model-info`;
- open `/docs`;
- run `/predict`;
- review API schemas;
- review documentation;
- review Postman collection;
- review Docker and Railway setup.

Expected healthy runtime behavior:

```text
GET /health works
GET /model-info reports artifact_status = available
POST /predict returns a decision-support recommendation
```

The API still keeps missing-artifact and invalid-artifact error handling because
future model replacement, bad deploys, or local file deletion must fail clearly.

## 4. Model Artifact Source and Safety

The current prototype model originally comes from:

```text
https://github.com/AdityaNugrahaPS/KoopCare-EDA
```

Current artifact path:

```text
models/best_model.pkl
```

Runtime identity:

```text
model_name: XGBoost
model_version: koopcare-xgboost-v1
threshold: 0.6660796
required_features: 25
```

Only use trusted KoopCare/team artifacts. Python pickle/joblib files can execute
code while loading, so do not replace this file with an unknown artifact.

Do not silently replace `models/best_model.pkl`. If the model changes, follow:

```text
docs/model_handoff_contract.md
```

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

If `/model-info` is healthy, it should show:

```text
artifact_status = available
metadata_source = artifact
model_loaded = true
```

## 6. Run with Docker

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

Docker Compose still mounts:

```text
./models:/app/models:ro
```

This lets developers test a deliberate local artifact replacement. The
production Docker image also includes `models/best_model.pkl`, so a public
platform such as Railway can run without a manual volume.

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

This gives reviewers a visible signal that the repository is maintained and
testable.

## 9. Public URL Deployment

Public deployment is now prepared in this repository.

Deployment config:

```text
Dockerfile
railway.toml
docs/public_deployment.md
docs/railway_variables.md
```

Recommended public flow:

```text
Railway public FastAPI URL
-> /health
-> /model-info
-> /predict
```

After Railway gives a public URL, verify from project 14:

```powershell
npm run verify:ml-api -- https://your-ml-api-url
```

Then connect project 14 by setting:

```text
ML_API_BASE_URL=https://your-ml-api-url
ML_SCORING_MODE=optional_fallback
```

After project 14 redeploys, verify the full public path:

```powershell
npm run verify:public -- https://koopcare-fullstack-demo-platform-production.up.railway.app/ --write-test --expect-ml-api
```

## 10. Recommended Message for Reviewers

```text
This repository contains the KoopCare ML inference API for credit scoring decision support.

It is ready for local, Docker, and public API deployment testing. The API exposes /health, /model-info, and /predict. The approved prototype model artifact is included at models/best_model.pkl so a Docker-based public deployment can run real inference.

The API output is only an AI recommendation. Final financing decisions must remain under cooperative officer review.
```

## 11. Important Limitation

The current model is a prototype trained on Home Credit style data.

For real BMT production deployment, the model should be retrained with
cooperative-native data and reviewed again with the model handoff contract.
