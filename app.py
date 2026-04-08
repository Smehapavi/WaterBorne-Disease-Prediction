import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# Load trained model and scaler
model = joblib.load("water_model.pkl")
scaler = joblib.load("scaler.pkl")

# Feature order (must match training)
features = [
    "Diarrhea_MA7",
    "Rainfall_MA3",
    "Turbidity (NTU)",
    "pH Level",
    "Contaminant Level (ppm)",
    "Month",
    "Monsoon"
]

# Page settings
st.set_page_config(
    page_title="Waterborne Disease Prediction",
    layout="centered"
)

st.title("💧 Waterborne Disease Outbreak Prediction")
st.caption("AI model estimating outbreak risk for Diarrhea, Cholera, and Typhoid")

st.success("Model Loaded Successfully")

# ----------------------------
# User Input Section
# ----------------------------

col1, col2 = st.columns(2)

with col1:
    diarrhea = st.number_input("Diarrhea Moving Avg (7)", value=50)
    rainfall = st.number_input("Rainfall Moving Avg (3)", value=120)
    turbidity = st.number_input("Turbidity (NTU)", value=6.0)

with col2:
    ph = st.number_input("pH Level", value=7.2)
    contaminant = st.number_input("Contaminant Level (ppm)", value=3.5)
    month = st.slider("Month", 1, 12, 7)
    monsoon = st.selectbox("Monsoon Season", [0, 1])

# ----------------------------
# Prediction Button
# ----------------------------

if st.button("Predict Outbreak Risk"):

    input_data = pd.DataFrame(
        [[diarrhea, rainfall, turbidity, ph, contaminant, month, monsoon]],
        columns=features
    )

    scaled = scaler.transform(input_data)
    probs = model.predict_proba(scaled)

    d = probs[0][0][1]
    c = probs[1][0][1]
    t = probs[2][0][1]

    # ----------------------------
    # Risk Display
    # ----------------------------

    st.subheader("Predicted Risk Levels")

    st.write("Diarrhea Risk")
    st.progress(d)

    st.write("Cholera Risk")
    st.progress(c)

    st.write("Typhoid Risk")
    st.progress(t)

    # ----------------------------
    # Risk Status Indicator
    # ----------------------------

    max_risk = max(d, c, t)

    if max_risk > 0.6:
        st.error("🚨 High outbreak risk detected")
    elif max_risk > 0.3:
        st.warning("⚠ Moderate outbreak probability")
    else:
        st.success("✅ Low outbreak probability")

    # ----------------------------
    # Bar Chart Visualization
    # ----------------------------

    risk_data = pd.DataFrame({
        "Disease": ["Diarrhea", "Cholera", "Typhoid"],
        "Probability": [d, c, t]
    })

    st.subheader("Outbreak Probability Comparison")
    st.bar_chart(risk_data.set_index("Disease"))

    # ----------------------------
    # AI Interpretation
    # ----------------------------

    st.subheader("AI Interpretation")

    if turbidity > 5:
        st.write("⚠ High turbidity detected. Water contamination risk is increased.")

    if rainfall > 100:
        st.write("🌧 Heavy rainfall may spread waterborne pathogens.")

    if ph < 6.5 or ph > 8.5:
        st.write("⚠ Unsafe pH level detected in water.")

    if contaminant > 3:
        st.write("⚠ Elevated contaminant concentration detected.")

import requests

requests.get(f"http://127.0.0.1:5000/update/{int(d*100)}/{int(c*100)}/{int(t*100)}")