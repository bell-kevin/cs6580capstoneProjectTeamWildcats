from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


TRAFFIC_HOURLY_COLUMNS = [f"H{hour:02d}00" for hour in range(24)]


@dataclass(frozen=True)
class PipelinePaths:
    traffic_dir: Path
    weather_dir: Path
    holidays_file: Path
    output_dir: Path



def _sorted_files(directory: Path, pattern: str) -> list[Path]:
    files = sorted(directory.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files found in {directory} matching {pattern!r}.")
    return files



def load_and_clean_traffic(traffic_files: Iterable[Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for path in traffic_files:
        raw = pd.read_csv(path)
        required_columns = {"DATE", "LANE", *TRAFFIC_HOURLY_COLUMNS}
        missing = required_columns - set(raw.columns)
        if missing:
            raise ValueError(f"Traffic file {path} missing columns: {sorted(missing)}")

        normalized = raw[["DATE", "LANE", *TRAFFIC_HOURLY_COLUMNS]].melt(
            id_vars=["DATE", "LANE"],
            value_vars=TRAFFIC_HOURLY_COLUMNS,
            var_name="hour_bucket",
            value_name="traffic_count",
        )

        normalized["hour"] = normalized["hour_bucket"].str[1:3].astype(int)
        normalized["date"] = pd.to_datetime(normalized["DATE"], errors="coerce")
        normalized = normalized.dropna(subset=["date"])
        normalized["date_hour"] = normalized["date"] + pd.to_timedelta(normalized["hour"], unit="h")
        normalized["traffic_count"] = pd.to_numeric(normalized["traffic_count"], errors="coerce")

        frames.append(normalized[["date_hour", "LANE", "traffic_count"]])

    long_traffic = pd.concat(frames, ignore_index=True)
    lane_counts = (
        long_traffic.groupby(["date_hour", "LANE"], as_index=False)["traffic_count"].sum(min_count=1)
    )

    hourly_traffic = (
        lane_counts.groupby("date_hour", as_index=False)
        .agg(
            traffic_count_total=("traffic_count", "sum"),
            lane_count=("LANE", "nunique"),
        )
        .sort_values("date_hour")
    )
    return hourly_traffic



def load_and_clean_weather(weather_files: Iterable[Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for path in weather_files:
        raw = pd.read_excel(path)
        timestamp_column = raw.columns[0]

        renamed = raw.rename(
            columns={
                timestamp_column: "weather_timestamp_raw",
                "TMP ° F": "temp_f",
                "DWP °F": "dewpoint_f",
                "RELH %": "humidity_pct",
                "ALTI in": "altimeter_in",
                "SOLR W/m*m": "solar_w_m2",
                "VOLT volt": "voltage_v",
                "SKNT mph": "wind_speed_mph",
                "GUST mph": "gust_mph",
                "DRCT °": "wind_direction_deg",
                "SNOW in": "snow_depth_in",
                "P01I in": "precip_1hr_in",
                "SINT in": "snow_interval_in",
            }
        )

        cleaned = renamed[[
            "weather_timestamp_raw",
            "temp_f",
            "dewpoint_f",
            "humidity_pct",
            "altimeter_in",
            "solar_w_m2",
            "voltage_v",
            "wind_speed_mph",
            "gust_mph",
            "wind_direction_deg",
            "snow_depth_in",
            "precip_1hr_in",
            "snow_interval_in",
        ]].copy()

        cleaned["weather_timestamp"] = pd.to_datetime(
            cleaned["weather_timestamp_raw"].astype(str).str.replace(" MST", "", regex=False),
            format="%m-%d-%Y %H:%M",
            errors="coerce",
        )

        cleaned = cleaned.dropna(subset=["weather_timestamp"])
        cleaned["date_hour"] = cleaned["weather_timestamp"].dt.floor("h")

        numeric_columns = [
            "temp_f",
            "dewpoint_f",
            "humidity_pct",
            "altimeter_in",
            "solar_w_m2",
            "voltage_v",
            "wind_speed_mph",
            "gust_mph",
            "wind_direction_deg",
            "snow_depth_in",
            "precip_1hr_in",
            "snow_interval_in",
        ]
        for column in numeric_columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

        frames.append(cleaned[["date_hour", *numeric_columns]])

    stacked_weather = pd.concat(frames, ignore_index=True)
    hourly_weather = (
        stacked_weather.groupby("date_hour", as_index=False)
        .agg(
            temp_f=("temp_f", "mean"),
            dewpoint_f=("dewpoint_f", "mean"),
            humidity_pct=("humidity_pct", "mean"),
            altimeter_in=("altimeter_in", "mean"),
            solar_w_m2=("solar_w_m2", "mean"),
            voltage_v=("voltage_v", "mean"),
            wind_speed_mph=("wind_speed_mph", "mean"),
            gust_mph=("gust_mph", "max"),
            wind_direction_deg=("wind_direction_deg", "mean"),
            snow_depth_in=("snow_depth_in", "mean"),
            precip_1hr_in=("precip_1hr_in", "max"),
            snow_interval_in=("snow_interval_in", "mean"),
            weather_samples_per_hour=("temp_f", "count"),
        )
        .sort_values("date_hour")
    )
    return hourly_weather



def load_holidays(holidays_file: Path) -> pd.DataFrame:
    holidays = pd.read_csv(holidays_file)
    expected = {"observed_date", "holiday_name", "observed_shifted"}
    missing = expected - set(holidays.columns)
    if missing:
        raise ValueError(f"Holiday file {holidays_file} missing columns: {sorted(missing)}")

    holidays = holidays.copy()
    holidays["observed_date"] = pd.to_datetime(holidays["observed_date"], errors="coerce").dt.date
    holidays = holidays.dropna(subset=["observed_date"])
    return holidays[["observed_date", "holiday_name", "observed_shifted"]]



def build_joined_dataset(paths: PipelinePaths) -> pd.DataFrame:
    traffic_files = _sorted_files(paths.traffic_dir, "Trappers_Loop_*.csv")
    weather_files = _sorted_files(paths.weather_dir, "SBBWK_*.xlsx")

    traffic = load_and_clean_traffic(traffic_files)
    weather = load_and_clean_weather(weather_files)
    holidays = load_holidays(paths.holidays_file)

    joined = traffic.merge(weather, on="date_hour", how="left", validate="1:1")
    joined["date"] = joined["date_hour"].dt.date
    joined = joined.merge(holidays, left_on="date", right_on="observed_date", how="left")
    joined["is_federal_holiday"] = joined["holiday_name"].notna()
    joined["is_weekend"] = joined["date_hour"].dt.dayofweek >= 5
    joined["hour"] = joined["date_hour"].dt.hour
    joined["day_of_week"] = joined["date_hour"].dt.day_name()

    return joined.sort_values("date_hour").reset_index(drop=True)



def build_data_quality_report(joined: pd.DataFrame) -> pd.DataFrame:
    report = pd.DataFrame(
        {
            "metric": [
                "row_count",
                "date_hour_min",
                "date_hour_max",
                "traffic_null_count",
                "weather_missing_rows",
                "holiday_rows",
                "weekend_rows",
            ],
            "value": [
                len(joined),
                joined["date_hour"].min(),
                joined["date_hour"].max(),
                int(joined["traffic_count_total"].isna().sum()),
                int(joined["temp_f"].isna().sum()),
                int(joined["is_federal_holiday"].sum()),
                int(joined["is_weekend"].sum()),
            ],
        }
    )
    return report



def run_pipeline(paths: PipelinePaths) -> tuple[Path, Path]:
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    joined = build_joined_dataset(paths)
    output_file = paths.output_dir / "snowbasin_hourly_joined.csv"
    joined.to_csv(output_file, index=False)

    report = build_data_quality_report(joined)
    report_file = paths.output_dir / "snowbasin_data_quality_report.csv"
    report.to_csv(report_file, index=False)

    return output_file, report_file



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Snowbasin joined modeling dataset.")
    parser.add_argument("--traffic-dir", type=Path, default=Path("data/raw/trappersLoopCounts"))
    parser.add_argument("--weather-dir", type=Path, default=Path("data/raw/weatherData"))
    parser.add_argument(
        "--holidays-file",
        type=Path,
        default=Path("data/raw/federalHolidayData/us_federal_holidays_2015_2026.csv"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    paths = PipelinePaths(
        traffic_dir=args.traffic_dir,
        weather_dir=args.weather_dir,
        holidays_file=args.holidays_file,
        output_dir=args.output_dir,
    )
    output_file, report_file = run_pipeline(paths)
    print(f"Saved joined dataset to {output_file}")
    print(f"Saved quality report to {report_file}")


if __name__ == "__main__":
    main()
