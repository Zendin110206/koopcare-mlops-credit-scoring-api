# KoopCare Prediction Usage Examples

This document explains how to run and test the KoopCare ML inference API after the `POST /predict` endpoint is available.

Use this guide when you want to:

- run the API locally;
- check whether the model artifact is available;
- send a prediction request;
- understand the prediction response;
- test common error responses;
- import the Postman collection.

## 1. Prerequisites

Run all commands from the repository root:

```text
<repo-root>
```

Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Copy the environment template:

```powershell
Copy-Item .env.example .env
```

Download the local model artifact when you want `/predict` to run real inference:

```powershell
Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/AdityaNugrahaPS/KoopCare-EDA/main/best_model.pkl" `
  -OutFile ".\models\best_model.pkl"
```

The model artifact stays local and is ignored by git.

## 2. Start the API

Run:

```powershell
uvicorn src.main:app --reload
```

Default local base URL:

```text
http://127.0.0.1:8000
```

Open FastAPI Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Docker alternative:

```powershell
docker compose up --build
```

See:

```text
docs/docker_usage.md
```

## 3. Check Service Health

Request:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
```

Example response:

```json
{
  "status": "ok",
  "service": "KoopCare ML Inference API",
  "environment": "development",
  "model_loaded": true,
  "model_path": "models/best_model.pkl"
}
```

Important note:

`model_loaded` in `/health` only checks whether the configured model path exists. Use `/model-info` to validate the artifact structure and runtime components.

## 4. Check Model Runtime Readiness

Request:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/model-info" -Method Get
```

Expected response when `models/best_model.pkl` is available and valid:

```json
{
  "model_loaded": true,
  "model_name": "XGBoost",
  "model_version": "koopcare-xgboost-v1",
  "model_path": "models/best_model.pkl",
  "threshold": 0.6660796,
  "features_count": 25,
  "artifact_status": "available",
  "artifact_keys": [
    "features",
    "model",
    "model_name",
    "preprocessor",
    "threshold"
  ],
  "artifact_error": null,
  "metadata_source": "artifact",
  "note": "Model artifact is available and runtime components were validated."
}
```

Only call `/predict` for real inference when:

```text
artifact_status = available
model_loaded = true
metadata_source = artifact
```

## 5. Send a Prediction Request

PowerShell request:

```powershell
$body = @'
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
'@

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/predict" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body |
  ConvertTo-Json -Depth 5
```

Equivalent curl request:

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## 6. Expected Prediction Response

With the current local `best_model.pkl` artifact, the documented example payload returns:

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

The exact probability can change if the model artifact changes.

The interpretation stays the same:

- `prob_default` is the model probability for class 1, meaning default risk.
- `threshold` is the cutoff used for the recommendation.
- `LAYAK` means `prob_default` is below the threshold.
- `TIDAK_LAYAK` means `prob_default` is greater than or equal to the threshold.
- `risk_level` is an interpretation band, not a final financing decision.
- `confidence` is based on distance from the threshold, not model accuracy.
- `human_review_required` must remain true.
- `final_decision` remains null because the cooperative officer makes the final decision outside this API.

## 7. Common Validation Error Example

Request with invalid ownership flag:

```powershell
$body = @'
{
  "code_gender": "M",
  "name_income_type": "Working",
  "name_education_type": "Secondary / secondary special",
  "name_family_status": "Married",
  "occupation_type": "Laborers",
  "flag_own_car": "INVALID",
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
'@

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/predict" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

Expected HTTP status:

```text
422 Unprocessable Entity
```

Reason:

```text
flag_own_car only accepts Y or N
```

## 8. Model Artifact Error Examples

If `models/best_model.pkl` is missing, `POST /predict` returns HTTP `503`:

```json
{
  "detail": {
    "error": "model_artifact_missing",
    "message": "Model artifact not found at models/best_model.pkl."
  }
}
```

If the artifact exists but is invalid, `POST /predict` returns HTTP `503`:

```json
{
  "detail": {
    "error": "model_artifact_invalid",
    "message": "Model artifact is missing required keys: model, preprocessor, threshold."
  }
}
```

If the artifact loads but runtime inference fails, `POST /predict` returns HTTP `500`:

```json
{
  "detail": {
    "error": "prediction_failed",
    "message": "Unable to generate prediction: transform failed"
  }
}
```

## 9. Postman Collection

The repository includes a Postman collection:

```text
postman/koopcare_ml_inference_api.postman_collection.json
```

Import it into Postman, then run these requests:

```text
GET {{base_url}}/
GET {{base_url}}/health
GET {{base_url}}/model-info
POST {{base_url}}/predict
POST {{base_url}}/predict with invalid ownership flag
```

Default collection variable:

```text
base_url = http://127.0.0.1:8000
```

## 10. Operational Notes

Before showing a demo:

1. Activate `.venv`.
2. Install dependencies from `requirements.txt`.
3. Ensure `models/best_model.pkl` exists locally.
4. Run `uvicorn src.main:app --reload`.
5. Open `/model-info` and confirm `artifact_status` is `available`.
6. Run `/predict` with the example payload.
7. Explain that the model is prototype decision support, not an automatic approval system.

## 11. Current Limitation

The current model is trained on Home Credit style data, not real BMT production data.

The request still includes `EXT_SOURCE` fields because the current prototype artifact expects them.

For production BMT deployment, the model should be retrained using cooperative-native features such as saving balance, member active duration, saving consistency, previous financing history, and repayment behavior.

If a retrained model changes the required request fields, update the API contract, Postman collection, and integration notes before FE/BE/mobile teams consume the new behavior.

Related documents:

```text
docs/model_handoff_contract.md
docs/team_integration_contract.md
```
