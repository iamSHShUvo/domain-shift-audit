from io import BytesIO

import pandas as pd


def parse_and_validate_csv(contents: bytes) -> tuple[pd.DataFrame, list[str]]:
    try:
        dataframe = pd.read_csv(BytesIO(contents))
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
        raise ValueError("The uploaded file must be a valid CSV.") from error

    return dataframe, validate_dataframe(dataframe)


def validate_dataframe(dataframe: pd.DataFrame) -> list[str]:
    if "cohort" not in dataframe.columns:
        raise ValueError("The CSV must contain a 'cohort' column.")

    cohorts = dataframe["cohort"]
    invalid_cohorts = cohorts.isna() | ~cohorts.isin(["source", "target"])
    if invalid_cohorts.any():
        raise ValueError("The 'cohort' column may contain only 'source' and 'target'.")

    source_count = int((cohorts == "source").sum())
    target_count = int((cohorts == "target").sum())
    if source_count < 5 or target_count < 5:
        raise ValueError("The CSV must contain at least 5 rows in each cohort.")

    features = dataframe.select_dtypes(include="number").columns.tolist()
    if not features:
        raise ValueError("The CSV must contain at least one numeric feature column.")

    return features
