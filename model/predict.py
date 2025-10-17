import json
import joblib
import pandas as pd
import requests
from datetime import datetime, timedelta

# Load trained model once (for performance)
_model = joblib.load("model/flood_rf_model_usn.pkl")

def fetch_rainfall(lat, lon, start, end):
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"start={start.strftime('%Y%m%d')}&end={end.strftime('%Y%m%d')}"
        f"&latitude={lat}&longitude={lon}"
        "&parameters=PRECTOTCORR&community=AG&format=JSON"
    )
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    rainfall = data["properties"]["parameter"]["PRECTOTCORR"]
    df = pd.DataFrame({
        "date": pd.to_datetime(list(rainfall.keys()), format='%Y%m%d'),
        "rainfall_mm": list(rainfall.values())
    })
    return df

def predict_flood(start_date_str, end_date_str, lat, lon):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    rain_df = fetch_rainfall(lat, lon, start_date - timedelta(days=14), end_date)

    df = rain_df.copy()
    for lag in [1, 2, 3, 7, 14]:
        df[f"rain_lag_{lag}"] = df["rainfall_mm"].shift(lag)
    for w in [3, 7, 14]:
        df[f"rain_sum_{w}"] = df["rainfall_mm"].rolling(window=w, min_periods=1).sum()
    df = df.dropna()

    pred_df = df[df["date"].between(start_date, end_date)].copy()
    X = pred_df.drop(columns=["date"])

    pred_probs = _model.predict_proba(X)[:, 1] * 100

    return {
        "prediction": {
            "date": pred_df["date"].dt.strftime("%Y-%m-%d").tolist(),
            "percentage": pred_probs.round(2).tolist()
        }
    }
