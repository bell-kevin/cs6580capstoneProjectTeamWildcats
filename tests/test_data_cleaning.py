from pathlib import Path

import pandas as pd

from src.data_cleaning import (
    PipelinePaths,
    build_joined_dataset,
    load_and_clean_traffic,
    run_pipeline,
)


def test_load_and_clean_traffic_aggregates_lanes() -> None:
    traffic_file = Path("data/raw/trappersLoopCounts/Trappers_Loop_2015.csv")
    hourly = load_and_clean_traffic([traffic_file])

    assert {"date_hour", "traffic_count_total", "lane_count"}.issubset(hourly.columns)
    assert len(hourly) > 8000

    midnight = hourly[hourly["date_hour"] == pd.Timestamp("2015-01-01 00:00:00")]
    assert len(midnight) == 1
    assert float(midnight.iloc[0]["traffic_count_total"]) == 181.0
    assert int(midnight.iloc[0]["lane_count"]) == 2


def test_build_joined_dataset_has_weather_and_flags() -> None:
    paths = PipelinePaths(
        traffic_dir=Path("data/raw/trappersLoopCounts"),
        weather_dir=Path("data/raw/weatherData"),
        holidays_file=Path("data/raw/federalHolidayData/us_federal_holidays_2015_2026.csv"),
        output_dir=Path("data/processed"),
    )

    joined = build_joined_dataset(paths)
    assert len(joined) > 60000
    assert joined["date_hour"].is_monotonic_increasing
    assert joined["temp_f"].notna().sum() > 15000
    assert joined["is_weekend"].dtype == bool
    assert joined["is_federal_holiday"].sum() > 0


def test_run_pipeline_writes_outputs(tmp_path: Path) -> None:
    paths = PipelinePaths(
        traffic_dir=Path("data/raw/trappersLoopCounts"),
        weather_dir=Path("data/raw/weatherData"),
        holidays_file=Path("data/raw/federalHolidayData/us_federal_holidays_2015_2026.csv"),
        output_dir=tmp_path,
    )

    output_file, report_file = run_pipeline(paths)

    assert output_file.exists()
    assert report_file.exists()

    report = pd.read_csv(report_file)
    assert {"metric", "value"} == set(report.columns)
    assert "row_count" in set(report["metric"])
