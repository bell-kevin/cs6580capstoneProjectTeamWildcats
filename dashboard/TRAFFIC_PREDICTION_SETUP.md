# Traffic Prediction Dashboard Setup

## Quick Start

Your dashboard now has AI-powered traffic predictions! Claude can help users predict Snowbasin traffic using models from Hugging Face.

## What Was Added

### 1. Files Created

```
dashboard/
├── lib/
│   ├── claude.ts                    # Claude AI with traffic prediction prompt
│   ├── traffic-prediction.ts        # Prediction functions
│   ├── uta.ts                       # UTA transit integration
│   └── supabase/
│       └── server.ts                # Supabase client
├── CLAUDE_TRAFFIC_PREDICTION_GUIDE.md  # Full guide for Claude
└── TRAFFIC_PREDICTION_SETUP.md         # This file
```

### 2. How It Works

1. **User asks for prediction** in chat
   - "Predict traffic for Saturday at 8am"
   - "How busy will it be tomorrow?"

2. **Claude understands** using system prompt
   - Detects intent
   - Asks for model choice (Random Forest or LSTM)
   - Gathers required parameters

3. **Claude asks for missing info**
   - Weather conditions
   - Date/time details
   - Or offers to use typical values

4. **Prediction is made** using HuggingFace models
   - Calls `predictTraffic()` function
   - Currently uses simulation (TODO: connect real models)

5. **Results are explained** to user
   - Clear prediction number
   - Context and analysis
   - Recommendations

## Models Available

### Random Forest (Public)
- **Repo:** `hazemdhW26/snowbasin-traffic-random-forest`
- **URL:** https://huggingface.co/hazemdhW26/snowbasin-traffic-random-forest
- **Type:** Scikit-learn pipeline
- **Best for:** Quick, general predictions

### LSTM (Public)
- **Repo:** `hazemdhW26/snowbasin-traffic-lstm`
- **URL:** https://huggingface.co/hazemdhW26/snowbasin-traffic-lstm
- **Type:** PyTorch LSTM
- **Best for:** Time-series forecasting

Both models are **public** - no token needed to access!

## Required Parameters

When users ask for predictions, Claude needs:

### Time Information
- `hour` (0-23)
- `day_of_week` (Monday, Tuesday, etc.)
- `month` (1-12)
- `is_weekend` (true/false)
- `is_federal_holiday` (true/false)

### Weather Conditions
- `temp_f` (temperature in Fahrenheit)
- `humidity_pct` (0-100)
- `wind_speed_mph`
- `snow_depth_in`
- `precip_1hr_in`

### Infrastructure
- `lane_count` (typically 2-4)

## Example Conversations

### Example 1: Simple Request
```
User: "Predict traffic for next Saturday at 8am"

Claude: "I can help predict traffic for Saturday at 8am!
Which model would you like to use?
1. Random Forest (recommended for quick predictions)
2. LSTM (advanced time-series forecasting)

Also, I'll need weather conditions:
- Temperature (°F)
- Humidity (%)
- Wind speed (mph)
- Snow depth (inches)
- Precipitation (inches)

Or I can use typical winter Saturday conditions?"

User: "Use Random Forest with typical conditions"

Claude: "Using Random Forest with typical winter conditions...

**Prediction: 1,350 vehicles/hour**

This is HIGH traffic - Saturday mornings with good snow
are the busiest times. Consider arriving before 7am!"
```

### Example 2: Detailed Request
```
User: "Random Forest prediction for Sunday 2pm.
      Temp 30°F, humidity 60%, wind 8mph,
      snow depth 20 inches, no precipitation"

Claude: "**Traffic Prediction Results**

Predicted: 1,100 vehicles/hour
Model: Random Forest
Time: Sunday 2pm

**Conditions:**
- Temperature: 30°F ❄️
- Snow: 20 inches 🎿
- Weekend

**Analysis:**
Moderate-high traffic expected. Great skiing
conditions will attract visitors. Sunday afternoons
are typically busy as day-skiers head home.

Would you like predictions for other times?"
```

## Environment Setup

### Required Environment Variables

Create `.env.local` in the dashboard folder:

```env
# Anthropic API for Claude
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Supabase
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key

# Optional: Hugging Face (only if using private repos)
# HUGGINGFACE_TOKEN=hf_your_token_here  # Not needed for public repos!
```

### Install Dependencies

```bash
cd dashboard
npm install @anthropic-ai/sdk
npm install @supabase/ssr
```

## Testing

### Test the System Prompt

Try these queries in the chat:

1. **Basic:**
   - "Predict traffic for Saturday morning"
   - "How busy will it be tomorrow at noon?"

2. **Model Selection:**
   - "Use LSTM to predict Friday 5pm traffic"
   - "Compare Random Forest and LSTM"

3. **Edge Cases:**
   - "What about Christmas Day?"
   - "Predict traffic at midnight"

### Expected Behavior

✅ Claude asks for model choice if not specified
✅ Claude requests missing parameters
✅ Claude offers to use typical values
✅ Predictions are formatted nicely
✅ Claude explains the results
✅ Claude provides recommendations

## Next Steps (TODOs)

### Phase 1: Current (Simulation)
- ✅ System prompt created
- ✅ Parameter extraction
- ✅ Simulated predictions
- ✅ Response formatting

### Phase 2: Real Model Integration

Replace the `simulatePrediction()` function in `traffic-prediction.ts` with actual model calls:

```typescript
// Option 1: Call Python microservice
export async function predictTraffic(model: ModelType, params: TrafficPredictionParams) {
  const response = await fetch('http://your-python-api/predict', {
    method: 'POST',
    body: JSON.stringify({ model, params }),
  });
  return response.json();
}

// Option 2: Direct HuggingFace Inference API
export async function predictTraffic(model: ModelType, params: TrafficPredictionParams) {
  const repoId = model === 'random-forest'
    ? 'hazemdhW26/snowbasin-traffic-random-forest'
    : 'hazemdhW26/snowbasin-traffic-lstm';

  // Call HF Inference API or your backend
  // ...
}
```

### Phase 3: Enhancements
- [ ] Cache predictions
- [ ] Add visualization charts
- [ ] Store prediction history
- [ ] Compare predictions vs actual
- [ ] Multi-hour forecasts for LSTM
- [ ] Real-time traffic lag data

## Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │ "Predict Saturday 8am"
       ↓
┌─────────────────────────┐
│  Next.js Dashboard      │
│  (/app/api/chat)        │
└──────┬──────────────────┘
       │
       ↓
┌─────────────────────────┐
│  Claude AI              │
│  (lib/claude.ts)        │
│  - System prompt        │
│  - Understands intent   │
│  - Asks for params      │
└──────┬──────────────────┘
       │
       ↓
┌─────────────────────────┐
│  Prediction Function    │
│  (lib/traffic-pred.ts)  │
│  - Validate params      │
│  - Call model           │
│  - Format result        │
└──────┬──────────────────┘
       │
       ↓
┌─────────────────────────┐
│  HuggingFace Models     │
│  - Random Forest        │
│  - LSTM                 │
└─────────────────────────┘
       │
       ↓
┌─────────────────────────┐
│  Response to User       │
│  - Prediction number    │
│  - Analysis             │
│  - Recommendations      │
└─────────────────────────┘
```

## Troubleshooting

### Claude doesn't detect prediction requests
- Check the system prompt in `lib/claude.ts`
- Verify keywords are being matched
- Look at console logs in the API route

### Prediction function errors
- Check parameter formatting
- Verify all required fields are present
- Look for type mismatches

### Models not loading
- Ensure repos are public on HuggingFace
- Check repo names match exactly
- Verify network connectivity

## Support

- **Full Guide:** See `CLAUDE_TRAFFIC_PREDICTION_GUIDE.md`
- **Model Integration:** See `../HUGGINGFACE_INTEGRATION.md`
- **Issues:** Check dashboard logs in browser console

## Summary

✨ Your dashboard now has intelligent traffic prediction!
🤖 Claude understands natural language requests
📊 Two ML models available (Random Forest & LSTM)
🎿 Optimized for Snowbasin ski resort traffic
🚀 Ready to test with simulated predictions
