import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolate_database(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DB_PATH", str(tmp_path / "audits.db"))


def upload_csv(contents: str):
    return client.post(
        "/api/audits",
        files={"file": ("cohorts.csv", contents, "text/csv")},
    )


def test_upload_accepts_valid_csv() -> None:
    rows = ["cohort,value"]
    rows.extend(f"source,{value}" for value in range(5))
    rows.extend(f"target,{value}" for value in range(5, 10))

    response = upload_csv("\n".join(rows))

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["n_source"] == 5
    assert response.json()["n_target"] == 5
    assert response.json()["n_features"] == 1


def test_upload_rejects_missing_cohort_column() -> None:
    rows = ["value"] + [str(value) for value in range(10)]

    response = upload_csv("\n".join(rows))

    assert response.status_code == 400
    assert "cohort" in response.json()["detail"]
    assert not Path(os.environ["DB_PATH"]).exists()


def test_upload_rejects_cohort_with_fewer_than_five_rows() -> None:
    rows = ["cohort,value"]
    rows.extend(f"source,{value}" for value in range(4))
    rows.extend(f"target,{value}" for value in range(5))

    response = upload_csv("\n".join(rows))

    assert response.status_code == 400
    assert "at least 5" in response.json()["detail"]
    assert not Path(os.environ["DB_PATH"]).exists()


def test_upload_rejects_csv_without_numeric_features() -> None:
    rows = ["cohort,description"]
    rows.extend(f"source,source-{value}" for value in range(5))
    rows.extend(f"target,target-{value}" for value in range(5))

    response = upload_csv("\n".join(rows))

    assert response.status_code == 400
    assert "numeric feature" in response.json()["detail"]
    assert not Path(os.environ["DB_PATH"]).exists()
