import pandas as pd

LOWER_BOUND = 35
TARGET = 45


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
    delta_sm = model.predict(X)[0]
    predicted_sm = float(current_sm + delta_sm)

    # Decision logic
    if predicted_sm >= LOWER_BOUND:
        return {
            "action": "WAIT",
            "predicted_moisture": round(predicted_sm, 2)
        }

    deficit = TARGET - current_sm
    seconds = deficit * calibration_factor

    return {
        "action": "IRRIGATE",
        "predicted_moisture": round(predicted_sm, 2),
        "recommended_valve_seconds": round(seconds, 2)
    }
