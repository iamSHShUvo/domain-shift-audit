# AGENTS.md

Context file for AI coding agents working on this repository. Read this first.

## Project

Domain Shift Audit: a small web service. A user uploads a CSV of imaging
features from two cohorts (`source` and `target`), and the service reports
which features drifted, with a LOW_DRIFT or HIGH_DRIFT verdict.

Full requirements are in `SPEC.md`. Work is tracked in GitHub Issues
(#1 to #10), and each issue has acceptance criteria.

## Stack

Python 3.10+, FastAPI, SQLite, one HTML page (no frontend framework), pytest,
Docker Compose, GitHub Actions.

## Commands

- Run tests: `make test`
- Run locally: `uvicorn app.main:app --reload`
- Run everything in containers: `docker compose up`

## Rules for agents

1. Work on one GitHub Issue at a time. Read its acceptance criteria before coding.
2. Do not change `SPEC.md` without telling the human. If the spec is wrong, say so.
3. Write tests for every acceptance criterion. A task is not done until `make test` passes.
4. Use synthetic data only. Never add real patient data, DICOM files, or credentials to the repo.
5. Keep code simple: no extra frameworks, no features outside `SPEC.md`.
6. Commit messages reference the issue, for example `Add upload validation. Closes #2`.
7. The human reviews and approves every merge.

## Where to find more

- `SPEC.md`: requirements and acceptance criteria
- `docs/agents.md`: the agent team, roles, and handoffs
- `docs/process.md`: how work moves from issue to merge
- `README.md`: problem description and how to run the project