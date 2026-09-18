from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "bike_rental_model.pkl"
STATIC_DIR = BASE_DIR / "static"

artifact = joblib.load(MODEL_PATH)
model = artifact["model"]
feature_names = artifact["feature_names"]

app = FastAPI(
    title="Bike Rental Demand API",
    description="Predict hourly bike rental demand using a tuned LightGBM model.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class PredictionRequest(BaseModel):
    year: Literal[2011, 2012] = 2012
    month: int = Field(6, ge=1, le=12)
    hour: int = Field(12, ge=0, le=23)
    weekday: int = Field(1, ge=0, le=6)
    holiday: bool = False
    working_day: bool = True
    weather: Literal["Clear", "Mist", "Light Snow", "Heavy Rain"] = "Clear"
    season: Literal["Springer", "Summer", "Fall", "Winter"] = "Summer"
    temperature: float = Field(0.50, ge=0.0, le=1.0)
    humidity: float = Field(0.50, ge=0.0, le=1.0)
    windspeed: float = Field(0.20, ge=0.0, le=1.0)


class PredictionResponse(BaseModel):
    predicted_rentals: int
    raw_prediction: float
    demand_level: str
    message: str


def build_features(payload: PredictionRequest) -> pd.DataFrame:
    row = pd.DataFrame(0, index=[0], columns=feature_names, dtype=float)

    row.loc[0, "yr"] = payload.year
    row.loc[0, "mnth"] = payload.month
    row.loc[0, "hr"] = payload.hour
    row.loc[0, "holiday"] = int(payload.holiday)
    row.loc[0, "workingday"] = int(payload.working_day)
    row.loc[0, "temp"] = payload.temperature
    row.loc[0, "hum"] = payload.humidity
    row.loc[0, "windspeed"] = payload.windspeed
    row.loc[0, "year_month"] = (payload.year - 2011) * 12 + payload.month

    weather_map = {
        "Heavy Rain": "weathersit_Heavy Rain",
        "Light Snow": "weathersit_Light Snow",
        "Mist": "weathersit_Mist",
    }
    weather_col = weather_map.get(payload.weather)
    if weather_col and weather_col in row.columns:
        row.loc[0, weather_col] = 1

    season_map = {
        "Springer": "season_springer",
        "Summer": "season_summer",
        "Winter": "season_winter",
    }
    season_col = season_map.get(payload.season)
    if season_col and season_col in row.columns:
        row.loc[0, season_col] = 1

    if payload.weekday != 0:
        weekday_col = f"weekday_{payload.weekday}"
        if weekday_col in row.columns:
            row.loc[0, weekday_col] = 1

    return row


def demand_level(value: int) -> str:
    if value < 100:
        return "Low"
    if value < 300:
        return "Moderate"
    if value < 600:
        return "High"
    return "Very High"


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "model": "LightGBM", "features": len(feature_names)}


@app.post("/api/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest):
    try:
        features = build_features(payload)
        raw_prediction = max(0.0, float(model.predict(features)[0]))
        predicted = int(round(raw_prediction))
        level = demand_level(predicted)
        return PredictionResponse(
            predicted_rentals=predicted,
            raw_prediction=round(raw_prediction, 2),
            demand_level=level,
            message=f"Expected demand is {level.lower()} for the selected conditions.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Prediction failed.") from exc
