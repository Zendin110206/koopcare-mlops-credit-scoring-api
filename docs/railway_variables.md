# Railway Variables Guide

Last updated: 2026-05-16

This guide explains what to do when Railway shows suggested variables from this
repository.

Railway scans `.env.example` and can suggest variables automatically. That is
normal. Do not click "Add all" without checking the values first, because some
values in `.env.example` are local-development defaults.

Official Railway references:

- `https://docs.railway.com/variables`
- `https://docs.railway.com/config-as-code/reference`
- `https://docs.railway.com/deployments/healthchecks`

## Short Answer

Use this for the project 13 Railway service:

```text
APP_ENV=production
APP_DEBUG=false
MODEL_PATH=models/best_model.pkl
MODEL_NAME=XGBoost
MODEL_VERSION=koopcare-xgboost-v1
MODEL_THRESHOLD=0.6660796
MODEL_FEATURES_COUNT=25
```

Do not add these unless Railway logs specifically require them:

```text
API_HOST
API_PORT
PORT
```

Why:

- the Docker command already listens on `0.0.0.0`;
- Railway injects `PORT`;
- the Docker command already uses `PORT` first, then `API_PORT`, then `8000`;
- setting `API_HOST=127.0.0.1` is local-only and should not drive public
  serving behavior.

## Variable-by-Variable Decision

| Variable | Railway value | Action | Reason |
| --- | --- | --- | --- |
| `APP_NAME` | `KoopCare ML Inference API` | optional | Nice metadata only. The API has a safe default. |
| `APP_ENV` | `production` | add | Public service should not say development. |
| `APP_DEBUG` | `false` | add | Debug mode should not be enabled in public demos. |
| `MODEL_PATH` | `models/best_model.pkl` | add | Confirms the committed model artifact path. |
| `MODEL_NAME` | `XGBoost` | add | Keeps metadata explicit. |
| `MODEL_VERSION` | `koopcare-xgboost-v1` | add | Keeps the response stable for project 14. |
| `MODEL_THRESHOLD` | `0.6660796` | add | Matches the inspected artifact threshold. |
| `MODEL_FEATURES_COUNT` | `25` | add | Matches the current artifact feature count. |
| `API_HOST` | do not add | skip | Local config value; Docker already binds `0.0.0.0`. |
| `API_PORT` | do not add | skip | Railway injects `PORT`; Docker already falls back safely. |
| `PORT` | do not add manually | skip | Railway owns this unless its logs ask you to override. |

## What To Do In Your Railway Screen

You saw suggested variables like:

```text
APP_ENV=development
APP_DEBUG=true
API_HOST=127.0.0.1
API_PORT=8000
```

Do not add them exactly like that for production.

Use the Raw Editor and paste this instead:

```text
APP_ENV=production
APP_DEBUG=false
MODEL_PATH=models/best_model.pkl
MODEL_NAME=XGBoost
MODEL_VERSION=koopcare-xgboost-v1
MODEL_THRESHOLD=0.6660796
MODEL_FEATURES_COUNT=25
```

If `APP_NAME` is already there, it is fine:

```text
APP_NAME=KoopCare ML Inference API
```

Do not worry about the Railway system variables such as:

```text
RAILWAY_PRIVATE_DOMAIN
RAILWAY_PROJECT_NAME
RAILWAY_SERVICE_NAME
RAILWAY_SERVICE_ID
```

Those are created by Railway. Leave them alone.

## After Setting Variables

Redeploy the project 13 service.

Then open:

```text
https://your-project-13-url/health
https://your-project-13-url/model-info
```

Expected `/model-info`:

```text
model_loaded=true
artifact_status=available
metadata_source=artifact
```

Then run from project 14:

```powershell
npm run verify:ml-api -- https://your-project-13-url
```

Only after that passes, put the project 13 public URL into the project 14
Railway service:

```text
ML_API_BASE_URL=https://your-project-13-url
ML_SCORING_MODE=optional_fallback
```

Then redeploy project 14 and verify:

```powershell
npm run verify:public -- https://koopcare-fullstack-demo-platform-production.up.railway.app/ --write-test --expect-ml-api
```
