<a name="readme-top"></a>

# The Snowbasin "Congestion Engine"

## The Wildcats

- Dani Lopez (Data Analyst)
- Hazem Dawahi (Frontend and Backend integration)
- Roberto Camposeco (Data Engineer)
- Kevin Bell (Data Miner)

## Project goal

Predict peak-hour traffic volume on Trappers Loop (SR-167) to optimize mountain resort staffing and parking operations 72 hours in advance.

## Sprint 2 status

This repository now includes a reproducible cleaning pipeline that reads from immutable raw data and writes a joined, analysis-ready dataset to `data/processed`.

### Data sources used by the pipeline

- Trappers Loop hourly traffic count CSV files in `data/raw/trappersLoopCounts`.
- SBBWK weather station Excel files in `data/raw/weatherData`.
- U.S. federal holiday calendar in `data/raw/federalHolidayData/us_federal_holidays_2015_2026.csv`.

### Reproducible pipeline

Run the full cleaning and join process:

```bash
python src/data_cleaning.py
```

Outputs:

- `data/processed/snowbasin_hourly_joined.csv`
- `data/processed/snowbasin_data_quality_report.csv`

### Tests

Run the automated test suite:

```bash
pytest -q
```

### Data audit artifact

A full inventory of every CSV and Excel source currently in the repository is documented at:

- `docs/data_inventory.md`

## Links

- Dashboard: https://dashboard-snowbasin-wildcats.vercel.app/
- Data export endpoint: https://d34agsj343lfgw.cloudfront.net/

<p align="right"><a href="#readme-top">back to top</a></p>
