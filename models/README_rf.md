---
tags:
- traffic-prediction
- sklearn
- pytorch
- time-series
library_name: sklearn
---

# snowbasin-traffic-rf

## Model Description
This model predicts traffic counts for Snowbasin ski resort based on time, weather, and historical traffic data.

## Model Type
RANDOM_FOREST

## Performance Metrics
- RMSE: 68.98842011684695
- MAE: 39.528401612882405
- R2: 0.9595977602814381

## Features
The model uses the following features:
- Temporal features (hour, day of week, month with cyclical encoding)
- Weather data (temperature, humidity, precipitation, wind speed, snow depth)
- Traffic lag features (1, 2, 3, 6, 12, 24, 168 hours)
- Special features (peak hours, federal holidays, holiday weekends)

## Usage

### Random Forest Model
```python
import joblib
from huggingface_hub import hf_hub_download

# Download model
model_path = hf_hub_download(repo_id="YOUR_USERNAME/snowbasin-traffic-rf", filename="champion_model.joblib")
model = joblib.load(model_path)

# Make predictions
predictions = model.predict(X)
```

### LSTM Model
```python
import torch
from huggingface_hub import hf_hub_download

# Download model
model_path = hf_hub_download(repo_id="YOUR_USERNAME/snowbasin-traffic-rf", filename="champion_lstm.pth")

# Load model architecture (you'll need the TrafficLSTM class)
model = TrafficLSTM(input_size=33)  # Adjust input_size based on your features
model.load_state_dict(torch.load(model_path))
model.eval()
```

## Training Details
- Split Strategy: time
- Train Rows: 55776
- Test Rows: 13944

## Citation
Developed by Team Wildcats for CS6580 Capstone Project - Spring 2026
