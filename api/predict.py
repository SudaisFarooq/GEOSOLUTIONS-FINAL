import sys
import json
import joblib
import pandas as pd
import requests
from datetime import datetime, timedelta

# Arguments: startDate endDate latitude longitude
start_date_str = sys.argv[1]
end_date_str = sys.argv[2]
LAT = float(sys.argv[3])
LON = float(sys.argv[4])

start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

# Load trained model
model = joblib.load("flood_rf_model_usn.pkl")

# Fetch rainfall for the location
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

rain_df = fetch_rainfall(LAT, LON, start_date - timedelta(days=14), end_date)

# Compute lagged/cumulative features
df = rain_df.copy()
for lag in [1,2,3,7,14]:
    df[f"rain_lag_{lag}"] = df["rainfall_mm"].shift(lag)
for w in [3,7,14]:
    df[f"rain_sum_{w}"] = df["rainfall_mm"].rolling(window=w, min_periods=1).sum()
df = df.dropna()

# Keep only rows for prediction period
pred_df = df[df["date"].between(start_date, end_date)].copy()
X = pred_df.drop(columns=["date"])

# Predict probabilities
pred_probs = model.predict_proba(X)[:,1] * 100

output = {
    "prediction": {
        "date": pred_df["date"].dt.strftime("%Y-%m-%d").tolist(),
        "percentage": pred_probs.round(2).tolist()
    }
}

print(json.dumps(output))
