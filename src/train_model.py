from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET_COLUMN = "traffic_count_total"
RANDOM_STATE = 42


def add_engineered_features(data: pd.DataFrame) -> pd.DataFrame:
    engineered = data.copy()
    engineered["date_hour"] = pd.to_datetime(engineered["date_hour"], errors="coerce")

    engineered["month"] = engineered["date_hour"].dt.month
    engineered["is_peak_hour"] = engineered["hour"].isin([7, 8, 9, 15, 16, 17]).astype(int)
    engineered["temp_dewpoint_spread"] = engineered["temp_f"] - engineered["dewpoint_f"]

    return engineered


def build_features_and_target(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    required = {
        TARGET_COLUMN,
        "lane_count",
        "temp_f",
        "dewpoint_f",
        "humidity_pct",
        "wind_speed_mph",
        "snow_depth_in",
        "precip_1hr_in",
        "hour",
        "day_of_week",
        "is_weekend",
        "is_federal_holiday",
        "month",
        "is_peak_hour",
        "temp_dewpoint_spread",
    }
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns for training: {sorted(missing)}")

    feature_columns = [
        "lane_count",
        "temp_f",
        "dewpoint_f",
        "humidity_pct",
        "wind_speed_mph",
        "snow_depth_in",
        "precip_1hr_in",
        "hour",
        "month",
        "temp_dewpoint_spread",
        "is_weekend",
        "is_federal_holiday",
        "is_peak_hour",
        "day_of_week",
    ]
    return data[feature_columns], data[TARGET_COLUMN]


def build_model_pipeline() -> Pipeline:
    numeric_features = [
        "lane_count",
        "temp_f",
        "dewpoint_f",
        "humidity_pct",
        "wind_speed_mph",
        "snow_depth_in",
        "precip_1hr_in",
        "hour",
        "month",
        "temp_dewpoint_spread",
        "is_weekend",
        "is_federal_holiday",
        "is_peak_hour",
    ]
    categorical_features = ["day_of_week"]

    preprocess = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_features,
            ),
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    regressor = RandomForestRegressor(
        n_estimators=250,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    return Pipeline(steps=[("preprocess", preprocess), ("regressor", regressor)])


def regression_metrics(y_true: pd.Series, y_pred: pd.Series | list[float]) -> dict[str, float]:
    rmse = mean_squared_error(y_true, y_pred) ** 0.5
    return {
        "rmse": float(rmse),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def train_and_evaluate(
    input_file: Path,
    model_dir: Path = Path("models"),
    results_dir: Path = Path("results"),
    test_size: float = 0.2,
) -> dict[str, float | str | int]:
    if not input_file.exists():
        raise FileNotFoundError(
            f"{input_file} was not found. Run `python src/data_cleaning.py` first to build processed data."
        )

    model_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(input_file)
    engineered = add_engineered_features(data)
    features, target = build_features_and_target(engineered)

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=RANDOM_STATE,
    )

    baseline = DummyRegressor(strategy="mean")
    baseline.fit(X_train, y_train)
    baseline_predictions = baseline.predict(X_test)
    baseline_scores = regression_metrics(y_test, baseline_predictions)

    pipeline = build_model_pipeline()
    pipeline.fit(X_train, y_train)
    champion_predictions = pipeline.predict(X_test)
    champion_scores = regression_metrics(y_test, champion_predictions)

    artifact_path = model_dir / "champion_model.joblib"
    joblib.dump(pipeline, artifact_path)

    metrics_df = pd.DataFrame(
        [
            {"model": "baseline_dummy_mean", **baseline_scores},
            {"model": "champion_random_forest", **champion_scores},
        ]
    )
    metrics_file = results_dir / "model_metrics.csv"
    metrics_df.to_csv(metrics_file, index=False)

    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, champion_predictions, alpha=0.3)
    lower = min(float(y_test.min()), float(min(champion_predictions)))
    upper = max(float(y_test.max()), float(max(champion_predictions)))
    plt.plot([lower, upper], [lower, upper], linestyle="--")
    plt.xlabel("Actual traffic_count_total")
    plt.ylabel("Predicted traffic_count_total")
    plt.title("Actual vs Predicted Traffic")
    actual_plot = results_dir / "actual_vs_predicted.svg"
    plt.tight_layout()
    plt.savefig(actual_plot)
    plt.close()

    residuals = y_test - champion_predictions
    plt.figure(figsize=(8, 6))
    plt.scatter(champion_predictions, residuals, alpha=0.3)
    plt.axhline(0.0, linestyle="--")
    plt.xlabel("Predicted traffic_count_total")
    plt.ylabel("Residual (actual - predicted)")
    plt.title("Residual Plot")
    residual_plot = results_dir / "residual_plot.svg"
    plt.tight_layout()
    plt.savefig(residual_plot)
    plt.close()

    summary = {
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "baseline_rmse": baseline_scores["rmse"],
        "baseline_mae": baseline_scores["mae"],
        "champion_rmse": champion_scores["rmse"],
        "champion_mae": champion_scores["mae"],
        "champion_r2": champion_scores["r2"],
        "model_artifact": str(artifact_path),
        "metrics_file": str(metrics_file),
        "actual_vs_predicted_plot": str(actual_plot),
        "residual_plot": str(residual_plot),
    }

    summary_file = results_dir / "training_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2))
    summary["summary_file"] = str(summary_file)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train and evaluate the Snowbasin traffic model.")
    parser.add_argument(
        "--input-file",
        type=Path,
        default=Path("data/processed/snowbasin_hourly_joined.csv"),
        help="Processed CSV created by src/data_cleaning.py",
    )
    parser.add_argument("--model-dir", type=Path, default=Path("models"))
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--test-size", type=float, default=0.2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = train_and_evaluate(
        input_file=args.input_file,
        model_dir=args.model_dir,
        results_dir=args.results_dir,
        test_size=args.test_size,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
