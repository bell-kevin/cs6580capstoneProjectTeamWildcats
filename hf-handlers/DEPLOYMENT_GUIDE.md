# Deploying Custom Handlers to Hugging Face

## Step 1: Upload handler.py to your Random Forest repository

1. Go to https://huggingface.co/hazemdhW26/snowbasin-traffic-random-forest
2. Click "Files and versions"
3. Click "Add file" → "Upload files"
4. Upload these files:
   - `handler_random_forest.py` → rename to `handler.py`
   - `requirements_handler.txt` → rename to `requirements.txt`
5. Commit the changes

## Step 2: Test the Inference API

Once uploaded, your model will be available at:
```
https://api-inference.huggingface.co/models/hazemdhW26/snowbasin-traffic-random-forest
```

### Test with curl:

```bash
curl https://api-inference.huggingface.co/models/hazemdhW26/snowbasin-traffic-random-forest \
  -X POST \
  -d '{"inputs": {
    "hour": 8,
    "day_of_week": "Saturday",
    "month": 1,
    "is_weekend": true,
    "is_federal_holiday": false,
    "temp_f": 28,
    "humidity_pct": 65,
    "wind_speed_mph": 10,
    "snow_depth_in": 18,
    "precip_1hr_in": 0,
    "lane_count": 2
  }}' \
  -H "Content-Type: application/json"
```

### Test with Python:

```python
import requests

API_URL = "https://api-inference.huggingface.co/models/hazemdhW26/snowbasin-traffic-random-forest"

payload = {
    "inputs": {
        "hour": 8,
        "day_of_week": "Saturday",
        "month": 1,
        "is_weekend": True,
        "is_federal_holiday": False,
        "temp_f": 28,
        "humidity_pct": 65,
        "wind_speed_mph": 10,
        "snow_depth_in": 18,
        "precip_1hr_in": 0,
        "lane_count": 2
    }
}

response = requests.post(API_URL, json=payload)
print(response.json())
```

## Step 3: Update Dashboard Environment Variable

In your dashboard folder, create or update `.env.local`:

```env
# Hugging Face Inference API
NEXT_PUBLIC_HF_RF_API_URL=https://api-inference.huggingface.co/models/hazemdhW26/snowbasin-traffic-random-forest
```

## Notes:

- The Serverless Inference API is **FREE** for public models
- Cold start: First request may be slow (10-20 seconds) as model loads
- Subsequent requests are fast (< 1 second)
- Rate limit: ~1000 requests/hour for free tier
- For LSTM model, you would need a similar handler (more complex due to sequence requirements)

## Advantages:

✅ No server management
✅ Free for public models
✅ Automatic scaling
✅ Global CDN
✅ HTTPS by default

You no longer need the FastAPI backend I created - just use the Inference API directly!
