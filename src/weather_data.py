import requests
import pandas as pd

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


import os
import sys
from pathlib import Path

import folium



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

        # Dane godzinowe
        hourly = data.get("hourly", {})
        df_hourly = pd.DataFrame(hourly)
        df_hourly["time"] = pd.to_datetime(df_hourly["time"])

        # Od teraz: 120 kolejnych godzin (5 dni)
        now = pd.to_datetime(data.get("current", {}).get("time"))
        df_next_5d = df_hourly[df_hourly["time"] > now].head(120)

        # Opisy i burza
        df_next_5d["storm"] = df_next_5d["weathercode"].apply(lambda c: "yes" if c in [95, 96, 99] else "no")
        df_next_5d["weather description"] = df_next_5d["weathercode"].map(WEATHER_CODES_EN)
        df_next_5d["opis pogody [PL]"] = df_next_5d["weathercode"].map(WEATHER_CODES_PL)

        # Zmiana nazw kolumn
        df_next_5d = df_next_5d.rename(columns={
            "temperature_2m": "temperature [°C]",
            "relative_humidity_2m": "humidity [%]",
            "wind_speed_10m": "wind speed [km/h]",
            "precipitation": "precipitation [mm]",
            "rain": "rain [mm]",
            "snowfall": "snowfall [cm]"
        })

        df_next_5d = df_next_5d.drop(columns=["weathercode"])

        # Zapis i zwrot
        df_next_5d.to_csv(save_path, index=False)
        return df_next_5d

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

