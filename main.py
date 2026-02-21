from fastapi import FastAPI
from pydantic import BaseModel
from threading import Thread
from simulator import generate_data, zones_state, logs
from fastapi.middleware.cors import CORSMiddleware
import joblib
import requests
from decision_engine import make_decision
from simulator import generate_data, zones_state, logs, history
from datetime import datetime
from database import predictions_collection

FIXED_LAT = 18.1510
FIXED_LON = 74.5770


app = FastAPI()

@app.on_event("startup")
def start_simulator():
    thread = Thread(target=generate_data, daemon=True)
    thread.start()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Load trained model once at startup
model = joblib.load("soil_response_model.pkl")


# -----------------------------
# Request Schemas
# -----------------------------
class IrrigationRequest(BaseModel):
    soil_moisture: float
    soil_moisture_lag1: float
    soil_type: str
    slope: str
    crop_kc: float
    calibration_factor: float


class CalibrationRequest(BaseModel):
    soil_moisture_before: float
    soil_moisture_after: float
    irrigation_seconds: float
    previous_calibration_factor: float


# -----------------------------
# Fetch Parameters from NASA POWER
# -----------------------------
def fetch_weather_data(lat, lon):
    today = datetime.utcnow().strftime("%Y%m%d")

    url = (
        "https://power.larc.nasa.gov/api/temporal/hourly/point?"
        "parameters=T2M,RH2M,WS2M,ET0,PRECTOTCORR&"
        "community=AG&"
        f"latitude={lat}&longitude={lon}&"
        f"start={today}&end={today}&format=JSON"
    )

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        params = data["properties"]["parameter"]

        temperature = list(params["T2M"].values())[-1]
        humidity = list(params["RH2M"].values())[-1]
        wind_speed = list(params["WS2M"].values())[-1]
        et0_hourly = list(params["ET0"].values())[-1]
        rain_mm = list(params["PRECTOTCORR"].values())[-1]

        # Convert hourly ET to 15-minute ET
        et_15min = et0_hourly / 4

        return temperature, humidity, wind_speed, et_15min, rain_mm

    except Exception as e:
        print("NASA API error:", e)
        # Safe fallback values
        return 30, 50, 2, 0.1, 0


# -----------------------------
# Prediction Endpoint
# -----------------------------
@app.post("/predict")
def predict(request: IrrigationRequest):

    temperature, humidity, wind_speed, et_15min, rain_mm = fetch_weather_data(
    FIXED_LAT,
    FIXED_LON
)

    # Build model feature dictionary
    features = {
    "temperature": temperature,
    "humidity": humidity,
    "wind_speed": wind_speed,
    "rain_mm": rain_mm,
    "et_15min": et_15min * request.crop_kc,
    "soil_moisture_current": request.soil_moisture,
    "soil_moisture_lag1": request.soil_moisture_lag1,
    "water_volume_liters": 0
}

    result = make_decision(
        model=model,
        features_dict=features,
        soil_type=request.soil_type,
        slope=request.slope,
        current_sm=request.soil_moisture,
        calibration_factor=request.calibration_factor
    )


    # from datetime import datetime

    document = {
        "timestamp": datetime.utcnow(),
        "location": {
            "lat": FIXED_LAT,
            "lon": FIXED_LON
        },
        "input_features": {
            **features,
            "crop_kc": request.crop_kc,
            "soil_type": request.soil_type,
            "slope": request.slope,
            "calibration_factor": request.calibration_factor
        },
        "model_output": {
            "predicted_soil_moisture": result.get("predicted_soil_moisture")
        },
        "decision": {
            "action": result.get("action"),
            "duration_seconds": result.get("duration_seconds"),
            "water_volume_liters": result.get("water_volume_liters")
        }
    }

    try:
        predictions_collection.insert_one(document)
    except Exception as e:
        print("MongoDB insert error:", e)

    return result

# -----------------------------
# Calibration Endpoint
# -----------------------------
@app.post("/calibrate")
def calibrate(request: CalibrationRequest):

    increase = request.soil_moisture_after - request.soil_moisture_before

    if increase <= 0:
        return {
            "error": "Invalid moisture increase. Calibration failed."
        }

    measured_c = request.irrigation_seconds / increase

    # Smooth update
    updated_c = (
        0.7 * request.previous_calibration_factor
        + 0.3 * measured_c
    )

    return {
        "measured_calibration_factor": round(measured_c, 2),
        "updated_calibration_factor": round(updated_c, 2)
    }

@app.get("/zones")
def get_zones():
    return zones_state


@app.get("/logs")
def get_logs():
    return logs[-20:]

@app.get("/history")
def get_history():
    return history
 