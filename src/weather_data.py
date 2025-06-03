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

def get_weather(latitude, longitude):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,rain,snowfall"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,rain,snowfall"
        "&timezone=Europe%2FWarsaw"
    )
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Dane aktualne
        current = data.get("current", {})
        current_time = current.get("time")
        df_current = pd.DataFrame([{
            "time": current_time,
            "temperature [°C]": current.get("temperature_2m"),
            "humidity [%]": current.get("relative_humidity_2m"),
            "wind speed [km/h]": current.get("wind_speed_10m"),
            "precipitation [mm]": current.get("precipitation"),
            "rain [mm]": current.get("rain"),
            "snowfall [cm]": current.get("snowfall")
        }])

        # Dane godzinowe
        hourly = data.get("hourly", {})
        df_hourly = pd.DataFrame(hourly)

        # Tylko najbliższe 24 godziny od teraz
        df_hourly["time"] = pd.to_datetime(df_hourly["time"])
        df_next_24h = df_hourly[df_hourly["time"] > pd.to_datetime(current_time)].head(24)

        # Zmiana nazw kolumn
        df_next_24h = df_next_24h.rename(columns={
            "temperature_2m": "temperature [°C]",
            "relative_humidity_2m": "humidity [%]",
            "wind_speed_10m": "wind speed [km/h]",
            "precipitation": "precipitation [mm]",
            "rain": "rain [mm]",
            "snowfall": "snowfall [cm]"
        })

        # Połączenie obu
        df_result = pd.concat([df_current, df_next_24h], ignore_index=True)
        return df_result

    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

def get_weather_forecast(latitude, longitude, days):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,rain,snowfall"
        "&timezone=Europe%2FWarsaw"
    )

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # Dane godzinowe
        hourly = data.get("hourly", {})
        df_hourly = pd.DataFrame(hourly)

        # Przekształcenie kolumny czasu
        df_hourly["time"] = pd.to_datetime(df_hourly["time"])

        # Odcięcie do n dni wprzód
        df_limited = df_hourly.head(24 * days)

        # Zmiana nazw kolumn
        df_limited = df_limited.rename(columns={
            "temperature_2m": "temperature [°C]",
            "relative_humidity_2m": "humidity [%]",
            "wind_speed_10m": "wind speed [km/h]",
            "precipitation": "precipitation [mm]",
            "rain": "rain [mm]",
            "snowfall": "snowfall [cm]"
        })

        return df_limited

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


# Funkcja służąca do zapisania koordynatów do miasta w pliku konfiguracyjnym

def config_set_city(config_path = 'config/config.json'):
    if os.path.exists(config_path) == True:
        config_data = pd.read_json(config_path)
    
    config_data = pd.read_json(config_path)

    city, cor = select_city()
    
    config_data['city_name'] = city
    config_data['latitude'] = cor[0]
    config_data['longitude'] = cor[1]
    

    #config_path = Path(config_path)
    #config_path.parent.mkdir(parents=True, exist_ok=True)
    config_data.to_json(path_or_buf=config_path, force_ascii=False, indent=2)
    
    return config_data[['city_name', 'latitude', 'longitude']]