# CS-6580 Sprint 4 Midterm MVP Presentation

> Suggested runtime: 7–10 minutes, ~10 slides.

---

## Slide 1 — Title / Hook
**Snowbasin Congestion Engine: Midterm MVP**  
Team Wildcats  

**Business Question:**  
How can Snowbasin predict peak-hour Trappers Loop traffic 72 hours ahead to improve staffing, parking, and guest arrival communication?

**Stakeholder:**  
Snowbasin operations managers and resort leadership.

---

## Slide 2 — Why This Matters
- Peak-day congestion degrades guest experience and increases operating risk.
- Staffing and parking decisions are currently reactive.
- A usable prediction product can drive proactive operations.

**Target business outcomes:**
- Reduce overflow parking incidents.
- Improve staffing precision.
- Improve arrival guidance on high-volume days.

---

## Slide 3 — Data Sources and Join Logic
**Primary inputs**
- UDOT Trappers Loop hourly traffic counts (`data/raw/trappersLoopCounts/*`).
- SBBWK station weather history (`data/raw/weatherData/*.xlsx`).
- U.S. federal holiday calendar (`data/raw/federalHolidayData/us_federal_holidays_2015_2026.csv`).

**Join key and grain**
- Common hourly grain (`date_hour`).
- Traffic and weather aligned hourly.
- Holiday/weekend enrichments added.

---

## Slide 4 — EDA Snapshot
Use these repository visuals:
- `results/traffic_count_distribution.svg`
- `results/temperature_distribution.svg`
- `results/correlation_heatmap.svg`

Talking points:
- Clear seasonality in weather and traffic volume.
- Hour-of-day and calendar effects matter.
- Weather spread and precipitation influence traffic variance.

---

## Slide 5 — Sprint 3 Feature Engineering
Engineered features used by model:
- `month`
- `is_peak_hour` (1 for 07–09 and 15–17)
- `temp_dewpoint_spread` = `temp_f - dewpoint_f`

Transformations:
- Numeric imputation + scaling (`SimpleImputer` + `StandardScaler`).
- Categorical imputation + encoding (`OneHotEncoder` for `day_of_week`).

---

## Slide 6 — Baseline vs Champion (Core Result)
**Baseline model:** `DummyRegressor(strategy='mean')`  
**Champion model:** `RandomForestRegressor`

From `results/training_summary.json`:
- Baseline RMSE: **295.82**
- Baseline MAE: **253.32**
- Champion RMSE: **102.91**
- Champion MAE: **59.02**
- Champion R²: **0.879**

**Narrative:** Champion materially outperforms baseline, validating business usefulness.

---

## Slide 7 — Evaluation Visuals
Use these artifacts:
- `results/actual_vs_predicted.svg`
- `results/residual_plot.svg`

Talking points:
- Actual-vs-predicted points cluster near diagonal.
- Residual plot shows reduced large-error frequency.
- Supports selecting the random-forest pipeline as current champion.

---

## Slide 8 — Sprint 4 MVP App
**Application:** `src/app.py` (Gradio)

Demo flow:
1. Load `models/champion_model.joblib`.
2. Enter weather + calendar + traffic context inputs.
3. Click **Predict traffic volume**.
4. Return predicted hourly vehicle count in real-time.

Run commands:
```bash
python src/train_model.py
python src/app.py
```

---

## Slide 9 — Reproducibility and Team Delivery
- `requirements.txt` added for environment setup.
- Pipeline scripts are reproducible and file-based:
  - `src/data_cleaning.py`
  - `src/train_model.py`
  - `src/app.py`
- Tests in `tests/` validate cleaning, inventory audit, and training artifacts.

---

## Slide 10 — Risks, Next Steps, Ask
**Current risks**
- Distribution drift from new weather/traffic patterns.
- Need for stronger experiment/board process evidence.

**Next Sprint opportunities**
- Hyperparameter tuning + model calibration.
- Add lag-based temporal features for 72-hour horizon fidelity.
- Deploy MVP to cloud endpoint and add monitoring.

**Ask to stakeholders**
- Confirm operational thresholds for “high congestion.”
- Provide feedback on MVP inputs and dashboard UX.

---

## Presenter Notes (optional)
- Keep each slide to ~45–60 seconds.
- Spend extra time on Slide 6 (impact) and Slide 8 (live demo).
- If demo fails, use saved metrics + screenshots as fallback evidence.
