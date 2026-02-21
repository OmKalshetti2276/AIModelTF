import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Load dataset
df = pd.read_csv("realistic_dataset.csv")

# Encode categorical features
df = pd.get_dummies(df, columns=["soil_type", "slope"])

# Define feature columns
FEATURES = [
    "temperature",
    "humidity",
    "wind_speed",
    "rain_mm",
    "et_15min",
    "soil_moisture_current",
    "soil_moisture_lag1",
    "water_volume_liters",
]

FEATURES += [col for col in df.columns if col.startswith("soil_type_")]
FEATURES += [col for col in df.columns if col.startswith("slope_")]

TARGET = "delta_sm"

X = df[FEATURES]
y = df[TARGET]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# RandomForest (balanced configuration)
model = RandomForestRegressor(
    n_estimators=300,
    max_depth=18,
    min_samples_leaf=4,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# Evaluation of the model that I trained
predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"MAE: {mae:.4f}")
print(f"R2 Score: {r2:.4f}")

# Saving the model
joblib.dump(model, "soil_response_model.pkl")
print("Model saved successfully.")
