# Domain Shift Audit

A small web service that checks whether a machine learning model trained on one
hospital cohort can be trusted on another. A user uploads a table of extracted
imaging features from two cohorts, and the service reports which features have
drifted and by how much.

## The problem

AI models for medical imaging are usually trained on data from a few
high-resource institutions. When they are used in a different country or
scanner setting, the input data can look statistically different (a "domain
shift"), and predictions become unreliable. Checking this before deployment is
slow and manual. This service automates that first safety check.

## What the system does

1. The user uploads a CSV file. Each row is one patient, one column is `cohort`
   (for example `source` or `target`), and the other columns are numeric features.
2. The backend compares the two cohorts feature by feature using the
   Mann-Whitney U test, corrects p-values with FDR, and computes fold change.
3. Results are stored in a database, so every audit run can be viewed later.
4. A web page lists the most drifted features and gives a verdict:
   - **Low drift**: fewer than 30% of features are significantly different.
   - **High drift**: 30% or more are significantly different. Recalibrate
     before reusing a model.

## Expected behavior

- A valid CSV returns an audit result in a few seconds.
- An invalid CSV (missing `cohort` column, fewer than two cohorts, no numeric
  features) returns a clear error message, and nothing is stored.
- Past runs remain available after the app restarts.

## Data note

Only synthetic or public data is used in this repository. No patient data is
stored or shipped.

## Tech stack

Python, FastAPI, SQLite, a single HTML page, pytest, Docker Compose,
GitHub Actions.

## Run locally

Install dependencies and start the API from the repository root:

```powershell
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The same commands are available with Make:

```text
make run
```

Generate the bundled synthetic example CSV with:

```powershell
python scripts/make_sample_data.py
```

The API is available at `http://127.0.0.1:8000`; its liveness endpoint is
`/health`.

## Run with Docker

Build the image and start the service with Docker Compose:

```powershell
docker compose up --build
```

The service is available at `http://127.0.0.1:8000`. Compose stores the SQLite
database in a named volume mounted at `/data`.

## Run tests

Run the test suite with Python:

```powershell
python -m pytest
```

Or use Make:

```text
make test
```

## Deployment

1. Build the container image from this repository and publish it to a registry
   your host can access.
2. Create a container service on a host such as Render or Fly.io using that
   image, and configure it to listen on port `8000`.
3. Attach a persistent disk to the container at `/data`.
4. Set the container environment variable `DB_PATH` to `/data/audits.db`.
5. Configure the host's health check to request `/health`.
6. Deploy the container and wait for the health check to report healthy.