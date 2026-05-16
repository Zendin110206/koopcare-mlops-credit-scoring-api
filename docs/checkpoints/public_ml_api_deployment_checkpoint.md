# Checkpoint - Public ML API Deployment Readiness

Last updated: 2026-05-16

This checkpoint records the public-deployment state of the KoopCare MLOps API.

It exists outside `local_context/` so the important deployment milestone is
visible in the public repository. The longer private learning notes remain in
`local_context/progress_notes/`, which is intentionally ignored by Git.

## Commit Scope

Main deployment commit:

```text
5149b21 chore: prepare ml api public deployment
```

Follow-up model-risk documentation commit:

```text
6dece83 docs: note model serialization warning
```

Current Railway variable clarification:

```text
docs(deployment): clarify Railway variables and checkpoint
```

## What Changed

The project moved from local-only model serving to public deployment readiness.

Before:

```text
Docker image did not include models/best_model.pkl
Public deployment needed a separate model artifact strategy
Project 14 public demo had to use fallback scoring
```

After:

```text
models/best_model.pkl is included for the approved public demo checkpoint
Dockerfile copies the model artifact into the image
railway.toml tells Railway to build with Dockerfile
/health is the Railway health check path
docs/public_deployment.md explains the public deploy flow
docs/railway_variables.md explains which Railway variables to add or skip
```

## Verified Locally

Commands verified:

```powershell
python -m compileall -q src tests
python -m pytest
python -m pip check
docker build -t koopcare-mlops-api:public-ready .
```

Runtime verified:

```text
Docker container starts
GET /health -> status ok
GET /model-info -> artifact_status available
POST /predict -> recommendation LAYAK
```

Project 14 bridge verified:

```powershell
npm run verify:ml-api -- http://127.0.0.1:8011
```

Result:

```text
MLOps API URL verification passed
```

## Railway Variables

Use:

```text
APP_ENV=production
APP_DEBUG=false
MODEL_PATH=models/best_model.pkl
MODEL_NAME=XGBoost
MODEL_VERSION=koopcare-xgboost-v1
MODEL_THRESHOLD=0.6660796
MODEL_FEATURES_COUNT=25
```

Skip unless Railway logs ask for them:

```text
API_HOST
API_PORT
PORT
```

## Remaining Manual Step

The code is ready, but the Railway account action must still happen manually:

```text
Deploy project 13 on Railway
Copy the public project 13 URL
Verify it with project 14 npm run verify:ml-api
Set project 14 ML_API_BASE_URL to that URL
Redeploy project 14
Verify project 14 with --expect-ml-api
```

## Current Status

```text
Project 13 code readiness for public ML API: ready
Project 13 public URL: waiting for Railway deployment
Project 14 integration code: ready
Project 14 public fallback: still active until ML_API_BASE_URL is updated
```
