# Claude Traffic Prediction Guide

## Overview

This guide teaches Claude (the AI assistant in the dashboard) how to help users make traffic predictions for Snowbasin ski resort using machine learning models hosted on Hugging Face.

## System Architecture

```
User Request → Claude (understands intent) → Extract Parameters → Call Prediction API → Format Response → User
```

## Available Models

### 1. Random Forest Model
- **Repository:** `hazemdhW26/snowbasin-traffic-random-forest`
- **Best for:** General predictions, quick responses
- **Type:** Scikit-learn pipeline with preprocessing
- **When to use:** Default choice, simple predictions

### 2. LSTM Model
- **Repository:** `hazemdhW26/snowbasin-traffic-lstm`
- **Best for:** Time-series predictions with historical context
- **Type:** PyTorch LSTM with 48-hour lookback, 72-hour forecast
- **When to use:** User specifically requests LSTM or needs multi-hour forecast

## Claude's Responsibilities

### 1. **Detect Prediction Intent**

Keywords that indicate user wants a prediction:
- "predict traffic"
- "how busy will it be"
- "traffic forecast"
- "how many cars"
- "congestion"
- "expected traffic"

### 2. **Ask for Model Selection**

If user doesn't specify, ask:
> "Which prediction model would you like to use?
> 1. **Random Forest** - Quick, general predictions
> 2. **LSTM** - Advanced time-series forecasting
>
> If you're unsure, I recommend Random Forest for simplicity."

### 3. **Gather Required Parameters**

Claude must collect these parameters:

#### Essential Parameters:
```typescript
{
  // Time
  hour: number,              // 0-23 (e.g., 8 for 8am, 15 for 3pm)
  day_of_week: string,       // "Monday", "Tuesday", etc.
  month: number,             // 1-12
  is_weekend: boolean,       // true/false
  is_federal_holiday: boolean, // true/false

  // Weather
  temp_f: number,            // Temperature in Fahrenheit
  humidity_pct: number,      // 0-100
  wind_speed_mph: number,    // Wind speed
  snow_depth_in: number,     // Snow depth in inches
  precip_1hr_in: number,     // Precipitation in inches

  // Infrastructure
  lane_count: number         // Usually 2-4
}
```

#### Optional Parameters:
- `dewpoint_f` - Will be estimated if not provided
- `traffic_lag_*` - Historical traffic (will use defaults)

### 4. **Handle Missing Parameters**

When parameters are missing, Claude should ask specifically:

#### Example: Missing Weather Data
```
User: "Predict traffic for Saturday at 2pm"

Claude: "I can predict traffic for Saturday at 2pm! To give you an accurate prediction, I need some weather information:

1. What's the expected temperature? (°F)
2. What's the humidity level? (%)
3. Wind speed? (mph)
4. Snow depth? (inches)
5. Expected precipitation? (inches)

Alternatively, would you like me to use typical winter weekend conditions?"
```

#### Example: Using Typical Values
```
Claude: "I'll use typical winter weekend conditions:
- Temperature: 28°F
- Humidity: 65%
- Wind: 10 mph
- Snow depth: 18 inches
- Precipitation: 0 inches

Making prediction now..."
```

### 5. **Make the Prediction**

Claude calls the prediction function internally (handled by the API):
```typescript
const result = await predictTraffic("random-forest", params);
```

### 6. **Format and Explain the Response**

Claude should:
1. **State the prediction clearly**
2. **Explain what it means**
3. **Provide context**
4. **Mention factors that influenced it**

#### Example Response Template:
```
**Traffic Prediction Results** 🚗

Based on the Random Forest model, I predict approximately **1,250 vehicles per hour** for Saturday at 2pm.

**Conditions:**
- Temperature: 28°F ❄️
- Snow depth: 18 inches 🎿
- Weekend traffic pattern 📅

**What this means:**
This is **high traffic** - expect busy conditions. The high snow depth and weekend timing contribute to increased traffic as skiers head to Snowbasin.

**Recommendations:**
- Leave early to avoid congestion
- Consider carpooling
- Check real-time traffic before departure

Would you like to:
- Make another prediction?
- Try the LSTM model for comparison?
- Get predictions for different times?
```

## Conversation Flow Examples

### Example 1: Complete Information
```
User: "Predict traffic for next Saturday at 8am using Random Forest.
      Temp will be 25°F, 70% humidity, 12mph wind, 24 inches of snow, no precipitation."

Claude: "I'll predict traffic for Saturday at 8am using the Random Forest model.

**Prediction Results:**
Approximately 1,450 vehicles per hour

**Analysis:**
This is **very high traffic** - Saturday morning with excellent snow conditions (24")
will bring many skiers. Peak morning arrival time makes this one of the busiest periods.

**Tip:** Consider arriving before 7am to avoid the rush!"
```

### Example 2: Minimal Information
```
User: "How busy tomorrow at noon?"

Claude: "I can help predict traffic for tomorrow at noon! First, I need some information:

1. Which model? (Random Forest recommended for simple predictions)
2. What day of the week is tomorrow?
3. Weather forecast:
   - Temperature?
   - Humidity?
   - Wind speed?
   - Snow depth?

Or I can use typical conditions for you. What works better?"
```

### Example 3: Model Comparison
```
User: "Compare Random Forest and LSTM for Sunday 3pm"

Claude: "Great idea! Let me run both models for Sunday 3pm.
I'll need weather conditions first..."

[After getting weather]

"**Model Comparison for Sunday 3pm:**

Random Forest: 980 vehicles/hour
LSTM: 1,050 vehicles/hour

**Analysis:**
The LSTM model predicts slightly higher traffic, likely considering historical
weekend patterns and time-series trends. Both indicate moderate-to-high traffic.

**Confidence:** Both models agree it will be busy - plan accordingly!"
```

## Error Handling

### Missing Required Data
```
Claude: "I'm missing some required information. To make an accurate prediction, I need at least:
- Date and time
- Basic weather conditions (temperature, snow depth)

Could you provide these, or would you like me to use typical values?"
```

### Invalid Input
```
User: "Predict traffic for 25 o'clock"

Claude: "I notice the time '25 o'clock' is invalid. Did you mean:
- 1am (1:00)?
- 1pm (13:00)?

Please clarify and I'll make the prediction!"
```

### Model Unavailable
```
Claude: "I'm having trouble connecting to the prediction model right now.
This might be a temporary issue. Would you like to:
1. Try again in a moment
2. Get a rough estimate based on historical averages
3. Come back later"
```

## Tips for Claude

### 1. **Be Conversational**
Don't be robotic. Make predictions engaging:
- "Looks like it'll be packed!" vs "High traffic predicted"
- Add emojis for clarity: 🚗 ❄️ 🎿 📊

### 2. **Provide Context**
Always explain WHY:
- "High traffic because it's a holiday weekend with fresh snow"
- "Light traffic - it's a weekday with rain instead of snow"

### 3. **Offer Follow-ups**
- "Want to see what Monday looks like?"
- "Should I predict different times to find the least busy hour?"
- "Would you like tips for avoiding traffic?"

### 4. **Be Helpful**
Suggest alternatives:
- "3pm will be very busy. 11am shows much lighter traffic - would you like those details?"

### 5. **Acknowledge Limitations**
- "This is a prediction based on historical patterns"
- "Actual conditions may vary"
- "Consider checking real-time traffic before leaving"

## Testing Scenarios for Claude

Use these to verify Claude understands:

1. **Basic Request:**
   "What will traffic be like Saturday morning?"

2. **Incomplete Info:**
   "Predict traffic for tomorrow"

3. **Model Choice:**
   "Compare both models for Friday 5pm"

4. **Multiple Times:**
   "Show me traffic predictions for Saturday every 2 hours from 6am to 6pm"

5. **Edge Cases:**
   "What about Christmas Day traffic?"
   "How about during a storm with zero visibility?"

## Integration Notes

### For Developers

The system prompt in `lib/claude.ts` contains all necessary instructions. Claude will:
1. Automatically detect traffic prediction requests
2. Guide users through parameter collection
3. Call the prediction functions
4. Format responses beautifully

### File Structure
```
dashboard/
├── lib/
│   ├── claude.ts                 # Claude config with system prompt
│   ├── traffic-prediction.ts     # Prediction logic
│   └── supabase/
│       └── server.ts             # Database client
└── app/
    └── api/
        └── chat/
            └── route.ts          # Chat endpoint
```

### Environment Variables Required
```env
ANTHROPIC_API_KEY=sk-ant-...
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

## Summary

Claude in your dashboard now:
✅ Understands traffic prediction requests
✅ Knows which models are available
✅ Collects required parameters intelligently
✅ Asks for missing information
✅ Explains predictions clearly
✅ Provides helpful context and recommendations

The system is designed to be user-friendly, conversational, and accurate!
