import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.audit import FeatureResult


DEFAULT_DB_PATH = Path("data/audits.db")


def get_db_path() -> Path:
    return Path(os.environ.get("DB_PATH", str(DEFAULT_DB_PATH)))


def initialize_db(db_path: str | Path | None = None) -> Path:
    path = Path(db_path) if db_path is not None else get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                filename TEXT NOT NULL,
                n_source INTEGER NOT NULL,
                n_target INTEGER NOT NULL,
                n_features INTEGER NOT NULL,
                n_significant INTEGER NOT NULL,
                verdict TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS feature_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id INTEGER NOT NULL REFERENCES audits(id) ON DELETE CASCADE,
                feature TEXT NOT NULL,
                mean_source REAL NOT NULL,
                mean_target REAL NOT NULL,
                fold_change REAL,
                p_value REAL NOT NULL,
                q_value REAL NOT NULL,
                significant INTEGER NOT NULL,
                UNIQUE (audit_id, feature)
            );
            """
        )
        connection.commit()
    finally:
        connection.close()
    return path


def save_audit(
    filename: str,
    n_source: int,
    n_target: int,
    n_features: int,
    n_significant: int,
    verdict: str,
    feature_results: list[FeatureResult],
    db_path: str | Path | None = None,
) -> dict[str, object]:
    path = initialize_db(db_path)
    created_at = datetime.now(timezone.utc).isoformat()
    connection = sqlite3.connect(path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO audits
                    (created_at, filename, n_source, n_target, n_features,
                     n_significant, verdict)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    filename,
                    n_source,
                    n_target,
                    n_features,
                    n_significant,
                    verdict,
                ),
            )
            audit_id = int(cursor.lastrowid)
            connection.executemany(
                """
                INSERT INTO feature_results
                    (audit_id, feature, mean_source, mean_target, fold_change,
                     p_value, q_value, significant)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        audit_id,
                        result["feature"],
                        result["mean_source"],
                        result["mean_target"],
                        result["fold_change"],
                        result["p_value"],
                        result["q_value"],
                        int(result["significant"]),
                    )
                    for result in feature_results
                ],
            )
    finally:
        connection.close()

    return {
        "id": audit_id,
        "created_at": created_at,
        "filename": filename,
        "n_source": n_source,
        "n_target": n_target,
        "n_features": n_features,
        "n_significant": n_significant,
        "verdict": verdict,
        "feature_results": feature_results,
    }
