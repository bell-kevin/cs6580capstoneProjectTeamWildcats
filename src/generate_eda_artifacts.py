"""Generate Sprint 2 visual evidence artifacts from the joined dataset."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from data_cleaning import PipelinePaths, build_joined_dataset


def _default_paths() -> PipelinePaths:
    return PipelinePaths(
        traffic_dir=Path("data/raw/trappersLoopCounts"),
        weather_dir=Path("data/raw/weatherData"),
        holidays_file=Path("data/raw/federalHolidayData/us_federal_holidays_2015_2026.csv"),
        output_dir=Path("data/processed"),
    )


def generate_results(results_dir: Path = Path("results")) -> list[Path]:
    results_dir.mkdir(parents=True, exist_ok=True)
    joined = build_joined_dataset(_default_paths())

    artifacts: list[Path] = []

    plt.figure(figsize=(10, 4))
    joined["traffic_count_total"].dropna().hist(bins=60)
    plt.title("Distribution of Hourly Traffic Counts")
    plt.xlabel("Hourly traffic count total")
    plt.ylabel("Frequency")
    traffic_hist = results_dir / "traffic_count_distribution.svg"
    plt.tight_layout()
    plt.savefig(traffic_hist)
    plt.close()
    artifacts.append(traffic_hist)

    plt.figure(figsize=(10, 4))
    joined["temp_f"].dropna().hist(bins=60)
    plt.title("Distribution of Temperature (F)")
    plt.xlabel("Temperature (F)")
    plt.ylabel("Frequency")
    temp_hist = results_dir / "temperature_distribution.svg"
    plt.tight_layout()
    plt.savefig(temp_hist)
    plt.close()
    artifacts.append(temp_hist)

    corr_columns = [
        "traffic_count_total",
        "temp_f",
        "dewpoint_f",
        "humidity_pct",
        "wind_speed_mph",
        "snow_depth_in",
        "precip_1hr_in",
    ]
    corr = joined[corr_columns].corr(numeric_only=True)

    plt.figure(figsize=(8, 6))
    image = plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar(image, fraction=0.046, pad=0.04)
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=45, ha="right")
    plt.yticks(range(len(corr.index)), corr.index)
    plt.title("Correlation Heatmap")
    heatmap = results_dir / "correlation_heatmap.svg"
    plt.tight_layout()
    plt.savefig(heatmap)
    plt.close()
    artifacts.append(heatmap)

    summary = joined[["traffic_count_total", "temp_f", "wind_speed_mph", "snow_depth_in"]].describe()
    summary_file = results_dir / "summary_statistics.csv"
    summary.to_csv(summary_file)
    artifacts.append(summary_file)

    return artifacts


if __name__ == "__main__":
    produced = generate_results()
    for artifact in produced:
        print(f"Generated {artifact}")
