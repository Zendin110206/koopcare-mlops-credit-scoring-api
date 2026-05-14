# References Directory

This directory is reserved for project references that are safe to commit, such as public links, non-sensitive notes, and summarized research references.

Do not commit private chat exports, private team files, credentials, or documents that require permission.

## Main Public References

- KoopCare MLOps API repository: `https://github.com/Zendin110206/koopcare-mlops-credit-scoring-api`
- KoopCare model/EDA repository: `https://github.com/AdityaNugrahaPS/KoopCare-EDA`
- KoopCare admin web/backend repository: `https://github.com/sayafauzi/koopcare-admin`
- KoopCare mobile app repository: `https://github.com/Gzaa19/KoopCare`
- Home Credit Default Risk dataset page: `https://www.kaggle.com/competitions/home-credit-default-risk/data`

## Supporting Repositories Reviewed During Project Audit

These repositories were reviewed as project context, but they are not the
current source of truth for this API's runtime contract:

- `https://github.com/g0maruuuu/koopcare-model`
- `https://github.com/g0maruuuu/koopcare`
- `https://github.com/Suvalen/KoopCare`

## Current Integration Source of Truth

For the current phase, use these references in this order:

1. This MLOps API repository for the ML API contract and `/predict` behavior.
2. `AdityaNugrahaPS/KoopCare-EDA` for the current `best_model.pkl` artifact source.
3. `sayafauzi/koopcare-admin` for the Express backend, React admin, MySQL schema, and loan review workflow.
4. `Gzaa19/KoopCare` for the Flutter mobile UI prototype.

Current phase decisions:

- The team is not migrating to Supabase for the current phase.
- The admin/backend repository continues to use Express and MySQL.
- The current model artifact is treated as the integration artifact for now.
- A future retrained model may replace it later, but that is not a blocker for the current backend integration work.

## Notes

Private context files are kept outside Git tracking through `.gitignore`.
