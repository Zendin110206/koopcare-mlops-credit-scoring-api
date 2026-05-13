# Express Backend Adapter Example

This folder contains reference code for integrating the KoopCare Express backend with the KoopCare ML inference API.

It is intentionally kept as an example, not as production code copied directly into another repository without review.

Recommended integration flow:

```text
React admin / Flutter mobile
-> Express backend
-> FastAPI ML API
```

Do not make the frontend or mobile app call the ML API directly for the main product flow.

## Files

```text
mlScoringClient.js
loanAiMapping.js
exampleLoanIntegration.js
```

## Environment Variable

In the Express backend, define:

```text
ML_API_BASE_URL=http://127.0.0.1:8000
```

If the Express backend runs inside Docker and the ML API runs on the host laptop:

```text
ML_API_BASE_URL=http://host.docker.internal:8000
```

If both services are inside the same Docker Compose network:

```text
ML_API_BASE_URL=http://ml-api:8000
```

## Required ML API Endpoints

```text
GET /health
GET /model-info
POST /predict
```

Before treating prediction as ready, the backend should check:

```text
GET /model-info
```

and expect:

```text
model_loaded: true
artifact_status: available
metadata_source: artifact
```

## Important Score Meaning

The current admin repository uses:

```text
ai_score 0-100
higher score = more eligible
```

The ML API returns:

```text
prob_default 0-1
higher probability = higher default risk
```

Do not store `prob_default * 100` as `ai_score`, because that reverses the meaning.

If the admin UI still needs a display score where higher means more eligible, use:

```text
eligibility_score = round((1 - prob_default) * 100)
```

Prefer storing the full ML response instead:

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

## Example Backend Usage

```js
import { predictCreditRisk } from './mlScoringClient.js';
import {
  buildPredictionPayload,
  buildLoanAiAssessmentRecord,
} from './loanAiMapping.js';

const requestPayload = buildPredictionPayload(applicationData);
const prediction = await predictCreditRisk(requestPayload);
const aiAssessment = buildLoanAiAssessmentRecord({
  loanId,
  requestPayload,
  prediction,
});
```

The backend should save `aiAssessment` into a loan AI assessment table or equivalent columns.

## Current Limitation

The current ML API contract still follows the prototype model artifact and requires Home Credit style fields, including:

```text
ext_source_1
ext_source_2
ext_source_3
```

For production BMT usage, the model should be retrained with cooperative-native features. When that happens, update the API schema, backend payload builder, frontend/mobile forms, tests, and documentation together.

