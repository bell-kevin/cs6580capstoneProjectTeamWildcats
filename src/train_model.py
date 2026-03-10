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
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

TARGET_COLUMN = "traffic_count_total"
RANDOM_STATE = 42
DEFAULT_SPLIT_STRATEGY = "time"
VALID_SPLIT_STRATEGIES = {"random", "time"}


def add_engineered_features(data: pd.DataFrame) -> pd.DataFrame:
    engineered = data.copy()
    engineered["date_hour"] = pd.to_datetime(engineered["date_hour"], errors="coerce")
    engineered["date"] = (
        pd.to_datetime(engineered["date"], errors="coerce")
        if "date" in engineered.columns
        else engineered["date_hour"].dt.normalize()
    )

    engineered["day_of_week_num"] = pd.to_datetime(engineered["date_hour"]).dt.dayofweek
    engineered["month"] = engineered["date_hour"].dt.month
    engineered["is_peak_hour"] = engineered["hour"].isin([7, 8, 9, 15, 16, 17]).astype(int)
    engineered["temp_dewpoint_spread"] = engineered["temp_f"] - engineered["dewpoint_f"]

    # Engineer Numeric columns for  Holdiday Weekends and Distance From a Holiday Weekend
    daily = (
        engineered.groupby("date")[["is_federal_holiday"]]
        .max()
        .sort_index()
        .reset_index()
    )

    daily["date"] = pd.to_datetime(daily["date"], errors="coerce").dt.normalize()
    daily["weekday"] = daily["date"].dt.dayofweek  

    daily["is_holiday_weekend"] = False

    holiday_dates = daily.loc[daily["is_federal_holiday"], "date"]

    for holiday_date in holiday_dates:
        wd = holiday_date.dayofweek

        if wd <= 2:
            saturday = holiday_date - pd.Timedelta(days=(wd + 2))
            sunday = saturday + pd.Timedelta(days=1)
            window_start = saturday
            window_end = holiday_date

        elif wd <= 4:
            saturday = holiday_date + pd.Timedelta(days=(5 - wd))
            sunday = saturday + pd.Timedelta(days=1)
            window_start = holiday_date
            window_end = sunday

        else:
            saturday = holiday_date - pd.Timedelta(days=(wd - 5))
            sunday = saturday + pd.Timedelta(days=1)
            window_start = saturday
            window_end = sunday

        daily.loc[
            (daily["date"] >= window_start) &
            (daily["date"] <= window_end),
            "is_holiday_weekend"
        ] = True

    daily["last_hw"] = daily["date"].where(daily["is_holiday_weekend"]).ffill()
    daily["days_since"] = (daily["date"] - daily["last_hw"]).dt.days

    daily["next_hw"] = daily["date"].where(daily["is_holiday_weekend"]).bfill()
    daily["days_until"] = (daily["next_hw"] - daily["date"]).dt.days

    daily["distance_to_holiday_weekend"] = daily[
        ["days_since", "days_until"]
    ].min(axis=1)

    # Merge back to hourly
    engineered = engineered.merge(
        daily[["date", "distance_to_holiday_weekend"]],
        on="date",
        how="left"
    )

    # Engineer lag features for traffic_count_total
    lag_hours = [1, 2, 3, 6, 12, 24, 168]

    for lag in lag_hours:
        engineered[f"traffic_lag_{lag}"] = (
            engineered[TARGET_COLUMN].shift(lag)
        )

    # adding in features that encode cyclical time patterns
    engineered["hour_sin"] = np.sin(2 * np.pi * engineered["hour"] / 24)
    engineered["hour_cos"] = np.cos(2 * np.pi * engineered["hour"] / 24)

    engineered["day_of_week_sin"] = np.sin(2 * np.pi * engineered["day_of_week_num"] / 7)
    engineered["day_of_week_cos"] = np.cos(2 * np.pi * engineered["day_of_week_num"] / 7)   

    engineered["month_sin"] = np.sin(2 * np.pi * engineered["month"] / 12)
    engineered["month_cos"] = np.cos(2 * np.pi * engineered["month"] / 12)    

    # Drop day of week numeric
    engineered = engineered.drop(columns=["day_of_week_num"])  

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
        "distance_to_holiday_weekend",
        "traffic_lag_1",
        "traffic_lag_2",
        "traffic_lag_3",
        "traffic_lag_6",
        "traffic_lag_12",
        "traffic_lag_24",
        "traffic_lag_168",
        "hour_sin",
        "hour_cos",
        "day_of_week_sin",
        "day_of_week_cos",
        "month_sin",
        "month_cos",
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
        "distance_to_holiday_weekend",
        "traffic_lag_1",
        "traffic_lag_2",
        "traffic_lag_3",
        "traffic_lag_6",
        "traffic_lag_12",
        "traffic_lag_24",
        "traffic_lag_168",
        "hour_sin",
        "hour_cos",
        "day_of_week_sin",
        "day_of_week_cos",
        "month_sin",
        "month_cos",
    ]
    return data[feature_columns], data[TARGET_COLUMN]


def drop_missing_target_rows(data: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Exclude records with missing response values before model fitting.

    The model can safely impute missing feature values, but imputing the response
    variable would create synthetic traffic trends and bias evaluation metrics.
    """

    filtered = data.dropna(subset=[TARGET_COLUMN]).copy()
    dropped_count = int(len(data) - len(filtered))
    return filtered, dropped_count


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
        "distance_to_holiday_weekend",
        "traffic_lag_1",
        "traffic_lag_2",
        "traffic_lag_3",
        "traffic_lag_6",
        "traffic_lag_12",
        "traffic_lag_24",
        "traffic_lag_168",
        "hour_sin",
        "hour_cos",
        "day_of_week_sin",
        "day_of_week_cos",
        "month_sin",
        "month_cos",
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


def split_dataset(
    features: pd.DataFrame,
    target: pd.Series,
    timestamps: pd.Series,
    test_size: float,
    split_strategy: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    if split_strategy not in VALID_SPLIT_STRATEGIES:
        raise ValueError(
            f"Unsupported split strategy {split_strategy!r}. Use one of {sorted(VALID_SPLIT_STRATEGIES)}."
        )

    if not 0 < test_size < 1:
        raise ValueError(f"test_size must be between 0 and 1, received {test_size}.")

    if split_strategy == "random":
        return train_test_split(
            features,
            target,
            test_size=test_size,
            random_state=RANDOM_STATE,
        )

    chronological = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(timestamps, errors="coerce"),
            "feature_row": features.index,
            "target": target,
        }
    ).dropna(subset=["timestamp"])

    if chronological.empty:
        raise ValueError("Time-based split requires at least one valid timestamp.")

    chronological = chronological.sort_values("timestamp")
    split_index = max(int(len(chronological) * (1 - test_size)), 1)
    split_index = min(split_index, len(chronological) - 1)

    train_idx = chronological.iloc[:split_index]["feature_row"]
    test_idx = chronological.iloc[split_index:]["feature_row"]

    return (
        features.loc[train_idx],
        features.loc[test_idx],
        target.loc[train_idx],
        target.loc[test_idx],
    )


def evaluate_split(
    features: pd.DataFrame,
    target: pd.Series,
    timestamps: pd.Series,
    test_size: float,
    split_strategy: str,
) -> dict[str, float | int | str]:
    X_train, X_test, y_train, y_test = split_dataset(
        features=features,
        target=target,
        timestamps=timestamps,
        test_size=test_size,
        split_strategy=split_strategy,
    )

    baseline = DummyRegressor(strategy="mean")
    baseline.fit(X_train, y_train)
    baseline_predictions = baseline.predict(X_test)
    baseline_scores = regression_metrics(y_test, baseline_predictions)

    pipeline = build_model_pipeline()
    pipeline.fit(X_train, y_train)
    champion_predictions = pipeline.predict(X_test)
    champion_scores = regression_metrics(y_test, champion_predictions)

    return {
        "split_strategy": split_strategy,
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "baseline_rmse": baseline_scores["rmse"],
        "baseline_mae": baseline_scores["mae"],
        "baseline_r2": baseline_scores["r2"],
        "champion_rmse": champion_scores["rmse"],
        "champion_mae": champion_scores["mae"],
        "champion_r2": champion_scores["r2"],
        "pipeline": pipeline,
        "y_test": y_test,
        "champion_predictions": champion_predictions,
    }

# Functions necessary for rnn/lstm model
# build preprocessor for LSTM model
def build_lstm_preprocessor() -> ColumnTransformer:
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
        "distance_to_holiday_weekend",
        "traffic_lag_1",
        "traffic_lag_2",
        "traffic_lag_3",
        "traffic_lag_6",
        "traffic_lag_12",
        "traffic_lag_24",
        "traffic_lag_168",
        "hour_sin",
        "hour_cos",
        "day_of_week_sin",
        "day_of_week_cos",
        "month_sin",
        "month_cos",
    ]   
    categorical_features = ["day_of_week"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]), numeric_features),
            ("categorical", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ]), categorical_features),
        ],
        remainder="drop"
    )

    return preprocessor 

# This ensures all rows in a sequence fed into the model are continuous
# It returns an array of dataframes, where each dataframe is a continuous sequence of rows with no gaps in the date_hour column.
def split_into_continuous_segments(df: pd.DataFrame) -> list[pd.DataFrame]:
    df = df.sort_values("date_hour").copy()

    df["date_hour"] = pd.to_datetime(df["date_hour"])
    df["time_diff"] = df["date_hour"].diff().dt.total_seconds() / 3600
    
    # Start a new sequence whenever the time difference between consecutive rows is over 1 hour
    df["segment_id"] = (df["time_diff"] > 1).cumsum()

    segments = []

    for _, seg in df.groupby("segment_id"):
        seg = seg.drop(columns=["time_diff", "segment_id"])
        if len(seg) >= 121:
            segments.append(seg)    

    return segments

# Create sliding window sequences within each segment, separating features and target and returning feature and target arrays suitable for RNN/LSTM 
def build_sequences(segments: list[pd.DataFrame], feature_cols: list[str], target_col: str, seq_length:int = 48, horizon:int = 72):
    X, y = [], []

    for seg in segments:
        features = seg[feature_cols].values
        target = seg[target_col].values

        for i in range(seq_length, len(seg) - horizon + 1):
            # the features window for one sample/window is the previous seq_length rows(48), and the target is the next horizon(72) rows after that
            X.append(features[i-seq_length:i])
            y.append(target[i:i+horizon])
    
    return np.array(X), np.array(y)

# Create pytorch traffic dataset for RNN/LSTM
class TrafficDataset(Dataset):
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]
    
# Define LSTM model for traffic prediction
class TrafficLSTM(nn.Module):
    def __init__(self, input_size, hidden_size=128, horizon=72):
        super().__init__()
       
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, num_layers=2, dropout=0.2, batch_first=True)
        self.fc = nn.Linear(hidden_size, horizon)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]
        output = self.fc(last_hidden)
        return output

#Create weighted mse loss function to prioritize accuracy nearer to the current time point in the horizon, then train the LSTM model
def weighted_mse(predictions, targets, weights):
    error = (predictions - targets) ** 2
    weighted_error = error * weights
    return weighted_error.mean()

def train_lstm_model(X, y, epochs=25, batch_size=128):
    dataset = TrafficDataset(X, y)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=True)

    model = TrafficLSTM(input_size=X.shape[2])

    # Create weights for custom loss function to prioritize accuracy nearer to the current time point
    horizon = y.shape[1]
    weights = torch.linspace(1.0, 0.3, steps=horizon)
    weights = weights / weights.sum()

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(epochs):
        
        epoch_loss = 0.0

        for batch_X, batch_y in dataloader:
            optimizer.zero_grad()
            predictions = model(batch_X)
            loss = weighted_mse(predictions, batch_y, weights=weights)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss:.5f}")
    
    return model

def train_and_evaluate(
    input_file: Path,
    model_dir: Path = Path("models"),
    results_dir: Path = Path("results"),
    test_size: float = 0.2,
    split_strategy: str = DEFAULT_SPLIT_STRATEGY,
    compare_with_time_split: bool = True,
) -> dict[str, float | str | int]:
    if not input_file.exists():
        raise FileNotFoundError(
            f"{input_file} was not found. Run `python src/data_cleaning.py` first to build processed data."
        )

    model_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv(input_file)
    engineered = add_engineered_features(data)
    engineered, dropped_target_rows = drop_missing_target_rows(engineered)

    if engineered.empty:
        raise ValueError(
            "No training rows available after removing records with missing target values."
        )

    features, target = build_features_and_target(engineered)

    # LSTM model training and evaluation _____________________________________________________________________________________________________

    # preprocess data for LSTM
    # Split into train and test
    train_raw_df, test_raw_df = train_test_split(engineered, test_size=test_size, shuffle=False)
    
    # Preprocess Features (Scale and impute)
    preprocessor = build_lstm_preprocessor()
    # Fit preprocessor on train data and transform train data
    X_train = preprocessor.fit_transform(train_raw_df)
    # transform test data with the same preprocessor fitted on train data
    X_test = preprocessor.transform(test_raw_df)

    # Scale Target
    target_scaler = StandardScaler()
    # fit target scaler on train target and transform train target
    y_train = target_scaler.fit_transform(
        train_raw_df[[TARGET_COLUMN]]
    ).flatten()
    # transform test target with the same target scaler fitted on train target
    y_test = target_scaler.transform(
        test_raw_df[[TARGET_COLUMN]]
    ).flatten()

    # rebuild train and test dataframes with preprocessed features and scaled target for sequence building
    train_lstm_df = pd.DataFrame(X_train)
    train_lstm_df[TARGET_COLUMN] = y_train
    train_lstm_df["date_hour"] = train_raw_df["date_hour"].values

    test_lstm_df = pd.DataFrame(X_test)
    test_lstm_df[TARGET_COLUMN] = y_test
    test_lstm_df["date_hour"] = test_raw_df["date_hour"].values

    # build sequences separately on train and test to avoid data leakage
    train_segments = split_into_continuous_segments(train_lstm_df)
    test_segments = split_into_continuous_segments(test_lstm_df)

    feature_columns = train_lstm_df.columns.drop([TARGET_COLUMN, "date_hour"]).tolist()

    X_train_seq, y_train_seq = build_sequences(
        train_segments,
        feature_columns,
        TARGET_COLUMN
    )

    X_test_seq, y_test_seq = build_sequences(
        test_segments,
        feature_columns,
        TARGET_COLUMN
    )

    print(f"Built {len(X_train_seq)} training sequences and {len(X_test_seq)} testing sequences of length 48 hours with a 72 hour horizon for RNN/LSTM model.")
    
    # Train and Save LSTM model
    lstm_model = train_lstm_model(X_train_seq, y_train_seq)
    torch.save(lstm_model.state_dict(), model_dir / "champion_lstm.pth")

    # Evaluate LSTM model
    lstm_model.eval()

    test_dataset = TrafficDataset(X_test_seq, y_test_seq)
    test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False)

    predictions = []

    with torch.no_grad():
        for batch_X, _ in test_loader:
            preds = lstm_model(batch_X)
            predictions.append(preds.cpu().numpy())

    lstm_predictions = np.vstack(predictions)

    # Assess LSTM
    y_true_lstm = target_scaler.inverse_transform(
    y_test_seq.reshape(-1,1)
    ).flatten()

    y_pred_lstm = target_scaler.inverse_transform(
        lstm_predictions.reshape(-1,1)
    ).flatten() 

    lstm_rmse = np.sqrt(mean_squared_error(y_true_lstm, y_pred_lstm))
    lstm_mae = mean_absolute_error(y_true_lstm, y_pred_lstm)
    lstm_r2 = r2_score(y_true_lstm, y_pred_lstm)

    print("LSTM RMSE:", lstm_rmse)
    print("LSTM MAE:", lstm_mae)
    print("LSTM R2:", lstm_r2)

    split_results = evaluate_split(
        features=features,
        target=target,
        timestamps=engineered["date_hour"],
        test_size=test_size,
        split_strategy=split_strategy,
    )

    comparison_results: dict[str, float | str] = {}
    if compare_with_time_split and split_strategy == "random":
        time_results = evaluate_split(
            features=features,
            target=target,
            timestamps=engineered["date_hour"],
            test_size=test_size,
            split_strategy="time",
        )
        comparison_results = {
            "time_split_champion_rmse": float(time_results["champion_rmse"]),
            "time_split_champion_mae": float(time_results["champion_mae"]),
            "time_split_champion_r2": float(time_results["champion_r2"]),
            "random_minus_time_rmse": float(split_results["champion_rmse"])
            - float(time_results["champion_rmse"]),
            "random_minus_time_mae": float(split_results["champion_mae"])
            - float(time_results["champion_mae"]),
            "random_minus_time_r2": float(split_results["champion_r2"])
            - float(time_results["champion_r2"]),
        }

    artifact_path = model_dir / "champion_model.joblib"
    joblib.dump(split_results["pipeline"], artifact_path)

    metrics_df = pd.DataFrame(
        [
            {
                "split_strategy": split_results["split_strategy"],
                "model": "baseline_dummy_mean",
                "rmse": split_results["baseline_rmse"],
                "mae": split_results["baseline_mae"],
                "r2": split_results["baseline_r2"],
            },
            {
                "split_strategy": split_results["split_strategy"],
                "model": "champion_random_forest",
                "rmse": split_results["champion_rmse"],
                "mae": split_results["champion_mae"],
                "r2": split_results["champion_r2"],
            },
            {
                "split_strategy": "sequence",
                "model": "lstm_model",
                "rmse": lstm_rmse,
                "mae": lstm_mae,
                "r2": lstm_r2,
            }
        ]
    )
    metrics_file = results_dir / "model_metrics.csv"
    metrics_df.to_csv(metrics_file, index=False)

    plt.figure(figsize=(8, 6))
    plt.scatter(split_results["y_test"], split_results["champion_predictions"], alpha=0.3)
    lower = min(
        float(split_results["y_test"].min()),
        float(min(split_results["champion_predictions"])),
    )
    upper = max(
        float(split_results["y_test"].max()),
        float(max(split_results["champion_predictions"])),
    )
    plt.plot([lower, upper], [lower, upper], linestyle="--")
    plt.xlabel("Actual traffic_count_total")
    plt.ylabel("Predicted traffic_count_total")
    plt.title("Actual vs Predicted Traffic")
    actual_plot = results_dir / "actual_vs_predicted.svg"
    plt.tight_layout()
    plt.savefig(actual_plot)
    plt.close()

    residuals = split_results["y_test"] - split_results["champion_predictions"]
    plt.figure(figsize=(8, 6))
    plt.scatter(split_results["champion_predictions"], residuals, alpha=0.3)
    plt.axhline(0.0, linestyle="--")
    plt.xlabel("Predicted traffic_count_total")
    plt.ylabel("Residual (actual - predicted)")
    plt.title("Residual Plot")
    residual_plot = results_dir / "residual_plot.svg"
    plt.tight_layout()
    plt.savefig(residual_plot)
    plt.close()

    summary = {
        "split_strategy": split_results["split_strategy"],
        "train_rows": split_results["train_rows"],
        "test_rows": split_results["test_rows"],
        "dropped_target_rows": dropped_target_rows,
        "baseline_rmse": split_results["baseline_rmse"],
        "baseline_mae": split_results["baseline_mae"],
        "champion_rmse": split_results["champion_rmse"],
        "champion_mae": split_results["champion_mae"],
        "champion_r2": split_results["champion_r2"],
        "model_artifact": str(artifact_path),
        "metrics_file": str(metrics_file),
        "actual_vs_predicted_plot": str(actual_plot),
        "residual_plot": str(residual_plot),
    }
    summary.update(comparison_results)

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
    parser.add_argument(
        "--split-strategy",
        choices=sorted(VALID_SPLIT_STRATEGIES),
        default=DEFAULT_SPLIT_STRATEGY,
        help="random uses shuffled rows; time trains on earliest rows and tests on latest rows.",
    )
    parser.add_argument(
        "--skip-time-comparison",
        action="store_true",
        help="Skip time-split comparison when using the random split strategy.",
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    summary = train_and_evaluate(
        input_file=args.input_file,
        model_dir=args.model_dir,
        results_dir=args.results_dir,
        test_size=args.test_size,
        split_strategy=args.split_strategy,
        compare_with_time_split=not args.skip_time_comparison,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
