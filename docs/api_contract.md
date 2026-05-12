# KoopCare ML Inference API Contract

## Purpose

This API will provide machine learning inference for KoopCare credit scoring decision support.

The API must not make final financing decisions. It only returns AI recommendations for cooperative officer review.

## Base URL

Local development:

```text
http://127.0.0.1:8000
```

## Endpoint Status

### GET /health

Status: implemented.

Checks whether the API service is running and whether the local model artifact exists.

Example response before `models/best_model.pkl` is available:

```json
{
  "status": "ok",
  "service": "KoopCare ML Inference API",
  "environment": "development",
  "model_loaded": false,
  "model_path": "models/best_model.pkl"
}
```

### GET /model-info

Status: implemented.

Returns configured model metadata and local model artifact availability.

Example response before `models/best_model.pkl` is available:

```json
{
  "model_loaded": false,
  "model_name": "XGBoost",
  "model_version": "koopcare-xgboost-v1",
  "model_path": "models/best_model.pkl",
  "threshold": 0.6660796,
  "features_count": 25,
  "artifact_status": "missing",
  "metadata_source": "configuration",
  "note": "Model artifact is not available yet. Copy best_model.pkl into models/ before enabling prediction."
}
```

### POST /predict

Status: planned.

Runs credit risk prediction.

Planned request:

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
  "days_employed": -2329,
  "days_last_phone_change": -1740.0,
  "ext_source_1": 0.5,
  "ext_source_2": 0.6,
  "ext_source_3": 0.4
}
```

Planned response:

```json
{
  "ai_recommendation": "LAYAK",
  "risk_level": "LOW",
  "prob_default": 0.2911,
  "threshold": 0.66608,
  "confidence": 0.56,
  "model_name": "XGBoost",
  "model_version": "koopcare-xgboost-v1",
  "human_review_required": true,
  "final_decision": null,
  "note": "AI recommendation only. Final financing decision must be reviewed and approved by cooperative officers."
}
```

## Label Meaning

The model predicts the probability of class 1.

```text
0 = non-default / lower risk / LAYAK
1 = default risk / higher risk / TIDAK_LAYAK
```

## Decision Rule

```text
if prob_default >= threshold:
    ai_recommendation = TIDAK_LAYAK
else:
    ai_recommendation = LAYAK
```

## Human Review

All predictions require cooperative officer review.

The API must not be used as an automatic loan approval or rejection system.

## Current Limitation

The current model direction is based on a prototype trained on Home Credit style data, not real BMT production data.

The current model artifact uses `EXT_SOURCE` features, which may not be available for unbankable BMT members. A production-ready BMT model should be retrained using cooperative-native features such as saving balance, member active duration, saving consistency, and repayment history.
