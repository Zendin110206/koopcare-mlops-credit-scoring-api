# Postman Directory

This directory contains API testing assets for the KoopCare ML Inference API.

## Available Collection

```text
koopcare_ml_inference_api.postman_collection.json
```

Import this file into Postman and keep the default collection variable:

```text
base_url = http://127.0.0.1:8000
```

## Included Requests

- `GET /health`
- `GET /model-info`
- `POST /predict`
- `POST /predict` with an invalid ownership flag for validation testing

## Before Running the Collection

Start the local API:

```powershell
uvicorn src.main:app --reload
```

For `POST /predict`, ensure the model artifact exists:

```text
models/best_model.pkl
```

For the approved public portfolio checkpoint, this artifact is committed in the
repository so local, Docker, and public demos can run real inference.
