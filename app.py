import streamlit as st
import pickle
import requests
import numpy as np


# ==============================
# Load Model
# ==============================

model = pickle.load(
    open("cab_linear_model.pkl","rb")
)

encoder = pickle.load(
    open("vehicle_encoder.pkl","rb")
)



# ==============================
# Page Settings
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
# OpenStreetMap Location
# ==============================


def get_coordinates(place):

    try:

        url="https://nominatim.openstreetmap.org/search"


        params={

            "q":place+", Tamil Nadu, India",

            "format":"json",

            "limit":1

        }


        headers={

            "User-Agent":
            "cab-fare-prediction-app"

        }


        response=requests.get(

            url,

            params=params,

            headers=headers,

            timeout=10

        )


        data=response.json()



        if data:

            return (

                float(data[0]["lat"]),

                float(data[0]["lon"])

            )


        return None



    except Exception:

        return None






# ==============================
# OSRM Distance
# ==============================


def get_distance_time(start,target):


    start_point=get_coordinates(start)

    end_point=get_coordinates(target)



    if start_point is None or end_point is None:

        return None,None



    start_lat,start_lon=start_point

    end_lat,end_lon=end_point




    try:


        url=(

        "https://router.project-osrm.org/route/v1/driving/"

        f"{start_lon},{start_lat};"

        f"{end_lon},{end_lat}"

        "?overview=false"

        )



        response=requests.get(

            url,

            timeout=10

        )


        data=response.json()



        distance=(

            data["routes"][0]["distance"]

            /

            1000

        )


        duration=(

            data["routes"][0]["duration"]

            /

            60

        )



        return round(distance,2),round(duration)



    except Exception:


        return None,None




# ==============================
# User Input
# ==============================


start=st.text_input(
    "📍 Starting Place"
)


target=st.text_input(
    "🎯 Target Place"
)



vehicle=st.selectbox(

    "🚘 Select Vehicle",

    [

        "Bike",

        "Auto",

        "Hatchback",

        "Sedan"

    ]

)



if st.button("🗺️ Find Distance"):


    distance,time=get_distance_time(

        start,

        target

    )


    if distance:


        st.session_state.distance=distance

        st.session_state.time=time


    else:


        st.error(
            "❌ Place not found"
        )



if "distance" in st.session_state:


    if vehicle in ["Bike","Auto"] and st.session_state.distance > 30:


        st.error(

            f"❌ {vehicle} unavailable above 30 KM"

        )


    else:


        st.success(

            f"📏 Distance : {st.session_state.distance} KM"

        )


        st.success(

            f"⏱️ Time : {st.session_state.time} Minutes"

        )
# ==============================
# Fare Calculation Functions
# ==============================


def get_base_fare(distance,vehicle):


    base={

        "Bike":30,
        "Auto":40,
        "Hatchback":50,
        "Sedan":60

    }


    per_km={

        "Bike":3,
        "Auto":6,
        "Hatchback":8,
        "Sedan":10

    }


    return (

        base[vehicle]

        +

        distance * per_km[vehicle]

    )





def get_driver_fare(distance,vehicle):


    rate={

        "Bike":3,
        "Auto":5,
        "Hatchback":8,
        "Sedan":10

    }


    return distance * rate[vehicle]





# ==============================
# ML Estimated Fare
# ==============================


if st.button(
    "🤖 Predict Estimated Fare"
):


    if "distance" not in st.session_state:


        st.warning(

            "First find distance"

        )


    else:



        distance=st.session_state.distance

        duration=st.session_state.time




        # Bike Auto Limit


        if vehicle in ["Bike","Auto"] and distance > 30:


            st.error(

                f"❌ {vehicle} unavailable above 30 KM"

            )


        else:



            mileage=vehicle_details[vehicle]["mileage"]


            petrol_price=110



            fuel_cost=(

                distance/mileage

            )*petrol_price




            vehicle_encoded=encoder.transform(

                [vehicle]

            )[0]




            input_data=np.array(

                [[

                    distance,

                    duration,

                    vehicle_encoded,

                    mileage,

                    petrol_price,

                    fuel_cost

                ]]

            )




            prediction=model.predict(

                input_data

            )[0]



            st.session_state.estimated=round(

                prediction

            )





if "estimated" in st.session_state:


    st.success(

        f"🤖 Estimated Fare : ₹{st.session_state.estimated}"

    )

# ==============================
# Actual Fare Calculation
# ==============================


if "distance" in st.session_state:


    st.divider()


    st.subheader(
        "🧾 Actual Fare Calculation"
    )



    # Editable Actual Distance

    actual_distance = st.number_input(

        "📏 Actual Distance (KM)",

        min_value=0.0,

        value=float(st.session_state.distance),

        step=0.1

    )



    # Editable Actual Time

    actual_time = st.number_input(

        "⏱️ Actual Time (Minutes)",

        min_value=0,

        value=int(st.session_state.time),

        step=1

    )





    if st.button(

        "💰 Calculate Actual Fare"

    ):



        # Vehicle restriction


        if vehicle in ["Bike","Auto"] and actual_distance > 30:


            st.error(

                f"❌ {vehicle} unavailable above 30 KM"

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






            # Final Actual Fare


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



            st.session_state.details={


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


    details=st.session_state.details



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
