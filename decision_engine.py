import pandas as pd

def make_decision(
    model,
    features_dict,
    soil_type,
    slope,
    current_sm,
    calibration_factor
):
    """
    Performs:
    1. Feature preparation
    2. delta_sm prediction
    3. Threshold check
    4. Irrigation duration calculation
    """

    # Ensure all required model columns exist
    for col in model.feature_names_in_:
        if col not in features_dict:
            features_dict[col] = 0

    # Encode categorical variables
    features_dict[f"soil_type_{soil_type}"] = 1
    features_dict[f"slope_{slope}"] = 1

    # Convert to DataFrame in correct column order
    X = pd.DataFrame([features_dict])[model.feature_names_in_]

    # Predict short-term moisture change
    # delta_sm = model.predict(X)[0]
    # predicted_sm = float(current_sm + delta_sm)
    delta_sm = model.predict(X)[0]

# Physical lower bound
    min_delta = -current_sm

# Optional upper bound (based on soil type)
    soil_fc = {
    "sandy": 18,
    "loamy": 64,
    "clay": 40
    }
    field_capacity = soil_fc[soil_type]

    LOWER_BOUND = 0.6 * field_capacity
    TARGET = 0.85 * field_capacity

    field_capacity = soil_fc[soil_type]
    max_delta = field_capacity - current_sm

# Constrain delta
    delta_sm = max(min_delta, min(delta_sm, max_delta))

    predicted_sm = float(current_sm + delta_sm)

    # Decision logic
    if predicted_sm >= LOWER_BOUND:
        return {
            "action": "WAIT",
            "predicted_moisture": round(predicted_sm, 2)
        }

    deficit = TARGET - current_sm
    seconds = deficit * calibration_factor/5

    return {
        "action": "IRRIGATE",
        "predicted_moisture": round(predicted_sm, 2),
        "recommended_valve_seconds": round(seconds, 2)
    }
