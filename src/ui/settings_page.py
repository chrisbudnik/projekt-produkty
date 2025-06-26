import streamlit as st
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import pandas as pd

from weather_data import get_weather_forecast


def reverse_geocode(lat, lon):
    geolocator = Nominatim(user_agent="weather_app")
    try:
        location = geolocator.reverse((lat, lon), language="pl", timeout=10)
        if location and "address" in location.raw:
            address = location.raw["address"]
            city = (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("hamlet")
            )
            return city or "Nieznana lokalizacja"
        return "Nieznana lokalizacja"
    except (GeocoderTimedOut, GeocoderUnavailable):
        return "Błąd geokodowania"


def setup_openai_api_key():
    """
    Set up OpenAI API key input in the sidebar.
    """

    st.subheader("Ustawienia AI")
    api_key_input = st.text_input("Wprowadź klucz OpenAI API", type="password")
    if api_key_input:
        st.session_state.openai_api_key = api_key_input
        st.success("Klucz API zapisany!")


def settings_page():
    config_path = "config/config.json"

    st.session_state.initialized = True
    config_data = pd.read_json(config_path)
    # loc = [config_data['latitude'][0], config_data['longitude'][0]]

    st.title("⚙️ Ustawienia")
    setup_openai_api_key()

    st.subheader("🗺️ Wybierz lokalizację")
    st.subheader("    Aktualna lokalizacja: " + str(config_data["city_name"][0]))

    default_location = [config_data["latitude"][0], config_data["longitude"][0]]

    m = folium.Map(location=default_location, zoom_start=15)

    # Dodaj popup z lat/lon po kliknięciu
    m.add_child(folium.LatLngPopup())

    map_data = st_folium(m, width=2050, height=650)

    selected_location = None

    if map_data and map_data["last_clicked"]:
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        loc = [lat, lon]
        m.add_child(folium.Marker(location=loc, popup="Tu jestem").add_to(m))

        city_name = reverse_geocode(lat, lon)

        st.markdown(f"📍 Wybrane miejsce: **{city_name}**")

        if st.button("✅ Wybierz lokalizację"):

            try:
                config_data[["city_name", "latitude", "longitude"]] = [
                    city_name,
                    lat,
                    lon,
                ]
                config_data.to_json(config_path, orient="records", indent=4)
                get_weather_forecast(
                    config_data["latitude"].loc[0],
                    config_data["longitude"].loc[0],
                    days=5,
                    interval_hours=1,
                )
                st.success(f"✅ Lokalizacja została wybrana: **{city_name}**")

            except Exception:
                st.error("❌ Nie udało się zapisać lokalizacji. Spróbuj ponownie.")
