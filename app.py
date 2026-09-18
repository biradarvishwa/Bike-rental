import streamlit as st
import pandas as pd
import joblib

st.set_page_config(
    page_title="Bike Rental Demand Prediction",
    page_icon="🚲",
    layout="centered"
)

@st.cache_resource
def load_model():
    artifact = joblib.load("bike_rental_model.pkl")
    return artifact["model"], artifact["feature_names"]

model, feature_names = load_model()

st.title("🚲 Bike Rental Demand Prediction")
st.write(
    "Predict bike rental demand using time, weather, season, "
    "holiday and working-day information."
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    yr = st.selectbox("Year", [2011, 2012], index=1)
    mnth = st.slider("Month", 1, 12, 6)
    hr = st.slider("Hour", 0, 23, 12)
    weekday = st.selectbox(
        "Weekday",
        list(range(7)),
        format_func=lambda x: [
            "Sunday", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday"
        ][x]
    )
    holiday = st.selectbox("Holiday", ["No", "Yes"])

with col2:
    workingday = st.selectbox("Working Day", ["No work", "Working Day"])
    weather = st.selectbox(
        "Weather Situation",
        ["Clear", "Mist", "Light Snow", "Heavy Rain"]
    )
    season = st.selectbox(
        "Season",
        ["Springer", "Summer", "Fall", "Winter"]
    )
    temp = st.number_input(
        "Temperature (normalized)",
        min_value=0.0, max_value=1.0, value=0.50, step=0.01
    )
    hum = st.number_input(
        "Humidity (normalized)",
        min_value=0.0, max_value=1.0, value=0.50, step=0.01
    )
    windspeed = st.number_input(
        "Windspeed (normalized)",
        min_value=0.0, max_value=1.0, value=0.20, step=0.01
    )

st.caption(
    "Temperature, humidity and windspeed use the normalized values "
    "present in the training dataset."
)

if st.button("🔮 Predict Bike Rentals", use_container_width=True):

    # Create exactly the feature columns used during training.
    input_data = pd.DataFrame(0, index=[0], columns=feature_names)

    input_data["yr"] = yr
    input_data["mnth"] = mnth
    input_data["hr"] = hr
    input_data["holiday"] = 1 if holiday == "Yes" else 0
    input_data["workingday"] = 1 if workingday == "Working Day" else 0
    input_data["temp"] = temp
    input_data["hum"] = hum
    input_data["windspeed"] = windspeed
    input_data["year_month"] = (yr - 2011) * 12 + mnth

    # drop_first=True in the notebook makes the first category the baseline.
    weather_map = {
        "Heavy Rain": "weathersit_Heavy Rain",
        "Light Snow": "weathersit_Light Snow",
        "Mist": "weathersit_Mist"
    }
    if weather in weather_map:
        input_data[weather_map[weather]] = 1

    season_map = {
        "Springer": "season_springer",
        "Summer": "season_summer",
        "Winter": "season_winter"
    }
    if season in season_map:
        input_data[season_map[season]] = 1

    if weekday != 0:
        input_data[f"weekday_{weekday}"] = 1

    prediction = max(0, float(model.predict(input_data)[0]))

    st.success("Prediction generated successfully!")
    st.metric("Predicted Bike Rentals", f"{prediction:,.0f} bikes")

    st.info(
        "Prediction generated using the tuned LightGBM regression model."
    )
