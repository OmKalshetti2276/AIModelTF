import joblib
import numpy as np
from decision_engine import make_decision

# Loaded the trained model
model = joblib.load("soil_response_model.pkl")

# -----------------------------
# Sample Test Input
# -----------------------------
current_sm = 34.0
lag_sm = 39.0

soil_type = "loamy"
slope = "flat"

calibration_factor = 30  # example value

# Example weather-derived inputs
features = {
    "temperature": 30,
    "humidity": 50,
    "wind_speed": 2,
    "rain_mm": 0,
    "et_15min": 0.08,
    "soil_moisture_current": current_sm,
    "soil_moisture_lag1": lag_sm,
    "water_volume_liters": 0
}

# -----------------------------
# Run Decision Engine
# -----------------------------
result = make_decision(
    model=model,
    features_dict=features,
    soil_type=soil_type,
    slope=slope,
    current_sm=current_sm,
    calibration_factor=calibration_factor
)

print("\n=== TEST RESULT ===")
print(result)
