import sqlite3

from app.db import initialize_db, save_audit


def test_audit_and_feature_results_are_stored_across_connections(tmp_path) -> None:
    db_path = tmp_path / "nested" / "audits.db"
    initialize_db(db_path)
    audit = save_audit(
        filename="cohorts.csv",
        n_source=5,
        n_target=5,
        n_features=1,
        n_significant=1,
        verdict="HIGH_DRIFT",
        feature_results=[
            {
                "feature": "signal",
                "mean_source": 1.0,
                "mean_target": 10.0,
                "fold_change": 10.0,
                "p_value": 0.01,
                "q_value": 0.01,
                "significant": True,
            }
        ],
        db_path=db_path,
    )

    with sqlite3.connect(db_path) as connection:
        audit_row = connection.execute(
            "SELECT filename, n_source, n_target, verdict FROM audits WHERE id = ?",
            (audit["id"],),
        ).fetchone()
        feature_row = connection.execute(
            "SELECT feature, fold_change, significant FROM feature_results "
            "WHERE audit_id = ?",
            (audit["id"],),
        ).fetchone()

    assert audit_row == ("cohorts.csv", 5, 5, "HIGH_DRIFT")
    assert feature_row == ("signal", 10.0, 1)


def test_database_tables_are_created_automatically(tmp_path) -> None:
    db_path = tmp_path / "audits.db"

    initialize_db(db_path)

    with sqlite3.connect(db_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert {"audits", "feature_results"} <= tables
