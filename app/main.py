from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.audit import compute_statistics, parse_and_validate_csv
from app.db import get_audit, initialize_db, list_audits, save_audit


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialize_db()
    yield


app = FastAPI(lifespan=lifespan)
INDEX_FILE = Path(__file__).parent / "static" / "index.html"


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(INDEX_FILE, media_type="text/html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/audits")
async def create_audit(file: UploadFile = File(...)) -> dict[str, object]:
    try:
        dataframe, features = parse_and_validate_csv(await file.read())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    statistics = compute_statistics(dataframe, features)
    return save_audit(
        filename=file.filename or "upload.csv",
        n_source=int((dataframe["cohort"] == "source").sum()),
        n_target=int((dataframe["cohort"] == "target").sum()),
        n_features=statistics["n_features"],
        n_significant=statistics["n_significant"],
        verdict=statistics["verdict"],
        feature_results=statistics["feature_results"],
    )


@app.get("/api/audits")
def get_audits() -> list[dict[str, object]]:
    return list_audits()


@app.get("/api/audits/{audit_id}")
def get_audit_by_id(audit_id: int) -> dict[str, object]:
    audit = get_audit(audit_id)
    if audit is None:
        raise HTTPException(status_code=404, detail="Audit not found.")
    return audit
