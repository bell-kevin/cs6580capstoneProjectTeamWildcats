# 🎿 Snowbasin Traffic Dashboard - Complete Setup

## ✅ What's Deployed

### 1. Machine Learning Models on Hugging Face
- **Random Forest**: https://huggingface.co/hazemdhW26/snowbasin-traffic-random-forest
- **LSTM**: https://huggingface.co/hazemdhW26/snowbasin-traffic-lstm

### 2. Free Gradio Space API
- **Space**: https://huggingface.co/spaces/hazemdhW26/snowbasin-traffic-prediction
- **API Endpoint**: `https://hazemdhw26-snowbasin-traffic-prediction.hf.space/api/predict`
- **Features**:
  - ✅ Model selection (Random Forest / LSTM)
  - ✅ Interactive web interface
  - ✅ Automatic REST API
  - ✅ Free tier (no cost!)

### 3. Next.js Dashboard with Claude AI
- **Location**: `dashboard/`
- **Features**:
  - ✅ Traffic predictions with ML models
  - ✅ Real-time UDOT road conditions
  - ✅ Weather station data
  - ✅ Traffic alerts and closures
  - ✅ Snow plow tracking
  - ✅ Interactive chat with Claude
  - ✅ Pretty welcome screen with examples

## 🚀 How to Run

### 1. Start Dashboard
```bash
cd dashboard
npm run dev
```

Visit: http://localhost:3000

### 2. Test in Chat

Ask Claude any of these:

#### Traffic Predictions:
```
"Predict traffic for Saturday at 8am"
"How busy will it be tomorrow at noon?"
"Use Random Forest to predict Friday 5pm traffic"
"Compare traffic for Saturday vs Sunday morning"
```

#### Road Conditions:
```
"Road conditions to Snowbasin"
"How are the roads in Ogden Canyon?"
"Are the plows out on SR-210?"
"Check Little Cottonwood Canyon status"
```

#### Weather Data:
```
"Surface temperature in Parley's Canyon"
"Weather stations near ski resorts"
"Wind speed at mountain passes"
```

#### Combined Requests:
```
"Predict Saturday 8am traffic and check SR-39 conditions"
"How are roads to Alta and what's the forecast?"
```

## 🎨 What's New & Pretty

### 1. Welcome Screen (`components/ChatWelcome.tsx`)
Beautiful card-based layout showing:
- 🧠 Traffic Predictions
- 🏔️ Road Conditions
- 🌡️ Weather Stations
- ⚠️ Alerts & Safety
- 📊 Model Selection Guide
- 💡 Pro Tips

### 2. Enhanced Claude Prompt
Claude now understands:
- How to ask users which model to use
- When to request UDOT data automatically
- How to combine traffic predictions with road conditions
- What to explain about each data source

### 3. Model Selection
Users can choose:
- **Random Forest** (default, recommended) - Fast and reliable
- **LSTM** (coming soon) - Advanced time-series analysis

## 📊 Data Sources

### Traffic Predictions
- **Source**: Hugging Face ML models
- **Updates**: On-demand when requested
- **Models**:
  - Random Forest: 68.99 RMSE, 0.96 R²
  - LSTM: 106.04 RMSE, 0.90 R²

### Road Conditions (UDOT)
- **Source**: Utah Department of Transportation API
- **Updates**: Every 5 minutes (cached)
- **Coverage**:
  - All Utah ski canyons
  - Mountain passes
  - Major highways
  - Weather stations

## 🔧 Configuration

### Environment Variables (Optional)
Create `.env.local` in `dashboard/`:

```env
# Anthropic API for Claude
ANTHROPIC_API_KEY=your-key-here

# Supabase (if using authentication)
NEXT_PUBLIC_SUPABASE_URL=your-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-key

# Custom Gradio Space URL (optional)
NEXT_PUBLIC_HF_SPACE_API_URL=https://hazemdhw26-snowbasin-traffic-prediction.hf.space/api/predict
```

## 🧪 Testing

### Test Gradio Space Directly
```bash
curl -X POST "https://hazemdhw26-snowbasin-traffic-prediction.hf.space/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "data": ["Random Forest", 8, "Saturday", 1, true, false, 28, 65, 10, 18, 0]
  }'
```

Expected response:
```json
{
  "data": ["🚗 **Predicted Traffic: 1250 vehicles/hour** ..."]
}
```

### Test Dashboard API Route
```bash
curl http://localhost:3000/api/predict \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model": "random-forest",
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
  }'
```

Expected response:
```json
{
  "prediction": 1250,
  "model": "random-forest",
  "confidence": "high",
  "timestamp": "2026-03-12T..."
}
```

## 📁 File Structure

```
dashboard/
├── app/
│   └── api/
│       └── predict/
│           └── route.ts         # Calls Gradio Space API
├── lib/
│   ├── claude.ts               # Enhanced system prompt
│   ├── traffic-prediction.ts   # Calls /api/predict
│   ├── udot.ts                 # UDOT real-time data
│   └── uta.ts                  # UTA transit (placeholder)
├── components/
│   └── ChatWelcome.tsx         # Pretty welcome screen
└── ...

hf-space-gradio/
├── app.py                      # Gradio app with model selection
├── requirements.txt
└── README.md
```

## 🎯 User Flow

```
1. User opens dashboard
   ↓
2. Sees welcome screen with examples
   ↓
3. Asks: "Predict Saturday 8am traffic"
   ↓
4. Claude asks: "Use Random Forest model?"
   ↓
5. Claude asks: "Weather conditions or typical?"
   ↓
6. User: "Use typical conditions"
   ↓
7. Claude calls /api/predict
   ↓
8. Dashboard calls Gradio Space API
   ↓
9. Gradio loads model from HF Hub
   ↓
10. Model makes prediction
   ↓
11. Result flows back to user
   ↓
12. Claude explains prediction with context
```

## 💡 Pro Tips

### For Users:
- **Be specific**: "Saturday 8am" is better than "tomorrow"
- **Provide weather**: More accurate predictions
- **Choose model**: Random Forest for speed, LSTM for accuracy (when available)
- **Combine requests**: "Predict traffic AND check roads"

### For Developers:
- **Check logs**: Browser console for API errors
- **Monitor Space**: https://huggingface.co/spaces/hazemdhW26/snowbasin-traffic-prediction/logs
- **Test fallback**: Predictions fall back to simulation if API fails
- **Check confidence**: "high" = real API, "simulated" = fallback

## 🚨 Troubleshooting

### "simulated" confidence in responses
- ❌ Gradio Space API is down or unreachable
- ✅ Check Space status at HF
- ✅ Try curl test to verify API
- ✅ Check browser console for errors

### Space shows "Building"
- ⏳ Wait 2-3 minutes for first build
- ✅ Refresh Space page to see status
- ✅ Check build logs for errors

### No UDOT data in responses
- ❌ User didn't ask about roads/ski resorts
- ✅ Try keywords: "road", "canyon", "ski", "conditions"
- ✅ Check UDOT API key in `lib/udot.ts`

## 📚 Documentation

- **Traffic Predictions**: See `CLAUDE_TRAFFIC_PREDICTION_GUIDE.md`
- **UDOT Integration**: See `UDOT_INTEGRATION_GUIDE.md`
- **HF Setup**: See `SETUP_HF_INFERENCE_API.md`
- **This Guide**: Complete setup overview

## 🎉 Success Checklist

- [ ] Dashboard runs with `npm run dev`
- [ ] Welcome screen appears on first load
- [ ] Chat with Claude works
- [ ] "Predict traffic" returns real predictions (not simulated)
- [ ] Confidence shows "high" not "simulated"
- [ ] Road condition queries return UDOT data
- [ ] Model selection works (Random Forest / LSTM)
- [ ] Gradio Space is running and accessible

## 💰 Cost Breakdown

- **Hugging Face Space**: FREE (community tier)
- **Model hosting**: FREE (public repos)
- **API calls**: FREE (no rate limits for your own Space)
- **UDOT API**: FREE (public data)
- **Claude AI**: $3-$15/month (API usage)
- **Hosting dashboard**: FREE (Vercel/Netlify) or self-hosted

## 🔮 Future Enhancements

- [ ] Add LSTM model support
- [ ] Historical traffic comparison
- [ ] Traffic prediction charts
- [ ] Map visualization of conditions
- [ ] Email/SMS alerts for conditions
- [ ] Multi-day forecasts
- [ ] UTA transit integration
- [ ] Mobile app

---

**Everything is ready! Just run `cd dashboard && npm run dev` and start chatting!** 🎿🚗
