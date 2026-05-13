# KoopCare Team Integration Contract

This document explains how backend, frontend, and mobile teams should integrate with the KoopCare ML inference API.

It focuses on safe API usage, stable request/response expectations, and how teams should react when the ML model changes.

## 1. Current Integration Status

Current available endpoints:

```text
GET /
GET /health
GET /model-info
POST /predict
GET /docs
```

Base URL for local development:

```text
http://127.0.0.1:8000
```

The endpoint used by product clients is:

```text
POST /predict
```

## 2. Recommended Client Flow

Before submitting prediction requests, backend or QA should check:

```text
GET /health
GET /model-info
```

Use `/health` to confirm the API process is running.

Use `/model-info` to confirm the model artifact is available and valid.

Only treat prediction as ready when `/model-info` returns:

```text
model_loaded: true
artifact_status: available
metadata_source: artifact
```

## 3. Backend Responsibility

The backend should:

- own authentication and user/session context;
- build the request payload for `/predict`;
- call the ML API;
- store the AI recommendation if product requirements need it;
- keep the final financing decision outside the ML API;
- handle ML API error statuses safely.

The backend should not:

- treat `LAYAK` as automatic approval;
- treat `TIDAK_LAYAK` as automatic rejection;
- bypass cooperative officer review;
- send incomplete or guessed values just to satisfy the schema.

## 4. Frontend and Mobile Responsibility

Frontend and mobile apps should:

- collect only fields required by the current backend flow;
- show AI output as recommendation, not final decision;
- display risk and probability carefully;
- avoid wording that suggests automatic approval or rejection;
- handle loading and error states clearly.

Recommended user-facing wording:

```text
Rekomendasi AI
```

Avoid wording like:

```text
Keputusan final AI
```

The final decision belongs to cooperative officers.

## 5. Current POST /predict Request Fields

Current request fields:

```text
code_gender
name_income_type
name_education_type
name_family_status
occupation_type
flag_own_car
flag_own_realty
cnt_children
cnt_fam_members
amt_income_total
amt_credit
amt_annuity
amt_goods_price
days_birth
days_employed
days_last_phone_change
ext_source_1
ext_source_2
ext_source_3
```

Important:

The current model artifact still expects `EXT_SOURCE` fields.

If the ML team retrains the model without `EXT_SOURCE`, this request contract may change.

Do not remove frontend/backend fields until the API contract and model artifact are updated together.

## 6. Current POST /predict Response Fields

Current response fields:

```text
ai_recommendation
risk_level
prob_default
threshold
confidence
model_name
model_version
human_review_required
final_decision
note
```

Client interpretation:

- `ai_recommendation` is the AI recommendation.
- `risk_level` is a simplified risk band.
- `prob_default` is the probability of default risk.
- `threshold` is the model cutoff.
- `confidence` is distance from threshold, not model accuracy.
- `human_review_required` should remain true.
- `final_decision` should remain null in this API.
- `note` contains the decision-support disclaimer.

## 7. Error Handling Contract

Clients should handle these statuses:

```text
200 prediction success
422 invalid request body
503 model missing or invalid
500 prediction runtime failure
```

Recommended handling:

- `422`: fix payload validation or form mapping.
- `503`: block prediction flow and show that ML service/model is not ready.
- `500`: show technical failure and ask user to retry later or contact support.

Do not show raw internal stack traces to end users.

## 8. Model Retraining Impact

The ML team may retrain the model.

Retraining can be low-impact or high-impact.

Low-impact change:

```text
same request fields
same feature list
same probability class order
new model weights or threshold
```

High-impact change:

```text
new request fields
removed EXT_SOURCE fields
different feature list
different preprocessing
different class order
different model output shape
```

High-impact changes require coordination with:

- ML/API owner;
- backend team;
- frontend team;
- mobile team;
- QA/tester;
- product or cooperative domain reviewer.

## 9. EXT_SOURCE Coordination

The current prototype depends on:

```text
ext_source_1
ext_source_2
ext_source_3
```

These may not be available for real BMT members.

If these fields are removed in a retrained model, do not only update the model artifact.

Also update:

- `PredictionRequest`;
- `build_model_feature_frame(...)`;
- request examples;
- Postman collection;
- frontend form;
- backend payload builder;
- mobile screen;
- API contract;
- tests.

## 10. Integration Readiness Checklist

Before FE/BE/mobile teams use a new API version:

- `/health` returns `status: ok`;
- `/model-info` returns `artifact_status: available`;
- `/predict` succeeds with the documented example;
- Postman collection is updated;
- API contract is updated;
- model card is updated;
- request fields are confirmed with backend/frontend/mobile;
- error behavior is tested;
- human-review wording is preserved.

## 11. Product Safety Rule

Every consuming app must preserve this rule:

```text
AI recommends, cooperative officers decide.
```

Do not design UI or backend automation that converts `LAYAK` or `TIDAK_LAYAK` into final financing decisions without officer review.
