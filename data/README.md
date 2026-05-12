# Data Directory

This directory is reserved for local datasets used during development, validation, or manual testing.

Raw datasets are not committed to this repository because they may be large, sensitive, or subject to external dataset terms.

## Prototype Dataset

The current KoopCare prototype model direction is based on Home Credit Default Risk style data.

Reference:

```text
https://www.kaggle.com/competitions/home-credit-default-risk/data
```

## Production Direction

For real BMT deployment, the model should be retrained using cooperative-native data such as:

- member active duration
- saving balance
- saving consistency
- requested financing amount
- repayment history
- late payment count
- previous loan count
- warning count

## Privacy

Do not commit real member data, identity documents, phone numbers, addresses, or financing records into this repository.
