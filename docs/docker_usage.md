# KoopCare Docker Usage

This document explains how to run the KoopCare ML Inference API with Docker.

Docker support is used for:

- reproducible local API serving;
- backend integration testing;
- frontend/mobile testing;
- Railway public deployment;
- portfolio review.

## 1. Model Artifact Rule

The current approved public deployment includes:

```text
models/best_model.pkl
```

inside the Docker image.

Earlier local-only checkpoints kept the model file outside Git and mounted it at
runtime. That is still a useful local replacement pattern, but the public demo
needs the model file available inside the deployed container so `/predict` can
work without manual file upload.

The artifact is a trusted project artifact and should still be treated carefully:

- only use artifacts from trusted KoopCare sources;
- keep the scikit-learn runtime compatible with the artifact;
- do not silently replace the artifact without rerunning tests and updating docs;
- keep final financing decisions under human officer review.

## 2. Run with Docker Compose

From the repository root:

```powershell
docker compose up --build
```

The first build can take several minutes because the scientific Python and
XGBoost dependencies are large.

The compose file still mounts:

```text
./models -> /app/models
```

as read-only:

```text
./models:/app/models:ro
```

This lets developers replace `models/best_model.pkl` locally for controlled
testing without changing the Dockerfile.

## 3. Run with Docker Directly

Build:

```powershell
docker build -t koopcare-mlops-credit-scoring-api .
```

Run:

```powershell
docker run --rm -p 8000:8000 koopcare-mlops-credit-scoring-api
```

The Docker command uses:

```text
PORT first
API_PORT second
8000 fallback
```

This makes the same image compatible with public platforms that inject `PORT`.

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

## 5. Expected Model Status

With the committed `models/best_model.pkl` artifact, `/model-info` should return:

```text
model_loaded: true
artifact_status: available
metadata_source: artifact
```

If the artifact is intentionally removed or replaced incorrectly:

```text
/health can still work
/model-info reports missing or invalid artifact
/predict returns HTTP 503
```

## 6. Railway Public Deployment

The repository includes:

```text
railway.toml
```

Railway should build from:

```text
Dockerfile
```

After Railway gives a public URL, verify it from project 14:

```powershell
npm run verify:ml-api -- https://your-ml-api-url
```

Then connect project 14 by setting:

```text
ML_API_BASE_URL=https://your-ml-api-url
```

See:

```text
docs/public_deployment.md
```

## 7. Stop the Container

```powershell
docker compose down
```

## 8. Rebuild After Dependency Changes

If `requirements.txt` changes:

```powershell
docker compose build --no-cache
docker compose up
```

## 9. Verified Local Docker Runtime

The Docker setup has been verified locally with the current `models/best_model.pkl`
artifact:

```text
GET /health      -> status ok
GET /model-info  -> artifact_status available
POST /predict    -> LAYAK / MEDIUM for the documented example payload
```

## 10. Notes for FE/BE/Mobile Teams

Use Docker when you need a stable local API base URL:

```text
http://127.0.0.1:8000
```

For public integration, use the deployed Railway URL instead.

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
