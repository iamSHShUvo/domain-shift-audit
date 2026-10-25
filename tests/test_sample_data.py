import pandas as pd

from scripts.make_sample_data import DRIFTED_FEATURES, generate_sample_data


def test_sample_data_is_synthetic_and_has_six_shifted_features(tmp_path) -> None:
    output_path = tmp_path / "sample.csv"

    generate_sample_data(output_path)
    dataframe = pd.read_csv(output_path)
    feature_columns = dataframe.select_dtypes(include="number").columns.tolist()
    source_means = dataframe.loc[dataframe["cohort"] == "source", feature_columns].mean()
    target_means = dataframe.loc[dataframe["cohort"] == "target", feature_columns].mean()

    assert len(dataframe) == 200
    assert len(feature_columns) == 20
    assert len(DRIFTED_FEATURES) == 6
    assert dataframe["cohort"].value_counts().to_dict() == {"source": 100, "target": 100}
    assert all(target_means[feature] > source_means[feature] + 1 for feature in DRIFTED_FEATURES)
