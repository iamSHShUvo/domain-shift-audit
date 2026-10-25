from io import BytesIO
from typing import TypedDict

import pandas as pd
from scipy.stats import false_discovery_control, mannwhitneyu


class FeatureResult(TypedDict):
    feature: str
    mean_source: float
    mean_target: float
    fold_change: float | None
    p_value: float
    q_value: float
    significant: bool


class AuditStatistics(TypedDict):
    n_features: int
    n_significant: int
    verdict: str
    feature_results: list[FeatureResult]


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


def compute_statistics(
    dataframe: pd.DataFrame, features: list[str]
) -> AuditStatistics:
    source_rows = dataframe["cohort"] == "source"
    target_rows = dataframe["cohort"] == "target"
    tested_results: list[FeatureResult] = []

    for feature in features:
        source_values = dataframe.loc[source_rows, feature].dropna()
        target_values = dataframe.loc[target_rows, feature].dropna()
        combined_values = pd.concat([source_values, target_values])

        if combined_values.nunique() <= 1 or source_values.empty or target_values.empty:
            continue

        mean_source = float(source_values.mean())
        mean_target = float(target_values.mean())
        test_result = mannwhitneyu(
            source_values.to_numpy(),
            target_values.to_numpy(),
            alternative="two-sided",
            nan_policy="omit",
        )
        tested_results.append(
            {
                "feature": feature,
                "mean_source": mean_source,
                "mean_target": mean_target,
                "fold_change": (
                    None if mean_source == 0 else mean_target / mean_source
                ),
                "p_value": float(test_result.pvalue),
                "q_value": 0.0,
                "significant": False,
            }
        )

    if tested_results:
        q_values = false_discovery_control(
            [result["p_value"] for result in tested_results], method="bh"
        )
        for result, q_value in zip(tested_results, q_values):
            result["q_value"] = float(q_value)
            result["significant"] = result["q_value"] < 0.05

    n_significant = sum(result["significant"] for result in tested_results)
    high_drift = bool(tested_results) and n_significant / len(tested_results) >= 0.3

    return {
        "n_features": len(tested_results),
        "n_significant": n_significant,
        "verdict": "HIGH_DRIFT" if high_drift else "LOW_DRIFT",
        "feature_results": tested_results,
    }
