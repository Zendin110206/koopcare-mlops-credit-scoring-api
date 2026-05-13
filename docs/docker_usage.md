# KoopCare Docker Usage

This document explains how to run the KoopCare ML Inference API with Docker.

Docker support is intended to make local serving more reproducible for API demos, backend integration, frontend/mobile testing, and portfolio review.

## 1. Important Artifact Rule

The Docker image does not include:

```text
models/best_model.pkl
```

The model artifact stays local and is mounted into the container at runtime.

Why:

- model artifacts are generated binary files;
- artifact permissions may belong to the model owner or project team;
- pickle/joblib artifacts should only come from trusted sources;
- keeping the image source-only makes the repository safer and cleaner.

## 2. Prepare the Model Artifact

Before running real prediction through Docker, prepare:

```text
models/best_model.pkl
```

PowerShell:

```powershell
Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/AdityaNugrahaPS/KoopCare-EDA/main/best_model.pkl" `
  -OutFile ".\models\best_model.pkl"
```

The artifact remains ignored by git.

## 3. Run with Docker Compose

From the repository root:

```powershell
docker compose up --build
```

The first build can take several minutes because the scientific Python and XGBoost dependencies are large.

The compose file mounts:

```text
./models -> /app/models
```

as read-only:

```text
./models:/app/models:ro
```

This allows the container to read `models/best_model.pkl` without baking it into the image.

## 4. Check the API

Health:

```text
http://127.0.0.1:8000/health
```

Model info:

```text
http://127.0.0.1:8000/model-info
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Prediction endpoint:

```text
POST http://127.0.0.1:8000/predict
```

Use the request payload from:

```text
docs/prediction_usage_examples.md
```

For a broader reviewer-oriented run guide, see:

```text
docs/reviewer_quickstart.md
```

## 5. Expected Model Status

If `models/best_model.pkl` exists and is compatible, `/model-info` should return:

```text
model_loaded: true
artifact_status: available
metadata_source: artifact
```

If the model artifact is missing, the API can still start.

In that case:

```text
/health works
/model-info reports missing artifact
/predict returns HTTP 503
```

## 6. Stop the Container

```powershell
docker compose down
```

## 7. Rebuild After Dependency Changes

If `requirements.txt` changes:

```powershell
docker compose build --no-cache
docker compose up
```

## 8. Verified Local Docker Runtime

The Docker setup has been verified locally with the current `models/best_model.pkl` artifact:

```text
GET /health      -> status ok
GET /model-info  -> artifact_status available
POST /predict    -> LAYAK / MEDIUM for the documented example payload
```

## 9. Notes for FE/BE/Mobile Teams

Use Docker when you need a stable local API base URL:

```text
http://127.0.0.1:8000
```

Before testing client integration, confirm:

```text
GET /health
GET /model-info
```

Then use:

```text
POST /predict
```

The AI output remains decision support only.

Final financing decisions must stay under cooperative officer review.
