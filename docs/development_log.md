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
- Added Docker support for reproducible local API serving. The first Docker checkpoint kept `best_model.pkl` outside the image, and the later approved public deployment checkpoint copies the trusted artifact into the production image.
- Added Docker asset tests for Dockerfile, `.dockerignore`, Compose model volume behavior, and Docker usage documentation.
- Added GitHub Actions CI for dependency validation, compile checks, and the full test suite on push and pull request.
- Added a reviewer quickstart guide so teammates, mentors, or portfolio reviewers can understand what is ready, what still needs the model artifact, and what is not deployed yet.
- Added CI asset tests so the workflow and reviewer runbook remain documented and testable.
- Added Express backend adapter examples for team handoff, including an ML API client, loan AI payload/response mapper, and example loan scoring integration function.
- Documented the score direction mismatch between the admin repository's `ai_score` concept and the ML API's `prob_default` output.
- Added tests that keep the backend adapter examples present and aligned with the integration contract.
- Updated GitHub Actions workflow actions to Node 24-compatible major versions after GitHub CI reported Node 20 action runtime deprecation warnings.
- Re-audited the team integration direction after the team confirmed the current phase will continue with Express backend and MySQL instead of Supabase.
- Clarified that mobile/admin product clients should call the Express backend, while the Express backend calls the FastAPI ML API.
- Added public reference links for the MLOps API, model artifact source, admin web/backend repository, and mobile app repository.

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

Docker support mounts `./models` into the Compose container as read-only for deliberate local artifact replacement/testing. For the approved public portfolio checkpoint, the production Docker image now also copies `models/best_model.pkl` so a public platform can run `/predict` without a manual volume or upload step.

GitHub Actions CI was added after local and Docker execution were stable. CI does not require `models/best_model.pkl`; the automated tests intentionally cover missing-model behavior and dummy artifact scenarios so the repository stays testable from a clean clone.

The Express backend adapter examples were added after auditing the admin repository integration gap. The admin repository already has a loan review flow and an `ai_score` concept, but the ML API returns `prob_default`, where a higher value means higher default risk. The example adapter therefore documents the safer storage approach: keep the full ML response and derive `eligibility_score = round((1 - prob_default) * 100)` only when a UI needs a score where higher means more eligible.

The CI workflow was updated from `actions/checkout@v4` and `actions/setup-python@v5` to Node 24-compatible major versions after GitHub Actions reported runtime deprecation warnings. This keeps the portfolio CI healthier for future reviewer runs.

The team integration audit after Progress 17 confirmed that the current
product architecture should remain:

```text
Flutter mobile / React admin
-> Express backend
-> MySQL and FastAPI ML API
```

For the current phase, the team is not migrating to Supabase and the model is
not being retrained in the near term. The current XGBoost artifact remains the
integration contract for now, while future model replacement remains covered by
the model handoff contract.

### Next Steps

- Coordinate with the backend team before applying the Express adapter example into the admin/backend repository.
- Start with a small backend Pull Request in `sayafauzi/koopcare-admin` for an ML API client and safe score mapping.
- Keep mobile/admin clients pointed at the Express backend, not directly at the ML API.
- Deploy the FastAPI ML API using the Dockerfile and `railway.toml`.
- Connect the fullstack demo service by setting `ML_API_BASE_URL` to the public ML API URL.
- Verify the public end-to-end flow with project 14 verification scripts.
- Update API/request examples when the retrained model contract changes.
- Push implementation in small, explainable commits.

## 2026-05-16

### Goal

Prepare the ML inference API for a real public demo path instead of a local-only
or fallback-only demo.

### Work Completed

- Confirmed the team allows the current prototype model artifact to be deployed
  for the public portfolio checkpoint.
- Updated `.gitignore` and `.dockerignore` so `models/best_model.pkl` remains
  the only model artifact intentionally included.
- Updated the Dockerfile so the production image copies
  `models/best_model.pkl`.
- Updated the Docker command and health check to respect platform-injected
  `PORT` first, then `API_PORT`, then `8000`.
- Added `railway.toml` so Railway can deploy the FastAPI service through the
  Dockerfile with `/health` as the deployment health check.
- Added `docs/public_deployment.md` as the beginner-safe public deployment
  handoff guide.
- Updated reviewer, Docker, model, prediction, Postman, and README guidance so
  docs no longer contradict the public deployment strategy.
- Updated asset tests so future edits cannot accidentally remove the public
  deployment contract.

### Key Decision

The project keeps the old missing-artifact and invalid-artifact safeguards, but
the approved public image now includes the trusted prototype artifact. This gives
the public demo a real trained-model path while still preserving clear error
handling for bad future replacements.

### Next Steps

- Deploy this repository as a Railway service.
- Copy the public ML API URL from Railway.
- Set project 14 `ML_API_BASE_URL` to that public ML API URL.
- Redeploy project 14.
- Verify the public chain:

```text
browser/user
-> project 14 public fullstack service
-> project 14 Express backend
-> project 13 public FastAPI ML API
-> models/best_model.pkl
```

## 2026-05-17

### Goal

Refresh the project 13 quality checkpoint after public deployment preparation
and tighten anything that could make the repository look inconsistent or less
professional as a portfolio MLOps project.

### Work Completed

- Added `CONTRIBUTING.md` with branch, commit, PR, validation, and model
  artifact replacement rules.
- Updated `README.md` so the project tree includes `CONTRIBUTING.md`,
  `.dockerignore`, `.gitattributes`, `railway.toml`, and the public checkpoint
  docs folder.
- Updated README endpoint examples so the first documented path matches the
  current public-ready state where `models/best_model.pkl` is committed and
  `/model-info` reports `artifact_status: available`.
- Kept the missing-artifact response documented as a fallback case instead of
  presenting it as the default current state.
- Fixed an external-source feature engineering edge case so all-missing
  `EXT_SOURCE_1`, `EXT_SOURCE_2`, and `EXT_SOURCE_3` stay unknown instead of
  producing a misleading product value.
- Added tests for the all-missing external source edge case.
- Added an in-memory validated artifact cache so `/model-info` and `/predict`
  do not repeatedly reload the same pickle file on every request.
- Keyed the artifact cache by resolved path, modified timestamp, and file size
  so a deliberate model replacement can be reloaded after the file metadata
  changes.
- Added a cache behavior test around `load_model_artifact(...)`.
- Parsed `railway.toml` with Python `tomllib` in tests so Railway config changes
  are validated structurally, not only by string matching.
- Added documentation tests that keep the contribution workflow visible.

### Key Decision

The current source layout is still acceptable for this API. The largest source
file is the model service layer, and it remains under 300 lines. No large
frontend-style component or ribuan-baris file exists in project 13. A split can
be considered later if the model service gains multiple artifacts, caching, or
monitoring, but forcing a premature refactor now would add risk without a clear
benefit.

### Next Steps

- Deploy the current Railway service manually and verify `/health`,
  `/model-info`, and `/predict` on the public URL.
- Keep future commits scoped and use `type(scope): summary` consistently.
- If model serving grows, consider adding a dedicated readiness endpoint,
  request tracing, and model performance monitoring as separate checkpoints.
