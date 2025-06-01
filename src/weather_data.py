import requests
import pandas as pd
from datetime import datetime

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

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

#df_forecast = get_weather_forecast(52.2297, 21.0122, days=7)  # Warszawa, prognoza na 3 dni
#print(df_forecast)


location_info = get_location_and_timezone("Berlin", "Germany")
print(location_info)