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
# Location Function
# ==============================

def get_coordinates(place):

    geolocator = Nominatim(
        user_agent="cab_prediction_app"
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
# OSRM Distance
# ==============================

def get_distance_time(start,target):


    start_point = get_coordinates(start)

    end_point = get_coordinates(target)


    if start_point is None or end_point is None:

        return None,None



    start_lat,start_lon = start_point

    end_lat,end_lon = end_point



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

        /

        1000

    )


    duration = (

        data["routes"][0]["duration"]

        /

        60

    )



    return round(distance,2),round(duration)




# ==============================
# Fare Calculation
# ==============================

def get_base_fare(distance,vehicle):


    rate = {

        "Bike":5,
        "Auto":8,
        "Hatchback":12,
        "Sedan":15

    }


    base = {

        "Bike":30,
        "Auto":40,
        "Hatchback":50,
        "Sedan":60

    }


    return (

        base[vehicle]

        +

        distance * rate[vehicle]

    )




def get_driver_fare(distance,vehicle):


    driver_rate={

        "Bike":3,
        "Auto":5,
        "Hatchback":8,
        "Sedan":10

    }


    return distance * driver_rate[vehicle]





# ==============================
# Input Section
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


    distance,time = get_distance_time(

        start,

        target

    )



    if distance:


        st.session_state.map_distance = distance

        st.session_state.map_time = time



    else:

        st.error(
            "Place not found"
        )





# ==============================
# Show Map Distance
# ==============================


if "map_distance" in st.session_state:


    distance = st.session_state.map_distance

    time = st.session_state.map_time



    # Bike Auto Limit


    if vehicle in ["Bike","Auto"] and distance > 30:


        st.error(
            f"❌ {vehicle} unavailable above 30 KM"
        )


    else:


        st.success(
            f"📏 Distance : {distance} KM"
        )


        st.success(
            f"⏱️ Time : {time} Minutes"
        )



# ==============================
# Estimated Fare
# ==============================


if st.button("🤖 Predict Estimated Fare"):


    if "map_distance" not in st.session_state:


        st.warning(
            "First find distance"
        )


    else:


        distance = st.session_state.map_distance

        duration = st.session_state.map_time



        if vehicle in ["Bike","Auto"] and distance > 30:


            st.error(
                "Vehicle unavailable"
            )

        else:



            mileage = vehicle_details[vehicle]["mileage"]


            petrol_price = 110


            fuel_cost = (

                distance/mileage

            ) * petrol_price



            encoded_vehicle = encoder.transform(

                [vehicle]

            )[0]



            data=np.array([

                [

                    distance,

                    duration,

                    encoded_vehicle,

                    mileage,

                    petrol_price,

                    fuel_cost

                ]

            ])



            prediction=model.predict(data)[0]


            st.session_state.estimated = round(
                prediction
            )



if "estimated" in st.session_state:


    st.success(

        f"🤖 Estimated Fare : ₹{st.session_state.estimated}"

    )
# ==============================
# Actual Fare Calculation
# ==============================


if "map_distance" in st.session_state:


    st.divider()


    st.subheader(
        "🧾 Actual Fare Calculation"
    )



    # Editable Actual Distance

    actual_distance = st.number_input(

        "📏 Actual Distance (KM)",

        min_value=0.0,

        value=float(st.session_state.map_distance),

        step=0.1

    )



    # Editable Actual Time


    actual_time = st.number_input(

        "⏱️ Actual Time (Minutes)",

        min_value=0,

        value=int(st.session_state.map_time),

        step=1

    )





    if st.button(
        "💰 Calculate Actual Fare"
    ):



        # Bike Auto Restriction


        if vehicle in ["Bike","Auto"] and actual_distance > 30:


            st.error(

                f"❌ {vehicle} is unavailable above 30 KM"

            )


        else:



            mileage = vehicle_details[vehicle]["mileage"]


            petrol_price = 110




            # Fuel Calculation


            fuel_used = (

                actual_distance /

                mileage

            )



            fuel_cost = (

                fuel_used *

                petrol_price

            )





            # Base Fare


            base_fare = get_base_fare(

                actual_distance,

                vehicle

            )





            # Driver Fare


            driver_fare = get_driver_fare(

                actual_distance,

                vehicle

            )






            # Time Cost


            time_cost = (

                actual_time *

                vehicle_details[vehicle]["time_rate"]

            )







            # Final Actual Price


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




            st.session_state.actual_details={


                "fuel_used":fuel_used,

                "fuel_cost":fuel_cost,

                "base_fare":base_fare,

                "driver_fare":driver_fare,

                "time_cost":time_cost

            }







# ==============================
# Display Actual Fare Details
# ==============================



if "actual" in st.session_state:



    details = st.session_state.actual_details



    st.write(
        f"⛽ Fuel Used : {details['fuel_used']:.2f} L"
    )


    st.write(
        f"⛽ Fuel Cost : ₹{details['fuel_cost']:.0f}"
    )


    st.write(
        f"🧾 Base Fare : ₹{details['base_fare']:.0f}"
    )


    st.write(
        f"👨‍✈️ Driver Fare : ₹{details['driver_fare']:.0f}"
    )


    st.write(
        f"⏱️ Time Cost : ₹{details['time_cost']:.0f}"
    )



    st.info(

        f"🧾 Actual Fare : ₹{st.session_state.actual}"

    )







# ==============================
# Fare Difference
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

        f"📊 Estimated vs Actual Difference : ₹{difference}"

    )
