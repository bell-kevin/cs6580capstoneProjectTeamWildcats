# UDOT Integration Guide

## Overview

The dashboard now integrates with the **Utah Department of Transportation (UDOT) API** to provide real-time road conditions, weather data, and ski canyon information.

## API Key

**API Key:** `d855f6463c5e49a092325ab22cf7640a`

This key is configured in `dashboard/lib/udot.ts` and provides access to:
- Road conditions
- Weather stations
- Traffic alerts
- Snow plow locations
- Mountain pass conditions

## How It Works

### Automatic Detection

When users ask about roads or ski resorts, Claude automatically fetches UDOT data:

#### Trigger Keywords:
- **General roads:** "road", "highway", "i-80", "i-15", "driving", "conditions"
- **Ski areas:** "ski", "canyon", "snowbasin", "alta", "snowbird", "brighton", "solitude"
- **Specific routes:** "sr-210", "sr-190", "sr-39", "us-189"
- **Conditions:** "snow plow", "closure", "traction", "weather station"

### User Experience

```
User: "What are the road conditions to Snowbasin?"

Claude: [Automatically fetches UDOT data]

**UDOT REAL-TIME SKI CANYON DATA:**

**Mountain Passes & Canyons:**

**Ogden Canyon (SR-39)**
- Status: Wet roads, use caution
- ⚠️ No traction devices required
- Surface Temp: 34°F
- Air Temp: 38°F
- Conditions: Partly cloudy, light rain

**Road Conditions:**

**SR-39 Ogden Canyon** (Mile 5-12)
- Conditions: Wet pavement
- Surface: Damp

**⚠️ Traffic Alerts:**
[Any active alerts]

**🚜 Active Snow Plows:**
- SR-39 (Northbound) - 25 mph

**🌡️ Weather Stations:**

**Ogden Canyon Station** (Mile 8)
- Air Temp: 38°F
- Surface Temp: 34°F
- Wind: 12 mph (gusts 18 mph)
- Snow Depth: 6"
- Visibility: 5 mi
```

## Available Data

### 1. Road Conditions
- Road name and location
- Current conditions description
- Travel restrictions (if any)
- Surface conditions
- Last updated timestamp

### 2. Mountain Passes
- Pass name and elevation
- Road status
- Travel restrictions
- Surface and air temperature
- Wind conditions
- Last updated timestamp

### 3. Traffic Alerts
- Severity level (low, medium, high)
- Road name and location
- Description
- Start and end times

### 4. Snow Plows
- Active plow locations
- Road name and direction
- Current speed
- GPS coordinates
- Last report time

### 5. Weather Stations
- Station name and location
- Air and surface temperature
- Wind speed and gusts
- Precipitation
- Snow depth
- Visibility

## API Endpoints Used

All endpoints use the base URL: `https://api.udot.utah.gov/api/v1`

1. **Road Conditions:** `/roadconditions?apiKey={key}`
2. **Weather Stations:** `/weatherstations?apiKey={key}`
3. **Alerts:** `/alerts?apiKey={key}`
4. **Snow Plows:** `/plows?apiKey={key}`

## Caching

To reduce API calls and improve performance:
- **Road/weather/alerts:** 5 minutes cache
- **Snow plows:** 1 minute cache (more frequent updates)

## Ski Canyon Focus

The system automatically filters for ski-related roads when it detects ski canyon queries:

**Ski Canyon Keywords:**
- cottonwood, parley, ogden, provo canyon
- alta, snowbird, brighton, solitude
- park city, deer valley, sundance
- powder mountain, snowbasin

**Filtered Routes:**
- SR-210 (Little Cottonwood Canyon)
- SR-190 (Big Cottonwood Canyon)
- SR-39 (Ogden Canyon)
- US-189 (Provo Canyon)

## Example Queries

### Example 1: General Road Conditions
```
User: "What are road conditions on I-80?"

Claude: [Fetches general UDOT road data]

**UDOT REAL-TIME ROAD DATA:**

**Road Conditions:**
- I-80 Eastbound (Mile 145-150): Clear, dry pavement
- I-80 Westbound (Mile 150-145): Clear, dry pavement

**Weather Stations:**
- Parleys Summit: 32°F, Wind 15mph, Clear
```

### Example 2: Ski Canyon Specific
```
User: "How are the roads to Alta?"

Claude: [Fetches ski canyon data - SR-210]

**UDOT REAL-TIME SKI CANYON DATA:**

**Mountain Passes:**
**Little Cottonwood Canyon (SR-210)**
- Status: Snow packed roads
- ⚠️ 4WD or chains required
- Surface Temp: 28°F
- Conditions: Heavy snow

**Active Snow Plows:**
- SR-210 (Uphill) - 15 mph
- SR-210 (Downhill) - 20 mph
```

### Example 3: Weather Stations
```
User: "What's the surface temperature in Parley's Canyon?"

Claude: [Fetches weather station data]

**Weather Stations:**
**Parley's Summit** (Mile 132)
- Air Temp: 28°F
- Surface Temp: 24°F ❄️
- Wind: 22 mph (gusts 35 mph)
- Visibility: 2 mi
```

### Example 4: Traffic Predictions + Road Conditions
```
User: "Predict traffic to Snowbasin Saturday 8am and check road conditions"

Claude: [Fetches both prediction + UDOT data]

**Traffic Prediction:**
1,350 vehicles/hour - HIGH traffic expected

**UDOT REAL-TIME SKI CANYON DATA:**
**Ogden Canyon (SR-39)**
- Status: Snow packed
- ⚠️ 4WD recommended
- Active plows on route

**Recommendation:**
Leave early (before 7am) due to high predicted traffic
and current snow conditions requiring 4WD.
```

## Integration with Traffic Predictions

UDOT data complements traffic predictions by providing:
1. **Real-time conditions** - actual current state
2. **Weather data** - for more accurate predictions
3. **Alerts** - unexpected closures or delays
4. **Context** - helps explain traffic patterns

## Error Handling

If UDOT API is unavailable:
- System logs the error
- Returns empty data (doesn't break chat)
- Claude continues without real-time data
- User doesn't see error messages

## Data Freshness

- Data is fetched on-demand when user asks
- Cached for 1-5 minutes to reduce API load
- "Last updated" timestamps shown to user
- Most critical data (plows) updated most frequently

## Files Modified/Created

### Created:
1. **`dashboard/lib/udot.ts`** - UDOT API integration
   - All API calls
   - Data parsing
   - Response formatting

### Modified:
2. **`dashboard/app/api/chat/route.ts`** - Uncommented UDOT integration
   - Import statements
   - `fetchRoadDataIfNeeded()` function
   - Added to both authenticated and guest chat

## Testing

### Test Queries:
1. "What are road conditions to Snowbasin?"
2. "Are the plows out on SR-210?"
3. "Check weather stations in Big Cottonwood Canyon"
4. "Any closures on I-80?"
5. "Road conditions and traffic prediction for Saturday"

### Expected Behavior:
✅ Claude detects road/ski keywords
✅ UDOT data is fetched automatically
✅ Data is formatted nicely with emojis
✅ Results include relevant sections (passes, conditions, alerts, plows)
✅ Empty sections are omitted
✅ Works in both guest and authenticated mode

## Monitoring

Check console logs for:
- API errors: `"UDOT API error:"`
- Fetch errors: `"Error fetching UDOT..."`
- Empty responses: May indicate API issues or filtering too aggressively

## Rate Limits

UDOT API rate limits (check their documentation):
- Our caching helps stay within limits
- 5-minute cache for most endpoints
- Consider implementing request counting if needed

## Future Enhancements

Potential additions:
- [ ] Camera feeds from UDOT
- [ ] Variable message sign data
- [ ] Construction zone information
- [ ] Incident reports
- [ ] Historical comparison
- [ ] Map visualization of conditions

## API Documentation

For full UDOT API documentation:
- Visit: https://udot.utah.gov/connect/business/api/
- Contact UDOT for additional endpoints or features

## Summary

✅ **UDOT Integration Active**
🔑 **API Key Configured**
🏔️ **Ski Canyon Focus**
📊 **Real-time Data Available**
🤖 **Claude Auto-detects Queries**
💨 **Cached for Performance**
🚀 **Ready to Use**

Users can now ask about road conditions and get live UDOT data automatically!
