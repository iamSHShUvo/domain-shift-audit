from fastapi import FastAPI, File, HTTPException, UploadFile

from app.audit import compute_statistics, parse_and_validate_csv

app = FastAPI()


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
    return {
        "filename": file.filename or "upload.csv",
        "n_source": int((dataframe["cohort"] == "source").sum()),
        "n_target": int((dataframe["cohort"] == "target").sum()),
        **statistics,
    }
