# KoopCare Model Handoff Contract

This document defines the minimum handoff contract between the ML training work and the KoopCare ML inference API.

Use this document when:

- the ML team retrains the model;
- the model artifact changes;
- the feature list changes;
- `EXT_SOURCE` features are removed or replaced;
- the API needs to verify a new `best_model.pkl`;
- backend, frontend, or mobile teams need to know whether a new model is safe to integrate.

## 1. Current Runtime Artifact

The current API expects a local model artifact:

```text
models/best_model.pkl
```

The artifact is ignored by git and must be prepared locally.

Current inspected artifact:

```text
model_name: XGBoost
threshold: 0.6660796
features_count: 25
model type: XGBClassifier
preprocessor type: ColumnTransformer
```

The current artifact was verified with:

```text
scikit-learn==1.6.1
xgboost==3.2.0
```

## 2. Required Artifact Shape

The artifact must be loadable with `joblib.load(...)`.

The artifact must be a dictionary with these required keys:

```text
features
model
preprocessor
threshold
```

Optional key:

```text
model_name
```

The API validates this at runtime.

If a new artifact does not match the expected contract, `/model-info` returns `artifact_status: "invalid"` and `/predict` returns HTTP `503`.

## 3. Required Runtime Methods

The artifact value under `model` must provide:

```text
predict_proba(...)
```

The artifact value under `preprocessor` must provide:

```text
transform(...)
```

The API uses:

```text
preprocessor.transform(model_input)
model.predict_proba(transformed_input)
```

The model must behave as binary classification.

The API expects `predict_proba(...)` to return exactly two probability columns:

```text
class 0 = non-default / lower risk
class 1 = default risk / higher risk
```

## 4. Feature Contract

The current API validates that artifact `features` exactly matches the feature order expected by the API.

Current feature columns:

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

Feature order matters.

If a retrained model changes the feature list, the API code must be updated deliberately.

Do not silently replace `models/best_model.pkl` with an artifact that expects a different feature set.

## 5. Threshold Contract

The artifact must include:

```text
threshold
```

The threshold must be a number between:

```text
0 and 1
```

The API decision rule is:

```text
prob_default >= threshold -> TIDAK_LAYAK
prob_default < threshold  -> LAYAK
```

If the model team changes threshold selection logic, document the reason in the model card or release note before integration.

## 6. Dependency Contract

The model team must provide the training/runtime dependency versions used to create the artifact.

At minimum:

```text
python
scikit-learn
xgboost
pandas
numpy
joblib
```

Why this matters:

Pickle/joblib artifacts can fail when library versions are different between training and serving.

The current artifact failed under a newer scikit-learn version and loaded successfully after pinning:

```text
scikit-learn==1.6.1
```

## 7. Retrained Model Handoff Checklist

Before a retrained model is accepted into this API, the ML team should provide:

- artifact file name;
- model type;
- label meaning;
- probability class order;
- selected threshold;
- expected feature list in order;
- preprocessing object or exact preprocessing steps;
- training dataset source;
- validation metrics;
- limitations;
- dependency versions;
- sample input row;
- expected prediction output for the sample input.

The API side should then verify:

- `joblib.load(...)` succeeds;
- required keys exist;
- feature order matches API mapping;
- preprocessor has `transform(...)`;
- model has `predict_proba(...)`;
- probability output has exactly two columns;
- `/model-info` returns `artifact_status: "available"`;
- `/predict` succeeds with the documented example payload or an updated payload;
- tests pass.

## 8. EXT_SOURCE Migration Note

The current prototype uses:

```text
EXT_SOURCE_1
EXT_SOURCE_2
EXT_SOURCE_3
```

These fields are useful in the Home Credit dataset but may not exist for real BMT or cooperative members.

If the ML team retrains a model without `EXT_SOURCE` features, the API request schema and feature engineering mapper will likely need to change.

Potential BMT-native replacement feature groups:

- saving balance;
- member active duration;
- saving consistency;
- previous financing history;
- repayment behavior;
- late payment count;
- officer warning count;
- cooperative transaction activity.

Removing `EXT_SOURCE` is not just a model change.

It can affect:

- `PredictionRequest`;
- `build_model_feature_frame(...)`;
- `MODEL_FEATURE_COLUMNS`;
- request examples;
- Postman collection;
- frontend form fields;
- backend payload builder;
- mobile input form;
- tests;
- API contract;
- model card.

## 9. Safe Integration Rule

Use this rule for every retrained artifact:

```text
No silent model replacement.
```

Every retrained model must go through:

```text
artifact inspect
-> dependency check
-> feature contract check
-> local inference check
-> tests
-> documentation update
-> commit
-> push
```

If the new model changes request fields, coordinate with backend, frontend, and mobile teams before changing `/predict`.

## 10. Recommended Versioning

Use a clear model version label:

```text
koopcare-xgboost-v1
koopcare-xgboost-v2
koopcare-bmt-native-v1
```

When the model changes, update:

- `.env.example`;
- `docs/model_card.md`;
- `docs/api_contract.md`;
- `docs/prediction_usage_examples.md`;
- `models/README.md`;
- `README.md`;
- tests if request/feature behavior changes.

## 11. Decision Support Requirement

Every model version must preserve the product rule:

```text
AI recommends, cooperative officers decide.
```

The API must continue returning:

```text
human_review_required: true
final_decision: null
```

Final financing approval or rejection must remain outside the AI API.
