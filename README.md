<div align="center">

# Domain Shift Audit

### A practical first check for feature distribution shift between imaging cohorts.

Upload a CSV of extracted features from a **source** and **target** cohort.
Review statistical differences, a concise drift verdict, and previous audit runs.

<br>

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/Storage-SQLite-003B57?logo=sqlite&logoColor=white)
[![CI](https://github.com/iamSHShUvo/domain-shift-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/iamSHShUvo/domain-shift-audit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-0A7B67.svg)](LICENSE)

</div>

> **Research tool, not a clinical device.** Domain Shift Audit provides a
> statistical screening result, not evidence of model safety or clinical
> performance. Validate findings with domain experts before making deployment
> decisions.

## About

Imaging models can encounter different scanners, patient populations, and
acquisition settings when moved beyond the institutions where they were
developed. These changes can alter the distributions of model input features
and may affect performance.

**Domain Shift Audit** makes an initial comparison easier to run and review.
It accepts a table of extracted features, compares the two cohorts feature by
feature, and saves each run so it can be reviewed later. It is intentionally
focused on tabular features; it does not process images or assess model
predictions.

## How it works

1. **Upload** a CSV containing a `cohort` column and numeric feature columns.
2. **Compare** source and target feature distributions using two-sided
   Mann–Whitney U tests.
3. **Adjust** p-values across tested features using the Benjamini–Hochberg
   false discovery rate procedure.
4. **Review** feature-level statistics and an overall drift verdict in the web
   interface or API.
5. **Return** to previous runs, which are stored in SQLite.

| Verdict | Rule |
| --- | --- |
| `LOW_DRIFT` | Fewer than 30% of tested features have an adjusted q-value below 0.05. |
| `HIGH_DRIFT` | At least 30% of tested features have an adjusted q-value below 0.05. |

Constant-valued features are skipped. Fold change is calculated as the target
mean divided by the source mean; it is null when the source mean is zero.

## Input format

Each row represents one observation. The `cohort` value must be exactly
`source` or `target`, with at least five rows in each cohort. Include one or
more numeric feature columns.

```csv
cohort,feature_01,feature_02
source,0.42,1.15
source,0.38,0.97
target,1.03,1.28
target,0.91,1.44
```

The example shows the required structure only; a valid upload needs at least
five rows for **each** cohort. Invalid files receive a clear error and are not
saved as audit runs.

## Get started

### Run locally

From the repository root, install the dependencies and start the app:

```powershell
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) to upload a CSV and review
results. The default SQLite database is `data/audits.db`; set `DB_PATH` to use
a different location.

To generate the bundled synthetic example:

```powershell
python scripts/make_sample_data.py
```

### Run with Docker Compose

```powershell
docker compose up --build
```

The app is available at [http://127.0.0.1:8000](http://127.0.0.1:8000).
Compose persists the SQLite database in the `audit-data` named volume, mounted
inside the container at `/data`.

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Web interface |
| `GET` | `/health` | Liveness check |
| `POST` | `/api/audits` | Upload a CSV and create an audit |
| `GET` | `/api/audits` | List saved audits, newest first |
| `GET` | `/api/audits/{id}` | Retrieve an audit and its feature results |

Interactive API documentation is available at
[/docs](http://127.0.0.1:8000/docs) while the app is running.

## Tests

Run the complete test suite with:

```powershell
python -m pytest
```

Or use Make:

```text
make test
```

## CI

The GitHub Actions workflow runs the test suite and a Docker build and health
check on every pull request. It also runs for pushes to `main`.

## Data and scope

This repository uses synthetic or public data only. Do not upload or commit
patient-identifiable or otherwise sensitive data. Domain Shift Audit does not
perform DICOM/image processing, model training, user management, or clinical
validation.

## Technology

Python · FastAPI · pandas · SciPy · SQLite · pytest · Docker Compose

---

Released under the [MIT License](LICENSE).
