import requests
import streamlit as st
import json
from geopy.geocoders import Nominatim
import pandas as pd
import time
from urllib.parse import urljoin
import os
import re

st.set_page_config(
    page_title="Property Price Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root, [data-theme="light"]{
    --primary-color: black;
    --bg-color:  #f8f9fa;
}
 [data-theme="dark"] {
    --primary-color: white;
    --bg-color: #0E1117;
  }
    .main-header {
        text-align: center;
        padding: 36px 0;
        background: linear-gradient(90deg, #FF4B4B 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 32px;
    }
    
    .status-container {
        display: flex;
        justify-content: center;
        margin-bottom: 32px;
    }
    
    .status-good {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 12px 20px;
        border-radius: 4px;
    }
    
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 12px 20px;
        border-radius: 4px;
    }
    
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 32px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 32px; 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .feature-tag {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 4px;
        font-size: 14px;
    }
    
    .info-card {
        background-color: var(--bg-color);
        color: var(--primary-color);
        border-left: 6px solid #764ba2;
        padding: 16px;
        margin: 6px 0;
        border-radius: 0 10px 10px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


def format_for_display(text):
    """Convert API format to user-friendly display format"""
    if not text:
        return text
    return text.replace('_', ' ').title()

def format_for_api(text):
    """Convert user input to API format"""
    if not text:
        return text
    return text.replace(' ', '_').upper()


def load_geodata():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "georef-belgium-postal-codes.csv")
    geo_df = pd.read_csv(data_path, delimiter=";")
    geo_df[["lat", "lon"]] = geo_df["Geo Point"].str.split(",", expand=True)
    geo_df["lat"] = geo_df["lat"].astype(float)
    geo_df["lon"] = geo_df["lon"].astype(float)
    geo_df["postCode"] = geo_df["Post code"].astype(str)
    grouped_df = geo_df.groupby("postCode")[["lat", "lon"]].mean()
    return grouped_df


def check_missing_fields(input):
    missing = [k for k, v in input.items() if v is None]
    if missing:
        for field in missing:
            st.error(f"❌ Missing value for: {field}")
        return False
    return True


def predict_price(data):
    if check_missing_fields(data):
        url = urljoin(
        st.secrets["predict_api"]["base_url"],
        st.secrets["predict_api"]["predict_endpoint"],)
      
        payload = {"data": data}
        print(payload)
        response = requests.post(url, json=payload)
        return response
    else:
        st.warning("Please fill in all required fields.")

def get_location(postcode):
    """Get location coordinates from address query"""
    try:
        geo_df = load_geodata()
        postcode =str(postcode)
        if postcode in geo_df.index:
            lat, lon = geo_df.loc[postcode]
            return lat, lon
        else:
            st.warning(f"⚠️ Postcode {postcode} not found in database")
            return None, None
    except Exception as e:
        st.error(f"❌ Error getting location: {str(e)}")
        return None, None
       


def check_server_status():
    """Check if the API server is running"""
    try:
        url = st.secrets["predict_api"]["base_url"]
        response = requests.get(url, timeout=5)
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
        property_data["type"] = format_for_display(property_data["type"])
        property_data["subtype"] =  format_for_display(property_data["subtype"])
        summary["Property Type"] = (
            f"{property_data['type']} - {property_data['subtype']}"
        )

    if property_data["province"]:
        summary["Province"] = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', property_data["province"])

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
       'Apartment', 'Flat Studio', 'Duplex', 'Penthouse', 'Ground Floor',
    'Apartment Block', 'Kot', 'Exceptional Property', 'Mixed Use Building',
    'Triplex', 'Loft', 'Service Flat'
    ]
    list_house = [
       'House', 'Villa', 'Town House', 'Chalet', 'Manor House', 'Mansion',
    'Bungalow', 'Country Cottage', 'Other Property', 'Castle', 'Pavilion',
    'Exceptional Property'
    ]
    
    list_type = ['Apartment', 'House']

    st.subheader("🏡 Property Details")

    col1, col2 = st.columns(2)

    with col1:
        property_type_display = st.selectbox(
            "Property Type",
            options= list_type,
            index=None,
            placeholder="Select property type...",
            key="property_type",
        )

    with col2:
        if st.session_state.get("property_type") == "Apartment":
            subtype_display = st.selectbox(
                "Apartment Subtype",
                options=[item.replace('_', ' ') for item in list_apt],
                index=None,
                placeholder="Select detailed subtype...",
                key="subtype",
            )
        elif st.session_state.get("property_type") ==  "House":
            subtype_display = st.selectbox(
                "House Subtype",
                options=[item.replace('_', ' ') for item in list_house],
                index=None,
                placeholder="Select detailed subtype...",
                key="subtype",
            )
        else:
            subtype_display = st.selectbox(
                "Property Subtype",
                options=[],
                index=None,
                placeholder="Select property type first...",
                key="subtype",
                disabled=True,
            )

    st.text(" ")

    # Main form
    with st.form("property_form", clear_on_submit=False):

        # Location Section
        st.subheader("📍 Location")

        col1, col2 = st.columns(2)

        with col1:
            province_display = st.selectbox(
                "Province",
                options=[
                    'Brussels', 'Luxembourg', 'Antwerp', 'Flemish Brabant', 'East Flanders', 'West Flanders', 'Liège', 'Walloon Brabant', 'Limburg', 'Namur', 'Hainaut'
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
                "Habitable Surface (m²)", min_value=0.0, value=50.0, step=0.1, format="%.2f"
            )
        with col2:
            terraceSurface = st.number_input(
                "Terrace Surface (m²)", min_value=0.0, value=0.0, step=0.1, format="%.2f"
            )
        with col3:
            gardenSurface = st.number_input(
                "Garden Surface (m²)", min_value=0.0, value=0.0, step=0.1, format="%.2f"
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
        
        property_type = format_for_api(property_type_display) if property_type_display else None
        subtype = format_for_api(subtype_display) if subtype_display else None
        province = province_display.replace(" ", "") if province_display else None
        
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
            else:
                property_input[field_key] = False

    # Process form submission
    if submit_button:
        with st.spinner("🔄 Processing your request..."):
            try:
                response = predict_price(property_input)
                
                if response is None:
                    pass
                elif response.status_code == 200:
                    response = response.json()
                    prediction = response["data"]

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
                        if postcode:
                            st.subheader("📍 Location")
                            lat, lon = get_location(postcode)

                            if lat and lon:
                                location_df = pd.DataFrame([{"lat": lat,"lon": lon,}])
                                st.map(location_df, zoom=10)
                            else:
                                st.warning("⚠️ Could not display location on map")

                elif response.status_code == 422:
                    detail = response.json().get("detail", [])
                    if detail:
                        error = detail[0]
                        loc = error.get("loc", [])
                        msg = error.get("msg", "Unknown error")
                        if len(loc) > 2:
                            field = loc[2]
                            st.error(f"⚠️ {field} : {msg}")
                        else:
                            msg = msg.replace("Value error,", "❌ ")
                            st.error(f"{msg}")
                    else:
                        st.error("⚠️ Unknown error occurred")
                elif response.status_code == 500:
                    error = response.json()["error"]
                    st.error(f"⛔ {error}")
                else:
                    st.error(f"⛔ API Error: {response.status_code} - {response.text}")

            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
