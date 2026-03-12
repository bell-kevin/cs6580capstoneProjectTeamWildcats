# Hugging Face Integration Guide

This guide explains how to train models and upload them to Hugging Face Hub, then load them in your dashboard.

## Prerequisites

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a Hugging Face account at [huggingface.co](https://huggingface.co)

3. Get your Hugging Face API token:
   - Go to Settings > Access Tokens
   - Create a new token with write permissions
   - Save the token securely

## Training and Uploading Models

### Option 1: Using Environment Variable (Recommended)

```bash
# Set your Hugging Face token
export HF_TOKEN="your_token_here"  # Linux/Mac
set HF_TOKEN=your_token_here       # Windows CMD
$env:HF_TOKEN="your_token_here"    # Windows PowerShell

# Train and upload models
python src/train_model.py \
    --push-to-hf \
    --hf-repo-name "your-username/snowbasin-traffic"
```

### Option 2: Using Command Line Argument

```bash
python src/train_model.py \
    --push-to-hf \
    --hf-repo-name "your-username/snowbasin-traffic" \
    --hf-token "your_token_here"
```

### Additional Options

```bash
# Create private repositories
python src/train_model.py \
    --push-to-hf \
    --hf-repo-name "your-username/snowbasin-traffic" \
    --hf-private

# Use custom test size and split strategy
python src/train_model.py \
    --push-to-hf \
    --hf-repo-name "your-username/snowbasin-traffic" \
    --test-size 0.25 \
    --split-strategy time
```

## What Gets Uploaded

The script creates **two separate repositories**:

### 1. Random Forest Model Repository
`your-username/snowbasin-traffic-random-forest`

Contains:
- `champion_model.joblib` - The trained sklearn pipeline
- `README.md` - Model card with metrics and usage instructions

### 2. LSTM Model Repository
`your-username/snowbasin-traffic-lstm`

Contains:
- `champion_lstm.pth` - PyTorch model weights
- `lstm_preprocessor.joblib` - Feature preprocessor
- `lstm_target_scaler.joblib` - Target variable scaler
- `lstm_config.json` - Model configuration
- `README.md` - Model card with metrics and usage instructions

## Loading Models in Your Dashboard

### Option 1: Using the Helper Script

```python
from src.load_from_huggingface import load_random_forest_model, load_lstm_model

# Load Random Forest model
rf_model = load_random_forest_model("your-username/snowbasin-traffic-random-forest")

# Load LSTM model
lstm_dict = load_lstm_model("your-username/snowbasin-traffic-lstm")
lstm_model = lstm_dict["model"]
preprocessor = lstm_dict["preprocessor"]
target_scaler = lstm_dict["target_scaler"]
```

### Option 2: Manual Loading

#### Random Forest:
```python
import joblib
from huggingface_hub import hf_hub_download

model_path = hf_hub_download(
    repo_id="your-username/snowbasin-traffic-random-forest",
    filename="champion_model.joblib"
)
rf_model = joblib.load(model_path)

# Make predictions
predictions = rf_model.predict(features_df)
```

#### LSTM:
```python
import torch
import joblib
import json
from huggingface_hub import hf_hub_download
from src.load_from_huggingface import TrafficLSTM

# Download files
model_path = hf_hub_download(
    repo_id="your-username/snowbasin-traffic-lstm",
    filename="champion_lstm.pth"
)
preprocessor_path = hf_hub_download(
    repo_id="your-username/snowbasin-traffic-lstm",
    filename="lstm_preprocessor.joblib"
)
scaler_path = hf_hub_download(
    repo_id="your-username/snowbasin-traffic-lstm",
    filename="lstm_target_scaler.joblib"
)
config_path = hf_hub_download(
    repo_id="your-username/snowbasin-traffic-lstm",
    filename="lstm_config.json"
)

# Load everything
with open(config_path) as f:
    config = json.load(f)

preprocessor = joblib.load(preprocessor_path)
target_scaler = joblib.load(scaler_path)

model = TrafficLSTM(input_size=config["input_size"])
model.load_state_dict(torch.load(model_path, weights_only=True))
model.eval()

# Make predictions
X_processed = preprocessor.transform(features_df)
X_tensor = torch.tensor(X_processed, dtype=torch.float32)

with torch.no_grad():
    predictions = model(X_tensor)
    predictions_original = target_scaler.inverse_transform(
        predictions.cpu().numpy().reshape(-1, 1)
    ).flatten()
```

## Features Required for Predictions

Both models expect the following features:

**Temporal Features:**
- `hour` (0-23)
- `day_of_week` (Monday, Tuesday, etc.)
- `month` (1-12)
- `is_weekend` (0 or 1)
- `is_federal_holiday` (0 or 1)
- `is_peak_hour` (0 or 1)

**Weather Features:**
- `temp_f` (temperature in Fahrenheit)
- `dewpoint_f` (dewpoint in Fahrenheit)
- `humidity_pct` (humidity percentage)
- `wind_speed_mph` (wind speed in mph)
- `snow_depth_in` (snow depth in inches)
- `precip_1hr_in` (precipitation in last hour in inches)

**Infrastructure:**
- `lane_count` (number of lanes)

**Engineered Features:**
- `temp_dewpoint_spread` (temp_f - dewpoint_f)
- `distance_to_holiday_weekend` (days to nearest holiday weekend)
- Traffic lag features: `traffic_lag_1`, `traffic_lag_2`, `traffic_lag_3`, `traffic_lag_6`, `traffic_lag_12`, `traffic_lag_24`, `traffic_lag_168`
- Cyclical encodings: `hour_sin`, `hour_cos`, `day_of_week_sin`, `day_of_week_cos`, `month_sin`, `month_cos`

## Troubleshooting

### Authentication Errors
If you get authentication errors, make sure:
1. Your HF_TOKEN is set correctly
2. You have write permissions for the repositories
3. For private repos, you need to pass the token when loading

### Model Loading Errors
If models fail to load:
1. Check that the repository names are correct
2. Verify the files were uploaded successfully on huggingface.co
3. For LSTM, ensure you have the TrafficLSTM class definition

### Feature Errors
If you get feature-related errors:
1. Make sure all required features are present in your DataFrame
2. Check that feature names match exactly (case-sensitive)
3. Use the feature engineering functions from `train_model.py` to create derived features

## Example Integration in Dashboard

```python
import gradio as gr
from src.load_from_huggingface import load_random_forest_model, predict_with_random_forest
from src.train_model import add_engineered_features
import pandas as pd

# Load model once at startup
rf_model = load_random_forest_model("your-username/snowbasin-traffic-random-forest")

def predict_traffic(hour, day_of_week, temp_f, humidity_pct, ...):
    # Create feature DataFrame
    features = pd.DataFrame({
        'hour': [hour],
        'day_of_week': [day_of_week],
        'temp_f': [temp_f],
        'humidity_pct': [humidity_pct],
        # ... add all other features
    })

    # Engineer features
    features = add_engineered_features(features)

    # Make prediction
    prediction = predict_with_random_forest(rf_model, features)

    return prediction[0]

# Create Gradio interface
interface = gr.Interface(
    fn=predict_traffic,
    inputs=[...],  # Define your inputs
    outputs="number"
)

interface.launch()
```

## Next Steps

1. Train your models with the desired parameters
2. Upload to Hugging Face using `--push-to-hf`
3. Integrate the model loading code into your dashboard
4. Test predictions with sample data
5. Deploy your dashboard with the Hugging Face models

## Support

For issues or questions:
- Check model cards on Hugging Face for usage examples
- Review `src/load_from_huggingface.py` for implementation details
- Check `src/train_model.py` for feature engineering code
