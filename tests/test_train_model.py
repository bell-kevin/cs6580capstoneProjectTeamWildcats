from pathlib import Path

import pandas as pd

from src.train_model import add_engineered_features, split_dataset, train_and_evaluate


def _sample_processed_dataset(rows: int = 120) -> pd.DataFrame:
    timestamps = pd.date_range("2024-01-01", periods=rows, freq="h")
    base = pd.DataFrame(
        {
            "date_hour": timestamps,
            "traffic_count_total": [float(200 + (i % 24) * 12) for i in range(rows)],
            "lane_count": [2 for _ in range(rows)],
            "temp_f": [30.0 + (i % 10) for i in range(rows)],
            "dewpoint_f": [20.0 + (i % 8) for i in range(rows)],
            "humidity_pct": [60.0 + (i % 20) for i in range(rows)],
            "wind_speed_mph": [5.0 + (i % 6) for i in range(rows)],
            "snow_depth_in": [15.0 + (i % 12) for i in range(rows)],
            "precip_1hr_in": [0.0 if i % 5 else 0.2 for i in range(rows)],
            "hour": [int(ts.hour) for ts in timestamps],
            "day_of_week": [ts.day_name() for ts in timestamps],
            "is_weekend": [ts.dayofweek >= 5 for ts in timestamps],
            "is_federal_holiday": [False for _ in range(rows)],
        }
    )
    return base


def test_add_engineered_features_adds_expected_columns() -> None:
    data = _sample_processed_dataset(24)
    engineered = add_engineered_features(data)

    assert {"month", "is_peak_hour", "temp_dewpoint_spread"}.issubset(engineered.columns)
    assert engineered["month"].between(1, 12).all()


def test_train_and_evaluate_writes_artifacts(tmp_path: Path) -> None:
    source = tmp_path / "processed.csv"
    _sample_processed_dataset(180).to_csv(source, index=False)

    summary = train_and_evaluate(
        input_file=source,
        model_dir=tmp_path / "models",
        results_dir=tmp_path / "results",
        test_size=0.25,
    )

    assert summary["train_rows"] == 135
    assert summary["test_rows"] == 45
    assert summary["split_strategy"] == "random"
    assert Path(summary["model_artifact"]).exists()
    assert Path(summary["metrics_file"]).exists()
    assert Path(summary["actual_vs_predicted_plot"]).exists()
    assert Path(summary["residual_plot"]).exists()
    assert "time_split_champion_rmse" in summary
    assert "random_minus_time_r2" in summary


def test_split_dataset_time_strategy_is_chronological() -> None:
    data = _sample_processed_dataset(20)
    engineered = add_engineered_features(data)
    features = engineered[["lane_count", "temp_f"]]
    target = engineered["traffic_count_total"]

    X_train, X_test, y_train, y_test = split_dataset(
        features=features,
        target=target,
        timestamps=engineered["date_hour"],
        test_size=0.25,
        split_strategy="time",
    )

    assert len(X_train) == 15
    assert len(X_test) == 5
    assert y_train.index.max() < y_test.index.min()


def test_train_and_evaluate_time_strategy_skips_random_comparison(tmp_path: Path) -> None:
    source = tmp_path / "processed.csv"
    _sample_processed_dataset(120).to_csv(source, index=False)

    summary = train_and_evaluate(
        input_file=source,
        model_dir=tmp_path / "models",
        results_dir=tmp_path / "results",
        test_size=0.2,
        split_strategy="time",
    )

    assert summary["split_strategy"] == "time"
    assert "time_split_champion_rmse" not in summary
