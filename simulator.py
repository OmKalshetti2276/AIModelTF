import random
import time
from decision_engine import make_decision
from ml_model import model

# -----------------------------
# Zone State (Global Memory)
# -----------------------------

zones_state = {
    "Zone A": {   # Reserved for real ESP32 later
        "moisture": 42.0,
        "valve_open": False,
        "flow_rate": 0
    },
    "Zone B": {
        "moisture": 68.0,
        "valve_open": False,
        "flow_rate": 0
    },
    "Zone C": {
        "moisture": 28.0,
        "valve_open": False,
        "flow_rate": 0
    }
}

logs = []

# 🔥 NEW: History storage for charts
history = {
    "Zone A": [],
    "Zone B": [],
    "Zone C": []
}

# -----------------------------
# Simulator Loop
# -----------------------------

def generate_data():
    previous_moisture = {}

    while True:
        for zone_name, zone in zones_state.items():

            # 🔹 Skip Zone A (hardware reserved)
            if zone_name == "Zone A":
                continue

            current_sm = zone["moisture"]
            lag_sm = previous_moisture.get(zone_name, current_sm)

            # 🔹 Natural evaporation drop
            zone["moisture"] -= random.uniform(0.1, 0.3)

            # -----------------------------
            # Build ML features
            # -----------------------------
            features = {
                "temperature": 30,
                "humidity": 50,
                "wind_speed": 2,
                "rain_mm": 0,
                "et_15min": 0.1,
                "soil_moisture_current": zone["moisture"],
                "soil_moisture_lag1": lag_sm,
                "water_volume_liters": 0
            }

            # -----------------------------
            # Call AI Decision Engine
            # -----------------------------
            result = make_decision(
                model=model,
                features_dict=features,
                soil_type="loamy",
                slope="flat",
                current_sm=zone["moisture"],
                calibration_factor=4
            )

            zone["last_decision"] = result["action"]
            zone["recommended_seconds"] = result.get("recommended_valve_seconds", 0)
            zone["predicted_moisture"] = result.get("predicted_moisture", zone["moisture"])
            zone["confidence"] = result.get("confidence", 0.87)

            # -----------------------------
            # Apply AI Decision
            # -----------------------------
            if result["action"] == "IRRIGATE":
                zone["valve_open"] = True
                zone["flow_rate"] = 12

                # Simulate irrigation effect
                zone["moisture"] += random.uniform(0.6, 1.0)

                logs.append({
                    "zone": zone_name,
                    "action": "IRRIGATE",
                    "recommended_seconds": result.get("recommended_valve_seconds", 0),
                    "moisture": round(zone["moisture"], 2),
                    "timestamp": time.time()
                })

            else:
                zone["valve_open"] = False
                zone["flow_rate"] = 0

            # Clamp & round moisture
            zone["moisture"] = max(0, round(zone["moisture"], 2))

            # Save previous moisture
            previous_moisture[zone_name] = zone["moisture"]

            # -----------------------------
            # 🔥 Store history for graphs
            # -----------------------------
            history[zone_name].append({
                "timestamp": time.time(),
                "moisture": zone["moisture"],
                "flow_rate": zone["flow_rate"]
            })

            # Keep only last 50 points
            if len(history[zone_name]) > 50:
                history[zone_name].pop(0)

        time.sleep(5)