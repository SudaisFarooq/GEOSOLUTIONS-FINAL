import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, precision_recall_fscore_support
import joblib

# ---------- CONFIG ----------
LAT, LON = 29.05, 79.48  # Udham Singh Nagar centroid
START_DATE = 20240101
END_DATE = 20251015

# ---------- FETCH RAINFALL ----------
print("🌧 Fetching daily rainfall from NASA POWER...")
url = (
    f"https://power.larc.nasa.gov/api/temporal/daily/point?"
    f"start={START_DATE}&end={END_DATE}&latitude={LAT}&longitude={LON}"
    "&parameters=PRECTOTCORR&community=AG&format=JSON"
)
response = requests.get(url)
response.raise_for_status()
data = response.json()

if "properties" in data and "parameter" in data["properties"] and "PRECTOTCORR" in data["properties"]["parameter"]:
    rainfall = data["properties"]["parameter"]["PRECTOTCORR"]
else:
    raise ValueError("NASA POWER API did not return PRECTOTCORR")

rain_df = pd.DataFrame({
    "date": pd.to_datetime(list(rainfall.keys()), format='%Y%m%d'),
    "rainfall_mm": list(rainfall.values())
})
print(f"✅ Rainfall data fetched: {len(rain_df)} days")

# ---------- FEATURE ENGINEERING ----------
df = rain_df.copy()

# Lagged rainfall features
for lag in [1,2,3,7,14]:
    df[f"rain_lag_{lag}"] = df["rainfall_mm"].shift(lag)

# Cumulative rainfall features
for w in [3,7,14]:
    df[f"rain_sum_{w}"] = df["rainfall_mm"].rolling(window=w, min_periods=1).sum()

# Flood label (top 10% of rainfall as proxy)
threshold = df["rainfall_mm"].quantile(0.9)
df["flood_label"] = (df["rainfall_mm"] > threshold).astype(int)

df = df.dropna()
print(f"✅ Prepared dataset: {len(df)} samples, {len(df.columns)} columns")

# ---------- RANDOM FOREST MODEL ----------
X = df.drop(columns=["date", "flood_label"])
y = df["flood_label"]

split = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

rf = RandomForestClassifier(n_estimators=200, max_depth=7, random_state=42)
rf.fit(X_train, y_train)

y_prob = rf.predict_proba(X_test)[:,1]
y_pred = (y_prob > 0.5).astype(int)

auc = roc_auc_score(y_test, y_prob)
p,r,f,_ = precision_recall_fscore_support(y_test, y_pred, average="binary")

print("\n📈 MODEL PERFORMANCE")
print(f"AUC: {auc:.3f}, Precision: {p:.2f}, Recall: {r:.2f}, F1: {f:.2f}")

# ---------- SAVE MODEL ----------
joblib.dump(rf, "flood_rf_model_usn.pkl")
print("\n💾 Random Forest model saved as 'flood_rf_model_usn.pkl'")