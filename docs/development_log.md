# Development Log

## 2026-05-12

### Goal

Prepare a professional MLOps/API repository for KoopCare credit scoring model integration.

### Current Context

KoopCare is an AI-assisted credit scoring decision-support system for BMT/cooperative financing workflows.

The current role focus is ML Ops and ML integration:

- prepare inference API
- load trained model artifact
- preserve preprocessing parity
- define request and response schema
- document model limitations
- support web/mobile/backend integration

### Work Completed

- Created initial API project structure.
- Prepared virtual environment with Python 3.12.5.
- Added base dependency list.
- Audited KoopCare context from WhatsApp chats, PDFs, and GitHub repositories.
- Identified model artifact mismatch between older README assumptions and actual artifact inspection.
- Confirmed the current model direction should follow the XGBoost artifact and threshold around `0.6660796`.
- Initialized Git repository and connected it to the public GitHub repository.
- Implemented the first FastAPI endpoints: `GET /` and `GET /health`.
- Added a basic test suite for the root and health endpoints.
- Implemented `GET /model-info` for configured model metadata and local artifact status.
- Added a response schema for model metadata.
- Added service-layer logic for model metadata so model-related logic does not stay inside `main.py`.
- Added prediction request and response schemas.
- Added schema validation tests for valid payloads, ownership flags, external source ranges, birth-day offsets, and human review defaults.
- Added feature engineering mapper from `PredictionRequest` into the 25 model feature columns expected by the XGBoost artifact.
- Added feature engineering tests for raw field mapping, derived feature calculations, employment anomaly handling, and missing external source values.
- Added safe model artifact metadata inspection for `best_model.pkl`.
- Added artifact metadata tests for missing, valid, and invalid artifact scenarios.
- Added prediction decision helpers for recommendation, risk level, confidence, and response construction.
- Added decision helper tests for threshold boundaries and invalid probability values.
- Downloaded the trusted local `best_model.pkl` artifact for runtime verification.
- Identified and fixed artifact compatibility by pinning `scikit-learn==1.6.1`.
- Added full model artifact loading with validation for model, preprocessor, feature order, and threshold.
- Added model loading tests for runtime components and invalid artifact structures.
- Made endpoint tests independent from local model artifact presence.
- Added prediction inference service method that connects feature engineering, preprocessing, model probability, and response construction.
- Added prediction inference tests for successful `LAYAK` and `TIDAK_LAYAK` responses, invalid probability shape, invalid probability value, and transform failures.
- Verified the local `best_model.pkl` artifact can produce a decision-support response from the example payload.
- Implemented `POST /predict` endpoint for HTTP prediction inference.
- Added endpoint-level error handling for missing artifact, invalid artifact, and prediction runtime failure.
- Added endpoint tests for successful prediction, missing model, invalid model, failed inference, and invalid request validation.
- Verified `POST /predict` through a local HTTP request using the real `best_model.pkl` artifact.
- Added prediction usage examples with PowerShell, curl, expected response, validation error examples, and model artifact error examples.
- Added a Postman collection for root, health, model-info, prediction, and invalid-request validation flows.
- Added documentation asset tests to make sure the Postman collection stays valid JSON and continues documenting the core endpoints.
- Added a model handoff contract for retrained artifacts, dependency compatibility, feature order, threshold, and `EXT_SOURCE` migration.
- Added a team integration contract for backend, frontend, and mobile teams using the prediction API safely.

### Key Technical Decision

The API implementation should follow the actual model artifact instead of outdated README assumptions.

The first implemented endpoint is `/health` because it proves that the API can run before adding model loading complexity.

The `/model-info` endpoint began as a configuration-only endpoint, then evolved into safe artifact validation. It now reports artifact metadata when `best_model.pkl` is available and valid, and falls back to configuration metadata when the artifact is missing or invalid.

The prediction schemas are prepared before the `/predict` endpoint so the API contract is explicit before model inference is added.

The feature engineering mapper is prepared before model loading so prediction input can be converted into the exact column order expected by the model artifact.

The model metadata endpoint now attempts to read artifact metadata when `best_model.pkl` exists, but it falls back safely to configuration metadata when the artifact is missing or invalid.

Prediction decision helpers are prepared before the prediction endpoint so probability-to-decision logic can be tested independently from model inference.

The current pickle artifact requires dependency compatibility. The artifact failed under `scikit-learn 1.8.0` and loaded successfully after pinning the environment to `scikit-learn 1.6.1`, which matches the version used when the artifact was created.

Model loading now validates runtime readiness:

- `model.predict_proba(...)` must exist
- `preprocessor.transform(...)` must exist
- feature names must match the expected 25 columns in order
- threshold must be between `0` and `1`

Prediction inference was implemented in the service layer before exposing the HTTP endpoint. This kept the riskiest ML path testable before request routing and HTTP error handling were added.

The prediction endpoint is now a thin HTTP wrapper around the service layer. FastAPI handles request validation, while the endpoint translates ML/runtime errors into explicit HTTP errors.

After the progress 01-10 review, the binary `predict_proba(...)` validation was tightened so the service only accepts exactly two probability columns: class 0 and class 1. This prevents a future multiclass artifact from being interpreted incorrectly as a binary default-risk model.

Prediction usage examples and the Postman collection were added after the endpoint was implemented so the examples match the real API behavior instead of documenting a planned contract too early.

The model handoff and team integration contracts were added because the ML model may be retrained. A retrained model can affect artifact structure, feature order, request fields, frontend/mobile forms, backend payload mapping, and documentation. Model replacement must therefore be deliberate, validated, and coordinated.

### Next Steps

- Add Dockerfile for reproducible local serving.
- Add GitHub Actions for automated tests on push.
- Update API/request examples when the retrained model contract changes.
- Push implementation in small, explainable commits.
