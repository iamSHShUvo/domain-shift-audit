from pathlib import Path

import numpy as np
import pandas as pd


DRIFTED_FEATURES = {f"feature_{index:02d}" for index in range(1, 7)}


def generate_sample_data(
    output_path: Path = Path("data/sample_synthetic.csv"),
) -> None:
    rng = np.random.default_rng(2026)
    rows: list[dict[str, str | float]] = []

    for cohort in ("source", "target"):
        for _ in range(100):
            row: dict[str, str | float] = {"cohort": cohort}
            for index in range(1, 21):
                feature = f"feature_{index:02d}"
                mean = 1.5 if cohort == "target" and feature in DRIFTED_FEATURES else 0.0
                row[feature] = float(rng.normal(loc=mean, scale=1.0))
            rows.append(row)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_path, index=False)


if __name__ == "__main__":
    generate_sample_data()
