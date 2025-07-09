import requests
import streamlit as st
import json
from geopy.geocoders import Nominatim
import pandas as pd
import time

st.set_page_config(
    page_title="Property Price Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #FF4B4B 0%, #721c24 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .status-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }
    
    .status-good {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem 1.25rem;
        border-radius: 0.25rem;
    }
    
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem 1.25rem;
        border-radius: 0.25rem;
    }
    
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .feature-tag {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.875rem;
    }
    
    .section-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        margin: 2rem 0;
    }
    
    .info-card {
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 10px 10px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

URL_API = "https://house-price-be.onrender.com/"


def get_location(query):
    """Get location coordinates from address query"""
    try:
        geolocator = Nominatim(user_agent="property-price-predictor")
        return geolocator.geocode(query)
    except Exception as e:
        st.error(f"Error getting location: {str(e)}")
        return None


def check_server_status():
    """Check if the API server is running"""
    try:
        response = requests.get(URL_API, timeout=5)
        return response.json().get("message", "Unknown"), True
    except requests.exceptions.RequestException:
        return "Connection Error", False


def format_currency(amount):
    """Format currency with proper thousands separators"""
    return f"€{amount:,.2f}"


def create_property_summary(property_data):
    """Create a formatted summary of the property"""
    summary = {}

    if property_data["type"] and property_data["subtype"]:
        summary["Property Type"] = (
            f"{property_data['type']} - {property_data['subtype']}"
        )

    if property_data["province"]:
        summary["Province"] = property_data["province"]

    if property_data["postCode"]:
        summary["Postcode"] = str(property_data["postCode"])

    if property_data["epcScore"]:
        summary["EPC Score"] = property_data["epcScore"]

    # Surface information
    surfaces = []
    if property_data["habitableSurface"] > 0:
        surfaces.append(f"Habitable: {property_data['habitableSurface']} m²")
    if property_data["terraceSurface"] > 0:
        surfaces.append(f"Terrace: {property_data['terraceSurface']} m²")
    if property_data["gardenSurface"] > 0:
        surfaces.append(f"Garden: {property_data['gardenSurface']} m²")

    if surfaces:
        summary["Surface Areas"] = " | ".join(surfaces)

    # Room counts
    rooms = []
    if property_data["bedroomCount"] > 0:
        rooms.append(f"{property_data['bedroomCount']} bedrooms")
    if property_data["bathroomCount"] > 0:
        rooms.append(f"{property_data['bathroomCount']} bathrooms")
    if property_data["toiletCount"] > 0:
        rooms.append(f"{property_data['toiletCount']} toilets")

    if rooms:
        summary["Rooms"] = " | ".join(rooms)

    return summary


# Main app
def main():
    st.html("<div class='main-header'><h1>Property Price Predictor</h1></div>")

    # Server status check
    with st.spinner("Checking server status..."):
        status_message, is_connected = check_server_status()

    if is_connected:
        st.html(
            f'<div class="status-container"><div class="status-good">✅ Server Status: {status_message}</div></div>'
        )
    else:
        st.html(
            f'<div class="status-container"><div class="status-error">❌ Server Status: {status_message}</div></div>'
        )
        st.warning(
            "⚠️ The prediction service is currently unavailable. Please try again later."
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

    st.subheader("🏡 Property Details")

    col1, col2 = st.columns(2)

    with col1:
        property_type = st.selectbox(
            "Property Type",
            options=["APARTMENT", "HOUSE"],
            index=None,
            placeholder="Select property type...",
            key="property_type",
        )

    with col2:
        if st.session_state.get("property_type") == "APARTMENT":
            subtype = st.selectbox(
                "Apartment Subtype",
                options=list_apt,
                index=None,
                placeholder="Select detailed subtype...",
                key="subtype",
            )
        elif st.session_state.get("property_type") ==  "HOUSE":
            subtype = st.selectbox(
                "House Subtype",
                options=list_house,
                index=None,
                placeholder="Select detailed subtype...",
                key="subtype",
            )
        else:
            subtype = st.selectbox(
                "Property Subtype",
                options=[],
                index=None,
                placeholder="Select property type first...",
                key="subtype",
                disabled=True,
            )

    # Main form
    with st.form("property_form", clear_on_submit=False):

        # Location Section
        st.subheader("📍 Location")

        col1, col2 = st.columns(2)

        with col1:
            province = st.selectbox(
                "Province",
                options=[
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
                ],
                index=None,
                placeholder="Select province...",
            )

        with col2:
            postcode = st.number_input(
                "Postcode",
                min_value=1000,
                max_value=9999,
                value=None,
                placeholder="Enter postcode...",
            )

        # Energy Performance
        st.divider()
        st.subheader("⚡ Energy Performance")

        epc_score = st.selectbox(
            "EPC Score",
            options=["A+", "A", "B", "C", "D", "E", "F", "G"],
            index=None,
            placeholder="Select EPC score...",
        )

        # Room Details
        st.divider()
        st.subheader("🛏️ Room Configuration")

        col1, col2, col3 = st.columns(3)

        with col1:
            bedroomCount = st.slider("Bedrooms", 0, 10, 2)
        with col2:
            bathroomCount = st.slider("Bathrooms", 0, 5, 1)
        with col3:
            toiletCount = st.slider("Toilets", 0, 5, 1)

        # Surface Areas
        st.divider()
        st.subheader("📐 Surface Areas")

        col1, col2, col3 = st.columns(3)

        with col1:
            habitableSurface = st.number_input(
                "Habitable Surface (m²)", min_value=0, value=0, step=1
            )
        with col2:
            terraceSurface = st.number_input(
                "Terrace Surface (m²)", min_value=0, value=0, step=1
            )
        with col3:
            gardenSurface = st.number_input(
                "Garden Surface (m²)", min_value=0, value=0, step=1
            )

        # Extra Features
        st.divider()
        st.subheader("✨ Additional Features")

        boolean_fields = [
            ("hasAttic", "Attic"),
            ("hasGarden", "Garden"),
            ("hasAirConditioning", "Air Conditioning"),
            ("hasArmoredDoor", "Armored Door"),
            ("hasVisiophone", "Visiophone"),
            ("hasTerrace", "Terrace"),
            ("hasOffice", "Office"),
            ("hasSwimmingPool", "Swimming Pool"),
            ("hasFireplace", "Fireplace"),
            ("hasBasement", "Basement"),
            ("hasDressingRoom", "Dressing Room"),
            ("hasDiningRoom", "Dining Room"),
            ("hasLift", "Lift"),
            ("hasHeatPump", "Heat Pump"),
            ("hasPhotovoltaicPanels", "Photovoltaic Panels"),
            ("hasLivingRoom", "Living Room"),
        ]
        property_input = {
            "habitableSurface": habitableSurface,
            "type": property_type,
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

        selected_features = []
        cols = st.columns(4)

        for i, (field_key, field_label) in enumerate(boolean_fields):
            with cols[i % 4]:
                checked = st.checkbox(field_label, key=field_key)
                if checked:
                    selected_features.append(field_label)

        # Submit buttons
        st.divider()

        col1, col2, col3, col4, col5 = st.columns(5)
        with col3:
            submit_button = st.form_submit_button(
                "🔮 Predict Price", type="primary", use_container_width=True
            )

        for field_key, _ in boolean_fields:
            if st.session_state.get(field_key, False):
                property_input[field_key] = True

    # Process form submission
    if submit_button:
        with st.spinner("🔄 Processing your request..."):
            try:
                response = requests.post(f"{URL_API}/predict", json=property_input)

                if response.status_code == 200:
                    prediction = response.json()

                    # Create property summary
                    summary = create_property_summary(property_input)

                    st.divider()

                    # Prediction result
                    st.html(
                        f'<div class="prediction-card"><h2>💰 Predicted Property Value</h2><h1>{format_currency(prediction['prediction'])}</h1><p>Based on your input and current market conditions</p></div>'
                    )

                    # Property summary
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.subheader("📋 Property Summary")

                        for key, value in summary.items():
                            st.html(
                                f'<div class="info-card"><strong>{key}:</strong> {value}</div>'
                            )

                        if len(selected_features) > 0:
                            st.write("**Additional Features:**")
                            features_html = ""
                            for feature in selected_features:
                                features_html += (
                                    f'<span class="feature-tag">{feature}</span>'
                                )
                            st.html(features_html)

                    with col2:
                        # Map display
                        if postcode and province:
                            st.subheader("📍 Location")
                            location_query = f"{postcode}, {province}, Belgium"
                            location = get_location(location_query)

                            if location:
                                location_df = pd.DataFrame(
                                    {
                                        "lat": [location.latitude],
                                        "lon": [location.longitude],
                                    }
                                )
                                st.map(location_df, zoom=10)
                            else:
                                st.warning("⚠️ Could not display location on map")

                else:
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            if isinstance(error_data["detail"], list):
                                missing_fields = [
                                    error.get("field", "Unknown field")
                                    for error in error_data["detail"]
                                    if isinstance(error, dict)
                                ]
                                st.error(
                                    f"❌ Missing or invalid input in: {', '.join(missing_fields)}"
                                )
                            else:
                                st.error(f"❌ {error_data['detail']}")
                        else:
                            st.error(
                                "❌ An error occurred while processing your request"
                            )
                    except:
                        st.error("❌ An error occurred while processing your request")

            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
