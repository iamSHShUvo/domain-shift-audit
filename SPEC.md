# Specification: Domain Shift Audit

This spec is written before the code. Each acceptance criterion (AC) maps to a
GitHub Issue and is covered by a test.

## Users

A medical physicist or researcher who wants a quick check of whether imaging
features from a new hospital differ from a reference cohort.

## Input format

A CSV file with:
- a column named `cohort` whose values are exactly `source` or `target`
- one or more numeric feature columns
- at least 5 rows per cohort

## Functional requirements

### FR1: Upload and validate
- AC1.1: `POST /api/audits` accepts a CSV file upload.
- AC1.2: If the `cohort` column is missing, the API returns HTTP 400 with a clear message.
- AC1.3: If `source` or `target` has fewer than 5 rows, the API returns HTTP 400.
- AC1.4: If there are no numeric feature columns, the API returns HTTP 400.
- AC1.5: On any validation error, nothing is stored.

### FR2: Audit computation
- AC2.1: For each numeric feature, run a two-sided Mann-Whitney U test between `source` and `target`.
- AC2.2: Correct p-values with Benjamini-Hochberg FDR. A feature is significant if q < 0.05.
- AC2.3: Fold change = mean(target) / mean(source). If mean(source) is 0, fold change is null.
- AC2.4: Features with constant values across all rows are skipped.
- AC2.5: Verdict is `HIGH_DRIFT` if at least 30% of tested features are significant, otherwise `LOW_DRIFT`.

### FR3: Storage
- AC3.1: Each audit is saved in SQLite with its summary and per-feature results.
- AC3.2: Saved audits are still available after the app restarts.

### FR4: Retrieval and display
- AC4.1: `GET /api/audits` returns all past audits, newest first.
- AC4.2: `GET /api/audits/{id}` returns the summary and per-feature results, sorted by q-value.
- AC4.3: `GET /api/audits/{id}` returns HTTP 404 for an unknown id.
- AC4.4: The web page at `/` has an upload form, shows the verdict and the top 10 drifted features after an upload, and lists past audits.

### FR5: Health
- AC5.1: `GET /health` returns `{"status": "ok"}`.

## API summary

| Method | Path | Purpose |
|---|---|---|
| POST | /api/audits | Upload CSV, run audit, store, return result |
| GET | /api/audits | List past audits |
| GET | /api/audits/{id} | One audit with per-feature results |
| GET | /health | Liveness check |
| GET | / | Web page |

## Data model

- `audits`: id, created_at, filename, n_source, n_target, n_features, n_significant, verdict
- `feature_results`: id, audit_id, feature, mean_source, mean_target, fold_change, p_value, q_value, significant

## Non-functional requirements

- NFR1: An audit of 500 rows and 100 features completes in under 5 seconds.
- NFR2: Only synthetic or public data is used in this repository.
- NFR3: The whole system starts with one command (`docker compose up`), and tests run with one command (`make test`).

## Out of scope

Image (DICOM) processing, user accounts, model training, PCA and SHAP plots.