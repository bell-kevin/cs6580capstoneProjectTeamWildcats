# Model Experiment Tracking

## Sprint 3 baseline and champion

| Experiment | Model | Key settings | RMSE | MAE | R² | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline | `DummyRegressor` | `strategy='mean'` | 295.82 | 253.32 | -0.0000 | Baseline benchmark for viability checks. |
| Champion | `RandomForestRegressor` | `n_estimators=250`, `min_samples_leaf=2`, `random_state=42` | 102.91 | 59.02 | 0.8790 | Uses engineered features + preprocessing pipeline. |

## Notes

- Full precision values are recorded in `results/model_metrics.csv` and `results/training_summary.json`.
- Any hyperparameter updates should append a new row to this table with resulting metrics.
