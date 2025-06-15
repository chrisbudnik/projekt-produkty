import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import os

from geopy.geocoders import Nominatim

from pathlib import Path
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium

import locale
from datetime import datetime

from weather_data import select_city



def load_weather_data(path = 'temp/weather.csv'):
    data = pd.read_csv(path)

    return data

def zmień_miasto(config_path='config/config.json'):
    st.header("🔄 Zmień miasto")

    wpisane = st.text_input("Wpisz nazwę miejscowości:")

    if wpisane:
        geolocator = Nominatim(user_agent="weather_app")
        try:
            location_list = geolocator.geocode(wpisane, exactly_one=False, addressdetails=True, limit=10, country_codes='pl')
        except Exception as e:
            st.error(f"Błąd podczas wyszukiwania lokalizacji: {e}")
            return

        if not location_list:
            st.warning("Nie znaleziono takiej miejscowości.")
            return

        elif len(location_list) == 1:
            loc = location_list[0]
            st.success(f"Znaleziono: {loc.address}")

            # Zapisz do config
            new_config = {"city_name": [loc.raw['address'].get('city', loc.raw['address'].get('town', wpisane))]}
            with open(config_path, "w", encoding="utf-8") as f:
                import json
                json.dump(new_config, f, ensure_ascii=False, indent=4)

            st.session_state["view"] = "prognoza"
            st.rerun()

        else:
            st.info(f"Znaleziono {len(location_list)} możliwych lokalizacji. Wybierz jedną:")

            options = []
            for loc in location_list:
                addr = loc.raw["address"]
                city = addr.get("city", addr.get("town", addr.get("village", wpisane)))
                county = addr.get("county", "brak powiatu")
                state = addr.get("state", "brak województwa")
                display_name = f"{city} ({county}, {state})"
                options.append((display_name, city))

            selected = st.selectbox("Wybierz lokalizację:", [name for name, _ in options])
            if st.button("Zatwierdź wybór"):
                selected_city = dict(options)[selected]
                new_config = {"city_name": [selected_city]}
                with open(config_path, "w", encoding="utf-8") as f:
                    import json
                    json.dump(new_config, f, ensure_ascii=False, indent=4)

                st.success(f"Miasto zostało ustawione na: {selected_city}")
                st.session_state["view"] = "prognoza"
                st.rerun()

def weather_forecast_page():
    """
    Strona z 5-dniową prognozą pogody na godzinę 12:00.
    Dane łączone są z pliku CSV i opcjonalnie z API.
    Wizualizacja obejmuje wykres oraz pogodową grafikę.
    """

    # Wczytaj dane z pliku CSV
    csv_data = pd.read_csv("temp/weather_forecast.csv")
    csv_data["time"] = pd.to_datetime(csv_data["time"], errors="coerce")

    config_data = pd.read_json("config/config.json")
    city_name = config_data['city_name'][0]



    if st.session_state.get("view") == "zmiana_miasta":
        zmień_miasto()

    # Opcjonalne dołączenie danych z API
    try:
        live_data = load_weather_data()
        live_data["time"] = pd.to_datetime(live_data["time"], errors="coerce")
        data = pd.concat([csv_data, live_data], ignore_index=True)
    except:
        data = csv_data

    # Filtrowanie danych z godziny 12:00
    data = data[data["time"].dt.hour == 12]
    data = data.sort_values("time").head(5)

    st.title(f"🌤️ Prognoza Pogody - {city_name}")

    # --- Trzy kolumny ---
    left, right = st.columns([4, 2])

    with left:
        # 🔘 Przełącznik: wybór typu wykresu
        chart_type = st.radio("Wybierz dane do wyświetlenia:", ["Temperatura", "Wiatr"], horizontal=True)

        if data.empty:
            st.warning("🚫 Brak danych pogodowych do wyświetlenia.")
        else:
            fig = go.Figure()
            x_vals = data["time"].dt.strftime("%Y-%m-%d")

            if chart_type == "Temperatura":
                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=data["temperature [°C]"],
                    mode="lines+markers",
                    name="Temperatura [°C]",
                    line=dict(shape="spline")
                ))
                fig.update_layout(yaxis_title="Temperatura [°C]")
            else:
                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=data["wind speed [km/h]"],
                    mode="lines+markers",
                    name="Wiatr [km/h]",
                    line=dict(shape="spline", dash="dot")
                ))
                fig.update_layout(yaxis_title="Wiatr [km/h]")

            fig.update_layout(
                xaxis_title="Data",
                height=500,
                margin=dict(t=30, b=30)
            )

            st.plotly_chart(fig, use_container_width=True)

    with right:
            st.subheader("📅 Prognoza na 5 dni")


            icon_map = {
                "bezchmurne": "sunny.png",
                "słonecz": "sunny.png",
                "pochmurno": "clouds.png",
                "zachmurzenie": "clouds.png",
                "przeważnie": "sunny.png",
                "deszcz": "rainy.png",
                "opady": "rainy.png",
                "śnieg": "snowy.png",
                "burza": "storm.png"
            }

            for _, row in data.iterrows():
                            # Ustawienie lokalizacji na polską
                locale.setlocale(locale.LC_TIME, "pl_PL.UTF-8")

                # Formatowanie daty z polskim dniem tygodnia
                date_str = row["time"].strftime("%A, %d.%m")


                temp = int(round(row["temperature [°C]"]))
                opis = row["opis pogody [PL]"].lower()

                # Dopasowanie ikony
                icon_file = "sunny.png"
                for key, filename in icon_map.items():
                    if key in opis:
                        icon_file = filename
                        break

                img_path = os.path.join("img", icon_file)

                col1, col2 = st.columns([1, 10])
                with col1:
                    st.image(img_path, width=60)
                with col2:
                    st.markdown(f"**{date_str}**  \n{row['opis pogody [PL]']}  \n🌡️ {temp}°C") 

#weather_forecast_page()