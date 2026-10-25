from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.audit import compute_statistics, parse_and_validate_csv
from app.db import initialize_db, save_audit


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialize_db()
    yield


app = FastAPI(lifespan=lifespan)


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
