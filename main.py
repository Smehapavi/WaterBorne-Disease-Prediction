import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Load cleaned East India dataset
df = pd.read_csv("east_region_india_water_disease_cleaned.csv")

# ==========================
# 1. Define outbreak thresholds
# ==========================
# Threshold = 75th percentile for each disease
df["Diarrhea_Outbreak"] = (df["Diarrheal Cases per 100,000 people"] > df["Diarrheal Cases per 100,000 people"].quantile(0.75)).astype(int)
df["Cholera_Outbreak"] = (df["Cholera Cases per 100,000 people"] > df["Cholera Cases per 100,000 people"].quantile(0.75)).astype(int)
df["Typhoid_Outbreak"] = (df["Typhoid Cases per 100,000 people"] > df["Typhoid Cases per 100,000 people"].quantile(0.75)).astype(int)

# ==========================
# 2. Feature Engineering
# ==========================
df["Diarrhea_MA7"] = df["Diarrheal Cases per 100,000 people"].rolling(7, min_periods=1).mean()
df["Rainfall_MA3"] = df["Rainfall (mm per year)"].rolling(3, min_periods=1).mean()
df["Month"] = 1  # Yearly data, dummy
df["Monsoon"] = 0

features = ["Diarrhea_MA7","Rainfall_MA3","Turbidity (NTU)","pH Level","Contaminant Level (ppm)","Month","Monsoon"]
X = df[features].fillna(0)
y = df[["Diarrhea_Outbreak","Cholera_Outbreak","Typhoid_Outbreak"]]

# ==========================
# 3. Train-Test Split
# ==========================
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==========================
# 4. Train Multi-Output Random Forest
# ==========================
from sklearn.multioutput import MultiOutputClassifier
rf = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42))
rf.fit(X_train_scaled, y_train)

# ==========================
# 5. Predict Function
# ==========================
def predict_outbreak(input_data):
    """
    input_data = dict with keys matching 'features'
    Returns: Outbreak probabilities for all 3 diseases
    """
    # Force correct column order
    df_input = pd.DataFrame([input_data])[features]
    df_scaled = scaler.transform(df_input)
    probs = rf.predict_proba(df_scaled)
    
    result = {
        "Diarrhea_Risk(%)": round(probs[0][0][1]*100,2),
        "Cholera_Risk(%)": round(probs[1][0][1]*100,2),
        "Typhoid_Risk(%)": round(probs[2][0][1]*100,2)
    }
    return result


# ==========================
# 6. Example usage
# ==========================
input_example = {
    "Diarrhea_MA7": 50,
    "Rainfall_MA3": 120,
    "Turbidity (NTU)": 6,
    "pH Level": 7.2,
    "Contaminant Level (ppm)": 3.5,
    "Month": 7,
    "Monsoon": 1
}

risk = predict_outbreak(input_example)
print("Predicted Outbreak Risk (%):", risk)

import joblib

joblib.dump(rf, "water_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("Model and scaler saved")