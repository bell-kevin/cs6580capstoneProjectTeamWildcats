# Setup Hugging Face Inference API for Traffic Predictions

## ✅ What You Have Now

Your models are uploaded to Hugging Face:
- ✅ [Random Forest Model](https://huggingface.co/hazemdhW26/snowbasin-traffic-random-forest)
- ✅ [LSTM Model](https://huggingface.co/hazemdhW26/snowbasin-traffic-lstm)

## 🚀 Simple Setup (Using HF Inference API - FREE!)

Instead of building a separate backend, we'll use **Hugging Face's free Serverless Inference API** by adding a custom handler to your model repository.

### Step 1: Add Custom Handler to Random Forest Model

1. **Go to your Random Forest repository:**
   https://huggingface.co/hazemdhW26/snowbasin-traffic-random-forest

2. **Click "Files and versions" → "Add file" → "Upload files"**

3. **Upload these files from `hf-handlers/` folder:**
   - `handler_random_forest.py` → **Rename to `handler.py`**
   - `requirements_handler.txt` → **Rename to `requirements.txt`**

4. **Commit the changes**

That's it! Hugging Face will automatically create an Inference API endpoint.

### Step 2: Test the API

Once the handler is uploaded, wait 1-2 minutes for HF to build the endpoint, then test:

```bash
curl https://api-inference.huggingface.co/models/hazemdhW26/snowbasin-traffic-random-forest \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "hour": 8,
      "day_of_week": "Saturday",
      "month": 1,
      "is_weekend": true,
      "is_federal_holiday": false,
      "temp_f": 28,
      "humidity_pct": 65,
      "wind_speed_mph": 10,
      "snow_depth_in": 18,
      "precip_1hr_in": 0
    }
  }'
```

**Expected response:**
```json
[{
  "prediction": 1250.5,
  "model": "random-forest",
  "confidence": "high"
}]
```

### Step 3: Update Dashboard (Already Done!)

I've already updated your dashboard to use the HF Inference API:
- ✅ `dashboard/app/api/predict/route.ts` - Calls HF Inference API
- ✅ Automatic fallback to simulation if API fails
- ✅ No environment variables needed (uses public endpoints)

### Step 4: Run Your Dashboard

```bash
cd dashboard
npm run dev
```

Then ask Claude in the chat:
```
"Predict traffic for Saturday at 8am with 18 inches of snow, temp 28F"
```

## 📊 How It Works

```
User asks Claude
    ↓
Claude extracts parameters
    ↓
Calls /api/predict (Next.js API route)
    ↓
Calls HF Inference API (with your custom handler)
    ↓
Handler loads model & makes prediction
    ↓
Returns result to dashboard
    ↓
Claude explains result to user
```

## 💰 Cost: **FREE!**

- Hugging Face Serverless Inference API is free for public models
- ~1000 requests/hour rate limit
- First request may be slow (cold start ~10-20 sec)
- Subsequent requests are fast (<1 sec)

## 🔧 What Files Changed

### Created:
1. `hf-handlers/handler_random_forest.py` - Custom handler for RF model
2. `hf-handlers/requirements_handler.txt` - Dependencies for handler
3. `hf-handlers/DEPLOYMENT_GUIDE.md` - Detailed instructions
4. `dashboard/app/api/predict/route.ts` - Next.js API route

### Files You Created (FastAPI backend - NOT NEEDED):
- `hf-space-backend/` folder - You can delete this, we don't need it!

## 📝 Next Steps

1. **Upload handler.py to HF repository** (Step 1 above)
2. **Test the endpoint** (Step 2 above)
3. **Run dashboard and test predictions**

## 🎯 Testing Checklist

- [ ] Upload `handler.py` and `requirements.txt` to HF repository
- [ ] Wait 2 minutes for HF to build endpoint
- [ ] Test with curl command
- [ ] Run dashboard with `npm run dev`
- [ ] Ask Claude: "Predict traffic for Saturday 8am"
- [ ] Verify real prediction (not simulation)

## 🚨 Troubleshooting

**"Model is loading" error:**
- First request after uploading handler takes 10-20 seconds
- Wait and try again

**"Error loading model":**
- Check handler.py and requirements.txt were uploaded correctly
- Check filenames are exactly `handler.py` and `requirements.txt`

**Dashboard shows "simulated" confidence:**
- API call failed or returned error
- Check browser console for error messages
- Verify handler is uploaded to HF repository

## 📚 References

- [Hugging Face Inference API Docs](https://huggingface.co/docs/api-inference/index)
- [Custom Inference Handlers](https://huggingface.co/docs/api-inference/detailed_parameters#custom-inference-handler)
- [Hosting scikit-learn Models on HF Hub](https://medium.com/nlplanet/hosting-scikit-learn-models-on-the-hugging-face-hub-with-skops-2349fcba1ec2)

---

**Sources:**
- [Hosting scikit-learn Models on the Hugging Face Hub with skops | Medium](https://medium.com/nlplanet/hosting-scikit-learn-models-on-the-hugging-face-hub-with-skops-2349fcba1ec2)
- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Deploying a Deep Learning Model on Hugging Face](https://learnopencv.com/deploy-deep-learning-model-huggingface-spaces/)
- [The Complete Hugging Face Primer for 2026 | KDnuggets](https://www.kdnuggets.com/the-complete-hugging-face-primer-for-2026)
