import requests
import pandas as pd
from datetime import datetime

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

import json

import os
import sys
from pathlib import Path

import folium
from PyQt5 import QtWidgets, QtCore, QtGui, QtWebEngineWidgets, QtWebChannel
from PyQt5.QtCore import QObject, pyqtSlot, QUrl
from geopy.geocoders import Nominatim

import pandas as pd
import requests
from pathlib import Path

# Mapowanie kodów pogodowych
WEATHER_CODES_EN = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

WEATHER_CODES_PL = {
    0: "Bezchmurne niebo",
    1: "Przeważnie bezchmurnie",
    2: "Częściowe zachmurzenie",
    3: "Zachmurzenie całkowite",
    45: "Mgła",
    48: "Mgła szronowa",
    51: "Lekka mżawka",
    53: "Umiarkowana mżawka",
    55: "Gęsta mżawka",
    56: "Lekka marznąca mżawka",
    57: "Gęsta marznąca mżawka",
    61: "Słabe opady deszczu",
    63: "Umiarkowane opady deszczu",
    65: "Intensywne opady deszczu",
    66: "Lekki marznący deszcz",
    67: "Silny marznący deszcz",
    71: "Słabe opady śniegu",
    73: "Umiarkowane opady śniegu",
    75: "Intensywne opady śniegu",
    77: "Ziarna śniegu",
    80: "Słabe przelotne opady deszczu",
    81: "Umiarkowane przelotne opady deszczu",
    82: "Silne przelotne opady deszczu",
    85: "Słabe przelotne opady śniegu",
    86: "Silne przelotne opady śniegu",
    95: "Burza",
    96: "Burza z lekkim gradem",
    99: "Burza z silnym gradem"
}

def get_weather(latitude, longitude, save_path='./temp/weather.csv'):
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,rain,snowfall,weathercode"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,rain,snowfall,weathercode"
        "&timezone=Europe%2FWarsaw"
    )
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Dane aktualne
        current = data.get("current", {})
        current_time = current.get("time")
        code = current.get("weathercode")
        df_current = pd.DataFrame([{
            "time": current_time,
            "temperature [°C]": current.get("temperature_2m"),
            "humidity [%]": current.get("relative_humidity_2m"),
            "wind speed [km/h]": current.get("wind_speed_10m"),
            "precipitation [mm]": current.get("precipitation"),
            "rain [mm]": current.get("rain"),
            "snowfall [cm]": current.get("snowfall"),
            "storm": "yes" if code in [95, 96, 99] else "no",
            "weather description": WEATHER_CODES_EN.get(code, "Unknown"),
            "opis pogody [PL]": WEATHER_CODES_PL.get(code, "Nieznany")
        }])

        # Dane godzinowe
        hourly = data.get("hourly", {})
        df_hourly = pd.DataFrame(hourly)
        df_hourly["time"] = pd.to_datetime(df_hourly["time"])

        # Najbliższe 24h od teraz
        df_next_24h = df_hourly[df_hourly["time"] > pd.to_datetime(current_time)].head(24)

        # Opisy i burza
        df_next_24h["storm"] = df_next_24h["weathercode"].apply(lambda c: "yes" if c in [95, 96, 99] else "no")
        df_next_24h["weather description"] = df_next_24h["weathercode"].map(WEATHER_CODES_EN)
        df_next_24h["opis pogody [PL]"] = df_next_24h["weathercode"].map(WEATHER_CODES_PL)

        # Zmiana nazw kolumn
        df_next_24h = df_next_24h.rename(columns={
            "temperature_2m": "temperature [°C]",
            "relative_humidity_2m": "humidity [%]",
            "wind_speed_10m": "wind speed [km/h]",
            "precipitation": "precipitation [mm]",
            "rain": "rain [mm]",
            "snowfall": "snowfall [cm]"
        })

        df_next_24h = df_next_24h.drop(columns=["weathercode"])

        # Połączenie obu
        df_result = pd.concat([df_current, df_next_24h], ignore_index=True)
        df_result.to_csv(save_path, index=False)
        return df_result

    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

def get_weather_forecast(latitude, longitude, days, interval_hours=12, save_path='./temp/weather_forecast.csv'):
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,rain,snowfall,weathercode"
        "&timezone=Europe%2FWarsaw"
    )

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        hourly = data.get("hourly", {})
        df_hourly = pd.DataFrame(hourly)
        df_hourly["time"] = pd.to_datetime(df_hourly["time"])

        total_hours = 24 * days
        samples_needed = total_hours // interval_hours

        df_filtered = df_hourly.iloc[::interval_hours].head(samples_needed)

        df_filtered["storm"] = df_filtered["weathercode"].apply(lambda code: "yes" if code in [95, 96, 99] else "no")
        df_filtered["weather description"] = df_filtered["weathercode"].map(WEATHER_CODES_EN)
        df_filtered["opis pogody [PL]"] = df_filtered["weathercode"].map(WEATHER_CODES_PL)

        df_filtered = df_filtered.rename(columns={
            "temperature_2m": "temperature [°C]",
            "relative_humidity_2m": "humidity [%]",
            "wind_speed_10m": "wind speed [km/h]",
            "precipitation": "precipitation [mm]",
            "rain": "rain [mm]",
            "snowfall": "snowfall [cm]"
        })

        df_filtered = df_filtered.drop(columns=["weathercode"])

        df_filtered.to_csv(save_path, index=False)
        return df_filtered

    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

def get_location_and_timezone(city, country=None, postal_code=None):
    geolocator = Nominatim(user_agent="location-tz-app")
    query = city
    if country:
        query += f", {country}"
    if postal_code:
        query += f", {postal_code}"
    
    location = geolocator.geocode(query)
    if location is None:
        return {"error": "Location not found"}

    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(lat=location.latitude, lng=location.longitude)

    return {
        "location": location.address,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "timezone": timezone_name
    }

class Bridge(QObject):
    def __init__(self, label, button):
        super().__init__()
        self.label = label
        self.button = button
        self.geolocator = Nominatim(user_agent="pyqt-folium-app")
        self.miasto = None
        self.wspolrzedne = None

    @pyqtSlot(float, float)
    def sendCoordinates(self, lat, lon):
        self.wspolrzedne = (lat, lon)
        try:
            location = self.geolocator.reverse(f"{lat}, {lon}", language='pl')
            addr = location.raw.get("address", {}) if location else {}
            self.miasto = addr.get("city") or addr.get("town") or addr.get("village") or "Nieznane miejsce"
        except Exception:
            self.miasto = "Błąd geolokalizacji"

        self.label.setText(f"{self.miasto}")
        self.button.setVisible(True)

def inject_js(html, map_var_name="map"):
    js = f"""
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <script>
    new QWebChannel(qt.webChannelTransport, function(channel) {{
        var bridge = channel.objects.bridge;
        var map = window.{map_var_name};
        var marker;
        map.on('click', function(e) {{
            if (marker) map.removeLayer(marker);
            marker = L.marker(e.latlng).addTo(map);
            bridge.sendCoordinates(e.latlng.lat, e.latlng.lng);
        }});
    }});
    </script>
    """
    return html.replace("</body>", js + "</body>")

def select_city():

    app = QtWidgets.QApplication(sys.argv)

    # Okno
    window = QtWidgets.QWidget()
    window.setWindowTitle("Wybierz miasto")
    layout = QtWidgets.QVBoxLayout(window)

    # Etykieta z nazwą miasta (na górze)
    label = QtWidgets.QLabel("Kliknij na mapie, aby wybrać miasto")
    label.setAlignment(QtCore.Qt.AlignCenter)
    font = QtGui.QFont()
    font.setPointSize(16)  # <--- Tu ustawiasz rozmiar czcionki
    font.setBold(True)
    label.setFont(font)
    layout.addWidget(label)

    # Przycisk wyboru
    button = QtWidgets.QPushButton("Wybierz")
    button.setVisible(False)

    # Mapa
    web = QtWebEngineWidgets.QWebEngineView()
    layout.addWidget(web)
    layout.addWidget(button)

    # Folium mapa
    start_coords = (52.2297, 21.0122)
    m = folium.Map(location=start_coords, zoom_start=6)
    html = m.get_root().render()
    html = inject_js(html, map_var_name=f"map_{m._id}")
    web.setHtml(html, baseUrl=QUrl("http://localhost/"))

    # Most JS↔Python
    bridge = Bridge(label, button)
    channel = QtWebChannel.QWebChannel()
    channel.registerObject("bridge", bridge)
    web.page().setWebChannel(channel)

    # Obsługa przycisku
    def on_accept():
        window.close()

    button.clicked.connect(on_accept)

    window.resize(800, 600)
    window.show()
    app.exec_()

    return bridge.miasto, bridge.wspolrzedne

def config_set_city(config_path = 'config/config.json'):
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if os.path.exists(config_path) == True:
        config_data = pd.read_json(config_path)
    
    #config_data = pd.read_json(config_path)

    city, cor = select_city()

    config_data = pd.DataFrame()
    config_data.at[0, 'city_name'] = city
    config_data.at[0, 'latitude'] = cor[0]
    config_data.at[0, 'longitude'] = cor[1]
        

    
    config_data.to_json(path_or_buf=config_path, force_ascii=False, indent=2)
    
    return config_data[['city_name', 'latitude', 'longitude']]

def example():
    config_path = 'config/config.json'

    if os.path.exists(config_path) == True:
        config_data = pd.read_json(config_path)
    else:
    
        config_data = config_set_city()

    if config_data['latitude'].isna().any() or config_data['longitude'].isna().any():
        config_data = config_set_city()


    config_data['latitude'] = config_data['latitude']
    config_data['longitude'] = config_data['longitude']

    df_forecast = get_weather_forecast(latitude = config_data['latitude'][0], 
                                       longitude = config_data['longitude'][0],
                                       days=7)

    print(df_forecast)

    df_forecast = get_weather(latitude = config_data['latitude'][0], 
                              longitude = config_data['longitude'][0])
    
    print(df_forecast)