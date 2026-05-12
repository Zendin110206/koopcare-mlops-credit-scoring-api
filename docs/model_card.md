# KoopCare Credit Scoring Model Card

## Model Purpose

The model provides credit risk prediction for KoopCare, an AI-assisted decision-support system for BMT/cooperative financing workflows.

The model is intended to support cooperative officers by estimating whether a financing applicant has higher or lower default risk.

## Product Context

KoopCare is designed for BMT/cooperatives serving unbankable or underbanked communities.

The product principle is:

```text
AI recommends, cooperative officers decide.
```

## Current Dataset

The current prototype model is based on Home Credit style credit risk data.

This dataset is used as a learning and prototyping baseline because real BMT data is not yet available.

## Current Model Artifact

Artifact inspection during project audit shows:

```text
artifact file: best_model.pkl
model_name: XGBoost
threshold: 0.6660796
required_features: 25
```

## Label Meaning

```text
0 = non-default / lower risk
1 = default risk / higher risk
```

## Main Feature Groups

The prototype model uses demographic, financial, employment, ownership, and engineered credit-risk features.

Examples:

- income type
- education type
- family status
- occupation type
- ownership of car/property
- income amount
- credit amount
- annuity amount
- age
- employment duration
- external source scores
- debt to income ratio
- payment rate

## Important Limitation

The prototype model currently uses `EXT_SOURCE_1`, `EXT_SOURCE_2`, and `EXT_SOURCE_3`.

These features are strong in the Home Credit dataset but may conflict with KoopCare's unbankable-user mission because real BMT members may not have formal external credit scores.

For production BMT deployment, the model should be retrained using BMT-native features such as:

- saving balance
- member active months
- saving consistency score
- previous loan count
- repayment history score
- late payment count
- warning count

## Intended Use

This model may be used for:

- prototype credit scoring demo
- API integration learning
- decision-support workflow simulation
- portfolio-level MLOps demonstration

## Not Intended For

This model must not be used for:

- automatic loan approval
- automatic loan rejection
- real BMT production decisions without validation
- decisions without cooperative officer review

## Human-in-the-loop Requirement

All predictions require human review.

The API response must clearly state that final decision-making belongs to cooperative officers.
