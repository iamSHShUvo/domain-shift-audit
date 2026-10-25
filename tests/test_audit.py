import numpy as np
import pandas as pd
from scipy.stats import false_discovery_control, mannwhitneyu

from app.audit import compute_statistics


def drift_dataframe(n_drifted: int) -> tuple[pd.DataFrame, list[str]]:
    features = [f"feature_{index}" for index in range(10)]
    rows = []
    for cohort in ("source", "target"):
        for value in range(10):
            row = {"cohort": cohort}
            for index, feature in enumerate(features):
                if cohort == "target" and index < n_drifted:
                    row[feature] = value + 100
                else:
                    row[feature] = value
            row["constant"] = 7
            rows.append(row)
    return pd.DataFrame(rows), features + ["constant"]


def test_statistics_run_two_sided_tests_and_bh_correction() -> None:
    dataframe, features = drift_dataframe(3)

    result = compute_statistics(dataframe, features)

    first_result = result["feature_results"][0]
    expected_p = mannwhitneyu(
        dataframe.loc[dataframe["cohort"] == "source", features[0]],
        dataframe.loc[dataframe["cohort"] == "target", features[0]],
        alternative="two-sided",
    ).pvalue
    expected_q_values = false_discovery_control(
        [feature["p_value"] for feature in result["feature_results"]], method="bh"
    )
    assert first_result["p_value"] == expected_p
    assert [feature["q_value"] for feature in result["feature_results"]] == list(
        expected_q_values
    )
    assert result["n_significant"] == 3
    assert result["verdict"] == "HIGH_DRIFT"
    assert all(feature["feature"] != "constant" for feature in result["feature_results"])


def test_verdict_is_low_below_thirty_percent_significance() -> None:
    dataframe, features = drift_dataframe(2)

    result = compute_statistics(dataframe, features)

    assert result["n_significant"] == 2
    assert result["verdict"] == "LOW_DRIFT"


def test_fold_change_is_null_when_source_mean_is_zero() -> None:
    dataframe = pd.DataFrame(
        {
            "cohort": ["source"] * 5 + ["target"] * 5,
            "feature": [0, 0, 0, 0, 0, 1, 2, 3, 4, 5],
        }
    )

    result = compute_statistics(dataframe, ["feature"])

    assert result["feature_results"][0]["fold_change"] is None


def test_nan_values_are_ignored_in_statistics() -> None:
    dataframe = pd.DataFrame(
        {
            "cohort": ["source"] * 5 + ["target"] * 5,
            "feature": [1, 2, 3, 4, np.nan, 11, 12, 13, 14, np.nan],
        }
    )

    result = compute_statistics(dataframe, ["feature"])

    assert result["feature_results"][0]["mean_source"] == 2.5
    assert result["feature_results"][0]["mean_target"] == 12.5
    assert result["feature_results"][0]["p_value"] == mannwhitneyu(
        [1, 2, 3, 4], [11, 12, 13, 14], alternative="two-sided"
    ).pvalue

