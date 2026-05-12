# Models Directory

This directory stores local machine learning model artifacts used by the KoopCare ML inference API.

## Expected Artifact

The planned API expects this local file:

```text
models/best_model.pkl
```

The model artifact is not committed by default because model files are generated artifacts and may require separate permission from the model owner or project team.

## Current Prototype Model

The current prototype model comes from the KoopCare EDA/model repository:

```text
https://github.com/AdityaNugrahaPS/KoopCare-EDA
```

Based on artifact inspection during project audit, the current `best_model.pkl` contains:

```text
model_name: XGBoost
threshold: 0.6660796
required_features: 25
```

## How to Prepare Locally

Download or copy `best_model.pkl` into this directory:

```text
models/best_model.pkl
```

After the API implementation is ready, check the loaded model through:

```text
GET /model-info
```

## Important Notes

This model is a prototype trained on Home Credit style data, not real BMT production data.

The model is used as decision support only. Final financing decisions must remain under cooperative officer review.
