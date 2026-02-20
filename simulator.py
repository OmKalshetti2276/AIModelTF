import random
import time

# Zone 1 reserved for real ESP32 later
zones_state = {
    "Zone A": {"moisture": 42.0, "valve_open": False, "flow_rate": 0},  # STATIC
    "Zone B": {"moisture": 68.0, "valve_open": False, "flow_rate": 0},
    "Zone C": {"moisture": 28.0, "valve_open": False, "flow_rate": 0},
}

logs = []

def generate_data():
    while True:
        for zone_name, zone in zones_state.items():

            # 🔵 Skip Zone A (reserved for ESP32)
            if zone_name == "Zone A":
                continue

            # Natural moisture drop
            zone["moisture"] -= random.uniform(0.1, 0.3)

            # Irrigation increase
            if zone["valve_open"]:
                zone["moisture"] += random.uniform(0.6, 1.0)
                zone["flow_rate"] = 12
            else:
                zone["flow_rate"] = 0

            zone["moisture"] = round(zone["moisture"], 2)

            # Simple irrigation rule
            if zone["moisture"] < 35:
                zone["valve_open"] = True
                logs.append({
                    "zone": zone_name,
                    "action": "IRRIGATE",
                    "moisture": zone["moisture"],
                    "timestamp": time.time()
                })

            elif zone["moisture"] > 45:
                zone["valve_open"] = False

        time.sleep(5)