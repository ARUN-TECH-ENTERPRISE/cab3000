import streamlit as st
import pickle
import requests
import numpy as np

from geopy.geocoders import Nominatim


# ==============================
# Load ML Model
# ==============================

model = pickle.load(
    open("cab_linear_model.pkl", "rb")
)

encoder = pickle.load(
    open("vehicle_encoder.pkl", "rb")
)



# ==============================
# Page Configuration
# ==============================

st.set_page_config(
    page_title="Cab Fare Prediction",
    page_icon="🚕"
)


st.title("🚕 Cab Fare Prediction System")



# ==============================
# Vehicle Details
# ==============================

vehicle_details = {

    "Bike": {
        "mileage":45,
        "time_rate":0.3
    },

    "Auto": {
        "mileage":30,
        "time_rate":0.5
    },

    "Hatchback": {
        "mileage":18,
        "time_rate":0.8
    },

    "Sedan": {
        "mileage":15,
        "time_rate":1
    }

}



# ==============================
# Get Location
# ==============================

def get_coordinates(place):

    geolocator = Nominatim(
        user_agent="cab_fare_prediction"
    )


    location = geolocator.geocode(
        place + ", Tamil Nadu, India"
    )


    if location:

        return (
            location.latitude,
            location.longitude
        )

    return None



# ==============================
# Distance and Time
# ==============================

def get_distance_time(start, target):

    start_point = get_coordinates(start)

    end_point = get_coordinates(target)


    if start_point is None or end_point is None:

        return None, None



    start_lat, start_lon = start_point

    end_lat, end_lon = end_point



    url = (

        "https://router.project-osrm.org/route/v1/driving/"

        f"{start_lon},{start_lat};"

        f"{end_lon},{end_lat}"

        "?overview=false"

    )


    response = requests.get(url)


    data = response.json()



    distance = (
        data["routes"][0]["distance"]
        /1000
    )


    duration = (
        data["routes"][0]["duration"]
        /60
    )


    return round(distance,2), round(duration)



# ==============================
# Distance Fare
# ==============================

def get_distance_fare(distance):


    if distance <= 10:
        return 60

    elif distance <= 20:
        return 100

    elif distance <= 30:
        return 120

    elif distance <=45:
        return 180

    elif distance <=75:
        return 300

    elif distance <=100:
        return 400

    elif distance <=135:
        return 450

    elif distance <=170:
        return 500

    elif distance <=250:
        return 550

    elif distance <=300:
        return 600

    elif distance <=400:
        return 750

    elif distance <=500:
        return 850

    elif distance <=600:
        return 1000

    elif distance <=800:
        return 1300

    else:
        return 1500



# ==============================
# User Input
# ==============================

start = st.text_input(
    "📍 Starting Place"
)


target = st.text_input(
    "🎯 Target Place"
)


vehicle = st.selectbox(
    "🚘 Select Vehicle",
    [
        "Bike",
        "Auto",
        "Hatchback",
        "Sedan"
    ]
)



# ==============================
# Find Distance
# ==============================

if st.button("🗺️ Find Distance"):


    distance, time = get_distance_time(
        start,
        target
    )


    if distance is not None:

        st.session_state.distance = distance

        st.session_state.time = time


    else:

        st.error(
            "Place not found"
        )



if "distance" in st.session_state:


    st.success(
        f"📏 Distance : {st.session_state.distance} KM"
    )


    st.success(
        f"⏱️ Time : {st.session_state.time} Minutes"
    )



# ==============================
# ML Estimated Fare
# ==============================

if st.button("🤖 Predict Estimated Fare"):


    if "distance" not in st.session_state:

        st.warning(
            "First click Find Distance"
        )

    else:


        distance = st.session_state.distance

        duration = st.session_state.time


        mileage = vehicle_details[vehicle]["mileage"]


        petrol_price = 110


        fuel_cost = (
            distance / mileage
        ) * petrol_price



        vehicle_encoded = encoder.transform(
            [vehicle]
        )[0]



        input_data = np.array([

            [
                distance,
                duration,
                vehicle_encoded,
                mileage,
                petrol_price,
                fuel_cost
            ]

        ])



        estimated = model.predict(
            input_data
        )[0]



        st.session_state.estimated = round(
            estimated
        )


if "estimated" in st.session_state:


    st.success(
        f"🤖 Estimated Fare : ₹{st.session_state.estimated}"
    )



# ==============================
# Actual Fare
# ==============================


if "distance" in st.session_state:


    st.divider()


    st.subheader(
        "🧾 Actual Fare Calculation"
    )


    actual_distance = st.number_input(
        "Actual Distance (KM)",
        value=float(st.session_state.distance)
    )


    actual_time = st.number_input(
        "Actual Time (Minutes)",
        value=float(st.session_state.time)
    )



    if st.button("Calculate Actual Fare"):


        mileage = vehicle_details[vehicle]["mileage"]


        fuel_used = (
            actual_distance / mileage
        )


        petrol_price = 110


        fuel_cost = (
            fuel_used * petrol_price
        )


        distance_cost = get_distance_fare(
            actual_distance
        )


        time_cost = (
            actual_time *
            vehicle_details[vehicle]["time_rate"]
        )



        actual_fare = (

            distance_cost
            +
            fuel_cost
            +
            time_cost

        )


        st.session_state.actual = round(
            actual_fare
        )



        st.write(
            f"⛽ Fuel Used : {fuel_used:.2f} L"
        )


        st.write(
            f"⛽ Fuel Cost : ₹{fuel_cost:.0f}"
        )



if "actual" in st.session_state:


    st.info(
        f"🧾 Actual Fare : ₹{st.session_state.actual}"
    )



# ==============================
# Difference
# ==============================


if (
    "estimated" in st.session_state
    and
    "actual" in st.session_state
):


    difference = abs(

        st.session_state.estimated
        -
        st.session_state.actual

    )


    st.warning(
        f"📊 Difference : ₹{difference}"
    )