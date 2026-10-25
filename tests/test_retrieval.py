from fastapi.testclient import TestClient

from app.db import save_audit
from app.main import app

client = TestClient(app)


def create_audit(filename: str, db_path: str):
    return save_audit(
        filename=filename,
        n_source=5,
        n_target=5,
        n_features=2,
        n_significant=1,
        verdict="LOW_DRIFT",
        feature_results=[
            {
                "feature": "later_q",
                "mean_source": 1.0,
                "mean_target": 2.0,
                "fold_change": 2.0,
                "p_value": 0.04,
                "q_value": 0.04,
                "significant": False,
            },
            {
                "feature": "earlier_q",
                "mean_source": 2.0,
                "mean_target": 1.0,
                "fold_change": 0.5,
                "p_value": 0.01,
                "q_value": 0.01,
                "significant": True,
            },
        ],
        db_path=db_path,
    )


def test_list_audits_returns_newest_first(monkeypatch, tmp_path) -> None:
    db_path = str(tmp_path / "audits.db")
    monkeypatch.setenv("DB_PATH", db_path)
    create_audit("older.csv", db_path)
    newer = create_audit("newer.csv", db_path)

    response = client.get("/api/audits")

    assert response.status_code == 200
    assert [audit["filename"] for audit in response.json()] == [
        "newer.csv",
        "older.csv",
    ]
    assert "feature_results" not in response.json()[0]
    assert response.json()[0]["id"] == newer["id"]


def test_get_audit_returns_feature_results_sorted_by_q_value(
    monkeypatch, tmp_path
) -> None:
    db_path = str(tmp_path / "audits.db")
    monkeypatch.setenv("DB_PATH", db_path)
    saved = create_audit("result.csv", db_path)

    response = client.get(f"/api/audits/{saved['id']}")

    assert response.status_code == 200
    assert response.json()["filename"] == "result.csv"
    assert [item["feature"] for item in response.json()["feature_results"]] == [
        "earlier_q",
        "later_q",
    ]
    assert response.json()["feature_results"][0]["significant"] is True


def test_get_unknown_audit_returns_404(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DB_PATH", str(tmp_path / "audits.db"))

    response = client.get("/api/audits/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Audit not found."
