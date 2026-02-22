from datetime import datetime
from database import predictions_collection

sample_doc = {
    "timestamp": datetime.utcnow(),
    "location": {"lat": 18.1510, "lon": 74.5770},
    "input_features": {
        "temperature": 30,
        "humidity": 55,
        "wind_speed": 2,
        "rain_mm": 0,
        "et_15min": 0.15,
        "soil_moisture_current": 45,
        "soil_moisture_lag1": 44,
        "water_volume_liters": 0,
        "crop_kc": 0.85,
        "soil_type": "loamy",
        "slope": "flat",
        "calibration_factor": 1.2
    },
    "model_output": {
        "predicted_soil_moisture": 43.8
    },
    "decision": {
        "action": "IRRIGATE",
        "duration_seconds": 120,
        "water_volume_liters": 15
    }
}

predictions_collection.insert_one(sample_doc)
print("Inserted sample data")