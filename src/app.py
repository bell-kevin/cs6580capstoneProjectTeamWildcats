from __future__ import annotations

from pathlib import Path

import gradio as gr
import joblib
import pandas as pd

MODEL_PATH = Path("models/champion_model.joblib")


def load_model(model_path: Path = MODEL_PATH):
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {model_path}. Run `python src/train_model.py` first."
        )
    return joblib.load(model_path)


MODEL = load_model()


def predict_traffic(
    lane_count: int,
    temp_f: float,
    dewpoint_f: float,
    humidity_pct: float,
    wind_speed_mph: float,
    snow_depth_in: float,
    precip_1hr_in: float,
    hour: int,
    day_of_week: str,
    is_weekend: bool,
    is_federal_holiday: bool,
) -> float:
    month = 1
    is_peak_hour = int(hour in {7, 8, 9, 15, 16, 17})
    temp_dewpoint_spread = temp_f - dewpoint_f

    row = pd.DataFrame(
        [
            {
                "lane_count": lane_count,
                "temp_f": temp_f,
                "dewpoint_f": dewpoint_f,
                "humidity_pct": humidity_pct,
                "wind_speed_mph": wind_speed_mph,
                "snow_depth_in": snow_depth_in,
                "precip_1hr_in": precip_1hr_in,
                "hour": hour,
                "month": month,
                "temp_dewpoint_spread": temp_dewpoint_spread,
                "is_weekend": is_weekend,
                "is_federal_holiday": is_federal_holiday,
                "is_peak_hour": is_peak_hour,
                "day_of_week": day_of_week,
            }
        ]
    )

    prediction = float(MODEL.predict(row)[0])
    return round(prediction, 2)


def build_app() -> gr.Blocks:
    with gr.Blocks(title="Snowbasin Congestion Predictor") as app:
        gr.Markdown("# Snowbasin Congestion Predictor")
        gr.Markdown("Predict hourly Trappers Loop traffic from the saved Sprint 3 champion model.")

        with gr.Row():
            lane_count = gr.Slider(1, 4, value=2, step=1, label="Lane count")
            hour = gr.Slider(0, 23, value=8, step=1, label="Hour of day")
            day_of_week = gr.Dropdown(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                value="Saturday",
                label="Day of week",
            )

        with gr.Row():
            temp_f = gr.Slider(-30, 90, value=28, label="Temperature (°F)")
            dewpoint_f = gr.Slider(-40, 70, value=18, label="Dew point (°F)")
            humidity_pct = gr.Slider(0, 100, value=75, label="Humidity (%)")

        with gr.Row():
            wind_speed_mph = gr.Slider(0, 80, value=10, label="Wind speed (mph)")
            snow_depth_in = gr.Slider(0, 150, value=20, label="Snow depth (in)")
            precip_1hr_in = gr.Slider(0, 5, value=0, label="Precip in previous hour (in)")

        with gr.Row():
            is_weekend = gr.Checkbox(value=True, label="Weekend")
            is_federal_holiday = gr.Checkbox(value=False, label="Federal holiday")

        predict_button = gr.Button("Predict traffic volume")
        output = gr.Number(label="Predicted traffic count this hour (vehicles)")

        predict_button.click(
            fn=predict_traffic,
            inputs=[
                lane_count,
                temp_f,
                dewpoint_f,
                humidity_pct,
                wind_speed_mph,
                snow_depth_in,
                precip_1hr_in,
                hour,
                day_of_week,
                is_weekend,
                is_federal_holiday,
            ],
            outputs=output,
        )

    return app


if __name__ == "__main__":
    build_app().launch(server_name="0.0.0.0", server_port=7860)
