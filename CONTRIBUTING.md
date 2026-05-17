# KoopCare MLOps Contribution Workflow

This repository is used as a public portfolio-quality MLOps project. Keep every
change small, reviewable, and consistent with the API contract.

## Working Principles

- Prefer small checkpoints over large mixed changes.
- Keep source code, docs, tests, Docker, and deployment notes consistent.
- Do not silently replace `models/best_model.pkl`.
- Do not commit `.env`, virtual environments, cache folders, private local
  notes, raw datasets, or generated reports.
- Keep the product principle explicit:

```text
AI recommends, cooperative officers decide.
```

## Branches

Use a focused branch name:

```text
feature/<short-scope>
fix/<short-scope>
docs/<short-scope>
chore/<short-scope>
```

Examples:

```text
feature/readiness-endpoint
fix/external-source-feature-edge-case
docs/railway-deployment-guide
```

## Commit Style

Use conventional commits with a scope:

```text
type(scope): short imperative summary
```

Recommended types:

```text
feat
fix
docs
test
ci
chore
refactor
```

Examples:

```text
fix(features): preserve missing external source products
docs(deployment): clarify Railway public URL checks
test(docker): validate Railway config as TOML
```

Avoid vague commits:

```text
update
fix bug
final
chore: changes
```

## Pull Request Checklist

Before opening or merging a PR:

```powershell
python -m compileall -q src tests
python -m pip check
python -m pytest
```

If deployment files changed, also review:

```text
Dockerfile
docker-compose.yml
railway.toml
docs/docker_usage.md
docs/public_deployment.md
docs/railway_variables.md
```

If model input, output, or artifact behavior changed, also update:

```text
docs/api_contract.md
docs/model_handoff_contract.md
docs/prediction_usage_examples.md
postman/koopcare_ml_inference_api.postman_collection.json
examples/express_backend_adapter/
```

## Model Artifact Rule

The current committed artifact is approved only for the public portfolio demo
checkpoint:

```text
models/best_model.pkl
```

Any replacement must be treated as a contract change. Validate:

- artifact keys;
- feature order;
- request fields;
- preprocessing compatibility;
- `predict_proba` class order;
- threshold;
- dependency versions;
- documentation and integration examples.

Follow:

```text
docs/model_handoff_contract.md
```

## PR Scope Guidance

Good PR scope:

```text
one bug fix + tests
one documentation consistency update
one endpoint + tests + docs
one deployment config update + verification notes
```

Risky PR scope:

```text
model replacement + API schema change + deployment + backend integration + docs
```

Split risky work into checkpoints so reviewers can reason about each change.
