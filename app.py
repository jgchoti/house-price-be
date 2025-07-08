import requests
import streamlit as st
import json
from geopy.geocoders import Nominatim
import pandas as pd


URL_API = "https://house-price-be.onrender.com/"


def get_location(query):
    geolocator = Nominatim(user_agent="property-price-predictor")
    return geolocator.geocode(query)


try:
    response = requests.get(URL_API).json()
    st.write("🟢 server status: ", response["message"])
except:
    st.error("🔴 server status: Connection Error")

prediction = None
with st.form("my_form"):
    st.header("🏠 Property Price Prediction")

    type = st.selectbox(
        "🏡 Property Type? ",
        ("APARTMENT", "HOUSE"),
        index=None,
        placeholder="Select property type...",
    )
    list_apt = [
        "APARTMENT",
        "FLAT STUDIO",
        "DUPLEX",
        "PENTHOUSE",
        "GROUND FLOOR",
        "APARTMENT BLOCK",
        "KOT",
        "EXCEPTIONAL PROPERTY",
        "MIXED USE BUILDING",
        "TRIPLEX",
        "LOFT",
        "SERVICE FLAT",
    ]
    list_house = [
        "HOUSE",
        "VILLA",
        "TOWN HOUSE",
        "CHALET",
        "MANOR HOUSE",
        "MANSION",
        "BUNGALOW",
        "COUNTRY COTTAGE",
        "OTHER PROPERTY",
        "CASTLE",
        "PAVILION",
        "EXCEPTIONAL PROPERTY",
    ]
    if type == "APARTMENT":
        subtype = st.selectbox(
            "🏡 Detailed subtype ? ",
            list_apt,
            index=None,
            placeholder="Select property subtype...",
        )
    else:
        subtype = st.selectbox(
            "🏡 Detailed subtype ? ",
            list_house,
            index=None,
            placeholder="Select property subtype...",
        )
    province = st.selectbox(
        "🇧🇪 Province? ",
        (
            "BRUSSELS",
            "LUXEMBOURG",
            "ANTWERP",
            "FLEMISH BRABANT",
            "EAST FLANDERS",
            "WEST FLANDERS",
            "LIÈGE",
            "WALLOON BRABANT",
            "LIMBURG",
            "NAMUR",
            "HAINAUT",
        ),
        index=None,
        placeholder="Select property location...",
    )

    postcode = st.number_input(
        "🇧🇪 Insert a postcode",
        value=None,
        placeholder="Type a number...",
        min_value=1000,
        max_value=9999,
    )

    epc_score = st.selectbox(
        "⚡️ epcScore? ",
        ("A+", "A", "B", "C", "D", "E", "F", "G"),
        index=None,
        placeholder="Select EPC score...",
    )
    st.divider()
    st.subheader("🏠 Rooms Detail")
    bedroomCount = st.slider("🛌 How many bedrooms? ", 0, 10, 2)
    bathroomCount = st.slider("🛀 How many bathrooms? ", 0, 5, 2)
    toiletCount = st.slider("🚽 How many toilets? ", 0, 5, 2)
    st.divider()
    st.subheader("📐 Surface")
    col1, col2, col3 = st.columns(3)
    with col1:
        habitableSurface = st.number_input("Insert habitable surface (m2)")
    with col2:
        terraceSurface = st.number_input("Insert terrace surface (m2)")
    with col3:
        gardenSurface = st.number_input("Insert garden surface (m2)")

    property_input = {
        "habitableSurface": habitableSurface,
        "type": type,
        "subtype": subtype,
        "province": province,
        "postCode": postcode,
        "epcScore": epc_score,
        "bedroomCount": bedroomCount,
        "bathroomCount": bathroomCount,
        "toiletCount": toiletCount,
        "terraceSurface": terraceSurface,
        "gardenSurface": gardenSurface,
    }
    st.divider()
    st.subheader("✨ Extra Features")
    boolean_fields = [
        "hasAttic",
        "hasGarden",
        "hasAirConditioning",
        "hasArmoredDoor",
        "hasVisiophone",
        "hasTerrace",
        "hasOffice",
        "hasSwimmingPool",
        "hasFireplace",
        "hasBasement",
        "hasDressingRoom",
        "hasDiningRoom",
        "hasLift",
        "hasHeatPump",
        "hasPhotovoltaicPanels",
        "hasLivingRoom",
    ]
    selected = []
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    for i, field in enumerate(boolean_fields):
        with cols[i % 3]:
            field_label = field.replace("has", "").replace("Room", " Room")
            checked = st.checkbox(field_label, key=field)
            if checked:
                property_input[field] = True
                selected.append(field_label)

    col1, col2, col3, col4 = st.columns(4)
    with col2:
        submit_button = st.form_submit_button("🔮 Predict Price", type="primary")
    with col3:
        reset_button = st.form_submit_button("🔄 Reset Form", type="secondary")

    if reset_button:
        st.rerun()
if submit_button:
    try:
        response = requests.post(f"{URL_API}/predict", json=property_input)

        if response.status_code == 200:
            prediction = response.json()
        else:
            try:
                error_data = response.json()
                if "detail" in error_data:
                    if isinstance(error_data["detail"], list):
                        missing_fields = [error["field"] for error in error_data["detail"] if "field" in error]
                        st.error(f"❌  Missing Input in: {', '.join(missing_fields)}")
                    else:
                        st.error(f"❌  {error_data['detail']}")
            except:
                st.warning("⚠️ Could not parse error response from server.")
                st.warning(response.json())
            prediction = None

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Request failed: {e}")
        prediction = None

st.divider()

if prediction:
    st.subheader("📋 Your Selection:")
    if type and subtype and province:
        st.write(f"**Property:** {type} - {subtype}")
        st.write(f"**Location:** {province}")
    if postcode:
        st.write(f"**Postcode:** {postcode}")
    if epc_score:
        st.write(f"**EPC Score:** {epc_score}")
    if habitableSurface != 0:
        st.write(f"**Habitable Surface:** {habitableSurface} m2")
    if terraceSurface != 0:
        st.write(f"**terrace Surface:** {terraceSurface} m2")
    if gardenSurface != 0:
        st.write(f"**Garden Surface:** {gardenSurface} m2")
    if selected:
        st.write("**Extra Features:** " + " ".join([f"✅ {feat}" for feat in selected]))
    st.badge("Success", icon=":material/check:", color="green")
    st.header(f"💶 Predicted Price: €{prediction["prediction"]:,.2f}", divider=True)

    st.divider()
    if postcode and province:
        location_query = f"{postcode}, {province}, Belgium"
        location = get_location(location_query)
        st.subheader("📍 Approximate Location")
        if location:
            location_df = pd.DataFrame(
                {"lat": [location.latitude], "lon": [location.longitude]}
            )
            st.map(location_df)
        else:
            st.warning("⚠️ Could not find coordinates for the given postcode.")
else:
    if prediction and "detail" in prediction:
        if isinstance(prediction["detail"], list):
            missing_fields = [error["field"] for error in prediction["detail"] if "field" in error]
            st.error(f"❌ Missing Input in: {', '.join(missing_fields)}")
        else:
            st.error(f"❌ Missing Input in: {prediction['field']}")
