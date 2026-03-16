"""
Custom handler for Random Forest model on Hugging Face Inference API
Upload this as 'handler.py' to the hazemdhW26/snowbasin-traffic-random-forest repository
"""

from typing import Dict, List, Any
import joblib
import pandas as pd
import numpy as np


class EndpointHandler:
    def __init__(self, path=""):
        """Load the model when the endpoint starts"""
        self.model = joblib.load(f"{path}/champion_model.joblib")
        print("Random Forest model loaded successfully")

    def __call__(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process inference requests

        Args:
            data: Dictionary with "inputs" key containing prediction parameters

        Returns:
            List of predictions
        """
        try:
            # Extract inputs
            inputs = data.pop("inputs", data)

            # Handle both single prediction and batch predictions
            if isinstance(inputs, dict):
                inputs = [inputs]

            # Prepare features for each input
            predictions = []
            for input_data in inputs:
                # Prepare features
                features = self._prepare_features(input_data)

                # Convert to DataFrame for sklearn pipeline
                X = pd.DataFrame([features])

                # Make prediction
                prediction = float(self.model.predict(X)[0])

                predictions.append({
                    "prediction": prediction,
                    "model": "random-forest",
                    "confidence": "high"
                })

            return predictions

        except Exception as e:
            return [{"error": str(e)}]

    def _prepare_features(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare features from input parameters"""
        # Calculate dewpoint if not provided
        dewpoint = params.get("dewpoint_f", params["temp_f"] - 10)

        # Calculate cyclical encodings
        hour = params["hour"]
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)

        day_of_week_map = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        day_of_week_num = day_of_week_map.get(params["day_of_week"], 0)
        day_of_week_sin = np.sin(2 * np.pi * day_of_week_num / 7)
        day_of_week_cos = np.cos(2 * np.pi * day_of_week_num / 7)

        month = params["month"]
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)

        # Determine peak hour
        is_peak_hour = 1 if hour in [7, 8, 9, 15, 16, 17] else 0

        # Temperature-dewpoint spread
        temp_dewpoint_spread = params["temp_f"] - dewpoint

        # Distance to holiday weekend (simplified)
        distance_to_holiday_weekend = 0 if params.get("is_federal_holiday", False) else 30

        # Create feature dictionary
        features = {
            'lane_count': params.get("lane_count", 2),
            'temp_f': params["temp_f"],
            'dewpoint_f': dewpoint,
            'humidity_pct': params["humidity_pct"],
            'wind_speed_mph': params["wind_speed_mph"],
            'snow_depth_in': params["snow_depth_in"],
            'precip_1hr_in': params["precip_1hr_in"],
            'hour': hour,
            'month': month,
            'temp_dewpoint_spread': temp_dewpoint_spread,
            'is_weekend': int(params.get("is_weekend", False)),
            'is_federal_holiday': int(params.get("is_federal_holiday", False)),
            'is_peak_hour': is_peak_hour,
            'day_of_week': params["day_of_week"],
            'distance_to_holiday_weekend': distance_to_holiday_weekend,
            'traffic_lag_1': params.get("traffic_lag_1", 500),
            'traffic_lag_2': params.get("traffic_lag_2", 500),
            'traffic_lag_3': params.get("traffic_lag_3", 500),
            'traffic_lag_6': params.get("traffic_lag_6", 500),
            'traffic_lag_12': params.get("traffic_lag_12", 500),
            'traffic_lag_24': params.get("traffic_lag_24", 500),
            'traffic_lag_168': params.get("traffic_lag_168", 500),
            'hour_sin': hour_sin,
            'hour_cos': hour_cos,
            'day_of_week_sin': day_of_week_sin,
            'day_of_week_cos': day_of_week_cos,
            'month_sin': month_sin,
            'month_cos': month_cos,
        }

        return features
