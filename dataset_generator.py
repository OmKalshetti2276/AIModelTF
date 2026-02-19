import numpy as np
import pandas as pd

# Simulation Settings
DAYS = 30
INTERVALS_PER_DAY = 24 * 4
TOTAL_STEPS = DAYS * INTERVALS_PER_DAY

# Zones
zones = [
    {"soil_type": "sandy", "slope": "flat"},
    {"soil_type": "sandy", "slope": "moderate"},
    {"soil_type": "loamy", "slope": "flat"},
    {"soil_type": "clay", "slope": "steep"},
    {"soil_type": "loamy", "slope": "flat"},
]

soil_drainage = {
    "sandy": 0.05,
    "loamy": 0.03,
    "clay": 0.01
}

data = []

for zone in zones:

    soil_type = zone["soil_type"]
    slope = zone["slope"]
    drainage = soil_drainage[soil_type]

    soil_moisture = np.random.uniform(35, 50)
    soil_moisture_lag = soil_moisture

    for t in range(TOTAL_STEPS):

        temperature = np.random.uniform(20, 38)
        humidity = np.random.uniform(30, 85)
        wind_speed = np.random.uniform(0.5, 5)
        rain_mm = np.random.choice([0, 0, 0, 1, 2])
        et_15min = np.random.uniform(0.05, 0.12)
        water_volume = np.random.choice([0, 0, 20, 40])

        delta_sm = (
            -et_15min
            + rain_mm * 0.2
            + water_volume * 0.02
            - drainage
        )

        next_sm = soil_moisture + delta_sm
        next_sm = max(10, min(80, next_sm))

        data.append([
            temperature,
            humidity,
            wind_speed,
            rain_mm,
            et_15min,
            soil_moisture,
            soil_moisture_lag,
            water_volume,
            soil_type,
            slope,
            delta_sm
        ])

        soil_moisture_lag = soil_moisture
        soil_moisture = next_sm

columns = [
    "temperature",
    "humidity",
    "wind_speed",
    "rain_mm",
    "et_15min",
    "soil_moisture_current",
    "soil_moisture_lag1",
    "water_volume_liters",
    "soil_type",
    "slope",
    "delta_sm"
]

df = pd.DataFrame(data, columns=columns)
df.to_csv("realistic_dataset.csv", index=False)

print("Dataset generated successfully!")
