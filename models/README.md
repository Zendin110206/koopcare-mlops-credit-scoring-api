# Models Directory

This directory stores local machine learning model artifacts used by the KoopCare ML inference API.

## Expected Artifact

The API expects this local file:

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

Runtime verification on 2026-05-12 confirmed:

```text
artifact keys: features, model, model_name, preprocessor, threshold
model type: XGBClassifier
preprocessor type: ColumnTransformer
```

## Expected Artifact Structure

The API expects `best_model.pkl` to be a trusted joblib/pickle artifact containing these keys:

```text
features
model
preprocessor
threshold
```

The artifact may also contain:

```text
model_name
```

Only use model artifacts from trusted KoopCare/team sources. Python pickle/joblib files can execute code during loading, so do not load unknown artifacts.

## Dependency Compatibility

The current artifact was serialized with scikit-learn 1.6.1.

Use the pinned project requirements before loading the model:

```powershell
pip install -r requirements.txt
```

If scikit-learn is too new, loading the pickle can fail even when the artifact file itself is correct.

## How to Prepare Locally

Download or copy `best_model.pkl` into this directory:

```text
models/best_model.pkl
```

PowerShell download command:

```powershell
Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/AdityaNugrahaPS/KoopCare-EDA/main/best_model.pkl" `
  -OutFile ".\models\best_model.pkl"
```

After the API implementation is ready, check the loaded model through:

```text
GET /model-info
```

## Important Notes

This model is a prototype trained on Home Credit style data, not real BMT production data.

The model is used as decision support only. Final financing decisions must remain under cooperative officer review.

If the ML team provides a retrained artifact, validate it against:

```text
docs/model_handoff_contract.md
```

Do not silently replace `models/best_model.pkl` with a retrained model that changes feature order, request fields, probability class order, or dependency requirements.
