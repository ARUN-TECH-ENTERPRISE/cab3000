import streamlit as st
import pickle
import requests
import numpy as np
from geopy.geocoders import Nominatim


# ==============================
# Load Model
# ==============================

model = pickle.load(
    open("cab_linear_model.pkl", "rb")
)

encoder = pickle.load(
    open("vehicle_encoder.pkl", "rb")
)


# ==============================
# Page
# ==============================

st.set_page_config(
    page_title="Cab Fare Prediction",
    page_icon="🚕",
    layout="centered"
)

st.title("🚕 Cab Fare Prediction System")


# ==============================
# Vehicle Details
# ==============================

vehicle_details = {

    "Bike":{
        "mileage":45,
        "time_rate":0.3
    },

    "Auto":{
        "mileage":30,
        "time_rate":0.5
    },

    "Hatchback":{
        "mileage":18,
        "time_rate":0.8
    },

    "Sedan":{
        "mileage":15,
        "time_rate":1
    }
}


# ==============================
# Location
# ==============================

def get_coordinates(place):

    geolocator = Nominatim(
        user_agent="cab_app"
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
# Map Distance
# ==============================

def get_distance_time(start,target):

    start_point = get_coordinates(start)

    end_point = get_coordinates(target)


    if start_point is None or end_point is None:
        return None,None



    start_lat,start_lon=start_point

    end_lat,end_lon=end_point



    url = (

        "https://router.project-osrm.org/route/v1/driving/"

        f"{start_lon},{start_lat};"

        f"{end_lon},{end_lat}"

        "?overview=false"

    )


    response=requests.get(url)

    data=response.json()


    distance = (

        data["routes"][0]["distance"]

        /1000

    )


    duration=(

        data["routes"][0]["duration"]

        /60

    )


    return round(distance,2),round(duration)



# ==============================
# Base Fare
# ==============================

def get_base_fare(distance,vehicle):


    if distance<=5:

        fare={
            "Bike":30,
            "Auto":40,
            "Hatchback":50,
            "Sedan":60
        }


    elif distance<=10:

        fare={
            "Bike":50,
            "Auto":60,
            "Hatchback":70,
            "Sedan":90
        }


    elif distance<=15:

        fare={
            "Bike":70,
            "Auto":80,
            "Hatchback":90,
            "Sedan":110
        }


    elif distance<=20:

        fare={
            "Bike":90,
            "Auto":100,
            "Hatchback":110,
            "Sedan":130
        }


    elif distance<=25:

        fare={
            "Bike":110,
            "Auto":120,
            "Hatchback":130,
            "Sedan":150
        }


    elif distance<=30:

        fare={
            "Bike":130,
            "Auto":140,
            "Hatchback":150,
            "Sedan":160
        }


    elif distance<=60:

        fare={
            "Hatchback":250,
            "Sedan":300
        }


    elif distance<=100:

        fare={
            "Hatchback":500,
            "Sedan":550
        }


    elif distance<=180:

        fare={
            "Hatchback":1000,
            "Sedan":1100
        }


    elif distance<=240:

        fare={
            "Hatchback":1500,
            "Sedan":1600
        }


    elif distance<=400:

        fare={
            "Hatchback":2500,
            "Sedan":2600
        }


    else:

        fare={
            "Hatchback":3000,
            "Sedan":3200
        }


    return fare.get(vehicle,0)


# ==============================
# Driver Fare
# ==============================

def get_driver_fare(distance,vehicle):


    if distance<=5:

        fare={
            "Bike":50,
            "Auto":60,
            "Hatchback":70,
            "Sedan":80
        }


    elif distance<=10:

        fare={
            "Bike":70,
            "Auto":80,
            "Hatchback":90,
            "Sedan":100
        }


    elif distance<=15:

        fare={
            "Bike":100,
            "Auto":110,
            "Hatchback":120,
            "Sedan":130
        }


    elif distance<=20:

        fare={
            "Bike":120,
            "Auto":130,
            "Hatchback":145,
            "Sedan":155
        }


    elif distance<=30:

        fare={
            "Bike":150,
            "Auto":165,
            "Hatchback":200,
            "Sedan":220
        }


    elif distance<=60:

        fare={
            "Hatchback":350,
            "Sedan":400
        }


    elif distance<=100:

        fare={
            "Hatchback":500,
            "Sedan":550
        }


    elif distance<=180:

        fare={
            "Hatchback":1000,
            "Sedan":1100
        }


    elif distance<=240:

        fare={
            "Hatchback":1500,
            "Sedan":1600
        }


    elif distance<=400:

        fare={
            "Hatchback":2500,
            "Sedan":2600
        }


    else:

        fare={
            "Hatchback":3000,
            "Sedan":3200
        }


    return fare.get(vehicle,0)



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
# Find Distance Button
# ==============================

if st.button("🗺️ Find Distance"):


    distance,time = get_distance_time(
        start,
        target
    )


    if distance:


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
        f"⏱️ Duration : {st.session_state.time} Minutes"
    )



# ==============================
# ML Estimated Fare
# ==============================

if st.button("🤖 Predict Estimated Fare"):


    if "distance" not in st.session_state:

        st.warning(
            "First find distance"
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



    if st.button("Calculate Actual Fare"):


        distance = st.session_state.distance

        duration = st.session_state.time


        mileage = vehicle_details[vehicle]["mileage"]


        petrol_price = 110



        # Fuel

        fuel_used = (

            distance / mileage

        )


        fuel_cost = (

            fuel_used *

            petrol_price

        )



        # Base fare

        base_fare = get_base_fare(
            distance,
            vehicle
        )



        # Driver fare

        driver_fare = get_driver_fare(
            distance,
            vehicle
        )



        # Time cost

        time_cost = (

            duration *

            vehicle_details[vehicle]["time_rate"]

        )



        # Final actual fare

        actual_fare = (

            base_fare

            +

            fuel_cost

            +

            driver_fare

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


        st.write(
            f"🧾 Base Fare : ₹{base_fare}"
        )


        st.write(
            f"👨‍✈️ Driver Fare : ₹{driver_fare}"
        )


        st.write(
            f"⏱️ Time Cost : ₹{time_cost:.0f}"
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
