# Public Deployment Guide

Last updated: 2026-05-16

This guide explains how to publish the KoopCare MLOps API so the public
fullstack demo can use trained model scoring instead of fallback scoring.

## Current Goal

The target runtime is:

```text
public fullstack KoopCare web app
  -> Express backend in project 14
  -> public FastAPI MLOps API in project 13
  -> models/best_model.pkl
  -> XGBoost prediction response
```

The public MLOps API must expose:

```text
GET /
GET /health
GET /model-info
POST /predict
```

## Recommended Platform

The repository now includes:

```text
railway.toml
```

The Railway service should build from:

```text
Dockerfile
```

The Docker image now includes:

```text
models/best_model.pkl
```

This is intentional for the public portfolio demo. The team has allowed the
current prototype model artifact to be deployed so the end-to-end public demo can
show real trained-model inference.

## Why the Model Artifact Is Included Now

Earlier local-only checkpoints kept `best_model.pkl` outside Git and mounted it
into Docker at runtime.

That was safe for local development, but it creates a public deployment problem:

```text
public container starts
model file is missing
/health works
/model-info reports missing
/predict returns 503 model_artifact_missing
```

For the current public demo checkpoint, the artifact is small enough and approved
for deployment, so the Docker build includes it.

## Railway Setup

Create a new Railway service from:

```text
https://github.com/Zendin110206/koopcare-mlops-credit-scoring-api
```

Railway should detect:

```text
railway.toml
Dockerfile
```

Set these variables if Railway does not already infer them:

```text
APP_ENV=production
MODEL_PATH=models/best_model.pkl
MODEL_NAME=XGBoost
MODEL_VERSION=koopcare-xgboost-v1
MODEL_THRESHOLD=0.6660796
MODEL_FEATURES_COUNT=25
```

Do not manually set `PORT` unless Railway support or logs specifically ask for
it. Railway injects `PORT`, and the Docker command now uses:

```text
PORT first
API_PORT second
8000 fallback
```

## Public URL Checks

After Railway provides a public URL, check:

```text
https://your-ml-api-url/health
https://your-ml-api-url/model-info
```

Expected `/model-info` readiness:

```text
model_loaded: true
artifact_status: available
metadata_source: artifact
```

Then verify from project 14:

```powershell
npm run verify:ml-api -- https://your-ml-api-url
```

That command checks `/health`, `/model-info`, and `/predict`.

## Connect Project 14

After the public MLOps API verification passes, open the Railway service for
project 14 and set:

```text
ML_API_BASE_URL=https://your-ml-api-url
ML_SCORING_MODE=optional_fallback
```

Keep `optional_fallback` during the first public integration test so the product
workflow remains available if the ML service has a temporary outage.

Then run from project 14:

```powershell
npm run verify:public -- https://koopcare-fullstack-demo-platform-production.up.railway.app/ --write-test --expect-ml-api
```

The expected scoring source is:

```text
source=ml_api
```

Only after that passes should you consider:

```text
ML_SCORING_MODE=strict_ml
```

## Public Demo Safety Notes

This model is still a prototype decision-support model.

Do not describe the API as automatic approval.

Use this product principle everywhere:

```text
AI recommends, cooperative officers decide.
```

The public API can demonstrate trained scoring, but real production credit use
still needs:

- cooperative-native retraining;
- domain review;
- security review;
- legal/compliance review;
- monitoring and audit logging.
