import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import os
from openai import OpenAI

from geopy.geocoders import Nominatim
from pathlib import Path
from streamlit_folium import st_folium
import folium

import locale
from datetime import datetime, timezone

from weather_data import select_city, get_weather, get_weather_forecast

from llm.responses import get_llm_response
from llm.prompts import WEATHER_LIFESTYLE_ASSISTANT



def expert_chat_component(location: str, weather_data: str):
    """
    A simple chat input component for user interaction.
    This function allows users to input text and displays the input back to them.
    """
    st.subheader("💬 Chat with Expert")
    
    prompt = st.chat_input("Say something")
    if prompt:
        st.write(f"Pytanie do eksperta: {prompt}")
        
        full_prompt = WEATHER_LIFESTYLE_ASSISTANT.format(
            location=location, 
            prompt=prompt, 
            weather_data=weather_data
        )

        with st.spinner("Ekspert analizuje dane..."):
            client = OpenAI()
            response = get_llm_response(client, full_prompt)

        st.success("Odpowiedź eksperta:")
        st.write(response)


def load_weather_data(path='temp/weather_forecast.csv'):
    config_path = 'config/config.json'
    config_data = pd.read_json(config_path)
    timestamp_utc = datetime.now(timezone.utc).timestamp()

    file_missing = not os.path.exists(path)
    outdated = pd.isna(config_data.loc[0, "last_weather_request"]) or \
               (timestamp_utc - config_data['last_weather_request'].loc[0] > 10 * 60)

    if file_missing or outdated:
        config_data['last_weather_request'] = timestamp_utc
        config_data.to_json(config_path, orient='records', indent=4)

        get_weather_forecast(
            config_data['latitude'].loc[0],
            config_data['longitude'].loc[0],
            days=5,
            interval_hours=1
        )

    data = pd.read_csv(path)

    if 'time' in data.columns:
        data['time'] = pd.to_datetime(data['time'], errors='coerce')

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
    Strona z prognozą pogody – wszystkie godziny.
    Wykres obejmuje pełne dane, sekcja ikon tylko godz. 12:00.
    """

    # --- Locale PL ---
    try:
        locale.setlocale(locale.LC_TIME, "pl_PL.UTF-8")
    except locale.Error:
        st.warning("⚠️ Nie udało się ustawić języka polskiego dla dat. Sprawdź ustawienia systemu.")

    if os.path.exists("temp/weather_forecast.csv"):
        csv_data = pd.read_csv("temp/weather_forecast.csv")
    else:
        load_weather_data()
        csv_data = pd.read_csv("temp/weather_forecast.csv")

    csv_data["time"] = pd.to_datetime(csv_data["time"], errors="coerce")

    config_data = pd.read_json("config/config.json")
    city_name = config_data['city_name'][0]

    live_data = load_weather_data()
    live_data["time"] = pd.to_datetime(live_data["time"], errors="coerce")
    data = pd.concat([csv_data, live_data], ignore_index=True)

    data = data.sort_values("time")

    st.title(f"🌤️ Prognoza Pogody - {city_name}")

    left, right = st.columns([4, 2])

    with left:
        chart_type = st.radio("Wybierz dane do wyświetlenia:", ["Temperatura", "Wiatr"], horizontal=True)


        # Zakładamy, że masz `data` z kolumną datetime 'time'
        data["date_only"] = data["time"].dt.date
        unique_days = sorted(data["date_only"].unique())[:5]

        # Polskie skróty dni tygodnia (0 = poniedziałek)
        dni_tygodnia = {
            0: "Poniedziałek", 1: "Wtorek", 2: "Środa", 3: "Czwartek", 4: "Piątek", 5: "Sobota", 6: "Niedziela"
        }

        # Generowanie etykiet do radia np. "Pn, 16.06"
        day_labels = [
            f"{dni_tygodnia[pd.to_datetime(date).weekday()]}, {pd.to_datetime(date).strftime('%d.%m')}"
            for date in unique_days
        ]

        # Mapa: label → date
        day_map = dict(zip(day_labels, unique_days))

        # Wyświetlenie radia w poziomie
        selected_day_label = st.radio("📆 Wybierz dzień:", day_labels, horizontal=True)
        selected_day = day_map[selected_day_label]




        filtered_data = data[data["date_only"] == selected_day]

        if filtered_data.empty:
            st.warning("🚫 Brak danych pogodowych do wyświetlenia.")
        else:
            fig = go.Figure()
            x_vals = filtered_data["time"].dt.strftime("%H:%M")

            if chart_type == "Temperatura":
                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=filtered_data["temperature [°C]"],
                    mode="lines",
                    name="Temperatura [°C]",
                    line=dict(shape="spline")
                ))
                fig.update_layout(yaxis_title="Temperatura [°C]")
            else:
                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=filtered_data["wind speed [km/h]"],
                    mode="lines",
                    name="Wiatr [km/h]",
                    line=dict(shape="spline", dash="dot")
                ))
                fig.update_layout(yaxis_title="Wiatr [km/h]")

            fig.update_layout(
                xaxis_title="Godzina",
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



        # Dane z południa każdego dnia (godz. 12:00)
        midday_data = data[data["time"].dt.hour == 12].sort_values("time").head(5)

        for _, row in midday_data.iterrows():
            weekday = row["time"].weekday()
            date_str = f"{dni_tygodnia[weekday]}, {row['time'].strftime('%d.%m')}"
            temp = int(round(row["temperature [°C]"]))
            opis = row["opis pogody [PL]"].lower()

            # Dobranie ikony
            icon_file = "sunny.png"
            for key, filename in icon_map.items():
                if key in opis:
                    icon_file = filename
                    break

            img_path = os.path.join("img", icon_file)

            # Wyświetlenie: ikona + opis
            col1, col2 = st.columns([1, 10])
            with col1:
                st.image(img_path, width=60)
            with col2:
                st.markdown(
                    f"**{date_str}**  \n"
                    f"{row['opis pogody [PL]']}  \n"
                    f"🌡️ {temp}°C"
                )
    
    expert_chat_component(location=city_name,
                          weather_data=data.to_csv(index=False))
