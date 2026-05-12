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
  "artifact_keys": [],
  "artifact_error": null,
  "metadata_source": "configuration",
  "note": "Model artifact is not available yet. Copy best_model.pkl into models/ before enabling prediction."
}
```

Artifact status meaning:

- `missing`: configured artifact path does not exist yet
- `available`: artifact exists, can be loaded, and contains required keys
- `invalid`: artifact exists but cannot be loaded or does not match the expected structure

Expected artifact keys:

```text
features
model
preprocessor
threshold
```

Optional artifact key:

```text
model_name
```

### POST /predict

Status: planned endpoint. Request/response schemas, feature mapping, and decision helpers are implemented.

Runs credit risk prediction. The endpoint itself is not active yet.

Prepared request schema:

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
  "days_employed": -2329.0,
  "days_last_phone_change": -1740.0,
  "ext_source_1": 0.5,
  "ext_source_2": 0.6,
  "ext_source_3": 0.4
}
```

Prepared response schema:

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

Notes:

- `days_birth` must be a negative Home Credit style day offset.
- `days_last_phone_change` must be less than or equal to `0`.
- `ext_source_1`, `ext_source_2`, and `ext_source_3` are optional and must be between `0` and `1` when provided.
- `flag_own_car` and `flag_own_realty` currently accept `Y` or `N`.

Prepared model feature columns:

```text
CODE_GENDER
NAME_INCOME_TYPE
NAME_EDUCATION_TYPE
NAME_FAMILY_STATUS
OCCUPATION_TYPE
FLAG_OWN_CAR
FLAG_OWN_REALTY
CNT_CHILDREN
CNT_FAM_MEMBERS
AMT_INCOME_TOTAL
AMT_CREDIT
AMT_ANNUITY
AMT_GOODS_PRICE
DAYS_EMPLOYED
DAYS_LAST_PHONE_CHANGE
AGE_YEARS
DAYS_EMPLOYED_ANOM
EXT_SOURCE_1
EXT_SOURCE_2
EXT_SOURCE_3
EXT_SOURCE_MEAN
EXT_SOURCE_MIN
EXT_SOURCE_PROD
DEBT_TO_INCOME
PAYMENT_RATE
```

Prepared derived feature rules:

- `AGE_YEARS = abs(days_birth) / 365`
- `DAYS_EMPLOYED_ANOM = 1` when `days_employed == 365243`, otherwise `0`
- anomalous `DAYS_EMPLOYED = 365243` is replaced with missing value
- `EXT_SOURCE_MEAN` is the mean of external source scores
- `EXT_SOURCE_MIN` is the minimum of external source scores
- `EXT_SOURCE_PROD` is the product of external source scores
- `DEBT_TO_INCOME = amt_credit / (amt_income_total + 1)`
- `PAYMENT_RATE = amt_annuity / (amt_credit + 1)`

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

Prepared risk level rule:

```text
if prob_default >= threshold:
    risk_level = HIGH
elif prob_default >= threshold * 0.75:
    risk_level = MEDIUM
else:
    risk_level = LOW
```

Prepared confidence rule:

```text
confidence = abs(prob_default - threshold) / max(threshold, 1 - threshold)
```

The returned confidence is capped at `1.0` and rounded in the prediction response.

## Human Review

All predictions require cooperative officer review.

The API must not be used as an automatic loan approval or rejection system.

## Current Limitation

The current model direction is based on a prototype trained on Home Credit style data, not real BMT production data.

The current model artifact uses `EXT_SOURCE` features, which may not be available for unbankable BMT members. A production-ready BMT model should be retrained using cooperative-native features such as saving balance, member active duration, saving consistency, and repayment history.
